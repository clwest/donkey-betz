# Error Tracking Document

**Purpose:** Track errors discovered during sessions for future investigation and fixing.

---

## Active Errors

*(No active errors)*

---

## Resolved Errors

### 2. Learning Orchestrator - NoneType User Error

**First Seen:** Session 752 (January 14, 2026)
**Resolved:** Session 752 (January 14, 2026)
**Status:** FIXED

**Error Message:**
```
ERROR learning_orchestrator: Error sending to Personal Assistant: 'NoneType' object has no attribute 'id'
```

**Root Cause:**
When an `AgentExecution` is created without a user (e.g., system-triggered or test execution), `execution.user` is `None`. The learning orchestrator then tried to send insights to Personal Assistant using `user.id`, which failed.

**Fix Applied:**
Added null check at the start of `_send_to_personal_assistant()` method:
```python
if not user:
    logger.debug("No user provided, skipping Personal Assistant notification")
    return
```

**File Modified:**
- `core/self_development/learning_orchestrator.py:255-259` - Added null check for user parameter

**Verification:**
- Tested with `None` user - gracefully skips notification
- Debug log confirms: `No user provided, skipping Personal Assistant notification`
- No more `'NoneType' object has no attribute 'id'` errors

---

### 1. AgentContribution Not Being Tracked - Live Feed Stale

**First Seen:** Session 752 (January 14, 2026)
**Resolved:** Session 752 (January 14, 2026)
**Status:** FIXED

**Symptom:**
Neural Orchestra Live Feed showed no activity since December 6, 2025. Only 5 total `AgentContribution` records existed despite 29 images created in the last month.

**Root Cause:**
1. Images were created without `agent` field set
2. The contribution tracking tried to create `AgentContribution` with `project=None`
3. `AgentContribution.project` was a **required** ForeignKey (no `null=True`)
4. Creation failed silently (exception caught and logged)

**Fix Applied:**
1. **Made `AgentContribution.project` nullable** - Migration `0010_session_752_make_agentcontribution_project_optional.py`
2. **Updated `core/views_image.py`** to:
   - Set `agent` field when creating `ImageHistory` records
   - Track contributions even without a project (shows as "Unknown")
3. **Files modified:**
   - `core/models/agents_registry/models.py` - Added `null=True, blank=True` to project FK
   - `core/views_image.py` - Added image-generation-agent lookup and contribution tracking
   - `agents/migrations/0010_session_752_make_agentcontribution_project_optional.py` - New migration

**Verification:**
- Created test contribution successfully with `project=None`
- API now returns 6 contributions (up from 5)
- New contribution appears at top of Live Feed with timestamp `2026-01-15T00:05:48`
- Future image generations will now properly track agent contributions

---

## Error Categories

| Category | Count (Open) | Notes |
|----------|-------|-------|
| User/Auth | 0 | NoneType user error FIXED |
| Database | 0 | AgentContribution tracking FIXED |
| API | 0 | |
| Frontend | 0 | |
| Celery | 0 | |

---

## Session Error Log

| Session | Date | Error | Status |
|---------|------|-------|--------|
| 752 | 2026-01-14 | Learning Orchestrator NoneType User | **FIXED** |
| 752 | 2026-01-14 | AgentContribution Not Being Tracked | **FIXED** |

---

**Last Updated:** Session 752 - January 14, 2026
**All errors resolved!** 🎉
