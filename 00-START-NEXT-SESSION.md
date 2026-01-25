# Session 824 - UI Integration Sprint

**Previous Session:** 823 (Self-Execution Engine)
**Date:** January 25, 2026
**Status:** 74 Agents | 77 Spiders | 236 Celery Tasks | 60 Audits | **SELF-AWARE + SELF-EXECUTING**

---

## The Problem

Over Sessions 819-823, we built powerful backend capabilities that are **CLI-only**:

| Session | Capability | Current Access | Should Be |
|---------|------------|----------------|-----------|
| 819 | Deliverables Marketplace | Plan only | Workspace → Deliverables tab |
| 820 | Self-Healing Orchestration | `auto_remediate` CLI | Workspace → Remediation tab |
| 822 | SKIN Layer (file writes) | CLI only | Workspace → Operations tab |
| 823 | Self-Execution Engine | `run_metrics_action_check()` | Workspace → Command tab |
| 823 | Live System Metrics | `_gather_live_system_metrics()` | Workspace → Dashboard |

**The Workspace page should be the command center**, not the terminal.

---

## Session 824 Goals

### Phase 1: Expose Live Metrics (API + UI)

**Backend API:**
```python
# New endpoint: /api/platform/live-metrics/
# Returns output of _gather_live_system_metrics()
{
    "components": {"agents": 213, "spiders": 77, "celery_tasks": 228},
    "health": {"heart": "healthy", "lungs": "unknown", "brain": "focused", "skin": "dormant"},
    "activity": {"spider_entries_24h": 0, "agent_executions_24h": 94, "llm_calls_24h": 6055},
    "remediation": {"open_findings": 755, "tasks_by_status": {...}},
    "revenue": {"total": 0.01, "last_7_days": 0}
}
```

**Frontend Component:** `LiveMetricsDashboard.tsx`
- Real-time metrics cards
- Body system health indicators
- Activity sparklines
- Auto-refresh every 60 seconds

### Phase 2: Trigger Rules Management

**Backend API:**
```python
# GET /api/platform/triggers/
# Returns all trigger rules with status
[
    {"name": "no_spider_data_24h", "enabled": true, "in_cooldown": false, ...},
    ...
]

# POST /api/platform/triggers/{name}/toggle/
# Enable/disable a trigger rule

# POST /api/platform/triggers/run-now/
# Manually run metrics check
```

**Frontend Component:** `TriggerRulesPanel.tsx`
- List all 10 trigger rules
- Show condition, threshold, action
- Toggle enabled/disabled
- Show cooldown status
- "Run Check Now" button

### Phase 3: Manual Actions Panel

**Backend API:**
```python
# POST /api/platform/actions/run-spiders/
# POST /api/platform/actions/run-remediation/
# POST /api/platform/actions/run-self-audit/
# POST /api/platform/actions/agent-health-check/
```

**Frontend Component:** `ActionsPanel.tsx`
- Button grid for common actions
- Confirmation dialogs
- Status feedback (running/complete/failed)

### Phase 4: Remediation Status View

**Backend API:**
```python
# GET /api/platform/remediation/status/
# Returns findings and task status
{
    "open_findings": 755,
    "by_priority": {"P0": 5, "P1": 23, "P2": 127, ...},
    "recent_tasks": [...],
    "agents_assigned": [...]
}
```

**Frontend Component:** `RemediationStatusPanel.tsx`
- Finding counts by priority
- Recent task list with status
- Agent assignment overview

---

## Implementation Order

1. **Create `/api/platform/live-metrics/` endpoint** using existing `_gather_live_system_metrics()`
2. **Create `LiveMetricsDashboard.tsx`** component
3. **Add to Workspace Command tab** (replace or enhance current metrics)
4. **Create `/api/platform/triggers/` endpoints**
5. **Create `TriggerRulesPanel.tsx`** component
6. **Create `/api/platform/actions/` endpoints**
7. **Create `ActionsPanel.tsx`** component
8. **Create `/api/platform/remediation/status/` endpoint**
9. **Create `RemediationStatusPanel.tsx`** component

---

## Current Workspace Structure

The Workspace page already has Platform Command Center tabs (Session 815):

```
Workspace Page
├── Operations Tab (existing - file operations log)
├── Command Tab (Session 815)
│   ├── Mission section
│   ├── Metrics section ← ENHANCE with live metrics
│   └── Activity section
├── Governance Tab (Session 815)
│   ├── Emergency controls
│   └── Pending decisions
└── Knowledge Tab (Session 815)
    ├── Canon browser
    ├── Playbooks
    └── Audits browser
```

**Proposed Enhancement:**
```
Command Tab
├── Live Metrics Dashboard (NEW - Phase 1)
├── Trigger Rules Panel (NEW - Phase 2)
├── Actions Panel (NEW - Phase 3)
└── Remediation Status (NEW - Phase 4)
```

---

## Key Files

### Backend (to create/modify)
```
core/views_platform.py         # Add live-metrics, triggers, actions endpoints
core/urls.py                   # Add new routes
```

### Frontend (to create)
```
frontend/src/components/platform/LiveMetricsDashboard.tsx
frontend/src/components/platform/TriggerRulesPanel.tsx
frontend/src/components/platform/ActionsPanel.tsx
frontend/src/components/platform/RemediationStatusPanel.tsx
```

### Existing (reference)
```
core/tasks.py                  # _gather_live_system_metrics()
core/services/metrics_action_trigger.py  # MetricsActionTrigger
frontend/src/pages/WorkspacePage.tsx     # Platform Command Center
frontend/src/components/platform/        # Existing platform components
```

---

## Quick Start

```bash
# Start platform
make start && make celery

# Current CLI commands (to be replaced by UI)
python manage.py shell -c "from core.tasks import run_metrics_action_check; print(run_metrics_action_check())"
python manage.py auto_remediate --status
```

---

## Previous Sessions

| Session | Focus |
|---------|-------|
| **824** | UI Integration Sprint - Expose backend to Workspace |
| **823** | SELF-EXECUTION - System now self-aware + self-executing |
| **822** | SKIN Layer Autonomous Remediation - Agents can write files |
| **821** | Phase 1.5 Staleness Validation for Self-Healing System |
| **820** | Self-Healing Orchestration + Tiered Docs Injection |
| **819** | Deliverables Marketplace - Product catalog of AI outputs |

---

**START HERE:** The backend is powerful but hidden. This session exposes everything via the Workspace UI.
