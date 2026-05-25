# Handoff 04: Database Model Consolidation

**Priority:** MEDIUM-HIGH
**Estimated Sessions:** 2
**Dependencies:** Handoff 03 (Sci-Fi Rationalization) helps reduce model count

---

## Problem Statement

The platform has **161 model classes** across **16,670 lines** in three files:

1. `content/models.py` - 108,100 bytes
2. `agents/models.py` - 55,689 bytes
3. `core/models_unified_system.py` - Large file with Phase 1-6 + Sci-Fi models

**Issues:**
- Probable orphaned/unused models from rapid development
- Unclear which models are actively used
- Duplicate or near-duplicate models
- SQLite with pgvector fallbacks (not fully PostgreSQL)
- No clear model organization strategy
- Heavy migration history

---

## Current State Analysis

### Model Distribution (Approximate)

```
content/models.py (~40 models)
├── Document types (DocumentType, ContentStatus, ContentSource)
├── Content models (Document, Embedding, KnowledgeBase)
├── Image models (ImageHistory, ImageGeneration)
├── Video models (VideoHistory, VideoGeneration)
├── Audio models (AudioHistory)
├── Project models (Project, ProjectAsset)
├── Template models
└── Analytics models

agents/models.py (~30 models)
├── Agent models (Agent, AgentExecution, AgentLog)
├── Collaboration models
├── Learning models
├── Wiring models
└── Registry models

core/models_unified_system.py (~90 models)
├── Phase 1: SpiderData, Opportunity
├── Phase 2: Revenue, Payment
├── Phase 3: TeamCollaboration
├── Phase 4: Distribution
├── Phase 5: LearningLoop
├── Phase 6: ProactiveAlert
├── Sci-Fi: Memory, Mood, Evolution, Dreams, Prophecies, etc.
└── A/B Testing, Goals, etc.
```

---

## Solution: Audit, Consolidate, Organize

### Target State

```
core/models/
├── __init__.py              # Exports all models
├── base.py                  # UnifiedBaseModel, common mixins
├── content/
│   ├── __init__.py
│   ├── documents.py         # Document, Embedding, KnowledgeBase
│   ├── media.py             # ImageHistory, VideoHistory, AudioHistory
│   └── projects.py          # Project, ProjectAsset
├── agents/
│   ├── __init__.py
│   ├── agents.py            # Agent, AgentExecution, AgentStats
│   └── collaboration.py     # TeamCollaboration, HiveMind
├── intelligence/
│   ├── __init__.py
│   ├── spiders.py           # SpiderData, SpiderExecution
│   ├── opportunities.py     # Opportunity, OpportunityScore
│   └── learning.py          # LearningOutcome, FeedbackLoop
├── revenue/
│   ├── __init__.py
│   ├── tracking.py          # Revenue, Payment, RevenueGoal
│   └── distribution.py      # Distribution, Platform
├── platform/
│   ├── __init__.py
│   ├── memory.py            # Memory (simplified)
│   ├── alerts.py            # ProactiveAlert
│   └── testing.py           # ABTest, ABTestVariant
└── deprecated/
    ├── __init__.py
    └── scifi_deprecated.py  # AgentDream, Prophecy, TimeCapsule

# Old files become compatibility shims
content/models.py            # Re-exports from core.models.content
agents/models.py             # Re-exports from core.models.agents
core/models_unified_system.py # Re-exports all
```

---

## Implementation Plan

### Session 1: Audit and Identify Cleanup Targets

**Goal:** Find unused models, duplicates, and organize migration plan

**Tasks:**

1. **Create model audit script**
   ```python
   # scripts/audit_models.py
   import os
   import re
   import ast
   from collections import defaultdict

   def find_model_classes(filepath):
       """Extract model class names from a file."""
       with open(filepath) as f:
           content = f.read()

       # Find class definitions that inherit from models.Model or similar
       pattern = r'class\s+(\w+)\s*\([^)]*(?:Model|UnifiedBaseModel)[^)]*\)'
       return re.findall(pattern, content)

   def find_model_usage(model_name, directory='.'):
       """Find where a model is used in the codebase."""
       usages = []
       for root, dirs, files in os.walk(directory):
           # Skip migrations, cache, venv
           dirs[:] = [d for d in dirs if d not in ['migrations', '__pycache__', '.venv', 'venv', 'node_modules']]

           for f in files:
               if f.endswith('.py'):
                   filepath = os.path.join(root, f)
                   with open(filepath) as file:
                       content = file.read()
                       if model_name in content:
                           # Count occurrences
                           count = content.count(model_name)
                           usages.append((filepath, count))
       return usages

   # Find all models
   model_files = [
       'content/models.py',
       'agents/models.py',
       'core/models_unified_system.py'
   ]

   all_models = {}
   for f in model_files:
       if os.path.exists(f):
           models = find_model_classes(f)
           all_models[f] = models
           print(f"\n{f}: {len(models)} models")
           for m in models:
               print(f"  - {m}")

   # Check usage of each model
   print("\n\n=== MODEL USAGE ANALYSIS ===\n")
   for file, models in all_models.items():
       for model in models:
           usages = find_model_usage(model)
           # Exclude the definition file
           external_usages = [(f, c) for f, c in usages if f != file]
           total_external = sum(c for f, c in external_usages)

           status = "UNUSED" if total_external == 0 else f"Used in {len(external_usages)} files ({total_external} refs)"
           print(f"{model}: {status}")

           if total_external == 0:
               print(f"  ⚠️  CANDIDATE FOR REMOVAL")
   ```

2. **Run audit and categorize results**
   ```bash
   python scripts/audit_models.py > model_audit_results.txt
   ```

3. **Check database for empty tables**
   ```python
   # Run in Django shell
   from django.apps import apps
   from django.db import connection

   # Get all models
   all_models = apps.get_models()

   print("=== TABLE RECORD COUNTS ===")
   empty_tables = []
   for model in all_models:
       try:
           count = model.objects.count()
           table_name = model._meta.db_table
           print(f"{table_name}: {count} records")
           if count == 0:
               empty_tables.append(table_name)
       except Exception as e:
           print(f"{model.__name__}: ERROR - {e}")

   print(f"\n\n=== EMPTY TABLES ({len(empty_tables)}) ===")
   for t in empty_tables:
       print(f"  - {t}")
   ```

4. **Identify duplicate models**
   Look for:
   - Models with same/similar fields
   - Models with same purpose in different files
   - Models that could be merged

5. **Create consolidation plan document**
   ```markdown
   # Model Consolidation Plan

   ## Models to KEEP (actively used)
   - ImageHistory: 1,234 records, used in 15 files
   - VideoHistory: 567 records, used in 12 files
   - ...

   ## Models to MERGE
   - AgentExecution + AgentLog → AgentExecution (add log fields)
   - ...

   ## Models to DEPRECATE (unused, 0 records)
   - OldModel1
   - OldModel2
   - ...

   ## Models to DEPRECATE (Sci-Fi rationalization)
   - AgentDream
   - Prophecy
   - TimeCapsule
   - ...
   ```

**Deliverables:**
- [ ] Model audit script created
- [ ] Usage analysis for all 161 models
- [ ] Empty table report
- [ ] Duplicate model identification
- [ ] Consolidation plan document

---

### Session 2: Reorganize and Migrate

**Goal:** Move models to organized structure, create compatibility shims

**Tasks:**

1. **Create new model directory structure**
   ```bash
   mkdir -p core/models/{content,agents,intelligence,revenue,platform,deprecated}
   touch core/models/__init__.py
   touch core/models/base.py
   touch core/models/content/__init__.py
   touch core/models/agents/__init__.py
   touch core/models/intelligence/__init__.py
   touch core/models/revenue/__init__.py
   touch core/models/platform/__init__.py
   touch core/models/deprecated/__init__.py
   ```

2. **Create base model module**
   ```python
   # core/models/base.py
   """
   Base models and mixins for the unified platform.
   """
   from django.db import models
   from django.contrib.auth import get_user_model
   from django.utils import timezone
   import uuid

   User = get_user_model()


   class UnifiedBaseModel(models.Model):
       """
       Base model for all platform models.

       Provides:
       - UUID primary key
       - Created/updated timestamps
       - Soft delete capability
       - Common utility methods
       """
       id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
       created_at = models.DateTimeField(auto_now_add=True)
       updated_at = models.DateTimeField(auto_now=True)
       is_deleted = models.BooleanField(default=False)

       class Meta:
           abstract = True
           ordering = ['-created_at']

       def soft_delete(self):
           self.is_deleted = True
           self.save(update_fields=['is_deleted', 'updated_at'])

       def restore(self):
           self.is_deleted = False
           self.save(update_fields=['is_deleted', 'updated_at'])


   class TimestampMixin(models.Model):
       """Simple timestamp mixin for models that don't need full base."""
       created_at = models.DateTimeField(auto_now_add=True)
       updated_at = models.DateTimeField(auto_now=True)

       class Meta:
           abstract = True


   class UserOwnedMixin(models.Model):
       """Mixin for models owned by a user."""
       user = models.ForeignKey(
           User,
           on_delete=models.CASCADE,
           related_name='%(class)s_set'
       )

       class Meta:
           abstract = True
   ```

3. **Migrate content models**
   ```python
   # core/models/content/media.py
   """
   Media generation history models.
   """
   from django.db import models
   from core.models.base import UnifiedBaseModel, UserOwnedMixin


   class ImageHistory(UnifiedBaseModel, UserOwnedMixin):
       """History of generated images."""
       prompt = models.TextField()
       enhanced_prompt = models.TextField(blank=True)
       image_url = models.URLField(max_length=500)
       thumbnail_url = models.URLField(max_length=500, blank=True)
       provider = models.CharField(max_length=50)
       model = models.CharField(max_length=50)
       style = models.CharField(max_length=50, blank=True)
       size = models.CharField(max_length=20)
       generation_time_ms = models.IntegerField(default=0)
       cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
       metadata = models.JSONField(default=dict, blank=True)

       class Meta:
           db_table = 'content_imagehistory'  # Keep original table name
           verbose_name_plural = 'Image histories'


   class VideoHistory(UnifiedBaseModel, UserOwnedMixin):
       """History of generated videos."""
       prompt = models.TextField()
       video_url = models.URLField(max_length=500, blank=True)
       thumbnail_url = models.URLField(max_length=500, blank=True)
       provider = models.CharField(max_length=50)
       model = models.CharField(max_length=50)
       duration = models.IntegerField(default=0)
       status = models.CharField(max_length=20, default='pending')
       task_id = models.CharField(max_length=100, blank=True)
       generation_time_ms = models.IntegerField(default=0)
       cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
       metadata = models.JSONField(default=dict, blank=True)

       class Meta:
           db_table = 'content_videohistory'
           verbose_name_plural = 'Video histories'


   class AudioHistory(UnifiedBaseModel, UserOwnedMixin):
       """History of generated audio."""
       text = models.TextField()
       audio_url = models.URLField(max_length=500, blank=True)
       provider = models.CharField(max_length=50)
       voice = models.CharField(max_length=50)
       model = models.CharField(max_length=50)
       duration_seconds = models.FloatField(default=0)
       generation_time_ms = models.IntegerField(default=0)
       cost = models.DecimalField(max_digits=10, decimal_places=4, default=0)
       metadata = models.JSONField(default=dict, blank=True)

       class Meta:
           db_table = 'content_audiohistory'
           verbose_name_plural = 'Audio histories'
   ```

4. **Create compatibility shim for content/models.py**
   ```python
   # content/models.py (UPDATED - compatibility shim)
   """
   COMPATIBILITY SHIM

   Models have been moved to core.models.content
   This file re-exports them for backward compatibility.

   New code should import from:
       from core.models.content import ImageHistory, VideoHistory, AudioHistory
       from core.models.content import Document, Embedding, KnowledgeBase
       from core.models.content import Project, ProjectAsset

   This shim will be removed in a future version.
   """
   import warnings

   # Re-export all models from new location
   from core.models.content.media import ImageHistory, VideoHistory, AudioHistory
   from core.models.content.documents import Document, Embedding, KnowledgeBase
   from core.models.content.projects import Project, ProjectAsset

   # ... other re-exports

   def __getattr__(name):
       """Emit deprecation warning for direct attribute access."""
       warnings.warn(
           f"Importing {name} from 'content.models' is deprecated. "
           f"Use 'from core.models.content import {name}' instead.",
           DeprecationWarning,
           stacklevel=2
       )
       # Try to find in submodules
       from core.models import content as content_models
       return getattr(content_models, name)
   ```

5. **Create database migration (no-op for table names)**
   ```python
   # core/migrations/XXXX_reorganize_models.py
   """
   This migration documents the model reorganization.
   No actual database changes needed because we keep db_table names.
   """
   from django.db import migrations

   class Migration(migrations.Migration):
       dependencies = [
           ('core', 'previous_migration'),
       ]

       operations = [
           # Document the reorganization
           migrations.RunSQL(
               sql="-- Models reorganized to core.models.* structure",
               reverse_sql="-- Reverse: N/A"
           ),
       ]
   ```

6. **Update imports across codebase**
   ```bash
   # Find all imports from old locations
   grep -r "from content.models import" --include="*.py" | grep -v migrations | grep -v __pycache__
   grep -r "from agents.models import" --include="*.py" | grep -v migrations | grep -v __pycache__

   # Update each file to use new imports
   # (or rely on compatibility shim for now)
   ```

7. **Move deprecated models**
   ```python
   # core/models/deprecated/scifi_deprecated.py
   """
   DEPRECATED MODELS

   These models are deprecated and will be removed in a future version.
   They are kept for data preservation only.
   Do not use these models in new code.
   """
   from django.db import models
   from core.models.base import UnifiedBaseModel
   import warnings


   class DeprecatedModelMixin:
       """Mixin that warns on any usage."""

       def save(self, *args, **kwargs):
           warnings.warn(
               f"{self.__class__.__name__} is deprecated.",
               DeprecationWarning
           )
           super().save(*args, **kwargs)


   class AgentDream(DeprecatedModelMixin, UnifiedBaseModel):
       """DEPRECATED: Agent Dreams feature."""
       agent_name = models.CharField(max_length=100)
       dream_content = models.TextField()
       dream_type = models.CharField(max_length=50)

       class Meta:
           db_table = 'core_agentdream'


   class Prophecy(DeprecatedModelMixin, UnifiedBaseModel):
       """DEPRECATED: Prophecy/Predictions feature."""
       agent_name = models.CharField(max_length=100)
       prediction = models.TextField()
       confidence = models.FloatField()

       class Meta:
           db_table = 'core_prophecy'


   class TimeCapsule(DeprecatedModelMixin, UnifiedBaseModel):
       """DEPRECATED: Time Capsules feature."""
       agent_name = models.CharField(max_length=100)
       message = models.TextField()
       open_at = models.DateTimeField()

       class Meta:
           db_table = 'core_timecapsule'
   ```

**Deliverables:**
- [ ] New model directory structure created
- [ ] Base models and mixins in core/models/base.py
- [ ] Content models migrated to core/models/content/
- [ ] Agent models migrated to core/models/agents/
- [ ] Intelligence models migrated to core/models/intelligence/
- [ ] Revenue models migrated to core/models/revenue/
- [ ] Platform models migrated to core/models/platform/
- [ ] Deprecated models isolated in core/models/deprecated/
- [ ] Compatibility shims in place
- [ ] All imports working (either new or via shim)

---

## Validation Checklist

After all sessions, verify:

- [ ] Django migrations run successfully
- [ ] All existing data preserved
- [ ] Views still work (use compatibility shims)
- [ ] Admin still works
- [ ] No import errors
- [ ] Deprecated model warnings appear in logs

---

## Files to Modify

1. `core/models/__init__.py` - New model exports
2. `core/models/base.py` - New base models
3. `core/models/content/*.py` - Migrated content models
4. `core/models/agents/*.py` - Migrated agent models
5. `content/models.py` - Compatibility shim
6. `agents/models.py` - Compatibility shim
7. `core/models_unified_system.py` - Compatibility shim

---

## Risk Mitigation

1. **Keep db_table names** - No actual table changes needed
2. **Compatibility shims** - Old imports continue working
3. **Deprecation warnings** - Track usage of old imports
4. **Test migrations** - Run on copy of database first

---

## Success Metrics

| Metric | Before | Target |
|--------|--------|--------|
| Model classes | 161 | < 100 (after removing unused) |
| Model files | 3 large files | 15+ organized files |
| Largest model file | 108,100 bytes | < 20,000 bytes |
| Orphaned models | Unknown | 0 |
| Deprecated models | Mixed in | Isolated in deprecated/ |

---

## Commands for Next Claude Session

```bash
# Start here
cd /Users/donkeyking/development/unified-donkey-betz

# Read this handoff
cat docs/handoffs/HANDOFF_04_DATABASE_CONSOLIDATION.md

# Check current model counts
grep "class.*Model" content/models.py | wc -l
grep "class.*Model" agents/models.py | wc -l
grep "class.*Model" core/models_unified_system.py | wc -l

# Begin Session 1 tasks
```
