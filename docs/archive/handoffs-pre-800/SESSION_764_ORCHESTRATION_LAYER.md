# Session 764: Orchestration Layer Implementation

**Date:** January 15, 2026
**Built On:** Session 763 Mission Control System
**Status:** Complete

## Overview

This session implemented a comprehensive **Orchestration Layer** that enables multi-agent workflow execution with checkpointing, human-in-the-loop approval gates, retry logic, and Celery integration. The system builds on the Mission Control infrastructure from Session 763 to provide approval workflows.

## Problem Statement

The platform had 72 agents that could execute individually, but lacked:
1. **Multi-step workflows** - No way to chain agent executions in sequence
2. **Checkpoint/Resume** - Failed workflows couldn't be resumed from last successful step
3. **Human approval gates** - No way to pause for human review before/after critical steps
4. **Cost budgets** - No enforcement of spending limits across workflow executions
5. **Parallel execution** - No support for running independent steps concurrently
6. **Dependency resolution** - No way to express step dependencies for optimal ordering

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    OrchestrationEngine                          │
│  (Central coordinator for workflow execution)                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
┌───▼───┐           ┌─────▼─────┐         ┌─────▼─────┐
│ Step  │           │ Approval  │         │Checkpoint │
│Executor│          │   Gate    │         │  Manager  │
└───┬───┘           └─────┬─────┘         └───────────┘
    │                     │
    │              ┌──────▼──────┐
    │              │MissionControl│  ← Existing (Session 763)
    │              │  Executor    │
    │              └─────────────┘
    │
┌───▼────┐
│Agent   │  ← Existing
│Router  │
└────────┘
```

## Files Created

### 1. Data Models (`core/models_orchestration.py`)

**OrchestrationExecution** - Tracks workflow runs
- UUID primary key
- Links to CustomWorkflow and User
- Status tracking: pending, running, waiting_approval, completed, failed, cancelled, paused
- Checkpoint data (JSONField) for resume capability
- Cost/token aggregation
- Input/output data storage

**OrchestrationStepExecution** - Individual step tracking
- Links to execution and workflow step
- Per-step timing, cost, tokens
- Retry count tracking
- Error message storage
- Input/output data per step

**OrchestrationApprovalGate** - Links to HumanAttentionItem
- UUID reference to attention item (avoids FK complexity)
- Status: pending, approved, rejected, modified, expired
- Approval config and expiration
- Methods: approve(), reject(), modify(), auto_approve()

### 2. Core Services

**`core/services/orchestration_engine.py`** (~450 lines)
- Main orchestration coordinator
- `execute_workflow()` - Start new workflow execution
- `resume_execution()` - Resume from checkpoint
- `cancel_execution()` - Cancel running execution
- Supports three execution modes:
  - **sequential** - Steps run one after another
  - **parallel** - All steps run concurrently
  - **dependency** - Steps run based on depends_on_steps

**`core/services/orchestration_step_executor.py`** (~200 lines)
- Wraps AgentRouter for step execution
- Tracks timing, cost, tokens per step
- Handles timeouts and errors
- Builds task descriptions from templates with variable substitution

**`core/services/orchestration_checkpoint.py`** (~60 lines)
- Save checkpoint after each successful step
- Load checkpoint for resume
- Get resume point (next step number)
- Clear checkpoint after completion

**`core/services/orchestration_dependencies.py`** (~150 lines)
- `get_ready_steps()` - Find steps with satisfied dependencies
- `get_blocked_steps()` - Find steps blocked by failure
- `build_execution_order()` - Create parallelizable layers
- `validate_dependencies()` - Check for cycles and invalid refs

**`core/services/orchestration_approval.py`** (~370 lines)
- Creates approval gates with HumanAttentionItem
- Registers 3 Mission Control handlers:
  - `approve_orchestration_step` - Approve and resume
  - `reject_orchestration_step` - Reject and fail
  - `modify_orchestration_step` - Approve with changes
- Auto-approval check for expired gates

### 3. API Endpoints (`core/views_orchestration.py`)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/orchestration/workflows/` | GET | List available workflows |
| `/api/orchestration/workflows/{id}/execute/` | POST | Execute a workflow |
| `/api/orchestration/executions/` | GET | List executions |
| `/api/orchestration/executions/{id}/` | GET | Get execution details |
| `/api/orchestration/executions/{id}/resume/` | POST | Resume paused execution |
| `/api/orchestration/executions/{id}/cancel/` | POST | Cancel execution |

### 4. Celery Tasks (`core/tasks.py`)

```python
@shared_task
def execute_orchestration_async(execution_id: str):
    """Execute an orchestration workflow asynchronously."""

@shared_task
def check_orchestration_timeouts():
    """Check for timed-out orchestration executions."""

@shared_task
def check_orchestration_auto_approvals():
    """Check for auto-approvals on expired approval gates."""
```

### 5. Celery Beat Schedule (`core/celery.py`)

```python
'check-orchestration-timeouts': {
    'task': 'core.tasks.check_orchestration_timeouts',
    'schedule': crontab(minute='*/5'),  # Every 5 minutes
},
'check-orchestration-auto-approvals': {
    'task': 'core.tasks.check_orchestration_auto_approvals',
    'schedule': crontab(minute='*/5'),  # Every 5 minutes
},
```

### 6. Frontend API (`frontend/src/lib/api.ts`)

TypeScript interfaces and API client:
- `OrchestrationWorkflow` - Workflow definition
- `OrchestrationExecution` - Execution status
- `OrchestrationStepExecution` - Step details
- `OrchestrationExecutionDetail` - Full execution with steps and gates
- `orchestrationApi` - API methods for all endpoints

## Files Modified

### `core/models_unified_system.py`

Extended **CustomWorkflow** with:
```python
execution_mode = models.CharField(max_length=20, default='sequential')
max_retries = models.IntegerField(default=3)
timeout_seconds = models.IntegerField(default=3600)
require_approval_on_error = models.BooleanField(default=True)
cost_budget = models.DecimalField(max_digits=10, decimal_places=4, null=True)
```

Extended **CustomWorkflowStep** with:
```python
timeout_seconds = models.IntegerField(default=300)
requires_approval = models.BooleanField(default=False)
approval_config = models.JSONField(default=dict)
depends_on_steps = models.JSONField(default=list)  # [1, 2] = depends on steps 1 and 2
rollback_step = models.IntegerField(null=True)
cost_limit = models.DecimalField(max_digits=10, decimal_places=4, null=True)
```

Expanded **AGENT_CHOICES** to include all 72 routable agents.

### `core/urls.py`

Added orchestration API routes:
```python
from core.views_orchestration import get_urlpatterns as get_orchestration_urls
urlpatterns += [
    path('api/orchestration/', include((get_orchestration_urls(), 'orchestration'))),
]
```

## Key Features

### 1. Checkpoint/Resume
After each successful step, the execution state is saved:
- Current step number
- All step outputs
- Accumulated context
- Retry counts

On failure, the workflow can be resumed from the last checkpoint rather than starting over.

### 2. Approval Gates
Steps with `requires_approval=True` pause execution and create a HumanAttentionItem in Mission Control. Users can:
- **Approve** - Continue execution
- **Reject** - Fail the workflow
- **Modify** - Approve with parameter changes

### 3. Auto-Approval
Gates can be configured with:
```python
approval_config = {
    'approval_timeout_hours': 24,
    'auto_approve_on_timeout': True,
    'approval_message': 'Please review step output'
}
```

### 4. Cost Tracking
- Per-step cost from agent execution
- Aggregated total_cost on execution
- Optional cost_budget enforcement (aborts if exceeded)

### 5. Execution Modes

**Sequential** (default):
```
Step 1 → Step 2 → Step 3
```

**Parallel**:
```
Step 1 ─┬─ Step 2 ─┬─ Step 3
        └──────────┘
```

**Dependency-based**:
```
Step 1 (no deps) → Step 2 (depends on 1)
                 → Step 3 (depends on 1)
                 → Step 4 (depends on 2, 3)
```

### 6. Error Handling
On step failure:
- If `require_approval_on_error=True`, creates error review gate
- Human can choose: retry, skip, or abort
- Retry respects `max_retries` limit

## Database Migrations

Created two migrations:
1. `0167_orchestration_layer.py` - Adds fields to CustomWorkflow and CustomWorkflowStep
2. `0168_orchestration_new_models.py` - Creates the three orchestration tables

## Integration with Mission Control (Session 763)

The approval service registers handlers with MissionControlExecutor:
```python
mission_control_executor.register('approve_orchestration_step', self._handle_approve)
mission_control_executor.register('reject_orchestration_step', self._handle_reject)
mission_control_executor.register('modify_orchestration_step', self._handle_modify)
```

When a user takes action on an approval gate in the Human Page, Mission Control routes to these handlers which update the gate and resume/fail the execution.

## Usage Example

### Create a Workflow (Admin or API)

```python
workflow = CustomWorkflow.objects.create(
    name="Content Pipeline",
    execution_mode="sequential",
    max_retries=3,
    timeout_seconds=3600,
    require_approval_on_error=True,
)

# Step 1: Research
CustomWorkflowStep.objects.create(
    workflow=workflow,
    order=1,
    name="Research Topic",
    agent="ResearchAgent",
    config={'prompt_template': 'Research: {topic}'},
)

# Step 2: Write (requires approval)
CustomWorkflowStep.objects.create(
    workflow=workflow,
    order=2,
    name="Write Article",
    agent="ContentWriterAgent",
    requires_approval=True,
    approval_config={'approval_message': 'Review article before publishing'},
    depends_on_steps=[1],
)

# Step 3: Publish
CustomWorkflowStep.objects.create(
    workflow=workflow,
    order=3,
    name="Publish",
    agent="SocialMediaAgent",
    depends_on_steps=[2],
)
```

### Execute via API

```bash
curl -X POST /api/orchestration/workflows/{workflow_id}/execute/ \
  -H "Authorization: Token xxx" \
  -d '{"input": {"topic": "AI Trends 2026"}, "async": true}'
```

### Monitor Execution

```bash
curl /api/orchestration/executions/{execution_id}/ \
  -H "Authorization: Token xxx"
```

### Resume After Approval

When step 2 completes and requires approval, a HumanAttentionItem appears in Mission Control. After approval:

```bash
curl -X POST /api/orchestration/executions/{execution_id}/resume/ \
  -H "Authorization: Token xxx"
```

## Testing Recommendations

1. **Unit Tests:**
   - Test OrchestrationEngine.execute_workflow() with mock agents
   - Test DependencyResolver ordering and cycle detection
   - Test CheckpointManager save/load
   - Test ApprovalGate state transitions

2. **Integration Tests:**
   - Execute a 3-step workflow end-to-end
   - Test checkpoint/resume on step failure
   - Test approval gate → Mission Control → resume flow
   - Verify cost aggregation across steps

3. **Manual Verification:**
   - Create workflow via admin
   - Execute via API
   - Check Human Page for approval items
   - Approve and verify workflow resumes
   - Check cost/token tracking

## Future Enhancements

1. **Workflow Templates** - Pre-built workflow patterns for common use cases
2. **Conditional Steps** - Skip steps based on previous output
3. **Rollback Support** - Execute rollback_step on failure
4. **Webhook Notifications** - Notify external systems on state changes
5. **Workflow Versioning** - Track changes to workflow definitions
6. **Visual Workflow Editor** - Frontend UI for building workflows

## Related Files

| File | Purpose |
|------|---------|
| `core/services/mission_control_executor.py` | Handler registration (Session 763) |
| `core/models_human_interface.py` | HumanAttentionItem model |
| `core/agent_router.py` | Agent execution routing |
| `core/agents/base_agent.py` | Base agent with cost tracking |

## Verification

All components verified working:
- Django check: No issues
- All imports successful
- Database tables created
- Mission Control handlers registered
- 6 API endpoints exposed
- Frontend TypeScript API ready
