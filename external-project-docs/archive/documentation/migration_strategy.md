# Database Field Migration Strategy

## Overview

This document provides a detailed, actionable strategy for migrating database field names to consistent standards while maintaining system stability and backwards compatibility.

## Migration Principles

1. **Zero Downtime**: All changes must be deployable without service interruption
2. **Backwards Compatible**: Old code must work during transition
3. **Incremental**: Small, testable changes over big-bang migrations
4. **Reversible**: Every change must have a rollback path
5. **Monitored**: Track errors and performance throughout

## Compatibility Layer Design

### Property-Based Compatibility

```python
class CompatibilityMixin:
    """Mixin to provide backwards compatibility for renamed fields"""
    
    @property
    def started_at(self):
        """Compatibility property for old field name"""
        warnings.warn(
            "started_at is deprecated, use created_at instead",
            DeprecationWarning,
            stacklevel=2
        )
        return self.created_at
    
    @started_at.setter
    def started_at(self, value):
        self.created_at = value
```

### Dual-Write Pattern

```python
def save(self, *args, **kwargs):
    """Ensure both old and new fields stay in sync during migration"""
    if hasattr(self, 'started_at') and hasattr(self, 'created_at'):
        self.created_at = self.started_at
    super().save(*args, **kwargs)
```

### Serializer Compatibility

```python
class CompatibilitySerializer(serializers.ModelSerializer):
    # Support both field names during transition
    started_at = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        fields = ['created_at', 'started_at']  # Include both
```

## Phase-by-Phase Migration Plan

### Phase 1: Foundation (Week 1)

#### 1.1 Create Standards Document
```python
# schema_audit/standards.py
FIELD_NAMING_STANDARDS = {
    'timestamps': {
        'creation': 'created_at',
        'modification': 'updated_at',
        'deletion': 'deleted_at',
        'process_start': 'started_at',
        'process_end': 'completed_at'
    },
    'relationships': {
        'user_reference': 'user',  # ForeignKey to User
        'author_reference': 'author',  # When user is ambiguous
        'owner_reference': 'owner'  # For ownership semantics
    },
    'status': {
        'active_state': 'is_active',
        'archived_state': 'is_archived',
        'deleted_state': 'is_deleted',
        'published_state': 'is_published'
    }
}
```

#### 1.2 Create Base Models
```python
# core/base_models.py
class TimestampedModel(models.Model):
    """Base model with standard timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class SoftDeleteModel(TimestampedModel):
    """Base model with soft delete support"""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
```

#### 1.3 Create Validation Tools
```bash
# management/commands/validate_schema.py
python manage.py validate_schema --app agent_orchestra
# Reports: 
# - Model 'Agent' uses non-standard field 'started_at'
# - Model 'Task' missing standard field 'updated_at'
```

### Phase 2: Low-Hanging Fruit (Week 2)

#### 2.1 Fix Zero-Usage Fields
```bash
# Find fields with no usage
python schema_audit/find_unused_fields.py

# Generate migration for unused fields
python manage.py makemigrations --name standardize_unused_fields
```

#### 2.2 Add Missing Standard Fields
```python
# migrations/0001_add_missing_timestamps.py
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='agent',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
```

#### 2.3 Standardize New Development
```python
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-model-standards
        name: Check Django Model Standards
        entry: python schema_audit/check_standards.py
        language: system
        files: models\.py$
```

### Phase 3: Compatibility Implementation (Week 3-4)

#### 3.1 High-Risk Field Migration Plan

**Example: Migrating `started_at` to `created_at`**

Step 1: Add new field
```python
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='taskOrchestration',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
    ]
```

Step 2: Data migration
```python
def migrate_started_to_created(apps, schema_editor):
    TaskOrchestration = apps.get_model('agent_orchestra', 'TaskOrchestration')
    for task in TaskOrchestration.objects.all():
        task.created_at = task.started_at
        task.save()

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(migrate_started_to_created),
    ]
```

Step 3: Add compatibility layer
```python
class TaskOrchestration(CompatibilityMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # Keep old field during transition
    started_at = models.DateTimeField()  
    
    def save(self, *args, **kwargs):
        # Sync fields during transition
        self.started_at = self.created_at
        super().save(*args, **kwargs)
```

Step 4: Update code gradually
```python
# Before
tasks = TaskOrchestration.objects.order_by('-started_at')

# After (with compatibility)
tasks = TaskOrchestration.objects.order_by('-created_at')
```

### Phase 4: Application Migration (Week 5-8)

#### 4.1 Migration Order (Low to High Risk)

1. **Week 5**: Low-risk apps
   - mythology_lab
   - shame  
   - walking_companion
   - ml_models

2. **Week 6**: Medium-risk apps
   - images
   - prompts
   - voice_journals
   - movement

3. **Week 7**: High-risk apps (careful!)
   - memory
   - content
   - learning_intelligence
   - universal_builder

4. **Week 8**: Critical apps (extra caution!)
   - agent_orchestra
   - ai_partner
   - core
   - accounts

#### 4.2 Per-App Migration Checklist

- [ ] Create compatibility mixins
- [ ] Add new standardized fields
- [ ] Migrate data
- [ ] Update model code
- [ ] Update views/viewsets
- [ ] Update serializers
- [ ] Update admin
- [ ] Update API documentation
- [ ] Test thoroughly
- [ ] Monitor for errors
- [ ] Update related apps

### Phase 5: Cleanup (Week 9-10)

#### 5.1 Remove Compatibility Layers
```python
# After monitoring shows no usage of old names
class Migration(migrations.Migration):
    operations = [
        migrations.RemoveField(
            model_name='taskOrchestration',
            name='started_at',
        ),
    ]
```

#### 5.2 Final Validation
```bash
# Run comprehensive validation
python manage.py validate_schema --strict

# Check for any remaining non-standard fields
python schema_audit/final_audit.py
```

## Rollback Procedures

### Level 1: Code Rollback
```bash
# Revert code changes while keeping DB changes
git revert <migration-commit>
# Compatibility layer handles differences
```

### Level 2: Migration Rollback  
```bash
# Rollback specific migration
python manage.py migrate agent_orchestra 0044
```

### Level 3: Emergency Rollback
```sql
-- Emergency SQL to restore old field names
ALTER TABLE agent_orchestra_task 
RENAME COLUMN created_at TO started_at;
```

## Monitoring Plan

### Error Tracking
```python
# middleware/field_monitoring.py
class FieldMigrationMonitor:
    def process_exception(self, request, exception):
        if 'started_at' in str(exception):
            logger.warning(
                f"Legacy field access detected: {exception}",
                extra={'path': request.path}
            )
```

### Performance Monitoring
```sql
-- Check for slow queries after migration
SELECT query, mean_time
FROM pg_stat_statements
WHERE query LIKE '%created_at%'
ORDER BY mean_time DESC;
```

### Usage Analytics
```python
# Log deprecation warnings
import warnings
warnings.filterwarnings('error', category=DeprecationWarning)
```

## Success Metrics

1. **Zero increase in error rate**
2. **No performance degradation**
3. **All tests passing**
4. **No customer-reported issues**
5. **Successful removal of compatibility layers**

## Timeline Summary

- **Week 1**: Setup and preparation
- **Week 2**: Low-risk improvements
- **Week 3-4**: Compatibility layer implementation
- **Week 5-8**: Phased app migration
- **Week 9-10**: Cleanup and finalization
- **Week 11-12**: Buffer for issues

Total duration: 12 weeks with buffer