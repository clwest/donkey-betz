# Phase 1: Foundation Assessment Agent

## IMPORTANT: READ THIS FIRST
You are working in a TEST ENVIRONMENT at:
`/Users/donkeyking/development/unification-workspace/`

**DO NOT TOUCH PRODUCTION DATABASES**

## Your Mission
Create comprehensive system backup and tracking infrastructure for the unification process.

## Database Connections
- Test DB: `ai_unified_test_db` (NOT PRODUCTION)
- Backup location: `./shared/backups/`
- Log location: `./shared/logs/`

## Prerequisites
- Python virtual environment activated: `source ../../.venv/bin/activate`
- Test database created: `ai_unified_test_db`
- Django project copied to test environment

## Steps to Execute

### Step 1: Create Timestamped Backup
```bash
mkdir -p ../../shared/backups/pre-unification-$(date +%Y%m%d_%H%M%S)
cp -r backend/ ../../shared/backups/pre-unification-$(date +%Y%m%d_%H%M%S)/
pg_dump ai_unified_test_db > ../../shared/backups/pre-unification-$(date +%Y%m%d_%H%M%S)/database.sql
```

### Step 2: Generate System Inventory
```bash
python manage.py shell -c "
from agents.models import AgentTemplate, AgentInstance
print(f'Agent Templates: {AgentTemplate.objects.count()}')
print(f'Agent Instances: {AgentInstance.objects.count()}')
" > ../../shared/logs/system_inventory.txt
```

### Step 3: Create Unification Tracking
```bash
python manage.py makemigrations --name add_unification_tracking
python manage.py migrate
```

## Success Criteria
- [ ] Complete backup in `shared/backups/` directory
- [ ] `system_inventory.txt` with current metrics
- [ ] `unification_status.json` tracking file created
- [ ] Migration for UnificationTracking model applied
- [ ] Handoff JSON created at `shared/handoff/phase1.json`

## Testing Your Work
Run: `python test_script.py`

## If Something Goes Wrong
Run: `bash rollback.sh`

## Handoff
When complete, create `../../shared/handoff/phase1.json` with:
```json
{
  "phase": 1,
  "status": "complete",
  "timestamp": "ISO-8601 timestamp",
  "backup_location": "shared/backups/pre-unification-TIMESTAMP/",
  "inventory_file": "shared/logs/system_inventory.txt",
  "tracking_enabled": true,
  "metrics": {
    "agent_templates": 0,
    "agent_instances": 0
  }
}
```

## Notes
- All paths are relative to this agent's directory
- Log all actions to `shared/logs/phase1.log`
- Ensure test database is used, never production
- Create incremental backups before any destructive operations