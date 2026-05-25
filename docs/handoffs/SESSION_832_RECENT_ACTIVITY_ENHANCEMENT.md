---
originating_session: 832
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 832 - Recent Activity Enhancement

**Previous Session:** 831 (Remediation Pipeline + LLM Timeouts)
**Date:** January 26, 2026
**Status:** 74 Agents | 77 Spiders | 235 Celery Tasks | Enhanced Activity Feed

---

## What Was Accomplished

### 1. Enhanced Backend Recent Activity (`_get_recent_activity()`)

**New Fields Added:**
| Field | Description |
|-------|-------------|
| `created_at` | When task was started (previously only had `completed_at`) |
| `input_data` | Summary of input parameters passed to agent |
| `triggered_by` | Username who triggered execution, or "system" |

**Status Support Expanded:**
- Previously: Only showed `completed` and `failed` tasks
- Now: Shows `pending`, `in_progress`, `completed`, and `failed`
- In-progress tasks are prioritized to appear at top of feed
- Limit increased from 10 to 15 items

### 2. Integrated RecentActivityService

The `metrics_view()` endpoint now includes `system_activity` which aggregates:
- **Dreams** - Agent dreams from last 72 hours
- **Conversations** - Agent-to-agent conversations
- **Decisions** - Boardroom decisions
- **Pilots** - Experiments and pilot runs

This provides a broader view of autonomous system activity beyond just task executions.

### 3. Enhanced Frontend Display

**New ActivityCard Features:**
- Status-aware icons (spinning loader for in-progress, pause for pending)
- "Running" badge with animation for in-progress tasks
- Amber highlighting for running tasks
- Shows "Started X ago" for in-progress tasks
- Displays triggered_by user
- Shows input parameters in expandable section
- Shows both start and completion timestamps

**New ActivityFeedSection Component:**
- Tabbed interface: "Agent Tasks" | "System Activity"
- Badge showing count of currently running tasks
- Activity type counts in System Activity tab

**New SystemActivityCard Component:**
- Color-coded by type (purple=dreams, blue=conversations, amber=decisions, green=pilots)
- Shows icon, title, subtitle, agent, timestamp, status

---

## Files Modified

### Backend
| File | Changes |
|------|---------|
| `core/views_platform_command.py` | Enhanced `_get_recent_activity()` with new fields, all statuses, priority ordering; Added `system_activity` to `metrics_view()` |

### Frontend
| File | Changes |
|------|---------|
| `frontend/src/lib/api.ts` | Enhanced `RecentActivity` interface; Added `SystemActivityItem`, `SystemActivity` types; Updated metrics response type |
| `frontend/src/pages/workspace/tabs/CommandTab.tsx` | New imports; Enhanced `ActivityCard` with status icons/badges; New `ActivityFeedSection` with tabs; New `SystemActivityCard`; New `getSystemActivityIcon` helper |

---

## API Changes

### GET /api/platform/metrics/

**New fields in `recent_activity` items:**
```json
{
  "id": "uuid",
  "agent_name": "CodeReviewAgent",
  "agent_category": "Development",
  "task": "Review code changes...",
  "task_full": "Full task description...",
  "created_at": "2026-01-26T10:00:00Z",
  "completed_at": "2026-01-26T10:01:00Z",
  "success": true,
  "status": "completed",
  "execution_time_ms": 1234,
  "tokens_used": 500,
  "cost": 0.0025,
  "error_message": null,
  "output_summary": "Review complete...",
  "tool_results": ["read_file", "analyze"],
  "input_data": {"file_path": "/src/...", "context": "..."},
  "triggered_by": "admin"
}
```

**New `system_activity` field:**
```json
{
  "system_activity": {
    "success": true,
    "activities": [
      {
        "id": "uuid",
        "type": "dream",
        "icon": "💭",
        "title": "Dream title",
        "subtitle": "by AgentName",
        "timestamp": "2026-01-26T10:00:00Z",
        "timestamp_display": "2h ago",
        "agent_name": "ThinkingAgent"
      }
    ],
    "counts": {"dream": 5, "conversation": 3, "decision": 2, "pilot": 1},
    "total": 11,
    "hours_back": 72,
    "timestamp": "2026-01-26T12:00:00Z"
  }
}
```

---

## Visual Changes

### Command Tab - Recent Activity Section

**Before:**
- Single list of completed/failed tasks only
- Basic success/failure icons
- Limited information displayed

**After:**
- Two tabs: "Agent Tasks" and "System Activity"
- In-progress tasks highlighted with amber styling
- Running task count badge
- Status-specific icons with animations
- Expandable input parameters
- Start and completion timestamps
- Triggered by user shown
- System activity shows dreams, conversations, decisions, pilots

---

## Testing

To verify changes:

1. **Check in-progress tasks appear:**
   - Trigger a long-running agent task
   - Should see it at top with spinning loader and "Running" badge

2. **Check new fields:**
   - Expand any activity card
   - Should see "Triggered by", "Started", "Completed" times
   - If input_data exists, should see "Input Parameters" section

3. **Check System Activity tab:**
   - Click "System Activity" tab
   - Should see dreams, conversations, decisions, pilots
   - Should see activity type counts at top

---

## Previous Sessions

| Session | Focus |
|---------|-------|
| **832** | Recent Activity Enhancement - New fields, all statuses, system activity |
| **831** | Remediation Pipeline + LLM Timeouts + UI Fixes |
| **830** | Agent File Operations + Production Auth Fixes |
| **829** | Self-Healing UI Controls + SKIN Layer File Writing |
| **828** | Self-Healing Execution - 514/742 tasks (69.3%) |
| **827** | Production 502 Fix - Async Conversations |

---

**SESSION 832 COMPLETE - Recent Activity now shows running tasks, input data, system activity**
