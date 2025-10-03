# Phase 2: Database Schema Unification Agent

## IMPORTANT: READ THIS FIRST
You are working in a TEST ENVIRONMENT at:
`/Users/donkeyking/development/unification-workspace/`

**DO NOT TOUCH PRODUCTION DATABASES**

## Your Mission
Consolidate duplicate models and create unified base classes for all entities.

## Prerequisites
- Phase 1 must be complete
- Check for handoff file: `../../shared/handoff/phase1.json`
- Python virtual environment activated
- Test database: `ai_unified_test_db`

## Database Connections
- Test DB: `ai_unified_test_db` (NOT PRODUCTION)
- Backup location: `./shared/backups/`
- Log location: `./shared/logs/`

## Steps to Execute

### Step 1: Read Phase 1 Handoff
```python
import json
with open('../../shared/handoff/phase1.json') as f:
    phase1_data = json.load(f)
print(f"Phase 1 completed at: {phase1_data['timestamp']}")
```

### Step 2: Create Unified Base Models
Create file: `backend/core/unified_models.py`
```python
from django.db import models
import uuid

class UnifiedBaseModel(models.Model):
    """Universal base model for all entities"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict)
    version = models.IntegerField(default=1)
    
    class Meta:
        abstract = True

class UnifiedAgent(UnifiedBaseModel):
    """Base class for all agent types"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    capabilities = models.JSONField(default=list)
    system_prompt = models.TextField()
    
    class Meta:
        abstract = True
```

### Step 3: Create Schema Mapping
Document old to new model mappings in `schema_mapping.json`

### Step 4: Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Success Criteria
- [ ] `backend/core/unified_models.py` created with base classes
- [ ] Migration scripts for model consolidation created
- [ ] `schema_mapping.json` documenting old->new mappings
- [ ] Validation script confirming no data loss
- [ ] Handoff JSON created at `shared/handoff/phase2.json`

## Testing Your Work
Run: `python test_script.py`

## If Something Goes Wrong
Run: `bash rollback.sh`

## Handoff
When complete, create `../../shared/handoff/phase2.json` with:
```json
{
  "phase": 2,
  "status": "complete",
  "timestamp": "ISO-8601 timestamp",
  "unified_models_created": true,
  "migrations_applied": ["0001_unified_base", "0002_agent_inheritance"],
  "schema_mapping": "schema_mapping.json",
  "models_unified": {
    "base_models": 2,
    "agent_models": 10
  }
}
```

## Notes
- Ensure backward compatibility with existing models
- Create comprehensive schema documentation
- Test all model relationships before proceeding
- Backup database before applying migrations