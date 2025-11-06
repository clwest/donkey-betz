# UUID Field Pattern - Critical Project Standard

**Date:** November 6, 2025 (Session 59)
**Status:** MANDATORY for all future development

---

## 🚨 The Problem

**This platform uses UUID primary keys throughout:**
- `ImageHistory` → UUID primary key
- `VideoHistory` → UUID primary key
- `AudioHistory` → UUID primary key
- `WorkflowHistory` → UUID primary key
- All UnifiedBaseModel descendants → UUID

**Common Mistake:** Using `IntegerField` to reference UUID models

```python
# ❌ WRONG - Will cause 500 errors!
input_image_id = models.IntegerField(
    null=True,
    help_text="ImageHistory ID"
)

# ✅ CORRECT - Use UUIDField!
input_image_id = models.UUIDField(
    null=True,
    help_text="ImageHistory UUID"
)
```

---

## 🔍 Why This Happens

1. Django defaults to IntegerField for foreign keys
2. Developers assume "ID" means integer
3. UUID models need explicit UUIDField references
4. PostgreSQL cannot cast `integer` to `uuid`

---

## ✅ The Solution

### Rule 1: All `*_id` fields referencing UUID models must be UUIDField

```python
# When referencing ImageHistory, VideoHistory, AudioHistory, etc:
input_image_id = models.UUIDField(null=True, blank=True)
source_video_id = models.UUIDField(null=True, blank=True)
related_audio_id = models.UUIDField(null=True, blank=True)
```

### Rule 2: Check before creating migrations

```bash
# Search for potential issues:
grep -rn "_id.*IntegerField" content/models.py core/models.py
```

### Rule 3: If you find an IntegerField bug

**Don't try to alter the field type!** PostgreSQL can't cast `integer → uuid`.

Instead, drop and recreate:

```python
# Custom migration
operations = [
    migrations.RemoveField(
        model_name='mymodel',
        name='problem_field_id',
    ),
    migrations.AddField(
        model_name='mymodel',
        name='problem_field_id',
        field=models.UUIDField(null=True, blank=True),
    ),
]
```

---

## 🐛 Session 59 Bug Fix

**Problem Found:** `WorkflowHistory.input_image_id` was IntegerField

**Impact:**
- Creative Upscale workflow → 500 error
- Any workflow using gallery images → crash
- Frontend showed errors but backend was the culprit

**Fix Applied:**
1. Cleared workflow history (5 records)
2. Created custom migration to drop/recreate field as UUIDField
3. Migration `0006_fix_workflow_history_uuid_field.py` applied successfully

**Files Changed:**
- `content/models.py` (line 2008): IntegerField → UUIDField
- `content/migrations/0006_fix_workflow_history_uuid_field.py`: Custom migration

---

## 📋 Checklist for New Features

When adding ANY field that references images, videos, audio, or workflows:

- [ ] Is this field referencing a UUID model?
- [ ] Did I use `UUIDField` instead of `IntegerField`?
- [ ] Did I test with an actual UUID value?
- [ ] Did I check the migration doesn't try to cast integer→uuid?

---

## 🔗 Related Models Using UUID

**All these use UUID primary keys:**
- ImageHistory
- VideoHistory
- AudioHistory
- WorkflowHistory
- WorkflowFavorite
- Any model inheriting from `UnifiedBaseModel`

**When referencing them, ALWAYS use UUIDField!**

---

## 💡 Quick Reference

```python
# ✅ CORRECT PATTERNS
class MyModel(models.Model):
    # Foreign key with UUID
    image = models.ForeignKey(ImageHistory, null=True, on_delete=models.CASCADE)

    # Direct UUID reference
    image_id = models.UUIDField(null=True, blank=True)
    video_id = models.UUIDField(null=True, blank=True)

# ❌ WRONG PATTERNS
class MyModel(models.Model):
    # DON'T DO THIS!
    image_id = models.IntegerField(null=True)  # Will break!
    video_id = models.PositiveIntegerField(null=True)  # Will break!
```

---

**Last Updated:** Session 59 - November 6, 2025
**Status:** Applied project-wide, documented for future development
