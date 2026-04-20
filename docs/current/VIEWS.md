<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`../PLATFORM_WHAT_IT_IS.md`](/docs/PLATFORM_WHAT_IT_IS.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality (Session 1099 verifier).

# Views Documentation

**Total View Files:** 143
**Location:** `core/views*.py`
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [View Categories](#view-categories)
3. [Complete View List](#complete-view-list)
4. [Key Views Detail](#key-views-detail)

---

## Overview

Views handle HTTP requests and render responses for the web UI. The platform has 143 view files organized by feature domain.

### Architecture
```
HTTP Request
     │
     ▼
Django URL Router (core/urls.py)
     │
     ▼
View Function/Class (core/views_*.py)
     │
     ├── Authentication Check
     ├── Business Logic (Services)
     ├── Database Queries (Models)
     └── Template Rendering
     │
     ▼
HTTP Response (HTML/JSON)
```

---

## View Categories

### Dashboard & Command Center (8)

| View File | Purpose |
|-----------|---------|
| `views_command_center.py` | Main command center dashboard |
| `views_dashboard_api.py` | Dashboard API endpoints |
| `views_dashboard_stats.py` | Dashboard statistics |
| `views_autonomous_dashboard.py` | Autonomous systems monitoring |
| `views_autonomous_monitoring.py` | Real-time autonomous monitoring |
| `views_autonomous_reasoning.py` | Reasoning visualization |
| `views_master_demo.py` | Demo dashboard |
| `views_public_stats.py` | Public statistics page |

### Agent System (18)

| View File | Purpose |
|-----------|---------|
| `views_agent_analytics.py` | Agent performance analytics |
| `views_agent_collaboration.py` | Multi-agent collaboration UI |
| `views_agent_dashboard.py` | Agent monitoring dashboard |
| `views_agent_ecosystem.py` | Ecosystem visualization |
| `views_agent_evolution.py` | XP and level progression UI |
| `views_agent_execution.py` | Execution monitoring |
| `views_agent_hybrid.py` | Hybrid agent features |
| `views_agent_intelligence.py` | Intelligence features |
| `views_agent_learning.py` | Learning system UI |
| `views_agent_mood.py` | Mood tracking and display |
| `views_agent_orchestration.py` | Orchestration UI |
| `views_agent_relationships.py` | Relationship visualization |
| `views_agent_tracking.py` | Agent activity tracking |
| `views_agent_training.py` | Agent training UI |
| `views_agent_work_platform.py` | Work platform features |
| `views_hive_mind.py` | Hive mind coordination |
| `views_collective_intelligence.py` | Collective intelligence UI |
| `views_neural_orchestra.py` | Neural orchestra visualization |

### Content & Media (12)

| View File | Purpose |
|-----------|---------|
| `views_content.py` | Content management |
| `views_content_calendar.py` | Content scheduling |
| `views_image.py` | Image generation UI |
| `views_video.py` | Video generation UI |
| `views_audio.py` | Audio generation UI |
| `views_podcast.py` | Podcast studio |
| `views_campaign.py` | Campaign orchestration |
| `views_creative_director.py` | Creative direction UI |
| `views_distribution.py` | Content distribution |
| `views_auto_distribution.py` | Automated distribution |
| `views_artifacts.py` | Artifact management |
| `views_share.py` | Content sharing |

### Intelligence & Research (12)

| View File | Purpose |
|-----------|---------|
| `views_intelligence_api.py` | Intelligence API endpoints |
| `views_spider_dashboard.py` | Spider network monitoring |
| `views_spider_data.py` | Spider data browsing |
| `views_spider_intelligence.py` | Spider intelligence analysis |
| `views_research_demo.py` | Research demonstration |
| `views_research_feedback.py` | Research feedback collection |
| `views_knowledge.py` | Knowledge management |
| `views_rag_embeddings.py` | RAG and embeddings UI |
| `views_visualization.py` | Data visualization |
| `views_real_data.py` | Real data display |
| `views_unified_intelligence.py` | Unified intelligence UI |
| `views_solution_explorer.py` | Solution exploration |

### Learning & Analytics (12)

| View File | Purpose |
|-----------|---------|
| `views_learning.py` | Learning system main |
| `views_learning_dashboard.py` | Learning analytics dashboard |
| `views_learning_journey.py` | User learning journey |
| `views_learning_loop.py` | Learning loop visualization |
| `views_learning_path.py` | Learning paths |
| `views_analytics.py` | General analytics |
| `views_workflow_analytics.py` | Workflow analytics |
| `views_revenue_analytics.py` | Revenue analytics |
| `views_roi_metrics.py` | ROI metrics |
| `views_revenue.py` | Revenue tracking |
| `views_revenue_tracking.py` | Detailed revenue tracking |
| `views_ab_testing.py` | A/B testing UI |

### User & Profile (10)

| View File | Purpose |
|-----------|---------|
| `views_profile.py` | User profile |
| `views_profile_management.py` | Profile management |
| `views_enhanced_profile.py` | Enhanced profile features |
| `views_user_profile.py` | User profile API |
| `views_portfolio.py` | User portfolio |
| `views_preferences.py` | User preferences |
| `views_personal_memories.py` | Personal memories UI |
| `views_personality.py` | Personality settings |
| `views_interview.py` | User interview/onboarding |
| `views_upload.py` | File upload handling |

### Betting & Markets (6)

| View File | Purpose |
|-----------|---------|
| `views_betting.py` | Betting dashboard |
| `views_predictions.py` | Prediction markets |
| `views_odds_sports.py` | Sports odds display |
| `views_income_action.py` | Income opportunities |
| `views_income_builder.py` | Income builder UI |
| `views_real_income_builder.py` | Real income tracking |

### Opportunities (5)

| View File | Purpose |
|-----------|---------|
| `views_opportunities.py` | Opportunities main |
| `views_opportunity.py` | Single opportunity |
| `views_categorized_opportunities.py` | Categorized view |
| `views_job_application_system.py` | Job applications |
| `views_business_ideas.py` | Business ideas |

### Legal (3)

| View File | Purpose |
|-----------|---------|
| `views_legal.py` | Legal assistant main |
| `views_legal_cases.py` | Case management |
| `views_provenance.py` | Data provenance |

### Workflow & Projects (8)

| View File | Purpose |
|-----------|---------|
| `views_workflow.py` | Workflow management |
| `views_workflow_engine.py` | Workflow engine |
| `views_advanced_workflows.py` | Advanced workflows |
| `views_projects.py` | Project management |
| `views_projects_api.py` | Projects API |
| `views_project_builder.py` | Project builder |
| `views_project_collaboration.py` | Project collaboration |
| `views_project_intelligence.py` | Project intelligence |

### Memory & Sci-Fi Features (6)

| View File | Purpose |
|-----------|---------|
| `views_memory_palace.py` | Memory palace visualization |
| `views_memory_clusters.py` | Memory clustering |
| `views_time_capsules.py` | Time capsules UI |
| `views_time_travel.py` | Time travel/decision replay |
| `views_consciousness.py` | Consciousness features |
| `views_consciousness_test.py` | Consciousness testing |

### Assistant & Chat (8)

| View File | Purpose |
|-----------|---------|
| `views_personal_assistant.py` | Personal assistant main |
| `views_personal_assistant_dev.py` | PA development mode |
| `views_assistant_bypass.py` | Assistant bypass mode |
| `views_assistant_intelligent.py` | Intelligent assistant |
| `views_assistant_minimal.py` | Minimal assistant |
| `views_assistant_rag_enhanced.py` | RAG-enhanced assistant |
| `views_unified_assistant.py` | Unified assistant |
| `views_advisor_api.py` | Advisor API |

### Integration & Platform (12)

| View File | Purpose |
|-----------|---------|
| `views_discord.py` | Discord integration |
| `views_stripe.py` | Stripe payments |
| `views_stripe_voice.py` | Stripe voice payments |
| `views_marketplace.py` | Marketplace |
| `views_voice_marketplace.py` | Voice marketplace |
| `views_platform_integrations.py` | Platform integrations |
| `views_partnership.py` | Partnership features |
| `views_davinci.py` | DaVinci Resolve UI |
| `views_character_training.py` | Character training |
| `views_ai_training.py` | AI training |
| `views_ai_ecosystem.py` | AI ecosystem |
| `views_ai_learning_api.py` | AI learning API |

### System & Admin (15)

| View File | Purpose |
|-----------|---------|
| `views_diagnostics.py` | System diagnostics |
| `views_validation.py` | Data validation |
| `views_verification_api.py` | Verification API |
| `views_auto_fix.py` | Auto-fix utilities |
| `views_deploy.py` | Deployment UI |
| `views_self_development.py` | Self-development |
| `views_session_handoff.py` | Session handoff |
| `views_ecosystem_activation.py` | Ecosystem activation |
| `views_isolation_control.py` | Isolation control |
| `views_push_notifications.py` | Push notifications |
| `views_proactive.py` | Proactive features |
| `views_proposals.py` | Proposals system |
| `views_multi_llm.py` | Multi-LLM support |
| `views_unified_placeholders.py` | Placeholder views |
| `views.py` | Base views |

### Unified & Bridge (6)

| View File | Purpose |
|-----------|---------|
| `views_unified.py` | Unified views |
| `views_unified_backend.py` | Unified backend |
| `views_unified_bridge.py` | Bridge views |
| `views_unified_metrics.py` | Unified metrics |
| `views_super_platform.py` | Super platform |
| `views_team_collaboration.py` | Team collaboration |

---

## Complete View List (143)

```
views.py
views_ab_testing.py
views_advanced_workflows.py
views_advisor_api.py
views_agent_analytics.py
views_agent_collaboration.py
views_agent_dashboard.py
views_agent_ecosystem.py
views_agent_evolution.py
views_agent_execution.py
views_agent_hybrid.py
views_agent_intelligence.py
views_agent_learning.py
views_agent_mood.py
views_agent_orchestration.py
views_agent_relationships.py
views_agent_tracking.py
views_agent_training.py
views_agent_work_platform.py
views_ai_ecosystem.py
views_ai_learning_api.py
views_ai_training.py
views_analytics.py
views_artifacts.py
views_assistant_bypass.py
views_assistant_intelligent.py
views_assistant_minimal.py
views_assistant_rag_enhanced.py
views_audio.py
views_auto_distribution.py
views_auto_fix.py
views_autonomous_dashboard.py
views_autonomous_monitoring.py
views_autonomous_reasoning.py
views_betting.py
views_business_ideas.py
views_campaign.py
views_categorized_opportunities.py
views_character_training.py
views_collaboration.py
views_collective_intelligence.py
views_command_center.py
views_consciousness.py
views_consciousness_test.py
views_content.py
views_content_calendar.py
views_creative_director.py
views_dashboard_api.py
views_dashboard_stats.py
views_davinci.py
views_deploy.py
views_diagnostics.py
views_discord.py
views_distribution.py
views_ecosystem.py
views_ecosystem_activation.py
views_enhanced_profile.py
views_hive_mind.py
views_image.py
views_income_action.py
views_income_builder.py
views_intelligence_api.py
views_interview.py
views_isolation_control.py
views_job_application_system.py
views_knowledge.py
views_learning.py
views_learning_dashboard.py
views_learning_journey.py
views_learning_loop.py
views_learning_path.py
views_legal.py
views_legal_cases.py
views_marketplace.py
views_master_demo.py
views_memory_clusters.py
views_memory_palace.py
views_multi_llm.py
views_neural_orchestra.py
views_odds_sports.py
views_opportunities.py
views_opportunity.py
views_partnership.py
views_personal_assistant.py
views_personal_assistant_dev.py
views_personal_memories.py
views_personality.py
views_platform_integrations.py
views_podcast.py
views_portfolio.py
views_predictions.py
views_preferences.py
views_proactive.py
views_profile.py
views_profile_management.py
views_project_builder.py
views_project_collaboration.py
views_project_intelligence.py
views_projects.py
views_projects_api.py
views_proposals.py
views_provenance.py
views_public_stats.py
views_push_notifications.py
views_rag_embeddings.py
views_real_data.py
views_real_income_builder.py
views_research_demo.py
views_research_feedback.py
views_revenue.py
views_revenue_analytics.py
views_revenue_tracking.py
views_roi_metrics.py
views_self_development.py
views_session_handoff.py
views_share.py
views_solution_explorer.py
views_spider_dashboard.py
views_spider_data.py
views_spider_intelligence.py
views_stripe.py
views_stripe_voice.py
views_super_platform.py
views_team_collaboration.py
views_time_capsules.py
views_time_travel.py
views_unified.py
views_unified_assistant.py
views_unified_backend.py
views_unified_bridge.py
views_unified_intelligence.py
views_unified_metrics.py
views_unified_placeholders.py
views_upload.py
views_user_profile.py
views_validation.py
views_verification_api.py
views_video.py
views_visualization.py
views_voice_marketplace.py
views_workflow.py
views_workflow_analytics.py
views_workflow_engine.py
```

---

## Key Views Detail

### views_command_center.py

Main command center dashboard providing unified system overview.

**Key Functions:**
- `command_center_dashboard()` - Main dashboard view
- `get_system_status()` - System health status
- `get_agent_summary()` - Agent overview
- `get_spider_summary()` - Spider network status

### views_agent_dashboard.py

Agent monitoring and management interface.

**Key Functions:**
- `agent_dashboard()` - Agent list and stats
- `agent_detail()` - Single agent view
- `agent_execution_history()` - Execution logs
- `agent_knowledge()` - Agent knowledge base

### views_spider_intelligence.py

Spider data analysis and intelligence features.

**Key Functions:**
- `spider_intelligence()` - Main intelligence view
- `trending_topics()` - Trending data
- `search_spider_data()` - Semantic search
- `spider_analytics()` - Collection analytics

### views_betting.py

Sports betting and prediction markets dashboard.

**Key Functions:**
- `betting_dashboard()` - Main betting UI
- `odds_display()` - Current odds
- `bankroll_management()` - Bankroll tracking
- `bet_history()` - Betting history

### views_memory_palace.py

Memory palace visualization for agent memories.

**Key Functions:**
- `memory_palace()` - Memory visualization
- `memory_room()` - Room detail
- `add_memory()` - Add new memory
- `search_memories()` - Semantic search

---

## URL Patterns

Views are mapped in `core/urls.py`. Example patterns:

```python
# Dashboard
path('command-center/', views_command_center.dashboard, name='command_center'),

# Agents
path('agents/', views_agent_dashboard.agent_list, name='agent_list'),
path('agents/<int:id>/', views_agent_dashboard.agent_detail, name='agent_detail'),

# Spiders
path('spiders/', views_spider_dashboard.dashboard, name='spider_dashboard'),
path('spiders/data/', views_spider_data.browse, name='spider_data'),
```

---

## Related Documentation

- [API_ENDPOINTS.md](API_ENDPOINTS.md) - REST API endpoints
- [WEBSOCKETS.md](WEBSOCKETS.md) - Real-time WebSocket consumers
- [SERVICES.md](SERVICES.md) - Business logic services
