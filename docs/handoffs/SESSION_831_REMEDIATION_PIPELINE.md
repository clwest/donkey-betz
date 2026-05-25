---
originating_session: 831
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 831: Remediation Pipeline + UI Fixes

**Date:** January 26, 2026
**Focus:** Complete remediation pipeline, LLM timeouts, UI improvements

---

## Summary

Session 831 completed the self-healing remediation pipeline by connecting open findings to agent execution, fixed LLM timeout issues, and improved UI feedback.

### Key Achievements

1. **Remediation Pipeline Complete** - Open findings now auto-assign to agents
2. **LLM Timeout Fixes** - Added 60s timeouts + 2 retries to all providers
3. **UI Feedback** - Run Remediation button shows success/error messages
4. **Recent Activity Fix** - Task text shows 2 lines instead of truncating

---

## 1. Remediation Pipeline (Findings → Tasks → Execution)

### Problem
User had 777 open findings but clicking "Run Remediation" said "No pending tasks". The assignment phase wasn't being triggered.

### Solution
Modified `/api/platform/actions/run-remediation/` to:
1. Check if there are assigned tasks
2. If none, check for open findings
3. If open findings exist, run assignment phase first
4. Return message telling user to run remediation again

### New Celery Task
```python
@shared_task
def assign_findings_to_agents(limit=50, priority_filter=['P0', 'P1', 'P2']):
    """Assign open findings to appropriate agents."""
    orchestrator = get_remediation_orchestrator(max_tasks_per_cycle=limit)
    return orchestrator.assign_open_findings(priority_filter=priority_filter, limit=limit)
```

### Flow
```
Open Findings (777) → Assignment Phase → Pending Tasks → Execution Phase → Completed
```

---

## 2. LLM Timeout Fixes

### Problem
Spider opportunity analysis failing with "Timeout connecting to server" errors.

### Solution
Added explicit timeout configuration to all LLM providers:

| Provider | Connect | Read | Total | Retries |
|----------|---------|------|-------|---------|
| OpenAI | 20s | 90s | 60s | 2 |
| Anthropic | 20s | 90s | 60s | 2 |
| DeepSeek | 20s | 90s | 60s | 2 |
| Together AI | 30s | 120s | 60s | 2 |

**File:** `core/services/llm_provider_registry.py`

---

## 3. UI Improvements

### Remediation Button Feedback
Added `onSuccess` and `onError` handlers to mutations in `GovernanceTab.tsx`:
- Shows green success message with details
- Shows red error message if failed
- Auto-dismisses after 30 seconds

### Auto-Detect Agent
When no agent specified, auto-selects the agent with most pending tasks:
```python
top_agent = AuditRemediationTask.objects.filter(
    status='assigned'
).values('assigned_agent').annotate(
    count=Count('id')
).order_by('-count').first()
```

### Recent Activity Text
Changed from `truncate max-w-md` to `line-clamp-2`:
- Shows 2 lines of text before truncating
- Uses full available width
- Click to expand for full text

---

## PRs Merged

| PR | Title |
|----|-------|
| #228 | Remediation button feedback messages |
| #229 | Auto-detect agent with pending tasks |
| #230 | LLM timeout fixes (60s, 2 retries) |
| #231 | Auto-assign open findings to agents |
| #232 | Recent Activity text display fix |

---

## Files Modified

| File | Changes |
|------|---------|
| `core/views_platform_command.py` | Auto-assign findings, auto-detect agent |
| `core/tasks.py` | New `assign_findings_to_agents` task |
| `core/services/llm_provider_registry.py` | Timeout config for all providers |
| `frontend/src/pages/workspace/tabs/GovernanceTab.tsx` | Feedback messages |
| `frontend/src/pages/WorkspacePage.tsx` | Recent Activity line-clamp fix |

---

## Current State

- **Self-Healing Pipeline:** Fully connected (discover → assign → execute → verify)
- **LLM Providers:** All have 60s timeouts with 2 retries
- **UI:** Shows clear feedback for remediation actions
- **Open Findings:** 777 ready for assignment and remediation

---

## Next Steps

1. Run remediation to assign open findings to agents
2. Run remediation again to execute assigned tasks
3. Monitor progress in Governance tab
4. Check Celery logs for detailed execution info
