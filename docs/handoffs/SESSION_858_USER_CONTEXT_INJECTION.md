---
originating_session: 858
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 858: User Context Injection

**Date:** January 28, 2026
**Focus:** Teaching the System About the User - Connecting Profile Data to Agents

## Summary

Implemented user context injection so that all 74 agents now receive personalized user data through the existing `context` dict parameter, without changing the `execute()` signature.

## Key Changes

### 1. AgentRouter User Context (`core/agent_router.py`)

Added three new methods:

- **`_get_user_context(agent_name, task)`** - Retrieves user profile and memory context
- **`_apply_injection_policy(agent_name, task, profile_context, memory_context)`** - Filters context based on agent category
- **`_record_user_learning(agent_name, task, result, user_context)`** - Records success patterns for learning loop

Added injection policy mappings:
- `AGENT_INJECTION_POLICIES` - Defines what data each agent category gets
- `AGENT_CATEGORY_MAP` - Maps agents to categories (career, content, financial, development, research)

### 2. Context Injection Flow

In `route()`:
1. Calls `_get_user_context()` alongside other context gathering
2. Injects user context into `context` dict: `context['user']`, `context['user_name']`, etc.
3. Logs injection in `context_summary`
4. Calls `_record_user_learning()` after successful execution

In `gather_context()`:
- Added `user_context` to pre-gathered context return dict

### 3. Workspace Auto-Creation (`core/services/workspace_manager.py`)

Added `_ensure_personal_workspace()` method that:
- Creates personal workspace at `generated_content/users/{username}/`
- Auto-activates on first access
- Prevents "No active workspace" errors

Modified `get_active_workspace()`:
- Now auto-creates personal workspace for ANY user without one
- No longer requires explicit workspace registration

## Agent Injection Policy

| Category | Agents | Data Injected |
|----------|--------|---------------|
| **career** | OpportunityPipelineAgent, OpportunityScoringAgent | skills, job_preferences, salary_range, work_history, success_patterns |
| **content** | ContentWriterAgent, ContentStrategyAgent, SEOOptimizerAgent | communication_style, tone_preferences, goals |
| **financial** | StockAnalystAgent, SportsOddsAnalyst, ArbitrageDetector | risk_tolerance, betting_preferences, investment_goals |
| **development** | CodeGeneratorAgent, FullStackDeveloperAgent, DevOpsAgent | skills, tech_stack, github_username |
| **research** | ResearchAgent, TrendAnalysisAgent, CompetitorAnalysisAgent | interests, learning_goals, preferred_topics |
| **default** | All other agents | name, goals, communication_style |

## How Agents Access User Context

Agents now receive user data in the `context` parameter:

```python
def execute(self, task, context, scifi_context, spider_context):
    # Access user context
    user = context.get('user', {})
    user_name = context.get('user_name', '')
    user_skills = context.get('user_skills', [])
    user_goals = context.get('user_goals', [])
    user_communication_style = context.get('user_communication_style', 'professional')

    # Use for personalization
    if user_skills:
        prompt += f"\nUser has skills in: {', '.join(user_skills)}"
```

## Learning Feedback Loop

When an agent succeeds, `_record_user_learning()` creates a `UserMemoryContext` entry:
- `memory_type='success_pattern'`
- `source='agent:{agent_name}'`
- Contains task summary, execution time, tokens used

This enables the system to learn what works for each user.

## Testing

```bash
# Test user context injection
python manage.py shell -c "
from django.contrib.auth import get_user_model
from core.agent_router import get_agent_router
user = get_user_model().objects.filter(is_staff=True).first()
router = get_agent_router(user)
context = router._get_user_context('ContentWriterAgent', 'test')
print(context)
"
```

## Files Modified

| File | Changes |
|------|---------|
| `core/agent_router.py` | Added `_get_user_context()`, `_apply_injection_policy()`, `_record_user_learning()`, injection mappings |
| `core/services/workspace_manager.py` | Added `_ensure_personal_workspace()`, updated `get_active_workspace()` |

## What This Enables

1. **Personalized Agent Responses** - Agents know user's name, skills, preferences
2. **Category-Specific Context** - Career agents get job data, content agents get tone preferences
3. **No More "No Active Workspace"** - Personal workspace auto-created
4. **Learning Feedback Loop** - Success patterns recorded for future improvement
5. **Backwards Compatible** - No changes to `execute()` signature

## Next Steps

1. **Enhance Individual Agents** - Update high-value agents to use `context['user']`
2. **Profile Onboarding** - Create interview flow to populate EnhancedUserProfile
3. **User Canon Doc** - Auto-generate "Operating Manual" from profiles
4. **Success Pattern Retrieval** - Use recorded patterns in agent prompts
