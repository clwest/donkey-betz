# 🧹 SYSTEM PROMPT: Post-Migration Consolidation Cleanup

**Session**: 107+ (After migration fix complete)  
**Priority**: High - Clean up technical debt  
**Estimated Time**: 2-4 hours  
**Prerequisites**: Migration fix completed successfully (Session 106)

## YOUR MISSION

You are a codebase consolidation specialist. The critical migration crisis has been fixed, but temporary compatibility models and incomplete consolidation from Sessions 91-93 need to be properly cleaned up. Complete the consolidation process and remove technical debt while maintaining system stability.

## 🎯 SUCCESS CRITERIA

1. ✅ Remove all migration compatibility models safely
2. ✅ Complete the remaining 24.2% of consolidation (currently 75.8% per CONSOLIDATION_VERIFICATION.md)
3. ✅ Update all 52 files still using legacy imports
4. ✅ Remove temporary workarounds from Session 105
5. ✅ Validate all Phase 2 functionality works with real data
6. ✅ Update documentation to reflect clean state

## 📊 CONSOLIDATION STATUS (From CONSOLIDATION_VERIFICATION.md)

### Current State
- **Migration Progress**: 75.8% complete
- **Legacy Import Files**: 52 files still using old imports  
- **Deprecated Files**: 30 marked (only 1.3% of redundant files)
- **Lines for Removal**: 8,307 marked (target was 40,000+)
- **Duplicate Services**: Still high counts in memory/agent services

### Target State
- **Migration Progress**: 100% complete
- **Legacy Import Files**: 0 files using old imports
- **Deprecated Files**: All redundant files properly marked or removed
- **Service Consolidation**: Complete per CONSOLIDATION_PLAN.md targets

## 🧹 CLEANUP IMPLEMENTATION STEPS

### Step 1: Validate Migration Fix Success

First, confirm the migration fix from Session 106 is stable:

```bash
cd /Users/donkeyking/development/donkey_betz/backend

# Verify all migrations applied
python manage.py showmigrations | grep -c "\[ \]"  # Should be 0

# Test Phase 2 functionality
python manage.py shell -c "
from ai_partner.models_phase2 import WorkflowTemplate, Phase2UserProfile
from ai_partner.services.agent_recommendation_engine import AgentRecommendationEngine
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

# Test database operations
wt = WorkflowTemplate.objects.first()
print(f'WorkflowTemplate test: {wt.name if wt else \"No templates found\"}')

profile, created = Phase2UserProfile.objects.get_or_create(user=user)
print(f'Phase2UserProfile test: Created={created}, ID={profile.id}')

# Test recommendation engine with real data
engine = AgentRecommendationEngine(user_id=user.id)
recs = engine.get_recommendations('test query', limit=2)
print(f'Recommendation engine test: {len(recs)} recommendations')
print('SUCCESS: All Phase 2 components working with real data')
"
```

### Step 2: Remove Migration Compatibility Models

Now that migrations are fixed, remove the temporary compatibility models:

#### 2A: Remove ConversationMemory Model
```python
# In backend/ai_partner/models.py
# REMOVE the entire ConversationMemory class that was added in Session 106
# It should have a comment "MIGRATION COMPATIBILITY MODEL"

# Before removing, check no data exists:
python manage.py shell -c "
from ai_partner.models import ConversationMemory
count = ConversationMemory.objects.count()
print(f'ConversationMemory records: {count}')
if count > 0:
    print('WARNING: Data exists, consider migration to UnifiedMemoryEntry')
else:
    print('Safe to remove - no data exists')
"
```

#### 2B: Remove memory App (if created)
```bash
# Check if memory app was created in Session 106
ls -la backend/memory/ 2>/dev/null && echo "Memory app exists, needs removal"

# Remove from INSTALLED_APPS
# Edit backend/server/settings.py - remove 'memory' if it was added

# After confirming no data loss, remove the directory
rm -rf backend/memory/
```

### Step 3: Complete Legacy Import Migration

Use the CONSOLIDATION_SAFETY_REPORT.md findings to update remaining legacy imports:

```bash
# Find all files with legacy memory imports
grep -r "from.*memory_service import" backend/ --include="*.py" | head -10

# Find files importing deprecated executors
grep -r "sync_executor_with_communication" backend/ --include="*.py"
grep -r "sync_executor_enhanced" backend/ --include="*.py"

# Create comprehensive replacement script
cat > update_legacy_imports.py << 'EOF'
"""
Update legacy imports to use consolidated services.
Based on CONSOLIDATION_PLAN.md mapping.
"""

import os
import re

# Import mappings from CONSOLIDATION_PLAN.md
IMPORT_MAPPINGS = {
    # Memory services
    'from ai_partner.memory_services.enhanced_memory_service import EnhancedMemoryService':
        'from shared_memory.services import UnifiedMemoryService as EnhancedMemoryService',
    'from ai_partner.memory_services.reliable_memory_service import ReliableMemoryService':
        'from shared_memory.services import UnifiedMemoryService as ReliableMemoryService',
    'from ai_partner.memory_services.ukf_memory_service import UKFMemoryService':
        'from shared_memory.services import UnifiedMemoryService as UKFMemoryService',
    'from memory.memory_service import MemoryService':
        'from shared_memory.services import UnifiedMemoryService as MemoryService',
    
    # Agent executors  
    'from agent_orchestra.sync_executor import SyncExecutor':
        'from agent_orchestra.enhanced_sync_executor import EnhancedSyncAgentExecutor as SyncExecutor',
    'from agent_orchestra.fast_sync_executor import FastSyncExecutor':
        'from agent_orchestra.enhanced_sync_executor import EnhancedSyncAgentExecutor as FastSyncExecutor',
    'from agent_orchestra.sync_executor_with_communication import SyncExecutorWithCommunication':
        'from agent_orchestra.enhanced_sync_executor import EnhancedSyncAgentExecutor as SyncExecutorWithCommunication',
        
    # API services
    'from content_pipeline.services.fallback_data_service import FallbackDataService':
        'from core.services.unified_fallback_service import UnifiedFallbackService as FallbackDataService',
}

def update_file_imports(file_path):
    """Update imports in a single file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    for old_import, new_import in IMPORT_MAPPINGS.items():
        if old_import in content:
            content = content.replace(old_import, new_import)
            print(f"Updated {file_path}: {old_import.split('import')[1].strip()}")
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def scan_and_update():
    """Scan for legacy imports and update them"""
    updated_files = []
    
    for root, dirs, files in os.walk('backend'):
        # Skip migrations and __pycache__
        dirs[:] = [d for d in dirs if d not in ['migrations', '__pycache__', '.git']]
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_file_imports(file_path):
                    updated_files.append(file_path)
    
    print(f"\nUpdated {len(updated_files)} files:")
    for file_path in updated_files:
        print(f"  - {file_path}")

if __name__ == "__main__":
    scan_and_update()
EOF

python update_legacy_imports.py
```

### Step 4: Mark and Remove Deprecated Services

Based on CONSOLIDATION_PLAN.md, mark remaining deprecated services:

```bash
# Create deprecation script for services marked in consolidation plan
cat > mark_deprecated_services.py << 'EOF'
"""Mark deprecated services per CONSOLIDATION_PLAN.md"""

import os

# Services to deprecate from CONSOLIDATION_PLAN.md
DEPRECATED_SERVICES = [
    # Memory services
    'backend/ai_partner/memory_services/enhanced_memory_service.py',
    'backend/ai_partner/memory_services/reliable_memory_service.py', 
    'backend/ai_partner/memory_services/ukf_memory_service.py',
    'backend/ai_partner/memory_services/ukf_enhanced_memory_service.py',
    'backend/ai_partner/memory_services/memory_retrieval_service.py',
    'backend/ai_partner/memory_services/optimized_memory_search.py',
    'backend/ai_partner/memory_services/fast_memory_search.py',
    'backend/ai_partner/memory_services/combined_memory_search.py',
    'backend/content/services/content_memory_service.py',
    'backend/core/services/memory_cache_service.py',
    'backend/universal_builder/memory_content_service.py',
    
    # Agent executors
    'backend/agent_orchestra/sync_executor.py',
    'backend/agent_orchestra/fast_sync_executor.py', 
    'backend/agent_orchestra/multi_llm_sync_executor.py',
    'backend/agent_orchestra/progress_enhanced_executor.py',
    'backend/agent_orchestra/sync_executor_with_communication.py',
    'backend/agent_orchestra/business_builder_executor.py',
    'backend/agent_orchestra/self_development_executor.py',
    'backend/agent_orchestra/mock_tool_executor.py',
    'backend/agent_orchestra/channel_aware_executor.py',
]

DEPRECATION_HEADER = '''"""
⚠️  DEPRECATED - DO NOT USE ⚠️ 

This module has been deprecated and will be removed in v2.0.
Use the consolidated services instead:

Memory Services → shared_memory.services.UnifiedMemoryService  
Agent Executors → agent_orchestra.enhanced_sync_executor.EnhancedSyncAgentExecutor

This file exists only for backward compatibility during the transition period.
"""

import warnings
warnings.warn(
    f"The module {__name__} is deprecated. Use consolidated services instead.",
    DeprecationWarning,
    stacklevel=2
)

'''

def add_deprecation_warning(file_path):
    """Add deprecation warning to a file"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
        
    with open(file_path, 'r') as f:
        content = f.read()
    
    if 'DEPRECATED - DO NOT USE' in content:
        print(f"Already deprecated: {file_path}")
        return False
    
    # Insert deprecation header after shebang/encoding but before other imports
    lines = content.split('\n')
    insert_pos = 0
    
    for i, line in enumerate(lines):
        if line.startswith('#!') or 'coding:' in line or 'encoding:' in line:
            insert_pos = i + 1
        elif line.strip() == '':
            continue
        else:
            break
    
    lines.insert(insert_pos, DEPRECATION_HEADER)
    
    with open(file_path, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"Marked deprecated: {file_path}")
    return True

# Mark all deprecated services
for service_path in DEPRECATED_SERVICES:
    add_deprecation_warning(service_path)
EOF

python mark_deprecated_services.py
```

### Step 5: Clean Up Session 105 Workarounds

Remove temporary workarounds that were added in Session 105:

#### 5A: Clean up views_phase2.py
```python
# Edit backend/ai_partner/views_phase2.py
# Remove get_test_recommendations() function completely
# Ensure all endpoints use real services, not mock data

# Before:
@action(detail=False, methods=['post'])
def recommend_agents(self, request):
    # Mock data for now until migration fixed
    recommendations = get_test_recommendations()  # REMOVE THIS
    
# After:
@action(detail=False, methods=['post'])
def recommend_agents(self, request):
    engine = AgentRecommendationEngine(user_id=request.user.id)
    recommendations = engine.get_recommendations(
        query=request.data.get('query'),
        context=request.data.get('context', {}),
        limit=request.data.get('limit', 5)
    )
```

#### 5B: Restore learning_intelligence Integration
```python
# Uncomment all learning_intelligence imports that were commented in Session 105:
# - backend/api_services/learning_api_service.py
# - backend/ai_partner/services/learning_enhanced_ai.py  
# - backend/agent_orchestra/services/learning_enhanced_orchestrator.py
# - backend/mythology_lab/hooks/enhanced_conversation_memory.py

# Example restoration:
# FROM:
# # from learning_intelligence.models import SymbolicMemoryAnchor  # Commented in Session 105
# TO:
from learning_intelligence.models import SymbolicMemoryAnchor
```

### Step 6: Validate Complete System

```bash
# Run comprehensive system test
python manage.py test --keepdb --parallel 4 ai_partner agent_orchestra shared_memory

# Test Phase 2 end-to-end functionality
python -c "
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model
from ai_partner.services.agent_recommendation_engine import AgentRecommendationEngine
from ai_partner.services.user_context_service import UserContextService
from ai_partner.services.workflow_orchestrator import WorkflowOrchestrator

User = get_user_model()
user = User.objects.first()

print('=== PHASE 2 END-TO-END TEST ===')

# Test recommendation engine
engine = AgentRecommendationEngine(user_id=user.id)
recs = engine.get_recommendations('I need help with marketing strategy', limit=3)
print(f'✅ AgentRecommendationEngine: {len(recs)} recommendations')

# Test user context  
context_service = UserContextService(user_id=user.id)
patterns = context_service.get_user_patterns()
print(f'✅ UserContextService: {len(patterns)} patterns')

# Test workflow orchestrator
orchestrator = WorkflowOrchestrator(user_id=user.id)
templates = orchestrator.get_workflow_templates()
print(f'✅ WorkflowOrchestrator: {len(templates)} templates')

print('✅ ALL PHASE 2 SERVICES FUNCTIONAL WITH REAL DATA')
"

# Performance test with real data
python -c "
import time, asyncio, sys, os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from ai_partner.personal_ai_services import PersonalAIService
from django.contrib.auth import get_user_model

async def performance_test():
    User = get_user_model()
    user = User.objects.first()
    ai_service = PersonalAIService(user)
    
    start_time = time.time()
    
    # Test agent deployment with real data
    result = await ai_service.deploy_agent_magic(
        user=user,
        agent_name='Business Agent',
        original_message='Create a marketing plan for a new product launch'
    )
    
    end_time = time.time()
    print(f'⏱️  Agent deployment time: {end_time - start_time:.2f}s')
    print(f'📊 Result type: {type(result)}')
    print(f'🎯 Using real data: {\"orchestration_id\" in result}')
    
asyncio.run(performance_test())
"
```

## 📊 CONSOLIDATION COMPLETION METRICS

Track progress toward full consolidation:

```bash
# Count remaining deprecated services
find backend/ -name "*.py" -exec grep -l "DEPRECATED.*DO NOT USE" {} \; | wc -l

# Count files still using legacy imports  
grep -r "memory_services\|sync_executor\|fallback_data_service" backend/ --include="*.py" | wc -l

# Measure total lines of code reduction
find backend/ -name "*.py" -not -path "*/migrations/*" -exec wc -l {} \; | awk '{sum += $1} END {print "Total lines:", sum}'

# Services consolidation check
find backend/ -path "*/services/*" -name "*.py" | wc -l
```

## 🧪 FINAL VALIDATION CHECKLIST

Before completing consolidation cleanup:

1. ✅ **All migrations applied**: `python manage.py showmigrations` shows no unapplied
2. ✅ **No compatibility models**: ConversationMemory and memory.MemoryEntry removed
3. ✅ **Legacy imports updated**: grep finds 0 deprecated import patterns  
4. ✅ **Services marked deprecated**: All deprecated services have warnings
5. ✅ **Session 105 workarounds removed**: No mock data or commented imports
6. ✅ **Phase 2 real data functional**: All APIs return database-backed data
7. ✅ **Performance maintained**: Response times within acceptable ranges
8. ✅ **Tests passing**: Full test suite passes with real data

## 📈 SUCCESS METRICS

**Target State Achievement:**
- Migration Progress: 100% (was 75.8%)
- Legacy Import Files: 0 (was 52)  
- Service Consolidation: Per CONSOLIDATION_PLAN.md ratios achieved
- Technical Debt: Reduced by removal of compatibility layers
- System Performance: Maintained or improved with consolidated services

## 📤 HANDOFF TO NEXT SESSION

Once consolidation cleanup is complete:

1. **Update CLAUDE.md** with new consolidation status
2. **Document final architecture** in consolidated state
3. **Ready for Phase 3 integration** with clean codebase
4. **Performance benchmarks** established for future reference

---

**Remember**: This cleanup enables future development on a solid foundation. Take time to do it properly - technical debt eliminated now prevents problems later.