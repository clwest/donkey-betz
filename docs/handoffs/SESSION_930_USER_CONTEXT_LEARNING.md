---
originating_session: 930
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 930 - User Context Injection & Learning System

**Date:** February 4, 2026
**Focus:** How user context flows to agents + How system learns from user interactions
**Status:** ✅ COMPLETE - Backend fully implemented, deployed to production

---

## Session Summary

This session addressed two fundamental questions:
1. **How does the User get injected into context?** → Documented existing system
2. **How does the system start learning from the User?** → Implemented new learning infrastructure

### What Was Completed

| Component | Status | PR | Details |
|-----------|--------|-----|---------|
| Documentation of current system | ✅ | #835 | Context injection flow, injection policies |
| User Learning Models | ✅ | #836 | 5 new models in `models_user_learning.py` |
| Migration 0228 | ✅ | #836 | Applied to Railway production |
| ProfileCompletenessService | ✅ | #837 | Gap detection, contextual prompts |
| AgentFeedbackService | ✅ | #837 | 👍/👎 tracking, effectiveness scoring |
| GoalTrackingService | ✅ | #837 | Progress tracking, auto-linking |
| SkillEvolutionService | ✅ | #837 | Skill inference, proficiency tracking |
| API Endpoints (14 routes) | ✅ | #837 | Full REST API at `/api/user-learning/` |

---

## Part 1: Current User Context System (Documented)

### User Profile Models (4 Layers)

| Model | Location | Purpose | Key Fields |
|-------|----------|---------|------------|
| `UserProfile` | `core/models.py:552` | Basic profile & preferences | display_name, skills, occupation, job_preferences (remote_only, contract_work, hourly_rate_min), preferred_ai_model, default_content_tone |
| `ExtendedUserProfile` | `core/models.py:807` | Professional details | current_title, years_experience, experience_level, desired_salary, work_history, education, certifications |
| `EnhancedUserProfile` | `core/models.py:1600` | Goals & deep preferences | primary_role, long_term_goals, quarterly_objectives, risk_tolerance, investment_goals, learning_preferences, communication_preferences |
| `HumanPreference` | `core/models_human_interface.py:263` | Learned preferences | topic_weights, source_weights, approval_rate, avg_decision_time_ms, trusted_agents, blocked_sources |

### Context Injection Flow

```
User Request
    │
    ▼
┌─────────────────────────────────────────────┐
│           AgentRouter.route()                │
│                                              │
│  1. _get_user_context(agent_name, task)      │
│     ├─ AgentContextMiddleware.get_user_context()  │
│     │   └─ Extracts from all 4 profile models     │
│     │   └─ 5-minute cache to avoid DB hits        │
│     └─ MemoryContextService.get_prompt_context()  │
│         └─ Decay-weighted memories (e^-age/21)    │
│         └─ ~500 token cap per memory block        │
│                                              │
│  2. _apply_injection_policy(agent_name)      │
│     └─ Category-based field filtering        │
│                                              │
└─────────────────────────────────────────────┘
    │
    ▼
Agent Execution with Personalized Context
```

### Injection Policies by Agent Category

**Location:** `core/agent_router.py`

| Category | Agents | Fields Injected |
|----------|--------|-----------------|
| `personal_assistant` | PersonalAssistantAgent | **ALL** (full context) |
| `career` | OpportunityPipelineAgent, CustomerResearchAgent, OpportunityScoringAgent | skills, job_preferences, salary_range, work_history, success_patterns |
| `content` | ContentWriterAgent, PodcastCoordinatorAgent, BrandIdentityAgent, SEOOptimizerAgent | communication_style, tone_preferences, goals |
| `financial` | StockAnalystAgent, SportsOddsAnalyst, PredictionMarketAnalyst, ArbitrageDetector | risk_tolerance, betting_preferences, investment_goals |
| `development` | FullStackDeveloperAgent, CodeReviewAgent, DevOpsAgent | skills, tech_stack, github_username |
| `research` | ResearchAgent, TrendAnalysisAgent, CompetitorAnalysisAgent | interests, learning_goals, preferred_topics |
| `default` | All others | name, goals, communication_style |

### Key Implementation Files

| File | Class/Function | Purpose |
|------|----------------|---------|
| `core/agent_router.py` | `AgentRouter._get_user_context()` | Main entry point for context gathering |
| `core/agent_router.py` | `AgentRouter._apply_injection_policy()` | Category-based filtering |
| `core/agent_context_middleware.py` | `AgentContextMiddleware.get_user_context()` | Extracts structured context from all profiles |
| `core/services/memory_context_service.py` | `MemoryContextService.get_prompt_context()` | Builds decay-weighted memory context |

---

## Part 2: Existing Learning Mechanisms (Documented)

### Learning Bridges Architecture

**Location:** `core/learning_bridges/`

```
User Interaction (view, click, apply, etc.)
    │
    ▼
┌─────────────────────────────────────────────┐
│      PersonalizationFeedbackLoop            │
│      (personalization_bridge.py)            │
│                                             │
│  Listens to Django signals:                 │
│  - OpportunityInteraction.post_save         │
│  - ConversationMemory.post_save             │
│                                             │
│  Extracts patterns:                         │
│  - work_style: remote/hybrid/onsite         │
│  - job_type: full_time/contract/freelance   │
│  - industry: tech/ai/finance/crypto         │
│  - skills: python/javascript/data           │
│  - salary preferences                       │
│                                             │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│         UserAgentLearning Model             │
│                                             │
│  - domain: 'chat_preferences', 'user_prefs' │
│  - content: JSON of learned patterns        │
│  - confidence: 0-1 (increases with use)     │
│  - source: behavioral/conversational        │
│                                             │
└─────────────────────────────────────────────┘
```

### Memory Decay Weighting

**Formula:** `weight = e^(-age_days / 21)`

| Age | Weight | Meaning |
|-----|--------|---------|
| Today | 1.00 | Full relevance |
| 1 week | 0.72 | High relevance |
| 3 weeks | 0.37 | Moderate relevance |
| 6 weeks | 0.14 | Low relevance |
| 2 months | 0.05 | Near-forgotten |

---

## Part 3: Gaps Identified & Addressed

| Gap | Status | Solution |
|-----|--------|----------|
| **User Skill Evolution** | ✅ FIXED | `UserSkill` + `SkillDemonstration` models, `SkillEvolutionService` |
| **Agent-Specific Learning** | ✅ FIXED | `AgentFeedback` model, `AgentFeedbackService` |
| **Goal Progress Tracking** | ✅ FIXED | `GoalProgress` model, `GoalTrackingService` |
| **Active Feedback Loop** | ✅ FIXED | 👍/👎 API endpoint, effectiveness scoring |
| **Profile Completeness UX** | ✅ FIXED | `ProfileCompletionPrompt` model, `ProfileCompletenessService` |
| **Conversion Metrics** | 🔄 PARTIAL | Can now link deliverables to goals for tracking |

---

## Part 4: New Models Created (PR #836)

**File:** `core/models_user_learning.py`

### AgentFeedback
Track user feedback on agent executions for per-agent learning.

```python
class AgentFeedback(models.Model):
    user = models.ForeignKey(User, related_name='agent_feedbacks')
    agent = models.ForeignKey(Agent, related_name='user_feedbacks')
    execution_id = models.UUIDField(null=True)  # Link to AgentExecution
    rating = models.IntegerField(choices=[(1, 'Helpful'), (0, 'Neutral'), (-1, 'Not Helpful')])
    feedback_text = models.TextField(blank=True)
    context_snapshot = models.JSONField(default=dict)
    task_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### GoalProgress
Track progress entries toward user goals.

```python
class GoalProgress(models.Model):
    goal = models.ForeignKey(UserGoal, related_name='goal_progress_entries')
    deliverable = models.ForeignKey(Deliverable, null=True)
    initiative = models.ForeignKey(Initiative, null=True)
    progress_delta = models.IntegerField()  # Percentage points (e.g., 5 = +5%)
    milestone_reached = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    is_automatic = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

### UserSkill
Track user skill proficiency levels (1-10 scale).

```python
class UserSkill(models.Model):
    user = models.ForeignKey(User, related_name='tracked_skills')
    skill_name = models.CharField(max_length=100)
    category = models.CharField(choices=[
        ('technical', 'Technical'), ('creative', 'Creative'),
        ('analytical', 'Analytical'), ('communication', 'Communication'),
        ('leadership', 'Leadership'), ('domain', 'Domain Knowledge')
    ])
    proficiency_level = models.IntegerField(default=1)  # 1-10
    evidence_count = models.IntegerField(default=0)
    confidence = models.FloatField(default=0.5)  # 0-1
    first_demonstrated = models.DateTimeField(auto_now_add=True)
    last_demonstrated = models.DateTimeField(auto_now=True)
```

### SkillDemonstration
Record individual skill demonstrations as evidence.

```python
class SkillDemonstration(models.Model):
    skill = models.ForeignKey(UserSkill, related_name='demonstrations')
    deliverable = models.ForeignKey(Deliverable, null=True)
    quality_score = models.FloatField()  # 0-1
    context = models.TextField(blank=True)
    inference_source = models.CharField(default='deliverable')  # deliverable, manual, import
    created_at = models.DateTimeField(auto_now_add=True)
```

### ProfileCompletionPrompt
Track profile completion prompts to prevent over-prompting.

```python
class ProfileCompletionPrompt(models.Model):
    user = models.ForeignKey(User, related_name='profile_prompts')
    field_category = models.CharField(max_length=50)
    field_name = models.CharField(max_length=100)
    prompt_text = models.TextField()
    was_completed = models.BooleanField(default=False)
    was_dismissed = models.BooleanField(default=False)
    response_value = models.TextField(blank=True)
    prompted_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True)
```

---

## Part 5: New Services Created (PR #837)

### ProfileCompletenessService
**File:** `core/services/profile_completeness_service.py`

Identifies gaps in user profiles and generates natural language prompts.

```python
class ProfileCompletenessService:
    PROFILE_FIELDS = {
        'basic': [('display_name', 'Display Name', 1, "What would you like me to call you?"), ...],
        'skills': [...],
        'career': [...],
        'goals': [...],
        'preferences': [...],
        'financial': [...],
    }

    def get_completeness_score(self, user) -> float
    def get_profile_gaps(self, user) -> Dict[str, List[ProfileGap]]
    def get_next_question(self, user) -> Optional[ProfileGap]
    def get_contextual_prompt(self, user, context: str = None) -> Optional[str]
    def record_prompt(self, user, field_name: str, prompt_text: str) -> None
    def record_response(self, user, field_name: str, value: str, completed: bool = True) -> None
```

### AgentFeedbackService
**File:** `core/services/agent_feedback_service.py`

Handles 👍/👎 feedback and calculates agent effectiveness for each user.

```python
class AgentFeedbackService:
    def record_feedback(self, user, agent, rating: int, ...) -> AgentFeedback
    def get_agent_effectiveness(self, user, agent) -> AgentEffectiveness
    def adjust_context_for_agent(self, user, agent, base_context: Dict) -> Dict
    def get_user_agent_summary(self, user) -> Dict[str, Any]

    # Syncs to existing AgentLearningService for deep learning
    def _sync_to_learning_service(self, user, agent, rating: int, context: Dict = None)
```

**AgentEffectiveness dataclass:**
```python
@dataclass
class AgentEffectiveness:
    agent_id: str
    agent_name: str
    total_feedbacks: int
    helpful_count: int
    not_helpful_count: int
    neutral_count: int
    effectiveness_score: float  # -1 to 1
    recent_trend: str  # 'improving', 'declining', 'stable'
    top_successful_contexts: List[str]
    areas_for_improvement: List[str]
```

### GoalTrackingService
**File:** `core/services/goal_tracking_service.py`

Links deliverables and initiatives to goals, calculates progress.

```python
class GoalTrackingService:
    def link_deliverable_to_goal(self, deliverable, goal, progress_delta: int = 5, ...) -> GoalProgress
    def link_initiative_to_goal(self, initiative, goal, progress_delta: int = 10, ...) -> GoalProgress
    def record_manual_progress(self, goal, progress_delta: int, milestone: str = '', ...) -> GoalProgress
    def calculate_progress(self, goal) -> int  # 0-100
    def get_goal_summary(self, goal) -> GoalSummary
    def get_user_goals_dashboard(self, user) -> Dict[str, Any]
    def suggest_goal_for_deliverable(self, user, deliverable) -> Optional[UserGoal]
    def auto_link_deliverable(self, deliverable) -> Optional[GoalProgress]
```

### SkillEvolutionService
**File:** `core/services/skill_evolution_service.py`

Infers skills from deliverables and tracks proficiency evolution.

```python
class SkillEvolutionService:
    # 50+ skill patterns mapped to categories
    SKILL_PATTERNS = {
        'python': ('Python', 'technical'),
        'writing': ('Writing', 'creative'),
        'analysis': ('Analysis', 'analytical'),
        ...
    }

    def infer_skills_from_deliverable(self, deliverable, min_confidence: float = 0.5) -> List[tuple]
    def record_skill_demonstration(self, user, skill_name: str, category: str, quality_score: float, ...) -> SkillDemonstration
    def update_skills_from_deliverable(self, user, deliverable, base_quality: float = 0.7) -> List[SkillDemonstration]
    def get_user_skills(self, user) -> List[Dict]
    def get_skill_growth_chart(self, user, months: int = 6) -> Dict[str, Any]
    def get_skill_recommendations(self, user) -> List[Dict]
    def get_skills_summary(self, user) -> Dict[str, Any]
```

---

## Part 6: API Endpoints Created (PR #837)

**File:** `core/views_user_learning_api.py`
**Base URL:** `/api/user-learning/`

### Agent Feedback Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/feedback/` | POST | Record agent feedback (👍/👎) |
| `/effectiveness/<agent_id>/` | GET | Get agent effectiveness for user |
| `/agent-summary/` | GET | Get summary of all agents for user |

### Profile Completeness Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/profile-completeness/` | GET | Get completeness score and gaps |
| `/profile-next-question/` | GET | Get next profile question to ask |
| `/profile-response/` | POST | Record user's profile response |

### Goal Tracking Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/goals/` | GET | Get goals dashboard |
| `/goals/<goal_id>/` | GET | Get goal detail with progress |
| `/goals/<goal_id>/progress/` | POST | Record manual goal progress |

### Skill Evolution Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/skills/` | GET | Get skills summary |
| `/skills/growth/` | GET | Get skill growth chart data |
| `/skills/demonstrate/` | POST | Record manual skill demonstration |
| `/skills/recommendations/` | GET | Get skill improvement recommendations |

### Combined Endpoint

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/summary/` | GET | Get combined learning summary |

---

## Part 7: Files Created/Modified

| Action | File | Purpose |
|--------|------|---------|
| ✅ CREATE | `core/models_user_learning.py` | 5 new models (326 lines) |
| ✅ CREATE | `core/migrations/0228_session_930_user_learning.py` | Migration (141 lines) |
| ✅ CREATE | `core/services/profile_completeness_service.py` | Gap detection service (339 lines) |
| ✅ CREATE | `core/services/agent_feedback_service.py` | Feedback service (350 lines) |
| ✅ CREATE | `core/services/goal_tracking_service.py` | Goal tracking service (399 lines) |
| ✅ CREATE | `core/services/skill_evolution_service.py` | Skill evolution service (473 lines) |
| ✅ CREATE | `core/views_user_learning_api.py` | API endpoints (660 lines) |
| ✅ MODIFY | `core/models.py` | Import new models |
| ✅ MODIFY | `core/urls.py` | Add 14 API routes |

**Total new code:** ~2,700 lines

---

## Part 8: Production Deployment

### Pull Requests Merged

| PR | Title | Status |
|----|-------|--------|
| #835 | docs(Session 930): User Context & Learning System handoff | ✅ Merged |
| #836 | feat(Session 930): Add User Learning System models | ✅ Merged |
| #837 | feat(Session 930): Add User Learning System services and API | ✅ Merged |

### Database Migration

```bash
# Migration 0228 applied to Railway production
railway run python manage.py migrate core 0228 --no-input
# Result: [X] core.0228_session_930_user_learning
```

---

## Part 9: Next Steps (Future Sessions)

### Frontend Components Needed

1. **Profile Completeness Widget** (Home page)
   - Progress bar showing completeness %
   - "Complete your profile" CTA
   - Guided questions flow

2. **Feedback Buttons** (Agent outputs)
   - 👍/👎 after deliverables
   - Optional text feedback
   - "This helped me with [goal]" linking

3. **Goal Progress Dashboard** (Workspace)
   - Goal cards with progress bars
   - Linked deliverables/initiatives
   - Milestone celebrations

4. **Skill Evolution Chart** (Profile page)
   - Skill levels over time
   - Recent demonstrations
   - Growth recommendations

### Integration Points (PR #840 - COMPLETED)

| Integration | Status | Location |
|-------------|--------|----------|
| **Auto-link deliverables to goals** | ✅ DONE | `DeliverableEnvelopeService._trigger_learning_from_deliverable()` |
| **Infer skills from deliverables** | ✅ DONE | `DeliverableEnvelopeService._trigger_learning_from_deliverable()` |
| **Adjust context per agent** | ✅ DONE | `AgentRouter._apply_agent_learning()` |
| **BaseAgent learning triggers** | ✅ DONE | `BaseAgent._trigger_deliverable_learning()` |
| **PA profile prompting** | ✅ DONE | See Part 10 below |

### Remaining Work (Future Sessions)

1. **Frontend Components** - Build React components to visualize learning data

---

## Part 10: PA Profile Interview (Session 931)

Personal Assistant now naturally prompts users to fill in missing profile information.

### Implementation Summary

| Component | File | Change |
|-----------|------|--------|
| Profile Context Method | `consumers_unified_v2.py:302-352` | `get_profile_context()` - fetches completeness % and suggested question |
| Context Injection | `consumers_unified_v2.py:156-180` | Injects profile section into system_context when gaps exist |
| Prompt Recording | `consumers_unified_v2.py:354-368` | `record_profile_prompt()` - tracks which questions were suggested |
| Agent Instructions | `personal_assistant_agent.py:478-493` | PROFILE AWARENESS section in system_prompt |

### How It Works

```
User Sends Message to PA
    │
    ▼
get_profile_context()
    ├─ ProfileCompletenessService.get_completeness_score()
    ├─ ProfileCompletenessService.get_next_question()
    └─ Returns: { completeness_percent, suggested_question, question_field }
    │
    ▼
Build System Context
    ├─ If completeness < 80% AND has_gaps:
    │   └─ Add USER PROFILE STATUS section with:
    │       - completeness percentage
    │       - suggested question to weave in naturally
    │       - prompting guidelines (don't force it, etc.)
    └─ If completeness >= 80%:
        └─ Note: "Profile well-filled, personalize responses"
    │
    ▼
LLM Generates Response (may naturally ask profile question)
    │
    ▼
record_profile_prompt()
    └─ Logs that this question was offered (prevents repeat prompts for 7 days)
```

### Profile Prompting Guidelines (in PA system prompt)

```
When natural and conversational, consider asking about missing profile information.
Suggested question to weave in naturally: "[dynamic question]"
- Only ask if it fits the conversation flow
- Don't force it if user is focused on a specific task
- Frame it as helping you serve them better
- If they answer, acknowledge and thank them
```

### Example Natural Prompts Generated

| Category | Example Question |
|----------|------------------|
| basic | "I'd like to get to know you better. What would you like me to call you?" |
| skills | "To better match opportunities to you, what are your key skills?" |
| career | "For career-related recommendations, what's your current job title?" |
| goals | "To help you achieve your objectives, what are you trying to accomplish this quarter?" |
| preferences | "To personalize your experience, how do you prefer to communicate?" |
| financial | "For financial insights, what are your investment goals?" |

### Files Modified

| File | Changes |
|------|---------|
| `core/consumers_unified_v2.py` | +66 lines: `get_profile_context()`, `record_profile_prompt()`, system_context injection |
| `core/agents/personal_assistant_agent.py` | +16 lines: PROFILE AWARENESS section in system_prompt |

---

## Success Metrics

| Metric | Current | Target | Notes |
|--------|---------|--------|-------|
| Profile completeness avg | Unknown | 70%+ | API available, need frontend |
| Feedback collection rate | 0% | 20%+ | API available, need frontend buttons |
| Goals with progress tracking | 0 | 50%+ | Auto-linking now active! |
| Skill demonstrations tracked | 0 → Auto | 100+/week | Auto-inference now integrated! |

---

## PRs Merged

| PR | Title | Status |
|----|-------|--------|
| #835 | docs(Session 930): User Context & Learning System handoff | ✅ Merged |
| #836 | feat(Session 930): Add User Learning System models | ✅ Merged |
| #837 | feat(Session 930): Add User Learning System services and API | ✅ Merged |
| #838 | docs(Session 930): Complete handoff with all implementation details | ✅ Merged |
| #839 | docs(Session 930): Update start file for Session 931 | ✅ Merged |
| #840 | feat(Session 930): Add auto-learning integration triggers | ✅ Merged |

---

**Session 930-931 Complete - User Learning System + PA Profile Interview!**
