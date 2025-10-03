# Async/Sync Context Issues - Comprehensive Map

## Current Error Pattern
```
UnboundLocalError: cannot access local variable 'sync_to_async' where it is not associated with a value
```

## Call Stack Analysis

### 1. Entry Point: Auto-processing Conversation
- **Trigger**: New conversation saved triggers signal
- **Location**: Unknown signal handler
- **Context**: Likely SYNC (Django signals are typically sync)

### 2. Unified Conversation Bridge
- **File**: `/backend/ai_partner/services/unified_conversation_bridge.py`
- **Method**: `process_conversation_async` (line 48)
- **Context**: ASYNC (method name suggests async)
- **Call**: `await unified_adapter.process_conversation()`

### 3. Unified Embedding Adapter
- **File**: `/backend/shared_memory/unified_embedding_adapter.py`
- **Method**: `process_conversation` (line 161)
- **Context**: ASYNC (being awaited)
- **Call**: `await self.unified_service.create_memory()`

### 4. Unified Memory Service
- **File**: `/backend/shared_memory/services.py`
- **Method**: `create_memory` (line 90)
- **Context**: ASYNC (being awaited)
- **Error Location**: Line 90 - trying to use `sync_to_async`

## Potential Issues to Investigate

### 1. Import Scope Issues
- **Question**: Is `sync_to_async` properly imported at module level?
- **Check**: Line 15 shows global import, but error suggests it's not accessible
- **Possibility**: Could there be a syntax error or indentation issue?

### 2. Method Definition Issues
- **Question**: Is the `create_memory` method properly defined?
- **Check**: Need to verify the method signature and body
- **Possibility**: Malformed method causing Python to misinterpret scope

### 3. Conditional Import Conflicts
- **Pattern Found**: Multiple redundant imports inside if statements
- **Fixed**: Removed local imports, but error persists
- **Question**: Did we miss any? Is there another scope issue?

### 4. File Corruption/Partial Edits
- **Question**: Were all edits applied correctly?
- **Check**: Need to verify file integrity
- **Possibility**: Partial edit leaving method in invalid state

## Investigation Steps Needed

### Step 1: Verify File State
```bash
# Check if file is syntactically valid
python -m py_compile shared_memory/services.py

# Check specific line 90
sed -n '85,95p' shared_memory/services.py
```

### Step 2: Trace Import Chain
- Check if `asgiref.sync` is properly installed
- Verify no circular imports
- Check for any module-level exceptions

### Step 3: Examine Method Structure
- Verify `create_memory` method is properly indented
- Check for any hidden characters or encoding issues
- Ensure all try/except blocks are properly closed

### Step 4: Context Switching Pattern
```
Django View (SYNC) 
  → Signal Handler (SYNC)
    → Bridge.process_conversation_async (ASYNC) 
      → Adapter.process_conversation (ASYNC)
        → Service.create_memory (ASYNC)
          → sync_to_async usage (ERROR)
```

## Common Patterns Causing This Error

### 1. Shadowed Imports
```python
# Global import
from asgiref.sync import sync_to_async

def method():
    if condition:
        from asgiref.sync import sync_to_async  # Shadows global
        # sync_to_async available here
    # sync_to_async NOT available here if condition was true
```

### 2. Exception in Import
```python
try:
    from asgiref.sync import sync_to_async
except ImportError:
    sync_to_async = None  # Could cause UnboundLocalError later
```

### 3. Conditional Definition
```python
if some_condition:
    def create_memory():
        # uses sync_to_async
else:
    def create_memory():
        # different implementation
```

## Recommended Investigation Order

1. **Immediate Check**: Verify line 90 content and surrounding context
2. **Syntax Validation**: Run Python compilation check
3. **Import Verification**: Trace all sync_to_async usages
4. **Method Structure**: Examine complete create_memory method
5. **Call Chain**: Verify each step in the async call chain

## Questions to Answer

1. Is the error happening on the actual line 90 or is the line number misleading?
2. Are there any decorators on create_memory that might affect scope?
3. Is there a try/except block that might be catching and re-raising incorrectly?
4. Are there any metaclasses or descriptors affecting the service class?
5. Is the UnifiedMemoryService being instantiated correctly?

## Investigation Results

### Test 1: Syntax Check ✅
- `python -m py_compile services.py` - No errors
- File is syntactically valid

### Test 2: Import Test ✅
- `sync_to_async` imports successfully
- Type: `<class 'function'>`
- Module: `asgiref.sync`
- UnifiedMemoryService imports successfully
- sync_to_async IS accessible in the services module

### Test 3: Isolated Method Test ✅
- `create_memory` works perfectly in isolation
- Successfully creates memory without errors
- All sync_to_async calls work as expected

## Key Discovery

**The error only occurs in the specific context of the auto-processing conversation flow!**

This suggests:
1. The error is not in the code itself
2. Something in the runtime context is affecting the import
3. Possibly a threading or event loop issue
4. Could be related to how Django signals interact with async code

## Hypothesis

The error might be caused by:

### 1. Signal Handler Context
- Django signals running in a different thread
- Import context not properly shared
- Async context being created incorrectly

### 2. Multiple Event Loops
- Signal handler might be creating its own event loop
- Conflict between Django's async handling and manual event loop creation

### 3. Import Timing
- The module might be imported before Django is fully initialized
- Lazy loading causing import to happen in wrong context

### 4. Gevent/Eventlet Monkey Patching
- Some library might be monkey-patching the import system
- Affecting how modules are loaded in async context

## Root Cause Analysis

### Complete Flow Discovered

1. **Django Signal** (`@receiver(post_save, sender=ConversationMemory)`)
   - Context: SYNC
   - Location: `unified_conversation_bridge.py` line 106

2. **Background Thread** (`threading.Thread`)
   - Context: SYNC (new thread)
   - Location: line 160
   - Creates new database connection

3. **process_conversation_sync** 
   - Context: SYNC
   - Location: line 65
   - **Critical**: Uses `async_to_sync` at line 86

4. **async_to_sync(process_conversation_async)**
   - Context: ASYNC (created by async_to_sync)
   - This is where the context switching happens

5. **Error occurs in create_memory**
   - The async context created by async_to_sync seems corrupted
   - sync_to_async import not accessible in this context

### The Problem

**Threading + async_to_sync + nested async calls = Context Corruption**

The issue appears to be:
1. Running in a background thread
2. Using async_to_sync to create an event loop
3. Inside that, trying to use sync_to_async again
4. The import context is not properly maintained

### Why It Works in Isolation

- Direct async execution has clean context
- No threading involved
- No nested async_to_sync/sync_to_async calls

## Recommended Solutions

### Solution 1: Pure Sync Implementation
Create a fully synchronous version of the processing pipeline that doesn't use any async methods.

### Solution 2: Pure Async Implementation  
Use Django's async signal handlers and avoid threading entirely.

### Solution 3: Fix the Current Implementation
Instead of using threading + async_to_sync, use one of:
- asyncio.run() in the thread
- Django's sync_to_async for the entire operation
- Celery or other task queue

### Solution 4: Disable Auto-Processing
As a temporary fix, disable the signal handler and process conversations manually.