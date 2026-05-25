---
originating_session: 841
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 841: Experiment Monitoring Fixes

**Date:** January 27, 2026
**Focus:** Stop global experiment halts, add provider outage handling, fix naming bug
**Status:** COMPLETED
**PR:** #320

---

## Summary

Fixed experiments being incorrectly halted with "100% error rate" due to system-wide error calculation, lack of minimum thresholds, provider outage cascading, and a naming bug that created "Unknown Decision" experiments.

---

## Problem Statement

Experiments were being halted prematurely due to four issues:

1. **Error rate calculated system-wide** - A single failing agent affected ALL experiments
2. **No minimum sample size** - Experiments halted after 1-2 failures (100% error rate from 1/1)
3. **Provider outages cascade** - OpenAI 429 errors triggered halts across all experiments
4. **"Unknown Decision" naming** - Using `.title` instead of `.topic` created 79 misnamed experiments

---

## Changes Made

### PR 1: Stop Global Halts

#### 1.1 Added Experiment FK to AgentExecution

**File:** `core/models_unified_system.py:557-565`

```python
experiment = models.ForeignKey(
    'core.Experiment',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='agent_executions',
    help_text="Session 841: Experiment this execution belongs to"
)
```

#### 1.2 Created Migration

**File:** `core/migrations/0191_add_experiment_fk_to_agent_execution.py`

#### 1.3 Updated ExperimentMetricsService

**File:** `core/services/experiment_metrics.py`

Added minimum thresholds:
```python
MIN_EXECUTIONS_FOR_ERROR_RATE = 10  # Need at least 10 executions
MIN_AGE_MINUTES = 10  # Experiment must be 10+ minutes old
```

Changed error rate calculation to filter by experiment:
```python
executions = AgentExecution.objects.filter(
    created_at__gte=effective_start,
    experiment=self.experiment  # Scope to THIS experiment only
)
```

#### 1.4 Updated Execution Creation Points

**Files:** `core/agent_router.py:912-914`, `core/tasks.py:259-279`

Both now extract `experiment_id` from context and link executions to experiments.

---

### PR 2: Provider Outage Handling

#### 2.1 Created Provider Health Tracker

**New File:** `core/services/provider_health_tracker.py`

Key features:
- Tracks errors per provider using Django cache (Redis)
- 5-minute sliding window
- 5+ errors marks provider as degraded
- Thread-safe using cache operations

```python
def is_provider_degraded(provider: str) -> bool:
    """True if provider has 5+ errors in last 5 minutes"""

def any_provider_degraded() -> bool:
    """True if ANY provider is degraded"""
```

#### 2.2 Updated LLM Providers

**File:** `core/services/llm_provider_registry.py`

OpenAI and Anthropic providers now record errors:
- `rate_limit` (429 errors)
- `server_error` (5xx errors)
- `timeout`
- `connection_error`

#### 2.3 Added Retry with Exponential Backoff

**File:** `core/agents/base_agent.py:1899-1965`

New method `_call_llm_with_retry()`:
- Exponential backoff: `delay = base_delay * (2 ** attempt)`
- Jitter: `delay += delay * 0.1 * random.random()`
- Max 3 retries, max 30s delay
- Retries on: rate_limit, server_error, connection_error, timeout

#### 2.4 Suppress Halts During Provider Outages

**File:** `core/services/experiment_metrics.py:67-92`

```python
if provider_degraded:
    metrics['error_rate'] = 0.0
    metrics['integrity_anomaly'] = False
    metrics['_provider_degraded'] = True  # Debug flag
```

---

### PR 3: Fix "Unknown Decision" Naming

**File:** `core/services/gate_progression_pipeline.py:429`

Before:
```python
decision_topic = getattr(gate.decision, 'title', 'Unknown Decision')[:100]
```

After:
```python
decision_topic = (gate.decision.topic or f"Gate-{str(gate.id)[:8]}")[:100]
```

The Decision model has `.topic` not `.title` (verified at `models_unified_system.py:17222`).

---

## Files Changed

| File | Change |
|------|--------|
| `core/models_unified_system.py` | Add experiment FK to AgentExecution |
| `core/migrations/0191_*` | Migration for new FK |
| `core/services/experiment_metrics.py` | Filter by experiment, add minimums, check provider health |
| `core/agent_router.py` | Pass experiment to execution |
| `core/tasks.py` | Pass experiment to execution |
| `core/services/provider_health_tracker.py` | NEW - Track provider health |
| `core/services/llm_provider_registry.py` | Record errors in health tracker |
| `core/agents/base_agent.py` | Add `_call_llm_with_retry()` method |
| `core/services/gate_progression_pipeline.py` | Fix `.title` → `.topic` |

---

## Verification

```bash
# Verify experiment FK exists
python manage.py shell -c "
from core.models_unified_system import AgentExecution
print(f'Has experiment field: {hasattr(AgentExecution, \"experiment\")}')
"
# Output: Has experiment field: True

# Check existing Unknown Decision experiments (will not create new ones)
python manage.py shell -c "
from core.models import Experiment
unknown = Experiment.objects.filter(name__icontains='Unknown Decision').count()
print(f'Existing Unknown Decision experiments: {unknown}')
"
# Output: Existing Unknown Decision experiments: 79
```

---

## Impact

### Before
- Error rate: System-wide calculation
- Minimum threshold: None (1 failure = 100%)
- Provider outages: Cascade to all experiments
- New experiments: Named "Unknown Decision"

### After
- Error rate: Per-experiment scoped
- Minimum threshold: 10 executions, 10 minutes age
- Provider outages: Suppressed from metrics
- New experiments: Named with actual decision topic

---

## Rollback Plan

All changes are backwards-compatible:
- FK is nullable - existing executions unaffected
- Minimum thresholds are safe defaults (returns 0% error rate)
- Provider health tracker fails safe (assumes healthy)

To rollback: revert migration, redeploy previous code.

---

## Next Session Priorities

1. Monitor experiment system to verify no more false halts
2. Consider backfilling `experiment` FK on existing AgentExecution records
3. Add alerting for provider degradation events
4. Clean up the 79 existing "Unknown Decision" experiments

---

## Session Stats

- **Duration:** ~30 minutes
- **PRs:** 1 merged (#320)
- **Files Changed:** 9 (1 new)
- **Lines Changed:** +454, -11
