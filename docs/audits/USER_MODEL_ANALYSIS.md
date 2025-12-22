# User Model Analysis

**Date:** December 21, 2025
**Session:** 528
**Status:** CLEANED - Option B Implemented

---

## Executive Summary

User model cleanup completed with Option B (Clarify & Clean):

| Action | Status |
|--------|--------|
| Delete `models_profile.py` | ✅ Done - unused, table never existed |
| Delete `models_user_profile_enhanced.py` | ✅ Done - duplicate classes |
| Update imports to canonical locations | ✅ Done - 5 files updated |
| Add deprecation warning to UserPreferences | ✅ Done |
| Document canonical model locations | ✅ Done (this file) |

**Files Deleted:** 2
**Files Modified:** 4
**Data Lost:** None (all backups in `backups/session_528_user_model_cleanup/`)

---

## Final Model Architecture

### Canonical User Models (in `core/models.py`)

| Model | Purpose | Records |
|-------|---------|---------|
| **UserProfile** | Main profile: preferences, credits, job prefs | 10 |
| **ExtendedUserProfile** | Job application data: resume, work history | 10 |
| **EnhancedUserProfile** | Power user: subscription, executive features | 3 |
| **UserStatistics** | Usage metrics: content counts, storage | 10 |
| **UserMemoryContext** | Memory system: context for AI | 682 |
| **UserAgentLearning** | Learning records: what agents learned | 238 |
| **UserEmbedding** | Vector embeddings for search | 30 |
| ~~UserPreferences~~ | DEPRECATED - 0 records, never used | 0 |

### Models in `core/models_unified_system.py`

These models exist for organizational reasons and share the same db_table as their `core/models.py` counterparts (Django deduplicates them):

- `UserAgentLearning` - identical to `core.models.UserAgentLearning`
- `UserBehaviorSignal` - 0 records, unused
- `UserPreferenceProfile` - 1 record, low usage
- `UserPlatformAccount` - 0 records, unused
- `UserLearningProfile` - 0 records, unused
- `UserNotificationPreference` - 0 records, unused
- `UserGoal` - 0 records, unused
- `UserBriefFeedback` - 0 records, unused

---

## Import Guidelines

### Preferred Imports

```python
# ALWAYS import user models from core.models
from core.models import (
    UserProfile,
    ExtendedUserProfile,
    EnhancedUserProfile,
    UserStatistics,
    UserMemoryContext,
    UserAgentLearning,
    UserEmbedding,
)
```

### Avoid These Imports

```python
# DON'T use these - files deleted or deprecated
from core.models_profile import UserProfile  # FILE DELETED
from core.models_user_profile_enhanced import EnhancedUserProfile  # FILE DELETED
```

---

## Changes Made in Session 528

### Files Deleted

1. **`core/models_profile.py`**
   - Had `UserProfile` class with different structure
   - Database table `user_ai_profiles` never created
   - No imports found anywhere

2. **`core/models_user_profile_enhanced.py`**
   - Had duplicate `EnhancedUserProfile` class
   - Had duplicate `UserMemoryContext` class
   - 5 files updated to import from `core.models` instead

### Files Modified

1. **`intelligence/profile_context_service.py`**
   - Changed 3 imports from `models_user_profile_enhanced` to `core.models`

2. **`core/consumers.py`**
   - Changed 1 import

3. **`intelligence/interview_consumer.py`**
   - Changed 4 imports

4. **`core/models.py`**
   - Added deprecation warning to `UserPreferences`

### Deprecation Added

```python
class UserPreferences(models.Model):
    """
    DEPRECATED - Session 528: This model has 0 records and is not used.
    ...
    """
    def save(self, *args, **kwargs):
        import warnings
        warnings.warn(
            "UserPreferences is deprecated. Use UserProfile for preferences.",
            DeprecationWarning,
            stacklevel=2
        )
        super().save(*args, **kwargs)
```

---

## Remaining Technical Debt

### Low Priority (Leave As-Is)

1. **UserAgentLearning dual definition**
   - Defined in both `core/models.py` and `core/models_unified_system.py`
   - Django deduplicates them (same `db_table`)
   - 45+ imports across codebase - too risky to consolidate
   - Both imports work correctly

2. **Unused models in `models_unified_system.py`** - NOW DEPRECATED
   - 6 models with 0 records: UserBehaviorSignal, UserPlatformAccount, UserLearningProfile, UserNotificationPreference, UserGoal, UserBriefFeedback
   - All marked DEPRECATED in docstrings (Session 528)
   - Can be removed in future session after confirming no new usage

### Future Consideration

3. **Merge profile models**
   - `UserProfile` + `ExtendedUserProfile` have overlapping fields
   - Would require data migration
   - Defer until clear business need

---

## Backup Location

All original files backed up before changes:

```
backups/session_528_user_model_cleanup/
├── db_backup_20251221_191112.sql  (1.2 GB)
├── models.py.bak
├── models_profile.py.bak
├── models_user_profile_enhanced.py.bak
└── models_unified_system.py.bak
```

---

*Updated by Session 528 - December 21, 2025*
