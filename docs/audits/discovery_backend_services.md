# Agent 1.1: Backend Services Discovery

**Date:** December 21, 2025
**Status:** Complete
**Total Services Discovered:** 93+ Python modules

---

## Summary

Discovered **93 backend service modules** across 5 directories:
- `core/services/` - 67 files (main business logic)
- `core/super_platform/` - 12 files (unified intelligence hub)
- `core/prompts/` - 3 files (central prompt registry)
- `core/assistant/` - 8 files (GPT tool definitions)
- `ai_core/spiders/` - 50+ files (spider infrastructure)

---

## 1. Core Services (`core/services/`) - 67 Files

### Business Intelligence Services
| Service | Purpose | Used By |
|---------|---------|---------|
| `smart_trending_service.py` | Real-time trending data aggregation | PersonalAssistant, ContentWriterAgent |
| `unified_intelligence_search.py` | Cross-spider semantic search | tasks.py |
| `spider_intelligence.py` | Spider data access service | PersonalAssistant, tasks.py |
| `spider_priority_engine.py` | Prioritizes spider fetching | tasks.py |
| `spider_semantic_search.py` | Semantic spider data search | tasks.py |
| `research_orchestrator.py` | Orchestrates research workflows | views_business_ideas.py |
| `creative_orchestrator.py` | Orchestrates creative workflows | views_business_ideas.py |
| `decision_extractor.py` | Extracts decisions from content | tasks.py |
| `policy_context.py` | Policy context for agents | PersonalAssistant, tasks.py |
| `domain_extraction_service.py` | Extracts domains from content | models_partnership.py |
| `market_data_service.py` | Market data for trading | tasks.py |

### Learning & Intelligence Services
| Service | Purpose | Used By |
|---------|---------|---------|
| `collective_intelligence.py` | Cross-agent knowledge sharing | tasks.py |
| `agent_learning_service.py` | Individual agent learning | agent_collaboration_hub.py |
| `implicit_learning.py` | Learns from user behavior | (__init__.py export only) |
| `recommendation_engine.py` | Content/action recommendations | (__init__.py export only) |
| `knowledge_similarity.py` | Knowledge similarity scoring | tasks.py |
| `ml_scoring_engine.py` | XGBoost ML scoring | tasks.py |
| `realtime_scorer.py` | Real-time opportunity scoring | tasks.py |
| `scoring_dispatcher.py` | Dispatches scoring jobs | tasks.py |
| `pipeline_learning.py` | Pipeline performance learning | tasks.py |

### Agent Collaboration Services
| Service | Purpose | Used By |
|---------|---------|---------|
| `agent_collaboration.py` | Multi-agent collaboration | (__init__.py export) |
| `agent_collaboration_hub.py` | Collaboration hub | views_agent_collaboration.py |
| `agent_intelligence_context.py` | Agent context building | (imports visible) |
| `agent_training.py` | Agent training pipelines | views_agent_training.py |

### Content Generation Services
| Service | Purpose | Used By |
|---------|---------|---------|
| `content_pipeline.py` | Unified content pipeline | tasks.py |
| `content_export.py` | Export content (md/txt/docx/pdf) | views_projects_api.py |
| `tts_optimizer.py` | Text-to-speech optimization | views_audio.py |
| `podcast_audio_service.py` | Podcast audio generation | (imported) |
| `style_library.py` | Style preset library | views_business_ideas.py |

### Project Services
| Service | Purpose | Used By |
|---------|---------|---------|
| `project_research_bridge.py` | Links research to projects | views_projects_api.py, tasks.py |
| `living_project_service.py` | Living/dynamic projects | views_projects_api.py, tasks.py |
| `research_to_creative_pipeline.py` | Research-to-creative flow | views_projects_api.py |
| `research_pdf_service.py` | PDF research extraction | views_projects_api.py |

### Analytics & Tracking Services
| Service | Purpose | Used By |
|---------|---------|---------|
| `analytics_service.py` | Platform analytics | views_analytics.py |
| `workflow_analytics.py` | Workflow performance | views_workflow_analytics.py |
| `roi_tracker.py` | ROI tracking | tasks.py |
| `provenance_tracker.py` | Content provenance | tasks.py |

### Payment & Monetization Services
| Service | Purpose | Used By |
|---------|---------|---------|
| `stripe_subscription.py` | Stripe subscriptions | views_stripe.py |
| `stripe_voice_payments.py` | Voice marketplace payments | (imported) |
| `gumroad_publishing.py` | Gumroad publishing | views_platform_integrations.py, tasks.py |
| `marketplace_discovery_service.py` | Marketplace discovery | (imported) |
| `income_action_service.py` | Income action tracking | (imported) |

### Discord Services
| Service | Purpose | Used By |
|---------|---------|---------|
| `discord_bot.py` | Main Discord bot (99+ commands) | (standalone) |
| `discord_notifications.py` | Discord channel notifications | tasks.py (15+ locations) |
| `discord_voice.py` | Discord voice features | (imported) |

### Legal Services
| Service | Purpose | Used By |
|---------|---------|---------|
| `litigation_brain.py` | Legal document analysis | views_legal.py |

### Autonomous Services
| Service | Purpose | Used By |
|---------|---------|---------|
| `autonomous_loop.py` | Autonomous intelligence loop | tasks.py |
| `blockchain_event_listener.py` | Blockchain event monitoring | (imported) |

### Testing & Validation Services
| Service | Purpose | Used By |
|---------|---------|---------|
| `ab_testing.py` | A/B testing framework | views_ab_testing.py |
| `hitl_validation.py` | Human-in-the-loop validation | tasks.py |

### Event System Services
| Service | Purpose | Used By |
|---------|---------|---------|
| `event_bus.py` | Event bus infrastructure | tasks.py |
| `event_handlers.py` | Event handler workers | tasks.py |

### Miscellaneous Services
| Service | Purpose | Used By |
|---------|---------|---------|
| `task_memory.py` | Task memory persistence | PersonalAssistant, views_assistant_bypass.py |
| `proactive_intelligence.py` | Proactive suggestions | PersonalAssistant |
| `smart_suggestions.py` | Context-aware suggestions | PersonalAssistant |
| `reference_resolver.py` | Reference resolution | PersonalAssistant |
| `streaming_progress.py` | Progress streaming | (imported) |
| `classification_integration.py` | Query classification | PersonalAssistant |
| `semantic_routing.py` | Semantic agent routing | (imported) |
| `memory_embedding_service.py` | Memory embeddings | tasks.py |
| `workflow_builder.py` | Workflow construction | tasks.py |
| `watermark_service.py` | Content watermarking | watermark_integration.py |
| `watermark_integration.py` | Watermark integration | views_provenance.py |
| `provenance_service.py` | Content provenance | content/signals.py |
| `certificate_service.py` | Certificates | views_provenance.py |
| `ai_content_agents.py` | AI content agent wrappers | (imported) |
| `resolve_learning.py` | Resolve pipeline learning | (imported) |

---

## 2. Super Platform (`core/super_platform/`) - 12 Files

The unified intelligence hub (Sessions 263-266):

| Module | Purpose | Used By |
|--------|---------|---------|
| `coordinator.py` | SuperPlatformCoordinator - unified brain | views_super_platform.py |
| `prompt_builder.py` | DynamicPromptBuilder - context-aware prompts | ContentWriterAgent, coordinator |
| `query_classifier.py` | QueryClassifier - intent detection | classification_integration.py |
| `context_aggregator.py` | ContextAggregator - multi-source context | coordinator.py, PersonalAssistant |
| `scifi_integration.py` | SciFiIntegrationService - mood/memory/evolution | agent_router.py |
| `learning_loop.py` | LearningLoopService - outcome tracking | agents/base_agent.py (all agents) |
| `autonomy_engine.py` | AutonomyEngine - self-operating system | tasks.py |
| `revenue_integration.py` | RevenueIntegrationService - opportunity scoring | opportunity_pipeline_orchestrator |
| `agent_context_service.py` | AgentContextService - spider data for agents | spider_context_mixin.py |
| `spider_context_mixin.py` | SpiderContextMixin - agent mixin | deprecated agents |
| `learning_companion_service.py` | LearningCompanionService - charter/progress | PersonalAssistant |

---

## 3. Prompts (`core/prompts/`) - 3 Files

Central prompt registry (Session 266):

| Module | Purpose | Used By |
|--------|---------|---------|
| `registry.py` | PLATFORM_CONTEXT, AGENT_PROMPTS, ADVISOR_PROMPTS | 14+ files |
| `tool_descriptions.py` | GPT tool descriptions | tool_definitions.py |

---

## 4. Assistant (`core/assistant/`) - 8 Files

GPT function calling infrastructure:

| Module | Purpose | Used By |
|--------|---------|---------|
| `tool_definitions.py` | GPT function schemas | PersonalAssistant |
| `image_tools.py` | Image generation tools | tool_definitions.py |
| `video_tools.py` | Video generation tools | tool_definitions.py |
| `audio_tools.py` | Audio generation tools | tool_definitions.py |
| `base.py` | Base tool classes | all tool files |
| `utils.py` | Utility functions | tool files |
| `constants.py` | Constants | tool files |

---

## 5. Spider Infrastructure (`ai_core/spiders/`) - 50+ Files

| Category | Key Files |
|----------|-----------|
| **Base** | `base_spider.py`, `spider_registry.py` |
| **Orchestration** | `spider_orchestrator.py`, `spider_army_orchestrator.py`, `spider_connector_orchestrator.py` |
| **Data Pipeline** | `data_pipeline.py`, `spider_data_router.py`, `real_data_collector.py` |
| **Specialized** | `news_spider.py`, `sports_data_spider.py`, `freelance_opportunity_spider.py` |
| **Integration** | `integration.py`, `income_builder_connector.py` |
| **Monitoring** | `metrics.py`, `monitoring_dashboard.py` |
| **Web Layer** | `web_request_layer.py`, `playwright_spider.py` |
| **Revenue** | `revenue_tracker.py`, `roi_calculator.py`, `opportunity_scorer.py` |
| **Handlers** | `reddit_handler.py`, `bluesky_handler.py`, `oauth_handler.py` |

---

## Potentially Orphaned Services

Services that appear to have **limited or no active imports**:

| Service | Evidence | Recommendation |
|---------|----------|----------------|
| `watermark_service.py` | Only imported by watermark_integration.py | Verify if watermarking is used |
| `provenance_service.py` | Only imported by content/signals.py | Verify if signals are connected |
| `certificate_service.py` | Only imported by views_provenance.py | Verify if certificates are used |
| `discord_voice.py` | No visible imports found | Check Discord bot usage |
| `streaming_progress.py` | No visible imports in main code | May be frontend-only |
| `semantic_routing.py` | No visible imports | May be superseded by agent_router |
| `implicit_learning.py` | Only in __init__.py | Verify actual usage |
| `recommendation_engine.py` | Only in __init__.py, views_preferences.py | Verify actual usage |

---

## Duplicate/Overlapping Services

Potential redundancy identified:

| Group | Services | Notes |
|-------|----------|-------|
| **Collaboration** | `agent_collaboration.py`, `agent_collaboration_hub.py` | May be different purposes |
| **Watermarking** | `watermark_service.py`, `watermark_integration.py` | Integration wrapper exists |
| **Provenance** | `provenance_service.py`, `provenance_tracker.py` | Tracker appears more active |
| **Learning** | `agent_learning_service.py`, `implicit_learning.py`, `learning_loop.py` | Different scopes |

---

## Key Integration Patterns

### Most Connected Services (by import count)
1. `discord_notifications.py` - 15+ locations in tasks.py
2. `smart_trending_service.py` - PersonalAssistant, ContentWriterAgent
3. `collective_intelligence.py` - tasks.py, learning loops
4. `ml_scoring_engine.py` - tasks.py (multiple scoring tasks)

### Services With Views (Frontend Connected)
- `litigation_brain.py` → `views_legal.py`
- `stripe_subscription.py` → `views_stripe.py`
- `gumroad_publishing.py` → `views_platform_integrations.py`
- `workflow_analytics.py` → `views_workflow_analytics.py`
- `analytics_service.py` → `views_analytics.py`
- `ab_testing.py` → `views_ab_testing.py`

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Total service files | 67 |
| Super platform modules | 12 |
| Prompt modules | 3 |
| Assistant modules | 8 |
| Spider modules | 50+ |
| **Grand Total** | **140+** |

---

## Gaps Identified

1. **SuperPlatformCoordinator** - Exists but only used in `views_super_platform.py`, not by agents
2. **implicit_learning.py** - Exported but unclear if actively collecting data
3. **recommendation_engine.py** - Exported but unclear usage beyond preferences view
4. **semantic_routing.py** - May be superseded by deterministic agent_router

---

## Next Steps

- Agent 1.2 should verify which agents use these services
- Agent 2.1 (Prompting System Audit) should deep-dive super_platform usage
- Agent 2.5 (Learning System Audit) should verify learning services are connected

---

*Generated by Agent 1.1: Backend Services Discovery*
