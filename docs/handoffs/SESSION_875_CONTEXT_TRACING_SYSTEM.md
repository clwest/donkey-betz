---
originating_session: 875
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 875: Context Tracing System

## Summary
Implemented a comprehensive context tracing system to diagnose the root cause of `'list' object has no attribute 'get'` errors in agent execution. This follows the 6-point recommendation from ChatGPT to add forensic tracing across the execution pipeline.

## Problem Statement
ResearchAgent (and potentially other agents) were receiving `context` as a `list` instead of the expected `dict`, causing AttributeError when calling `.get()`. The root cause was unknown - whether it originated from:
- LLM output generating malformed next_steps
- Parser mishandling the output
- Celery serialization/deserialization issues
- Router or agent entry point problems

## Solution Implemented

### 1. ContextTracer Service (`core/services/context_tracing.py`)
New service with:
- **Trace ID generation**: Unique IDs for correlating events across pipeline stages
- **6 logging methods** for each mutation point:
  - `log_llm_output()` - Raw LLM response
  - `log_parser_output()` - After parsing into structured data
  - `log_pre_enqueue()` - Before Celery serializes the task
  - `log_post_deserialize()` - After Celery deserializes the task
  - `log_router()` - At AgentRouter entry
  - `log_agent()` - At agent execute() entry
- **Schema validation**: `validate_next_steps()` checks if next_steps is List[str]
- **Auto-repair**: `auto_repair_context()` converts invalid types to empty dict
- **Alerting**: Sends Discord alerts for bad context events

### 2. BadContextEvent Model
New database model for persisting forensic data:
```python
class BadContextEvent(models.Model):
    trace_id = models.CharField(max_length=64, db_index=True)
    stage = models.CharField(max_length=32, choices=STAGE_CHOICES)
    agent_name = models.CharField(max_length=128, blank=True)
    action_name = models.CharField(max_length=128, blank=True)
    task_name = models.CharField(max_length=256, blank=True)
    context_type = models.CharField(max_length=64)
    context_preview = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    extra_data = models.JSONField(default=dict)
    source = models.CharField(max_length=256, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 3. Integration Points
Tracing added at:
- `core/tasks.py:execute_agent_task()` - post_deserialize stage
- `intelligence/tasks.py:execute_agent_task()` - post_deserialize stage
- `core/services/conversation_action_dispatcher.py:dispatch_actions()` - pre_enqueue stage + next_steps validation
- `core/agent_router.py:route()` - router stage

## Files Changed
| File | Changes |
|------|---------|
| `core/services/context_tracing.py` | **NEW** - ContextTracer service |
| `core/models_unified_system.py` | Added BadContextEvent model |
| `core/migrations/0209_add_bad_context_event.py` | Migration for new model |
| `core/tasks.py` | Added tracing at Celery entry point |
| `intelligence/tasks.py` | Added tracing at Celery entry point |
| `core/services/conversation_action_dispatcher.py` | Added pre_enqueue tracing + schema validation |
| `core/agent_router.py` | Added router stage tracing |

## Related PRs
- PR #553 - Initial defensive checks (merged)
- PR #554 - Context tracing system (this session)

## How to Use

### Query Bad Context Events
```python
from core.models_unified_system import BadContextEvent

# Get recent events
events = BadContextEvent.objects.order_by('-created_at')[:10]

# Get events for specific agent
events = BadContextEvent.get_recent_by_agent('ResearchAgent')

# Get events by trace ID
events = BadContextEvent.get_recent_by_trace('trace-id-here')

# Get stage summary (last 24 hours)
summary = BadContextEvent.get_stage_summary(hours=24)
```

### Trace a Specific Execution
When debugging, look for log lines with `[TRACE:xxx]` prefix to follow context through the pipeline.

## Next Steps (Future Sessions)
1. **Add LLM output tracing**: Integrate `log_llm_output()` in ConversationOrchestrator where DecisionSummary is generated
2. **Add parser tracing**: Integrate `log_parser_output()` after next_steps parsing
3. **Add agent entry tracing**: Integrate `log_agent()` in BaseAgent.execute()
4. **Monitor BadContextEvent table**: Set up alerts when events accumulate
5. **Analyze patterns**: Once we have data, identify where context corruption originates

## Testing
```bash
# Verify migration applied
python manage.py migrate core

# Verify imports work
python manage.py shell -c "from core.services.context_tracing import ContextTracer; from core.models_unified_system import BadContextEvent; print('OK')"

# Check for any bad context events
python manage.py shell -c "from core.models_unified_system import BadContextEvent; print(f'Events: {BadContextEvent.objects.count()}')"
```

## Session Stats
- Duration: Continuation of Session 874/875
- PRs Created: 1 (PR #554)
- Files Changed: 7
- New Models: 1 (BadContextEvent)
- New Services: 1 (ContextTracer)
