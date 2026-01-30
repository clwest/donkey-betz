# Experiment Halt Rules Audit - Session 873

**Date:** January 29, 2026
**Auditor:** ThinkingAgent + Claude
**Status:** ISSUES IDENTIFIED

---

## Executive Summary

The experiment halt system has a critical instrumentation gap: **0% of AgentExecution records have the experiment FK set**, making scoped error rate calculations impossible. This led to 77 experiments being batch-halted on Jan 27, 2026.

---

## Current Halt Conditions (Thresholds)

| Condition | Default Threshold | Description |
|-----------|-------------------|-------------|
| `error_rate_max` | **35.0%** | Max error rate before halt |
| `bias_detection_rate_max` | 15.0% | Max bias detection rate |
| `user_trust_index_min` | 3.8 | Min user trust score (1-5) |
| `integrity_anomaly_detected` | true | Halt on integrity anomalies |
| `telemetry_kill_switch` | true | Halt on kill switch signal |

**Safeguards (Session 841/855):**
- `MIN_EXECUTIONS_FOR_ERROR_RATE = 20` - Need 20+ executions before calculating
- `MIN_AGE_MINUTES = 30` - 30-minute grace period for new experiments
- Provider degradation suppression - Suppress metrics during outages

---

## Issues Found

### 1. AgentExecution Experiment FK Never Set (CRITICAL)

**Evidence:**
```
Total executions: 2,363
With experiment FK set: 0 (0.0%)
```

**Impact:** Error rate calculation in `_calculate_error_rate()` always returns 0.0 due to MIN_EXECUTIONS check when filtering by experiment.

**Root Cause:** Multiple AgentExecution models exist:
- `core.models_unified_system.AgentExecution` (has experiment FK, never set)
- `agents.models.AgentExecution` (different model, no experiment FK)
- `core.models.agents_registry.AgentExecution` (different model)

**Location where FK IS passed:** `core/tasks.py:309`
```python
execution_record = AgentExecution.objects.create(
    ...
    experiment=experiment,  # Session 841: Link to experiment
)
```

But this only works when `experiment` parameter is passed to `conversation_action_dispatch()`.

### 2. Batch Halt Event (Jan 27, 2026)

**Evidence:**
```
2026-01-27: 77 experiments halted at 15:10:00.xxx
All named: "Experiment: Unknown Decision"
All reason: "Error rate 100.0% exceeded threshold 25.0%"
```

**Hypothesis:** Before Session 841 safeguards, the error rate was calculated from ALL executions in the time window, not scoped to specific experiments. When 5+ system-wide failures occurred, all running experiments got halted.

### 3. Stale Running Experiments

**Evidence:**
```
4 running experiments:
- All named "Experiment: Unknown Decision"
- Ages: 54-57 hours (should be resolved)
- Linked executions: 0
```

### 4. Experiment Naming Issue

**Evidence:** All experiments have generic name "Experiment: Unknown Decision" instead of descriptive names from the decision that spawned them.

---

## Recommended Fixes

### Fix 1: Wire Up Experiment FK (HIGH PRIORITY)

**Files to modify:**
1. `core/agent_integration.py` - Add experiment parameter to execute()
2. `core/views_projects_api.py` - Add experiment lookup
3. `core/personal_ai_assistant_enhanced.py` - Add experiment context

**Code pattern:**
```python
# Look up active experiment for this execution
experiment = Experiment.objects.filter(
    status='running',
    pilot__gate__decision__id=decision_id
).first()

execution = AgentExecution.objects.create(
    ...
    experiment=experiment,  # Link to experiment
)
```

### Fix 2: Better Experiment Naming

**Location:** Experiment creation code (where "Unknown Decision" is set)

**Fix:** Pull name from decision.title or generate from context:
```python
name = f"Experiment: {decision.title or 'Auto-generated'}"
```

### Fix 3: Clean Up Stale Experiments

**Command:**
```python
from core.models_pilot_readiness import Experiment
from django.utils import timezone
from datetime import timedelta

# Mark stale running experiments as inconclusive
stale = Experiment.objects.filter(
    status='running',
    started_at__lt=timezone.now() - timedelta(hours=48)
)
count = stale.update(
    status='inconclusive',
    ended_at=timezone.now(),
    result_summary='Auto-closed: No activity for 48+ hours'
)
print(f"Closed {count} stale experiments")
```

### Fix 4: Add Minimum Sample Size to Halt Message

**Location:** `core/models_pilot_readiness.py:1033`

**Enhancement:**
```python
if metrics.get('error_rate', 0) > conditions.get('error_rate_max', 25.0):
    sample_size = metrics.get('sample_size', 'unknown')
    return True, (
        f"Error rate {metrics['error_rate']}% exceeded threshold "
        f"{conditions['error_rate_max']}% (sample: {sample_size})"
    )
```

---

## Monitoring Recommendations

1. **Add instrumentation dashboard for:**
   - % of AgentExecutions with experiment FK set
   - Running experiments age distribution
   - Halt events per day with reasons

2. **Add alert for:**
   - Batch halts (>5 experiments halted in 1 hour)
   - Experiments running >48 hours without KPI updates

3. **Add validation:**
   - Reject halt decisions when sample_size < MIN_EXECUTIONS
   - Log warning when experiment FK is not set

---

## Files Involved

| File | Purpose |
|------|---------|
| `core/models_pilot_readiness.py` | Experiment model + halt conditions |
| `core/services/experiment_metrics.py` | Metrics gathering |
| `core/tasks.py:22185` | `_gather_experiment_metrics()` |
| `core/tasks.py:300` | AgentExecution creation (has experiment param) |
| `core/agent_integration.py:352` | AgentExecution creation (missing experiment) |

---

## Conclusion

The experiment halt system has good safeguards in code (MIN_EXECUTIONS, MIN_AGE, provider suppression) but lacks the instrumentation to use them effectively. The 0% FK linkage means all experiments appear to have 0 executions, bypassing error rate checks entirely.

**Priority:** Fix the experiment FK wiring before any new experiments are started.
