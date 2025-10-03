# Django Model Validation Report

Models checked: 123


## ❌ Critical Violations


### Boolean Naming
Found 40 violations:

- accounts.User.telegram_notifications -> should start with 'is_'
- agent_orchestra.AgentCommunication.acknowledged -> should start with 'is_'
- agent_orchestra.AgentInstance.telegram_notified -> should start with 'is_'
- agent_orchestra.AgentLearning.success -> should start with 'is_'
- agent_orchestra.AgentMessage.requires_response -> should start with 'is_'
- agent_orchestra.AgentTemplate.requires_approval -> should start with 'is_'
- agent_orchestra.AgentTool.requires_approval -> should start with 'is_'
- agent_orchestra.RegulatoryDocumentEmbedding.significant -> should start with 'is_'
- agent_orchestra.TaskOrchestration.email_requested -> should start with 'is_'
- agent_orchestra.TaskOrchestration.email_sent -> should start with 'is_'
- ... and 30 more


### Deprecated Field
Found 6 violations:

- core.MovementGoal.end_date
- core.MovementGoal.start_date
- movement.DetectedWorkout.end_time
- movement.DetectedWorkout.start_time
- movement.MovementSession.end_time
- movement.MovementSession.start_time


### Missing Created At
Found 29 violations:

- accounts.User
- accounts.UserManager
- agent_orchestra.BillComparisonEmbedding
- agent_orchestra.DeletedRedditIdea
- agent_orchestra.HistoricalLegislativePattern
- agent_orchestra.RedditIdea
- agent_orchestra.TaskOrchestration
- ai_evolution.EvolutionMetrics
- ai_partner.ConversationSegment
- ai_partner.ConversationTopic
- ... and 19 more


### Non Standard Timestamp
Found 26 violations:

- accounts.User.date_joined
- agent_orchestra.BusinessImpactAnalysis.effective_date
- agent_orchestra.GovernmentContractEmbedding.due_date
- agent_orchestra.GovernmentContractEmbedding.posted_date
- agent_orchestra.LegislativeBillEmbedding.introduced_date
- agent_orchestra.LegislativeBillEmbedding.last_action_date
- agent_orchestra.RegulatoryDocumentEmbedding.comment_due_date
- agent_orchestra.RegulatoryDocumentEmbedding.effective_date
- agent_orchestra.RegulatoryDocumentEmbedding.publication_date
- ai_evolution.EvolutionMetrics.timestamp
- ... and 16 more


## ⚠️  Warnings


### Abbreviation
Found 32 warnings:

- agent_orchestra.AgentResult.description -> consider using 'description'
- agent_orchestra.AgentTemplate.description -> consider using 'description'
- agent_orchestra.AgentTool.description -> consider using 'description'
- agent_orchestra.AgentWorkspace.description -> consider using 'description'
- agent_orchestra.BusinessImpactAnalysis.description -> consider using 'description'
- agent_orchestra.GovernmentContractEmbedding.description -> consider using 'description'
- agent_orchestra.GovernmentContractEmbedding.description_embedding -> consider using 'description'
- agent_orchestra.HistoricalLegislativePattern.description -> consider using 'description'
- agent_orchestra.RegulatoryDocumentEmbedding.document_number -> consider using 'number'
- agent_orchestra.ResearchCollection.description -> consider using 'description'
- ... and 22 more


### Missing Updated At
Found 96 warnings:

- accounts.User
- accounts.UserManager
- agent_orchestra.AgentCommunication
- agent_orchestra.AgentInstance
- agent_orchestra.AgentLearning
- agent_orchestra.AgentMessage
- agent_orchestra.AgentResult
- agent_orchestra.BillComparisonEmbedding
- agent_orchestra.DeletedRedditIdea
- agent_orchestra.GovernmentContractEmbedding
- ... and 86 more


## Summary

- Total violations: 101
- Total warnings: 128

❌ Found 101 violations that need to be fixed