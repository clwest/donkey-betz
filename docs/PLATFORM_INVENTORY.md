# Platform Master Inventory

**Generated:** 2026-05-22 20:05:30
**Git HEAD:** `1c113da7`

> Runtime-derived snapshot of the Donkey Betz platform. Regenerate with `python manage.py generate_platform_inventory`.
> Companion to `core/services/doc_claim_verification.py` — this doc captures the ground truth; the verifier flags where doc claims drift from it.

## Executive Summary

| Subsystem | Headline |
|---|---|
| [Agents](#agents) | 83 agents in AGENT_MAP (74 enabled, 8 rerouted, 1 blocked); 151 rows in Agent table. |
| [Spiders](#spiders) | 80 spiders across 41 categories (80 working, 0 placeholder) |
| [Services](#services) | 112 `*Service` classes across 332 files in core/services/ |
| [Celery Tasks](#celery-tasks) | 398 user-defined Celery tasks (excludes celery.* internals) |
| [Celery Beat — Scheduled Tasks](#beat-schedule) | 78 enabled + 0 disabled = 78 PeriodicTask rows |
| [Personal Assistant (PA) Tools](#pa-tools) | 103 tool schemas + 168 registered handlers; 8 enrichment services |
| [Database Models](#database-models) | 581 concrete models across 23 apps |
| [URL Routes](#url-routes) | 1854 path() patterns across all core/urls*.py files |
| [Django View Files](#views-files) | 206 files matching core/views*.py |
| [Django Management Commands](#management-commands) | 178 management commands in core/management/commands/ |
| [Discord Integration](#discord) | 96 @*.command decorators, 48 @app_commands.command, 25 Cog classes in discord_bot.py |
| [Body Systems](#body-systems) | 9 body systems monitored by run_all_systems_scan |
| [LLM Providers](#llm-providers) | 6 providers registered in LLMProviderRegistry |
| [Signal Intelligence](#signal-intelligence) | 10 SignalCluster pattern types, MIN_CLUSTER_SIZE=3 |
| [AgentMemory Types](#memory-types) | 7 memory types tracked by AgentMemory model |
| [Content Pipeline](#content-pipeline) | 3 reviewer classes referenced, 9 content domains, max_claims default=20 |
| [Initiative Pipeline](#initiative-pipeline) | 5 pipeline stages (auto-dispatch on stages [4, 5]) |
| [Frontend (React + Vite)](#frontend) | 61 routes in App.tsx, 5 workspace primary tabs, 9 betting dashboard tabs |
| [Infrastructure](#infrastructure) | 10 Procfile processes, 3 distinct Redis DB indices in settings |
| [Code Statistics](#code-stats) | 2,027 Python files, 988,861 lines across core/ + ai_core/ + intelligence/ |
| [Doc-vs-Reality Verifier State](#verifier-state) | 73 registered claims across 34 docs: 72 OK, 1 drifts |

## Table of Contents

- [Agents](#agents)
- [Spiders](#spiders)
- [Services](#services)
- [Celery Tasks](#celery-tasks)
- [Celery Beat — Scheduled Tasks](#beat-schedule)
- [Personal Assistant (PA) Tools](#pa-tools)
- [Database Models](#database-models)
- [URL Routes](#url-routes)
- [Django View Files](#views-files)
- [Django Management Commands](#management-commands)
- [Discord Integration](#discord)
- [Body Systems](#body-systems)
- [LLM Providers](#llm-providers)
- [Signal Intelligence](#signal-intelligence)
- [AgentMemory Types](#memory-types)
- [Content Pipeline](#content-pipeline)
- [Initiative Pipeline](#initiative-pipeline)
- [Frontend (React + Vite)](#frontend)
- [Infrastructure](#infrastructure)
- [Code Statistics](#code-stats)
- [Doc-vs-Reality Verifier State](#verifier-state)

<a id="agents"></a>
## Agents

**Headline:** 83 agents in AGENT_MAP (74 enabled, 8 rerouted, 1 blocked); 151 rows in Agent table.

**Code location:** `core/agent_router.py AGENT_MAP`

**Notes:** AGENT_MAP total = 83 (74 enabled + 8 rerouted + 1 blocked). DB Agent rows = 151. Top agent_type breakdown: income=20, content=17, career=15, business=14, job_search=12, finance=12, ai_ml=11, creative=11, marketing=10, analytics=7. Blocked: ['CodeGeneratorAgent']. Rerouted: ['AudioAgent', 'COOAgent', 'CTOAgent', 'CodeReviewAgent', 'DevOpsAgent', 'FullStackDeveloperAgent', 'VideoAgent', 'WorkflowAgent'].

| Name | Module | Status |
|---|---|---|
| AISeriesWorkflowAgent | core.agents.ai_series_workflow_agent | enabled |
| ArbitrageDetector | core.agents.markets.arbitrage_detector | enabled |
| AudioAgent | core.agents.audio_agent | rerouted |
| AutonomousContentStudioCoordinator | core.agents.autonomous_content_studio_coordinator | enabled |
| BearCaseAgent | core.agents.stocks.bear_case_agent | enabled |
| BlockchainAuditCoordinator | core.agents.blockchain.blockchain_audit_coordinator | enabled |
| BookmakerAgent | core.agents.bookmaker_agent | enabled |
| BrandIdentityAgent | core.agents.strategy.brand_identity_agent | enabled |
| BrandStrategyAgent | core.agents.business.brand_strategy_agent | enabled |
| BullCaseAgent | core.agents.stocks.bull_case_agent | enabled |
| COOAgent | core.agents.executive.coo_agent | rerouted |
| CTOAgent | core.agents.executive.cto_agent | rerouted |
| CampaignOrchestratorAgent | core.agents.campaign_orchestrator_agent | enabled |
| CharacterTrainingAgent | core.agents.training.character_training_agent | enabled |
| CodeGeneratorAgent | core.agents.code_generator_agent | blocked |
| CodeReviewAgent | core.agents.code_review_agent | rerouted |
| CompetitorAnalysisAgent | core.agents.business.competitor_analysis_agent | enabled |
| ContentAuditAgent | core.agents.security.content_audit_agent | enabled |
| ContentDiversityOrchestrator | core.agents.content_diversity_orchestrator | enabled |
| ContentExecutorAgent | core.agents.content_executor_agent | enabled |
| ContentStrategyAgent | core.agents.strategy.content_strategy_agent | enabled |
| ContentWriterAgent | core.agents.content_writer_agent | enabled |
| ContrarianAgent | core.agents.content.contrarian_agent | enabled |
| CreativeDirectorAgent | core.agents.executive.creative_director_agent | enabled |
| CulturalImpactAgent | core.agents.narrative.cultural_impact_agent | enabled |
| CustomerResearchAgent | core.agents.business.customer_research_agent | enabled |
| DebateAdvocateAgent | core.agents.podcast.debate_advocate_agent | enabled |
| DebateSkepticAgent | core.agents.podcast.debate_skeptic_agent | enabled |
| DecisionEnforcerAgent | core.agents.decision_enforcer_agent | enabled |
| DevOpsAgent | core.agents.devops_agent | rerouted |
| DistributionAgent | core.agents.distribution_agent | enabled |
| EditorAgent | core.agents.editor_agent | enabled |
| ExploitDetectorAgent | core.agents.blockchain.exploit_detector_agent | enabled |
| FullStackDeveloperAgent | core.agents.fullstack_developer_agent | rerouted |
| GamePredictor | core.agents.markets.game_predictor | enabled |
| ImageAgent | core.agents.image_agent | enabled |
| ImageEditingAgent | core.agents.image_editing_agent | enabled |
| InstitutionalWatcherAgent | core.agents.stocks.institutional_watcher_agent | enabled |
| LegalDocDrafterAgent | core.agents.legal.legal_doc_drafter_agent | enabled |
| LineMovementAnalyzer | core.agents.markets.line_movement_analyzer | enabled |
| MarketAnomalyDetectorAgent | core.agents.stocks.market_anomaly_detector_agent | enabled |
| MarketIntelligenceAgent | core.agents.analysis.market_intelligence_agent | enabled |
| MarketIntelligenceCoordinator | core.agents.stocks.market_intelligence_coordinator | enabled |
| MarketMovementMonitorAgent | core.agents.stocks.market_movement_monitor_agent | enabled |
| MarketingStrategyAgent | core.agents.business.marketing_strategy_agent | enabled |
| MeetingCoordinatorAgent | core.agents.executive.meeting_coordinator_agent | enabled |
| MemoryIsolationAgent | core.agents.security.memory_isolation_agent | enabled |
| ModeratorAgent | core.agents.podcast.moderator_agent | enabled |
| NarrativeDriftCoordinator | core.agents.narrative.narrative_drift_coordinator | enabled |
| NarrativeHistorianAgent | core.agents.narrative.narrative_historian_agent | enabled |
| OpportunityPipelineAgent | core.agents.opportunity_pipeline_agent | enabled |
| OpportunityScoringAgent | core.agents.analysis.opportunity_scoring_agent | enabled |
| PerformanceAnalystAgent | core.agents.content.performance_analyst_agent | enabled |
| PlatformAuditAgent | core.agents.platform_audit_agent | enabled |
| PodcastCoordinatorAgent | core.agents.podcast.podcast_coordinator_agent | enabled |
| PredictionMarketAnalyst | core.agents.markets.prediction_market_analyst | enabled |
| PromptEngineeringAgent | core.agents.prompt_engineering_agent | enabled |
| ResearchAgent | core.agents.research_agent | enabled |
| ResolveAgent | core.agents.resolve_agent | enabled |
| SEOOptimizerAgent | core.agents.strategy.seo_optimizer_agent | enabled |
| SharpActionDetector | core.agents.markets.sharp_action_detector | enabled |
| SignalScannerAgent | core.agents.stocks.signal_scanner_agent | enabled |
| SmartContractAuditorAgent | core.agents.blockchain.smart_contract_auditor_agent | enabled |
| SocialMediaAgent | core.agents.strategy.social_media_agent | enabled |
| SportsOddsAnalyst | core.agents.markets.sports_odds_analyst | enabled |
| StockAnalystAgent | core.agents.stocks.stock_analyst_agent | enabled |
| StockAuditCoordinator | core.agents.stocks.stock_audit_coordinator | enabled |
| SystemIntelligenceAgent | core.agents.system_intelligence_agent | enabled |
| TalkingCharacterAgent | core.agents.talking_character_agent | enabled |
| TechnicalDocumentAgent | core.agents.technical_document_agent | enabled |
| ThinkingAgent | core.agents.thinking_agent | enabled |
| ThreeDAgent | core.agents.three_d_agent | enabled |
| TopicMinerAgent | core.agents.content.topic_miner_agent | enabled |
| TrainedCreationAgent | core.agents.training.trained_creation_agent | enabled |
| TransactionMonitorAgent | core.agents.blockchain.transaction_monitor_agent | enabled |
| TrendAnalysisAgent | core.agents.analysis.trend_analysis_agent | enabled |
| TrendBreakDetectorAgent | core.agents.narrative.trend_break_detector_agent | enabled |
| VideoAgent | core.agents.video_agent | rerouted |
| VideoEditingAgent | core.agents.video_editing_agent | enabled |
| VoiceCriticAgent | core.agents.content.voice_critic_agent | enabled |
| WhaleWatcherAgent | core.agents.blockchain.whale_watcher_agent | enabled |
| WorkflowAgent | core.agents.workflow_agent | rerouted |
| WorkflowOrchestrationAgent | core.agents.workflow_orchestration_agent | enabled |

<a id="spiders"></a>
## Spiders

**Headline:** 80 spiders across 41 categories (80 working, 0 placeholder)

**Code location:** `ai_core/spiders/spider_registry.py`

**Notes:** Working (non-placeholder): 80. Categories (41): top 10 by count — tech=8, news=8, financial=7, legal=6, education=4, content=3, community=3, startups=2, innovation=2, design=2.

| Name | Category | Class | Priority | Placeholder |
|---|---|---|---|---|
| adzuna | jobs | AdzunaSpider | 1 | no |
| arstechnica | tech | ArsTechnicaSpider | 1 | no |
| awwwards | design | BaseIntelligenceSpider | 1 | no |
| axios | news | AxiosSpider | 1 | no |
| bbc | news | BBCSpider | 1 | no |
| behance | design | BehanceSpider | 1 | no |
| bluesky | social | BlueSkySpider | 1 | no |
| business_news | business | BusinessNewsSpider | 1 | no |
| coingecko | financial | CoinGeckoSpider | 1 | no |
| colorado_family_law | legal | ColoradoFamilyLawSpider | 1 | no |
| coursera | education | BaseIntelligenceSpider | 1 | no |
| courtlistener | legal | CourtListenerSpider | 2 | no |
| crunchbase | startups | CrunchbaseSpider | 1 | no |
| defenseone | defense_tech | DefenseOneSpider | 1 | no |
| devto | tech | DevToSpider | 1 | no |
| discord | community | DiscordSpider | 1 | no |
| discord_training | training | DiscordTrainingSpider | 2 | no |
| education_rss | education | EducationRSSSpider | 1 | no |
| etherscan | financial | EtherscanSpider | 1 | no |
| etherscan_api | blockchain | EtherscanAPISpider | 1 | no |
| financial | financial | FinancialIntelligenceSpider | 1 | no |
| findlaw | legal | FindLawSpider | 2 | no |
| finnhub | financial | FinnhubSpider | 1 | no |
| food | food | FoodSpider | 1 | no |
| freecodecamp | tech | BaseIntelligenceSpider | 1 | no |
| giphy | social | GiphySpider | 2 | no |
| github | tech | GitHubSpider | 1 | no |
| github_jobs | tech | TechCommunitySpider | 2 | no |
| google_news | news | BaseIntelligenceSpider | 1 | no |
| government | government | GovernmentSpider | 1 | no |
| hackernews | tech | HackerNewsSpider | 1 | no |
| hackernoon | community | BaseIntelligenceSpider | 1 | no |
| health | health | HealthSpider | 1 | no |
| huggingface | ai_ml | HuggingFaceSpider | 1 | no |
| justia_family_law | legal | JustiaPlaywrightSpider | 1 | no |
| kaggle | ai_ml | KaggleSpider | 1 | no |
| kalshi | prediction_markets | KalshiSpider | 1 | no |
| kickstarter | tech | KickstarterSpider | 1 | no |
| legal_news | legal | LegalNewsSpider | 2 | no |
| legislation | legislation | LegislationSpider | 1 | no |
| library | library | LibrarySpider | 1 | no |
| lifehacker | lifestyle | LifehackerSpider | 1 | no |
| lii | legal | LegalInformationInstituteSpider | 2 | no |
| medium | content | MediumIntelligenceSpider | 2 | no |
| mit_tech_review | innovation | MITTechReviewSpider | 1 | no |
| mobihealthnews | healthtech | MobiHealthNewsSpider | 1 | no |
| newsapi | news | NewsAPISpider | 1 | no |
| noaa_weather | weather | NOAASpider | 2 | no |
| npr | news | NPRSpider | 1 | no |
| openmeteo | weather | OpenMeteoSpider | 1 | no |
| parenting | parenting | ParentingSpider | 1 | no |
| polygon_finance | financial | PolygonSpider | 1 | no |
| polygon_gaming | gaming | PolygonGamingSpider | 1 | no |
| producthunt | content | ContentMonetizationSpider | 2 | no |
| real_estate | real_estate | RealEstateSpider | 1 | no |
| reddit | community | RedditSpider | 1 | no |
| remoteok | remote_work | RemoteOKSpider | 2 | no |
| reuters_rss | news | ReutersRSSSpider | 1 | no |
| science | science | ScienceSpider | 1 | no |
| sec_edgar | financial | SECSpider | 1 | no |
| securityweek | cybersecurity | SecurityWeekSpider | 1 | no |
| smashingmagazine | web_development | SmashingMagazineSpider | 1 | no |
| sports_injuries | sports_injuries | BaseIntelligenceSpider | 1 | no |
| sports_news | sports_news | BaseIntelligenceSpider | 1 | no |
| spotify | entertainment | SpotifySpider | 2 | no |
| substack | content | ContentMonetizationSpider | 2 | no |
| teachable | education | TeachableSpider | 1 | no |
| techcrunch | news | TechCrunchSpider | 1 | no |
| techcrunch_startups | tech | BaseIntelligenceSpider | 1 | no |
| theodds | sports_odds | TheOddsSpider | 1 | no |
| theverge | news | TheVergeSpider | 1 | no |
| travel | travel | TravelSpider | 1 | no |
| udemy | education | UdemySpider | 1 | no |
| unsplash | visual_trends | UnsplashSpider | 1 | no |
| variety | entertainment | VarietySpider | 1 | no |
| venturebeat | startups | VentureBeatSpider | 1 | no |
| weworkremotely | freelance | WeWorkRemotelySpider | 1 | no |
| wired | innovation | WiredSpider | 1 | no |
| yahoo_finance | financial | YahooFinanceSpider | 1 | no |
| youtube | video | YouTubeSpider | 1 | no |

<a id="services"></a>
## Services

**Headline:** 112 `*Service` classes across 332 files in core/services/

**Code location:** `core/services/`

| Class | File |
|---|---|
| ABTestingService | core/services/ab_testing.py |
| AIDecisionPromoterService | core/services/ai_decision_promoter.py |
| ATSKeywordService | core/services/ats_keyword_service.py |
| AgentCollaborationService | core/services/agent_collaboration.py |
| AgentContributionService | core/services/agent_contribution.py |
| AgentFeedbackService | core/services/agent_feedback_service.py |
| AgentIntelligenceContextService | core/services/agent_intelligence_context.py |
| AgentIntelligenceService | core/services/ai_content_agents.py |
| AgentLearningService | core/services/agent_learning_service.py |
| AgentTrainingService | core/services/agent_training.py |
| AnalyticsService | core/services/analytics_service.py |
| ArtifactExecutionService | core/services/artifact_execution.py |
| ArtifactExtractionService | core/services/artifact_extraction.py |
| AuditTrackerService | core/services/audit_tracker.py |
| AutoKPITrackingService | core/services/auto_kpi_tracking.py |
| AutoSpawnerService | core/services/auto_spawner_service.py |
| BoardroomLearningService | core/services/boardroom_learning.py |
| BoardroomLearningService | core/services/boardroom_learning_service.py |
| BoardroomMLService | core/services/boardroom_ml_service.py |
| BodyVitalsService | core/services/body_vitals.py |
| BrainService | core/services/brain.py |
| BrainstormSearchService | core/services/brainstorm_search_service.py |
| CeleryHealthService | core/services/celery_health.py |
| CertificateService | core/services/certificate_service.py |
| CirculatorySystemService | core/services/circulatory.py |
| CitationGateService | core/services/citation_gate_service.py |
| ClassificationIntegrationService | core/services/classification_integration.py |
| CollectiveIntelligenceService | core/services/collective_intelligence.py |
| ConcernTrackerService | core/services/concern_tracker.py |
| CongressSyncService | core/services/congress_sync.py |
| ContentAuditService | core/services/provenance_service.py |
| ContentScoringService | core/services/content_scoring_service.py |
| ConversationMemoryService | core/services/conversation_memory_service.py |
| DecisionPrioritizationService | core/services/decision_prioritization.py |
| DeduplicationService | core/services/deduplication_service.py |
| DeliverableEnvelopeService | core/services/deliverable_envelope.py |
| DiagnosticPipelineService | core/services/diagnostic_pipeline.py |
| DigestiveSystemService | core/services/digestive.py |
| DiscordNotificationService | core/services/discord_notifications.py |
| DiscordVoiceService | core/services/discord_voice.py |
| DomainExtractionService | core/services/domain_extraction_service.py |
| EmbeddingService | core/services/embedding_service.py |
| ExperimentMetricsService | core/services/experiment_metrics.py |
| ExperimentRecommendationService | core/services/experiment_recommendations.py |
| ExperimentRollbackService | core/services/experiment_rollback.py |
| ExperimentSuggestionService | core/services/experiment_suggestion.py |
| GoalTrackingService | core/services/goal_tracking_service.py |
| GumroadPublishingService | core/services/gumroad_publishing.py |
| HITLValidationService | core/services/hitl_validation.py |
| HeartMonitorService | core/services/heart.py |
| HumanActionService | core/services/human_action_service.py |
| HumanAttentionLifecycleService | core/services/human_attention_lifecycle.py |
| HumanInterfaceService | core/services/human_interface_service.py |
| ImmuneSystemService | core/services/immune.py |
| ImplicitLearningService | core/services/implicit_learning.py |
| IncomeActionService | core/services/income_action_service.py |
| InitiativeIntegrationService | core/services/initiative_integration_service.py |
| IntelligenceQueryService | core/services/intelligence_query.py |
| KPIAlertService | core/services/kpi_alerts.py |
| KalshiService | core/services/kalshi_service.py |
| KnowledgeSimilarityService | core/services/knowledge_similarity.py |
| LearningVelocityService | core/services/learning_velocity.py |
| LivingProjectService | core/services/living_project_service.py |
| LungsCapacityService | core/services/lungs.py |
| MarketDataService | core/services/market_data_service.py |
| MarketplaceDiscoveryService | core/services/marketplace_discovery_service.py |
| MemoryContextService | core/services/memory_context_service.py |
| MemoryEmbeddingService | core/services/memory_embedding_service.py |
| MuscularSystemService | core/services/muscular.py |
| NarrativeInjectionService | core/services/content_voice_system.py |
| NervousService | core/services/nervous.py |
| OrchestrationApprovalService | core/services/orchestration_approval.py |
| OriginalityService | core/services/provenance_service.py |
| PALearningInsightsService | core/services/pa_learning_insights.py |
| PDFExportService | core/services/pdf_export_service.py |
| PersonaAdvisorService | core/services/persona_advisor_service.py |
| PilotProgressService | core/services/pilot_progress.py |
| PipelineLearningService | core/services/pipeline_learning.py |
| PlatformContextService | core/services/platform_context_service.py |
| PlatformIntelligenceBriefingService | core/services/platform_intelligence_briefing.py |
| PolicyContextService | core/services/policy_context.py |
| ProactiveIntelligenceService | core/services/proactive_intelligence.py |
| ProfileCompletenessService | core/services/profile_completeness_service.py |
| ProvenanceService | core/services/provenance_service.py |
| PushNotificationService | core/services/push_notification_service.py |
| RAGObservabilityService | core/services/rag_observability_service.py |
| RecentActivityService | core/services/recent_activity.py |
| ResearchPDFService | core/services/research_pdf_service.py |
| ResolveLearningService | core/services/resolve_learning.py |
| ReviewDocumentService | core/services/review_document.py |
| ScopedRetrievalService | core/services/scoped_retrieval.py |
| SemanticRoutingService | core/services/semantic_routing.py |
| SideChatService | core/services/side_chat.py |
| SignalAggregationService | core/services/signal_aggregation_service.py |
| SkillEvolutionService | core/services/skill_evolution_service.py |
| SkinService | core/services/skin.py |
| SmartSuggestionsService | core/services/smart_suggestions.py |
| SmartTrendingService | core/services/smart_trending_service.py |
| SpiderDeduplicationService | core/services/spider_deduplication.py |
| SpiderIntelligenceService | core/services/spider_intelligence.py |
| SpineRouterService | core/services/spine.py |
| StrategicMemoryService | core/services/strategic_memory_service.py |
| StreamingProgressService | core/services/streaming_progress.py |
| StripeSubscriptionService | core/services/stripe_subscription.py |
| StripeVoicePaymentService | core/services/stripe_voice_payments.py |
| TaskMemoryService | core/services/task_memory.py |
| TraceAttachmentService | core/services/trace_attachment_service.py |
| WatermarkService | core/services/watermark_service.py |
| WeeklySynthesisService | core/services/weekly_synthesis.py |
| WeightedLearningService | core/services/weighted_learning.py |
| WorkflowAnalyticsService | core/services/workflow_analytics.py |
| WorkflowBuilderService | core/services/workflow_builder.py |

<a id="celery-tasks"></a>
## Celery Tasks

**Headline:** 398 user-defined Celery tasks (excludes celery.* internals)

**Code location:** `core/tasks.py + siblings`

**Notes:** Top 10 modules by task count: core.tasks=332, intelligence.tasks=14, sports=8, core.tasks_agents=6, (top-level)=5, ai_core.tasks=5, ml=5, roi_metrics=4, narrative_drift=3, content_studio=2

| Task |
|---|
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |
|  |

<a id="beat-schedule"></a>
## Celery Beat — Scheduled Tasks

**Headline:** 78 enabled + 0 disabled = 78 PeriodicTask rows

**Code location:** `django_celery_beat.PeriodicTask + core/tasks_schedule.py`

| Name | Task | Enabled | Queue |
|---|---|---|---|
| aggregate-roi-metrics-daily | core.tasks.aggregate_roi_metrics_daily | yes | default |
| aggregate-spider-signals | aggregate_spider_signals | yes | long_running |
| auto-approve-boardroom-items | core.tasks.auto_approve_boardroom_items | yes | default |
| auto-archive-stale-deliverables | core.tasks.auto_archive_stale_deliverables | yes | default |
| auto-promote-low-risk-decisions | core.tasks.auto_promote_low_risk_decisions | yes | default |
| backfill-spider-embeddings | core.tasks.backfill_spider_embeddings | yes | ml |
| calculate-daily-revenue-metrics | intelligence.tasks.calculate_daily_revenue_metrics | yes | default |
| celery.backend_cleanup | celery.backend_cleanup | yes | (default) |
| check-celery-health | core.tasks.check_celery_health | yes | broadcast |
| check-learning-loop-slo | core.check_learning_loop_slo | yes | default |
| check-llm-cost-spike | core.tasks.check_llm_cost_spike | yes | default |
| check-operating-rhythm-status | core.tasks.check_operating_rhythm_status | yes | default |
| claim-stale-events | core.tasks.claim_stale_events | yes | default |
| clean-stale-data | ai_core.tasks.clean_stale_data | yes | default |
| cleanup-audio-cache | core.tasks.cleanup_audio_cache | yes | default |
| cleanup-automated-conversation-artifacts | core.tasks.cleanup_automated_conversation_artifacts | yes | default |
| cleanup-boardroom-junk | core.tasks.cleanup_boardroom_junk | yes | default |
| cleanup-celery-task-events | core.tasks.cleanup_celery_task_events | yes | default |
| cleanup-conversation-duplicates | core.tasks.cleanup_conversation_duplicates_task | yes | default |
| cleanup-expired-boardroom-items | core.tasks.cleanup_expired_boardroom_items | yes | default |
| cleanup-expired-fleet-artifacts | core.tasks.cleanup_expired_fleet_artifacts | yes | broadcast |
| cleanup-expired-pa-insights | core.tasks.cleanup_expired_pa_insights | yes | default |
| cleanup-expired-signals | cleanup_expired_signals | yes | default |
| cleanup-expired-uploads | core.tasks.cleanup_expired_uploads | yes | default |
| cleanup-halted-experiments | core.tasks.cleanup_halted_experiments | yes | default |
| cleanup-junk-initiatives | core.tasks.cleanup_junk_initiatives | yes | default |
| cleanup-learning-readback | core.tasks.cleanup_learning_readback_events | yes | default |
| cleanup-llm-call-logs | core.tasks.cleanup_llm_call_logs | yes | default |
| cleanup-old-model-files | ml.cleanup_old_model_files | yes | default |
| cleanup-old-notifications | core.tasks.cleanup_old_notifications | yes | default |
| cleanup-old-predictions | sports.cleanup_old_predictions | yes | default |
| cleanup-old-resolve-jobs | core.tasks.cleanup_old_resolve_jobs | yes | default |
| cleanup-opportunities-daily | intelligence.tasks.cleanup_old_opportunities | yes | default |
| cleanup-resolved-signatures | core.tasks.cleanup_resolved_signatures | yes | default |
| cleanup-spider-item-hashes | core.tasks.cleanup_spider_item_hashes | yes | default |
| cleanup-stale-content | core.tasks.cleanup_stale_content | yes | default |
| cleanup-stale-dreams | core.tasks.cleanup_stale_dreams | yes | default |
| cleanup-stale-running-experiments | core.tasks.cleanup_stale_running_experiments | yes | long_running |
| cleanup-stale-scoring-requests | core.tasks.cleanup_stale_scoring_requests | yes | default |
| cleanup-stuck-agent-executions | core.tasks.cleanup_stale_agent_executions | yes | broadcast |
| collect-real-opportunities | ai_core.tasks.collect_real_opportunities | yes | long_running |
| coo-daily-diagnostic | core.tasks.run_coo_daily_diagnostic | yes | long_running |
| cto-daily-diagnostic | core.tasks.run_cto_daily_diagnostic | yes | long_running |
| decay-learning-patterns | core.tasks.decay_learning_patterns | yes | default |
| detect-duplicate-initiatives | core.tasks.detect_duplicate_initiatives | yes | default |
| dream-daily-surfacing | core.tasks.surface_top_dreams | yes | default |
| enforce-data-retention | core.tasks.enforce_data_retention | yes | default |
| enforce-db-retention-daily | core.tasks.enforce_db_retention | yes | long_running |
| expire-old-opportunities | core.tasks.expire_old_opportunities | yes | default |
| expire-old-suggestions | core.tasks.expire_old_suggestions | yes | default |
| expire-overdue-validations | core.tasks.expire_overdue_validations | yes | default |
| generate-operator-edge-newsletter | core.tasks.generate_operator_edge_newsletter | yes | content |
| heart-service-heartbeat | core.tasks.run_heartbeat | yes | broadcast |
| maintain-dream-backlog | core.tasks.maintain_dream_backlog | yes | default |
| monitor-celery-health | core.tasks.monitor_celery_health | yes | broadcast |
| monitor-isolation-progress | core.tasks.monitor_isolation_progress | yes | default |
| poll-pending-3d-models | core.tasks.poll_pending_3d_models | yes | default |
| process-core-spider-data | core.tasks.process_core_spider_data | yes | long_running |
| process-hitl-escalations | core.tasks.process_hitl_escalations | yes | default |
| process-human-attention-lifecycle | core.tasks.process_human_attention_lifecycle | yes | default |
| process-spider-actions | core.tasks.process_spider_actions | yes | long_running |
| promote-to-shared-knowledge | core.tasks.promote_to_shared_knowledge | yes | default |
| reap-zombie-work | core.tasks.reap_zombie_work | yes | default |
| reconcile-experiment-status-outcome | core.tasks.reconcile_experiment_status_outcome | yes | long_running |
| report-pending-review-metrics | core.tasks.report_pending_review_metrics | yes | default |
| rescan-active-workspaces | core.tasks.rescan_active_workspaces | yes | default |
| run-spider-network | core.tasks.run_spider_network | yes | long_running |
| scan-concerns-for-human-action | core.tasks.scan_concerns_for_human_action | yes | default |
| scan-income-spider-orchestrator | intelligence.tasks.scan_income_spider_orchestrator | yes | long_running |
| scan-spider-opportunities | intelligence.tasks.scan_spider_opportunities | yes | long_running |
| send-pending-notifications | core.tasks.send_pending_notifications | yes | default |
| spider-data-retention | core.tasks.spider_data_retention | yes | long_running |
| sync-pipeline-insights-to-collective | core.tasks.sync_pipeline_insights_to_collective | yes | default |
| trend-daily-diagnostic | core.tasks.run_trend_daily_diagnostic | yes | long_running |
| update-distribution-analytics | core.tasks.update_distribution_analytics | yes | default |
| update-mythology-pattern-statistics | core.tasks.update_mythology_pattern_statistics | yes | default |
| verify-completed-fixes | core.tasks.verify_completed_fixes | yes | default |
| warm-up-spiders | ai_core.tasks.warm_up_spider_network | yes | long_running |

<a id="pa-tools"></a>
## Personal Assistant (PA) Tools

**Headline:** 103 tool schemas + 168 registered handlers; 8 enrichment services

**Code location:** `core/services/pa_tool_schemas.py + tool_dispatcher.py`

**Notes:** Schemas: 103. Handlers (self.register in tool_dispatcher.py): 168. Intent-mapped: 102. Unique enrichment services (8): ['advisor', 'blog_performance', 'domain_context', 'intelligence_enricher', 'platform_briefing', 'proactive_intelligence', 'spider_trends', 'strategic_memory'].

| Schema name | Canonical intent |
|---|---|
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |
|  |  |

<a id="database-models"></a>
## Database Models

**Headline:** 581 concrete models across 23 apps

**Notes:** By app: core=472, content=23, sports=14, agents=10, mythology=7, persistence=7, ai_intelligence=6, django_celery_beat=6, self_awareness=6, coleadership=5, ai_opportunities=4, style_memory=4, django_celery_results=3, intelligence=3, auth=2, pipelines=2, admin=1, authtoken=1, contenttypes=1, learning_bridges=1, ml=1, rendering=1, sessions=1

| Model | App | DB Table |
|---|---|---|
| LogEntry | admin |  |
| AgentChannel | agents |  |
| AgentChannelMembership | agents |  |
| AgentChannelMessage | agents |  |
| AgentContribution | agents |  |
| AgentExecution | agents |  |
| AgentOrchestration | agents |  |
| AgentPerformanceMetrics | agents |  |
| AgentRegistry | agents |  |
| AgentTool | agents |  |
| UnifiedAgentTemplate | agents |  |
| AgentKnowledgeBase | ai_intelligence |  |
| AgentLearningEvent | ai_intelligence |  |
| AgentLearningSession | ai_intelligence |  |
| LearningDocument | ai_intelligence |  |
| LearningEmbedding | ai_intelligence |  |
| LearningInsight | ai_intelligence |  |
| AIStrategy | ai_opportunities |  |
| GeneratedProject | ai_opportunities |  |
| ProjectDeployment | ai_opportunities |  |
| ProjectFile | ai_opportunities |  |
| Group | auth |  |
| Permission | auth |  |
| Token | authtoken |  |
| AgentRecommendation | coleadership |  |
| CoLeadershipDecision | coleadership |  |
| CoLeadershipPreferences | coleadership |  |
| DecisionOutcome | coleadership |  |
| HumanDecision | coleadership |  |
| AISession | content |  |
| AudioHistory | content |  |
| CharacterModel | content |  |
| CharacterTrainingImage | content |  |
| ContentAnalytics | content |  |
| ContentGeneration | content |  |
| ContentTemplate | content |  |
| ContentWorkflow | content |  |
| Document | content |  |
| DocumentEmbedding | content |  |
| Feedback | content |  |
| ImageHistory | content |  |
| KnowledgeBase | content |  |
| MiniFigAsset | content |  |
| ProjectShare | content |  |
| ProjectWorkflow | content |  |
| UploadSession | content |  |
| UserCreativePreference | content |  |
| VideoHistory | content |  |
| VideoTranscript | content |  |
| WorkflowExecution | content |  |
| WorkflowFavorite | content |  |
| WorkflowHistory | content |  |
| ContentType | contenttypes |  |
| ABAssignment | core |  |
| ABConversion | core |  |
| ABExperiment | core |  |
| ABExperimentResult | core |  |
| ABTest | core |  |
| ABTestEvent | core |  |
| ABTestVariant | core |  |
| ABVariant | core |  |
| AIModelRelease | core |  |
| AISeries | core |  |
| ATSKeywordMapping | core |  |
| ActivePriority | core |  |
| Advisor | core |  |
| AdvisorInsight | core |  |
| Agent | core |  |
| AgentAbility | core |  |
| AgentAccuracyMetrics | core |  |
| AgentAssignment | core |  |
| AgentCategory | core |  |
| AgentChannel | core |  |
| AgentCollaboration | core |  |
| AgentControlEntry | core |  |
| AgentConversation | core |  |
| AgentDecisionSummary | core |  |
| AgentDream | core |  |
| AgentEvolution | core |  |
| AgentExecution | core |  |
| AgentExecutionMemory | core |  |
| AgentImprovementRecord | core |  |
| AgentInteractionRecord | core |  |
| AgentKnowledgeSource | core |  |
| AgentLLMConfig | core |  |
| AgentLearning | core |  |
| AgentLearningConnection | core |  |
| AgentLearningSession | core |  |
| AgentMemory | core |  |
| AgentMessage | core |  |
| AgentMood | core |  |
| AgentPerformanceMetric | core |  |
| AgentPerformanceStats | core |  |
| AgentPersonality | core |  |
| AgentPrediction | core |  |
| AgentQueryPerformance | core |  |
| AgentRecommendation | core |  |
| AgentRelationship | core |  |
| AgentRole | core |  |
| AgentSession | core |  |
| AgentSolution | core |  |
| AgentSpiderConnection | core |  |
| AgentTeam | core |  |
| AgentTeamMembership | core |  |
| AnalyticsAlert | core |  |
| AnalyticsDashboard | core |  |
| Application | core |  |
| ArtifactExecution | core |  |
| ArtifactExtractionLog | core |  |
| AssistantProfile | core |  |
| Attorney | core |  |
| AttributionPath | core |  |
| AudioCache | core |  |
| AuditFinding | core |  |
| AuditLog | core |  |
| AuditRemediationTask | core |  |
| AuditReport | core |  |
| AuditVerificationRun | core |  |
| AutoTopic | core |  |
| AutomatedAction | core |  |
| AutomatedActionLog | core |  |
| AutonomousAction | core |  |
| AutonomousActionLog | core |  |
| AutonomousSituationSession | core |  |
| AutonomyConfiguration | core |  |
| AutopilotAction | core |  |
| BadContextEvent | core |  |
| Bankroll | core |  |
| BettingSession | core |  |
| BettingStats | core |  |
| Bill | core |  |
| BillChunk | core |  |
| BlockchainAuditBrief | core |  |
| BlockchainMonitoringSession | core |  |
| BlockchainSecurityAlert | core |  |
| BreathCycle | core |  |
| Budget | core |  |
| BusinessResearchResult | core |  |
| Campaign | core |  |
| CampaignDeliverable | core |  |
| CampaignResearch | core |  |
| CaseDocument | core |  |
| CaseKnowledgeGraph | core |  |
| CaseLawUpdate | core |  |
| CaseMemorandum | core |  |
| CaseProfile | core |  |
| CeleryTaskEvent | core |  |
| ChannelEpisode | core |  |
| ChannelMembership | core |  |
| ChannelMessage | core |  |
| ChatConversation | core |  |
| Child | core |  |
| CirculationPulse | core |  |
| CitationViolation | core |  |
| ClientDeliverable | core |  |
| ClosePack | core |  |
| ClusterEvolution | core |  |
| CockpitAgentState | core |  |
| CockpitAuditLog | core |  |
| CockpitAutopilotEvent | core |  |
| CockpitAutopilotPolicy | core |  |
| CockpitIncident | core |  |
| CockpitIncidentEvent | core |  |
| CodeArtifact | core |  |
| CodeJobLog | core |  |
| CodeRun | core |  |
| Collaboration | core |  |
| CollaborationSession | core |  |
| CollaborativeContent | core |  |
| CompetitorComparison | core |  |
| ComplianceCheck | core |  |
| ComplianceRule | core |  |
| ComponentStatus | core |  |
| ConceptForgeArtifact | core |  |
| ConceptForgeRun | core |  |
| ConceptForgeStageRun | core |  |
| CongressMember | core |  |
| ContentAsset | core |  |
| ContentAuditResult | core |  |
| ContentChannel | core |  |
| ContentDebate | core |  |
| ContentDistribution | core |  |
| ContentEngagement | core |  |
| ContentGenerationJob | core |  |
| ContentPackage | core |  |
| ContentPacket | core |  |
| ContentPacketItem | core |  |
| ContentPerformancePrediction | core |  |
| ContentProvenance | core |  |
| ContentPurchase | core |  |
| ContentQualityBlacklist | core |  |
| ContentShowroom | core |  |
| ContractRecord | core |  |
| ConversationArtifact | core |  |
| ConversationMemory | core |  |
| ConversationMessage | core |  |
| ConversionEvent | core |  |
| CoordinatorOutcome | core |  |
| CostTracking | core |  |
| CryptoSentiment | core |  |
| CustomWorkflow | core |  |
| CustomWorkflowStep | core |  |
| DataProvenance | core |  |
| DebugAnnotation | core |  |
| DecisionAggregate | core |  |
| DecisionLedgerEntry | core |  |
| DecisionPoint | core |  |
| DecisionRecord | core |  |
| DecisionTypeSuccessPattern | core |  |
| DeliberationSession | core |  |
| DeliberationTurn | core |  |
| Deliverable | core |  |
| DeliverableAppend | core |  |
| DeliverableCollection | core |  |
| DeliverableEvent | core |  |
| DeliverableExport | core |  |
| DeployJob | core |  |
| DesignSystemUpdate | core |  |
| DesignTrend | core |  |
| DigestionStatus | core |  |
| DigestivePulse | core |  |
| DirectMessage | core |  |
| DiscordClient | core |  |
| DiscordLinkCode | core |  |
| DiscordServer | core |  |
| DiscordServerChannel | core |  |
| DistributionAnalytics | core |  |
| DistributionInsight | core |  |
| DistributionPlatform | core |  |
| DistributionRecommendation | core |  |
| DocVersion | core |  |
| DocumentRelationship | core |  |
| DreamExploration | core |  |
| DreamFeedbackPreference | core |  |
| DreamImplementation | core |  |
| EarningsPrediction | core |  |
| EngagementEvent | core |  |
| EngagementMetrics | core |  |
| EnhancedUserProfile | core |  |
| ErrorInstance | core |  |
| ErrorPattern | core |  |
| ExecutionRun | core |  |
| ExhibitList | core |  |
| Experiment | core |  |
| ExperimentLearning | core |  |
| ExtendedUserProfile | core |  |
| ExtractedArtifact | core |  |
| F2FSession | core |  |
| FailureDetection | core |  |
| FailureDiagnosis | core |  |
| FailurePrescription | core |  |
| FailureSignature | core |  |
| FeedbackItem | core |  |
| FleetArtifact | core |  |
| FleetAuthAuditLog | core |  |
| FleetEvent | core |  |
| FleetServiceIdentity | core |  |
| FleetServiceKey | core |  |
| FleetServiceRotation | core |  |
| FlowRoute | core |  |
| FlowStatus | core |  |
| FounderFeedback | core |  |
| FreelanceOpportunity | core |  |
| GeneratedCode | core |  |
| GeneratedProject | core |  |
| GeneratedResponse | core |  |
| GovernanceState | core |  |
| HeartBeat | core |  |
| HiveMindContribution | core |  |
| HiveMindSession | core |  |
| HumanAttentionItem | core |  |
| HumanControlAction | core |  |
| HumanFeedbackRecord | core |  |
| HumanPreference | core |  |
| HumanSystemState | core |  |
| ImmuneResponse | core |  |
| ImmuneStatus | core |  |
| ImpactCredit | core |  |
| ImpactEvent | core |  |
| ImplementationAction | core |  |
| IngestionRoute | core |  |
| Initiative | core |  |
| InitiativeActionItem | core |  |
| InitiativeStage | core |  |
| IntelligentPromptMetric | core |  |
| IntelligentPromptStats | core |  |
| InterAgentMessage | core |  |
| JobApplication | core |  |
| JobMatch | core |  |
| JobMatchProfile | core |  |
| KPISnapshot | core |  |
| KillSwitch | core |  |
| KnowledgeTransfer | core |  |
| LLMCallEvent | core |  |
| LLMCallLog | core |  |
| LLMModel | core |  |
| LLMProvider | core |  |
| LearnedPreferenceRecord | core |  |
| LearningAchievement | core |  |
| LearningCompanion | core |  |
| LearningInsight | core |  |
| LearningJourney | core |  |
| LearningJourneyStep | core |  |
| LearningJourneyTemplate | core |  |
| LearningPattern | core |  |
| LearningProgress | core |  |
| LearningProgressSnapshot | core |  |
| LearningReadbackEvent | core |  |
| LegalCase | core |  |
| LegalDocument | core |  |
| LegalMemory | core |  |
| LegalResearchResult | core |  |
| LevelMilestone | core |  |
| LitigationDocument | core |  |
| LivingProjectConfig | core |  |
| MLModelVersion | core |  |
| MagicLink | core |  |
| MarketIntelligenceBrief | core |  |
| MarketMonitoringSession | core |  |
| Meeting | core |  |
| MemoryCluster | core |  |
| MemoryClusterMembership | core |  |
| MemoryConnection | core |  |
| MemoryPalaceRoom | core |  |
| MessageThread | core |  |
| MobilePushToken | core |  |
| MoodHistory | core |  |
| MoodTriggerRule | core |  |
| MuscleGroup | core |  |
| MuscleStatus | core |  |
| MuscularPulse | core |  |
| MythologyQuarantine | core |  |
| Narrative | core |  |
| NarrativeAlert | core |  |
| NarrativeEvidence | core |  |
| NarrativeShift | core |  |
| NewsletterSubscriber | core |  |
| NotificationLog | core |  |
| NotificationPreference | core |  |
| Opportunity | core |  |
| OpportunityAction | core |  |
| OpportunityContent | core |  |
| OpportunityDigest | core |  |
| OpportunityInteraction | core |  |
| OpportunityOutcome | core |  |
| OpportunityPredictionAccuracy | core |  |
| OpportunityRevenue | core |  |
| OpportunityScore | core |  |
| OpportunityTask | core |  |
| OpsRun | core |  |
| OpsRunEvent | core |  |
| OrchestrationApprovalGate | core |  |
| OrchestrationExecution | core |  |
| OrchestrationStepExecution | core |  |
| OriginalityScore | core |  |
| OutreachDraft | core |  |
| PAToolInsight | core |  |
| PartnershipProject | core |  |
| Party | core |  |
| PerformanceComparison | core |  |
| PerformanceLog | core |  |
| PersonaResumeTemplate | core |  |
| PilotExecution | core |  |
| PilotImplementation | core |  |
| PilotReadinessGate | core |  |
| PipelineLearningInsight | core |  |
| PipelineRun | core |  |
| PipelineStageFeedback | core |  |
| PlacedWager | core |  |
| PlacedWagerLeg | core |  |
| PlatformMetrics | core |  |
| PodcastDebate | core |  |
| PodcastEpisode | core |  |
| PodcastParticipant | core |  |
| PodcastShow | core |  |
| PodcastStyleProfile | core |  |
| PolicyExperiment | core |  |
| PredictionComment | core |  |
| PredictionFollowUp | core |  |
| PredictionOutcome | core |  |
| PredictionStats | core |  |
| PreviewDeployment | core |  |
| PreviewEnvironment | core |  |
| PreviewService | core |  |
| PricingOptimization | core |  |
| ProactiveAlert | core |  |
| ProactiveNotification | core |  |
| ProjectActivity | core |  |
| ProjectCollaborator | core |  |
| ProjectComment | core |  |
| ProjectEnvVar | core |  |
| ProjectInsight | core |  |
| ProjectPresence | core |  |
| ProjectRepo | core |  |
| ProjectResearchFeedback | core |  |
| ProjectSpiderPriority | core |  |
| ProjectWorkspace | core |  |
| PublishedWorkflow | core |  |
| PushSubscription | core |  |
| Quarantine | core |  |
| ... | _(181 more rows truncated)_ |

<a id="url-routes"></a>
## URL Routes

**Headline:** 1854 path() patterns across all core/urls*.py files

**Code location:** `core/urls*.py`

| Prefix | Count |
|---|---|
| api | 1773 |
| (root) | 5 |
| sports | 4 |
| marketplace | 4 |
| diagnostics | 3 |
| <uuid:provenance_id> | 3 |
| audit | 3 |
| originality | 3 |
| income-builder | 2 |
| neural-orchestra | 2 |
| ai-nexus | 2 |
| profile | 2 |
| watermark | 2 |
| accounts | 2 |
| dashboard | 1 |
| income | 1 |
| decisions | 1 |
| decision-command | 1 |
| opportunity-detail | 1 |
| opportunities | 1 |
| revenue-opportunities | 1 |
| revenue | 1 |
| revenue-dashboard | 1 |
| monetization | 1 |
| monetization-hub | 1 |
| learning | 1 |
| learning-dashboard | 1 |
| analytics | 1 |
| analytics-dashboard | 1 |
| control | 1 |
| control-center | 1 |
| diagnostic-dashboard | 1 |
| sports-hub | 1 |
| dbao | 1 |
| dbao-dashboard | 1 |
| login | 1 |
| logout | 1 |
| signup | 1 |
| assistant | 1 |
| notifications | 1 |
| create | 1 |
| verify | 1 |
| similar | 1 |
| admin | 1 |
| content-studio | 1 |
| ai-studio | 1 |
| ai-production-hub | 1 |
| command | 1 |
| ai-building-products | 1 |
| visualization | 1 |
| agent-testing | 1 |
| ai-job-market-dashboard | 1 |
| nexus | 1 |
| intelligence | 1 |
| share | 1 |
| truth | 1 |
| api-auth | 1 |
| health | 1 |

<a id="views-files"></a>
## Django View Files

**Headline:** 206 files matching core/views*.py

**Code location:** `core/views*.py`

| File |
|---|
| views.py |
| views_ab_testing.py |
| views_advanced_workflows.py |
| views_advisor_api.py |
| views_agent_analytics.py |
| views_agent_collaboration.py |
| views_agent_collaboration_api.py |
| views_agent_dashboard.py |
| views_agent_ecosystem.py |
| views_agent_evolution.py |
| views_agent_execution.py |
| views_agent_extras.py |
| views_agent_intelligence.py |
| views_agent_learning.py |
| views_agent_orchestration.py |
| views_agent_relationships.py |
| views_agent_tracking.py |
| views_agent_training.py |
| views_agent_work_platform.py |
| views_ai_ecosystem.py |
| views_ai_learning_api.py |
| views_ai_training.py |
| views_analytics.py |
| views_analytics_real.py |
| views_app_manifest.py |
| views_artifacts.py |
| views_assistant_bypass.py |
| views_assistant_minimal.py |
| views_ats_optimization.py |
| views_audio.py |
| views_audit_api.py |
| views_audit_tracking.py |
| views_auto_distribution.py |
| views_auto_fix.py |
| views_autonomous_dashboard.py |
| views_autonomous_reasoning.py |
| views_betting.py |
| views_body.py |
| views_bpaas_api.py |
| views_brain.py |
| views_business_ideas.py |
| views_campaign.py |
| views_categorized_opportunities.py |
| views_celery_api.py |
| views_character_training.py |
| views_circulatory.py |
| views_code_artifacts.py |
| views_code_jobs.py |
| views_code_runner.py |
| views_collaboration.py |
| views_collective_intelligence.py |
| views_competitor_comparison.py |
| views_conceptforge.py |
| views_content.py |
| views_content_calendar.py |
| views_content_learning.py |
| views_creative_director.py |
| views_dashboard_api.py |
| views_dashboard_stats.py |
| views_davinci.py |
| views_deliberation.py |
| views_deliverables.py |
| views_demo_pipeline.py |
| views_deploy.py |
| views_deploy_verify.py |
| views_diagnostics.py |
| views_digestive.py |
| views_discord.py |
| views_distribution.py |
| views_docs_index.py |
| views_ecosystem.py |
| views_ecosystem_activation.py |
| views_enhanced_profile.py |
| views_executor_runs.py |
| views_f2f.py |
| views_fleet_admin.py |
| views_fleet_artifacts.py |
| views_fleet_events.py |
| views_government.py |
| views_heart.py |
| views_hive_mind.py |
| views_home.py |
| views_human_interface.py |
| views_image.py |
| views_image_edit.py |
| views_image_gallery.py |
| views_image_generate.py |
| views_image_helpers.py |
| views_image_misc.py |
| views_image_portfolio.py |
| views_image_tools.py |
| views_image_workflow.py |
| views_immune.py |
| views_inbox.py |
| views_income_action.py |
| views_initiative_kickstart.py |
| views_integration_health.py |
| views_intelligence_api.py |
| views_interview.py |
| views_isolation_control.py |
| views_job_application_system.py |
| views_knowledge.py |
| views_learning.py |
| views_learning_dashboard.py |
| views_learning_journey.py |
| views_learning_journey_api.py |
| views_learning_loop.py |
| views_learning_path.py |
| views_legal.py |
| views_legal_cases.py |
| views_llm_routing.py |
| views_lungs.py |
| views_marketplace.py |
| views_memory_clusters.py |
| views_memory_palace.py |
| views_mobile.py |
| views_multi_llm.py |
| views_muscular.py |
| views_nervous.py |
| views_neural_orchestra.py |
| views_newsletter.py |
| views_obs.py |
| views_odds_sports.py |
| views_opportunities.py |
| views_opportunity.py |
| views_ops_console.py |
| views_orchestration.py |
| views_pdf_export.py |
| views_personal_assistant.py |
| views_personal_assistant_dev.py |
| views_personal_memories.py |
| views_personality.py |
| views_platform_command.py |
| views_platform_integrations.py |
| views_podcast.py |
| views_portfolio.py |
| views_predictions.py |
| views_preferences.py |
| views_preview_api.py |
| views_proactive.py |
| views_profile.py |
| views_profile_management.py |
| views_project_collaboration.py |
| views_project_hub.py |
| views_project_intelligence.py |
| views_projects.py |
| views_projects_api.py |
| views_proposals.py |
| views_provenance.py |
| views_public_changelog.py |
| views_public_intelligence.py |
| views_public_stats.py |
| views_push_notifications.py |
| views_rag_embeddings.py |
| views_rag_observability.py |
| views_react.py |
| views_real_data.py |
| views_real_income_builder.py |
| views_redirect.py |
| views_research_demo.py |
| views_research_feedback.py |
| views_revenue.py |
| views_revenue_analytics.py |
| views_revenue_tracking.py |
| views_roi_metrics.py |
| views_self_development.py |
| views_session_handoff.py |
| views_share.py |
| views_skin.py |
| views_solution_explorer.py |
| views_spider_dashboard.py |
| views_spider_data.py |
| views_spider_feed.py |
| views_spider_intelligence.py |
| views_spine.py |
| views_status_api.py |
| views_stock_intelligence.py |
| views_strategic_memory.py |
| views_stripe.py |
| views_stripe_billing.py |
| views_stripe_voice.py |
| views_super_platform.py |
| views_team_collaboration.py |
| views_telemetry.py |
| views_time_capsules.py |
| views_time_travel.py |
| views_trace_viewer.py |
| views_unified.py |
| views_unified_bridge.py |
| views_unified_intelligence.py |
| views_upload.py |
| views_user_learning_api.py |
| views_user_profile.py |
| views_validation.py |
| views_video.py |
| views_video_agents.py |
| views_vip_invite.py |
| views_visualization.py |
| views_voice_marketplace.py |
| views_workflow.py |
| views_workflow_analytics.py |
| views_workflow_engine.py |
| views_workflow_run.py |
| views_workspace_api.py |
| views_workspace_templates.py |
| views_workspace_triggers.py |

<a id="management-commands"></a>
## Django Management Commands

**Headline:** 178 management commands in core/management/commands/

**Code location:** `core/management/commands/`

| Command |
|---|
| python manage.py achieve_95_reality |
| python manage.py activate_spiders |
| python manage.py add_critical_celery_tasks |
| python manage.py add_fleet_key |
| python manage.py agent_introduction_party |
| python manage.py apply_publish_gate |
| python manage.py askdocs |
| python manage.py assign_agent_voices |
| python manage.py assign_memories_to_rooms |
| python manage.py audit_database |
| python manage.py auto_remediate |
| python manage.py backfill_agent_control_blocked_at |
| python manage.py backfill_blog_attention |
| python manage.py backfill_blog_attention_items |
| python manage.py backfill_contributions |
| python manage.py backfill_decision_summaries |
| python manage.py backfill_decisions |
| python manage.py backfill_deliverable_workspaces |
| python manage.py backfill_deliverables |
| python manage.py backfill_dream_origins |
| python manage.py backfill_evolution_xp |
| python manage.py backfill_experiment_learnings |
| python manage.py backfill_initiative_owners |
| python manage.py backfill_initiative_signals |
| python manage.py backfill_media_workspaces |
| python manage.py backfill_research_brief_links |
| python manage.py backfill_stage_documents |
| python manage.py backfill_voice_scores |
| python manage.py boardroom_approval |
| python manage.py boost_spiders |
| python manage.py bootstrap_agent_relationships |
| python manage.py bootstrap_learning_system |
| python manage.py build_advisor_audit |
| python manage.py build_beat_audit |
| python manage.py build_body_system_audit |
| python manage.py build_capability_audit |
| python manage.py build_celery_audit |
| python manage.py build_discord_audit |
| python manage.py build_docs_index |
| python manage.py build_learning_bridge_audit |
| python manage.py build_management_command_audit |
| python manage.py build_ml_audit |
| python manage.py build_pa_tool_audit |
| python manage.py build_rag_corpus |
| python manage.py build_runtime_audit |
| python manage.py build_spider_audit |
| python manage.py bulk_embed_spiders |
| python manage.py calibrate_halt_thresholds |
| python manage.py celery_inspect_report |
| python manage.py check_experiment_status |
| python manage.py check_initiative_drift |
| python manage.py circulation_check |
| python manage.py classify_docs_for_rag |
| python manage.py clean_initiative_names |
| python manage.py cleanup_agent_solutions |
| python manage.py cleanup_agents |
| python manage.py cleanup_content_quality |
| python manage.py cleanup_conversation_duplicates |
| python manage.py cleanup_empty_tables |
| python manage.py cleanup_fleet_artifacts |
| python manage.py cleanup_orphan_documents |
| python manage.py cleanup_single_letter_docs |
| python manage.py cleanup_stale_initiatives |
| python manage.py cleanup_stuck_executions |
| python manage.py cleanup_stuck_tasks |
| python manage.py connect_all_agents |
| python manage.py consolidate_duplicate_initiatives |
| python manage.py consolidate_workspaces |
| python manage.py create_test_token |
| python manage.py create_workflow_templates |
| python manage.py daily_priorities |
| python manage.py db_health_snapshot |
| python manage.py deploy_platform_unification |
| python manage.py digestion_check |
| python manage.py discover_learning_cohorts |
| python manage.py draft_repo_verifier_claims |
| python manage.py embed_documents |
| python manage.py enrich_boardroom_ml |
| python manage.py ensure_enhanced_profiles |
| python manage.py extract_initiatives_from_survey |
| python manage.py fetch_training_data |
| python manage.py fix_episode_titles |
| python manage.py fix_evolution_levels |
| python manage.py fix_initiative_stages |
| python manage.py fix_initiative_titles |
| python manage.py fix_orphan_initiative_tracking |
| python manage.py fix_pilot_started_at |
| python manage.py fix_selfblog_categories |
| python manage.py fix_stuck_initiatives |
| python manage.py fix_workspace_deliverables |
| python manage.py fix_workspace_permissions |
| python manage.py fix_workspace_visibility |
| python manage.py fleet_health_rollup |
| python manage.py force_agent_cycle |
| python manage.py full_system_demo |
| python manage.py generate_ironwood_sprites |
| python manage.py generate_platform_inventory |
| python manage.py generate_sample_data |
| python manage.py heart_check |
| python manage.py immune_check |
| python manage.py import_patent_disclosures |
| python manage.py ingest_codebase |
| python manage.py init_platform |
| python manage.py initiative_rate_limit |
| python manage.py load_all_agents_advisors |
| python manage.py lungs_check |
| python manage.py migrate_images_to_cloudinary |
| python manage.py migrate_pa_identity |
| python manage.py muscular_check |
| python manage.py normalize_evolution_data |
| python manage.py operating_rhythm |
| python manage.py ops_verify |
| python manage.py populate_agents |
| python manage.py process_spider_data |
| python manage.py produce_content |
| python manage.py provision_fleet_identity |
| python manage.py ragtest |
| python manage.py reality_check |
| python manage.py refresh_doc_inventory_blocks |
| python manage.py refresh_repo_context |
| python manage.py regenerate_pilots |
| python manage.py register_coo_agent |
| python manage.py register_creative_agents |
| python manage.py register_cto_agent |
| python manage.py register_external_repo |
| python manage.py repo_knowledge_audit |
| python manage.py rescore_opportunities |
| python manage.py rotate_fleet_key |
| python manage.py run_code_agent |
| python manage.py run_discord_bot |
| python manage.py run_smoke_tests |
| python manage.py run_ui_smoke |
| python manage.py seed_golden_path_demo |
| python manage.py seed_learning_journeys |
| python manage.py seed_mythology |
| python manage.py seed_production |
| python manage.py seed_test_scenarios |
| python manage.py selfpatch |
| python manage.py set_founder_intent |
| python manage.py setup_codebase_workspace |
| python manage.py setup_llm_routing |
| python manage.py setup_pa_service_account |
| python manage.py setup_production_workspace |
| python manage.py setup_workspace_autopilot |
| python manage.py show_remediation_findings |
| python manage.py spine_check |
| python manage.py start_bridge |
| python manage.py start_learning_demo |
| python manage.py start_resolve_render |
| python manage.py survey_external_repo |
| python manage.py sync_agent_learning |
| python manage.py sync_agent_tools |
| python manage.py sync_celery_beat |
| python manage.py sync_celery_schedules |
| python manage.py sync_docs_index_to_documents |
| python manage.py sync_orchestrations |
| python manage.py sync_persona_learning |
| python manage.py sync_spider_agents |
| python manage.py sync_task_queues |
| python manage.py system_health_check |
| python manage.py system_reality_check |
| python manage.py test_agent_scenarios |
| python manage.py test_all_agents |
| python manage.py test_initiatives_perf |
| python manage.py test_prompt_layer |
| python manage.py triage_spider_embeddings |
| python manage.py trigger_pilot_evaluation |
| python manage.py trigger_stage2_generation |
| python manage.py tune_fed_alert_triggers |
| python manage.py update_experiment_thresholds |
| python manage.py validate_data_integrity |
| python manage.py validate_section |
| python manage.py validate_security |
| python manage.py verify_doc_claims |
| python manage.py verify_surgical_moves |
| python manage.py warmup_body_systems |
| python manage.py wire_agents_to_spiders |
| python manage.py write_self_blog |

<a id="discord"></a>
## Discord Integration

**Headline:** 96 @*.command decorators, 48 @app_commands.command, 25 Cog classes in discord_bot.py

**Code location:** `core/services/discord_bot.py`

| Cog |
|---|
| AgentAccessCommands |
| AgentCommands |
| ClientCommands |
| ContentCommands |
| ContentPipelineCommands |
| DeveloperCommands |
| GumroadCommands |
| HelpCommands |
| HumanInterfaceCommands |
| InteractiveCommands |
| LegalCommands |
| MLScoringCommands |
| OBSCommands |
| PodcastCommands |
| ReactionFeedbackCog |
| ResolveCommands |
| ReviewCommands |
| RoleManager |
| SeriesCommands |
| ServerSetupCommands |
| SituationCommands |
| SpiderCommands |
| StatusCommands |
| StudioCommands |
| VoiceCommands |

<a id="body-systems"></a>
## Body Systems

**Headline:** 9 body systems monitored by run_all_systems_scan

**Code location:** `core/tasks.py (body_systems)`

| System |
|---|
| heart |
| lungs |
| brain |
| spine |
| immune |
| digestive |
| muscular |
| circulatory |
| skin |

<a id="llm-providers"></a>
## LLM Providers

**Headline:** 6 providers registered in LLMProviderRegistry

**Code location:** `core/services/llm_provider_registry.py`

| Provider |
|---|
| openai |
| anthropic |
| deepseek |
| together |
| gemini |
| ollama |

<a id="signal-intelligence"></a>
## Signal Intelligence

**Headline:** 10 SignalCluster pattern types, MIN_CLUSTER_SIZE=3

**Code location:** `core/models_signal_intelligence.py + services/signal_aggregation_service.py`

| Pattern Type | Label |
|---|---|
| demand_spike | Demand Spike |
| trend_emergence | Trend Emergence |
| sentiment_shift | Sentiment Shift |
| opportunity_window | Opportunity Window |
| knowledge_gap | Knowledge Gap |
| competitive_signal | Competitive Signal |
| market_movement | Market Movement |
| skill_demand | Skill Demand |
| content_gap | Content Gap |
| user_need | User Need |

<a id="memory-types"></a>
## AgentMemory Types

**Headline:** 7 memory types tracked by AgentMemory model

**Code location:** `core/models_unified_system.py (AgentMemory.MEMORY_TYPE_CHOICES)`

| Type | Label |
|---|---|
|  | Success |
|  | Failure |
|  | User Preference |
|  | Technique |
|  | Insight |
|  | Interaction |
|  | Feedback |

<a id="content-pipeline"></a>
## Content Pipeline

**Headline:** 3 reviewer classes referenced, 9 content domains, max_claims default=20

**Code location:** `core/services/content_review_panel_v2.py + domain_content_context.py + claims_pack_builder.py`

| Component | Value |
|---|---|
| Reviewers (always) | SkepticReviewer, FactCheckReviewer |
| Reviewers (conditional) | DomainPersonaReviewer (when domain confidence ≥ 0.2) |
| All reviewer names found | DomainPersonaReviewer, FactCheckReviewer, SkepticReviewer |
| Domain builders | finance, crypto, sports, betting, ai_tech, legal, career, health, education |
| ClaimsPackBuilder default max_claims | 20 |

<a id="initiative-pipeline"></a>
## Initiative Pipeline

**Headline:** 5 pipeline stages (auto-dispatch on stages [4, 5])

**Code location:** `core/models_document_registry.py (STAGE_TYPES)`

| Stage # | Type | Auto-dispatch |
|---|---|---|
|  | research | no |
|  | planning | no |
|  | evaluation | no |
|  | specification | yes |
|  | execution | yes |

<a id="frontend"></a>
## Frontend (React + Vite)

**Headline:** 61 routes in App.tsx, 5 workspace primary tabs, 9 betting dashboard tabs

**Code location:** `frontend/src/App.tsx, pages/workspace/types.ts, pages/BettingPage.tsx`

**Notes:** Workspace tabs: ['home', 'work', 'build', 'intelligence', 'system']. Betting tabs: ['hub', 'games', 'top_plays', 'sharp', 'arbitrage', 'watching', 'odds', 'wagers', 'records'].

| Surface | Count |
|---|---|
| App.tsx <Route> | 61 |
| Workspace primary tabs | 5 |
| Betting dashboard tabs | 9 |

<a id="infrastructure"></a>
## Infrastructure

**Headline:** 10 Procfile processes, 3 distinct Redis DB indices in settings

**Code location:** `Procfile + core/settings.py`

| Component | Value |
|---|---|
| Procfile processes | web, celery-worker, celery-pa, celery-content, celery-long-running, celery-long-running-2, celery-broadcast, celery-beat, code-worker, resolve-node |
| Redis DB indices (settings.py) | 1, 2, 3 |

<a id="code-stats"></a>
## Code Statistics

**Headline:** 2,027 Python files, 988,861 lines across core/ + ai_core/ + intelligence/

| Tree | Files | Lines |
|---|---|---|
| core | 1621 | 822464 |
| ai_core | 295 | 119912 |
| intelligence | 111 | 46485 |
| TOTAL (python) | 2027 | 988861 |

<a id="verifier-state"></a>
## Doc-vs-Reality Verifier State

**Headline:** 73 registered claims across 34 docs: 72 OK, 1 drifts

**Code location:** `core/services/doc_claim_verification.py (run via `python manage.py verify_doc_claims`)`

**Notes:** Severity rollup: ok=72, low=0, medium=1, high=0, error=0. Top drifting docs: docs/SERVICES.md.

| Doc | OK | Drift | Error |
|---|---|---|---|
| CLAUDE.md | 10 | 0 | 0 |
| core/epa_handlers/td_handlers_ops.py | 1 | 0 | 0 |
| core/learning_bridges/base.py | 1 | 0 | 0 |
| core/management/commands/load_all_agents_advisors.py | 2 | 0 | 0 |
| core/models_document_registry.py | 1 | 0 | 0 |
| core/models_unified_system.py | 1 | 0 | 0 |
| core/services/advisor_context_builder.py | 1 | 0 | 0 |
| core/services/priority/governor.py | 1 | 0 | 0 |
| docs/ADVISOR_AUDIT.md | 2 | 0 | 0 |
| docs/AGENTS.md | 3 | 0 | 0 |
| docs/API_PATH_POLICY.md | 2 | 0 | 0 |
| docs/ARCHITECTURE.md | 1 | 0 | 0 |
| docs/BACKEND_INVENTORY.md | 6 | 0 | 0 |
| docs/BEAT_AUDIT.md | 1 | 0 | 0 |
| docs/BODY_SYSTEM_AUDIT.md | 1 | 0 | 0 |
| docs/CAPABILITIES.md | 4 | 0 | 0 |
| docs/CAPABILITY_AUDIT.md | 2 | 0 | 0 |
| docs/CELERY_AUDIT.md | 1 | 0 | 0 |
| docs/DISCORD_INTEGRATION.md | 1 | 0 | 0 |
| docs/LEARNING_BRIDGE_AUDIT.md | 1 | 0 | 0 |
| docs/ML_AUDIT.md | 1 | 0 | 0 |
| docs/PA_TOOL_AUDIT.md | 2 | 0 | 0 |
| docs/SERVICES.md | 1 | 1 | 0 |
| docs/SPIDERS.md | 3 | 0 | 0 |
| docs/SPIDER_AUDIT.md | 2 | 0 | 0 |
| docs/topics/agent-system.md | 2 | 0 | 0 |
| docs/topics/body-systems.md | 1 | 0 | 0 |
| docs/topics/celery-workers.md | 1 | 0 | 0 |
| docs/topics/content-pipeline.md | 3 | 0 | 0 |
| docs/topics/frontend.md | 3 | 0 | 0 |
| docs/topics/infrastructure.md | 3 | 0 | 0 |
| docs/topics/initiative-pipeline.md | 2 | 0 | 0 |
| docs/topics/personal-assistant.md | 4 | 0 | 0 |
| docs/topics/spider-network.md | 1 | 0 | 0 |

---

*Generated by `core.services.platform_inventory`. When the docs elsewhere in the repo disagree with anything in this file, this file is authoritative.*
