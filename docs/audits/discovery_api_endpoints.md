# Agent 1.4: API Endpoints Discovery

**Date:** December 21, 2025
**Status:** Complete
**Total Endpoints Discovered:** 1200+ URL patterns

---

## Summary

Discovered **1268 path() calls** across **136 view files** totaling **100,667 lines of code**.

This is a massive API surface area covering all platform features.

---

## 1. View Files by Domain (136 files)

### Assistant & AI (15 files)
| File | Purpose | Endpoints |
|------|---------|-----------|
| views_assistant_intelligent.py | Main AI assistant | Multiple |
| views_assistant_minimal.py | Minimal assistant | Few |
| views_assistant_rag_enhanced.py | RAG-enhanced assistant | Few |
| views_personal_assistant_dev.py | Dev assistant | Few |
| views_unified_assistant.py | Unified assistant | Multiple |
| views_consciousness.py | Consciousness features | Multiple |
| views_consciousness_test.py | Consciousness testing | Few |
| views_command_center.py | AI Command Center | Multiple |
| views_ai_training.py | AI training dashboard | Multiple |
| views_ai_ecosystem.py | AI ecosystem | Multiple |
| views_ai_learning_api.py | Learning API | Multiple |
| views_agent_intelligence.py | Agent intelligence | 10+ |
| views_multi_llm.py | Multi-LLM support | Few |
| views_hive_mind.py | Hive Mind mode | 5 |
| views_visualization.py | AI visualization | Few |

### Agent System (20 files)
| File | Purpose | Endpoints |
|------|---------|-----------|
| views_agent_dashboard.py | Agent dashboard | 6 |
| views_agent_execution.py | Agent execution | Multiple |
| views_agent_hybrid.py | Hybrid agents | Few |
| views_agent_work_platform.py | Agent work | Multiple |
| views_agent_collaboration.py | Agent collaboration | 11 |
| views_agent_learning.py | Agent learning | 20+ |
| views_agent_tracking.py | Agent tracking | 4 |
| views_agent_evolution.py | Evolution system | 11 |
| views_agent_mood.py | Mood system | 9 |
| views_agent_relationships.py | Relationships | 14 |
| views_agent_training.py | Agent training | Multiple |
| views_agent_ecosystem.py | Agent ecosystem | Multiple |
| views_personality.py | Personalities | 6 |
| views_memory_palace.py | Memory Palace | 12 |
| views_memory_clusters.py | Memory clusters | 9 |
| views_predictions.py | Predictions | 9 |
| views_time_capsules.py | Time capsules | 8 |
| views_time_travel.py | Time travel debugging | 17 |
| views_collective_intelligence.py | Collective intelligence | Multiple |
| views_neural_orchestra.py | Neural orchestra | Multiple |

### Spider Network (5 files)
| File | Purpose | Endpoints |
|------|---------|-----------|
| views_spider_intelligence.py | Spider intelligence | 15+ |
| views_spider_dashboard.py | Spider dashboard | 11 |
| views_spider_data.py | Spider data | Multiple |
| views_intelligence_api.py | Intelligence API | 3 |
| views_unified_intelligence.py | Unified search | Multiple |

### Projects (10 files)
| File | Purpose | Endpoints |
|------|---------|-----------|
| views_projects.py | Project builder | 8 |
| views_projects_api.py | Project API | 20+ |
| views_project_builder.py | Project builder | Multiple |
| views_project_collaboration.py | Collaboration | 11 |
| views_portfolio.py | Portfolio | Multiple |
| views_business_ideas.py | Business ideas | 6 |
| views_partnership.py | Partnerships | Multiple |
| views_research_feedback.py | Research feedback | Multiple |
| views_solution_explorer.py | Solutions | Multiple |
| views_advanced_workflows.py | Advanced workflows | Multiple |

### Opportunities & Revenue (8 files)
| File | Purpose | Endpoints |
|------|---------|-----------|
| views_opportunity.py | Opportunities | 20+ |
| views_categorized_opportunities.py | Categories | Multiple |
| views_income_builder.py | Income builder | Multiple |
| views_income_action.py | Income actions | 6 |
| views_real_income_builder.py | Real income | Multiple |
| views_revenue.py | Revenue | Multiple |
| views_revenue_tracking.py | Revenue tracking | Multiple |
| views_revenue_analytics.py | Analytics | Multiple |

### Content & Creative (10 files)
| File | Purpose | Endpoints |
|------|---------|-----------|
| views_image.py | Image generation | Multiple |
| views_share.py | Content sharing | Multiple |
| views_character_training.py | Character training | Multiple |
| views_creative_director.py | Creative director | Multiple |
| views_davinci.py | DaVinci Resolve | Multiple |
| views_podcast.py | Podcast studio | 6 |
| views_campaign.py | Marketing campaigns | 8 |
| views_workflow.py | Workflows | Multiple |
| views_workflow_engine.py | Workflow engine | Multiple |
| views_workflow_analytics.py | Workflow analytics | Multiple |

### User & Profile (10 files)
| File | Purpose | Endpoints |
|------|---------|-----------|
| views_user_profile.py | User profile | Multiple |
| views_enhanced_profile.py | Enhanced profile | Multiple |
| views_profile.py | Profile | Multiple |
| views_profile_management.py | Profile management | Multiple |
| views_preferences.py | Preferences | 18+ |
| views_personal_memories.py | Personal memories | Multiple |
| views_isolation_control.py | Isolation control | Multiple |
| views_self_development.py | Self development | Multiple |
| views_learning_journey.py | Learning journey | Multiple |
| views_learning_path.py | Learning path | Multiple |

### Legal (2 files)
| File | Purpose | Endpoints |
|------|---------|-----------|
| views_legal.py | Legal assistant | 20+ |
| views_legal_api.py | Legal API | Multiple |

### Distribution & Marketplace (5 files)
| File | Purpose | Endpoints |
|------|---------|-----------|
| views_marketplace.py | Marketplace | 12 |
| views_distribution.py | Distribution | Multiple |
| views_auto_distribution.py | Auto distribution | Multiple |
| views_stripe.py | Stripe payments | Multiple |
| views_platform_integrations.py | Platform integrations | Multiple |

### Analytics & Diagnostics (8 files)
| File | Purpose | Endpoints |
|------|---------|-----------|
| views_analytics.py | Analytics | Multiple |
| views_dashboard_api.py | Dashboard API | Multiple |
| views_dashboard_stats.py | Dashboard stats | Multiple |
| views_diagnostics.py | Diagnostics | Multiple |
| views_verification_api.py | Verification | Multiple |
| views_public_stats.py | Public stats | Multiple |
| views_learning_dashboard.py | Learning dashboard | Multiple |
| views_learning_loop.py | Learning loop | Multiple |

### Testing & Misc (15 files)
| File | Purpose | Endpoints |
|------|---------|-----------|
| views_ab_testing.py | A/B testing | 7 |
| views_proactive.py | Proactive alerts | Multiple |
| views_advisor_api.py | Advisor API | 3 |
| views_ecosystem.py | Ecosystem stats | 5 |
| views_ecosystem_activation.py | Activation | Multiple |
| views_deploy.py | Deployment | 5 |
| views_auto_fix.py | Auto-fix | 1 |
| views_master_demo.py | Demo | Multiple |
| views_real_data.py | Real data | Multiple |
| views_super_platform.py | Super platform | Multiple |
| views.py | Core views | Multiple |
| views_unified*.py | Unified endpoints | Multiple |
| views_knowledge.py | Knowledge | Multiple |
| views_provenance.py | Provenance | Multiple |
| views_odds_sports.py | Sports betting | Multiple |

---

## 2. Major API Categories

### Assistant APIs
```
/api/assistant/chat/                    # Main chat endpoint
/api/assistant/intelligent/            # Intelligent assistant
/api/command-center/                   # AI Command Center
```

### Agent APIs
```
/api/agents/                           # Agent list
/api/agents/<id>/                      # Agent detail
/api/agents/<id>/execute/              # Execute agent
/api/agent-intelligence/...            # 10+ intelligence endpoints
/api/agent-collaboration/...           # 11 collaboration endpoints
/api/agent-learning/...                # 20+ learning endpoints
/api/agent-mood/...                    # 9 mood endpoints
/api/agent-evolution/...               # 11 evolution endpoints
/api/agent-relationships/...           # 14 relationship endpoints
/api/agent-conversations/              # Agent conversations
/api/agent-dreams/                     # Agent dreams
/api/agent-predictions/                # Predictions
/api/time-capsules/                    # Time capsules
/api/time-travel/                      # Time travel debugging
/api/hive-mind/                        # Hive Mind mode
/api/memory-palace/                    # Memory Palace
/api/memory-clusters/                  # Memory clusters
/api/personality/                      # Personalities
```

### Spider APIs
```
/api/spider/trending/                  # Trending topics
/api/spider/insights/                  # Market insights
/api/spider/tech-trends/               # Tech trends
/api/spider/jobs/                      # Job market
/api/spider/search/                    # Search data
/api/spider/registry/                  # Spider registry
/api/spider/dashboard/                 # Dashboard
/api/spider/execution-logs/            # Execution logs
/api/spider/health/                    # Health summary
```

### Project APIs
```
/api/projects/                         # Project list
/api/projects/<id>/                    # Project detail
/api/projects/<id>/agents/             # Project agents
/api/projects/<id>/research/           # Project research
/api/projects/<id>/export/             # Export project
/api/projects/<id>/export-content/     # Export content
/api/projects/<id>/update-content/     # Update content
/api/business-ideas/                   # Business ideas
/api/brand-recommendations/            # Brand recs
```

### Opportunity APIs
```
/api/opportunities/                    # List opportunities
/api/opportunities/<id>/               # Detail
/api/opportunities/<id>/score/         # Score
/api/opportunities/<id>/act/           # Take action
/api/opportunities/<id>/tasks/         # Tasks
/api/revenue/                          # Revenue
/api/income-action/                    # Income actions
```

### Legal APIs
```
/api/legal/cases/                      # Case list
/api/legal/cases/<id>/                 # Case detail
/api/legal/upload/                     # Document upload
/api/legal/analyze/                    # Motion analysis
/api/legal/conferral/                  # Conferral email
/api/legal/response-session/           # Response session
/api/legal/rewrite/                    # Motion rewrite
```

### Content APIs
```
/api/image/generate/                   # Image generation
/api/video/generate/                   # Video generation
/api/audio/generate/                   # Audio generation
/api/character/train/                  # Character training
/api/davinci/render/                   # DaVinci render
/api/podcasts/                         # Podcast studio
/api/campaigns/                        # Marketing campaigns
```

### Preference & Learning APIs
```
/api/preferences/                      # All preferences
/api/preferences/implicit/             # Implicit preferences
/api/preferences/recommendations/      # Style recommendations
/api/preferences/evolution/            # Style evolution
/api/ab-testing/                       # A/B testing
```

### Distribution APIs
```
/api/distribution/platforms/           # Platforms
/api/marketplace/                      # Marketplace
/api/marketplace/install/              # Install workflow
/api/marketplace/publish/              # Publish workflow
```

---

## 3. Endpoint Statistics

| Category | Approximate Count |
|----------|-------------------|
| Assistant/AI | 50+ |
| Agent System | 150+ |
| Spider Network | 50+ |
| Projects | 80+ |
| Opportunities | 60+ |
| Content Creation | 100+ |
| User/Profile | 80+ |
| Legal | 30+ |
| Distribution | 40+ |
| Analytics | 50+ |
| Workflows | 50+ |
| Misc/Testing | 100+ |
| **TOTAL** | **~840 unique endpoints** |

Note: 1268 path() calls includes some duplicates and includes patterns.

---

## 4. View File Statistics

| Metric | Count |
|--------|-------|
| View files | 136 |
| Total lines of code | 100,667 |
| Average LOC per file | ~740 |
| path() calls | 1,268 |

---

## 5. Potentially Dead Endpoints

Endpoints that may not be called by frontend:

| Endpoint | File | Concern |
|----------|------|---------|
| `/api/inject-test/` | views_agent_intelligence.py | Testing only |
| `/api/consciousness/test/` | views_consciousness_test.py | Testing only |
| `/api/master-demo/` | views_master_demo.py | Demo only |
| Various `/api/unified-*` | views_unified_*.py | May be legacy |

---

## 6. Gaps Identified

### P0 - Critical
1. **No API documentation** - 1200+ endpoints with no Swagger/OpenAPI

### P1 - High
2. **Inconsistent naming** - Some use hyphens, some underscores
3. **No versioning** - All endpoints at `/api/` root

### P2 - Medium
4. **Large view files** - Some views have 1000+ lines
5. **Dead endpoints** - Testing/demo endpoints in production

---

*Generated by Agent 1.4: API Endpoints Discovery*
