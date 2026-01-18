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

## Modal Formatting Fixes

### Problem
User reported that execution detail modals were showing truncated data:
1. **Task descriptions cut off** at 500 characters
2. **Research Query content truncated** - showed "...all underpinned by inve" instead of full text
3. **Doubled Kaggle URLs** - `https://www.kaggle.com/c/https://www.kaggle.com/competitions/...`

### Root Causes

1. **Task field truncated**: `agent_router.py:1092` truncates task to 500 chars when saving AgentExecution, but full task is stored in `input_data['task']`

2. **Dream/HiveMind content truncated**: Pipeline files (`dream_execution_pipeline.py:272`, `hivemind_execution_pipeline.py:243`) truncate content to 500 chars in `description` field, but full content is stored in `config`

3. **Kaggle spider URL construction**: `kaggle_spider.py` prepended `https://www.kaggle.com/c/` to refs that were already full URLs

### Fixes Applied

#### Fix 6: Return full task from API (views_orchestration.py)
```python
# Session 767: Get full task from input_data (task field is truncated to 500 chars)
input_data = agent_exec.input_data or {}
full_task = input_data.get('task') or agent_exec.task
```

#### Fix 7: Build task with full config content (orchestration_step_executor.py)
```python
def _build_task(self, step, context):
    config = step.config or {}

    # Check for dream context (from dream_execution_pipeline)
    dream_ctx = config.get('dream_context', {})
    if dream_ctx:
        task_parts = [step.name.split(': ', 1)[-1] if ': ' in step.name else step.description.split('\n')[0]]
        task_parts.append("")
        task_parts.append("Context from dream:")
        task_parts.append(f"- Title: {dream_ctx.get('title', 'N/A')}")
        task_parts.append(f"- Content: {dream_ctx.get('content', 'N/A')}")  # Full content!
        task_parts.append(f"- Type: {dream_ctx.get('type', 'N/A')}")
        return '\n'.join(task_parts)

    # Similar for hivemind_context...
```

#### Fix 8: Kaggle spider URL construction (kaggle_spider.py)
```python
# Session 767: Handle ref that might be full URL or just slug
ref = comp.get('ref', '')
if ref.startswith('http'):
    comp_url = ref  # Already a full URL
elif '/' in ref:
    comp_url = f"https://www.kaggle.com/{ref}"  # Path like "competitions/name"
else:
    comp_url = f"https://www.kaggle.com/c/{ref}"  # Just a slug
```

### Data Fixes

Fixed existing bad data in database:

| Table | Records Fixed | Issue |
|-------|---------------|-------|
| AgentExecution | 31 | Doubled Kaggle URLs |
| OrchestrationStepExecution | 7 | Doubled Kaggle URLs |

Fix command used:
```python
import re
# Pattern: https://www.kaggle.com/c/https://www.kaggle.com/competitions/...
# Fixed to: https://www.kaggle.com/competitions/...
fixed_str = re.sub(
    r'https://www\.kaggle\.com/c/(https://www\.kaggle\.com/[^"]+)',
    r'\1',
    data_str
)
```

## Files Modified (Complete List)

1. **core/services/orchestration_engine.py**
   - Line 119: Set `timeout_at=None` at creation
   - Lines 256-259: Calculate `timeout_at` from actual start time

2. **core/tasks.py**
   - Lines 24397-24408: Added step cleanup when execution times out

3. **core/services/orchestration_step_executor.py**
   - Added `concurrent.futures` import
   - Lines 114-127: Wrapped `router.route()` with timeout enforcement
   - `_build_task()`: Use full content from `config.dream_context`/`config.hivemind_context`

4. **core/agents/content_writer_agent.py**
   - Lines 792-796: Added `timeout=120.0` to OpenAI client
   - Line 817: Added `timeout=120.0` to completions request

5. **core/views_orchestration.py**
   - Return full task from `input_data['task']` instead of truncated field
   - Added `full_context` to step intelligence API response (dream_context, hivemind_context from workflow step config)

6. **ai_core/spiders/specialized/kaggle_spider.py**
   - Check if `ref` is already full URL before prepending base

7. **frontend/src/pages/AgentsPage.tsx**
   - Added expandable sections for long content
   - Formatted ResearchAgent, ContentStrategyAgent outputs
   - Formatted Tool Results section (success badges, topic tags, ML analysis, opportunities)
   - Formatted Recommendations section (content_type, priority badges, keywords)
   - Use `full_context` from API for dream/hivemind content (not truncated stored data)

8. **frontend/src/lib/api.ts**
   - Added `full_context` type to `StepIntelligenceData` interface

## Missing Celery Worker Fix

### Problem
User reported system had low activity after running for 20 hours. Investigation revealed:
- **0 agent executions** in the last 3+ hours
- **Celery beat was scheduling tasks** but they weren't being processed
- Dreams (274) and conversations (346) had been created in the last 24 hours, but the latest dream was from 16+ hours ago

### Root Cause
The `long_running` Celery worker was NOT running after the system restart. Only `default`, `broadcast`, and `beat` workers had started.

Tasks routed to the `long_running` queue include:
- `generate_agent_dreams` (every 2 hours)
- `run_agent_conversation` (every 30 minutes)
- `execute_dream_implementations` (every 20 minutes)
- `collect_spider_data` (every 30 minutes)
- `run_unified_intelligence_pipeline` (hourly)
- `run_autonomous_content_studio` (4x daily)
- Various market/blockchain monitoring tasks

### Why It Happened
The Makefile has a check for existing workers:
```bash
@if pgrep -f "hostname=long_running" >/dev/null 2>&1; then \
    echo "-> Celery long_running worker already running"; \
```

However, the stale PID file (`.celery-long-running.pid`) contained PID 83588 which no longer existed. The process check passed but the worker wasn't actually running.

### Fix Applied
Started the missing worker manually:
```bash
OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES nohup .venv/bin/celery -A core worker \
  --loglevel=info \
  --pool=threads \
  --concurrency=2 \
  --queues=long_running \
  --hostname=long_running@%h > celery-long-running.log 2>&1 &
```

### Current Workers Running (Post-Fix)
| Worker | PID | Queues |
|--------|-----|--------|
| default | 88894 | default, agents, sports, content, ml |
| broadcast | 88924 | broadcast |
| **long_running** | **49640** | **long_running** |
| beat | 88943 | (scheduler) |

### Immediate Results
After starting the worker:
- Tasks immediately started processing
- 2 new conversations created within 10 minutes
- Agent conversation cycle running (CompetitorAnalysisAgent, CodeReviewAgent, CodeGeneratorAgent, BrandStrategyAgent participating)

### Recommendation
Consider adding process health monitoring to detect when workers die without updating PID files. The Makefile's existing check relies on `pgrep` which may not work correctly with stale PIDs.

## Learning System Improvements

Session 767 also included a comprehensive review and improvement of the agent learning system.

### Issues Identified

| Issue | Before | After |
|-------|--------|-------|
| Isolated agents | 25 agents with no learning connections | 0 (all connected) |
| Pattern mining | Only 1 LearningPattern from 64k events | 12 active patterns |
| Knowledge freshness | 28% stale sources, no decay | Auto-decay + freshness tracking |
| Teaching distribution | 99.98% self-learning | Cross-agent propagation enabled |
| SharedKnowledge | 50 entries | 121 entries (promoted) |

### Fixes Applied

#### Fix 1: Created 75 New AgentLearningConnection Records
25 isolated agents now have learning connections:
- Stock/Market agents (9): StockAnalystAgent, MarketMovementMonitorAgent, etc.
- Blockchain agents (5): BlockchainAuditCoordinator, SmartContractAuditorAgent, etc.
- Narrative/Content agents (6): NarrativeDriftCoordinator, AutonomousContentStudioCoordinator, etc.
- System/Orchestration agents (5): WorkflowOrchestrationAgent, OpportunityPipelineAgent, etc.

#### Fix 2: Pattern Mining Task (core/tasks.py)
Added `mine_learning_patterns()` Celery task that:
- Mines AgentLearning records to create LearningPattern entries
- Creates 4 pattern types: spider_effectiveness, agent_collaboration, learning_type_impact, top_teacher
- Runs every 12 hours at :45

#### Fix 3: Knowledge Freshness Maintenance (core/tasks.py)
Added `maintain_knowledge_freshness()` Celery task that:
- Decays freshness_score based on age (formula: max(0.1, 1.0 - days/60))
- Deactivates very stale sources (>90 days, <0.1 freshness)
- Marks expired sources as inactive
- Reports agents needing knowledge refresh
- Runs daily at 4:15 AM

#### Fix 4: Cross-Agent Learning Propagation (intelligence/spider_agent_connector.py)
Modified `_create_learning_record()` to propagate learning to connected agents:
- When agent learns from spider data, shares with up to 5 connected students
- Creates proper cross-agent learning records
- Updates AgentLearningConnection stats (total_transfers, avg_improvement_score)

#### Fix 5: Knowledge Promotion (core/tasks.py)
Added `promote_to_shared_knowledge()` Celery task that:
- Promotes high-confidence AgentKnowledgeSource entries (≥0.7 confidence)
- Promotes high-usefulness KnowledgeTransfer entries (≥0.8 usefulness)
- Creates SharedKnowledge entries accessible to all agents
- Runs weekly on Sunday at 5 AM

### Files Modified

1. **core/services/learning_pattern_engine.py**
   - Added `mine_patterns()` method (lines 485-738)
   - Added `maintain_knowledge_freshness()` method (lines 740-858)
   - Added `promote_to_shared_knowledge()` method (lines 860-989)

2. **intelligence/spider_agent_connector.py**
   - Modified `_create_learning_record()` to propagate learning
   - Added `_propagate_to_connected_agents()` method

3. **core/tasks.py**
   - Added `mine_learning_patterns()` task
   - Added `maintain_knowledge_freshness()` task
   - Added `promote_to_shared_knowledge()` task

4. **core/settings.py** (lines 1235-1252)
   - Added beat schedule for `mine-learning-patterns` (every 12h at :45)
   - Added beat schedule for `maintain-knowledge-freshness` (daily at 4:15 AM)
   - Added beat schedule for `promote-to-shared-knowledge` (weekly Sunday 5 AM)
   - **Note:** Schedules must be in `settings.py` not `celery.py` because Django's
     `CELERY_BEAT_SCHEDULE` setting overrides `app.conf.beat_schedule` via
     `config_from_object('django.conf:settings', namespace='CELERY')`

### Results

```
Learning Patterns: 1 → 12 active patterns
- spider_effectiveness: 9 (which agents benefit from spider data)
- learning_type_impact: 2 (spider_intelligence +15%, cross_agent_delegation)
- application_outcome: 1 (original)

Knowledge Freshness:
- Fresh (≥0.7): 255 sources (7%)
- Moderate (0.3-0.7): 3,133 sources (85%)
- Stale (<0.3): 297 sources (8%)

SharedKnowledge: 50 → 121 entries
- insight: 57 (from AgentKnowledgeSource)
- technique: 43 (from KnowledgeTransfer)
- skill: 13, pattern: 8 (existing)
```

## Summary of Session 767 Fixes

| Bug | Root Cause | Fix | Status |
|-----|------------|-----|--------|
| timeout_at < started_at | Timeout set at creation, not start | Set timeout at actual start time | ✅ Fixed |
| Orphaned running steps | Steps not cleaned up on parent timeout | Added cleanup in check_orchestration_timeouts | ✅ Fixed |
| Step timeout not enforced | ThreadPoolExecutor context manager blocked | Use explicit executor without context manager | ✅ Fixed |
| OpenAI calls hang | No timeout on client | Added 120s timeout to BaseAgent.client | ✅ Fixed (was already in BaseAgent) |
| OpenAI in ContentWriter | Direct OpenAI client usage | Added 120s timeout | ✅ Fixed |
| Task truncated in modal | API returned truncated field | Return full task from input_data | ✅ Fixed |
| Research content truncated | _build_task used truncated description | Use full content from config | ✅ Fixed |
| Doubled Kaggle URLs | Spider prepended base to full URLs | Check if ref is already full URL | ✅ Fixed |
| Existing bad URLs | Historical data had doubled URLs | Database fix (38 records) | ✅ Fixed |
| Step status not updated | Threading/transaction issue | Needs investigation | ⚠️ Known Issue |
| No activity for 16+ hours | long_running worker not started | Started missing worker | ✅ Fixed |
| Isolated agents (25) | No learning connections created | Created 75 new connections | ✅ Fixed |
| Pattern mining (1 pattern) | No task to mine AgentLearning | Added mine_learning_patterns task | ✅ Fixed |
| Knowledge freshness | No decay mechanism | Added maintain_knowledge_freshness task | ✅ Fixed |
| Teaching imbalance | No cross-agent propagation | Added propagation in spider connector | ✅ Fixed |
| SharedKnowledge growth | No promotion mechanism | Added promote_to_shared_knowledge task | ✅ Fixed |
