# 🔧 SYSTEM PROMPT: Critical Database Migration Fix

**Session**: 106  
**Priority**: CRITICAL - Must complete before any other work  
**Estimated Time**: 2-3 hours  
**Prerequisites**: Read SESSION_106_CRITICAL_HANDOFF.md first  

## YOUR MISSION

You are a Django migration specialist tasked with fixing a critical database migration crisis that is blocking all development. The system underwent memory model consolidation in Sessions 91-93, but migration compatibility was not properly maintained. **Fix this immediately.**

## 🚨 CRITICAL CONTEXT

### The Problem
- **Migration 0029_phase2_models cannot be applied** due to missing model dependencies
- **ConversationMemory model**: Referenced in migrations but never created
- **MemoryEntry model**: Consolidated to UnifiedMemoryEntry but migrations still reference old name
- **learning_intelligence app**: Disabled due to circular dependencies
- **All Phase 2/3 features running on mock data only** - no database persistence

### Root Cause
Sessions 91-93 successfully consolidated 21 memory services into UnifiedMemoryEntry (75.8% complete per CONSOLIDATION_VERIFICATION.md) but failed to create migration compatibility layer. Django migrations reference models that were removed during consolidation.

## 🎯 SUCCESS CRITERIA

1. ✅ All Django migrations apply without KeyError exceptions
2. ✅ Phase 2 tables exist in database (WorkflowTemplate, Phase2UserProfile, etc.)
3. ✅ learning_intelligence app re-enabled and functional
4. ✅ Server starts without import errors
5. ✅ Phase 2 APIs return real database data (not mock data)
6. ✅ Data persists across server restarts

## 📋 STEP-BY-STEP IMPLEMENTATION

### Step 1: Analyze Current Migration State
```bash
cd /Users/donkeyking/development/donkey_betz/backend

# Check current migration status
python manage.py showmigrations ai_partner
python manage.py showmigrations learning_intelligence

# Check database state
python manage.py dbshell
\dt ai_partner*;
\dt learning_intelligence*;
\q
```

### Step 2: Create Migration Compatibility Layer

#### 2A: Create Missing memory App Models
```bash
# Check if memory app exists
ls -la backend/memory/ 2>/dev/null || echo "Memory app missing"

# If missing, create it
mkdir -p backend/memory/migrations
touch backend/memory/__init__.py
touch backend/memory/migrations/__init__.py
```

Create `backend/memory/models.py`:
```python
"""
MIGRATION COMPATIBILITY MODELS

These models exist solely to satisfy Django migration dependencies
from the pre-consolidation era. DO NOT USE THESE MODELS DIRECTLY.

All memory functionality has been consolidated into:
shared_memory.models.UnifiedMemoryEntry

This file should be removed once all legacy migrations are resolved.
"""

from django.db import models
from django.contrib.auth import get_user_model
from shared_memory.models import UnifiedMemoryEntry

User = get_user_model()

class MemoryEntry(UnifiedMemoryEntry):
    """
    Migration compatibility proxy for old memory.MemoryEntry model.
    All functionality moved to UnifiedMemoryEntry.
    """
    class Meta:
        proxy = True
        app_label = 'memory'
        
    def __str__(self):
        return f"MemoryEntry(DEPRECATED) -> {super().__str__()}"
```

#### 2B: Create Missing ConversationMemory Model

Add to `backend/ai_partner/models.py` (before the last class):

```python
import uuid
from django.utils import timezone

class ConversationMemory(models.Model):
    """
    MIGRATION COMPATIBILITY MODEL
    
    This model was referenced in multiple ai_partner migrations but never
    actually created. It was intended to be replaced by UnifiedMemoryEntry
    during the consolidation in Sessions 91-93.
    
    This model exists purely for migration compatibility. 
    DO NOT USE - use UnifiedMemoryEntry instead.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversation_memories')
    transcript = models.TextField(default="", blank=True)
    session_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Fields referenced in migration 0004
    memory_strength = models.FloatField(default=1.0)
    access_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Fields referenced in migration 0005
    segments = models.JSONField(default=list, blank=True)
    
    # Fields referenced in migration 0008
    embedding = models.JSONField(null=True, blank=True)
    
    # Fields referenced in migration 0012
    context_data = models.JSONField(default=dict, blank=True)
    
    # Fields referenced in migration 0013
    summary = models.TextField(blank=True, default="")
    
    # Fields referenced in migration 0016
    importance_score = models.FloatField(default=0.5)
    
    # Fields referenced in migration 0017
    tags = models.JSONField(default=list, blank=True)
    
    # Fields referenced in migration 0018
    related_memories = models.ManyToManyField('self', blank=True, symmetrical=False)
    
    # Fields referenced in migration 0021
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        app_label = 'ai_partner'
        db_table = 'ai_partner_conversationmemory'
        ordering = ['-session_date']
        indexes = [
            models.Index(fields=['user', '-session_date']),
            models.Index(fields=['importance_score']),
        ]
    
    def __str__(self):
        return f"ConversationMemory(DEPRECATED - {self.user.username} - {self.session_date})"
```

#### 2C: Fix learning_intelligence Model References

Edit `backend/learning_intelligence/models.py` (add at the end):

```python
# MIGRATION COMPATIBILITY ALIASES
# These aliases exist to satisfy migration dependencies

# Alias for old lowercase reference
MemoryEntry = LearningMemoryEntry

# Ensure proper app labeling
class Meta:
    app_label = 'learning_intelligence'
```

### Step 3: Create Compatibility Migration

```bash
# Create new migration for ConversationMemory
python manage.py makemigrations ai_partner --name add_conversation_memory_compatibility

# If memory app needs to be added to INSTALLED_APPS temporarily:
```

Edit `backend/server/settings.py` if needed:
```python
# Add memory to INSTALLED_APPS temporarily for migration
INSTALLED_APPS = [
    # ... existing apps ...
    'memory',  # Temporary for migration compatibility
]
```

### Step 4: Apply Migrations in Correct Order

```bash
# Try to apply migrations step by step
python manage.py migrate memory --fake-initial 2>/dev/null || echo "No memory migrations needed"

# Apply the new compatibility migration
python manage.py migrate ai_partner

# Now try the blocked Phase 2 migration
python manage.py migrate ai_partner 0029

# Verify all migrations applied
python manage.py showmigrations | grep -v "\[X\]"
```

### Step 5: Re-enable learning_intelligence

Edit `backend/server/settings.py` line 340:
```python
# Re-enable learning_intelligence
'learning_intelligence',  # Uncomment this line
```

### Step 6: Restore Commented Code

#### 6A: Restore SystemInsight.learning_anchor field
In `backend/ai_partner/models.py` lines 751-759, uncomment:
```python
# Restore this field
learning_anchor = models.ForeignKey(
    'learning_intelligence.SymbolicMemoryAnchor',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='system_insights',
    help_text="Associated learning anchor if this insight led to learning"
)
```

#### 6B: Restore Service Imports
Restore imports in these files (replace commented sections):
- `backend/api_services/learning_api_service.py`
- `backend/ai_partner/services/learning_enhanced_ai.py`
- `backend/agent_orchestra/services/learning_enhanced_orchestrator.py`
- `backend/mythology_lab/hooks/enhanced_conversation_memory.py`

### Step 7: Update Phase 2 APIs to Use Real Data

Edit `backend/ai_partner/views_phase2.py` - Remove mock data function and enable real recommendations:

```python
# REMOVE this mock function (lines added in Session 105)
def get_test_recommendations():
    # ... remove this entire function

# ENABLE real data in RecommendationViewSet methods
@action(detail=False, methods=['post'])
def recommend_agents(self, request):
    # Remove mock data conditional
    # Use real AgentRecommendationEngine instead
    engine = AgentRecommendationEngine(user_id=request.user.id)
    recommendations = engine.get_recommendations(
        query=request.data.get('query'),
        context=request.data.get('context', {}),
        limit=request.data.get('limit', 5)
    )
    # ... real implementation
```

## 🧪 TESTING CHECKLIST

After each step, verify:

```bash
# 1. Server starts without errors
python manage.py runserver &
sleep 3
curl http://localhost:8000/api/health/ || echo "Server not responding"
pkill -f runserver

# 2. All migrations applied
python manage.py showmigrations | grep -c "\[ \]" | xargs -I {} echo "Unapplied migrations: {}"

# 3. Phase 2 tables exist
python manage.py shell -c "
from ai_partner.models_phase2 import WorkflowTemplate, Phase2UserProfile
print('WorkflowTemplate table exists:', WorkflowTemplate._meta.db_table)
print('Phase2UserProfile table exists:', Phase2UserProfile._meta.db_table)
try:
    wt_count = WorkflowTemplate.objects.count()
    profile_count = Phase2UserProfile.objects.count()
    print(f'WorkflowTemplate count: {wt_count}')
    print(f'Phase2UserProfile count: {profile_count}')
except Exception as e:
    print(f'ERROR accessing tables: {e}')
"

# 4. Phase 2 APIs return real data
python -c "
import requests
import json
# Test requires running server
response = requests.post('http://localhost:8000/api/ai-partner/recommendations/recommend_agents/', 
    json={'query': 'help with marketing'},
    headers={'Authorization': 'Bearer YOUR_TOKEN'})
data = response.json()
print('API Response:', json.dumps(data, indent=2)[:500])
print('Using real data:', 'test_data' not in str(data))
"
```

## ⚠️ TROUBLESHOOTING

### If migrations still fail:
```bash
# Check specific error
python manage.py migrate ai_partner 0029 --verbosity=2

# If ConversationMemory table already exists but Django doesn't know:
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_name LIKE %s', ['ai_partner_conversationmemory'])
print('ConversationMemory table exists:', cursor.fetchall())
"

# Fake individual migrations if needed
python manage.py migrate ai_partner 0004 --fake
python manage.py migrate ai_partner 0005 --fake
# ... continue as needed
```

### If learning_intelligence issues persist:
```bash
# Check model loading
python manage.py shell -c "
import learning_intelligence.models
print('Models loaded successfully')
print('MemoryEntry alias:', hasattr(learning_intelligence.models, 'MemoryEntry'))
"
```

## 🎯 COMPLETION VALIDATION

**Your session is complete when ALL of these pass:**

1. ✅ `python manage.py migrate` runs without errors
2. ✅ `python manage.py runserver` starts without import errors  
3. ✅ Phase 2 tables queryable: `WorkflowTemplate.objects.count()` works
4. ✅ learning_intelligence enabled in settings.py
5. ✅ Phase 2 API returns real data (not mock responses)
6. ✅ No commented imports in service files
7. ✅ SystemInsight.learning_anchor field uncommented and working

## 📤 HANDOFF TO NEXT SESSION

Once complete:
1. **Update SESSION_106_CRITICAL_HANDOFF.md** with results
2. **Document any deviations** from this plan
3. **Test Phase 2 functionality** end-to-end
4. **Prepare for Phase 3 integration** (real data connection)

---

**Remember**: This is the highest priority task. No other development should proceed until the migration system is fully functional and Phase 2/3 features can persist data to the database.