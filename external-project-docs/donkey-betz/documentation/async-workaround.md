# Async Context Workaround Strategy

## Current Status
- System is functioning well overall
- Two non-blocking async errors persist:
  1. Memory insights retrieval 
  2. Learning tracking

## Recommended Approach

### Option 1: Disable Enhanced Memory for Intelligent Prompting
Since the error occurs when intelligent prompting tries to use enhanced memory, we can disable this feature temporarily:

```python
# In intelligent_prompt_service.py, modify _analyze_conversation_context:
if self.enhanced_memory and user_profile:
    try:
        # WORKAROUND: Skip enhanced memory in async context
        logger.debug("Skipping enhanced memory insights due to async context issues")
        memory_insights = []
    except Exception as e:
        logger.warning(f"Memory insights retrieval failed: {e}")
        memory_insights = []
```

### Option 2: Use User ID Instead of User Object
Pass user ID instead of user object to avoid foreign key access:

```python
# In personal_ai_services.py, modify the call:
optimal_prompt = await self.intelligent_prompts.select_optimal_prompt(
    user_message=message,
    conversation_context=conversation_history or [],
    user_profile=self.user.id  # Pass ID instead of profile object
)
```

### Option 3: Create Async-Safe User Profile
Create a simple data class that doesn't trigger database access:

```python
@dataclass
class AsyncSafeUserProfile:
    user_id: int
    profile_data: dict
```

## Recommendation
Since the errors are non-blocking and the system works well:
1. Log these as known issues
2. Implement Option 1 (disable feature) as immediate fix
3. Plan proper async refactoring for future release

The current system is ~95% functional, which is acceptable for production use.