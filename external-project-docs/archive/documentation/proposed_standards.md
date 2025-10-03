# Django Model Field Naming Standards

## Purpose

This document defines the official field naming standards for all Django models in the move_that_ass project. Following these standards will:

- Reduce development errors
- Improve code readability
- Simplify database queries
- Enable better tooling support

## Field Naming Standards

### 1. Timestamp Fields

Use these exact names for timestamp fields:

| Purpose | Field Name | Type | Notes |
|---------|------------|------|-------|
| Record creation | `created_at` | DateTimeField | auto_now_add=True |
| Last modification | `updated_at` | DateTimeField | auto_now=True |
| Soft deletion | `deleted_at` | DateTimeField | null=True, blank=True |
| Process/event start | `started_at` | DateTimeField | For processes with duration |
| Process/event end | `completed_at` | DateTimeField | Pairs with started_at |
| Scheduling | `scheduled_at` | DateTimeField | For future events |
| Publication | `published_at` | DateTimeField | For content/posts |
| Expiration | `expires_at` | DateTimeField | For time-limited items |

**❌ Avoid these patterns:**
- `created`, `date_created`, `creation_date`, `created_date`
- `modified`, `last_modified`, `date_modified`
- `start_time`, `start_date`, `begins_at`
- `end_time`, `end_date`, `ends_at`

### 2. User References

| Purpose | Field Name | Type | Notes |
|---------|------------|------|-------|
| Primary user | `user` | ForeignKey | to=settings.AUTH_USER_MODEL |
| Content creator | `author` | ForeignKey | When 'user' is ambiguous |
| Resource owner | `owner` | ForeignKey | For ownership semantics |
| Modifier | `modified_by` | ForeignKey | Who last changed it |
| Approver | `approved_by` | ForeignKey | For approval workflows |

**❌ Avoid these patterns:**
- `user_id` (unless it's an IntegerField for external systems)
- `created_by` (use `author` for content creation)
- `userid`, `user_name`

### 3. Status/Boolean Fields

All boolean fields MUST use the `is_` prefix:

| Purpose | Field Name | Type |
|---------|------------|------|
| Active state | `is_active` | BooleanField |
| Archived state | `is_archived` | BooleanField |
| Deleted state | `is_deleted` | BooleanField |
| Published state | `is_published` | BooleanField |
| Verified state | `is_verified` | BooleanField |
| Featured state | `is_featured` | BooleanField |
| Completed state | `is_completed` | BooleanField |

**❌ Avoid these patterns:**
- `active`, `enabled`, `visible` (use `is_active`, `is_enabled`, `is_visible`)
- `archived`, `deleted` (use `is_archived`, `is_deleted`)
- Suffix patterns like `_enabled`, `_active`

### 4. Relationship Fields

| Pattern | Example | Notes |
|---------|---------|-------|
| ForeignKey | `organization` | Singular, lowercase |
| OneToOne | `profile` | Singular, lowercase |
| ManyToMany | `tags` | Plural, lowercase |
| Generic FK | `content_object` | Standard Django pattern |

### 5. Counting/Quantity Fields

| Purpose | Pattern | Example |
|---------|---------|---------|
| Count | `{item}_count` | `view_count`, `like_count` |
| Total | `total_{items}` | `total_points`, `total_revenue` |
| Maximum | `max_{items}` | `max_attempts`, `max_users` |

### 6. Money/Price Fields

| Purpose | Pattern | Type |
|---------|---------|------|
| Prices | `{item}_price` | DecimalField |
| Amounts | `{item}_amount` | DecimalField |
| Costs | `{item}_cost` | DecimalField |
| Currency | `currency_code` | CharField(max_length=3) |

### 7. Naming Conventions

1. **Use snake_case**: `user_profile`, not `userProfile` or `UserProfile`
2. **Be descriptive**: `registration_deadline` not `deadline`
3. **Avoid abbreviations**: `description` not `desc`
4. **Be consistent**: If you use `url` in one place, don't use `link` elsewhere

## Model Structure Standards

### Base Model Example

```python
from django.db import models
from django.conf import settings

class StandardModel(models.Model):
    """Example model following all naming standards"""
    
    # Relationships (at top)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    # Core fields
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    # Status fields (boolean)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    # Timestamps (at bottom)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', '-created_at']),
        ]
```

### Abstract Base Models

```python
class TimestampedModel(models.Model):
    """Base model with standard timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class UserOwnedModel(TimestampedModel):
    """Base model for user-owned resources"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set'
    )
    
    class Meta:
        abstract = True

class SoftDeleteModel(TimestampedModel):
    """Base model with soft delete support"""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
```

## Validation Checklist

Before creating or modifying a model, ensure:

- [ ] Timestamp fields use standard names (`created_at`, `updated_at`)
- [ ] Boolean fields start with `is_`
- [ ] User references use `user` (not `user_id` or `created_by`)
- [ ] Relationships use appropriate singular/plural forms
- [ ] No abbreviations in field names
- [ ] Field names are in snake_case
- [ ] Related names are properly set for ForeignKeys

## Migration Guidelines

When renaming fields to meet standards:

1. **Add new field** with standard name
2. **Create data migration** to copy values
3. **Add compatibility property** for old name
4. **Update all code** to use new name
5. **Remove old field** after verification

## Enforcement

1. **Pre-commit hooks** will validate new models
2. **CI/CD checks** will fail on non-standard fields
3. **Code reviews** must verify naming standards
4. **Django checks** will warn about non-compliance

## Exceptions

Exceptions to these standards require:
1. Technical justification
2. Team consensus
3. Documentation in model docstring
4. Addition to exceptions list below

### Approved Exceptions

1. **accounts.User.date_joined** - Django built-in field
2. **External API fields** - Must match external schema