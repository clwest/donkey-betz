<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md) (sole authoritative counts per `DOC_LIFECYCLE.md` §2c). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

# Services Reference

**Last Updated:** Session 1133 close (May 23, 2026 — post 1131-1133 arc count refresh)
**Location:** `core/services/`
**Total Services:** 112 `*Service` classes across 336 files

---

## Overview

The services layer contains business logic separated from views and models. Services are organized by domain and follow a consistent pattern of stateless classes with methods that orchestrate operations.

---

## Service Categories

| Category | Count | Purpose |
|----------|-------|---------|
| AI/Agent Intelligence | 15 | Agent learning, collaboration, context |
| Content Generation | 11 | Creative orchestration, pipelines, deliberation |
| Research & Analysis | 7 | Research orchestration, PDF processing |
| Spider/Data Intelligence | 6 | Spider network, semantic search |
| Scoring & ML | 6 | ML engine, real-time scoring |
| Discord Integration | 5 | Bot, voice, notifications |
| Legal/Litigation | 4 | Document ingestion, response writing |
| Workflow & Automation | 5 | Workflow builder, analytics |
| Payments & Monetization | 4 | Stripe, Gumroad, ROI tracking |
| Provenance & Compliance | 4 | Content audit, originality |
| Memory & Learning | 5 | Embeddings, implicit learning |
| Event System | 3 | Event bus, handlers |
| Chief of Staff | 5 | Reviews, decisions, concerns |
| **System Health** | **2** | **HEART + LUNGS services (Sessions 701-702)** |
| **Workspace & User Context** | **3** | **Workspace management, user context injection (Session 858)** |
| **Initiative Pipeline** | **3** | **Auto-progression, signal aggregation, domain context (Sessions 891, 900, 905-906)** |
| Utility Services | 16 | Various specialized services |

---

## Workspace & User Context (Session 858)

### WorkspaceManager
**File:** `workspace_manager.py`
**Purpose:** Central orchestrator for agent-to-filesystem operations (SKIN Layer)

```python
from core.services.workspace_manager import get_workspace_manager

manager = get_workspace_manager(user)
workspace = manager.get_active_workspace()  # Auto-creates personal workspace if none exists

# Write files with audit trail
operation = manager.write_file(
    workspace=workspace,
    relative_path='generated/report.md',
    content='# Report...',
    agent_name='ResearchAgent'
)
```

**Session 858 Addition:** `get_active_workspace()` now auto-creates personal workspaces at `generated_content/users/{username}/` for any user without one. This eliminates "No active workspace" errors.

### MemoryContextService
**File:** `memory_context_service.py`
**Purpose:** Builds personalized memory blocks for agent prompts

```python
from core.services.memory_context_service import get_memory_context_service

service = get_memory_context_service(user)
memory_context = service.get_prompt_context(user)
# Returns: String with user's preferences, goals, decisions, success patterns
```

### AgentContextMiddleware
**File:** `core/agent_context_middleware.py`
**Purpose:** Extracts comprehensive user context for agent personalization

```python
from core.agent_context_middleware import get_user_context_for_agent

user_context = get_user_context_for_agent(user)
# Returns: {
#   'professional_profile': {...},
#   'skills': {...},
#   'job_preferences': {...},
#   'success_patterns': {...},
#   ...
# }
```

---

## AI/Agent Intelligence (15 Services)

### AgentCollaborationService
**File:** `agent_collaboration.py`
**Purpose:** Orchestrates multi-agent collaboration sessions

```python
from core.services.agent_collaboration import AgentCollaborationService

service = AgentCollaborationService()
result = service.run_collaboration(
    agents=['CTOAgent', 'CreativeDirectorAgent'],
    topic='Platform architecture review',
    collaboration_type='debate'
)
```

### AgentCollaborationHub
**File:** `agent_collaboration_hub.py`
**Purpose:** Real-time agent messaging and consensus building

### AgentIntelligenceContextService
**File:** `agent_intelligence_context.py`
**Purpose:** Builds rich context for agent execution including memories, trends, and spider data

### AgentLearningService
**File:** `agent_learning_service.py`
**Purpose:** Tracks agent interactions and learns preferences over time

### AgentTrainingService
**File:** `agent_training.py`
**Purpose:** Fine-tuning and training agent behaviors

### AgentIntelligenceService
**File:** `ai_content_agents.py`
**Purpose:** Central agent capability registry and routing

### CollectiveIntelligenceService
**File:** `collective_intelligence.py`
**Purpose:** Cross-agent knowledge sharing, gap detection, and synthesis

```python
from core.services.collective_intelligence import CollectiveIntelligenceService

service = CollectiveIntelligenceService()
report = service.generate_collective_report(topic='AI trends')
gaps = service.identify_knowledge_gaps()
```

### PAIntelligenceEnricher
**File:** `pa_intelligence_enricher.py`
**Purpose:** Enriches Personal Assistant responses with platform intelligence

### ClassificationIntegrationService
**File:** `classification_integration.py`
**Purpose:** Intent classification and agent delegation

### SemanticRoutingService
**File:** `semantic_routing.py`
**Purpose:** Routes requests to appropriate agents using semantic similarity

### ProactiveIntelligenceService
**File:** `proactive_intelligence.py`
**Purpose:** Generates proactive suggestions and alerts

### SmartSuggestionsService
**File:** `smart_suggestions.py`
**Purpose:** Context-aware smart suggestions for users

### IntelligenceQueryService
**File:** `intelligence_query.py`
**Purpose:** Unified interface for querying platform intelligence

### PolicyContextService
**File:** `policy_context.py`
**Purpose:** Injects policy and guideline context into agent prompts

### ImplicitLearningService
**File:** `implicit_learning.py`
**Purpose:** Learns from user behavior signals without explicit feedback

---

## Content Generation (8 Services)

### CreativeOrchestrator
**File:** `creative_orchestrator.py`
**Purpose:** Orchestrates multi-asset creative generation (images, videos, audio)

```python
from core.services.creative_orchestrator import CreativeOrchestrator

orchestrator = CreativeOrchestrator()
result = orchestrator.generate_full_asset_pack(
    prompt='Cyberpunk city',
    include_video=True,
    include_audio=True
)
```

### UnifiedContentPipeline
**File:** `content_pipeline.py`
**Purpose:** Tiered content pipeline ($5-$50K packages)

### ResearchToCreativePipeline
**File:** `research_to_creative_pipeline.py`
**Purpose:** Converts research insights into creative briefs

### StyleLibrary
**File:** `style_library.py`
**Purpose:** Manages 80+ style presets for image generation

### TTSTextOptimizer
**File:** `tts_optimizer.py`
**Purpose:** Optimizes text for text-to-speech conversion

### PodcastAudioService
**File:** `podcast_audio_service.py`
**Purpose:** Podcast episode audio generation and assembly

### ContentExportService
**File:** `content_export.py`
**Purpose:** Exports content in various formats

### WatermarkService
**File:** `watermark_service.py`
**Purpose:** Adds watermarks to generated content

### ClaimsPackBuilder (Session 964)
**File:** `claims_pack_builder.py`
**Purpose:** Queries SpiderData (72h) and SignalCluster (active) to assemble a ClaimsPack with deterministic claim IDs for LLM citation tracking

```python
from core.services.claims_pack_builder import get_claims_pack_builder

builder = get_claims_pack_builder()
pack = builder.build(topic='AI market trends', max_claims=20)
prompt_block = pack.to_prompt_block()  # [C-xxxxxxxxxx] markers for LLM
```

### ContentReviewPanelV2 (Session 964)
**File:** `content_review_panel_v2.py`
**Purpose:** 3 structured reviewers (Skeptic + FactCheck + DomainPersona) with validated JSON output and synthetic FAIL on validation failure

```python
from core.services.content_review_panel_v2 import run_reviews

reviews = run_reviews(draft='...', claims_pack=pack, topic='AI trends')
# Each review: {reviewer, verdict, top_issues, required_changes, suggested_edits, confidence}
```

### ContentDeliberationRunner (Session 964)
**File:** `content_deliberation_runner.py`
**Purpose:** Full deliberation pipeline: ClaimsPack -> Draft -> Review -> DecisionEnforcer -> PublishGate -> SelfBlog with stats_snapshot['deliberation']

```python
from core.services.content_deliberation_runner import ContentDeliberationRunner

runner = ContentDeliberationRunner()
result = runner.run_blog(topic='AI market trends', voice='professional')
# result: {status, selfblog_id, deliberation_session_id, decision, gate_result, summary}
```

---

## Research & Analysis (7 Services)

### ResearchOrchestrator
**File:** `research_orchestrator.py`
**Purpose:** Multi-phase research orchestration with source aggregation

```python
from core.services.research_orchestrator import ResearchOrchestrator

orchestrator = ResearchOrchestrator()
result = orchestrator.run_full_research(
    topic='AI market trends 2025',
    depth='comprehensive'
)
```

### ResearchPDFService
**File:** `research_pdf_service.py`
**Purpose:** PDF ingestion and analysis for research

### ProjectResearchBridge
**File:** `project_research_bridge.py`
**Purpose:** Connects research to project context

### LivingProjectService
**File:** `living_project_service.py`
**Purpose:** Maintains project state and learning

### AnalyticsService
**File:** `analytics_service.py`
**Purpose:** Platform analytics and time-series data

### WorkflowAnalyticsService
**File:** `workflow_analytics.py`
**Purpose:** Workflow execution analytics and metrics

### MarketplaceDiscoveryService
**File:** `marketplace_discovery_service.py`
**Purpose:** Discovers marketplace opportunities and platform fit

---

## Spider/Data Intelligence (6 Services)

### SpiderIntelligenceService
**File:** `spider_intelligence.py`
**Purpose:** Central interface for spider data intelligence

```python
from core.services.spider_intelligence import SpiderIntelligenceService

service = SpiderIntelligenceService()
insights = service.get_insights_for_prompt('AI startup funding')
trends = service.get_trending_topics(categories=['tech', 'finance'])
```

### SpiderSemanticSearch
**File:** `spider_semantic_search.py`
**Purpose:** Semantic search across spider-collected data

### SpiderPriorityEngine
**File:** `spider_priority_engine.py`
**Purpose:** Prioritizes spider execution based on relevance

### SmartTrendingService
**File:** `smart_trending_service.py`
**Purpose:** Analyzes trends from spider data

### DomainExtractionService
**File:** `domain_extraction_service.py`
**Purpose:** Extracts domain-specific entities from text

### UnifiedIntelligenceSearch
**File:** `unified_intelligence_search.py`
**Purpose:** Unified search across all intelligence sources

---

## Scoring & ML (6 Services)

### MLScoringEngine
**File:** `ml_scoring_engine.py`
**Purpose:** XGBoost-based opportunity scoring with SHAP explanations

```python
from core.services.ml_scoring_engine import MLScoringEngine

engine = MLScoringEngine()
result = engine.score_opportunity(opportunity_data)
explanation = result.shap_explanation
```

### ScoringDispatcher
**File:** `scoring_dispatcher.py`
**Purpose:** Routes scoring requests to appropriate engines

### RealtimeScorer
**File:** `realtime_scorer.py`
**Purpose:** Real-time scoring queue with priority handling

### RecommendationEngine
**File:** `recommendation_engine.py`
**Purpose:** Generates personalized recommendations

### KnowledgeSimilarityService
**File:** `knowledge_similarity.py`
**Purpose:** Computes similarity between knowledge items

### ABTestingService
**File:** `ab_testing.py`
**Purpose:** A/B testing framework for experiments

---

## Discord Integration (5 Services)

### DonkeyBetzBot
**File:** `discord_bot.py`
**Purpose:** Main Discord bot with 29 command Cogs (112 commands)

### DiscordNotificationService
**File:** `discord_notifications.py`
**Purpose:** Sends notifications to Discord channels

```python
from core.services.discord_notifications import DiscordNotificationService

service = DiscordNotificationService()
await service.send_dream_notification(agent_name, dream_content)
await service.send_system_status(status_data)
```

### DiscordVoiceService
**File:** `discord_voice.py`
**Purpose:** Voice channel recording and voice cloning

### ElevenLabsVoiceCloner
**File:** `discord_voice.py`
**Purpose:** Voice cloning via ElevenLabs API

### VoiceRecorder
**File:** `discord_voice.py`
**Purpose:** Records voice from Discord channels

---

## Legal/Litigation (4 Services)

### LegalDocumentIngestor
**File:** `litigation_brain.py`
**Purpose:** Ingests and parses legal documents

### LegalContextBuilder
**File:** `litigation_brain.py`
**Purpose:** Builds legal context from case history

### LegalResponseWriter
**File:** `litigation_brain.py`
**Purpose:** Drafts legal responses and filings

### LegalFilingPackager
**File:** `litigation_brain.py`
**Purpose:** Packages documents for court filing

---

## Workflow & Automation (5 Services)

### WorkflowBuilderService
**File:** `workflow_builder.py`
**Purpose:** Builds and manages multi-step workflows

### AutonomousIntelligenceLoop
**File:** `autonomous_loop.py`
**Purpose:** Autonomous monitoring and intelligence gathering

### AutonomousActionExecutor
**File:** `autonomous_action_executor.py`
**Purpose:** Executes autonomous actions based on triggers

### TaskMemoryService
**File:** `task_memory.py`
**Purpose:** Tracks task state and progress

### StreamingProgressService
**File:** `streaming_progress.py`
**Purpose:** Real-time progress updates via WebSocket

---

## Payments & Monetization (4 Services)

### StripeSubscriptionService
**File:** `stripe_subscription.py`
**Purpose:** Subscription management via Stripe

### StripeVoicePaymentService
**File:** `stripe_voice_payments.py`
**Purpose:** Voice marketplace payments

### GumroadPublishingService
**File:** `gumroad_publishing.py`
**Purpose:** Publishes content to Gumroad

### ROITracker
**File:** `roi_tracker.py`
**Purpose:** Tracks ROI, conversions, and attribution

```python
from core.services.roi_tracker import ROITracker

tracker = ROITracker()
summary = tracker.get_roi_summary(period='weekly')
attribution = tracker.attribute_conversion(user_id, source)
```

---

## Provenance & Compliance (4 Services)

### ProvenanceService
**File:** `provenance_service.py`
**Purpose:** Content provenance tracking

### ProvenanceTracker
**File:** `provenance_tracker.py`
**Purpose:** Tracks content lineage and transformations

### ContentAuditService
**File:** `provenance_service.py`
**Purpose:** Audits content for compliance

### OriginalityService
**File:** `provenance_service.py`
**Purpose:** Checks content originality

---

## Memory & Learning (5 Services)

### MemoryEmbeddingService
**File:** `memory_embedding_service.py`
**Purpose:** Generates and searches memory embeddings for semantic retrieval

**Session 768 Enhancement:** Memory Safety Classification
- `create_memory()` - Now accepts `safety_class` parameter and auto-detects poison risk
- `update_memory_embedding()` - Skips `test_only` and high-risk memories
- `backfill_embeddings()` - Excludes `test_only` and `poison_risk_score >= 0.5`

**Safety Classes:**
- `test_only` - Never embedded (health checks, connectivity tests)
- `exploratory` - Review before using
- `candidate` - Default, auto-promoted to approved if low risk (<0.3)
- `approved` - Always embedded

See: `docs/MEMORY_SAFETY_CLASSIFICATION.md` for full documentation.

### PipelineLearningService
**File:** `pipeline_learning.py`
**Purpose:** Learning from pipeline execution outcomes

### ResolveLearningService
**File:** `resolve_learning.py`
**Purpose:** Learning from DaVinci Resolve render outcomes

### ReferenceResolver
**File:** `reference_resolver.py`
**Purpose:** Resolves entity references in text

### DeduplicationService
**File:** `deduplication_service.py`
**Purpose:** Deduplicates content and knowledge items

---

## Event System (3 Services)

### EventBus
**File:** `event_bus.py`
**Purpose:** Central event bus for pub/sub messaging

```python
from core.services.event_bus import EventBus, Event

bus = EventBus()
bus.publish(Event(
    stream='opportunities',
    event_type='new_opportunity',
    data={'title': 'AI Job Opening'}
))
```

### EventHandlerRegistry
**File:** `event_handlers.py`
**Purpose:** Registers and dispatches event handlers

### EventConsumerWorker
**File:** `event_handlers.py`
**Purpose:** Background worker for event processing

---

## Chief of Staff (5 Services)

### ReviewDocumentService
**File:** `review_document.py`
**Purpose:** Generates Pro/Con review documents for decisions

```python
from core.services.review_document import ReviewDocumentService

service = ReviewDocumentService()
review = service.generate_review(
    topic='Should we add AR features?',
    context=project_context
)
```

### SideChatService
**File:** `side_chat.py`
**Purpose:** Pro/Con interrogation of decisions

### DecisionExtractor
**File:** `decision_extractor.py`
**Purpose:** Extracts decisions from conversations

### ConcernTrackerService
**File:** `concern_tracker.py`
**Purpose:** Tracks and escalates concerns for human review

### HumanActionService
**File:** `human_action_service.py`
**Purpose:** Surfaces items requiring human action

---

## System Health (2 Services)

### HeartMonitorService
**File:** `heart.py`
**Purpose:** Central health monitoring system - the "heartbeat" of the AI body (Session 701)

Monitors 6 system components every 60 seconds:
- **Brain** - ThinkingAgent availability
- **Nervous System** - LLM Provider Registry status
- **Organs** - 72 Agents health
- **Sensory** - 77 Spiders health
- **Skin** - Workspace Manager availability
- **Memory** - Database + Redis connectivity

```python
from core.services.heart import get_heart_monitor

heart = get_heart_monitor()

# Run full health check
pulse = heart.pulse()
print(f"Health: {pulse['overall_status']} ({pulse['health_score']}%)")

# Check specific component
brain_status = heart.check_brain()

# Quick alive check
is_alive = heart.is_alive()

# Get cached vitals
vitals = heart.get_vitals()
```

### LungsCapacityService
**File:** `lungs.py`
**Purpose:** Resource and capacity management - the "breathing" of the AI body (Session 702)

Manages token/cost budgets across all LLM providers:
- **Breathing Check** - Aggregates consumption, updates cycles
- **Oxygen Levels** - Remaining budget percentages
- **Forecasting** - Projects end-of-period usage
- **Alerts** - Discord notifications at 80%/95% thresholds

Default Budgets: System ($50/day, $500/month), OpenAI ($30/day), Anthropic ($20/day), Together AI ($10/day), DeepSeek ($10/day)

```python
from core.services.lungs import get_lungs_monitor

lungs = get_lungs_monitor()

# Run full breathing check
result = lungs.breathe()
print(f"O2 Level: {result['oxygen_level']}%")

# Check if call allowed within budget
can_call, reason = lungs.can_breathe(provider='openai', estimated_tokens=1000)

# Record consumption after call
lungs.record_breath(provider='openai', agent='ResearchAgent', tokens=500, cost=0.01)

# Get spending forecast
forecast = lungs.forecast_end_of_period(budget)

# Get spending velocity
velocity = lungs.get_spending_velocity(hours=24)
```

**Features:**
- Singleton pattern for efficient reuse
- 60-second Celery Beat schedule (`run_heartbeat` task)
- Discord alerts on CRITICAL status
- Time-series database storage (HeartBeat model)
- Component status caching (ComponentStatus model)
- CLI management command: `python manage.py heart_check`

---

## Initiative Pipeline (3 Services)

### InitiativeAutoProgressionService
**File:** `initiative_auto_progression.py`
**Purpose:** Quality-based automatic stage advancement for initiatives (Session 905-906)

```python
from core.services.initiative_auto_progression import InitiativeAutoProgressionService

service = InitiativeAutoProgressionService()

# Check if a stage qualifies for progression
result = service.check_stage_for_progression(initiative_stage)
# Returns: {'qualifies': True, 'confidence': 0.75, 'criteria_met': [...], 'criteria_missing': [...]}

# Progress initiative to next stage
service.progress_initiative_stage(initiative)

# Trigger async document generation for next stage
service.trigger_next_stage_generation(initiative)
```

**Quality Criteria:**
- Content length ≥ 500 characters
- Required sections present (with flexible alternatives)
- No "insufficient data" markers
- Confidence threshold: 60%

### SignalAggregationService
**File:** `signal_aggregation_service.py`
**Purpose:** Clusters spider signals into patterns for Origin & Trigger UI (Session 900)

```python
from core.services.signal_aggregation_service import SignalAggregationService

service = SignalAggregationService()

# Aggregate recent spider data into signal clusters
clusters = service.aggregate_signals(hours=24, min_signals=3)

# Generate auto-topics from clusters
topics = service.generate_auto_topics(clusters)
```

**Signal Clustering:**
- Groups SpiderData by keyword/topic overlap
- Calculates strength, confidence, novelty scores
- Creates SignalCluster and AutoTopic records

### DomainContentContextBuilder
**File:** `domain_content_context.py`
**Purpose:** Injects domain-specific platform data into content generation (Session 891)

```python
from core.services.domain_content_context import DomainContentContextBuilder

builder = DomainContentContextBuilder()

# Build context for a specific domain
context = builder.build_context(topic="AI trading strategies", user=user)
# Returns: Domain-specific data (finance, crypto, sports, etc.)

# Detect domain from topic
domains = builder.detect_domains(topic)  # Returns up to 2 domains
```

**Supported Domains:** finance, crypto, sports, betting, ai_tech, legal, career, health, education

---

## Utility Services (16 Services)

### KalshiService
**File:** `kalshi_service.py`
**Purpose:** Kalshi prediction market integration with RSA-PSS auth

### MarketDataService
**File:** `market_data_service.py`
**Purpose:** Sports odds and market data

### BlockchainEventListener
**File:** `blockchain_event_listener.py`
**Purpose:** Listens to blockchain events for audit

### CertificateService
**File:** `certificate_service.py`
**Purpose:** Manages user certifications

### HITLValidationService
**File:** `hitl_validation.py`
**Purpose:** Human-in-the-loop validation workflows

### ArtifactExtractionService
**File:** `artifact_extraction.py`
**Purpose:** Extracts actionable artifacts from conversations

### ArtifactExecutionService
**File:** `artifact_execution.py`
**Purpose:** Executes extracted artifacts

### WeeklySynthesisService
**File:** `weekly_synthesis.py`
**Purpose:** Generates weekly intelligence synthesis

### PushNotificationService
**File:** `push_notification_service.py`
**Purpose:** Web push notifications for alerts

### WatermarkIntegration
**File:** `watermark_integration.py`
**Purpose:** Integrates watermarking into pipelines

### IncomeActionService
**File:** `income_action_service.py`
**Purpose:** Tracks income-generating actions

---

## Usage Patterns

### Service Instantiation
Most services are stateless and can be instantiated directly:

```python
from core.services.spider_intelligence import SpiderIntelligenceService

service = SpiderIntelligenceService()
result = service.get_insights_for_prompt('query')
```

### Async Services
Some services have async methods for non-blocking operations:

```python
from core.services.discord_notifications import DiscordNotificationService

service = DiscordNotificationService()
await service.send_notification(channel, message)
```

### Service Composition
Services often compose other services:

```python
class CreativeOrchestrator:
    def __init__(self):
        self.spider_service = SpiderIntelligenceService()
        self.style_library = StyleLibrary()
        self.recommendation_engine = RecommendationEngine()
```

---

## See Also

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [AGENTS.md](AGENTS.md) - Agent reference (71 agents)
- [SPIDERS.md](SPIDERS.md) - Spider network (77 spiders)
- [CAPABILITIES.md](CAPABILITIES.md) - Full feature list
