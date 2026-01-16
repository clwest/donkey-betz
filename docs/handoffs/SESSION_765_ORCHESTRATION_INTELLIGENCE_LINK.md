# Session 765: Orchestration Intelligence Link

**Date:** January 15, 2026
**Built On:** Session 764 Orchestration Layer
**Status:** Complete

## Overview

This session addressed a critical gap in the orchestration layer: **workflow steps were disconnected from the core agent intelligence systems**. Users could see that steps executed, but couldn't see:
- What context was injected (spider data, learning patterns, advisor insights)
- What tools the agent used
- What memories were created
- The full execution details with task and reasoning

## Problem Statement

From user feedback:
> "These executions don't make sense to me. We can't click on them to find out what they are doing... what is happening to all of that [learning, conversing, sharing, tools, dreaming]? That's the core layer that we haven't connected to everything yet."

The orchestration layer (Session 764) tracked workflow execution, but `OrchestrationStepExecution` had no link to the underlying `AgentExecution` record where all the intelligence data is stored.

## Solution Architecture

```
┌─────────────────────────┐
│   Frontend UI           │
│   (click step to view)  │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐
│   getStepIntelligence   │
│   API Endpoint          │
└───────────┬─────────────┘
            │
┌───────────▼─────────────┐     ┌─────────────────────────┐
│OrchestrationStepExecution├────►│    AgentExecution       │
│   execution_id (NEW)    │     │    (full intelligence)  │
└─────────────────────────┘     └───────────┬─────────────┘
                                            │
                        ┌───────────────────┼───────────────────┐
                        │                   │                   │
              ┌─────────▼─────┐  ┌──────────▼────────┐  ┌───────▼───────┐
              │ Context       │  │   AgentMemory    │  │  Tool Calls   │
              │ Injected      │  │   Records        │  │  Made         │
              └───────────────┘  └──────────────────┘  └───────────────┘
```

## Changes Made

### 1. Backend Model (`core/models_orchestration.py`)

Added `execution_id` field to link to `AgentExecution`:

```python
# Session 765: Link to underlying AgentExecution for intelligence data
execution_id = models.UUIDField(
    null=True,
    blank=True,
    help_text="ID of the AgentExecution record for accessing memories, learning, and full execution data"
)
```

### 2. AgentResult Class (`core/agents/base_agent.py`)

Added `execution_id` field to pass back from router:

```python
# Session 765: Link to AgentExecution record for intelligence data
execution_id: Optional[str] = None
```

### 3. AgentRouter (`core/agent_router.py`)

Modified `route()` to set execution_id on result:

```python
# Session 765: Set execution_id on result for orchestration linking
if execution_record and hasattr(execution_record, 'id'):
    result.execution_id = str(execution_record.id)
```

### 4. Step Executor (`core/services/orchestration_step_executor.py`)

Captures execution_id from AgentRouter result:

```python
# Session 765: Capture execution_id for intelligence linking
execution_id = None
if hasattr(result, 'execution_id') and result.execution_id:
    execution_id = result.execution_id
    step_exec.execution_id = execution_id
    step_exec.save(update_fields=['execution_id'])
```

### 5. New API Endpoint (`core/views_orchestration.py`)

Added `OrchestrationStepIntelligenceView`:

```
GET /api/orchestration/executions/{execution_id}/steps/{step_number}/intelligence/
```

Returns:
- `step_info`: Basic step execution data
- `agent_execution`: Full AgentExecution record with task, tokens, cost
- `context_injected`: What context was injected (spider, learning, advisor, etc.)
- `tool_calls`: Tools the agent used
- `memories_created`: Memories generated during execution

### 6. Frontend API (`frontend/src/lib/api.ts`)

Added TypeScript interfaces and API function:

```typescript
export interface StepIntelligenceData {
  step_info: { ... }
  agent_execution: { ... } | null
  memories_created: StepIntelligenceMemory[]
  context_injected: { spider_data?, learning_patterns?, advisor_insights?, ... }
  tool_calls: Array<{ name?, function?, arguments? }>
}

orchestrationApi.getStepIntelligence(executionId, stepNumber)
```

### 7. Frontend UI (`frontend/src/pages/AgentsPage.tsx`)

Enhanced execution detail modal:
- Steps are now clickable
- Clicking a step shows intelligence panel with:
  - Context Injected badges (Spider Data, Learning Patterns, Advisor Insights, etc.)
  - Tool Calls list
  - Memories Created with types and content
  - Execution Details (task, tokens, cost, execution ID)

## Database Migration

Created `core/migrations/0169_add_execution_id_to_step.py`:

```python
migrations.AddField(
    model_name="orchestrationstepexecution",
    name="execution_id",
    field=models.UUIDField(blank=True, null=True, ...)
)
```

## Files Modified

| File | Changes |
|------|---------|
| `core/models_orchestration.py` | Added `execution_id` field to OrchestrationStepExecution |
| `core/agents/base_agent.py` | Added `execution_id` to AgentResult dataclass |
| `core/agent_router.py` | Set `execution_id` on result after agent execution |
| `core/services/orchestration_step_executor.py` | Capture and store execution_id |
| `core/views_orchestration.py` | Added OrchestrationStepIntelligenceView endpoint |
| `frontend/src/lib/api.ts` | Added StepIntelligenceData types and getStepIntelligence API |
| `frontend/src/pages/AgentsPage.tsx` | Enhanced modal with clickable steps and intelligence panel |

## Files Created

| File | Purpose |
|------|---------|
| `core/migrations/0169_add_execution_id_to_step.py` | Database migration for new field |

## What Users See Now

When viewing an execution and clicking on a step:

1. **Context Injected** - Colored badges showing what intelligence was provided:
   - 🕷️ Spider Data (X trends)
   - 📚 Learning Patterns
   - 🧙 Advisor Insights
   - 📊 Performance Feedback
   - ✨ Sci-Fi Context
   - 🧠 Knowledge State

2. **Tool Calls** - List of tools the agent used during execution

3. **Memories Created** - Any memories generated, with:
   - Type (success, failure, technique, insight, etc.)
   - Valence (positive/negative/neutral)
   - Content preview

4. **Execution Details** - Full execution record:
   - Task description
   - Execution time (ms)
   - Tokens used
   - Cost
   - Execution ID (clickable link potential)

## Key Insight

The **orchestration layer now surfaces the core intelligence pipeline** that was always happening behind the scenes. When an agent executes:

1. **AgentRouter** gathers spider data, learning patterns, advisor insights, and more
2. **Agent executes** with this enriched context
3. **Memories are created** based on success/failure
4. All of this is now **visible** through the step intelligence panel

## Verification

1. Build passes: `npm run build` ✓
2. Migration applied: `python manage.py migrate` ✓
3. Server running: Daphne restarted ✓
4. API endpoint: `/api/orchestration/executions/{id}/steps/{step}/intelligence/` ✓

## Next Steps

1. **Execute a workflow** to generate real intelligence data
2. **Click on steps** to see the intelligence panel populate
3. **Verify memories** are being created and linked
4. Consider adding links to Memory Palace for deep exploration
5. Consider adding conversation/collaboration history if multi-agent

## Related Sessions

| Session | Topic |
|---------|-------|
| 764 | Orchestration Layer (base implementation) |
| 763 | Mission Control System (approval gates) |
| 744 | Integration Roadmap (context injection) |
| 758 | Integration Health Observability |
