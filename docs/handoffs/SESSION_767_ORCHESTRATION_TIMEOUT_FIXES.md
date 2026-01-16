# Session 767: Orchestration Timeout Fixes

**Date:** January 16, 2026
**Focus:** Fix workflow execution timeout bugs and orphaned step cleanup

## Problem

User reported overnight workflow executions that timed out. Investigation revealed:

1. **8 timed out executions** - 4 HiveMind and 4 Opportunity workflows
2. **Strange timing** - Some had `timeout_at` BEFORE `started_at`
3. **Orphaned steps** - 5 step executions stuck in "running" status after parent timed out
4. **ContentWriterAgent bottleneck** - All timed-out executions got stuck on ContentWriterAgent

## Root Causes Found

### Bug #1: Timeout calculated from creation time, not start time
```python
# BEFORE (line 117 in orchestration_engine.py):
execution = OrchestrationExecution.objects.create(
    ...
    timeout_at=timezone.now() + timedelta(seconds=workflow.timeout_seconds)  # Set at creation
)
```

When executions are queued async, there's a delay between creation and actual start. The timeout was counting from creation, not start, causing:
- Shorter effective timeout windows
- In extreme cases, `timeout_at < started_at` (timeout already passed before execution began)

### Bug #2: Orphaned step executions not cleaned up
When `check_orchestration_timeouts()` marked an execution as timed_out, it didn't update the associated step executions that were in "running" state.

## Fixes Applied

### Fix 1: Calculate timeout at execution start (orchestration_engine.py)

```python
# Creation (line 119): Set timeout_at to None initially
execution = OrchestrationExecution.objects.create(
    ...
    timeout_at=None  # Session 767: Set at start time, not creation time
)

# Execution start (lines 256-259): Calculate timeout from actual start time
execution.started_at = execution.started_at or timezone.now()
if not execution.timeout_at:
    execution.timeout_at = timezone.now() + timedelta(seconds=workflow.timeout_seconds)
execution.save(update_fields=['status', 'started_at', 'timeout_at'])
```

### Fix 2: Clean up orphaned steps on timeout (tasks.py)

```python
@shared_task
def check_orchestration_timeouts():
    ...
    for execution in timed_out:
        execution.status = 'timed_out'
        execution.error_message = 'Workflow timeout exceeded'
        execution.completed_at = now
        execution.save()

        # Session 767: Also mark any running step executions as failed
        running_steps = execution.step_executions.filter(status='running')
        for step in running_steps:
            step.status = 'failed'
            step.error_message = 'Timed out with parent orchestration'
            step.completed_at = now
            step.save()
            steps_cleaned += 1
```

### Manual Cleanup

Cleaned up existing orphaned data:
- 4 orphaned steps from already-timed-out executions → marked failed
- 1 additional stale "running" execution (11+ hours old) → marked timed_out

## Results After Fixes

| Metric | Before | After |
|--------|--------|-------|
| Running executions | 1 (stale) | 0 |
| Running steps (orphaned) | 5 | 0 |
| Timed out executions | 8 | 9 |
| Completed executions | 11 | 11 |
| Failed steps | 0 | 5 |
| Completed steps | 38 | 38 |

## Files Modified

1. **core/services/orchestration_engine.py**
   - Line 119: Set `timeout_at=None` at creation
   - Lines 256-259: Calculate `timeout_at` from actual start time

2. **core/tasks.py**
   - Lines 24397-24408: Added step cleanup when execution times out
   - Added `steps_cleaned` counter to return value

## Testing

Future executions will now:
1. Calculate timeout from actual start time (not creation time)
2. Properly clean up running steps when execution times out
3. Report steps_cleaned count in timeout task results

## Related Sessions

- Session 764: Orchestration Layer (original implementation)
- Session 766: Human Page Data Quality Fixes (previous session)

## ContentWriterAgent Investigation

### Problem
All timed-out executions got stuck on ContentWriterAgent. Investigation revealed:
- 3 `AgentExecution` records stuck in `in_progress` status for 11+ hours
- Normal ContentWriterAgent execution time: 30-67 seconds (avg 36.4s)
- The stuck executions never completed, suggesting API hangs

### Root Causes

1. **Step executor didn't enforce timeout**: The `timeout` variable was set (line 86) but never actually enforced. The `router.route()` call could hang indefinitely.

2. **No OpenAI client timeout**: The OpenAI API call in ContentWriterAgent had no timeout, allowing it to hang indefinitely on network issues.

### Additional Fixes Applied

#### Fix 3: Timeout enforcement in step executor (orchestration_step_executor.py)

```python
# Session 767: Execute with timeout enforcement using concurrent.futures
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(
        self.router.route,
        agent_name=step.agent,
        task=task,
        context=agent_context,
    )
    try:
        result = future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        raise TimeoutError(f"Agent {step.agent} timed out after {timeout} seconds")
```

#### Fix 4: OpenAI client timeout in ContentWriterAgent (content_writer_agent.py)

```python
# Session 767: Add timeout to OpenAI client to prevent hanging
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    timeout=120.0  # 2 minute timeout for API calls
)

response = client.chat.completions.create(
    ...
    timeout=120.0  # Session 767: Explicit request timeout
)
```

### Cleanup Done
- 3 stuck `AgentExecution` records → marked as failed

## Files Modified (Complete List)

1. **core/services/orchestration_engine.py**
   - Line 119: Set `timeout_at=None` at creation
   - Lines 256-259: Calculate `timeout_at` from actual start time

2. **core/tasks.py**
   - Lines 24397-24408: Added step cleanup when execution times out

3. **core/services/orchestration_step_executor.py**
   - Added `concurrent.futures` import
   - Lines 114-127: Wrapped `router.route()` with timeout enforcement

4. **core/agents/content_writer_agent.py**
   - Lines 792-796: Added `timeout=120.0` to OpenAI client
   - Line 817: Added `timeout=120.0` to completions request

#### Fix 5: ThreadPoolExecutor context manager blocking (orchestration_step_executor.py)

**Issue Found:** The `with ThreadPoolExecutor(...)` context manager was blocking on exit even after timeout, because `executor.shutdown(wait=True)` is called automatically when exiting the `with` block.

```python
# BEFORE - Context manager blocks until thread finishes
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(...)
    result = future.result(timeout=timeout)  # Timeout fires but...
    # __exit__ calls shutdown(wait=True), blocks until thread done!

# AFTER - Explicit executor management with non-blocking shutdown
executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
try:
    future = executor.submit(...)
    result = future.result(timeout=timeout)
except concurrent.futures.TimeoutError:
    executor.shutdown(wait=False, cancel_futures=True)  # Don't wait!
    raise TimeoutError(f"Agent timed out")
finally:
    executor.shutdown(wait=False)
```

## Known Issue: Step Status Not Updated on Timeout

**Symptom:** When step timeout fires, the `error_message` is set correctly but `status` sometimes remains "running" instead of being updated to "failed".

**Investigation:** The `mark_failed()` method is called and sets both status and error_message, but only error_message persists. This suggests a possible threading/transaction issue with Django ORM and ThreadPoolExecutor.

**Workaround:** The `check_orchestration_timeouts()` task already cleans up orphaned running steps, so this is self-healing. But the root cause needs further investigation.

## Verification Commands

```bash
# Check for orphaned running steps
.venv/bin/python manage.py shell -c "
from core.models_orchestration import OrchestrationStepExecution
orphaned = OrchestrationStepExecution.objects.filter(status='running').exclude(orchestration__status='running')
print(f'Orphaned running steps: {orphaned.count()}')"

# Check execution status distribution
.venv/bin/python manage.py shell -c "
from core.models_orchestration import OrchestrationExecution
from django.db.models import Count
stats = OrchestrationExecution.objects.values('status').annotate(count=Count('id'))
for s in stats:
    print(f\"{s['status']}: {s['count']}\")"

# Check for stuck AgentExecutions
.venv/bin/python manage.py shell -c "
from core.models_unified_system import AgentExecution
stuck = AgentExecution.objects.filter(status='in_progress')
print(f'Stuck AgentExecutions: {stuck.count()}')"
```

## Summary of Session 767 Fixes

| Bug | Root Cause | Fix | Status |
|-----|------------|-----|--------|
| timeout_at < started_at | Timeout set at creation, not start | Set timeout at actual start time | ✅ Fixed |
| Orphaned running steps | Steps not cleaned up on parent timeout | Added cleanup in check_orchestration_timeouts | ✅ Fixed |
| Step timeout not enforced | ThreadPoolExecutor context manager blocked | Use explicit executor without context manager | ✅ Fixed |
| OpenAI calls hang | No timeout on client | Added 120s timeout to BaseAgent.client | ✅ Fixed (was already in BaseAgent) |
| OpenAI in ContentWriter | Direct OpenAI client usage | Added 120s timeout | ✅ Fixed |
| Step status not updated | Threading/transaction issue | Needs investigation | ⚠️ Known Issue |
