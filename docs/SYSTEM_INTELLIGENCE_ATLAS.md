# System Intelligence Atlas

**Complete Catalog of All Intelligent Components**

**Last Updated:** Session 461 (December 16, 2025)
**Total Components:** 200+ intelligent entities

---

## Quick Stats

| Category | Count | Status |
|----------|-------|--------|
| **Agents** | 48 | Active |
| **Advisors** | 25 | Active |
| **Spiders** | 66 | Active |
| **Learning Bridges** | 10 | Active |
| **Autonomous Loops** | 3 | Active |
| **Services** | 40+ | Active |
| **Sci-Fi Features** | 15 | Active |

---

## Part 1: Agents (48 Total)

All agents inherit from `BaseAgent` with TimeTravelMixin for decision tracking.

### Creation Agents (4)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| ImageAgent | `core/agents/image_agent.py` | Generate images (logos, banners, illustrations) | `generate_image`, `generate_variations` |
| VideoAgent | `core/agents/video_agent.py` | Generate videos (text-to-video, animations) | `generate_video`, `animate_image` |
| AudioAgent | `core/agents/audio_agent.py` | Generate audio (TTS, voiceovers) | `generate_voice`, `generate_sfx` |
| ThreeDAgent | `core/agents/three_d_agent.py` | Generate 3D models | `convert_to_3d`, `generate_scene` |

### Editing Agents (2)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| ImageEditingAgent | `core/agents/image_editing_agent.py` | Edit images (upscale, remove bg, etc.) | `upscale`, `remove_background`, `search_replace` |
| VideoEditingAgent | `core/agents/video_editing_agent.py` | Edit videos (trim, effects, text) | `trim_video`, `add_text`, `add_effects` |

### Research Agents (1)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| ResearchAgent | `core/agents/research_agent.py` | Web search + spider network queries | `web_search`, `spider_query`, `analyze_trends` |

### Strategy Agents (4)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| ContentStrategyAgent | `core/agents/strategy/content_strategy_agent.py` | Content recommendations from trends | `analyze_content`, `suggest_topics` |
| BrandIdentityAgent | `core/agents/strategy/brand_identity_agent.py` | Brand colors, styles, consistency | `analyze_brand`, `suggest_identity` |
| SEOOptimizerAgent | `core/agents/strategy/seo_optimizer_agent.py` | Hashtags, metadata, keywords | `generate_keywords`, `optimize_meta` |
| SocialMediaAgent | `core/agents/strategy/social_media_agent.py` | Platform-specific content strategy | `platform_strategy`, `schedule_content` |

### Executive Agents (4)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| CTOAgent | `core/agents/executive/cto_agent.py` | Technical planning and analysis | `technical_review`, `architecture_plan` |
| COOAgent | `core/agents/executive/coo_agent.py` | Operations planning and risk analysis | `ops_review`, `risk_assessment` |
| CreativeDirectorAgent | `core/agents/executive/creative_director_agent.py` | Creative guidance and prompt enhancement | `enhance_prompt`, `creative_direction` |
| MeetingCoordinatorAgent | `core/agents/executive/meeting_coordinator_agent.py` | Coordinates meetings between agents | `schedule_meeting`, `synthesize_outcomes` |

### Analysis Agents (3)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| TrendAnalysisAgent | `core/agents/analysis/trend_analysis_agent.py` | Spider intelligence analysis | `analyze_trends`, `identify_patterns` |
| OpportunityScoringAgent | `core/agents/analysis/opportunity_scoring_agent.py` | Opportunity scoring engine | `score_opportunity`, `rank_opportunities` |
| MarketIntelligenceAgent | `core/agents/analysis/market_intelligence_agent.py` | Market analysis and intelligence | `market_scan`, `competitive_intel` |

### Training Agents (2)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| CharacterTrainingAgent | `core/agents/training/character_training_agent.py` | FLUX LoRA character training | `train_character`, `manage_lora` |
| TrainedCreationAgent | `core/agents/training/trained_creation_agent.py` | LoRA image generation | `generate_with_lora`, `list_trained` |

### Security Agents (2)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| MemoryIsolationAgent | `core/agents/security/memory_isolation_agent.py` | Memory isolation and security | `isolate_memory`, `verify_access` |
| ContentAuditAgent | `core/agents/security/content_audit_agent.py` | Content moderation and audit | `audit_content`, `flag_violations` |

### Business Research Agents (5)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| CompetitorAnalysisAgent | `core/agents/business/competitor_analysis_agent.py` | Competitor analysis, SWOT, positioning | `analyze_competitors`, `swot_analysis` |
| CustomerResearchAgent | `core/agents/business/customer_research_agent.py` | Customer personas, pain points, sentiment | `build_persona`, `analyze_sentiment` |
| BrandStrategyAgent | `core/agents/business/brand_strategy_agent.py` | Brand positioning, messaging, visual direction | `brand_positioning`, `messaging_framework` |
| MarketingStrategyAgent | `core/agents/business/marketing_strategy_agent.py` | Channel strategy, campaigns, funnel optimization | `channel_strategy`, `campaign_plan` |
| BusinessContentStrategyAgent | `core/agents/business/content_strategy_agent.py` | Content pillars, formats, topic ideas | `content_pillars`, `topic_ideation` |

### Development Agents (4)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| CodeGeneratorAgent | `core/agents/code_generator_agent.py` | Generate code from specifications | `generate_code`, `explain_code`, `refactor_code` |
| FullStackDeveloperAgent | `core/agents/fullstack_developer_agent.py` | Build complete features (frontend + backend + DB) | `design_feature`, `implement_backend`, `implement_frontend` |
| CodeReviewAgent | `core/agents/code_review_agent.py` | Review code for quality, security, performance | `review_code`, `check_security`, `check_performance` |
| DevOpsAgent | `core/agents/devops_agent.py` | CI/CD pipelines, Docker, K8s, infrastructure | `create_dockerfile`, `create_pipeline`, `create_k8s_manifests` |

### Legal Agents (1)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| LegalDocDrafterAgent | `core/agents/legal/legal_doc_drafter_agent.py` | Draft legal documents, motions, conferral emails | `draft_motion`, `analyze_motion`, `generate_conferral` |

### Blockchain Audit Agents (5)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| SmartContractAuditorAgent | `core/agents/blockchain/smart_contract_auditor_agent.py` | Audit Solidity code for vulnerabilities | `audit_contract`, `detect_vulnerabilities`, `audit_by_address` |
| TransactionMonitorAgent | `core/agents/blockchain/transaction_monitor_agent.py` | Watch for suspicious tx patterns | `monitor_transactions`, `flag_suspicious` |
| WhaleWatcherAgent | `core/agents/blockchain/whale_watcher_agent.py` | Track large token movements (100+ ETH) | `track_whales`, `alert_movements` |
| ExploitDetectorAgent | `core/agents/blockchain/exploit_detector_agent.py` | Pattern match known exploits | `detect_exploits`, `match_patterns` |
| BlockchainAuditCoordinator | `core/agents/blockchain/blockchain_audit_coordinator.py` | Orchestrate all blockchain audit agents | `run_audit_cycle`, `correlate_findings` |

### Stock Audit Agents (5)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| StockAnalystAgent | `core/agents/stocks/stock_analyst_agent.py` | Analyze SEC filings, fundamentals, valuations | `analyze_filing`, `check_valuation`, `assess_risk` |
| MarketMovementMonitorAgent | `core/agents/stocks/market_movement_monitor_agent.py` | Detect unusual price/volume movements | `monitor_movements`, `detect_spikes` |
| InstitutionalWatcherAgent | `core/agents/stocks/institutional_watcher_agent.py` | Track insider trading & 13F filings | `track_insiders`, `analyze_13f` |
| MarketAnomalyDetectorAgent | `core/agents/stocks/market_anomaly_detector_agent.py` | Detect pump & dump, manipulation patterns | `detect_manipulation`, `flag_anomalies` |
| StockAuditCoordinator | `core/agents/stocks/stock_audit_coordinator.py` | Orchestrate all stock audit agents | `run_audit_cycle`, `correlate_findings` |

### Orchestration Agents (4)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| PersonalAssistantAgent | `core/agents/personal_assistant_agent.py` | Main user interaction and routing | `delegate_to_agent`, `process_request` |
| WorkflowAgent | `core/agents/workflow_agent.py` | Multi-step workflow coordination | `execute_workflow`, `chain_agents` |
| WorkflowOrchestrationAgent | `core/agents/workflow_orchestration_agent.py` | Complex workflow management | `orchestrate_workflow`, `manage_steps` |
| AISeriesWorkflowAgent | `core/agents/ai_series_workflow_agent.py` | Multi-episode content series orchestration | `create_series`, `manage_episodes` |

### Pipeline Agents (2)

| Agent | File | Purpose | Key Tools |
|-------|------|---------|-----------|
| OpportunityPipelineAgent | `core/agents/opportunity_pipeline_agent.py` | Income opportunity pipeline management | `process_opportunity`, `track_application` |
| ContentExecutorAgent | `core/agents/content_executor_agent.py` | Execute content creation pipelines | `execute_content`, `manage_assets` |

---

## Part 2: Advisors (25 Total)

Legendary advisors modeled after real-world experts. Location: `advisors/registry.py`

### Financial & Investment Advisors (6)

| ID | Name | Domain | Expertise Level |
|----|------|--------|-----------------|
| `financial_strategist` | Sarah Chen | Financial Planning | Expert |
| `crypto_expert` | Marcus Rodriguez | Crypto Analysis | Master |
| `options_master` | Jennifer Park | Options Trading | Legend |
| `warren_buffett_advisor` | Warren Buffett (AI) | Investment Strategy | Legend |
| `cathie_wood_advisor` | Cathie Wood (AI) | Investment Strategy | Legend |
| `ray_dalio_advisor` | Ray Dalio (AI) | Risk Management | Legend |

### Business & Strategy Advisors (4)

| ID | Name | Domain | Expertise Level |
|----|------|--------|-----------------|
| `business_strategist` | David Kim | Business Strategy | Expert |
| `startup_guru` | Lisa Thompson | Startup Consulting | Master |
| `gary_vaynerchuk_advisor` | Gary Vaynerchuk (AI) | Marketing Strategy | Legend |
| `grant_cardone_advisor` | Grant Cardone (AI) | Sales Optimization | Legend |

### Technology Advisors (4)

| ID | Name | Domain | Expertise Level |
|----|------|--------|-----------------|
| `tech_architect` | Alex Chen | Technical Architecture | Master |
| `ai_strategist` | Dr. Priya Patel | AI/ML Strategy | Legend |
| `elon_musk_advisor` | Elon Musk (AI) | Product Development | Legend |
| `sam_altman_advisor` | Sam Altman (AI) | AI/ML Strategy | Legend |

### Specialized Domain Advisors (7)

| ID | Name | Domain | Expertise Level |
|----|------|--------|-----------------|
| `sports_analytics_expert` | Mike Johnson | Sports Analytics | Master |
| `real_estate_mogul` | Robert Wilson | Real Estate | Legend |
| `legal_counsel` | Amanda Davis | Legal Counsel | Expert |
| `career_coach` | Dr. Maria Gonzalez | Career Coaching | Master |
| `billy_beane_advisor` | Billy Beane (AI) | Sports Analytics | Legend |
| `haralabos_voulgaris_advisor` | Haralabos Voulgaris (AI) | Sports Analytics | Legend |
| `mr_beast_advisor` | MrBeast (AI) | Content Strategy | Legend |

### Leadership & Specialized Advisors (4)

| ID | Name | Domain | Expertise Level |
|----|------|--------|-----------------|
| `chris_voss_advisor` | Chris Voss (AI) | Negotiation Strategy | Legend |
| `dr_peter_attia_advisor` | Dr. Peter Attia (AI) | Healthcare Strategy | Legend |
| `kevin_mitnick_advisor` | Kevin Mitnick (AI) | Cybersecurity | Legend |
| `sal_khan_advisor` | Sal Khan (AI) | Education Strategy | Legend |

### Advisor Domains

```python
class AdvisorDomain(Enum):
    FINANCIAL_PLANNING = "financial_planning"
    INVESTMENT_STRATEGY = "investment_strategy"
    RISK_MANAGEMENT = "risk_management"
    CRYPTO_ANALYSIS = "crypto_analysis"
    OPTIONS_TRADING = "options_trading"
    BUSINESS_STRATEGY = "business_strategy"
    STARTUP_CONSULTING = "startup_consulting"
    MARKETING_STRATEGY = "marketing_strategy"
    SALES_OPTIMIZATION = "sales_optimization"
    OPERATIONS_MANAGEMENT = "operations_management"
    TECHNICAL_ARCHITECTURE = "technical_architecture"
    AI_ML_STRATEGY = "ai_ml_strategy"
    PRODUCT_DEVELOPMENT = "product_development"
    DATA_STRATEGY = "data_strategy"
    CYBERSECURITY = "cybersecurity"
    LEGAL_COUNSEL = "legal_counsel"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    SPORTS_ANALYTICS = "sports_analytics"
    REAL_ESTATE = "real_estate"
    HEALTHCARE_STRATEGY = "healthcare_strategy"
    EDUCATION_STRATEGY = "education_strategy"
    CONTENT_STRATEGY = "content_strategy"
    CAREER_COACHING = "career_coaching"
    LEADERSHIP_DEVELOPMENT = "leadership_development"
    NEGOTIATION_STRATEGY = "negotiation_strategy"
```

---

## Part 3: Spider Network (66 Total)

Location: `ai_core/spiders/specialized/`

### Tech & News Spiders (15)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| HackerNewsSpider | `hackernews_spider.py` | news.ycombinator.com | Yes (JSON) |
| TechCrunchSpider | `techcrunch_spider.py` | techcrunch.com | RSS |
| DevToSpider | `devto_spider.py` | dev.to | Yes (API) |
| WiredSpider | `wired_spider.py` | wired.com | RSS |
| MITTechReviewSpider | `mit_tech_review_spider.py` | technologyreview.com | RSS |
| AxiosSpider | `axios_spider.py` | axios.com | RSS |
| TheVergeSpider | `verge_spider.py` | theverge.com | RSS |
| ArsTechnicaSpider | `arstechnica_spider.py` | arstechnica.com | RSS |
| BBCSpider | `bbc_spider.py` | bbc.com | RSS |
| NPRSpider | `npr_spider.py` | npr.org | RSS |
| ReutersSpider | `reuters_spider.py` | reuters.com | RSS |
| CNNSpider | `cnn_spider.py` | cnn.com | RSS |
| LifeHackerSpider | `lifehacker_spider.py` | lifehacker.com | RSS |
| SmashingMagazineSpider | `smashingmagazine_spider.py` | smashingmagazine.com | RSS |
| HashNodeSpider | `hashnode_spider.py` | hashnode.com | RSS |

### Financial Spiders (8)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| CoinGeckoSpider | `coingecko_spider.py` | coingecko.com | Yes (API) |
| YahooFinanceSpider | `yahoo_finance_spider.py` | finance.yahoo.com | Yes (API) |
| SeekingAlphaSpider | `seekingalpha_spider.py` | seekingalpha.com | RSS |
| BloombergSpider | `bloomberg_spider.py` | bloomberg.com | RSS |
| FinnhubSpider | `finnhub_spider.py` | finnhub.io | Yes (API) |
| PolygonSpider | `polygon_spider.py` | polygon.io | Yes (API) |
| SECSpider | `sec_spider.py` | sec.gov | Yes (EDGAR) |
| OpenSeaSpider | `opensea_spider.py` | opensea.io | Yes (API) |

### Blockchain Spiders (2)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| EtherscanAPISpider | `etherscan_api_spider.py` | Etherscan API V2 | Yes (API) |
| EtherscanSpider | `etherscan_spider.py` | etherscan.io | RSS |

### Jobs & Freelance Spiders (10)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| RemoteOKSpider | `remoteok_spider.py` | remoteok.com | Yes (JSON) |
| WeWorkRemotelySpider | `weworkremotely_spider.py` | weworkremotely.com | RSS |
| AdzunaSpider | `adzuna_spider.py` | adzuna.com | Yes (API) |
| FlexJobsSpider | `flexjobs_spider.py` | flexjobs.com | Scraper |
| AngelListSpider | `angellist_spider.py` | angel.co | Scraper |
| ToptalSpider | `toptal_spider.py` | toptal.com | Scraper |
| FiverrSpider | `fiverr_spider.py` | fiverr.com | Scraper |
| GuruSpider | `guru_spider.py` | guru.com | Scraper |
| PeoplePerHourSpider | `peopleperhour_spider.py` | peopleperhour.com | Scraper |
| HimalayasSpider | `himalayas_spider.py` | himalayas.app | Yes (API) |

### Creative & Design Spiders (10)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| DribbbleSpider | `dribbble_spider.py` | dribbble.com | Yes (API) |
| BehanceSpider | `behance_spider.py` | behance.net | Yes (API) |
| UnsplashSpider | `unsplash_spider.py` | unsplash.com | Yes (API) |
| FigmaSpider | `figma_spider.py` | figma.com | Scraper |
| CanvaSpider | `canva_spider.py` | canva.com | Scraper |
| ShutterstockSpider | `shutterstock_spider.py` | shutterstock.com | Yes (API) |
| AdobeStockSpider | `adobestock_spider.py` | stock.adobe.com | Yes (API) |
| CreativeMarketSpider | `creativemarket_spider.py` | creativemarket.com | Scraper |
| EnvatoSpider | `envato_spider.py` | envato.com | Scraper |
| 99DesignsSpider | `ninetyninedesigns_spider.py` | 99designs.com | Scraper |

### AI & ML Spiders (6)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| HuggingFaceSpider | `huggingface_spider.py` | huggingface.co | Yes (API) |
| MidjourneySpider | `midjourney_spider.py` | midjourney.com | Scraper |
| CivitaiSpider | `civitai_spider.py` | civitai.com | Yes (API) |
| RunwayMLSpider | `runwayml_spider.py` | runwayml.com | Scraper |
| ReplicateSpider | `replicate_spider.py` | replicate.com | Yes (API) |
| KaggleSpider | `kaggle_spider.py` | kaggle.com | Yes (API) |

### Digital Products Spiders (5)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| GumroadSpider | `gumroad_spider.py` | gumroad.com | Yes (API) |
| EtsySpider | `etsy_spider.py` | etsy.com | Yes (API) |
| LemonSqueezySpider | `lemonsqueezy_spider.py` | lemonsqueezy.com | Yes (API) |
| AppSumoSpider | `appsumo_spider.py` | appsumo.com | Scraper |
| SellfySpider | `sellfy_spider.py` | sellfy.com | Scraper |

### Content & Media Spiders (5)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| MediumSpider | `medium_spider.py` | medium.com | RSS |
| YouTubeSpider | `youtube_spider.py` | youtube.com | Yes (API) |
| SpotifySpider | `spotify_spider.py` | spotify.com | Yes (API) |
| IndieHackersSpider | `indiehackers_spider.py` | indiehackers.com | Scraper |
| VarietySpider | `variety_spider.py` | variety.com | RSS |

### Legal Spiders (5)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| CourtListenerSpider | `courtlistener_spider.py` | courtlistener.com | Yes (API) |
| JustiaSpider | `justia_spider.py` | justia.com | Scraper |
| JustiaPlaywrightSpider | `justia_playwright_spider.py` | justia.com | Playwright |
| FindLawSpider | `findlaw_spider.py` | findlaw.com | Scraper |
| LIISpider | `lii_spider.py` | law.cornell.edu | Scraper |
| ColoradoFamilyLawSpider | `colorado_family_law_spider.py` | Colorado courts | Playwright |

### Community Spiders (3)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| RedditSpider | `reddit_spider.py` | reddit.com (20+ subs) | Yes (API) |
| DiscordSpider | `discord_spider.py` | discord.com | Scraper |
| BlueSkySpider | `bluesky_spider.py` | bsky.app | Yes (API) |

### Education Spiders (3)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| TeachableSpider | `teachable_spider.py` | teachable.com | Scraper |
| UdemySpider | `udemy_spider.py` | udemy.com | Yes (API) |
| SkillshareSpider | `skillshare_spider.py` | skillshare.com | Scraper |

### Crowdfunding Spiders (4)

| Spider | File | Data Source | Real API |
|--------|------|-------------|----------|
| KickstarterSpider | `kickstarter_spider.py` | kickstarter.com | Scraper |
| KickstarterPlaywrightSpider | `kickstarter_playwright_spider.py` | kickstarter.com | Playwright |
| IndiegogoSpider | `indiegogo_spider.py` | indiegogo.com | Scraper |
| IndiegogoPlaywrightSpider | `indiegogo_playwright_spider.py` | indiegogo.com | Playwright |

---

## Part 4: Learning Systems

### Learning Bridges (10)

Location: `core/learning_bridges/`

| Bridge | File | Purpose |
|--------|------|---------|
| SpiderDataBridge | `spider_data_bridge.py` | Feed spider data to agent prompts |
| AgentExecutionBridge | `agent_execution_bridge.py` | Track agent execution for learning |
| ApplicationOutcomeBridge | `application_outcome_bridge.py` | Learn from job application outcomes |
| CollaborationBridge | `collaboration_bridge.py` | Learn from agent collaborations |
| PersonalizationBridge | `personalization_bridge.py` | User preference learning |
| RevenueAttributionBridge | `revenue_attribution_bridge.py` | Track revenue generation learning |
| AdvisorFeedbackBridge | `advisor_feedback_bridge.py` | Learn from advisor consultations |
| SportsBettingBridge | `sports_betting_bridge.py` | Sports prediction learning |

### Collective Intelligence Services

Location: `core/services/`

| Service | File | Purpose |
|---------|------|---------|
| CollectiveIntelligence | `collective_intelligence.py` | Central knowledge sharing hub |
| AgentLearningService | `agent_learning_service.py` | Manage agent knowledge |
| AgentCollaborationHub | `agent_collaboration_hub.py` | Multi-agent collaboration |
| AgentCollaboration | `agent_collaboration.py` | Agent teamwork |
| ImplicitLearning | `implicit_learning.py` | Background learning from usage |
| PipelineLearning | `pipeline_learning.py` | Learn from pipeline executions |

---

## Part 5: Sci-Fi Features (15)

Database models: `core/models_unified_system.py`

| Feature | Model | Purpose |
|---------|-------|---------|
| Agent Learning | `AgentKnowledge` | Agents learn from each other |
| Agent Conversations | `AgentConversation` | Real-time AI-to-AI chat |
| Agent Dreams | `AgentDream` | Creative thoughts when idle |
| Hive Mind Mode | `HiveMindSession` | Collective intelligence problem-solving |
| Memory Palace | `AgentMemory` | Persistent agent memory |
| Mood System | `AgentMood` | Emotional states affect behavior |
| Rivalries/Alliances | `AgentRelationship` | Agent relationships and dynamics |
| Evolution System | `AgentEvolution` | XP, levels, progression |
| Time Travel Debug | `AgentDecision` | Replay agent decision-making |
| Personality Profiles | `AgentPersonality` | Distinct agent personalities |
| Memory Clusters | `MemoryCluster` | Grouped related memories |
| Prophecies | `AgentProphecy` | Agent predictions and forecasts |
| Time Capsules | `TimeCapsule` | Messages to future selves |
| Conversation Contract | `ConversationQuality` | Quality scoring for conversations |
| Spider Integration | Real-time via bridge | Agents use spider data in prompts |

---

## Part 6: Autonomous Loops (3)

### AutonomousIntelligenceLoop

Location: `core/services/autonomous_loop.py`

**Runs:** Every 15 minutes via Celery Beat

| Component | Method | Purpose |
|-----------|--------|---------|
| SEC Filing Monitor | `check_sec_filings()` | Monitor SEC EDGAR for new filings |
| Content Opportunity Scanner | `check_content_opportunities()` | Scan for content creation opportunities |
| Job Opportunity Scanner | `check_job_opportunities()` | Find matching job opportunities |
| Stock Security Check | `check_stock_security()` | Run stock audit agent group |
| Blockchain Security Check | `check_blockchain_security()` | Run blockchain audit agent group |

### BlockchainEventListener

Location: `core/services/blockchain_event_listener.py`

**Runs:** Continuous background thread (15-second polling)

| Event Type | Description |
|------------|-------------|
| WHALE_TRANSFER | Large ETH movements (100+ ETH) |
| CONTRACT_DEPLOY | New contract deployments |
| SUSPICIOUS_TX | Unusual transaction patterns |
| EXPLOIT_SIGNATURE | Known exploit pattern detection |

### Celery Beat Schedules

Location: `core/celery.py`

| Task | Schedule | Purpose |
|------|----------|---------|
| `run_autonomous_loop` | Every 15 min | Full autonomous cycle |
| `run_stock_audit_cycle` | Every 30 min (market hours) | Stock monitoring |
| `run_blockchain_audit_cycle` | Every 15 min | Blockchain monitoring |
| `generate_agent_dreams` | Every 30 min | Agent idle thoughts |
| `run_daily_digest` | Daily at 8am | User opportunity digest |
| `send_daily_digest` | Daily at 9am | Email digests |
| `cleanup_old_records` | Daily at 3am | Database maintenance |

---

## Part 7: Core Services (40+)

Location: `core/services/`

### Intelligence & Learning

| Service | File | Purpose |
|---------|------|---------|
| CollectiveIntelligence | `collective_intelligence.py` | Central knowledge hub |
| AgentLearningService | `agent_learning_service.py` | Agent knowledge management |
| AgentIntelligenceContext | `agent_intelligence_context.py` | Context injection for agents |
| RecommendationEngine | `recommendation_engine.py` | Personalized recommendations |
| KnowledgeSimilarity | `knowledge_similarity.py` | Vector similarity search |

### Content & Creation

| Service | File | Purpose |
|---------|------|---------|
| ContentPipeline | `content_pipeline.py` | 6-tier content factory |
| CreativeOrchestrator | `creative_orchestrator.py` | Complex creative workflows |
| ResearchOrchestrator | `research_orchestrator.py` | Research coordination |
| ResearchToCreativePipeline | `research_to_creative_pipeline.py` | Research → Content flow |

### Communication

| Service | File | Purpose |
|---------|------|---------|
| DiscordBot | `discord_bot.py` | 45 interactive commands |
| DiscordNotifications | `discord_notifications.py` | Alert delivery |
| DiscordVoice | `discord_voice.py` | Voice recording/cloning |

### Analytics & Monitoring

| Service | File | Purpose |
|---------|------|---------|
| AnalyticsService | `analytics_service.py` | Platform analytics |
| ABTesting | `ab_testing.py` | A/B test framework |
| AutonomousLoop | `autonomous_loop.py` | Autonomous monitoring |
| BlockchainEventListener | `blockchain_event_listener.py` | Blockchain monitoring |

### Legal

| Service | File | Purpose |
|---------|------|---------|
| LitigationBrain | `litigation_brain.py` | Legal document analysis |
| ResearchPDFService | `research_pdf_service.py` | PDF extraction |

### Marketplace

| Service | File | Purpose |
|---------|------|---------|
| MarketplaceDiscoveryService | `marketplace_discovery_service.py` | Opportunity discovery |
| IncomeActionService | `income_action_service.py` | Job application actions |
| CertificateService | `certificate_service.py` | User certifications |

---

## Part 8: Agent Routing & Registration

### Agent Router

Location: `core/agent_router.py`

The router uses **deterministic routing** (no LLM involved) based on keyword patterns:

```python
ROUTING_PATTERNS = {
    'image': ['logo', 'image', 'picture', 'photo', 'banner', 'illustration'],
    'video': ['video', 'animation', 'animate', 'clip'],
    'audio': ['voice', 'audio', 'sound', 'speech', 'narration'],
    'research': ['research', 'find', 'search', 'look up', 'trending'],
    'legal': ['motion', 'legal', 'court', 'filing', 'attorney'],
    'code': ['code', 'function', 'implement', 'debug', 'refactor'],
    # ... etc
}
```

### Agent Registry

Location: `core/agents/registry.py`

Maintains runtime registration of all agents with:
- Agent instances
- Capability mappings
- Tool definitions
- Learning hook connections

---

## Part 9: Database Models for Intelligence

Location: `core/models_unified_system.py`

### Core Intelligence Models

| Model | Purpose |
|-------|---------|
| `Agent` | Agent definitions and stats |
| `AgentKnowledge` | Learned knowledge entries |
| `AgentConversation` | AI-to-AI conversations |
| `AgentDream` | Agent idle thoughts |
| `AgentMemory` | Persistent memories |
| `AgentMood` | Emotional states |
| `AgentDecision` | Time travel tracking |
| `AgentEvolution` | XP and leveling |
| `AgentRelationship` | Rivalries/alliances |
| `HiveMindSession` | Collective sessions |

### Data Models

| Model | Purpose |
|-------|---------|
| `SpiderData` | Raw spider data storage |
| `Opportunity` | Income opportunities |
| `OpportunityApplication` | Job applications |
| `ABTest` | A/B testing data |
| `UserGoal` | User goals and targets |

---

## Part 10: Extension Points

### Adding a New Agent

1. Create file in `core/agents/your_agent.py`
2. Inherit from `BaseAgent`
3. Define tools with `get_tools()`
4. Implement `execute()` method
5. Register in `core/agents/__init__.py`
6. Add routing pattern in `core/agent_router.py`

### Adding a New Spider

1. Create file in `ai_core/spiders/specialized/your_spider.py`
2. Inherit from `BaseSpider`
3. Implement `crawl()` method
4. Register in `ai_core/spiders/spider_registry.py`

### Adding a New Advisor

1. Add entry to `_initialize_advisor_network()` in `advisors/registry.py`
2. Define domain, specializations, decision frameworks
3. Advisor automatically available via Discord `/consult`

### Adding a New Learning Bridge

1. Create file in `core/learning_bridges/your_bridge.py`
2. Inherit from base bridge class
3. Implement `process()` and `learn()` methods
4. Register signal handlers

---

## Appendix: File Structure

```
unified-donkey-betz/
├── core/
│   ├── agents/                  # 48 agents
│   │   ├── blockchain/          # 5 blockchain audit agents
│   │   ├── stocks/              # 5 stock audit agents
│   │   ├── business/            # 5 business research agents
│   │   ├── executive/           # 4 executive agents
│   │   ├── strategy/            # 4 strategy agents
│   │   ├── analysis/            # 3 analysis agents
│   │   ├── security/            # 2 security agents
│   │   ├── training/            # 2 training agents
│   │   ├── legal/               # 1 legal agent
│   │   └── *.py                 # Core agents
│   ├── services/                # 40+ services
│   ├── learning_bridges/        # 10 learning bridges
│   └── models_unified_system.py # Sci-Fi models
├── advisors/
│   └── registry.py              # 25 advisors
├── ai_core/
│   └── spiders/
│       └── specialized/         # 66 spiders
└── docs/
    └── SYSTEM_INTELLIGENCE_ATLAS.md  # This file
```

---

**This atlas is a living document. Update as new components are added.**
