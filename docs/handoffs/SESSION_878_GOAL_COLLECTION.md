---
originating_session: 878
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 878: Goal Collection Implementation

## Summary

Implemented automatic goal collection for users who haven't set goals. The Personal Assistant now prompts users for their goals on first interaction, stores them in `EnhancedUserProfile.long_term_goals`, and injects them into the PA context for personalized responses.

**Status: COMPLETE**

---

## Problem Statement

From Session 877 User Connection Gaps analysis:
- All users had `goals: []` (empty)
- PA couldn't personalize advice without knowing user goals
- No mechanism existed for the system to proactively learn user goals

---

## Solution Implemented

### 1. Goal Collection Flow in `EnhancedPersonalAIAssistant`

Added `_handle_goal_collection()` method to `core/personal_ai_assistant_enhanced.py`:

**Flow:**
1. Check if user has goals → if yes, skip
2. Check if `goals_collection_pending` → user is responding to our prompt
   - Check for skip keywords → mark skipped, return None
   - Extract goals from response → save to `EnhancedUserProfile.long_term_goals`
3. Check if user skipped before → don't ask again
4. Check if recently asked (24h) → don't ask again
5. First interaction without goals → prompt user

**Skip Keywords:** `skip`, `later`, `not now`, `no thanks`, `pass`, `don't want to`, `i'll pass`

### 2. Goal Extraction Algorithm

Added `_extract_goals_from_response()` method:
- Parses bullet points: `- goal` or `* goal` or `• goal`
- Parses numbered lists: `1. goal` or `1) goal`
- Splits on newlines for multi-line responses
- Falls back to treating message as single goal if long enough
- Limits to 5 goals maximum

### 3. Context Middleware Integration

Updated `core/agent_context_middleware.py` to include goals:

```python
# Session 878: Get EnhancedUserProfile for goals
enhanced_profile = EnhancedUserProfile.objects.filter(user=user).first()

# In personalization dict:
'goals': enhanced_profile.long_term_goals if enhanced_profile else []
```

---

## Files Changed

| File | Change |
|------|--------|
| `core/personal_ai_assistant_enhanced.py` | Added `_handle_goal_collection()` and `_extract_goals_from_response()` methods |
| `core/agent_context_middleware.py` | Added EnhancedUserProfile loading and goals to personalization dict |

---

## Testing

### Test: Goal Collection Flow
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model
from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
from core.models import EnhancedUserProfile

User = get_user_model()
test_user = User.objects.get(username='test_user')

# Clear state
profile, _ = EnhancedUserProfile.objects.get_or_create(user=test_user)
profile.long_term_goals = []
profile.dynamic_attributes = {}
profile.save()

assistant = EnhancedPersonalAIAssistant(test_user)

# First message triggers prompt
result1 = assistant._handle_goal_collection('Hello')
print(f'Type: {result1.get(\"type\")}')  # goal_collection_prompt

# User provides goals
result2 = assistant._handle_goal_collection('''
- Build passive income
- Learn ML
- Launch my SaaS
''')
print(f'Saved: {result2.get(\"goals_saved\")}')
"
```

### Test: Goals in PA Context
```bash
python manage.py shell -c "
from django.contrib.auth import get_user_model
from core.agent_router import AgentRouter

User = get_user_model()
user = User.objects.get(username='test_user')
router = AgentRouter(user=user)
ctx = router._get_user_context('PersonalAssistantAgent', 'help')
print(f'Goals: {ctx.get(\"goals\")}')
"
```

---

## User Experience

### First Interaction (No Goals)
```
User: Hello, can you help me?

PA: Hi test_user! To help you most effectively, I'd love to know what you're
    working toward.

    **What are your top 2-3 goals right now?**

    They could be anything - career goals, learning goals, income targets, or
    personal projects. For example:
    - Increase my freelance income to $5k/month
    - Build and launch a SaaS product
    - Transition into a data science role

    (Type 'skip' if you'd rather set goals later)
```

### User Provides Goals
```
User: - Build a passive income stream of $3000/month
      - Learn machine learning and get an ML engineering job
      - Launch my SaaS idea by June

PA: Thanks for sharing your goals! I've noted:

    - Build a passive income stream of $3000/month
    - Learn machine learning and get an ML engineering job
    - Launch my SaaS idea by June

    I'll keep these in mind to help you more effectively. What would you like
    to work on today?
```

### User Skips
```
User: skip

PA: (continues to normal processing - user won't be asked again)
```

---

## State Tracking

Goals collection state is stored in `EnhancedUserProfile.dynamic_attributes`:

| Key | Type | Purpose |
|-----|------|---------|
| `goals_collection_pending` | bool | True when waiting for user's goal response |
| `goals_collection_skipped` | bool | True if user chose to skip |
| `goals_collection_skipped_at` | ISO datetime | When user skipped |
| `goals_collection_last_asked` | ISO datetime | Last time we prompted (for 24h cooldown) |
| `goals_collected_at` | ISO datetime | When goals were successfully saved |

---

## Remaining User Connection Gaps

From Session 877 analysis, still not addressed:

| Gap | Status | Next Step |
|-----|--------|-----------|
| Goals not collected | **FIXED** | Goal collection implemented |
| No onboarding flow | NOT FIXED | Wire up interview endpoints |
| Interview system unused | NOT FIXED | Connect to PA |
| EnhancedUserProfile sparse | NOT FIXED | Create for all users |
| Proactive learning | NOT FIXED | Add follow-up questions |

---

## Related Sessions

- **Session 877**: User connection gaps analysis, PA skills injection fix
- **Session 858**: User context injection infrastructure
- **Session 430**: Interview system creation (unused)

---

## Next Steps for Session 879

1. **Test in Browser**: Verify goal collection works in actual PA UI
2. **Wire Interview System**: Connect existing interview endpoints
3. **EnhancedUserProfile Creation**: Ensure all users have one
4. **Proactive Learning**: Add context-based follow-up questions