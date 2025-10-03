# Memory UnifiedMemoryEntry Deprecation Plan

## Overview

This document outlines the plan to deprecate `memory.UnifiedMemoryEntry` in favor of the primary `shared_memory.UnifiedMemoryEntry` system.

## Current Status (August 4, 2025)

### Three UnifiedMemoryEntry Models Exist:
1. **shared_memory.UnifiedMemoryEntry** - Primary UKF system (40,734 records)
2. **memory.UnifiedMemoryEntry** - Legacy system (29,856 records) 
3. **learning_intelligence.UnifiedMemoryEntry** - Specialized learning system (12 records)

### Progress Made:
- ✅ Data migration completed (35,632 records migrated)
- ✅ Memory Palace views updated to import from shared_memory
- ✅ Fixed model-table mismatch with `db_table = 'memory_memoryentry'`
- ✅ All UnifiedUnifiedMemoryEntry typos fixed

## Deprecation Steps

### Phase 1: Update Serializers (Immediate)
1. Check if `memory.serializers.UnifiedMemoryEntrySerializer` is compatible with `shared_memory.UnifiedMemoryEntry`
2. Update serializer imports if needed
3. Test all Memory Palace endpoints

### Phase 2: Verify Frontend Compatibility (1 week)
1. Test Memory Palace UI with new backend
2. Ensure all CRUD operations work correctly
3. Verify search functionality
4. Check that symbolic anchors still connect properly

### Phase 3: Final Migration (2 weeks)
1. Create management command to verify all legacy records are in UKF
2. Add database constraint to prevent new records in legacy table
3. Update any remaining references

### Phase 4: Remove Legacy Model (1 month)
1. Remove `UnifiedMemoryEntry` from memory/models.py
2. Create migration to drop foreign key constraints
3. Archive the legacy table (don't delete immediately)
4. Remove legacy serializers and views

## Testing Checklist

- [ ] Memory Palace can create new memories in UKF
- [ ] Memory Palace can read/update/delete UKF memories
- [ ] Symbolic anchor relationships work correctly
- [ ] Memory chains function properly
- [ ] Search returns results from UKF
- [ ] No new records created in legacy table

## Rollback Plan

If issues arise:
1. Revert view imports to use memory.UnifiedMemoryEntry
2. Legacy data remains intact in memory_memoryentry table
3. Re-run consolidation if needed

## Success Metrics

- Zero errors in Memory Palace after migration
- No new records in memory_memoryentry table
- All memory operations use shared_memory.UnifiedMemoryEntry
- Performance remains stable or improves

## Timeline

- Week 1: Serializer updates and testing
- Week 2: Frontend verification
- Week 3: Final migration and constraints
- Week 4: Model removal and cleanup