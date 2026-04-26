<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Services inventory snapshot
>
> **Where to look now:**
> - [docs/SERVICES.md](/docs/SERVICES.md)
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Services Documentation

**Total Services:** 93+
**Location:** `core/services/`
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Service Categories](#service-categories)
3. [Complete Service List](#complete-service-list)
4. [Key Services Detail](#key-services-detail)
5. [Usage Examples](#usage-examples)

---

## Overview

Services encapsulate business logic and are used by agents, views, and Celery tasks. All services follow a consistent pattern with dependency injection and error handling.

### Service Pattern
```python
class MyService:
    def __init__(self, user=None):
        self.user = user

    def do_something(self, **kwargs) -> Dict[str, Any]:
        # Business logic
        return {"success": True, "data": result}
```

---

## Service Categories

### AI & Agent Intelligence (15)

| Service | Purpose | Used By |
|---------|---------|---------|
| **AgentCollaborationService** | Multi-agent collaboration | MeetingCoordinatorAgent |
| **AgentCollaborationHub** | Collaboration orchestration | Workflow agents |
| **AgentIntelligenceContext** | Context management | All agents |
| **AgentLearningService** | Agent learning loop | BaseAgent |
| **AgentTraining** | Agent training management | Training agents |
| **CollectiveIntelligenceService** | Cross-agent knowledge | Knowledge pipeline |
| **SemanticRoutingService** | Embedding-based routing | AgentRouter |
| **PAIntelligenceEnricher** | PA context enrichment | PersonalAssistantAgent |
| **PALearningInsights** | PA learning analytics | Dashboard |
| **ImplicitLearningService** | Behavior-based learning | All agents |
| **AIContentAgents** | Content agent coordination | Content pipeline |
| **AIDecisionPromoter** | Auto-promote decisions | Governance |
| **DecisionExtractor** | Extract decisions from text | Boardroom |
| **DecisionPrioritization** | Prioritize decisions | Boardroom |
| **DecisionPromotionRules** | Promotion rule engine | Governance |

### Content Generation (8)

| Service | Purpose | Used By |
|---------|---------|---------|
| **CreativeOrchestrator** | Multi-asset generation | Content pipeline |
| **ContentPipeline** | $5-$50K tier system | Discord, Web |
| **ContentExport** | Export content packages | Download |
| **ResearchToCreativePipeline** | Research → Content flow | Workflows |
| **StyleLibrary** | 80+ style presets | Image generation |
| **WatermarkService** | Add watermarks | Image output |
| **WatermarkIntegration** | Watermark integration | Content pipeline |
| **ChecklistContentGenerator** | Checklist generation | Pilots |

### Research & Analysis (7)

| Service | Purpose | Used By |
|---------|---------|---------|
| **ResearchOrchestrator** | Research coordination | ResearchAgent |
| **ResearchPDFService** | PDF processing with OCR | Document upload |
| **UnifiedIntelligenceSearch** | Spider + research search | Search |
| **IntelligenceQuery** | Query intelligence data | API |
| **ProjectResearchBridge** | Project ↔ Research link | Projects |
| **RecentActivity** | Activity tracking | Dashboard |
| **WeeklySynthesis** | Weekly summaries | Reports |

### Spider & Data Intelligence (6)

| Service | Purpose | Used By |
|---------|---------|---------|
| **SpiderIntelligenceService** | Spider data analysis | Agents |
| **SmartTrendingService** | Trending topic detection | Trending API |
| **SpiderDeduplication** | Deduplicate spider data | Data cleanup |
| **SpiderSemanticSearch** | Semantic spider search | Search |
| **SpiderPriorityEngine** | Spider prioritization | Scheduling |
| **EmbeddingService** | Vector embeddings | All data |

### ML & Scoring (6)

| Service | Purpose | Used By |
|---------|---------|---------|
| **MLScoringEngine** | XGBoost + SHAP scoring | Opportunities |
| **OpportunityScoringService** | Opportunity scoring | Pipeline |
| **RealTimeScorer** | Real-time scoring | Events |
| **ScoringDispatcher** | Score distribution | Pipeline |
| **WeightedLearning** | Weighted learning system | ML |
| **LearningVelocity** | Learning speed tracking | Analytics |

### Discord Integration (5)

| Service | Purpose | Used By |
|---------|---------|---------|
| **DiscordBotService** | Main Discord bot | Discord |
| **DiscordNotificationService** | Channel notifications | Alerts |
| **DiscordVoice** | Voice channel features | Voice commands |
| **PushNotificationService** | Push notifications | Mobile |
| **EventBus** | Event distribution | All services |

### Chief of Staff & Governance (5)

| Service | Purpose | Used By |
|---------|---------|---------|
| **ReviewDocumentService** | Pro/Con analysis | Boardroom |
| **SideChatService** | Interrogation/debate | Review |
| **BoardroomLearning** | Boardroom analytics | Learning |
| **PolicyContext** | Policy management | Governance |
| **HITLValidation** | Human-in-the-loop | Pilots |

### Legal Services (4)

| Service | Purpose | Used By |
|---------|---------|---------|
| **LitigationBrain** | Legal document analysis | LegalAgent |
| **DocumentIngestionService** | Document upload | Legal |
| **LegalDocumentAnalyzer** | Document analysis | Legal |
| **ResponseWritingService** | Response generation | Legal |

### Payments & Monetization (4)

| Service | Purpose | Used By |
|---------|---------|---------|
| **StripeSubscription** | Subscription management | Billing |
| **StripeVoicePayments** | Voice marketplace payments | Voice |
| **GumroadPublishing** | Gumroad integration | Publishing |
| **ROITracker** | ROI tracking | Analytics |

### Provenance & Compliance (4)

| Service | Purpose | Used By |
|---------|---------|---------|
| **ProvenanceService** | Data lineage | Compliance |
| **ProvenanceTracker** | Track data chain | Audit |
| **DeduplicationService** | Deduplicate content | Data cleanup |
| **SystemRealityChecker** | Reality verification | Audit |

### Memory & Context (4)

| Service | Purpose | Used By |
|---------|---------|---------|
| **MemoryContextService** | Memory retrieval | Agents |
| **MemoryEmbeddingService** | Memory embeddings | Search |
| **TaskMemory** | Task memory | Celery |
| **KnowledgeSimilarity** | Knowledge matching | Learning |

### Experiment & Pilot (6)

| Service | Purpose | Used By |
|---------|---------|---------|
| **ExperimentMetrics** | Experiment tracking | Pilots |
| **ExperimentRecommendations** | Recommendations | Pilots |
| **ExperimentRollback** | Rollback support | Pilots |
| **ExperimentSuggestion** | Suggestions | Pilots |
| **ExperimentLearningEnhancer** | Learning enhancement | Pilots |
| **PilotProgress** | Pilot tracking | Dashboard |

### Autonomous & Events (6)

| Service | Purpose | Used By |
|---------|---------|---------|
| **AutonomousLoop** | Autonomous monitoring | Situations |
| **AutonomousActionExecutor** | Action execution | Situations |
| **BlockchainEventListener** | Blockchain events | Blockchain |
| **EventHandlers** | Event handling | Events |
| **ConcernTracker** | Concern tracking | Monitoring |
| **HumanActionService** | Human action requests | HITL |

### Market & Trading (3)

| Service | Purpose | Used By |
|---------|---------|---------|
| **KalshiService** | Prediction markets | Trading |
| **MarketDataService** | Market data | Stocks |
| **MarketplaceDiscoveryService** | Marketplace discovery | Income |

### Audio & Media (3)

| Service | Purpose | Used By |
|---------|---------|---------|
| **PodcastAudioService** | Podcast audio generation | Podcasts |
| **TTSOptimizer** | TTS optimization | Audio |
| **StreamingProgress** | Progress streaming | UI |

### Analytics & Reporting (4)

| Service | Purpose | Used By |
|---------|---------|---------|
| **AnalyticsService** | General analytics | Dashboard |
| **WorkflowAnalytics** | Workflow analytics | Workflows |
| **SystemStateAggregator** | System state | Health |
| **PlatformIntelligenceBriefing** | Briefings | Reports |

### Other (8)

| Service | Purpose | Used By |
|---------|---------|---------|
| **CertificateService** | User certifications | Profile |
| **ABTesting** | A/B testing | Experiments |
| **SmartSuggestions** | Smart suggestions | UI |
| **RecommendationEngine** | Recommendations | Discovery |
| **ReferenceResolver** | Reference resolution | Documents |
| **DomainExtractionService** | Domain extraction | URLs |
| **ClassificationIntegration** | Classification | Routing |
| **ArtifactExtraction** | Artifact extraction | Workflows |

---

## Complete Service List (93+)

```
1.  ab_testing
2.  agent_collaboration
3.  agent_collaboration_hub
4.  agent_intelligence_context
5.  agent_learning_service
6.  agent_training
7.  ai_content_agents
8.  ai_decision_promoter
9.  analytics_service
10. artifact_execution
11. artifact_extraction
12. auto_kpi_tracking
13. autonomous_action_executor
14. autonomous_loop
15. blockchain_event_listener
16. boardroom_learning
17. certificate_service
18. checklist_content_generator
19. classification_integration
20. collective_intelligence
21. concern_tracker
22. content_export
23. content_pipeline
24. creative_orchestrator
25. decision_extractor
26. decision_prioritization
27. decision_promotion_rules
28. deduplication_service
29. discord_bot
30. discord_notifications
31. discord_voice
32. domain_extraction_service
33. event_bus
34. event_handlers
35. experiment_learning_enhancer
36. experiment_metrics
37. experiment_recommendations
38. experiment_rollback
39. experiment_suggestion
40. gumroad_publishing
41. hitl_validation
42. human_action_service
43. implicit_learning
44. income_action_service
45. intelligence_query
46. kalshi_service
47. knowledge_similarity
48. kpi_alerts
49. learning_velocity
50. litigation_brain
51. living_project_service
52. market_data_service
53. marketplace_discovery_service
54. memory_context_service
55. memory_embedding_service
56. ml_scoring_engine
57. pa_intelligence_enricher
58. pa_learning_insights
59. pilot_progress
60. pipeline_learning
61. platform_intelligence_briefing
62. podcast_audio_service
63. policy_context
64. proactive_intelligence
65. project_research_bridge
66. provenance_service
67. provenance_tracker
68. push_notification_service
69. realtime_scorer
70. recent_activity
71. recommendation_engine
72. reference_resolver
73. research_orchestrator
74. research_pdf_service
75. research_to_creative_pipeline
76. resolve_learning
77. review_document
78. roi_tracker
79. scoring_dispatcher
80. semantic_routing
81. side_chat
82. smart_suggestions
83. smart_trending_service
84. spider_deduplication
85. spider_intelligence
86. spider_priority_engine
87. spider_semantic_search
88. streaming_progress
89. stripe_subscription
90. stripe_voice_payments
91. style_library
92. system_reality_checker
93. system_state_aggregator
94. task_memory
95. tts_optimizer
96. unified_intelligence_search
97. watermark_integration
98. watermark_service
99. weekly_synthesis
100. weighted_learning
101. workflow_analytics
102. workflow_builder
```

---

## Key Services Detail

### SpiderIntelligenceService

Main service for spider data analysis:

```python
from core.services.spider_intelligence import SpiderIntelligenceService

service = SpiderIntelligenceService()

# Get creative trends
trends = service.get_creative_trends(hours=48)

# Get financial data
financial = service.get_financial_intelligence()

# Search spider data
results = service.search(query="AI trends", limit=10)
```

### CollectiveIntelligenceService

Cross-agent knowledge sharing:

```python
from core.services.collective_intelligence import CollectiveIntelligenceService

service = CollectiveIntelligenceService()

# Share knowledge between agents
service.share_knowledge(
    source_agent="ResearchAgent",
    target_agent="ContentWriterAgent",
    knowledge_id=123
)

# Get knowledge for agent
knowledge = service.get_agent_knowledge("ImageAgent", limit=10)
```

### MLScoringEngine

XGBoost-based opportunity scoring:

```python
from core.services.ml_scoring_engine import MLScoringEngine

engine = MLScoringEngine()

# Score an opportunity
score = engine.score_opportunity(opportunity_id=123)

# Get SHAP explanation
explanation = engine.explain_score(opportunity_id=123)

# Retrain model
engine.retrain(min_samples=100)
```

### ReviewDocumentService

Chief of Staff Pro/Con analysis:

```python
from core.services.review_document import ReviewDocumentService

service = ReviewDocumentService()

# Generate review document
review = service.generate_review(
    decision_id=123,
    include_pro_con=True,
    include_risk_analysis=True
)
```

### ResolveLearningService

DaVinci Resolve learning loop:

```python
from core.services.resolve_learning import get_resolve_learning_service

service = get_resolve_learning_service()

# Record feedback
service.record_user_feedback(
    job_id="abc123",
    rating=5,
    was_used=True
)

# Get best grade for trends
grade = service.get_best_grade_for_trends(spider_trends)

# Get insights
insights = service.get_learning_insights()
```

---

## Usage Examples

### Import Services
```python
# Direct import
from core.services.spider_intelligence import SpiderIntelligenceService

# With singleton pattern
from core.services.resolve_learning import get_resolve_learning_service
service = get_resolve_learning_service()
```

### Service in View
```python
from django.http import JsonResponse
from core.services.spider_intelligence import SpiderIntelligenceService

def trending_api(request):
    service = SpiderIntelligenceService()
    trends = service.get_creative_trends(hours=24)
    return JsonResponse({"trends": trends})
```

### Service in Agent
```python
from core.agents.base_agent import BaseAgent
from core.services.spider_intelligence import SpiderIntelligenceService

class MyAgent(BaseAgent):
    def execute(self, task, context, **kwargs):
        spider_service = SpiderIntelligenceService()
        trends = spider_service.get_creative_trends()
        # Use trends in agent logic
```

### Service in Celery Task
```python
from celery import shared_task
from core.services.autonomous_loop import AutonomousLoop

@shared_task
def run_autonomous_check():
    loop = AutonomousLoop()
    return loop.run_cycle()
```

---

## Related Documentation

- [AGENTS.md](AGENTS.md) - Agents that use services
- [CELERY_TASKS.md](CELERY_TASKS.md) - Tasks that use services
- [API_ENDPOINTS.md](API_ENDPOINTS.md) - Endpoints that use services
