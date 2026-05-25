<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md) and [`PLATFORM_WHAT_IT_IS.md`](/docs/PLATFORM_WHAT_IT_IS.md). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality.
> **Note:** content may be stale (last refreshed 2026-01-21) — referenced from `docs/topics/README.md` as a system architecture map. Verify component wiring against current `core/` modules before relying on specifics.

# UNIFIED DONKEY BETZ - SYSTEM WIREMAP

**Created:** Session 636 (December 30, 2025)
**Purpose:** Complete architecture map showing how all components connect

---

## System Scale

| Component | Count |
|-----------|-------|
| Django Models | 394 |
| Agents | 71 (47 routable, 24 sub-agents) |
| Spiders | 77 |
| Services | 93 |
| Celery Tasks | 53 scheduled |
| Discord Commands | 112 |
| WebSocket Endpoints | 26+ |
| Foreign Key Relationships | 292 |

---

## ENTRY POINTS

```
                    ┌─────────────────────────────────────────┐
                    │           ENTRY POINTS                   │
                    └─────────────────────────────────────────┘
                                      │
        ┌─────────────┬───────────────┼───────────────┬─────────────┐
        ▼             ▼               ▼               ▼             ▼
   ┌─────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌─────────┐
   │  HTTP   │  │ WebSocket │  │  Discord  │  │  Celery   │  │  Cron   │
   │  REST   │  │ Channels  │  │   Bot     │  │   Beat    │  │  Jobs   │
   └────┬────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────┬────┘
        │             │              │              │             │
        └─────────────┴──────────────┴──────────────┴─────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │       PersonalAssistantAgent            │
                    │  (Entry point router for all requests)  │
                    └─────────────────────────────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            ▼                         ▼                         ▼
   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │    Semantic     │    │     Keyword     │    │    Business     │
   │    Routing      │    │     Routing     │    │    Context      │
   │  (embeddings)   │    │    (regex)      │    │    Routing      │
   └────────┬────────┘    └────────┬────────┘    └────────┬────────┘
            └─────────────────────┬┴─────────────────────────┘
                                  ▼
                    ┌─────────────────────────────────────────┐
                    │            AgentRouter                  │
                    │    (Deterministic, no LLM needed)       │
                    └─────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │         AGENT_MAP → Execute Agent       │
                    └─────────────────────────────────────────┘
```

---

## AGENT ECOSYSTEM (71 Agents)

### 47 Routable Agents

| Category | Agents |
|----------|--------|
| **Creation (4)** | ImageAgent, VideoAgent, AudioAgent, ThreeDAgent |
| **Editing (2)** | ImageEditingAgent, VideoEditingAgent |
| **Research/Analysis (3)** | ResearchAgent, TrendAnalysisAgent, OpportunityScoringAgent |
| **Content/Strategy (9)** | ContentWriterAgent, ContentStrategyAgent, BrandIdentityAgent, SEOOptimizerAgent, SocialMediaAgent, TopicMinerAgent, ContrarianAgent, PerformanceAnalystAgent, ContentExecutorAgent |
| **Executive (4)** | CreativeDirectorAgent, CTOAgent, COOAgent, MeetingCoordinatorAgent |
| **Business/Markets (9)** | CompetitorAnalysisAgent, CustomerResearchAgent, BrandStrategyAgent, PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector, MarketingStrategyAgent, MarketIntelligenceAgent, CryptoAgent |
| **Development (4)** | CodeGeneratorAgent, FullStackDeveloperAgent, CodeReviewAgent, DevOpsAgent |
| **Security/Audit (7)** | MemoryIsolationAgent, ContentAuditAgent, BlockchainAuditCoordinator, StockAuditCoordinator, MarketIntelligenceCoordinator, etc. |
| **Orchestration (6)** | WorkflowAgent, WorkflowOrchestrationAgent, AutonomousContentStudioCoordinator, PodcastCoordinatorAgent, CampaignOrchestratorAgent, AISeriesWorkflowAgent |
| **Special (3)** | PersonalAssistantAgent, ResolveAgent, ThinkingAgent |

### 24 Non-Routable Sub-Agents

Managed by coordinator agents:

| Coordinator | Sub-Agents |
|-------------|------------|
| **BlockchainAuditCoordinator** | SmartContractAuditAgent, TransactionMonitorAgent, WhaleWatcherAgent, ExploitDetectorAgent |
| **StockAuditCoordinator** | StockAnalystAgent, MarketMovementMonitorAgent, InstitutionalWatcherAgent, MarketAnomalyDetectorAgent, BullCaseAgent, BearCaseAgent, SignalScannerAgent |
| **AutonomousContentStudioCoordinator** | TopicMinerAgent, ContrarianAgent, PerformanceAnalystAgent |
| **NarrativeDriftCoordinator** | NarrativeHistorianAgent, TrendBreakDetectorAgent, CulturalImpactAgent |
| **PodcastCoordinatorAgent** | DebateAdvocateAgent, DebateSkepticAgent, ModeratorAgent |

---

## SPIDER NETWORK (77 Spiders)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SPIDER NETWORK                                │
└─────────────────────────────────────────────────────────────────────┘
        │
        ├── News/Media (10): TechCrunch, TheVerge, BBC, CNN, NPR,
        │                     Reuters, NewsAPI, HackerNews, DevTo, Ars
        │
        ├── Financial (9): CoinGecko, YahooFinance, Polygon, Finnhub,
        │                   Kalshi, TheOdds, SEC Edgar, Crypto APIs
        │
        ├── Tech (8): GitHub, Stack Overflow, npm, PyPI, Kickstarter,
        │              Google Trends, ProductHunt
        │
        ├── Legal (6): CourtListener, FindLaw, LII, Colorado Family Law,
        │               Justia, Government
        │
        ├── Education (5): Teachable, Udemy, Coursera, Kaggle, SkillShare
        │
        ├── Specialty (5): DefenseOne, MobiHealthNews, SecurityWeek,
        │                   Wired, MIT Tech Review
        │
        ├── Community (4): Reddit (8 subs), BlueSky, Discord
        │
        ├── Entertainment (4): Spotify, Giphy, YouTube, Polygon Gaming
        │
        ├── Lifestyle (4): Lifehacker, Travel, Parenting, Food
        │
        └── Other (22): Startups, AI/ML, Jobs, Weather, Science, etc.
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Data Methods: REST API (32), RSS (30), Web Scrape (10),            │
│                Playwright (2), JSON (3)                              │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SpiderData Model (6,500+ records) → Embeddings → Vector DB         │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│              Agents search via SpiderSemanticSearchService           │
└─────────────────────────────────────────────────────────────────────┘
```

---

## CELERY TASK ORCHESTRATION (53 Scheduled Tasks)

### Task Chains

```
1. SPIDER PIPELINE (every 15 min)
   run_spider_network()
       → backfill_spider_embeddings()
       → process_spider_data_automatic()

2. LEARNING CYCLE (continuous)
   agent_learning_cycle() [10 min]
       → agent_think_and_synthesize() [30 min]
       → update_agent_effectiveness() [daily]

3. OPPORTUNITY ENGINE (continuous)
   run_spider_network()
       → score_opportunities_from_spider_data() [hourly]
       → send_proactive_opportunity_alerts() [30 min]

4. DECISION PIPELINE (continuous)
   run_agent_conversation() [30 min]
       → batch_extract_artifacts() [hourly]
       → auto_promote_decisions() [30 min]
       → execute_approved_artifacts() [15 min]

5. DREAM LIFECYCLE (continuous)
   generate_agent_dreams() [15 min]
       → score_and_promote_dreams() [20 min]
       → execute_dream_implementations() [20 min]

6. CONTENT STUDIO (continuous)
   autonomous_content_studio_loop() [hourly]
       → track_content_performance() [daily 8 PM]

7. MARKET INTELLIGENCE (trading hours + passive)
   stock_audit_cycle() [30 min]
       → market_intelligence_desk() [8 AM]
       → market_movement_alerts() [30 min]

8. PREDICTION MARKETS (every 30 min)
   collect_kalshi_prediction_markets()
       → collect_kalshi_market_intelligence() [4 hours]

9. SPORTS BETTING (continuous)
   collect_sports_odds() [hourly]
       → snapshot_odds_for_line_movement() [20 min]
       → scan_arbs_and_notify() [5 min]

10. NARRATIVE DRIFT (every 4 hours)
    narrative_drift_detector_cycle()
        → narrative_shifts_to_content()
        → publish content

11. BROADCAST STATUS (every 60 seconds)
    broadcast_learning_status()
    broadcast_dream_journal()
    broadcast_relationship_status()
    broadcast_evolution_status()

12. 14 AUTONOMOUS SITUATIONS
    design_trends, viral_predictor, job_match, crypto_sentiment,
    earnings_predictor, tech_stack_tracker, ai_model_monitor,
    skill_gap_analyzer, case_law_monitor, regulatory_detector, etc.
```

---

## LEARNING SYSTEM (10 Learning Bridges)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EVENT-DRIVEN LEARNING                             │
│                  (Django signals trigger bridges)                    │
└─────────────────────────────────────────────────────────────────────┘

  post_save(SpiderData)       → SpiderDataLearningBridge
  post_save(AgentExecution)   → AgentExecutionBridge
  Opportunity outcome         → ApplicationOutcomeBridge
  Revenue recorded            → RevenueAttributionBridge
  Collaboration complete      → CollaborationBridge
  User interaction            → PersonalizationBridge
  Advisor feedback            → AdvisorFeedbackBridge
  Sports bet result           → SportsBettingBridge
                                    │
                                    ▼
                        ┌─────────────────────┐
                        │  UserAgentLearning  │
                        │      records        │
                        └─────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
  │  Agent Context  │    │ KnowledgeTransfer│    │   Collective    │
  │ (future improve)│    │ (agent-to-agent) │    │  Intelligence   │
  └─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## WEBSOCKET HUB (26+ Real-Time Endpoints)

| Endpoint | Consumer | Purpose |
|----------|----------|---------|
| `/ws/assistant/` | PersonalAssistantV2Consumer | Chat interface |
| `/ws/activity/` | AgentProgressConsumer | Agent work tracking |
| `/ws/consciousness/` | ConsciousnessConsumer | Self-awareness |
| `/ws/command-center/` | CommandCenterAIConsumer | Decision center |
| `/ws/spider-updates/` | SpiderWebSocketConsumer | Data updates |
| `/ws/project-progress/*` | ProjectProgressConsumer | Build progress |
| `/ws/ai-training/` | AITrainingConsumer | Learning status |
| `/ws/agent-platform/` | AgentPlatformConsumer | Money-making |
| `/ws/decisions/` | CommandCenterConsumer | Decision tracking |
| `/ws/notifications/` | NotificationConsumer | Alerts |
| `/ws/agent-monitor/` | AgentMonitorConsumer | Agent status |
| `/ws/deliverables/` | DeliverablesConsumer | Output tracking |
| `/ws/mythology/` | MythologyConsumer | Content review |
| ... | ... | 13 more endpoints |

---

## SERVICE LAYER (93 Services)

| Category | Count | Examples |
|----------|-------|----------|
| Decision Management | 8 | decision_executor, decision_extraction, artifact_execution, concern_tracker |
| Content/Creation | 12 | ai_content_agents, content_pipeline, smart_trending_service, creative_orchestrator |
| Learning | 8 | agent_learning_service, collective_intelligence, boardroom_learning, knowledge_transfer |
| Analysis/Scoring | 8 | spider_semantic_search, scoring_dispatcher, deduplication_service, anomaly_detection |
| Data Integration | 10 | blockchain_event_listener, push_notification_service, ab_testing, experiment_metrics |
| System Services | 15+ | agent_intelligence_context, system_state_aggregator, event_bus, cache_manager |

### Key Service Dependencies

```
AgentLearningService
    → UserAgentLearning model
    → Agent effectiveness updates

ContentPipelineService
    → ImageAgent, VideoAgent, AudioAgent
    → ContentAsset creation

ArtifactExecutionService
    → AgentRouter
    → specialized agent execution

DecisionExecutorService
    → Decision model
    → Discord/WebSocket notifications

SpiderSemanticSearchService
    → vector DB
    → ResearchAgent queries
```

---

## DATABASE MODEL CLUSTERS (394 Models)

### Core Models (core/models_unified_system.py)

| Model | Purpose |
|-------|---------|
| Agent | 71 agents tracked |
| Decision | pending/approved/executed |
| UserAgentLearning | learning records |
| AgentConversation | inter-agent chats |
| SpiderData | 6,500+ crawled records |
| OpportunityScore | scored opportunities |
| KnowledgeTransfer | agent-to-agent learning |
| CollectiveIntelligence | hive mind votes |
| ConversationMemory | memory tracking |

### Other Model Files (15+)

- **Content Pipeline:** ContentAsset, StyleEvolution, PerformanceMetric
- **Agent Memory:** AgentDream, AgentMood, AgentRelationship, AgentEvolution
- **Conversation Artifacts:** ExtractedArtifact, ReviewDocument, SideChat
- **Narrative Drift:** NarrativeDrift
- **Odds History:** OddsSnapshot (line movement)
- **Podcast Studio:** PodcastSeries, PodcastEpisode
- **AI Series:** AISeriesTemplate, AISeriesInstance
- **Legal:** LegalDocument
- **Projects:** Project, ProjectPhase, ProjectTask
- **System:** SystemState, HealthMetric
- **Sports:** Prediction, UserBet, BetResult
- **Content:** ContentAnalytics, ContentDistribution
- **Intelligence:** Opportunity, JobApplication

### Key Relationships (292 total)

| Target | ~Count |
|--------|--------|
| Most models → User | 100+ |
| Most models → Agent | 50+ |
| Many models → Decision | 30+ |
| Many models → Project | 25+ |
| Some models → SpiderData | 15+ |

---

## CRITICAL DATA FLOW

### Opportunity Discovery → Decision → Execution → Learning

```
1. Celery: run_spider_network() [every 15 min]
   │
   ▼
2. SpiderData created (100+ records per run)
   │
   ▼
3. Signal: post_save(SpiderData)
   │
   ▼
4. SpiderDataLearningBridge: extract patterns & route to agents
   │
   ▼
5. score_opportunities_from_spider_data() [hourly]
   ├─ ML model scores
   └─ Creates OpportunityScore
   │
   ▼
6. send_proactive_opportunity_alerts() [every 30 min]
   ├─ Filter for user preferences
   └─ Create Notification
   │
   ▼
7. User approval → Decision created
   │
   ▼
8. execute_approved_artifacts() [every 15 min]
   ├─ Call specialized agents
   └─ Create AgentExecution
   │
   ▼
9. Signal: post_save(AgentExecution)
   │
   ▼
10. AgentExecutionBridge processes
    ├─ Extract patterns
    ├─ Update effectiveness
    └─ Create UserAgentLearning
    │
    ▼
11. LEARNING RECORDED → Future decisions improved
```

---

## ARCHITECTURE SUMMARY

This is fundamentally a **REQUEST → ROUTE → EXECUTE → LEARN → IMPROVE** loop running 24/7:

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   ENTRY                                                              │
│   HTTP, WebSocket, Discord, Celery                                   │
│        │                                                             │
│        ▼                                                             │
│   ROUTE                                                              │
│   PersonalAssistantAgent + semantic/keyword/context routing          │
│        │                                                             │
│        ▼                                                             │
│   EXECUTE                                                            │
│   71 agents + 93 services calling 77 spiders                        │
│        │                                                             │
│        ▼                                                             │
│   LEARN                                                              │
│   10 learning bridges process events via Django signals              │
│        │                                                             │
│        ▼                                                             │
│   IMPROVE                                                            │
│   UserAgentLearning + KnowledgeTransfer inform future decisions     │
│        │                                                             │
│        └──────────────────────────────────────────────────────┐     │
│                                                                │     │
└────────────────────────────────────────────────────────────────┴─────┘
                              (continuous loop)
```

### Key Metrics Monitored

- Agent effectiveness scores
- Decision approval rates
- Learning patterns discovered
- Dream productivity
- Content performance
- Celery task health
- Spider data quality
- Market opportunities
- Prediction accuracy
- Experiment KPIs

---

## Quick Reference

| What | Where |
|------|-------|
| Agent routing | `core/agent_router.py` |
| All agents | `core/agents/` |
| Celery tasks | `core/tasks.py` |
| Celery schedules | `core/celery.py` |
| Learning bridges | `core/learning_bridges/` |
| Services | `core/services/` |
| Spiders | `ai_core/spiders/` |
| WebSocket consumers | `core/consumers/` |
| Discord commands | `core/services/discord_bot.py` |
| Models | `core/models*.py` |
