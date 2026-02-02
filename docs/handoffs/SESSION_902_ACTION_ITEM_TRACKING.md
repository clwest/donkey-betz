# Session 902 - Initiative Action Item Tracking

**Date:** February 1, 2026
**Focus:** Track next steps from conversations as actionable items

---

## Problem Statement

Conversation conclusions contained actionable "Next Steps" like:
```
=== DecisionSummary ===
Next Steps:
- ResearchAgent: Define canonical persona schema (Week 0-1)
- ContentWriterAgent: Draft methodology guide (Week 1-3)
- DataAnalysisAgent: Build validation framework (Week 2-4)
```

But these were:
- Just TEXT buried in conclusion fields
- Not parsed into trackable items
- Not assignable to agents/users
- No way to mark completion
- No timeline/due date tracking

### Before (Text Dump)
```
Conclusion text contains action items
→ No tracking
→ No completion status
→ No progress visibility
```

### After (Structured Tracking)
```
InitiativeActionItem records:
- title: "Define canonical persona schema"
- assigned_agent: "ResearchAgent"
- timeline_text: "Week 0-1"
- due_date: 2026-02-08
- status: pending → in_progress → completed
- priority: high
```

---

## Solution: InitiativeActionItem Model

**File:** `core/models_document_registry.py`

```python
class InitiativeActionItem(models.Model):
    """
    Session 902: Trackable action items extracted from conversation conclusions.
    """

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        BLOCKED = 'blocked', 'Blocked'
        CANCELLED = 'cancelled', 'Cancelled'

    class Priority(models.TextChoices):
        CRITICAL = 'critical', 'Critical'
        HIGH = 'high', 'High'
        MEDIUM = 'medium', 'Medium'
        LOW = 'low', 'Low'

    # Link to initiative
    initiative = models.ForeignKey(Initiative, related_name='action_items')
    source_conversation = models.ForeignKey('HiveMindSession', null=True)

    # Action item details
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    assigned_agent = models.CharField(max_length=100, blank=True)
    assigned_user = models.ForeignKey('core.UnifiedUser', null=True)

    # Timeline
    timeline_text = models.CharField(max_length=50, blank=True)  # "Week 0-1"
    due_date = models.DateField(null=True)
    estimated_hours = models.FloatField(null=True)

    # Status tracking
    status = models.CharField(choices=Status.choices, default='pending')
    priority = models.CharField(choices=Priority.choices, default='medium')

    # Completion tracking
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
    completed_by = models.CharField(max_length=100, blank=True)
    completion_notes = models.TextField(blank=True)
    blocked_reason = models.TextField(blank=True)

    # Dependencies
    depends_on = models.ManyToManyField('self', symmetrical=False, related_name='blocks')
```

---

## Action Item Parser Service

**File:** `core/services/action_item_parser.py`

Parses conversation syntheses to extract action items:

```python
class ActionItemParser:
    """
    Parses conversation conclusions to extract actionable items.

    Supports multiple formats:
    - "AgentName: Task description (Timeline)"
    - "- Task description [assigned to AgentName]"
    - "1. Task description"
    - Bullet points with agent mentions
    """

    SECTION_MARKERS = [
        'next steps',
        'action items',
        'follow-up',
        'to do',
        'tasks',
        'deliverables',
        'recommendations',
    ]
```

**Key Functions:**
- `parse_conclusion(text)` → List of action item dicts
- `extract_action_items_from_conversation(session_id)` → Create InitiativeActionItem records
- `bulk_extract_action_items(limit)` → Process multiple sessions

**Timeline Parsing:**
- "Week 0-1" → due_date = today + 1 week
- "5 days" → due_date = today + 5 days
- "immediate/urgent/asap" → due_date = tomorrow

**Priority Inference:**
- "critical", "urgent", "blocker" → critical
- "important", "high priority", "week 0" → high
- "nice to have", "optional", "future" → low
- Default → medium

---

## API Endpoints

**File:** `core/views_research_demo.py`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/initiatives/<id>/action-items/` | GET | List action items for initiative |
| `/api/initiatives/<id>/action-items/create/` | POST | Create new action item |
| `/api/initiatives/<id>/action-items/extract/` | POST | Extract from linked conversations |
| `/api/action-items/<id>/` | POST | Update action item status/details |
| `/api/action-items/<id>/delete/` | DELETE | Delete action item |
| `/api/action-items/extract/` | POST | Bulk extract from recent sessions |

**Update Endpoint Body:**
```json
{
  "status": "completed",
  "priority": "high",
  "title": "Updated title",
  "due_date": "2026-02-15",
  "completion_notes": "Done via PR #123"
}
```

**Response includes stats:**
```json
{
  "success": true,
  "stats": {
    "total": 5,
    "pending": 2,
    "in_progress": 1,
    "completed": 2,
    "blocked": 0,
    "completion_rate": 40.0
  },
  "action_items": [...]
}
```

---

## Frontend UI

**File:** `frontend/src/pages/workspace/tabs/InitiativesTab.tsx`

Added to ComprehensiveInitiativeModal:

### Stats Bar
```
○ 2 pending | ▶ 1 in progress | ✓ 2 completed
```

### Action Buttons
- **Extract from Conversations**: Parse synthesis for action items
- **Add Input**: Type new action item and press Enter

### Action Item List
Each item shows:
- **Checkbox**: Click to cycle status (pending → in_progress → completed)
- **Title**: With strikethrough when completed
- **Badges**: Agent name, timeline, overdue indicator, priority
- **Blocked Reason**: Red banner if blocked
- **Priority Toggle**: Click flame to cycle priority

### Status Colors
| Status | Background | Border |
|--------|------------|--------|
| Pending | dark | gray |
| In Progress | blue/5 | blue/30 |
| Completed | green/5 | green/30 (opacity 60%) |
| Blocked | red/5 | red/30 |

---

## Files Changed

| File | Change |
|------|--------|
| `core/models_document_registry.py` | Added InitiativeActionItem model |
| `core/migrations/0213_session_902_action_items.py` | NEW - Migration |
| `core/services/action_item_parser.py` | NEW - Parser service |
| `core/views_research_demo.py` | Added 6 API endpoints |
| `core/urls.py` | Added URL routes |
| `frontend/src/pages/workspace/tabs/InitiativesTab.tsx` | Action Items section in modal |

---

## Migration

```bash
# Apply migration
python manage.py migrate core 0213_session_902_action_items

# Test extraction
python manage.py shell -c "
from core.services.action_item_parser import bulk_extract_action_items
stats = bulk_extract_action_items(limit=20)
print(stats)
"
```

---

## Current State

- **Model**: Deployed and verified
- **API**: All 6 endpoints working
- **UI**: Deployed with full functionality
- **Extraction**: Ready - waiting for sessions with synthesis_summary

Currently 0 sessions have synthesis_summary populated, so extraction returns empty. Action items will appear as:
1. New multi-agent conversations complete with syntheses
2. Users manually create items via the UI

---

## PRs Created

| PR | Description |
|----|-------------|
| #681 | feat(Session 902): Initiative Action Items |
| #682 | fix(Session 902): Use correct HiveMindSession field names |

---

## Next Steps for Session 903

1. **Populate Test Data**: Run conversations to generate synthesis with action items
2. ~~**Auto-Extraction**: Celery task to extract on conversation completion~~ ✅ **DONE in PR #684**
3. **Kanban View**: Drag-and-drop board for action items
4. **Assignment UI**: Dropdown to assign to users
5. **Due Date Calendar**: Visual calendar of upcoming action items
