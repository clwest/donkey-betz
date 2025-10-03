# PostgreSQL Integration Validator - Migration Plan

**CRITICAL**: This migration involves 359 expensive embeddings that must be preserved at all costs. Follow each step exactly as outlined.

## Overview

This plan creates a unified PostgreSQL database (`ai_unified_platform`) that both AI Content Studio and DBAO can share, with proper schema separation to prevent conflicts.

### Current State
- **AI Content Studio**: PostgreSQL database `ai_content_studio` with 359 embeddings (pgvector)
- **DBAO**: SQLite database `db.sqlite3` with betting/agent data

### Target State
- **Unified Database**: `ai_unified_platform` 
- **AI Content Studio**: Uses `studio` schema
- **DBAO**: Uses `dbao` schema
- **Shared**: Uses `shared` schema for common resources

## ⚠️ CRITICAL REQUIREMENTS

1. **NEVER proceed without complete backups**
2. **Embeddings are expensive to regenerate - they MUST be preserved**
3. **Test each step on development copies first**
4. **Have rollback procedures ready at every step**
5. **Verify embedding integrity after each migration step**

## Files Created

### Scripts
- `backup_all.sh` - Comprehensive backup script
- `verify_embeddings.py` - Embedding integrity verification
- `migrate_to_unified.sh` - Main migration script
- `rollback.sh` - Emergency rollback script

### Configuration Files
- `settings_unified.py` - Unified Django settings for both projects
- Updated `.env` files with unified database credentials

## Step-by-Step Migration Process

### Phase 1: Pre-Migration (MANDATORY)

#### 1.1 Create Complete Backups
```bash
cd /Users/donkeyking/development/donkey-betz-agent-orchestra
./backup_all.sh
```

**This will create:**
- PostgreSQL dump of `ai_content_studio` (custom format)
- Human-readable SQL dump
- **CRITICAL**: CSV backup of all 359 embeddings
- SQLite backup of DBAO database
- Django data dumps from both projects
- Configuration file backups

#### 1.2 Verify Backups
```bash
# Check backup directory was created
ls -la backup_*

# Verify embedding backup specifically
head backup_*/embeddings_critical_backup.csv
wc -l backup_*/embeddings_critical_backup.csv  # Should show 360 lines (359 + header)

# Test PostgreSQL backup integrity
pg_restore --list backup_*/ai_content_studio_full.dump
```

#### 1.3 Verify Current Embeddings
```bash
python verify_embeddings.py --source-db ai_content_studio --source-user ai_studio_user
```

**STOP HERE if any verification fails!**

### Phase 2: Migration Execution

#### 2.1 Run Migration Script
```bash
# Only proceed if Phase 1 completed successfully
./migrate_to_unified.sh
```

**This script will:**
1. Create `ai_unified_platform` database
2. Install pgvector, pg_trgm, and uuid-ossp extensions
3. Create schemas: `studio`, `dbao`, `shared`
4. Create unified user: `ai_unified_user`
5. Migrate AI Content Studio data to `studio` schema
6. **PRESERVE ALL 359 EMBEDDINGS**
7. Migrate DBAO data to `dbao` schema
8. Create unified Django settings files
9. Update environment variables

#### 2.2 Verify Migration Success
```bash
# Verify unified database exists
psql -d ai_unified_platform -U ai_unified_user -c "\l"

# Check schemas
psql -d ai_unified_platform -U ai_unified_user -c "\dn"

# CRITICAL: Verify all embeddings migrated
psql -d ai_unified_platform -U ai_unified_user -c "SELECT COUNT(*) FROM studio.memories WHERE embedding IS NOT NULL;"

# Test vector similarity search
psql -d ai_unified_platform -U ai_unified_user -c "SELECT id, content_text[1:50] FROM studio.memories WHERE embedding IS NOT NULL ORDER BY embedding <-> (SELECT embedding FROM studio.memories WHERE embedding IS NOT NULL LIMIT 1) LIMIT 3;"
```

#### 2.3 Run Full Embedding Verification
```bash
python verify_embeddings.py --target-db ai_unified_platform --target-user ai_unified_user --source-db ai_content_studio --source-user ai_studio_user
```

**STOP and rollback if embedding verification fails!**

### Phase 3: Application Integration

#### 3.1 Update AI Content Studio Settings
```bash
cd /Users/donkeyking/development/ai-content-studio/backend

# Backup current settings
cp core/settings.py core/settings_original_backup.py

# Test unified settings
python manage.py check --settings=core.settings_unified

# Run migrations if needed
python manage.py migrate --settings=core.settings_unified

# Test database connection
python manage.py shell --settings=core.settings_unified -c "
from django.db import connection
connection.ensure_connection()
print('AI Content Studio unified DB connection: OK')
"
```

#### 3.2 Update DBAO Settings
```bash
cd /Users/donkeyking/development/donkey-betz-agent-orchestra/backend

# Backup current settings
cp core/settings.py core/settings_original_backup.py

# Test unified settings
python manage.py check --settings=core.settings_unified

# Run migrations if needed
python manage.py migrate --settings=core.settings_unified

# Test database connection
python manage.py shell --settings=core.settings_unified -c "
from django.db import connection
connection.ensure_connection()
print('DBAO unified DB connection: OK')
"
```

#### 3.3 Integration Testing
```bash
# Test AI Content Studio functionality
cd /Users/donkeyking/development/ai-content-studio/backend
python manage.py runserver --settings=core.settings_unified &

# Test DBAO functionality  
cd /Users/donkeyking/development/donkey-betz-agent-orchestra/backend
python manage.py runserver 8001 --settings=core.settings_unified &

# Test both can read/write simultaneously
# Kill servers when testing complete
```

### Phase 4: Final Verification

#### 4.1 Complete Application Tests
- Test AI Content Studio memory/embedding features
- Test DBAO agent orchestration
- Verify no data conflicts between systems
- Test Redis cache separation
- Verify Celery task routing

#### 4.2 Performance Verification
- Test vector similarity search performance
- Verify cache hit rates
- Check database connection pooling
- Monitor memory usage

#### 4.3 Backup Verification
```bash
# Create new backup of unified system
./backup_all.sh

# Compare embedding counts
python verify_embeddings.py --source-db ai_unified_platform --source-user ai_unified_user
```

## Database Schema Structure

### ai_unified_platform Database

```
├── studio schema (AI Content Studio)
│   ├── memories (WITH 359 EMBEDDINGS)
│   ├── contents
│   ├── agents
│   ├── billing_*
│   ├── content_*
│   ├── assistant_*
│   └── [117 total tables]
│
├── dbao schema (DBAO)
│   ├── agents_*
│   ├── odds_calculator_*
│   ├── sports_*
│   └── [65+ total tables]
│
├── shared schema (Common resources)
│   ├── auth_user (if sharing users)
│   ├── django_session (if sharing sessions)
│   └── [shared tables as needed]
│
└── public schema
    ├── Extensions (vector, pg_trgm, uuid-ossp)
    └── Default PostgreSQL objects
```

### Connection Configuration

**AI Content Studio:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ai_unified_platform',
        'USER': 'ai_unified_user',
        'PASSWORD': 'ai_unified_pass_2025',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'options': '-c search_path=studio,shared,public',
        }
    }
}
```

**DBAO:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'ai_unified_platform',
        'USER': 'ai_unified_user',
        'PASSWORD': 'ai_unified_pass_2025',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'options': '-c search_path=dbao,shared,public',
        }
    }
}
```

## Emergency Rollback

If anything goes wrong during migration:

```bash
./rollback.sh
```

This will:
1. Drop unified database
2. Restore original AI Content Studio PostgreSQL
3. Restore original DBAO SQLite
4. Restore all configuration files
5. Verify all 359 embeddings are intact

## Cache Key Separation

To prevent conflicts between systems:

- **AI Content Studio**: `ai_studio_unified:*`
- **DBAO**: `dbao_unified:*`
- **WebSocket Channels**: Separate prefixes

## Monitoring and Maintenance

### Daily Checks
```bash
# Verify embedding count
psql -d ai_unified_platform -U ai_unified_user -c "SELECT COUNT(*) FROM studio.memories WHERE embedding IS NOT NULL;"

# Check database size
psql -d ai_unified_platform -U ai_unified_user -c "SELECT pg_size_pretty(pg_database_size('ai_unified_platform'));"

# Verify both applications can connect
python verify_embeddings.py --source-db ai_unified_platform --source-user ai_unified_user
```

### Weekly Maintenance
- Run `VACUUM ANALYZE` on unified database
- Check backup integrity
- Monitor cache hit rates
- Review connection pool usage

## Troubleshooting

### Migration Fails
1. **STOP immediately**
2. Run `./rollback.sh`
3. Review error logs
4. Fix issues and re-attempt

### Embedding Count Mismatch
1. **CRITICAL**: Do not proceed
2. Run embedding verification script
3. Compare with backup
4. Rollback if necessary

### Performance Issues
1. Check connection pool settings
2. Verify indexes on vector columns
3. Monitor cache hit rates
4. Consider adjusting schema search paths

### Schema Conflicts
1. Review table name overlaps
2. Check foreign key relationships
3. Verify search path configuration
4. Consider additional schema separation

## Success Criteria

- [ ] 359 embeddings preserved and verified
- [ ] Both applications connect successfully
- [ ] Vector similarity search works
- [ ] No data conflicts between systems
- [ ] Cache separation working
- [ ] Celery tasks route correctly
- [ ] Performance acceptable
- [ ] Backup/restore tested
- [ ] Rollback procedure verified

## Next Steps After Migration

1. Update application startup scripts to use `settings_unified`
2. Update deployment configurations
3. Monitor performance and optimize as needed
4. Plan regular backup schedule for unified database
5. Consider implementing connection pooling (pgbouncer)
6. Document any application-specific changes needed

---

**Remember**: The 359 embeddings are irreplaceable. Every step must prioritize their preservation. When in doubt, rollback and reassess.