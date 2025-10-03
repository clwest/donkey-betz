# Async Event Loop Fix - Complete

## Problem
"RuntimeError: Event loop is closed" errors when the AI Assistant searches documents.

## Root Cause
The `MultiModelAIService` was being instantiated before checking if we're in an async context. When we're already in an async context and fall back to text search, the AI service's httpx client still tries to clean up its connections, causing the error.

## Solution Applied
1. **Moved AI service instantiation** inside the sync context check
2. **Only create AI service** when we can actually use it (not in async context)
3. **Improved cleanup timeout** handling for pending tasks

## Changes Made
In `/Users/donkeyking/development/move_that_ass/backend/ukf_system/services/unified_memory_search.py`:

### Before:
```python
ai_service = MultiModelAIService()  # Created too early!

# Handle async embedding generation in a thread-safe way
try:
    # Check if we're in an async context
    try:
        loop = asyncio.get_running_loop()
        # We're already in an async context, can't use asyncio.run
        query_embedding = None  # AI service still has httpx client to cleanup
```

### After:
```python
# Handle async embedding generation in a thread-safe way
try:
    # Check if we're in an async context
    try:
        loop = asyncio.get_running_loop()
        # We're already in an async context, can't use asyncio.run
        query_embedding = None  # No AI service created, no cleanup needed
    except RuntimeError:
        # No running loop, safe to create one
        try:
            # Only create AI service when we can use it
            ai_service = MultiModelAIService()  # Created only when needed
```

## Testing
1. Restart the server: `make run-backend-ws`
2. Ask the AI Assistant questions that trigger document search
3. Monitor `logs/errors.log` - no more "Event loop is closed" errors should appear

## Additional Note
The "Suspicious request blocked" warning at 23:37:59 was due to a query parameter containing special characters (apostrophe). This is handled by Django's security middleware and doesn't affect functionality.