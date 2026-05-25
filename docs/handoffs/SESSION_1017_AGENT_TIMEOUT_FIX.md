---
originating_session: 1017
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1017 — Agent Execution Pipeline Audit: Timeouts + .metadata Fix

**Date:** February 16, 2026
**PRs:** #1236, #1237

---

## Problem

Two agent execution reliability issues causing ~28 timeouts/day and ~67 `.metadata` crashes/day:

1. **AgentResult `.metadata` AttributeError**: Some code path calling `.metadata` on `AgentResult` (which only has `.data`), crashing OpportunityScoringAgent and SystemIntelligenceAgent.

2. **Agent timeout false positives**: `cleanup_stale_agent_executions` used 30-min default (Beat kwargs of 120 min weren't being passed). Legitimately slow agents (WorkflowAgent max 22 min, MeetingCoordinatorAgent max 24 min) were falsely killed. Three agent dispatch Celery tasks had no `time_limit` at all, so genuinely hung agents left orphaned `in_progress` records.

## Changes

### PR #1236 — AgentResult `.metadata` backward-compat
- **File:** `core/agents/base_agent.py`
- Added `.metadata` property alias on `AgentResult` that returns `.data`

### PR #1237 — Agent timeout limits
- **File:** `core/tasks.py`
- `execute_agent_task`: added `soft_time_limit=2700`, `time_limit=3000`, `SoftTimeLimitExceeded` handler
- `execute_initiative_stage_task`: same
- `universal_agent_workspace_output`: same
- `cleanup_stale_agent_executions`: changed default from 30 to 60 minutes

## Verification

Deployed to Railway and confirmed:
- Cleanup runs with 60-min threshold (not 30)
- All 3 dispatch tasks have `soft_time_limit=2700`
- New Celery workers deployed (container hash changed)
- WorkflowAgent at 21 min not falsely killed
- 0 false-positive timeouts since deploy
