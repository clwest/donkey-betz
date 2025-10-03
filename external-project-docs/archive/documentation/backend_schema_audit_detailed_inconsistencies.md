# Detailed Field Naming Inconsistencies Report

## Executive Summary

- **Total Models Analyzed**: 122
- **Total Apps**: 16

### Key Findings

- **25 models** missing standard `created_at` field
- **92 models** missing standard `updated_at` field
- **22 different patterns** for user references
- **97 boolean fields** with 3 naming patterns

## Timestamp Field Analysis

### Models Missing Standard Timestamps

### Non-Standard Timestamp Fields

- **completed_at**: 6 models
- **started_at**: 5 models
- **last_used**: 5 models
- **timestamp**: 4 models
- **date**: 4 models
- **ended_at**: 3 models
  - ai_partner.ConversationSegment
  - learning_intelligence.LearningSession
  - walking_companion.WalkingSession
- **read_at**: 2 models
  - agent_orchestra.AgentCommunication
  - agent_orchestra.AgentMessage
- **reviewed_at**: 2 models
  - agent_orchestra.RedditIdea
  - learning_intelligence.AnchorSuggestion
- **effective_date**: 2 models
  - agent_orchestra.RegulatoryDocumentEmbedding
  - agent_orchestra.BusinessImpactAnalysis
- **last_updated**: 2 models
  - ai_partner.UserLifeProfile
  - ml_models.MLUserModel
- **last_discussed**: 2 models
  - ai_partner.LifeGoalTracking
  - ai_partner.StartupIdeaIncubator
- **start_time**: 2 models
  - movement.MovementSession
  - movement.DetectedWorkout
- **end_time**: 2 models
  - movement.MovementSession
  - movement.DetectedWorkout
- **acknowledged_at**: 2 models
  - mythology_lab.MythologyAlert
  - walking_companion.BreakReminder
- **date_joined**: 1 models
  - accounts.User
- **email_sent_at**: 1 models
  - agent_orchestra.TaskOrchestration
- **archived_at**: 1 models
  - agent_orchestra.TaskOrchestration
- **estimated_completion**: 1 models
  - agent_orchestra.AgentInstance
- **actual_completion**: 1 models
  - agent_orchestra.AgentInstance
- **discovered_at**: 1 models
  - agent_orchestra.RedditIdea

## User Reference Patterns

### Pattern: `user (ForeignKey)`
- Used in 55 models

### Pattern: `user (OneToOneField)`
- Used in 6 models

### Pattern: `created_by (ForeignKey)`
- Used in 4 models
  - images.PromptHelper
  - images.ThemeHelper
  - ml_models.MLModelVersion
  - shame.Herd

### Pattern: `user_satisfaction (IntegerField)`
- Used in 3 models
  - agent_orchestra.TaskOrchestration
  - ai_partner.RAGPerformanceMetrics
  - learning_intelligence.LearningSession

### Pattern: `user_feedback (TextField)`
- Used in 2 models
  - agent_orchestra.TaskOrchestration
  - ai_partner.ConversationMemory

### Pattern: `username (CharField)`
- Used in 1 models
  - accounts.User

### Pattern: `telegram_username (CharField)`
- Used in 1 models
  - accounts.User

### Pattern: `user_context (JSONField)`
- Used in 1 models
  - agent_orchestra.AgentInstance

### Pattern: `user_notes (TextField)`
- Used in 1 models
  - agent_orchestra.RedditIdea

### Pattern: `avg_user_satisfaction (FloatField)`
- Used in 1 models
  - ai_evolution.EvolutionExperiment

### Pattern: `user_mood (CharField)`
- Used in 1 models
  - ai_partner.ConversationMemory

### Pattern: `is_user_message (BooleanField)`
- Used in 1 models
  - ai_partner.ConversationMemory

### Pattern: `user_skills_match (JSONField)`
- Used in 1 models
  - ai_partner.StartupIdeaIncubator

### Pattern: `user_acknowledged (BooleanField)`
- Used in 1 models
  - ai_partner.PersonalInsight

### Pattern: `favorited_by (ManyToManyField)`
- Used in 1 models
  - images.PromptHelper

### Pattern: `reinforced_by (ManyToManyField)`
- Used in 1 models
  - learning_intelligence.SymbolicMemoryAnchor

### Pattern: `reinforcing_user (ForeignKey)`
- Used in 1 models
  - learning_intelligence.AnchorReinforcementLog

### Pattern: `submitted_by (ForeignKey)`
- Used in 1 models
  - memory.MemoryFeedback

### Pattern: `members (ManyToManyField)`
- Used in 1 models
  - shame.Herd

### Pattern: `likes (ManyToManyField)`
- Used in 1 models
  - shame.HerdPost

### Pattern: `max_concurrent_users (IntegerField)`
- Used in 1 models
  - universal_builder.StackPattern

### Pattern: `notified_friends (ManyToManyField)`
- Used in 1 models
  - walking_companion.BreakReminder

### Models with Multiple User References

- **accounts.User**:
  - `username` -> 
  - `telegram_username` -> 
- **agent_orchestra.TaskOrchestration**:
  - `user` -> User
  - `user_satisfaction` -> 
  - `user_feedback` -> 
- **agent_orchestra.AgentInstance**:
  - `user` -> User
  - `user_context` -> 
- **agent_orchestra.RedditIdea**:
  - `user` -> User
  - `user_notes` -> 
- **ai_partner.ConversationMemory**:
  - `user` -> User
  - `user_mood` -> 
  - `is_user_message` -> 
  - `user_feedback` -> 
- **ai_partner.StartupIdeaIncubator**:
  - `user` -> User
  - `user_skills_match` -> 
- **ai_partner.PersonalInsight**:
  - `user` -> User
  - `user_acknowledged` -> 
- **ai_partner.RAGPerformanceMetrics**:
  - `user` -> User
  - `user_satisfaction` -> 
- **images.PromptHelper**:
  - `favorited_by` -> settings.AUTH_USER_MODEL
  - `created_by` -> settings.AUTH_USER_MODEL
- **learning_intelligence.SymbolicMemoryAnchor**:
  - `user` -> User
  - `reinforced_by` -> User
- **learning_intelligence.LearningSession**:
  - `user` -> User
  - `user_satisfaction` -> 
- **shame.Herd**:
  - `created_by` -> User
  - `members` -> User
- **shame.HerdPost**:
  - `user` -> User
  - `likes` -> User
- **walking_companion.BreakReminder**:
  - `user` -> User
  - `notified_friends` -> User

## Boolean Field Naming

### Naming Convention Distribution

- **is_**: 57 fields (58.8%)
- **other**: 36 fields (37.1%)
- **_enabled**: 4 fields (4.1%)

### Non-Standard Boolean Names

- accounts.User.telegram_notifications
- agent_orchestra.AgentTemplate.requires_approval
- agent_orchestra.TaskOrchestration.email_requested
- agent_orchestra.TaskOrchestration.email_sent
- agent_orchestra.TaskOrchestration.telegram_notified
- agent_orchestra.TaskOrchestration.saved_to_memory
- agent_orchestra.AgentInstance.telegram_notified
- agent_orchestra.AgentTool.requires_approval
- agent_orchestra.AgentCommunication.acknowledged
- agent_orchestra.AgentLearning.success
- agent_orchestra.AgentMessage.requires_response
- agent_orchestra.RegulatoryDocumentEmbedding.significant
- ai_evolution.EvolutionSession.converged
- ai_evolution.UserEvolutionPreferences.enable_evolution
- ai_evolution.UserEvolutionPreferences.auto_evolve_responses
- ai_evolution.EvolutionFeedback.was_helpful
- ai_evolution.EvolutionFeedback.would_use_again
- ai_evolution.EvolutionFeedback.task_completed
- ai_partner.UserLifeProfile.allow_ai_learning
- ai_partner.PersonalInsight.user_acknowledged

## Similar Fields with Different Names

### Concept: updated_at

Total usage across variations: 29 models

- **updated_at**: 27 models
- **last_updated**: 2 models
  - ai_partner.UserLifeProfile
  - ml_models.MLUserModel

### Concept: is_active

Total usage across variations: 15 models

- **is_active**: 14 models
- **is_enabled**: 1 models
  - images.PromptPlacement

### Concept: deleted_at

Total usage across variations: 3 models

- **deleted_at**: 1 models
  - agent_orchestra.DeletedRedditIdea
- **archived_at**: 1 models
  - agent_orchestra.TaskOrchestration
- **is_archived**: 1 models
  - agent_orchestra.TaskOrchestration

### Concept: user

Total usage across variations: 65 models

- **user**: 61 models
- **created_by**: 4 models
  - images.PromptHelper
  - images.ThemeHelper
  - ml_models.MLModelVersion
  - shame.Herd

### Concept: start_time

Total usage across variations: 8 models

- **started_at**: 5 models
  - agent_orchestra.TaskOrchestration
  - ai_evolution.EvolutionExperiment
  - ai_partner.ConversationSegment
  - learning_intelligence.LearningSession
  - walking_companion.WalkingSession
- **start_time**: 2 models
  - movement.MovementSession
  - movement.DetectedWorkout
- **start_date**: 1 models
  - core.MovementGoal

### Concept: end_time

Total usage across variations: 12 models

- **completed_at**: 6 models
- **ended_at**: 3 models
  - ai_partner.ConversationSegment
  - learning_intelligence.LearningSession
  - walking_companion.WalkingSession
- **end_time**: 2 models
  - movement.MovementSession
  - movement.DetectedWorkout
- **end_date**: 1 models
  - core.MovementGoal

