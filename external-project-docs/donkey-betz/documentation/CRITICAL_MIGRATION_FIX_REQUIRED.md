# 🔴 CRITICAL: Database Migration Fix Required

**Status**: BLOCKING ALL PROGRESS
**Severity**: CRITICAL
**Session**: 105 discovered, 106 must fix
**Date**: August 7, 2025

## Executive Summary

The Django migration system is completely broken due to circular dependencies and missing models. Phase 2 and Phase 3 cannot proceed without fixing this. The system currently runs ONLY on mock data with no database persistence for new features.

## The Problem Chain

### 1. Primary Issue: ConversationMemory Model Never Created
```python
KeyError: ('ai_partner', 'conversationmemory')
```
- Migration `0004_conversationmemory_created_at_and_more.py` tries to ADD fields to ConversationMemory
- But ConversationMemory was NEVER created in any migration
- Migrations 0002, 0003, 0004, 0005, 0008, 0012, 0013, 0016, 0017, 0018, 0021 all reference it
- The model doesn't exist in models.py either

### 2. Secondary Issue: Learning Intelligence Dependency
```python
KeyError: ('learning_intelligence', 'memoryentry')
```
- Migration `0019_create_self_observing_models.py` depends on `learning_intelligence.0001_initial`
- But learning_intelligence migration references `memoryentry` (lowercase) which doesn't exist
- The actual model is `LearningMemoryEntry` with alias `MemoryEntry`
- When learning_intelligence is disabled, other imports break

### 3. Tertiary Issue: Phase 2 Models Can't Be Created
```python
Migration ai_partner.0029_phase2_models
```
- Cannot be applied due to above issues
- Tables don't exist: `WorkflowTemplate`, `Phase2UserProfile`
- All Phase 2 features running on mock data only

## Current Workarounds (Temporary)

### What Was Done in Session 105
1. **Disabled learning_intelligence app**
   ```python
   # server/settings.py line 340
   # "learning_intelligence",  # TEMPORARILY DISABLED TO FIX MIGRATION
   ```

2. **Commented out problematic imports**
   - `ai_partner/services/learning_enhanced_ai.py`
   - `api_services/learning_api_service.py`
   - `agent_orchestra/services/learning_enhanced_orchestrator.py`

3. **Commented out SystemInsight.learning_anchor field**
   ```python
   # ai_partner/models.py lines 751-759
   ```

4. **Added ConversationMemory to migration 0003**
   - But this doesn't work because migration is already applied

## The Real Solution Path

### Option 1: Complete Migration Reset (Nuclear Option)
```bash
# WARNING: This will destroy all data
python manage.py migrate ai_partner zero
python manage.py migrate learning_intelligence zero
# Fix all migrations
python manage.py migrate
```

### Option 2: Surgical Fix (Recommended)
1. Create a proper ConversationMemory model in models.py
2. Create a new migration that properly handles the model
3. Fake the problematic migrations
4. Apply new migrations

### Option 3: Manual Database Fix
1. Create tables manually in PostgreSQL
2. Fake all problematic migrations
3. Continue from clean state

## Detailed Analysis

### ConversationMemory Investigation
The model appears to have been part of a refactoring to UnifiedMemoryEntry:
- `shared_memory/conversation_memory_bridge.py` shows migration from ConversationMemory to UnifiedMemoryEntry
- But the original model was removed before migrations were cleaned up
- This suggests an incomplete refactoring from sessions 80-90

### Learning Intelligence Issues
- Models have circular references
- The app was integrated from another project (intel_core)
- Dependencies weren't properly resolved during integration

### Migration Dependency Tree
```
ai_partner.0001_initial
├── ai_partner.0002_userlifeprofile_allow_ai_learning_and_more
├── ai_partner.0003_userpatternprofile_conversationembedding_and_more
│   └── ai_partner.0004_conversationmemory_created_at_and_more ❌ (references non-existent model)
│       └── ai_partner.0005_add_conversation_segments
│           └── ... (all subsequent migrations fail)
└── ai_partner.0019_create_self_observing_models
    └── learning_intelligence.0001_initial ❌ (circular dependency)
```

## Files Affected by Temporary Fixes

### Modified in Session 105
1. `backend/server/settings.py` - learning_intelligence disabled
2. `backend/learning_intelligence/models.py` - added app_label
3. `backend/ai_partner/models.py` - commented learning_anchor
4. `backend/ai_partner/migrations/0003_*.py` - attempted to add ConversationMemory
5. `backend/ai_partner/migrations/0019_*.py` - removed learning_intelligence dependency
6. `backend/api_services/learning_api_service.py` - commented imports
7. `backend/ai_partner/services/learning_enhanced_ai.py` - commented imports
8. `backend/agent_orchestra/services/learning_enhanced_orchestrator.py` - commented imports
9. `backend/mythology_lab/hooks/enhanced_conversation_memory.py` - disabled patching

## Impact Assessment

### What's Broken
- ❌ No database tables for Phase 2 models
- ❌ No persistence for agent recommendations
- ❌ No workflow templates in database
- ❌ No user profiles for Phase 2
- ❌ Learning intelligence completely disabled
- ❌ Memory anchoring system offline
- ❌ Mythology detection disabled

### What's Working (Mock Only)
- ✅ Phase 2 API endpoints (returning test data)
- ✅ Frontend components rendering
- ✅ Basic agent orchestration
- ✅ Phase 1 features

## Required Actions for Session 106

### Step 1: Assess Current Database State
```bash
python manage.py dbshell
\dt ai_partner*;
\dt learning_intelligence*;
SELECT * FROM django_migrations WHERE app='ai_partner' ORDER BY id;
```

### Step 2: Create ConversationMemory Model
```python
# In ai_partner/models.py
class ConversationMemory(models.Model):
    """Legacy model for migration compatibility"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transcript = models.TextField(default="")
    session_date = models.DateTimeField(auto_now_add=True)
    # ... other fields from migrations
```

### Step 3: Create Fix Migration
```bash
python manage.py makemigrations ai_partner --name fix_conversation_memory
```

### Step 4: Re-enable Learning Intelligence
After fixing ConversationMemory, carefully re-enable learning_intelligence

### Step 5: Apply Phase 2 Migration
```bash
python manage.py migrate ai_partner 0029
```

## Testing Checklist

After fixes:
- [ ] All migrations apply cleanly
- [ ] Phase 2 tables exist in database
- [ ] Learning intelligence re-enabled
- [ ] No import errors on startup
- [ ] API endpoints use real data
- [ ] Frontend components persist data

## Risk Assessment

**High Risk**: Attempting fixes without proper backup
**Medium Risk**: Data loss if migrations are reset
**Low Risk**: Continuing with mock data (but blocks progress)

## Recommendation

DO NOT proceed with Phase 3 or any other features until this is fixed. The technical debt is compounding and will become unmanageable. The next session (106) must be dedicated entirely to fixing these migration issues properly.