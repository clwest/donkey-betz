# Session 549: Human Action Required System + Deduplication

**Date:** December 24, 2025
**Commits:** `66e932d`, `e819179`
**Status:** COMPLETE

---

## Overview

Session 549 implemented two major features:
1. **Deduplication Service** - Cleaned 61,237 duplicate records from the database
2. **Human Action Required Alert System** - Full human-in-the-loop notification pipeline for concerns requiring policy decisions

---

## Part 1: Deduplication Service

### Problem
The ThinkingAgent identified "Information redundancy (duplicate topics)" as an active concern. Investigation revealed massive duplication:
- Spider URLs: 9,595 duplicates of "internal"
- Conversations: 480 copies of "Discussion: recent insights"
- Dreams: 541 copies of "Creative Thought"

### Solution
Created `core/services/deduplication_service.py` with:
- `check_spider_url_exists()` - Prevent duplicate spider data
- `find_similar_conversation()` - Find near-duplicate conversations
- `check_dream_title_unique()` - Ensure dream title uniqueness
- `run_full_deduplication()` - Clean existing duplicates

### Results
```
Total deleted: 61,237 records
├── Spider data: 14,472 deleted (58 remain due to FK refs)
├── Conversations: 45,449 deleted
└── Dreams: 1,316 deleted (1 remains)
```

### FK Constraint Handling
Initial bulk delete failed due to foreign key references from `trigger_event` and `narrative_evidence` tables. Fixed by implementing individual record deletion with try/except to skip referenced records.

---

## Part 2: Human Action Required Alert System

### Problem
ThinkingAgent identifies concerns that cannot be auto-resolved (legal, privacy, security, compliance issues). These require human policy decisions but there was no way to alert the user.

### Solution
Built a complete human-in-the-loop notification system.

### New Files

#### `core/services/human_action_service.py` (356 lines)
```python
class HumanActionService:
    # Categories concerns into action types
    ACTION_CATEGORIES = {
        'legal': 'legal_review',
        'privacy': 'legal_review',
        'provenance': 'data_provenance',
        'security': 'security_review',
        'compliance': 'compliance',
        'policy': 'policy_decision',
    }

    # Quick action templates per category
    QUICK_ACTIONS = {
        'legal_review': [
            {'action': 'approve', 'label': 'Approve After Review', 'style': 'success'},
            {'action': 'reject', 'label': 'Reject - Too Risky', 'style': 'danger'},
            {'action': 'defer', 'label': 'Need More Info', 'style': 'secondary'},
        ],
        # ... more categories
    }
```

Key methods:
- `create_action_notification(concern)` - Create notification for a concern
- `create_notifications_for_active_concerns()` - Batch create for all active
- `handle_action_response(notification_id, action, notes)` - Process user response
- `get_pending_actions(user)` - List pending action notifications

### API Endpoints

Added to `core/views_autonomous_reasoning.py`:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/reasoning/actions/pending/` | GET | List pending action notifications |
| `/api/v1/reasoning/actions/create/` | POST | Generate notifications for active concerns |
| `/api/v1/reasoning/actions/<uuid>/respond/` | POST | Handle user's action response |

### UI Components

Added to `ai_core/templates/ai_image_studio.html`:

1. **Pulsing Alert Button** - Red "Action Required" button in navbar with badge count
2. **Dropdown Panel** - Shows all pending notifications with details
3. **Quick Action Buttons** - Category-specific actions (Approve/Reject/Defer etc.)
4. **CSS Animation** - `pulse-action` keyframes for attention-grabbing effect

```html
<!-- Pulsing button in navbar -->
<div class="action-required-container" id="actionRequiredContainer" style="display: none;">
    <button class="btn btn-danger btn-sm pulse-action" data-bs-toggle="dropdown">
        ⚠️ Action Required <span class="badge bg-light text-danger" id="actionRequiredBadge">0</span>
    </button>
    <!-- Dropdown with notifications -->
</div>
```

### Model Updates

Added to `core/models_unified_system.py`:
```python
notification_type = models.CharField(max_length=50, choices=[
    ...
    ('action_required', 'Human Action Required'),  # Session 549
])
```

---

## Data Flow

```
ThinkingAgent detects concern
        ↓
Concern categorized (legal, security, etc.)
        ↓
Cannot be auto-verified → category='general'
        ↓
HumanActionService.create_action_notification()
        ↓
ProactiveNotification created (type='action_required')
        ↓
UI shows pulsing "Action Required" button
        ↓
User clicks → sees dropdown with concern details
        ↓
User clicks quick action (Approve/Reject/Defer)
        ↓
API: handle_human_action_api()
        ↓
Concern status updated (resolved/accepted/monitoring)
        ↓
Notification dismissed
        ↓
Button disappears (no pending actions)
```

---

## Testing Verification

```bash
# Create notifications for active concerns
curl -X POST http://localhost:8000/api/v1/reasoning/actions/create/
# Response: {"success": true, "notifications_created": 3}

# Check pending actions
curl http://localhost:8000/api/v1/reasoning/actions/pending/
# Response: {"success": true, "total": 3, "notifications": [...]}

# Handle an action
curl -X POST http://localhost:8000/api/v1/reasoning/actions/<uuid>/respond/ \
  -H "Content-Type: application/json" \
  -d '{"action": "approve"}'
# Response: {"success": true, "new_status": "resolved"}
```

---

## Files Modified

| File | Changes |
|------|---------|
| `core/services/deduplication_service.py` | NEW - Deduplication service |
| `core/services/human_action_service.py` | NEW - Human action notification service |
| `core/services/concern_tracker.py` | Added `information_redundancy` category + verification |
| `core/views_autonomous_reasoning.py` | Added 3 API endpoints for human actions |
| `core/urls.py` | Added URL routes for action APIs |
| `core/models_unified_system.py` | Added `action_required` notification type |
| `ai_core/templates/ai_image_studio.html` | Added pulsing alert button + dropdown UI |

---

## Session 550 Recommendations

1. **Scheduled Concern Scanning** - Add Celery Beat task to periodically create action notifications for new concerns

2. **Discord Integration** - Post action-required alerts to Discord for mobile notifications

3. **Action Analytics** - Track which actions are taken most often to improve auto-resolution

4. **Concern Prioritization** - Sort action notifications by severity and age

5. **Batch Actions** - Allow "Approve All" / "Reject All" for similar concerns

---

## Commands Reference

```bash
# Run thinking cycle to generate concerns
curl -X POST http://localhost:8000/api/v1/reasoning/trigger-cycle/

# Create action notifications
curl -X POST http://localhost:8000/api/v1/reasoning/actions/create/

# Check pending actions
curl http://localhost:8000/api/v1/reasoning/actions/pending/

# Run deduplication
.venv/bin/python manage.py shell -c "
from core.services.deduplication_service import get_deduplication_service
dedup = get_deduplication_service()
result = dedup.run_full_deduplication(dry_run=False)
print(result)
"
```
