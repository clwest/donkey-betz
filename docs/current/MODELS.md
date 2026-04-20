<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`../PLATFORM_WHAT_IT_IS.md`](/docs/PLATFORM_WHAT_IT_IS.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

# Database Models Documentation

**Total Models:** 324+
**Categories:** 37
**Main Location:** `core/models_unified_system.py` (10,000+ lines)
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Model Categories](#model-categories)
3. [Key Models Detail](#key-models-detail)
4. [Relationships](#relationships)

---

## Overview

The database schema consists of 324+ models organized into 37 categories, covering everything from agents and spiders to autonomous situations and governance.

### Model Locations

| File | Purpose | Line Count |
|------|---------|------------|
| `core/models_unified_system.py` | Main models | 10,000+ |
| `core/models_legal.py` | Legal assistant | ~500 |
| `core/models_autonomous_studio.py` | Content studio | ~650 |
| `core/models_autonomous_situations.py` | Situations | ~400 |
| `core/models_situation_triggers.py` | Event triggers | ~300 |
| `content/models.py` | Content/media | ~800 |

---

## Model Categories

### 1. Agent Models (15)

| Model | Purpose |
|-------|---------|
| `Agent` | Agent configuration and metadata |
| `AgentExecution` | Execution history |
| `AgentLearning` | Learning records |
| `AgentKnowledge` | Stored knowledge |
| `AgentKnowledgeSource` | Knowledge sources |
| `AgentMemory` | Memory entries |
| `AgentMood` | Current mood state |
| `AgentRelationship` | Agent relationships |
| `AgentEvolution` | XP and level |
| `AgentDream` | Dream entries |
| `AgentConversation` | Conversation records |
| `AgentConversationMessage` | Conversation messages |
| `AgentPersonality` | Personality traits |
| `AgentTimeCapsule` | Time capsules |
| `AgentActivity` | Activity log |

### 2. Spider Models (8)

| Model | Purpose |
|-------|---------|
| `SpiderData` | Collected spider data |
| `SpiderExecution` | Execution history |
| `SpiderExecutionLog` | Detailed logs |
| `SpiderConfig` | Spider configuration |
| `SpiderSchedule` | Scheduling config |
| `SpiderHealth` | Health metrics |
| `SpiderDataEmbedding` | Vector embeddings |
| `SpiderBridgeSignal` | Knowledge bridge |

### 3. Content Models (12)

| Model | Purpose |
|-------|---------|
| `GeneratedImage` | AI-generated images |
| `GeneratedVideo` | AI-generated videos |
| `GeneratedAudio` | AI-generated audio |
| `Generated3D` | AI-generated 3D models |
| `ContentPackage` | Content packages |
| `ContentSeries` | Multi-episode series |
| `ContentEpisode` | Series episodes |
| `StylePreset` | Style presets |
| `WatermarkConfig` | Watermark settings |
| `ContentExport` | Export records |
| `ContentDistribution` | Distribution records |
| `ContentAnalytics` | Analytics data |

### 4. Workflow Models (8)

| Model | Purpose |
|-------|---------|
| `Workflow` | Workflow definitions |
| `WorkflowStep` | Workflow steps |
| `WorkflowExecution` | Execution history |
| `WorkflowStepExecution` | Step execution |
| `WorkflowTemplate` | Templates |
| `WorkflowSchedule` | Scheduling |
| `WorkflowVariable` | Variables |
| `WorkflowArtifact` | Output artifacts |

### 5. Opportunity Models (10)

| Model | Purpose |
|-------|---------|
| `Opportunity` | Income opportunities |
| `OpportunityScore` | ML scores |
| `OpportunityOutcome` | Outcomes for learning |
| `OpportunityApplication` | Applications |
| `OpportunityMatch` | User matches |
| `OpportunityAlert` | Alert configs |
| `OpportunityCategory` | Categories |
| `OpportunitySource` | Data sources |
| `OpportunityTracking` | Tracking data |
| `OpportunityConversion` | Conversion funnel |

### 6. Governance Models (12)

| Model | Purpose |
|-------|---------|
| `BoardroomDecision` | Decisions from agents |
| `BoardroomVote` | Agent votes |
| `BoardroomDiscussion` | Discussion threads |
| `ReviewDocument` | Pro/Con reviews |
| `PilotGate` | Pilot readiness gates |
| `PilotChecklist` | Checklist items |
| `PilotExecution` | Pilot execution |
| `PilotOutcome` | Pilot outcomes |
| `ExperimentTracking` | Experiment tracking |
| `KPIOwnership` | KPI assignments |
| `GovernancePolicy` | Policies |
| `PolicyCompliance` | Compliance records |

### 7. Autonomous Situation Models (10)

| Model | Purpose |
|-------|---------|
| `AutonomousSituation` | Situation definitions |
| `SituationExecution` | Execution history |
| `SituationTrigger` | Event triggers |
| `SituationAlert` | Generated alerts |
| `ContentChannel` | Content studio channels |
| `ChannelEpisode` | Channel episodes |
| `TopicPerformance` | Topic performance |
| `ContentDebate` | Debate logs |
| `NarrativeTracking` | Narrative tracking |
| `NarrativeEvidence` | Evidence for shifts |

### 8. Market Intelligence Models (8)

| Model | Purpose |
|-------|---------|
| `MarketBrief` | Daily market briefs |
| `MarketPrediction` | Agent predictions |
| `PredictionOutcome` | Prediction outcomes |
| `MarketSignal` | Detected signals |
| `MarketAlert` | Market alerts |
| `AgentAccuracy` | Agent accuracy tracking |
| `ConfidenceMultiplier` | Confidence adjustments |
| `MarketEvent` | Market events |

### 9. Blockchain Models (6)

| Model | Purpose |
|-------|---------|
| `BlockchainAudit` | Audit records |
| `SmartContractAnalysis` | Contract analysis |
| `WhaleMovement` | Whale tracking |
| `TransactionAlert` | Transaction alerts |
| `ExploitDetection` | Exploit records |
| `BlockchainEvent` | On-chain events |

### 10. Legal Models (8)

| Model | Purpose |
|-------|---------|
| `LegalCase` | Case files |
| `CaseParty` | Parties involved |
| `CaseDocument` | Uploaded documents |
| `DocumentAnalysis` | Analysis results |
| `LegalMotion` | Motion records |
| `MotionResponse` | Response drafts |
| `CaseTimeline` | Case timeline |
| `EvidenceChecklist` | Evidence tracking |

### 11. User & Profile Models (10)

| Model | Purpose |
|-------|---------|
| `UserProfile` | Extended user data |
| `UserPreferences` | User preferences |
| `UserCertification` | Certifications |
| `UserSubscription` | Subscription status |
| `DiscordLink` | Discord account link |
| `ConversationSession` | Chat sessions |
| `UserActivity` | Activity tracking |
| `UserNotification` | Notifications |
| `PushSubscription` | Push notification subs |
| `UserBankroll` | Betting bankroll |

### 12. Voice & Audio Models (6)

| Model | Purpose |
|-------|---------|
| `VoiceProfile` | Voice profiles |
| `VoiceClone` | Cloned voices |
| `VoiceMarketplaceListing` | Marketplace listings |
| `VoicePurchase` | Purchase records |
| `VoiceGeneration` | Generation history |
| `PodcastShow` | Podcast shows |

### 13. Payment Models (6)

| Model | Purpose |
|-------|---------|
| `StripeCustomer` | Stripe customers |
| `StripeSubscription` | Subscriptions |
| `StripePayment` | Payments |
| `GumroadProduct` | Gumroad products |
| `GumroadSale` | Gumroad sales |
| `RevenueTracking` | Revenue tracking |

### 14. Analytics Models (8)

| Model | Purpose |
|-------|---------|
| `SystemMetrics` | System metrics |
| `APIUsage` | API usage tracking |
| `PerformanceMetrics` | Performance data |
| `ErrorLog` | Error logging |
| `AuditLog` | Audit trail |
| `FeatureUsage` | Feature usage |
| `ABTestResult` | A/B test results |
| `ConversionMetrics` | Conversion tracking |

### 15. DaVinci Resolve Models (3)

| Model | Purpose |
|-------|---------|
| `ResolveRenderJob` | Render jobs |
| `ResolveColorGrade` | Color grade presets |
| `ResolveLearning` | Learning records |

### 16-37. Additional Categories

Other model categories include:
- Training Models (LoRA training)
- Project Models (living projects)
- Client Models (client management)
- Advisor Models (famous advisors)
- Memory Palace Models (semantic memory)
- Hive Mind Models (collective intelligence)
- Provenance Models (data lineage)
- ROI Models (attribution)
- Collaboration Models (team features)
- And more...

---

## Key Models Detail

### Agent Model

```python
class Agent(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    category = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_routable = models.BooleanField(default=True)

    # Sci-Fi Features
    mood = models.ForeignKey('AgentMood', null=True)
    evolution = models.ForeignKey('AgentEvolution', null=True)
    personality = models.ForeignKey('AgentPersonality', null=True)

    # Stats
    total_executions = models.IntegerField(default=0)
    total_xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### SpiderData Model

```python
class SpiderData(models.Model):
    spider_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    title = models.CharField(max_length=500)
    content = models.TextField()
    url = models.URLField(null=True)
    source = models.CharField(max_length=200)

    # Embeddings
    embedding = ArrayField(models.FloatField(), null=True)
    embedding_model = models.CharField(max_length=50, null=True)

    # Metadata
    collected_at = models.DateTimeField(auto_now_add=True)
    relevance_score = models.FloatField(null=True)
    content_hash = models.CharField(max_length=64, unique=True)
```

### BoardroomDecision Model

```python
class BoardroomDecision(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    source_type = models.CharField(max_length=50)  # dream, conversation, hive_mind
    source_id = models.CharField(max_length=100)

    # Status
    status = models.CharField(max_length=20)  # pending, approved, rejected, piloting
    quality_score = models.FloatField(null=True)

    # Review
    review_document = models.ForeignKey('ReviewDocument', null=True)
    pilot_gate = models.ForeignKey('PilotGate', null=True)

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True)
    decided_by = models.ForeignKey(User, null=True)
```

### ContentChannel Model (Autonomous Studio)

```python
class ContentChannel(models.Model):
    name = models.CharField(max_length=100)
    platform = models.CharField(max_length=50)  # youtube, blog, podcast
    frequency = models.CharField(max_length=20)  # daily, weekly, monthly

    # Configuration
    topics = ArrayField(models.CharField(max_length=100))
    style_preferences = models.JSONField(default=dict)
    target_audience = models.TextField()

    # Status
    is_active = models.BooleanField(default=True)
    last_episode_at = models.DateTimeField(null=True)
    next_scheduled = models.DateTimeField(null=True)

    # Performance
    total_episodes = models.IntegerField(default=0)
    avg_performance_score = models.FloatField(default=0)
    confidence_multiplier = models.FloatField(default=1.0)
```

---

## Relationships

### Agent → Knowledge Flow

```
Agent
  │
  ├── AgentExecution (1:N)
  │
  ├── AgentKnowledge (1:N)
  │   └── AgentKnowledgeSource (N:1)
  │       └── SpiderData (N:1)
  │
  ├── AgentMemory (1:N)
  │
  └── AgentLearning (1:N)
```

### Spider → Agent Knowledge Flow

```
SpiderData
  │
  └── SpiderBridgeSignal
      │
      └── AgentKnowledgeSource
          │
          └── AgentKnowledge
              │
              └── Agent (prompt injection)
```

### Governance Flow

```
AgentDream / AgentConversation
  │
  └── BoardroomDecision
      │
      ├── ReviewDocument
      │
      └── PilotGate
          │
          ├── PilotChecklist
          │
          └── PilotExecution
              │
              └── PilotOutcome
```

### Autonomous Content Flow

```
ContentChannel
  │
  ├── ChannelEpisode (1:N)
  │   │
  │   └── ContentDebate (1:N)
  │       │
  │       └── TopicMiner vs Contrarian
  │
  └── TopicPerformance (1:N)
      │
      └── Learning Loop
```

---

## Database Commands

### Check Model Counts
```python
from core.models_unified_system import Agent, SpiderData
from core.models_autonomous_studio import ContentChannel

print(f"Agents: {Agent.objects.count()}")
print(f"Spider Data: {SpiderData.objects.count()}")
print(f"Content Channels: {ContentChannel.objects.count()}")
```

### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Database Shell
```bash
python manage.py dbshell
```

---

## Related Documentation

- [AGENTS.md](AGENTS.md) - Agent model usage
- [SPIDERS.md](SPIDERS.md) - Spider data models
- [AUTONOMOUS_SYSTEMS.md](AUTONOMOUS_SYSTEMS.md) - Situation models
