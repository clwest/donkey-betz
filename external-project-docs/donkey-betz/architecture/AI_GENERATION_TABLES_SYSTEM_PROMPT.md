# System Prompt: Create Missing AI Generation Database Tables

## Mission Statement
You are tasked with creating and applying Django migrations for missing AI Generation database tables in the Donkey Betz project. These tables exist as Django models but were never migrated to the database, causing 500 Internal Server Errors across multiple endpoints.

## Context & Background

### Issue Discovery
During Session 145, multiple 500 errors were identified when testing frontend endpoints:
- `/api/content/quota/status/` - 500 error
- `/api/content/brand-identity/active/` - 500 error  
- `/api/content/assets/?ai_only=true` - 500 error
- `/api/content/statistics/?days=30` - 500 error

**Root Cause**: Django models exist in `content/models/ai_generation.py` but corresponding database tables were never created.

### Current Status
- ✅ **Models Defined**: All AI generation models exist in Django code
- ✅ **Models Imported**: Properly imported in `content/models/__init__.py`
- ✅ **Views Created**: ViewSets and endpoints exist and reference these models
- ❌ **Database Tables**: Missing - never migrated to PostgreSQL database
- ✅ **Temporary Fix**: Error handling added to prevent 500s (returns mock data)

### Missing Database Tables
Based on error analysis, these tables don't exist:
1. `content_aigeneratedasset`
2. `content_assetgenerationquota` 
3. `content_brandidentity`
4. `content_assetgenerationrequest`

## Your Task

### Primary Goal
Create proper Django migrations and apply them to establish the missing AI generation database tables.

### Success Criteria
- ✅ All 4 missing tables created in PostgreSQL database
- ✅ Django migrations applied successfully (0 unapplied migrations)
- ✅ All content endpoints return 200 status instead of 500
- ✅ Frontend can successfully fetch real data from AI generation endpoints
- ✅ No breaking changes to existing functionality

## Technical Environment

### Database Configuration
```bash
# PostgreSQL Connection Details
Host: 127.0.0.1
Port: 5432  
Database: moveyourazz_dev
Username: moveyourazz_user
Password: secure_password

# Connection Test
PGPASSWORD=secure_password psql -h 127.0.0.1 -p 5432 -U moveyourazz_user -d moveyourazz_dev -c "\dt content_*"
```

### Django Environment
```bash
# Working Directory
cd /Users/donkeyking/development/donkey_betz/backend

# Django Management Commands
python manage.py makemigrations content
python manage.py migrate content
python manage.py showmigrations content
```

### Key Files
- **Models**: `/backend/content/models/ai_generation.py`
- **Views**: `/backend/content/views_ai_generation.py` 
- **URLs**: `/backend/content/urls.py`
- **Migrations**: `/backend/content/migrations/`

## Required Models Analysis

### 1. BrandIdentity Model
**Purpose**: Comprehensive brand identity for AI asset generation
**Key Fields**:
- `user` - ForeignKey to User
- `business_name` - CharField(max_length=200)
- `tagline` - CharField(max_length=500, blank=True)
- `colors` - JSONField(default=dict)
- `typography` - JSONField(default=dict)
- `voice_tone` - JSONField(default=dict)
- `imagery_style` - JSONField(default=dict)
- `values_mission` - JSONField(default=dict)
- `target_audience` - JSONField(default=dict)
- `usage_guidelines` - JSONField(default=dict)
- `is_active` - BooleanField(default=True)
- `created_at` - DateTimeField(auto_now_add=True)
- `updated_at` - DateTimeField(auto_now=True)

### 2. AssetGenerationQuota Model  
**Purpose**: User quota management for AI generation
**Key Fields**:
- `user` - OneToOneField to User
- `daily_limit` - IntegerField(default=100)
- `daily_used` - IntegerField(default=0)
- `monthly_limit` - IntegerField(default=1000)
- `monthly_used` - IntegerField(default=0) 
- `credits_balance` - IntegerField(default=0)
- `last_daily_reset` - DateTimeField
- `last_monthly_reset` - DateTimeField
- `created_at` - DateTimeField(auto_now_add=True)
- `updated_at` - DateTimeField(auto_now=True)

### 3. AssetGenerationRequest Model
**Purpose**: Track AI generation requests and their status
**Key Fields**:
- `request_id` - UUIDField(default=uuid.uuid4, unique=True)
- `user` - ForeignKey to User
- `brand_identity` - ForeignKey to BrandIdentity (nullable)
- `asset_type` - CharField(max_length=50)
- `status` - CharField (pending/processing/completed/failed/cancelled)
- `progress` - IntegerField(default=0)
- `prompt` - TextField
- `generation_settings` - JSONField(default=dict)
- `generated_assets` - JSONField(default=list)
- `error_message` - TextField(blank=True)
- `task_id` - CharField(max_length=100, blank=True)
- `created_at` - DateTimeField(auto_now_add=True)
- `updated_at` - DateTimeField(auto_now=True)

### 4. AIGeneratedAsset Model
**Purpose**: Store generated AI assets with metadata
**Key Fields**:
- `user` - ForeignKey to User
- `brand_identity` - ForeignKey to BrandIdentity (nullable)
- `asset_type` - CharField (logo/brand_colors/typography/marketing/product_visual/social_media)
- `name` - CharField(max_length=200)
- `file_url` - URLField
- `thumbnail_url` - URLField(blank=True)
- `metadata` - JSONField(default=dict)
- `style_attributes` - JSONField(default=dict)
- `quality_score` - FloatField(default=0.0)
- `generation_prompt` - TextField
- `generation_settings` - JSONField(default=dict)
- `is_favorite` - BooleanField(default=False)
- `created_at` - DateTimeField(auto_now_add=True)
- `updated_at` - DateTimeField(auto_now=True)

## Step-by-Step Implementation Guide

### Phase 1: Analysis & Preparation (15 minutes)
1. **Verify Current State**:
   ```bash
   # Check existing content migrations
   python manage.py showmigrations content
   
   # Verify models are importable
   python manage.py shell -c "from content.models.ai_generation import BrandIdentity, AssetGenerationQuota, AIGeneratedAsset, AssetGenerationRequest; print('All models import successfully')"
   
   # Check current database tables
   PGPASSWORD=secure_password psql -h 127.0.0.1 -p 5432 -U moveyourazz_user -d moveyourazz_dev -c "\dt content_*" | grep -E "(brand|asset|quota|generation)"
   ```

2. **Analyze Model Dependencies**:
   - Check for any ForeignKey relationships
   - Verify import paths are correct
   - Ensure no circular dependencies

### Phase 2: Migration Creation (20 minutes)
1. **Generate Migrations**:
   ```bash
   # Try automatic migration detection
   python manage.py makemigrations content --dry-run --verbosity=2
   
   # If automatic detection fails, create empty migration and populate manually
   python manage.py makemigrations content --empty
   ```

2. **Manual Migration Creation** (if needed):
   - Edit the created migration file
   - Add CreateModel operations for each missing model
   - Include proper dependencies and field definitions
   - Ensure correct table names (`db_table` if different from default)

3. **Migration Validation**:
   ```bash
   # Check SQL that will be generated
   python manage.py sqlmigrate content [migration_number]
   
   # Validate migration without applying
   python manage.py migrate content --plan
   ```

### Phase 3: Database Application (15 minutes)
1. **Apply Migrations**:
   ```bash
   # Apply the new migration
   python manage.py migrate content
   
   # Verify no unapplied migrations remain
   python manage.py showmigrations content | grep "\\[ \\]"
   ```

2. **Verify Table Creation**:
   ```bash
   # Check that all tables were created
   PGPASSWORD=secure_password psql -h 127.0.0.1 -p 5432 -U moveyourazz_user -d moveyourazz_dev -c "\dt content_*" | grep -E "(brand|asset|quota|generation)"
   
   # Verify table structure for key models
   PGPASSWORD=secure_password psql -h 127.0.0.1 -p 5432 -U moveyourazz_user -d moveyourazz_dev -c "\d content_brandidentity"
   ```

### Phase 4: Endpoint Testing (20 minutes)  
1. **Test Model Operations**:
   ```bash
   # Test basic model operations through Django shell
   python manage.py shell -c "
   from content.models.ai_generation import BrandIdentity
   from django.contrib.auth import get_user_model
   User = get_user_model()
   user = User.objects.first()
   brand = BrandIdentity.objects.create(user=user, business_name='Test Business')
   print(f'✅ BrandIdentity created: {brand.id}')
   "
   ```

2. **Test API Endpoints**:
   ```bash
   # Test endpoints that were previously failing (requires authentication)
   curl -X GET "http://localhost:8001/api/content/quota/status/" -H "Authorization: Token YOUR_TOKEN"
   curl -X GET "http://localhost:8001/api/content/brand-identity/active/" -H "Authorization: Token YOUR_TOKEN"  
   curl -X GET "http://localhost:8001/api/content/assets/?ai_only=true" -H "Authorization: Token YOUR_TOKEN"
   curl -X GET "http://localhost:8001/api/content/statistics/?days=30" -H "Authorization: Token YOUR_TOKEN"
   ```

3. **Verify Error Handling Removal**:
   - Check that endpoints return real data instead of mock responses
   - Verify 200 status codes instead of previous 500 errors
   - Test that the temporary error handling gracefully handles empty data

## Potential Challenges & Solutions

### Challenge 1: Migration Auto-Detection Fails
**Symptoms**: `makemigrations` reports "No changes detected"
**Cause**: Models not properly registered or import issues
**Solution**: 
- Verify models are imported in `content/models/__init__.py`
- Check for syntax errors in model definitions
- Try `python manage.py makemigrations content --empty` and manually populate

### Challenge 2: Foreign Key Dependency Issues
**Symptoms**: Migration fails due to missing referenced tables
**Cause**: Referenced models don't exist or incorrect relationships
**Solution**:
- Check that User model exists (should be django.contrib.auth.User)
- Verify ForeignKey field names and related_name attributes
- Consider using string references for forward declarations

### Challenge 3: JSON Field Issues  
**Symptoms**: Migration fails on JSONField creation
**Cause**: PostgreSQL version or django.contrib.postgres not configured
**Solution**:
- Verify PostgreSQL supports JSON (9.4+)
- Ensure `django.contrib.postgres` in INSTALLED_APPS
- Consider using TextField with JSON validation if issues persist

### Challenge 4: Table Already Exists Errors
**Symptoms**: Migration fails with "relation already exists" 
**Cause**: Partial migration or manual table creation
**Solution**:
- Check existing tables: `\dt content_*`
- Use `--fake` flag if tables exist but migration not recorded
- Drop problematic tables if safe to recreate

## Validation & Testing

### Database Validation
```sql
-- Verify all tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name LIKE 'content_%generation%' 
OR table_name LIKE 'content_%asset%' 
OR table_name LIKE 'content_brand%';

-- Check row counts (should be 0 for new tables)
SELECT 'content_brandidentity' as table_name, COUNT(*) as rows FROM content_brandidentity
UNION ALL SELECT 'content_assetgenerationquota', COUNT(*) FROM content_assetgenerationquota  
UNION ALL SELECT 'content_aigeneratedasset', COUNT(*) FROM content_aigeneratedasset
UNION ALL SELECT 'content_assetgenerationrequest', COUNT(*) FROM content_assetgenerationrequest;
```

### Django Model Validation
```bash
# Verify model operations work
python manage.py shell -c "
from content.models.ai_generation import *
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.first()

# Test each model creation
brand = BrandIdentity.objects.create(user=user, business_name='Test')
quota = AssetGenerationQuota.objects.create(user=user)
request = AssetGenerationRequest.objects.create(user=user, asset_type='logo', prompt='test')  
asset = AIGeneratedAsset.objects.create(user=user, asset_type='logo', name='test', file_url='http://test.com', generation_prompt='test')

print('✅ All models created successfully')
"
```

### Endpoint Validation
- Test each previously failing endpoint
- Verify 200 status codes
- Confirm JSON response structure matches expectations
- Ensure no mock data indicators in responses

## Success Metrics

### Technical Metrics
- ✅ 0 unapplied Django migrations
- ✅ 4 new database tables created
- ✅ All model CRUD operations work
- ✅ No SQL errors in Django logs

### Functional Metrics  
- ✅ All content endpoints return 200 status
- ✅ Frontend receives real data instead of mock responses
- ✅ User can interact with AI generation features
- ✅ No JavaScript console errors related to API calls

## Post-Implementation

### Documentation Updates
1. Update `CLAUDE.md` with completion status
2. Document any manual migration steps taken
3. Note any deviations from standard Django migration process

### Testing Recommendations
1. Create basic data fixtures for development
2. Test full AI generation workflow end-to-end
3. Verify quota management works correctly
4. Test brand identity management features

### Future Considerations
1. **Data Migration**: If production has mock data, plan migration strategy
2. **Performance**: Consider adding database indexes for frequently queried fields
3. **Backup**: Ensure backup strategy covers new tables
4. **Monitoring**: Add monitoring for AI generation usage and quotas

---

## Final Verification Checklist

Before marking this task complete, verify:

- [ ] `python manage.py showmigrations content` shows all migrations applied
- [ ] Database contains all 4 new tables with correct structure  
- [ ] `curl` tests return 200 status for all previously failing endpoints
- [ ] Django shell can create/read/update/delete records in all new models
- [ ] No 500 errors in Django logs when accessing AI generation features
- [ ] Frontend can successfully load AI generation pages without errors

**Expected Time**: 60-90 minutes total
**Priority**: HIGH - Blocks AI generation functionality
**Risk Level**: LOW - New tables, no existing data affected

---

*This system prompt created during Session 145 after identifying and temporarily fixing 500 errors with mock data responses. The proper solution requires creating these database tables.*