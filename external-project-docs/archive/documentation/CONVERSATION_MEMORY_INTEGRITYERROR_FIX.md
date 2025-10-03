# ConversationMemory IntegrityError Fix Documentation

## Problem Summary
Django was throwing IntegrityError exceptions when creating ConversationMemory objects:
```
null value in column "user_feedback" of relation "ai_partner_conversationmemory" violates not-null constraint
```

This error occurred for multiple fields:
- `user_feedback` (EncryptedTextField)
- `transcript` (EncryptedTextField) 
- `message_content` (EncryptedTextField)
- `user_mood` (CharField)
- `energy_level` (CharField)

## Root Cause Analysis

### 1. Encryption Service Issue
The `EncryptionService.encrypt()` method was returning `None` for empty strings:
```python
def encrypt(self, plaintext):
    if not plaintext:  # This catches empty strings!
        return None    # Database receives NULL instead of encrypted empty string
```

### 2. Field Configuration
- Fields were configured with `blank=True` (allows empty string in forms)
- But also `null=False` (database doesn't allow NULL)
- When encryption returned None, database constraint was violated

### 3. Missing Field Values
Many `ConversationMemory.objects.create()` calls throughout the codebase were missing required fields, relying on defaults that weren't being applied.

## Solution Implementation

### 1. Fixed Encryption Service (`/backend/security/encryption.py`)
```python
def encrypt(self, plaintext):
    """Encrypt text data"""
    # Handle None separately from empty string
    if plaintext is None:
        return None
    # Convert to string and encrypt (including empty strings)
    plaintext = str(plaintext)
    try:
        return self.cipher.encrypt(plaintext.encode()).decode()
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise
```

### 2. Enhanced Encrypted Fields (`/backend/security/fields.py`)
Added `get_db_prep_value()` to both EncryptedTextField and EncryptedCharField:
```python
def get_db_prep_value(self, value, connection, prepared=False):
    """Prepare value for database storage"""
    # First handle None values for non-null fields
    if value is None and not self.null:
        # Try to get the default value
        if self.has_default():
            value = self.get_default()
        # If no default but blank is allowed, use empty string
        elif self.blank:
            value = ''
    
    # Then call parent's method which will call get_prep_value
    return super().get_db_prep_value(value, connection, prepared)
```

### 3. Custom Manager (`/backend/ai_partner/models.py`)
Created `ConversationMemoryManager` to handle field defaults:
```python
class ConversationMemoryManager(models.Manager):
    """Custom manager to handle field defaults"""
    
    def create(self, **kwargs):
        """Override create to ensure fields have defaults"""
        # Set defaults for fields that might be None
        if 'user_mood' in kwargs and kwargs['user_mood'] is None:
            kwargs['user_mood'] = ''
        elif 'user_mood' not in kwargs:
            kwargs['user_mood'] = ''
        # ... similar for other fields
        
        return super().create(**kwargs)
```

### 4. Model Updates
- Added `objects = ConversationMemoryManager()` to ConversationMemory model
- Added `clean()` method to ensure fields are set before save
- Created migrations to add database-level defaults

### 5. Updated All Create Calls
Fixed all `ConversationMemory.objects.create()` calls across the codebase to include:
- `user_feedback=''`
- `user_mood=''`
- `energy_level=''`

## Files Modified

### Core Fix Files
1. `/backend/security/encryption.py` - Fixed empty string handling
2. `/backend/security/fields.py` - Added get_db_prep_value methods
3. `/backend/ai_partner/models.py` - Added custom manager and defaults

### Migration Files
1. `0017_add_default_to_transcript.py` - Added defaults for transcript and message_content
2. `0018_add_defaults_to_charfields.py` - Added defaults for user_mood and energy_level

### Updated Create Calls
1. `/backend/ai_partner/views.py`
2. `/backend/ai_partner/consumers.py`
3. `/backend/ai_partner/personal_ai_services.py`
4. `/backend/memory/views_memory_palace.py`
5. `/backend/ai_partner/services/learning_enhanced_personal_ai.py`
6. `/backend/content/services/content_memory_service.py`
7. `/backend/ai_partner/services/learning_enhanced_ai.py`
8. `/backend/ai_partner/code_assistant_service.py`
9. `/backend/ai_partner/services/document_ingestion_service.py`
10. `/backend/ai_partner/memory_services/reliable_memory_service.py`

### Integration Files
1. `/backend/mythology_lab/hooks/enhanced_conversation_memory.py` - Updated to call clean()

## Testing

All tests now pass:
```python
# Test 1: Minimal fields only
ConversationMemory.objects.create(user=user)  # ✅ Works!

# Test 2: Empty strings
ConversationMemory.objects.create(
    user=user,
    user_feedback='',
    transcript=''
)  # ✅ Works!

# Test 3: None values (converted to empty strings)
ConversationMemory.objects.create(
    user=user,
    user_feedback=None,
    transcript=None,
    user_mood=None
)  # ✅ Works!
```

## Key Learnings

1. **Encryption Services**: Must handle empty strings differently from None/null values
2. **Django Fields**: Fields with `blank=True, null=False` need special handling for None values
3. **Custom Managers**: Useful for ensuring data consistency at the model level
4. **Migrations**: Database defaults don't automatically apply to Django ORM create() calls

## Future Recommendations

1. Consider adding model-level validation in `full_clean()`
2. Add unit tests for encryption service edge cases
3. Consider using Django's `default` parameter more consistently
4. Document required vs optional fields in model docstrings

## Additional Agent Status Fixes (July 16, 2025)

### Agent Status Field Name Errors Fixed

**Problem**: Agent status functionality was failing with two errors:
1. `Cannot resolve keyword 'started_at' into field` - in AgentInstance queries
2. `You cannot call this from an async context` - in system_state_service calls

**Root Cause**: 
- `AgentInstance` model uses `created_at` field, not `started_at`
- `TaskOrchestration` model uses `started_at` field (correct)
- System state service calls were not wrapped with `sync_to_async`

**Files Fixed**:
1. `/backend/ai_partner/personal_ai_services.py:1100` - Changed `order_by('-started_at')` to `order_by('-created_at')` for AgentInstance queries
2. `/backend/ai_partner/personal_ai_services.py:868` - Wrapped `system_state_service.get_recent_agent_results()` with `sync_to_async`
3. `/backend/ai_partner/services/system_state_service.py:74` - Changed `'created_at'` to `'started_at'` for TaskOrchestration field reference

**Result**: 
- Agent status functionality now works properly
- All async context errors resolved
- ✅ Comprehensive testing passed