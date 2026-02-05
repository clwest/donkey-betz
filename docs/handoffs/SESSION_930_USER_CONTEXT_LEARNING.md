# Session 930 - User Context Injection & Learning System

**Date:** February 4, 2026
**Focus:** How user context flows to agents + How system learns from user interactions

---

## Overview

This session addresses two fundamental questions:
1. **How does the User get injected into context?**
2. **How does the system start learning from the User?**

---

## Part 1: Current User Context System

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

## Part 2: Current Learning Mechanisms

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

### Engagement Depth Tracking

| Action | Depth Score | Learning Signal |
|--------|-------------|-----------------|
| View | 1 | Weak interest |
| Click | 2 | Moderate interest |
| Bookmark | 3 | Strong interest |
| Apply | 4 | Intent to act |
| Interview | 5 | Serious commitment |
| Accept | 6 | Conversion |

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

## Part 3: Identified Gaps

### Gap Analysis

| Gap | Current State | Impact | Priority |
|-----|--------------|--------|----------|
| **User Skill Evolution** | Skills stored statically | No tracking of improvement over time | HIGH |
| **Agent-Specific Learning** | Learning is global | No per-agent profiles of what works | HIGH |
| **Conversion Metrics** | Basic engagement tracking | Can't measure which personalization converts | MEDIUM |
| **Goal Progress Tracking** | Goals stored, no progress | User can't see progress toward goals | HIGH |
| **Active Feedback Loop** | Passive learning only | System never asks user directly | HIGH |
| **Profile Completeness UX** | No prompting | User doesn't know what to fill in | MEDIUM |

---

## Part 4: Implementation Plan

### A. Profile Completeness & Active Prompting

**Goal:** PA proactively asks user about missing profile fields

**New Components:**
1. `ProfileCompletenessService` - Identifies gaps in user profiles
2. PA integration - Prompts user naturally during conversations

**Implementation:**
```python
# core/services/profile_completeness_service.py
class ProfileCompletenessService:
    REQUIRED_FIELDS = {
        'basic': ['display_name', 'skills', 'occupation'],
        'career': ['desired_salary', 'remote_preference', 'industries'],
        'goals': ['long_term_goals', 'quarterly_objectives'],
        'preferences': ['communication_style', 'risk_tolerance']
    }

    def get_profile_gaps(self, user) -> dict:
        """Returns missing fields by category"""

    def get_next_question(self, user) -> str:
        """Returns natural language question for highest-priority gap"""

    def get_completeness_score(self, user) -> float:
        """Returns 0-1 completeness score"""
```

### B. Feedback After Agent Execution

**Goal:** Collect 👍/👎 feedback after key outputs to learn per-agent preferences

**New Components:**
1. `AgentFeedback` model - Stores user feedback per agent execution
2. Frontend feedback UI - Simple thumbs up/down
3. `AgentLearningService` - Aggregates feedback into learning patterns

**Implementation:**
```python
# core/models_agent_feedback.py
class AgentFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    execution_id = models.UUIDField()  # Link to AgentExecution
    rating = models.IntegerField(choices=[(1, 'helpful'), (-1, 'not_helpful')])
    feedback_text = models.TextField(blank=True)
    context_snapshot = models.JSONField()  # What context was used
    created_at = models.DateTimeField(auto_now_add=True)

# core/services/agent_learning_service.py
class AgentLearningService:
    def record_feedback(self, user, agent, execution_id, rating, text=None):
        """Store feedback and update agent-specific learning"""

    def get_agent_effectiveness(self, user, agent) -> dict:
        """Get success rate and patterns for user+agent combo"""

    def adjust_context_for_agent(self, user, agent, base_context) -> dict:
        """Modify context based on what works for this user+agent"""
```

### C. Goal Progress Tracking

**Goal:** Link user goals to deliverables/initiatives and show progress

**New Components:**
1. `GoalProgress` model - Tracks progress toward goals
2. Goal-Deliverable linking - Connect outputs to goals
3. Progress dashboard widget

**Implementation:**
```python
# core/models_goal_tracking.py
class UserGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_date = models.DateField(null=True)
    category = models.CharField(max_length=50)  # career, financial, learning, etc.
    success_criteria = models.JSONField()  # Measurable criteria
    status = models.CharField(max_length=20)  # active, achieved, abandoned

class GoalProgress(models.Model):
    goal = models.ForeignKey(UserGoal, on_delete=models.CASCADE, related_name='progress_entries')
    deliverable = models.ForeignKey('Deliverable', null=True, on_delete=models.SET_NULL)
    initiative = models.ForeignKey('Initiative', null=True, on_delete=models.SET_NULL)
    progress_percentage = models.IntegerField()
    milestone_reached = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# core/services/goal_tracking_service.py
class GoalTrackingService:
    def link_deliverable_to_goal(self, deliverable, goal):
        """Connect a deliverable to a goal and calculate progress"""

    def calculate_progress(self, goal) -> int:
        """Calculate overall progress percentage"""

    def get_user_goal_summary(self, user) -> dict:
        """Get all goals with progress for dashboard"""
```

### D. Skill Evolution Tracking

**Goal:** Track how user skills improve based on successful outputs

**New Components:**
1. `SkillEvolution` model - Tracks skill levels over time
2. Skill inference from deliverables
3. Skill growth visualization

**Implementation:**
```python
# core/models_skill_evolution.py
class UserSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill_name = models.CharField(max_length=100)
    proficiency_level = models.IntegerField()  # 1-10
    evidence_count = models.IntegerField(default=0)  # Number of demonstrations
    last_demonstrated = models.DateTimeField()

class SkillDemonstration(models.Model):
    skill = models.ForeignKey(UserSkill, on_delete=models.CASCADE)
    deliverable = models.ForeignKey('Deliverable', null=True, on_delete=models.SET_NULL)
    quality_score = models.FloatField()  # From content quality assessment
    context = models.TextField()  # How skill was demonstrated
    created_at = models.DateTimeField(auto_now_add=True)

# core/services/skill_evolution_service.py
class SkillEvolutionService:
    def infer_skills_from_deliverable(self, deliverable) -> List[str]:
        """Extract skills demonstrated in a deliverable"""

    def update_user_skills(self, user, skills, quality_score):
        """Update skill proficiency based on new demonstration"""

    def get_skill_growth_chart(self, user) -> dict:
        """Get skill levels over time for visualization"""
```

---

## Part 5: Database Migrations

### New Models to Create

```python
# Migration: 0228_session_930_user_learning_system.py

# 1. AgentFeedback - Per-agent user feedback
# 2. UserGoal - User goals with criteria
# 3. GoalProgress - Progress tracking
# 4. UserSkill - Skill proficiency levels
# 5. SkillDemonstration - Evidence of skills
```

### Profile Updates

```python
# Add to EnhancedUserProfile
profile_completeness = models.FloatField(default=0.0)
last_completeness_prompt = models.DateTimeField(null=True)
prompt_preferences = models.JSONField(default=dict)  # When/how to prompt
```

---

## Part 6: Frontend Components

### New UI Elements

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

---

## Part 7: Implementation Order

### Phase 1: Foundation (This Session)
1. ✅ Document current state (complete)
2. Create new models (AgentFeedback, UserGoal, GoalProgress, UserSkill)
3. Create migrations
4. Create base services

### Phase 2: Profile Completeness
1. ProfileCompletenessService
2. PA integration for prompting
3. Frontend completeness widget

### Phase 3: Agent Feedback Loop
1. AgentFeedback model active
2. Frontend feedback buttons
3. AgentLearningService
4. Context adjustment based on feedback

### Phase 4: Goal Tracking
1. Goal creation UI
2. Deliverable-goal linking
3. Progress calculation
4. Dashboard widget

### Phase 5: Skill Evolution
1. Skill inference from deliverables
2. Proficiency tracking
3. Growth visualization

---

## Files to Create/Modify

| Action | File | Purpose |
|--------|------|---------|
| CREATE | `core/models_user_learning.py` | AgentFeedback, UserGoal, GoalProgress, UserSkill, SkillDemonstration |
| CREATE | `core/services/profile_completeness_service.py` | Gap detection and prompting |
| CREATE | `core/services/agent_learning_service.py` | Per-agent feedback aggregation |
| CREATE | `core/services/goal_tracking_service.py` | Goal progress calculation |
| CREATE | `core/services/skill_evolution_service.py` | Skill inference and tracking |
| CREATE | `core/migrations/0228_session_930_user_learning.py` | New models migration |
| MODIFY | `core/agent_router.py` | Integrate agent-specific learning |
| MODIFY | `core/models.py` | Add profile_completeness to EnhancedUserProfile |
| CREATE | `frontend/src/components/ProfileCompleteness.tsx` | Completeness widget |
| CREATE | `frontend/src/components/AgentFeedback.tsx` | Feedback buttons |
| CREATE | `frontend/src/components/GoalProgress.tsx` | Goal dashboard |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Profile completeness avg | Unknown | 70%+ |
| Feedback collection rate | 0% | 20%+ of executions |
| Goals with progress tracking | 0 | 50%+ of users have goals |
| Skill demonstrations tracked | 0 | 100+ per week |

---

**Session 930 Ready - Let's implement the User Learning System!**
