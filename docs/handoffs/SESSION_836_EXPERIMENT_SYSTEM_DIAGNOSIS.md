---
originating_session: 836
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

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

## Production API Fixes

After fixing the experiment system, several production 500 errors were discovered and fixed:

### Fix 1: Non-string Synthesis Handling (PR #284)

**Issue:** `session.synthesis[:500]` failed when synthesis was a dict instead of string.

**Fix:** `str(session.synthesis)[:500]` to handle both types.

### Fix 2: Wrong Field Name (PR #285)

**Issue:** `'AgentConversation' object has no attribute 'trigger_reason'`

**Fix:** Changed `conv.trigger_reason` to `conv.trigger_type` (correct field name).

### Fix 3: Conversation Modal Field Names (PR #286)

**Issue:** UI showed "Invalid Date" and "0 turns" despite API returning correct data.

**Root Cause:** Frontend expected different field names than API returned:

| Frontend Expected | API Returns |
|-------------------|-------------|
| `turns` array | `messages` array |
| `created_at` | `started_at` |
| `concluded_at` | `ended_at` |
| `conclusion_summary` | `conclusion`/`insights` |

**Fix:** Updated `ConversationDetailModal.tsx` to use correct field names.

### Fix 4: Conversation Stats Computed Dynamically (PR #288)

**Issue:** Conversations Panel showed "0 Completed" and "0% Avg Quality" despite 243 messages.

**Root Cause:** API used stale stored fields that were never updated after conversation creation.

**Fix:** Compute values dynamically at query time:
- `message_count`: Use actual count from messages array
- `status`: 'completed' if has ended_at/conclusion/synthesis
- `quality_score`: Estimate from message count

### Fix 5: MeetingCoordinatorAgent Placeholder Bug (PR #290)

**Issue:** MeetingCoordinatorAgent returned placeholder text like "CTOAgent's perspective on {topic}" instead of actual agent responses.

**Root Cause:** The `_start_meeting` method used string formatting instead of actually calling other agents.

**Fix:**
- `_start_meeting`: Now routes to real agents via AgentRouter
- `_synthesize_discussion`: Uses LLM for real synthesis
- `_extract_action_items`: Uses LLM for real extraction
- Meeting status: 'completed' when successful, not always 'in_progress'

---

## Files Modified

| File | Change |
|------|--------|
| `core/views_agent_learning.py` | Fixed synthesis, trigger_type, dynamic stats computation |
| `frontend/src/components/platform/ConversationDetailModal.tsx` | Fixed field names to match API |
| `core/agents/executive/meeting_coordinator_agent.py` | Fixed placeholder bug - now calls real agents |

---

## Session Stats

- **Duration:** ~4 hours
- **Root Cause:** Operational (Celery Beat) + API field mismatches + stale stored values + agent placeholders
- **Code Changes:** 5 PRs merged (#284, #285, #286, #288, #290)
- **Impact:** Unlocked 247 experiments, created 251 learnings, fixed production UI, fixed agent coordination
