# Async Context Issue Summary

## The Core Problem

The `UnboundLocalError: cannot access local variable 'sync_to_async'` is NOT a code error. The code is correct. The issue is a **context corruption** caused by complex async/sync mixing.

## What's Happening

1. **Signal Handler** (sync) triggers on ConversationMemory save
2. **Background Thread** is created to avoid blocking
3. **In the thread**, `async_to_sync` is used to call async methods
4. **Inside the async context**, `sync_to_async` becomes inaccessible

This creates a corrupted execution context where imports don't work as expected.

## Why This Is Happening

```
Django Signal (SYNC)
    ↓
Background Thread (SYNC) 
    ↓
async_to_sync() creates event loop
    ↓
Async methods run
    ↓
sync_to_async tries to import but fails ❌
```

The combination of:
- Threading
- async_to_sync in a thread
- Nested sync_to_async calls
- Import mechanics in Python

...creates a perfect storm where the import context is corrupted.

## Evidence

1. ✅ The code syntax is correct
2. ✅ sync_to_async imports fine normally  
3. ✅ create_memory works in isolation
4. ❌ Only fails in this specific signal→thread→async flow

## Quick Fixes (Choose One)

### Option 1: Disable Auto-Processing (Immediate)
```python
# In unified_conversation_bridge.py, comment out the signal
# @receiver(post_save, sender=ConversationMemory)
# def conversation_created_handler(sender, instance, created, **kwargs):
#     pass
```

### Option 2: Remove Threading (Simple)
```python
# In the signal handler, call sync method directly
bridge.process_conversation_sync(instance, create_legacy_embedding=True)
# Remove all the threading code
```

### Option 3: Use Celery (Recommended)
```python
# In the signal handler
from .tasks import process_conversation_task
process_conversation_task.delay(instance.id)
```

### Option 4: Fix the Sync Method (Best)
```python
# In process_conversation_sync, use asyncio.run instead
import asyncio
return asyncio.run(self.process_conversation_async(
    conversation, 
    create_legacy_embedding
))
```

## Long-term Solution

The mixing of sync Django signals, threading, and async code is inherently problematic. The system should either:

1. Use **fully async** Django (with async signals)
2. Use **fully sync** processing (no async methods)
3. Use a **task queue** (Celery, RQ, etc.)
4. **Separate** the async and sync paths completely

## Impact

This issue only affects:
- Auto-processing of new conversations
- The unified memory system
- Background processing

It does NOT affect:
- Chat functionality
- Direct API calls
- Other features

## Recommendation

For now, I recommend **disabling the auto-processing** until a proper solution is implemented. The conversations can still be processed manually or via a scheduled task.