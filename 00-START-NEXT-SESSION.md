# Session 930 - Start Here

**Previous Session:** 928 (Initiative Conversations + Modal Updates)
**Date:** February 4, 2026
**Status:** 76 Agents | 77 Spiders | 25 Advisors | 139 Personas | **373 INITIATIVES** | **Initiative Conversations: DEPLOYED** | **User Context Injection: EXISTS** | **User Learning: PARTIAL**

---

## PRIORITY: User Context Injection & Learning System

### The Question
How does the User get injected into context, and how does the system start learning from the User?

### Current State (from codebase exploration)

#### What EXISTS (Session 858+):

**User Profile Models:**
| Model | Location | Purpose |
|-------|----------|---------|
| `UserProfile` | `core/models.py:552` | Basic profile, skills, job preferences, AI preferences |
| `ExtendedUserProfile` | `core/models.py:807` | Work history, education, salary expectations |
| `EnhancedUserProfile` | `core/models.py:1600` | Goals, OKRs, risk tolerance, learning preferences |
| `HumanPreference` | `core/models_human_interface.py:263` | Notification prefs, learned preferences (topic_weights, approval_rate) |

**Context Injection Flow:**
```
User Request
    ↓
AgentRouter.route()
    ↓
_get_user_context(agent_name, task)
    ├─ AgentContextMiddleware.get_user_context()  [5-min cache]
    └─ MemoryContextService.get_prompt_context()  [decay-weighted memories]
    ↓
_apply_injection_policy(agent_name)  [category-based filtering]
    ↓
Agent Execution with Personalized Context
```

**Injection Policies by Category:**
| Category | Fields Injected |
|----------|-----------------|
| `personal_assistant` | **ALL** (full context) |
| `career` | skills, job_preferences, salary_range, work_history, success_patterns |
| `content` | communication_style, tone_preferences, goals |
| `financial` | risk_tolerance, betting_preferences, investment_goals |
| `development` | skills, tech_stack, github_username |
| `research` | interests, learning_goals, preferred_topics |
| `default` | name, goals, communication_style |

**Learning Mechanisms:**
- `PersonalizationFeedbackLoop` - Learns from opportunity interactions (view→click→apply→interview→accept)
- `UserAgentLearning` model - Stores domain-specific learnings with confidence scores
- `UserMemoryContext` - Decay-weighted memories (e^(-age_days/21))

#### What's MISSING:

| Gap | Impact |
|-----|--------|
| **User Skill Evolution** | No tracking of how skills improve over time |
| **Agent-Specific Learning** | No per-agent profiles of what works for specific user |
| **Conversion Metrics** | No tracking of which personalization strategies convert to action |
| **Goal Progress Tracking** | Goals stored but no progress metrics |
| **Active Learning Loop** | System doesn't ask user for feedback to improve |
| **Profile Completeness UX** | No prompting user to fill gaps in profile |

---

### Session 930 Tasks

#### 1. Audit Current User Context Flow
```bash
# Check which users have profiles
railway run python manage.py shell -c "
from core.models import UserProfile, ExtendedUserProfile, EnhancedUserProfile
from django.contrib.auth import get_user_model
User = get_user_model()

total = User.objects.count()
with_profile = UserProfile.objects.count()
with_extended = ExtendedUserProfile.objects.count()
with_enhanced = EnhancedUserProfile.objects.count()

print(f'Users: {total}')
print(f'With UserProfile: {with_profile}')
print(f'With ExtendedUserProfile: {with_extended}')
print(f'With EnhancedUserProfile: {with_enhanced}')
"
```

#### 2. Trace Context Injection
Test what context actually reaches agents:
```python
# In shell, test context for a specific user
from core.agent_context_middleware import AgentContextMiddleware
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.first()
middleware = AgentContextMiddleware()
context = middleware.get_user_context(user)
print(context)
```

#### 3. Implement Active Learning Improvements

**Option A: Profile Completeness Prompting**
- Add `profile_gaps` method to identify missing fields
- PA prompts user: "I notice I don't know your salary expectations. Would you like to share?"

**Option B: Feedback After Agent Execution**
- After key agent outputs, ask: "Was this helpful? (👍/👎)"
- Store in `UserAgentLearning` with agent_id for per-agent learning

**Option C: Goal Progress Tracking**
- Add `GoalProgress` model linking goals to deliverables/initiatives
- Show user: "You're 40% toward your goal of [X]"

**Option D: Skill Evolution Tracking**
- Track skills demonstrated in deliverables
- Auto-update user skills based on successful outputs

---

### Key Files to Review

| File | Purpose |
|------|---------|
| `core/agent_router.py` | `_get_user_context()`, `_apply_injection_policy()` |
| `core/agent_context_middleware.py` | `AgentContextMiddleware.get_user_context()` |
| `core/services/memory_context_service.py` | `MemoryContextService.get_prompt_context()` |
| `core/learning_bridges/personalization_bridge.py` | `PersonalizationFeedbackLoop` |
| `core/models.py` | UserProfile, ExtendedUserProfile, EnhancedUserProfile |
| `core/models_human_interface.py` | HumanPreference, HumanFeedbackRecord |

---

## Session 928 Summary (Previous)

### Deployed Features
- **Initiative Conversations** - "Discuss with Agents" button creates HiveMindSession with initiative context
- **HiveMind Modal Updates** - Sessions show linked initiative with clickable link
- **Blocker Analysis UI** - Health tab shows why initiatives are stuck

### Production Fixes
- Fixed `founder_intent_set` for 50 initiatives
- Reset 286 stub documents to PENDING
- Migration 0227 applied

### PRs Merged
#828, #829, #830, #831, #832, #833

---

## Recent Session History

| Session | Focus | Handoff |
|---------|-------|---------|
| **928** | Initiative Conversations + Modal Updates | `SESSION_928_INITIATIVE_CONVERSATIONS.md` |
| **927** | Universal Agent Voice System | `SESSION_926_UNIVERSAL_AGENT_VOICE.md` |
| **926** | Stage 1 Backfill Push (62% → 95%) | `SESSION_925_AUTO_CLEANUP.md` |
| 925 | Auto-Cleanup Stuck Executions | `SESSION_925_AUTO_CLEANUP.md` |

---

**Session 930 Focus: Understand and enhance how user context flows into agents and how the system learns from user interactions.**
