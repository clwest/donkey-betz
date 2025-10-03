# CRITICAL: Celery Task Flow Analysis & Agent Hanging Issues

**Date**: August 14, 2025  
**Severity**: CRITICAL  
**Status**: ANALYSIS COMPLETE - MULTIPLE ISSUES IDENTIFIED  

## Executive Summary

The agent execution system has multiple critical issues causing agents to hang indefinitely. Analysis reveals **3 stuck agents** (IDs: 111, 113, 114) that have been in "working" state for over 2 hours, and a pattern of execution failures in the Celery task flow.

## 🔴 CRITICAL FINDINGS

### 1. **Stuck Agents Problem**
```
Current Stuck Agents (> 10 minutes in working state):
- Agent 114: AI Hallucination Mitigation Advisor - 0% progress - Stuck for 2h 46m
- Agent 113: AI Hallucination Mitigation Advisor - 33% progress - Stuck for 2h 47m  
- Agent 111: Test Agent - 66% progress - Stuck for 2h 47m
- Agent 156: Business Builder Agent - 0% progress - Stuck for 0m (just started)
```

### 2. **Async/Sync Context Mixing Issues**

#### Problem Areas Identified:
1. **execute_agent_with_real_ai** (tasks.py:326-417)
   - Creates new event loop inside Celery task
   - Line 395-403: `asyncio.new_event_loop()` called within sync context
   - This can cause deadlocks when nested async operations occur

2. **EnhancedSyncAgentExecutor** (enhanced_sync_executor.py)
   - Mixes async and sync operations unsafely
   - Uses ThreadPoolExecutor without proper cleanup
   - Memory context initialization can fail silently (lines 80-98)

3. **OrchestrationMonitor** (orchestration_monitor.py)
   - Deprecated module still being referenced
   - Check completion logic creates event loops repeatedly

### 3. **Task Execution Flow Problems**

#### Current Flow:
```
1. User Request → AgentOrchestrator.execute_complex_task()
2. Creates TaskOrchestration & AgentInstances
3. Calls execute_agents_async() Celery task
4. For each agent:
   a. Tries execute_agent_with_real_ai.delay() 
   b. Falls back to threading if Celery fails
5. execute_agent_with_real_ai():
   a. Uses sync_executor.execute_agent_sync()
   b. Creates new event loop
   c. Runs orchestration monitor check
```

#### Issues in Flow:
- **No proper timeout handling** - soft_time_limit=300s but agents stuck for hours
- **Fallback to threading** (tasks.py:479-490) bypasses Celery's task management
- **Event loop creation** inside already running loops causes RuntimeError
- **No cleanup mechanism** for stuck agents except manual intervention

### 4. **Configuration Issues**

```python
# Current Settings (server/settings.py):
CELERY_TASK_TIME_LIMIT = 300  # 5 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 240  # 4 minutes soft limit
CELERY_WORKER_MAX_TASKS_PER_CHILD = 100
CELERY_WORKER_MAX_MEMORY_PER_CHILD = 200000  # 200MB

# Problems:
- Timeouts not being enforced for threaded tasks
- Memory limits too low for AI operations
- Worker pool using 'prefork' which doesn't handle async well
```

### 5. **Missing Error Recovery**

1. **No automatic retry for stuck agents**
2. **cleanup_stuck_agents task exists but not scheduled** (tasks.py:1228-1259)
3. **No circuit breaker for failing API calls**
4. **No dead letter queue for failed tasks**

## 🔧 ROOT CAUSES

### Primary Cause: Event Loop Conflicts
The main issue is improper handling of async/sync boundaries:
- Celery tasks are synchronous by nature
- Agent executors try to run async code using `asyncio.new_event_loop()`
- When multiple agents run simultaneously, event loops conflict
- Threading fallback bypasses Celery's management, losing timeout protection

### Secondary Causes:
1. **Deprecated sync_executor still in use** despite deprecation warning
2. **No proper task cancellation** when timeouts occur
3. **Missing health checks** for agent execution
4. **Inadequate logging** of execution failures

## 🚨 IMMEDIATE ACTIONS NEEDED

### 1. Kill Stuck Agents
```bash
# Run this to clean up stuck agents
python manage.py shell -c "
from agent_orchestra.models import AgentInstance
from django.utils import timezone
stuck = AgentInstance.objects.filter(
    id__in=[111, 113, 114, 156],
    current_status='working'
)
for agent in stuck:
    agent.current_status = 'failed'
    agent.error_message = 'Killed due to hanging - Session 146'
    agent.save()
print(f'Cleaned {stuck.count()} stuck agents')
"
```

### 2. Enable Cleanup Task
Add to beat_schedule in server/celery.py:
```python
'cleanup-stuck-agents': {
    'task': 'agent_orchestra.tasks.cleanup_stuck_agents',
    'schedule': crontab(minute='*/5'),  # Every 5 minutes
},
```

### 3. Fix Async/Sync Boundaries
Replace the problematic execute_agent_with_real_ai with proper sync execution:
```python
@shared_task(bind=True, max_retries=2, soft_time_limit=300, time_limit=330)
def execute_agent_with_real_ai(self, agent_id: int):
    try:
        # Use ONLY synchronous code here
        from .sync_executor import execute_agent_sync
        
        # Set up timeout handler
        import signal
        def timeout_handler(signum, frame):
            raise TimeoutError("Agent execution timeout")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(300)  # 5 minute timeout
        
        try:
            success = execute_agent_sync(agent_id)
        finally:
            signal.alarm(0)  # Cancel alarm
            
        return success
    except TimeoutError:
        # Handle timeout properly
        agent = AgentInstance.objects.get(id=agent_id)
        agent.current_status = "timeout"
        agent.save()
        raise
```

## 📊 METRICS & MONITORING

### Current State:
- **4 Celery workers** running (concurrency=4)
- **Redis queue**: Empty (all tasks picked up)
- **Recent success rate**: ~66% (4/6 recent agents completed)
- **Stuck agent rate**: 3 agents stuck out of ~156 total

### Recommended Monitoring:
1. Add Flower for Celery monitoring: `celery -A server flower`
2. Track agent execution times in database
3. Alert on agents stuck > 5 minutes
4. Monitor event loop creation/destruction

## 🔄 LONG-TERM SOLUTIONS

### 1. Redesign Task Execution
- Use Celery's native async support (Celery 5.x)
- Or completely separate async and sync paths
- Implement proper task chaining with callbacks

### 2. Implement Circuit Breakers
```python
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
def call_openai_api():
    # API calls with circuit breaker protection
    pass
```

### 3. Add Health Checks
- Heartbeat for long-running agents
- Progress reporting every 30 seconds
- Automatic restart for stuck workers

### 4. Proper Queue Management
```python
CELERY_TASK_ROUTES = {
    'agent_orchestra.tasks.execute_agent_with_real_ai': {
        'queue': 'agents',
        'routing_key': 'agent.execute',
        'priority': 5
    },
    'agent_orchestra.tasks.cleanup_stuck_agents': {
        'queue': 'maintenance',
        'routing_key': 'maintenance.cleanup',
        'priority': 1
    }
}
```

## 📝 TESTING RECOMMENDATIONS

### 1. Load Testing
```python
# Test concurrent agent execution
for i in range(10):
    execute_agent_with_real_ai.delay(agent_id)
# Monitor for hanging/conflicts
```

### 2. Timeout Testing
```python
# Test timeout handling
@shared_task(soft_time_limit=5)
def test_timeout():
    import time
    time.sleep(10)  # Should timeout
```

### 3. Memory Testing
Monitor memory usage during agent execution to validate limits

## ⚠️ RISKS IF NOT ADDRESSED

1. **System will become unusable** as more agents get stuck
2. **Database will fill** with incomplete agent records
3. **Users will experience timeouts** waiting for responses
4. **Memory leaks** from unclosed event loops
5. **Redis queue backlog** if workers keep dying

## ✅ SUCCESS CRITERIA

After fixes are applied:
1. No agents stuck > 5 minutes
2. 95%+ agent completion rate
3. Proper timeout handling with graceful failures
4. Clean worker logs without event loop errors
5. Monitoring shows healthy task throughput

## 🎯 PRIORITY ORDER

1. **IMMEDIATE**: Kill stuck agents and restart workers
2. **TODAY**: Fix async/sync boundaries in execute_agent_with_real_ai
3. **THIS WEEK**: Implement cleanup task and monitoring
4. **NEXT SPRINT**: Redesign entire task execution architecture

---

**Analysis Complete**  
**Next Steps**: Implement immediate fixes and monitor for 24 hours