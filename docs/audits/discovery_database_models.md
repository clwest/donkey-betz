# Agent 1.3: Database Models Discovery

**Date:** December 21, 2025
**Status:** Complete
**Total Models Discovered:** 200+ Django models

---

## Summary

Discovered **200+ database models** across 19 model files:
- `core/models_unified_system.py` - **140+ models** (main system)
- `core/models_legal.py` - 11 models (legal assistant)
- `content/models.py` - 23 models (content generation)
- Other specialized model files - 30+ models

---

## 1. Core Models by Domain

### User & Profile (core/models.py) - 12 Models
| Model | Purpose | FKs |
|-------|---------|-----|
| UnifiedBaseModel | Abstract base with timestamps | - |
| UserProfile | Basic user profile | User |
| UserPreferences | User preferences | User |
| EnhancedUserProfile | Extended profile with skills | User |
| UserMemoryContext | Memory for user context | User |
| ConversationMemory | Chat history | User |
| ChatConversation | Conversation threads | User |
| UserStatistics | Usage statistics | User |
| DiscordLinkCode | Discord account linking | User |
| ErrorPattern | Error pattern detection | - |
| ErrorInstance | Individual errors | ErrorPattern |
| AgentLearningSession | Agent learning sessions | User |
| AgentCollaboration | Agent collaborations | User |
| LearningInsight | Learning insights | - |

### Agent System (core/models_unified_system.py) - 30+ Models
| Model | Purpose | FKs |
|-------|---------|-----|
| AgentCategory | Agent categories | - |
| Agent | Core agent registry (149 agents) | Category |
| AgentSpiderConnection | Agent-spider mappings | Agent, Spider |
| AgentKnowledgeSource | Knowledge sources | Agent |
| AgentLearningConnection | Learning connections | Agent |
| KnowledgeTransfer | Knowledge sharing | Agent |
| AgentAssignment | User-agent assignments | User, Agent |
| AgentExecution | Execution logs | Agent |
| AgentPerformanceMetric | Performance metrics | Agent |
| AgentRole | Agent roles | - |
| AgentTeam | Agent teams | User |
| AgentTeamMembership | Team memberships | Agent, Team |
| AgentMessage | Agent-to-agent messages | Agent |
| AgentConversation | AI-to-AI conversations | Agent |
| ConversationMessage | Conversation messages | Conversation |
| ConversationArtifact | Artifacts from convos | Message |
| AgentDream | Agent dreams/thoughts | Agent |
| DreamImplementation | Dream implementations | Dream |
| AgentChannel | Discussion channels | Agent |
| ChannelMembership | Channel members | Channel, Agent |
| ChannelMessage | Channel messages | Channel, Agent |

### Advisor System (core/models_unified_system.py) - 5 Models
| Model | Purpose | FKs |
|-------|---------|-----|
| Advisor | Legendary advisors (25) | - |
| AdvisorInsight | Advisor insights | Advisor |
| AdvisorConsultationFeedback | Consultation feedback | Advisor, User |

### Spider Network (core/models_unified_system.py) - 10 Models
| Model | Purpose | FKs |
|-------|---------|-----|
| SpiderCategory | Spider categories | - |
| SpiderData | Raw spider data (20k+ records) | - |
| SpiderAnalytics | Spider performance | - |
| SpiderExecutionLog | Execution logs | - |
| TrendSnapshot | Trend snapshots | - |
| TrackSpiderMapping | Track-spider mapping | - |

### Opportunity & Revenue (core/models_unified_system.py) - 20+ Models
| Model | Purpose | FKs |
|-------|---------|-----|
| Opportunity | Core opportunity model | User |
| OpportunityScore | ML scoring | Opportunity |
| OpportunityAction | Actions taken | Opportunity |
| OpportunityRevenue | Revenue attribution | Opportunity |
| OpportunityContent | Generated content | Opportunity |
| OpportunityPredictionAccuracy | Prediction accuracy | Opportunity |
| OpportunityTask | Tasks | Opportunity |
| OpportunityOutcome | Outcomes | Opportunity |
| OpportunityDigest | Digests | User |
| Revenue | Revenue tracking | User |
| Application | Job applications | User, Opportunity |
| SavedOpportunity | Saved opportunities | User, Opportunity |

### ML Scoring System (core/models_unified_system.py) - 10 Models
| Model | Purpose | FKs |
|-------|---------|-----|
| MLModelVersion | Model versions | - |
| ScoringExplanation | SHAP explanations | - |
| ScoringConfiguration | Scoring configs | - |
| ScoringQueueItem | Queue items | - |
| ValidationRequest | HITL requests | - |
| ValidationDecision | HITL decisions | ValidationRequest |
| ValidationConfig | HITL config | - |

### Workflow System (core/models_unified_system.py) - 12 Models
| Model | Purpose | FKs |
|-------|---------|-----|
| CustomWorkflow | Custom workflows | User |
| CustomWorkflowStep | Workflow steps | Workflow |
| WorkflowExecution | Execution logs | Workflow |
| ScheduledWorkflow | Scheduled runs | Workflow |
| PublishedWorkflow | Published workflows | Workflow |
| WorkflowReview | Reviews | PublishedWorkflow |
| WorkflowInstallation | Installations | PublishedWorkflow |
| TeamWorkflow | Team workflows | Team |
| TeamWorkflowStep | Team workflow steps | TeamWorkflow |

### A/B Testing (core/models_unified_system.py) - 6 Models
| Model | Purpose | FKs |
|-------|---------|-----|
| ABExperiment | Experiments | User |
| ABVariant | Variants | Experiment |
| ABAssignment | User assignments | Variant |
| ABConversion | Conversions | Variant |
| ABExperimentResult | Results | Experiment |
| ABTest | Tests | - |
| ABTestVariant | Test variants | ABTest |
| ABTestEvent | Test events | ABTest |

### Sci-Fi Features (core/models_unified_system.py) - 25+ Models

#### Memory System
| Model | Purpose |
|-------|---------|
| MemoryConnection | Memory connections |
| MemoryPalaceRoom | Memory rooms |
| MemoryCluster | Memory clusters |
| MemoryClusterMembership | Cluster members |
| ClusterEvolution | Cluster evolution |

#### Mood System
| Model | Purpose |
|-------|---------|
| AgentMood | Current mood |
| MoodHistory | Mood history |
| MoodTriggerRule | Mood triggers |

#### Evolution System
| Model | Purpose |
|-------|---------|
| AgentEvolution | XP and levels |
| AgentAbility | Unlocked abilities |
| XPHistory | XP history |
| LevelMilestone | Level milestones |

#### Relationships
| Model | Purpose |
|-------|---------|
| AgentRelationship | Agent relationships |
| RelationshipEvent | Relationship events |
| Alliance | Alliances |
| Rivalry | Rivalries |

#### Time Travel Debugging
| Model | Purpose |
|-------|---------|
| AgentSession | Debug sessions |
| DecisionPoint | Decision points |
| ThoughtBubble | Thoughts |
| ReplayBookmark | Bookmarks |
| DebugAnnotation | Annotations |

#### Predictions & Time Capsules
| Model | Purpose |
|-------|---------|
| AgentPrediction | Predictions |
| PredictionStats | Prediction stats |
| PredictionComment | Comments |
| PredictionFollowUp | Follow-ups |
| TimeCapsule | Time capsules |
| TimeCapsuleReaction | Reactions |
| TimeCapsuleStats | Stats |

### Distribution System (core/models_unified_system.py) - 10 Models
| Model | Purpose |
|-------|---------|
| DistributionPlatform | Platforms (Gumroad, etc) |
| UserPlatformAccount | User accounts |
| ContentDistribution | Distribution records |
| DistributionRecommendation | Recommendations |
| DistributionAnalytics | Analytics |
| SuccessPattern | Success patterns |
| ContentPerformancePrediction | Predictions |
| PricingOptimization | Pricing optimization |
| DistributionInsight | Insights |

### Proactive System (core/models_unified_system.py) - 8 Models
| Model | Purpose |
|-------|---------|
| ProactiveAlert | Alerts |
| ProactiveNotification | Notifications |
| SmartSuggestion | Suggestions |
| AutomatedAction | Automated actions |
| AutomatedActionLog | Action logs |
| UserNotificationPreference | Notification prefs |
| UserGoal | User goals |

### Analytics (core/models_unified_system.py) - 8 Models
| Model | Purpose |
|-------|---------|
| UsageMetric | Usage metrics |
| PerformanceLog | Performance logs |
| CostTracking | Cost tracking |
| AnalyticsDashboard | Dashboards |
| AnalyticsAlert | Alerts |
| UserLearningProfile | Learning profiles |
| PerformanceComparison | Comparisons |

---

## 2. Specialized Model Files

### Legal Assistant (core/models_legal.py) - 11 Models
| Model | Purpose | FKs |
|-------|---------|-----|
| CaseProfile | Case information | User |
| Party | Case parties | CaseProfile |
| Attorney | Attorneys | CaseProfile |
| Child | Children | CaseProfile |
| CaseDocument | Documents | CaseProfile |
| LitigationDocument | Litigation docs | CaseProfile |
| CaseKnowledgeGraph | Knowledge graph | CaseProfile |
| DocumentRelationship | Doc relationships | Document |
| GeneratedResponse | AI responses | CaseProfile |
| ExhibitList | Exhibit lists | CaseProfile |
| CaseMemorandum | Memorandums | CaseProfile |

### Voice Marketplace (core/models_voice_marketplace.py) - 4 Models
| Model | Purpose |
|-------|---------|
| VoiceProfile | Voice profiles |
| VoiceTransaction | Transactions |
| VoiceReview | Reviews |
| VoiceCloneRequest | Clone requests |

### AI Series (core/models_ai_series.py) - 3 Models
| Model | Purpose |
|-------|---------|
| AISeries | Content series |
| SeriesEpisode | Episodes |
| SeriesCharacter | Characters |

### Narrative Drift (core/models_narrative_drift.py) - 4 Models
| Model | Purpose |
|-------|---------|
| Narrative | Narratives |
| NarrativeShift | Shifts |
| NarrativeEvidence | Evidence |
| NarrativeAlert | Alerts |

### Content Pipeline (core/models_content_pipeline.py) - 5 Models
| Model | Purpose |
|-------|---------|
| ContentPackage | Packages |
| ContentAsset | Assets |
| ContentPurchase | Purchases |
| ContentShowroom | Showrooms |
| ContentGenerationJob | Generation jobs |

### Podcast Studio (core/models_podcast_studio.py) - 4 Models
| Model | Purpose |
|-------|---------|
| PodcastShow | Shows |
| PodcastDebate | Debates |
| PodcastEpisode | Episodes |
| PodcastParticipant | Participants |

### Autonomous Studio (core/models_autonomous_studio.py) - 4 Models
| Model | Purpose |
|-------|---------|
| ContentChannel | Channels |
| ChannelEpisode | Episodes |
| TopicPerformance | Topic stats |
| ContentDebate | Debates |

### Autonomous Situations (core/models_autonomous_situations.py) - 10+ Models
| Model | Purpose |
|-------|---------|
| DesignTrend | Design trends |
| DesignSystemUpdate | System updates |
| ViralContentPrediction | Viral predictions |
| ThumbnailVariant | Thumbnail variants |
| JobMatchProfile | Job matching |
| JobMatch | Job matches |
| FreelanceOpportunity | Freelance opps |
| SideHustle | Side hustles |
| SECFilingAnalysis | SEC analysis |
| CryptoSentiment | Crypto sentiment |
| EarningsPrediction | Earnings predictions |
| TechStackTrend | Tech trends |

### Campaign (core/models_campaign.py) - 3 Models
| Model | Purpose |
|-------|---------|
| Campaign | Marketing campaigns |
| CampaignDeliverable | Deliverables |
| CampaignResearch | Research |

### Engagement (core/models_engagement_metrics.py) - 2 Models
| Model | Purpose |
|-------|---------|
| EngagementMetrics | Engagement data |
| OpportunityInteraction | Interactions |

### Pipeline Feedback (core/models_pipeline_feedback.py) - 6 Models
| Model | Purpose |
|-------|---------|
| PipelineStageFeedback | Stage feedback |
| StylePresetPerformance | Style performance |
| VoicePerformance | Voice performance |
| ContentEngagement | Engagement |
| ResearchQueryPerformance | Query performance |
| PipelineLearningInsight | Insights |

### Situation Triggers (core/models_situation_triggers.py) - 2 Models
| Model | Purpose |
|-------|---------|
| SituationTrigger | Triggers |
| TriggerEvent | Events |

---

## 3. Content Models (content/models.py) - 23 Models

| Model | Purpose |
|-------|---------|
| ContentTemplate | Templates |
| Document | Documents |
| DocumentEmbedding | Embeddings |
| KnowledgeBase | Knowledge bases |
| ContentGeneration | Generation records |
| ContentWorkflow | Workflows |
| WorkflowExecution | Executions |
| ContentAnalytics | Analytics |
| Feedback | User feedback |
| ImageHistory | Image history |
| VideoHistory | Video history |
| AudioHistory | Audio history |
| MiniFigAsset | 3D assets |
| WorkflowHistory | Workflow history |
| WorkflowFavorite | Favorites |
| _DeprecatedCreativeProject | Deprecated projects |
| ProjectWorkflow | Project workflows |
| CharacterModel | Character models |
| CharacterTrainingImage | Training images |
| UserCreativePreference | Creative prefs |
| AISession | AI sessions |
| ProjectShare | Project shares |
| UploadSession | Upload sessions |

---

## 4. Model Count Summary

| Category | Count |
|----------|-------|
| User & Profile | 14 |
| Agent System | 30+ |
| Advisor System | 5 |
| Spider Network | 10 |
| Opportunity & Revenue | 20+ |
| ML Scoring | 10 |
| Workflow System | 12 |
| A/B Testing | 8 |
| Sci-Fi Features | 25+ |
| Distribution | 10 |
| Proactive System | 8 |
| Analytics | 8 |
| Legal Assistant | 11 |
| Voice Marketplace | 4 |
| AI Series | 3 |
| Narrative Drift | 4 |
| Content Pipeline | 5 |
| Podcast Studio | 4 |
| Autonomous Studio | 4 |
| Autonomous Situations | 12 |
| Campaign | 3 |
| Engagement | 2 |
| Pipeline Feedback | 6 |
| Situation Triggers | 2 |
| Content Models | 23 |
| **TOTAL** | **~230** |

---

## 5. Potential Orphaned Models

Models that may have limited or no active usage:

| Model | File | Concern |
|-------|------|---------|
| _DeprecatedCreativeProject | content/models.py | Explicitly deprecated |
| ErrorPattern/ErrorInstance | core/models.py | May be legacy |
| LearningInsight | core/models.py | Check if active |
| AgentLearningSession | core/models.py | Check if active |
| AgentCollaboration | core/models.py | May be superseded |

---

## 6. Duplicate/Overlapping Models

| Models | Files | Issue |
|--------|-------|-------|
| UserProfile | models.py, models_profile.py | Duplicate definitions |
| EnhancedUserProfile | models.py, models_user_profile_enhanced.py | Duplicate |
| UserMemoryContext | models.py, models_user_profile_enhanced.py | Duplicate |
| AgentDecisionSummary | models_unified_system.py | Defined twice! |

---

## 7. Key Relationships

### Core Entity Relationships
```
User
  └── UserProfile
  └── UserPreferences
  └── EnhancedUserProfile
  └── Opportunity (many)
  └── Application (many)
  └── Revenue (many)
  └── Project (many)
  └── CaseProfile (legal)

Agent
  └── AgentCategory
  └── AgentSpiderConnection
  └── AgentKnowledgeSource
  └── AgentExecution
  └── AgentEvolution
  └── AgentMood
  └── AgentDream
  └── AgentConversation

Opportunity
  └── OpportunityScore
  └── OpportunityAction
  └── OpportunityRevenue
  └── Application

SpiderData
  └── SpiderAnalytics
  └── SpiderExecutionLog
```

---

## 8. Gaps Identified

### P0 - Critical
1. **Duplicate model definitions** - UserProfile, EnhancedUserProfile defined twice
2. **AgentDecisionSummary defined twice** in models_unified_system.py

### P1 - High
3. **Verify orphaned models** - _DeprecatedCreativeProject still in use?
4. **Clean up legacy models** - ErrorPattern, ErrorInstance

### P2 - Medium
5. **Consolidate user profile models** - 3+ profile-related files
6. **Document FK relationships** - Some missing reverse relations

---

*Generated by Agent 1.3: Database Models Discovery*
