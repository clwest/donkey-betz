# Session 836: Experiment System Diagnosis & Fix

**Date:** January 26, 2026
**Focus:** Diagnose experiment system, fix Celery Beat, activate learning loop
**Status:** COMPLETED

---

## Summary

Investigated why experiments weren't being processed and found that **Celery Beat was not running**. Once started, the system immediately processed 247 experiments and created 251 learnings.

---

## Problem Statement

ChatGPT analysis of agent output suggested an "85% experiment failure rate" with integrity halts. Investigation revealed:

1. The "85%" was from simulated agent research output, not real telemetry
2. Experiments weren't failing - they were **never being evaluated**
3. Root cause: Celery Beat scheduler was not running

---

## Investigation Findings

### Before Fix

| Metric | Value | Issue |
|--------|-------|-------|
| Experiments Running | 235 | Stuck forever |
| Experiments Success | 16 | Only manual completions |
| Outcome Classification | 235 pending | Never evaluated |
| ExperimentLearnings | 4 | Almost none |
| Celery Beat | NOT RUNNING | **ROOT CAUSE** |
| monitor_running_experiments task | Never executed | Last run: None |

### Experiment System Architecture

```
AgentDecisionSummary
       │
       ▼
PilotReadinessGate (373 waived, 33 approved)
       │
       ▼
PilotExecution (was: 247 running)
       │
       ▼
Experiment (was: 235 running, 0 classified)
       │
       ▼
[MONITORING TASK - NEVER RAN]
       │
       ▼
ExperimentLearning (was: only 4)
       │
       ▼
DecisionTypeSuccessPattern (was: 0)
```

### Key Tasks That Were Not Running

1. **`monitor_running_experiments`** - Every 10 mins, checks halt conditions
2. **`evaluate_and_complete_pilots`** - Completes pilots based on age/outcomes
3. **`update_experiment_kpis`** - Hourly KPI updates

---

## Resolution

### 1. Stopped Manual Celery Worker

```bash
pkill -9 -f "celery"
```

### 2. Started Celery Properly via Makefile

```bash
make celery
```

This starts:
- Default Worker (4 threads) - queues: default, agents, sports, content, ml
- Long-Running Worker (2 threads) - queue: long_running
- Broadcast Worker (2 threads) - queue: broadcast
- **Beat Scheduler** - 228 scheduled tasks

### 3. Immediate Results

The `evaluate_and_complete_pilots` task ran and processed all pending experiments:

```
Task core.tasks.evaluate_and_complete_pilots succeeded:
{
  'evaluated': 247,
  'completed_success': 220,
  'completed_partial': 24,
  'completed_failure': 3,
  'experiments_updated': 247,
  'learnings_created': 247,
  'patterns_updated': 247
}
```

---

## After Fix

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Experiments Running | 235 | 20 | -215 |
| Experiments Success | 16 | 224 | +208 |
| Experiments Partial | 0 | 24 | +24 |
| Experiments Failure | 0 | 3 | +3 |
| ExperimentLearnings | 4 | 251 | +247 |
| DecisionTypeSuccessPatterns | 0 | 29 | +29 |
| Celery Beat | Stopped | Running | Fixed |

### Success Rate by Decision Type

| Decision Type | Success Rate | Experiments |
|---------------|--------------|-------------|
| experiment_workflow | 100% | 11 |
| pipeline_research | 100% | 9 |
| product_agents | 100% | 6 |
| experiment_agents | 100% | 5 |
| experiment_audio | 100% | 5 |

---

## Key Learnings

1. **Celery Beat is critical** - Without it, all scheduled tasks (228 of them) don't run
2. **Use `make celery`** - Don't start workers manually with different flags
3. **The experiment system works** - Code was correct, just not executing
4. **ChatGPT analysis was based on hypothetical data** - Agent research briefs may contain simulated scenarios

---

## Files Involved

| File | Purpose |
|------|---------|
| `core/models_pilot_readiness.py` | Experiment, PilotExecution, ExperimentLearning models |
| `core/services/experiment_metrics.py` | Metrics gathering for halt conditions |
| `core/services/experiment_rollback.py` | Rollback service for failed experiments |
| `core/services/experiment_learning_enhancer.py` | Learning extraction and analytics |
| `core/tasks.py:21859` | `monitor_running_experiments` task |
| `core/tasks.py:22001` | `update_experiment_kpis` task |

---

## Verification Commands

```bash
# Check Celery processes
pgrep -fl celery

# Verify Beat is running
pgrep -fl "celery.*beat"

# Check experiment status
python manage.py shell -c "
from core.models_pilot_readiness import Experiment, ExperimentLearning
print(f'Experiments: {Experiment.objects.count()}')
print(f'Learnings: {ExperimentLearning.objects.count()}')
"

# Check Beat task history
python manage.py shell -c "
from django_celery_beat.models import PeriodicTask
t = PeriodicTask.objects.get(name='monitor-experiment-halt-conditions')
print(f'Last run: {t.last_run_at}')
"
```

---

## Next Session Priorities

1. Monitor experiment system over time to ensure stability
2. Review the 3 failed experiments for root cause
3. Verify ThinkingAgent is receiving learnings for improved decisions
4. Consider adding alerting if Celery Beat stops

---

## Session Stats

- **Duration:** ~30 minutes
- **Root Cause:** Operational (Celery Beat not running)
- **Code Changes:** None required
- **Impact:** Unlocked 247 experiments, created 251 learnings
