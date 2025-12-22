# Tasks.py Structure Analysis

**Date:** December 21, 2025
**Session:** 528
**Status:** CLOSED - Decision: Keep As-Is

---

## Final Decision

```
+------------------------------------------------------------------+
|  DECISION: KEEP tasks.py AS A SINGLE FILE                        |
|                                                                  |
|  Rationale:                                                      |
|  - File is large (17K lines) but well-organized                  |
|  - Tasks naturally grouped by function                           |
|  - Splitting adds complexity without proportional benefit        |
|  - Risk of breaking Celery autodiscovery and beat schedules      |
|  - Current structure works reliably                              |
|                                                                  |
|  This decision was reviewed and approved in Session 528.         |
|  Re-evaluate only if the file becomes genuinely problematic.     |
+------------------------------------------------------------------+
```

---

## Executive Summary

`core/tasks.py` contains 156 Celery tasks in 17,174 lines. While large, splitting was deferred due to:
1. Risk of breaking Celery autodiscovery
2. Extensive cross-task dependencies
3. Task decorators need careful handling
4. Lower priority than security fixes

---

## File Statistics

| Metric | Value |
|--------|-------|
| Total lines | 17,174 |
| Task functions (@shared_task) | 156 |
| Import statements | ~50 |
| Average task size | ~110 lines |

---

## Semantic Task Groupings

### Agent Tasks (30)
Tasks related to agent execution and learning:
- `run_agent_task`, `execute_agent_chain`
- `generate_agent_dreams`, `run_agent_conversations`
- `process_agent_learning`, `share_knowledge_between_agents`
- Agent evolution, mood, and consultation tasks

### Spider Tasks (19)
Data collection from external sources:
- `run_spider_batch`, `run_individual_spider`
- `fetch_trending_topics`, `collect_spider_data`
- Spider health checks and embeddings

### Content Tasks (16)
Content generation and processing:
- `generate_content_for_channel`
- `process_content_queue`, `schedule_content_publication`
- Content performance tracking

### Autonomous Tasks (12)
Self-running situation handlers:
- `run_autonomous_content_studio`
- `process_situation_triggers`
- `run_autonomous_intelligence_loop`

### Learning Tasks (10)
Collective intelligence system:
- `process_learning_queue`
- `sync_collective_knowledge`
- `update_agent_evolution_scores`

### Notification Tasks (10)
Discord and alert delivery:
- `send_discord_notification`
- `process_notification_queue`
- `send_system_alert`

### Revenue Tasks (10)
Income tracking and opportunities:
- `track_revenue_metrics`
- `process_opportunity_acceptance`
- `generate_revenue_report`

### Cleanup Tasks (6)
Maintenance and housekeeping:
- `cleanup_old_embeddings`
- `archive_old_logs`
- `prune_stale_sessions`

### Miscellaneous (43)
Various utility tasks that don't fit categories.

---

## Why Splitting Was Deferred

### Risk 1: Celery Autodiscovery
```python
# core/celery.py
app.autodiscover_tasks(['core'])
```
Moving tasks requires updating autodiscovery configuration.

### Risk 2: Circular Imports
Many tasks import from each other or share helpers defined in tasks.py.

### Risk 3: Transaction Boundaries
Some tasks are called within database transactions and have specific import timing.

### Risk 4: Beat Schedule References
```python
# core/celery.py
app.conf.beat_schedule = {
    'run-spider-batch': {
        'task': 'core.tasks.run_spider_batch',
        ...
    }
}
```
All beat schedules reference `core.tasks.*` paths.

---

## Future Refactoring Guide

If splitting is desired in a future session:

### Step 1: Create Package Structure
```
core/tasks/
├── __init__.py      # Import all tasks for backward compatibility
├── agent_tasks.py   # 30 tasks
├── spider_tasks.py  # 19 tasks
├── content_tasks.py # 16 tasks
├── autonomous_tasks.py # 12 tasks
├── learning_tasks.py   # 10 tasks
├── notification_tasks.py # 10 tasks
├── revenue_tasks.py     # 10 tasks
├── cleanup_tasks.py     # 6 tasks
└── utils.py         # Shared helpers
```

### Step 2: Update Celery Config
```python
# core/celery.py
app.autodiscover_tasks([
    'core.tasks.agent_tasks',
    'core.tasks.spider_tasks',
    # ... etc
])
```

### Step 3: Maintain Backward Compatibility
```python
# core/tasks/__init__.py
from .agent_tasks import *
from .spider_tasks import *
# ... etc

# This allows existing imports to continue working:
# from core.tasks import run_spider_batch
```

### Step 4: Update Beat Schedule
Change task paths OR use backward-compatible imports.

---

## Recommendation

The current single-file approach works fine for this codebase. The file is:
- Well-organized with related tasks grouped together
- Has clear docstrings
- Uses consistent patterns

**Splitting provides minimal benefit and carries risk.**

If maintainability becomes a concern, consider:
1. Adding section comments/dividers
2. Extracting shared helpers to utils
3. Better IDE navigation with class-based task organization

---

*Generated by Session 528 - December 21, 2025*
