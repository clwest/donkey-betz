# Database Fix Plan - Comprehensive Solution

## ✅ STATUS: SUCCESSFULLY RESOLVED (Session 121)
**Date Fixed**: August 9, 2025  
**All database issues have been resolved. See DATABASE_FIX_SUCCESS_REPORT.md for details.**

---

## Problem Summary (RESOLVED)
The application has database schema mismatches causing errors:
1. Missing column `unified_memory_entries.relationships`
2. Missing column `agent_orchestra_agentresult.mythology_confidence`
3. Type mismatch in `ai_partner_conversationembedding.conversation_id`
4. Unapplied migrations that can't be run due to dependencies

## Solution Overview
We'll create a fresh approach to fix the database without losing data or dealing with complex migration dependencies.

## Step-by-Step Plan

### Step 1: Stop All Services
```bash
# Stop all running services
make stop-services
# Or manually:
pkill -f "python.*manage.py"
pkill -f "celery"
pkill -f "daphne"
```

### Step 2: Run the Database Fix Script
```bash
cd backend
python fix_database_schema.py
```

This script will:
- Add missing columns to `unified_memory_entries`
- Add missing columns to `agent_orchestra_agentresult`
- Fix type mismatches
- Create missing indexes
- Mark problematic migrations as applied

### Step 3: Verify Database Schema
```bash
# Check that columns exist
python manage.py dbshell
\d unified_memory_entries
\d agent_orchestra_agentresult
\q
```

### Step 4: Clean Python Cache
```bash
# Remove all Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
```

### Step 5: Test Individual Components
```bash
# Test database connection
python manage.py shell
>>> from shared_memory.models import UnifiedMemoryEntry
>>> UnifiedMemoryEntry.objects.count()
>>> exit()

# Test API endpoints
python manage.py runserver 0.0.0.0:8000
# In another terminal:
curl http://localhost:8000/api/auth/user/
```

### Step 6: Start Services One by One
```bash
# 1. Start Redis
redis-server

# 2. Start Django (in new terminal)
cd backend
python manage.py runserver 0.0.0.0:8000

# 3. Start Daphne for WebSockets (in new terminal)
cd backend
daphne -b 0.0.0.0 -p 8001 server.asgi:application

# 4. Start Celery (in new terminal)
cd backend
celery -A server worker -l info

# 5. Start Frontend (in new terminal)
cd donkey-betz-frontend
npm run dev
```

### Step 7: Test the Application
1. Open http://localhost:5173
2. Login as testuser
3. Check dashboard loads without errors
4. Verify WebSocket connection works

## Alternative: Fresh Database (Nuclear Option)

If the above doesn't work, create a fresh database:

### Option A: Reset Specific Tables
```sql
-- Connect to database
psql -U moveyourazz_user -d moveyourazz_dev

-- Drop and recreate problematic tables
DROP TABLE IF EXISTS unified_memory_entries CASCADE;
DROP TABLE IF EXISTS agent_orchestra_agentresult CASCADE;

-- Exit
\q
```

Then run migrations:
```bash
python manage.py migrate
```

### Option B: Complete Fresh Start
```bash
# Backup current data (optional)
pg_dump -U moveyourazz_user moveyourazz_dev > backup.sql

# Drop and recreate database
dropdb moveyourazz_dev
createdb moveyourazz_dev -O moveyourazz_user

# Run all migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load fixtures if any
python manage.py loaddata initial_data.json
```

## Testing Checklist

After fixes, verify these work:
- [ ] Backend starts without migration warnings
- [ ] Dashboard loads without errors
- [ ] WebSocket connects successfully
- [ ] No "column does not exist" errors in logs
- [ ] API endpoints return data
- [ ] Celery tasks execute

## Common Issues and Solutions

### Issue: "column does not exist" still appears
**Solution**: The model might be cached. Restart all Python processes and clear cache.

### Issue: "relation does not exist"
**Solution**: The table wasn't created. Run the specific migration or create manually.

### Issue: Type mismatch errors
**Solution**: Check foreign key relationships match types (UUID vs BigInt).

### Issue: Migration won't apply
**Solution**: Mark it as fake-applied or edit the migration file to remove problematic operations.

## Monitoring Commands

```bash
# Check migration status
python manage.py showmigrations

# Check database tables
python manage.py dbshell
\dt

# Check specific table schema
\d table_name

# Watch logs
tail -f logs/*.log
```

## Success Criteria ✅ ALL MET

The system is fixed when:
1. No database errors in console
2. Dashboard loads completely
3. All API endpoints return 200 status
4. WebSocket connects and stays connected
5. No migration warnings on startup

## Next Steps After Fix

1. Create database backup
2. Document the final working schema
3. Update migration files to match reality
4. Test all features thoroughly
5. Commit the fixes

## Support Commands

```bash
# Quick health check
curl http://localhost:8000/api/core/dashboard/stats/

# Check WebSocket
wscat -c ws://localhost:8001/ws/dashboard-stats/

# Monitor database connections
SELECT * FROM pg_stat_activity WHERE datname = 'moveyourazz_dev';
```