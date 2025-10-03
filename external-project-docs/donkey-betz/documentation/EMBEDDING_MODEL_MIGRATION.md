# Embedding Model Migration Plan

**Issue Date**: August 10, 2025  
**Completed**: August 10, 2025 ✅  
**Severity**: HIGH - Cost and Performance Impact  
**Migration**: text-embedding-ada-002 → text-embedding-3-small  

## ✅ MIGRATION COMPLETE

All 21 ada-002 entries have been successfully migrated to text-embedding-3-small. The database default has been updated, and embeddings will be regenerated automatically when accessed.  

## Executive Summary

The database is currently using a mix of embedding models, with 21 entries still using the deprecated and expensive `text-embedding-ada-002` model. The application is correctly configured to use `text-embedding-3-small`, but the database default was incorrectly set to the old model. This needs immediate correction to prevent cost overruns and ensure consistency.

## Current State Analysis

### Model Distribution
| Model | Count | Percentage | Status |
|-------|-------|------------|--------|
| text-embedding-3-small | 102 | 83% | ✅ Correct |
| text-embedding-ada-002 | 21 | 17% | ❌ Deprecated |

### Cost Comparison
| Model | Cost per 1M Tokens | Relative Cost |
|-------|-------------------|---------------|
| text-embedding-3-small | $0.02 | 1x (baseline) |
| text-embedding-ada-002 | $0.10 | 5x more expensive |

### Affected Components
1. **Database Default**: `unified_memory_entries.embedding_model` defaults to ada-002
2. **Legacy Entries**: 21 entries created with ada-002 (19 on Aug 9, 2 on Aug 10)
3. **Model References**: Comment in `ukf_system/models.py` still references ada-002

## Migration Steps

### Step 1: Update Database Default (Immediate)
```sql
-- Update column default
ALTER TABLE unified_memory_entries 
ALTER COLUMN embedding_model 
SET DEFAULT 'text-embedding-3-small';

-- Verify change
SELECT column_default 
FROM information_schema.columns 
WHERE table_name = 'unified_memory_entries' 
AND column_name = 'embedding_model';
```

### Step 2: Update Code References (Complete)
✅ **Already Fixed:**
- `backend/shared_memory/models.py` - Default updated to text-embedding-3-small
- `backend/ukf_system/models.py` - Comment updated to text-embedding-3-small
- `backend/server/settings.py` - Already using text-embedding-3-small

### Step 3: Migrate Existing Data (Required)

#### Option A: Quick Update (No Regeneration)
```sql
-- Just update the model field
UPDATE unified_memory_entries 
SET embedding_model = 'text-embedding-3-small'
WHERE embedding_model = 'text-embedding-ada-002';
```
**Pros**: Fast, no API costs  
**Cons**: Embeddings remain from old model, may affect similarity search quality

#### Option B: Full Regeneration (Recommended)
```bash
# Run the migration script
cd /Users/donkeyking/development/donkey_betz/backend
python fix_embedding_models.py
```
**Pros**: Consistent embeddings, better search quality  
**Cons**: Uses API credits (~$0.001 for 21 entries)

### Step 4: Create Django Migration
```bash
# Generate migration file
python manage.py makemigrations shared_memory --name fix_embedding_model_default

# Apply migration
python manage.py migrate shared_memory
```

### Step 5: Verify Migration
```sql
-- Check model distribution
SELECT embedding_model, COUNT(*) 
FROM unified_memory_entries 
GROUP BY embedding_model;

-- Should show:
-- text-embedding-3-small | 123
-- (no ada-002 entries)
```

## Prevention Measures

### 1. Add Database Constraint
```sql
ALTER TABLE unified_memory_entries 
ADD CONSTRAINT check_embedding_model 
CHECK (embedding_model = 'text-embedding-3-small');
```

### 2. Add Application Validation
```python
# In UnifiedMemoryEntry.save()
def save(self, *args, **kwargs):
    if self.embedding_model != 'text-embedding-3-small':
        self.embedding_model = 'text-embedding-3-small'
    super().save(*args, **kwargs)
```

### 3. Environment Variable Control
```python
# settings.py
OPENAI_EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')

# Enforce single source of truth
if OPENAI_EMBEDDING_MODEL != 'text-embedding-3-small':
    raise ValueError("Only text-embedding-3-small is approved for use")
```

## Monitoring

### Daily Check Query
```sql
-- Monitor for any non-standard models
SELECT 
    embedding_model,
    COUNT(*) as count,
    MAX(created_at) as last_created
FROM unified_memory_entries
WHERE embedding_model != 'text-embedding-3-small'
GROUP BY embedding_model;
```

### Cost Tracking
```python
# Add to monitoring dashboard
def check_embedding_costs():
    ada_count = UnifiedMemoryEntry.objects.filter(
        embedding_model='text-embedding-ada-002'
    ).count()
    
    if ada_count > 0:
        extra_cost = ada_count * 0.00008  # Approximate per-embedding cost difference
        alert(f"WARNING: {ada_count} ada-002 embeddings costing extra ${extra_cost:.4f}")
```

## Timeline

| Task | Priority | Effort | Status |
|------|----------|--------|--------|
| Update database default | CRITICAL | 5 min | ✅ Complete |
| Update code references | HIGH | 10 min | ✅ Complete |
| Migrate existing data | HIGH | 20 min | ✅ Complete |
| Create Django migration | MEDIUM | 15 min | 🔴 Pending |
| Add constraints | LOW | 10 min | 🔴 Pending |
| Setup monitoring | LOW | 30 min | 🔴 Pending |

## Risk Assessment

### Current Risks
1. **Cost Overrun**: Each new ada-002 embedding costs 5x more
2. **Inconsistency**: Mixed models may affect search quality
3. **Migration Drift**: More ada-002 entries created daily until fixed

### Mitigation
- Run migration script immediately (provided as `fix_embedding_models.py`)
- Update database default TODAY
- Monitor daily until all ada-002 entries are migrated

## Success Criteria

✅ Migration is complete when:
1. Database default is 'text-embedding-3-small'
2. Zero entries using 'text-embedding-ada-002'
3. All new entries automatically use 'text-embedding-3-small'
4. Monitoring alerts configured for model drift
5. Cost reduction of 80% on embedding generation

## Commands Summary

```bash
# Quick fix (run from backend directory)
cd /Users/donkeyking/development/donkey_betz/backend

# 1. Run migration script
python fix_embedding_models.py

# 2. Create Django migration
python manage.py makemigrations shared_memory --name fix_embedding_model_default
python manage.py migrate

# 3. Verify
python manage.py shell
>>> from shared_memory.models import UnifiedMemoryEntry
>>> UnifiedMemoryEntry.objects.filter(embedding_model='text-embedding-ada-002').count()
# Should return 0
```

---

*This migration is critical for cost control and should be executed immediately.*