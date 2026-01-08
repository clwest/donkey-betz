# Session 727: Mythology App Deep Audit

**Date:** January 7, 2026
**Auditor:** Claude Code (Session 727)
**Status:** CRITICAL FINDINGS - Disconnected Systems

---

## Executive Summary

The mythology app is a **hallucination detection and prevention system** that is:
- Installed in `INSTALLED_APPS`
- Has API endpoints wired in `core/urls.py`
- Has services imported in 5 core files
- **BUT has 0 records in 6 of 7 database tables**

This represents ~2,295 lines of code that is **partially connected but not actively populating data**.

---

## What the Mythology App Does

The mythology system is designed to:
1. **Detect** hallucinations/mythology in AI outputs
2. **Prevent** mythology by injecting anti-mythology instructions
3. **Quarantine** suspicious content for human review
4. **Track** patterns to improve detection over time

### Models (7 total)

| Model | Purpose | Records |
|-------|---------|---------|
| `MythologyEvent` | Tracks mythology creation/mutation events | **0** |
| `MythPattern` | Recurring patterns to detect | **0** |
| `MythologyGuard` | Guards to prevent mythology | **0** |
| `MythologyCleanup` | Track cleanup operations | **0** |
| `MythologyAlert` | Alerts from monitoring | **0** |
| `FlaggedHallucination` | Flagged content for review | **0** |
| `HallucinationReview` | Reviews taken on flagged content | **0** |

### Separate Model: MythologyQuarantine

There's a DIFFERENT `MythologyQuarantine` model in `core/models_unified_system.py`:
- **9 records** (all pending, none reviewed)
- Used by `core/tasks.py` when learning transfers are blocked
- Last created: December 26, 2025

---

## Architecture Analysis

### Two Mythology Validation Systems (DUPLICATED)

**System 1: `ai_core/agents/mythology_validator.py`**
- Used by `core/agents/base_agent.py`
- Has `MythologyValidator` class with pattern matching
- Validates agent outputs before returning to users
- Logs violations internally but **DOES NOT write to database**

**System 2: `mythology/services.py`**
- `MythologyDetectionService` - Detects patterns
- `MythologyPreventionService` - Guards prompts/responses
- **HAS methods to write to MythologyEvent, MythologyAlert**
- Imported in 5 core files but writes are not happening

### Files That Import Mythology

```
core/assistant_prompt_enhanced.py     → MythologyPreventionService
core/consumers_hallucination.py       → MythologyDetectionService
core/views_assistant_intelligent.py   → MythologyPreventionService, HallucinationFlaggingService
core/unified_personal_assistant.py    → MythologyPreventionService
intelligence/mythology_enhanced_learning.py → MythologyDetectionService, MythologyPreventionService
```

### API Endpoints (15 total)

All wired at `/api/v1/mythology/`:

| Endpoint | Purpose | Working? |
|----------|---------|----------|
| `/stats/` | Dashboard statistics | Returns 0s |
| `/flagged-content/` | List flagged content | Returns empty |
| `/flagged-content/<id>/` | Detail view | N/A |
| `/review/` | Submit review | N/A |
| `/recent-events/` | Recent events | Returns empty |
| `/report/` | User reporting | Untested |
| `/notifications/` | Notification list | Returns empty |
| `/quarantine/` | Quarantine list | Returns 9 items |
| `/quarantine/stats/` | Quarantine stats | Works |
| `/quarantine/<id>/` | Quarantine detail | Works |
| `/quarantine/<id>/approve/` | Approve item | Works |
| `/quarantine/<id>/reject/` | Reject item | Works |

---

## Root Cause Analysis

### Why 0 Records in 6 Tables?

1. **Exception Handling Swallows Errors**
   - `mythology/services.py:_load_patterns()` catches all exceptions silently
   - Database writes may be failing without logging

2. **Validation Happens But Writes Don't**
   - `ai_core/agents/mythology_validator.py` does the actual work
   - It validates and corrects but doesn't persist to mythology app

3. **No Celery Tasks for Mythology**
   - No scheduled tasks to populate patterns or process events
   - No background processing of flagged content

4. **Disconnected Systems**
   - `core/tasks.py` writes to `MythologyQuarantine` (in core)
   - `mythology/` app models never receive data

---

## What Works vs What Doesn't

### Working

1. `MythologyQuarantine` (in core/) - 9 pending items
2. `ai_core/agents/mythology_validator.py` - Active validation
3. API endpoints for quarantine management
4. Anti-mythology instruction injection in prompts

### Not Working

1. `MythologyEvent` - Never populated (0 records)
2. `MythPattern` - Never populated (needs seeding)
3. `MythologyGuard` - Never populated (needs seeding)
4. `FlaggedHallucination` - Never populated
5. Pattern learning loop - Not functioning
6. Event tracking - Not functioning

---

## Recommendations

### Priority 1: Fix the Disconnect (HIGH)

**Option A: Connect mythology_validator to mythology app**
```python
# In ai_core/agents/mythology_validator.py
from mythology.services import MythologyDetectionService

# After detecting violations, record them:
detection_service = MythologyDetectionService()
detection_service.record_mythology_event(output, violations, agent_name)
```

**Option B: Consolidate to one system**
- Keep `ai_core/agents/mythology_validator.py` (it works)
- Deprecate `mythology/services.py`
- Add database persistence to the validator

### Priority 2: Seed Pattern Data (MEDIUM)

Create management command to seed `MythPattern`:
```python
# mythology/management/commands/seed_mythology_patterns.py
patterns = [
    {'pattern_type': 'numeric_inflation', 'regex_pattern': r'\b\d{3,}\s*(deployments?|instances?)'},
    {'pattern_type': 'false_authority', 'regex_pattern': r'(studies show|experts confirm)'},
    # ... etc
]
```

### Priority 3: Add Celery Tasks (MEDIUM)

```python
# In core/celery.py
'mythology-pattern-learning': {
    'task': 'mythology.tasks.update_pattern_statistics',
    'schedule': crontab(hour=4, minute=0),
}
```

### Priority 4: Review 9 Pending Quarantine Items (LOW)

These have been pending since December 26, 2025 - should be reviewed.

---

## Files Analyzed

| File | Lines | Purpose |
|------|-------|---------|
| `mythology/models.py` | 421 | Database models |
| `mythology/services.py` | 798 | Detection and prevention services |
| `mythology/views.py` | 1,010 | API endpoints |
| `mythology/urls.py` | 36 | URL routing |
| `ai_core/agents/mythology_validator.py` | 500+ | Actual validation logic |

**Total mythology-related code:** ~2,765 lines

---

## Conclusion

The mythology app represents significant development effort that is **partially operational**:
- Validation IS happening via `mythology_validator.py`
- But tracking, learning, and pattern improvement are NOT working

**Reality Score for Mythology: 30%**
- 30% because validation happens but nothing is tracked/learned

**Action Required:**
1. Decide: Consolidate to one system or connect both
2. Seed initial pattern data
3. Add Celery tasks for pattern learning
4. Review 9 pending quarantine items

---

*Audit completed: Session 727, January 7, 2026*
