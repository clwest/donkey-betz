# Memory Unification Phase 2: Legacy Records Investigation

## 🎯 Mission for Session 63

Investigate and migrate the remaining 14,660 legacy memory records that failed to migrate in Session 61.

## Current Situation

### What We Know
- **Total Legacy Records**: 29,856 in memory_memoryentry table
- **Successfully Migrated**: 15,196 records (51%)
- **Failed/Skipped**: 14,660 records (49%)
- **Current Coverage**: 77.6% (56,773 out of 73,187)

### Key Questions to Answer
1. Why did only 51% of legacy records migrate?
2. Are the remaining records invalid, duplicates, or have data issues?
3. What's preventing these records from migrating?
4. Can we safely migrate the remaining records?

## Investigation Steps

### Step 1: Analyze Failed Records
```sql
-- Check characteristics of unmigrated records
SELECT COUNT(*), 
       CASE 
         WHEN event IS NULL OR event = '' THEN 'empty_event'
         WHEN user_id IS NULL THEN 'no_user'
         WHEN is_active = false THEN 'inactive'
         ELSE 'other'
       END as issue_type
FROM memory_memoryentry
WHERE id NOT IN (
  SELECT (context_data->>'legacy_id')::uuid 
  FROM unified_memory_entries 
  WHERE source_system = 'memory'
)
GROUP BY issue_type;
```

### Step 2: Check Migration Logs
```python
# Check SystemMigrationLog for errors
from shared_memory.models import SystemMigrationLog
logs = SystemMigrationLog.objects.filter(
    source_system='memory',
    status__in=['failed', 'partial']
).order_by('-started_at')
```

### Step 3: Sample Failed Records
```python
# Get sample of unmigrated records
from memory.models import LegacyUnifiedMemoryEntry
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT * FROM memory_memoryentry 
        WHERE id NOT IN (
            SELECT (context_data->>'legacy_id')::uuid 
            FROM unified_memory_entries 
            WHERE source_system = 'memory'
        )
        LIMIT 10
    """)
    # Analyze the data
```

## Potential Issues to Check

### 1. Data Quality Issues
- Empty or null content (event field)
- Missing user associations
- Corrupted JSON fields
- Invalid timestamps

### 2. Duplicate Detection
- Check if content_hash logic is preventing duplicates
- Verify hash calculation consistency

### 3. Migration Logic Issues
- Batch size limitations
- Transaction rollbacks
- Offset calculation errors

### 4. Active/Inactive Records
- Check if is_active=false records were intentionally skipped
- Verify if this was a design decision

## Migration Strategy Options

### Option A: Fix and Retry
1. Identify specific issues preventing migration
2. Update migration bridge to handle edge cases
3. Re-run migration for failed records

### Option B: Force Migration
1. Create a more lenient migration script
2. Accept some data quality issues
3. Mark problematic records for later cleanup

### Option C: Archive and Move On
1. Document why records can't be migrated
2. Archive them separately
3. Accept 77.6% as final coverage

## Commands to Run

```bash
# Check current state
python manage.py unify_memories --phase verify

# Investigate failed records
python manage.py shell
>>> from shared_memory.legacy_memory_bridge import LegacyMemoryBridge
>>> bridge = LegacyMemoryBridge()
>>> # Analyze why records failed

# Try migration with verbose logging
python manage.py unify_memories --phase legacy --verbose
```

## Success Criteria

1. Understand why 14,660 records didn't migrate
2. Achieve 90%+ unified coverage if possible
3. Document any records that can't be migrated
4. Ensure data integrity for migrated records
5. Create plan for remaining ConversationMemory records

## Files to Review

1. `/backend/shared_memory/legacy_memory_bridge.py` - Migration logic
2. `/backend/memory/models.py` - Legacy model structure
3. `/backend/shared_memory/management/commands/unify_memories.py` - Command logic
4. Migration logs in SystemMigrationLog table

## Next Steps After Investigation

Based on findings, either:
1. Fix issues and complete migration
2. Create specialized migration for edge cases
3. Document unmigrateable records and move to ConversationMemory migration
4. Consider if 77.6% coverage is acceptable for production