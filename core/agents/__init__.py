"""
Unified Agent System - Clean Architecture
==========================================

Session 268: Phase 1 & 2 - Complete Agent Ecosystem
Session 280: Phase 2 - Strategy and Executive Agents
Session 281: Phase 3 - Analysis, Training, and Security Agents
Session 392: Migrated AgentRegistry from agents/registry.py

All agents inherit from BaseAgent and follow these principles:
1. Isolated tools - each agent only has access to its own tools
2. Time Travel Debugging - all decisions are recorded via TimeTravelMixin
3. Spider Context - agents receive relevant spider data (trends, market)
4. Sci-Fi Integration - mood, memory, evolution affect behavior

Architecture:
    User → Personal Assistant → Agent Router → Specialized Agents → Tools

Usage:
    # Direct import
    from core.agents import ImageAgent, VideoAgent

    # Sub-package import
    from core.agents.strategy import ContentStrategyAgent
    from core.agents.executive import CTOAgent
    from core.agents.analysis import TrendAnalysisAgent
    from core.agents.training import CharacterTrainingAgent
    from core.agents.security import MemoryIsolationAgent
    from core.agents.business import CompetitorAnalysisAgent, CustomerResearchAgent

    # Via AgentRouter (recommended)
    from core.agent_router import AgentRouter

    router = AgentRouter(user=request.user)
    result = router.route("ImageAgent", "create a cyberpunk logo", context={})

Available Agents (41 total):

    CREATION AGENTS (4):
        ImageAgent          - Image generation (logos, banners, illustrations)
        VideoAgent          - Video generation (text-to-video, animations)
        AudioAgent          - Audio generation (TTS, voiceovers)
        ThreeDAgent         - 3D model generation

    EDITING AGENTS (2):
        ImageEditingAgent   - Image editing (upscale, remove bg, variations)
        VideoEditingAgent   - Video editing (trim, effects, text)

    RESEARCH AGENTS (1):
        ResearchAgent       - Web search + spider network queries

    STRATEGY AGENTS (4) - Session 280:
        ContentStrategyAgent - Content recommendations from trends
        BrandIdentityAgent   - Brand colors, styles, consistency
        SEOOptimizerAgent    - Hashtags, metadata, keywords
        SocialMediaAgent     - Platform-specific content strategy

    EXECUTIVE AGENTS (4) - Session 280:
        CTOAgent              - Technical planning and analysis
        COOAgent              - Operations planning and risk analysis
        CreativeDirectorAgent - Creative guidance and prompt enhancement
        MeetingCoordinatorAgent - Coordinates meetings between agents

    ANALYSIS AGENTS (3) - Session 281, expanded Session 385:
        TrendAnalysisAgent       - Spider intelligence analysis
        OpportunityScoringAgent  - Opportunity scoring engine
        MarketIntelligenceAgent  - SEC filings, crypto, stocks analysis

    TRAINING AGENTS (2) - Session 281:
        CharacterTrainingAgent  - FLUX LoRA character training
        TrainedCreationAgent    - LoRA image generation

    SECURITY AGENTS (1) - Session 281:
        MemoryIsolationAgent    - Memory isolation and security

    BUSINESS RESEARCH AGENTS (5) - Session 293, expanded Session 337:
        CompetitorAnalysisAgent - Competitor analysis, SWOT, positioning
        CustomerResearchAgent   - Customer personas, pain points, sentiment
        BrandStrategyAgent      - Brand positioning, messaging, visual direction
        MarketingStrategyAgent  - Channel strategy, campaigns, funnel optimization
        BusinessContentStrategyAgent - Content pillars, formats, topic ideas

    DEVELOPMENT AGENTS (4) - Session 436:
        CodeGeneratorAgent       - Generate code from specifications
        FullStackDeveloperAgent  - Build complete features (frontend + backend)
        CodeReviewAgent          - Review code for quality, security, best practices
        DevOpsAgent              - CI/CD, Docker, Kubernetes, infrastructure

    ORCHESTRATION AGENTS (4) - Session 393:
        WorkflowAgent               - Multi-step workflow coordination (GPT-driven)
        WorkflowOrchestrationAgent  - Predefined workflow packages (16+ templates)
        OpportunityPipelineAgent    - Multi-stage opportunity execution (value multiplication)
        ContentExecutorAgent        - AI content generation for platform

    CONTENT WRITING AGENTS (1) - Session 496:
        ContentWriterAgent          - Transform research into blog posts, podcasts, articles

    CONTENT EDITING AGENTS (1) - Session 864:
        EditorAgent                 - Enhance content structure for publishing readiness

    ENTRY POINT:
        PersonalAssistantAgent  - REMOVED (deprecated, all PA traffic routes through Rigby)

    BLOCKCHAIN AUDIT AGENTS (5) - Session 461:
        SmartContractAuditorAgent   - Solidity code vulnerability detection
        TransactionMonitorAgent     - Suspicious transaction pattern monitoring
        WhaleWatcherAgent           - Large token movement tracking
        ExploitDetectorAgent        - Known exploit signature matching
        BlockchainAuditCoordinator  - Orchestrates all blockchain audit agents

Legacy Compatibility:
    The old `agents` package still works but emits deprecation warnings:

    # OLD (deprecated, shows warning):
    from agents import ImageAgent

    # NEW (preferred, no warning):
    from core.agents import ImageAgent
"""

# Base classes
from core.agents.base_agent import BaseAgent, AgentResult

# Registry (Session 392)
from core.agents.registry import (
    AgentRegistry,
    AgentCapability,
    AgentPerformanceStats,
    RegistryStats,
    get_agent_registry,
    get_agent,
    list_agents,
    find_best_agent,
    execute_agent,
    agent_registry,
)

# Creation Agents
from core.agents.image_agent import ImageAgent
from core.agents.video_agent import VideoAgent, get_video_agent
from core.agents.audio_agent import AudioAgent, get_audio_agent
from core.agents.talking_character_agent import TalkingCharacterAgent, get_talking_character_agent
from core.agents.three_d_agent import ThreeDAgent

# Editing Agents
from core.agents.image_editing_agent import ImageEditingAgent
from core.agents.video_editing_agent import VideoEditingAgent

# Research Agents
from core.agents.research_agent import ResearchAgent

# Platform Audit Agent (Session 857: Internal platform auditing)
from core.agents.platform_audit_agent import PlatformAuditAgent

# Orchestration Agents (Session 393: Added 3 new orchestrators)
from core.agents.workflow_agent import WorkflowAgent
from core.agents.workflow_orchestration_agent import (
    WorkflowOrchestrationAgent,
    get_workflow_orchestration_agent,
    AVAILABLE_WORKFLOWS,
)
from core.agents.opportunity_pipeline_agent import (
    OpportunityPipelineAgent,
    get_opportunity_pipeline_agent,
    PIPELINE_STAGES,
)
from core.agents.content_executor_agent import (
    ContentExecutorAgent,
    get_content_executor_agent,
    CONTENT_TYPES,
)

# PersonalAssistantAgent removed — deprecated, all PA traffic routes through Rigby

# Strategy Agents (Session 280)
from core.agents.strategy import (
    ContentStrategyAgent,
    BrandIdentityAgent,
    SEOOptimizerAgent,
    SocialMediaAgent,
)

# Executive Agents (Session 280)
from core.agents.executive import (
    CTOAgent,
    COOAgent,
    CreativeDirectorAgent,
    MeetingCoordinatorAgent,
)

# Analysis Agents (Session 281, expanded Session 385)
from core.agents.analysis import (
    TrendAnalysisAgent,
    OpportunityScoringAgent,
    MarketIntelligenceAgent,
)

# Training Agents (Session 281)
from core.agents.training import (
    CharacterTrainingAgent,
    TrainedCreationAgent,
)

# Security Agents (Session 281)
from core.agents.security import (
    MemoryIsolationAgent,
)

# Business Research Agents (Session 293, expanded Session 337)
from core.agents.business import (
    CompetitorAnalysisAgent,
    CustomerResearchAgent,
    BrandStrategyAgent,
    ContentStrategyAgent as BusinessContentStrategyAgent,  # Alias to avoid conflict
    MarketingStrategyAgent,
)

# Development Agents (Session 436, expanded Session 778)
from core.agents.code_generator_agent import CodeGeneratorAgent
from core.agents.fullstack_developer_agent import FullStackDeveloperAgent
from core.agents.code_review_agent import CodeReviewAgent
from core.agents.devops_agent import DevOpsAgent
from core.agents.prompt_engineering_agent import PromptEngineeringAgent

# Series Workflow Agent (Session 445)
from core.agents.ai_series_workflow_agent import AISeriesWorkflowAgent, get_ai_series_workflow_agent

# Autonomous Content Studio Coordinator (Session 466)
from core.agents.autonomous_content_studio_coordinator import AutonomousContentStudioCoordinator

# Content Debate Agents (Session 466)
from core.agents.content import (
    TopicMinerAgent,
    ContrarianAgent,
    PerformanceAnalystAgent,
)

# Rendering Agents (Session 478: DaVinci Resolve Integration)
from core.agents.resolve_agent import ResolveAgent, get_resolve_agent

# Content Writer Agent (Session 496: Written content from research)
from core.agents.content_writer_agent import ContentWriterAgent, get_content_writer_agent

# Editor Agent (Session 864: Content structure enhancement)
from core.agents.editor_agent import EditorAgent, enhance_blog, enhance_all_needing_enhancement

# Technical Document Agent (Session 622: Formal technical documents with governance)
from core.agents.technical_document_agent import (
    TechnicalDocumentAgent,
    infer_stage_from_deliverable,
    get_stage_for_doc_type,
    DOCUMENT_STAGES,
)

# Blockchain Audit Agents (Session 461)
from core.agents.blockchain import (
    SmartContractAuditorAgent,
    TransactionMonitorAgent,
    WhaleWatcherAgent,
    ExploitDetectorAgent,
    BlockchainAuditCoordinator,
)

# Narrative Drift Detector Agents (Session 471)
from core.agents.narrative import (
    NarrativeHistorianAgent,
    TrendBreakDetectorAgent,
    CulturalImpactAgent,
    NarrativeDriftCoordinator,
)

# Podcast Studio Agents (Session 496)
from core.agents.podcast import (
    PodcastCoordinatorAgent,
    DebateAdvocateAgent,
    DebateSkepticAgent,
    ModeratorAgent,
)

# Campaign Orchestrator Agent (Session 513: Marketing Campaign Hub)
from core.agents.campaign_orchestrator_agent import (
    CampaignOrchestratorAgent,
    get_campaign_orchestrator_agent,
)

# Markets Agents (Session 558: Prediction Markets & Sports Odds)
from core.agents.markets import (
    PredictionMarketAnalyst,
    SportsOddsAnalyst,
    ArbitrageDetector,
)

# Stock Audit Agents (Session 461 + 637: Full stock agent suite)
from core.agents.stocks import (
    StockAuditCoordinator,
    StockAnalystAgent,
    MarketMovementMonitorAgent,
    InstitutionalWatcherAgent,
    MarketAnomalyDetectorAgent,
    BullCaseAgent,
    BearCaseAgent,
    SignalScannerAgent,
    MarketIntelligenceCoordinator,
)

# Thinking Agent (Session 593: AI-powered evaluation and reasoning)
from core.agents.thinking_agent import ThinkingAgent

# System Intelligence Agent (Session 663: Platform health and attention monitoring)
from core.agents.system_intelligence_agent import SystemIntelligenceAgent

# Decision Enforcer Agent (Session 872: Prefrontal cortex - forces decisions after debate)
from core.agents.decision_enforcer_agent import (
    DecisionEnforcerAgent,
    enforce_decision_after_synthesis,
)

__all__ = [
    # Base
    'BaseAgent',
    'AgentResult',

    # Registry (Session 392)
    'AgentRegistry',
    'AgentCapability',
    'AgentPerformanceStats',
    'RegistryStats',
    'get_agent_registry',
    'get_agent',
    'list_agents',
    'find_best_agent',
    'execute_agent',
    'agent_registry',

    # Creation Agents (4) + factory functions
    'ImageAgent',
    'VideoAgent',
    'get_video_agent',
    'AudioAgent',
    'get_audio_agent',
    'TalkingCharacterAgent',
    'get_talking_character_agent',
    'ThreeDAgent',

    # Editing Agents (2)
    'ImageEditingAgent',
    'VideoEditingAgent',

    # Research Agents (1)
    'ResearchAgent',

    # Orchestration Agents (4) - Session 393
    'WorkflowAgent',
    'WorkflowOrchestrationAgent',
    'get_workflow_orchestration_agent',
    'AVAILABLE_WORKFLOWS',
    'OpportunityPipelineAgent',
    'get_opportunity_pipeline_agent',
    'PIPELINE_STAGES',
    'ContentExecutorAgent',
    'get_content_executor_agent',
    'CONTENT_TYPES',

    # PersonalAssistantAgent removed (deprecated)

    # Strategy Agents (4) - Session 280
    'ContentStrategyAgent',
    'BrandIdentityAgent',
    'SEOOptimizerAgent',
    'SocialMediaAgent',

    # Executive Agents (4) - Session 280
    'CTOAgent',
    'COOAgent',
    'CreativeDirectorAgent',
    'MeetingCoordinatorAgent',

    # Analysis Agents (3) - Session 281, expanded Session 385
    'TrendAnalysisAgent',
    'OpportunityScoringAgent',
    'MarketIntelligenceAgent',

    # Training Agents (2) - Session 281
    'CharacterTrainingAgent',
    'TrainedCreationAgent',

    # Security Agents (1) - Session 281
    'MemoryIsolationAgent',

    # Business Research Agents (5) - Session 293, expanded Session 337
    'CompetitorAnalysisAgent',
    'CustomerResearchAgent',
    'BrandStrategyAgent',
    'BusinessContentStrategyAgent',
    'MarketingStrategyAgent',

    # Development Agents (5) - Session 436, expanded Session 778
    'CodeGeneratorAgent',
    'FullStackDeveloperAgent',
    'CodeReviewAgent',
    'DevOpsAgent',
    'PromptEngineeringAgent',

    # Series Workflow Agent (1) - Session 445
    'AISeriesWorkflowAgent',
    'get_ai_series_workflow_agent',

    # Autonomous Content Studio (4) - Session 466
    'AutonomousContentStudioCoordinator',
    'TopicMinerAgent',
    'ContrarianAgent',
    'PerformanceAnalystAgent',

    # Rendering Agents (1) - Session 478
    'ResolveAgent',
    'get_resolve_agent',

    # Content Writer Agent (1) - Session 496
    'ContentWriterAgent',
    'get_content_writer_agent',

    # Editor Agent (1) - Session 864
    'EditorAgent',
    'enhance_blog',
    'enhance_all_needing_enhancement',

    # Technical Document Agent (1) - Session 622
    'TechnicalDocumentAgent',
    'infer_stage_from_deliverable',
    'get_stage_for_doc_type',
    'DOCUMENT_STAGES',

    # Blockchain Audit Agents (5) - Session 461
    'SmartContractAuditorAgent',
    'TransactionMonitorAgent',
    'WhaleWatcherAgent',
    'ExploitDetectorAgent',
    'BlockchainAuditCoordinator',

    # Narrative Drift Detector Agents (4) - Session 471
    'NarrativeHistorianAgent',
    'TrendBreakDetectorAgent',
    'CulturalImpactAgent',
    'NarrativeDriftCoordinator',

    # Podcast Studio Agents (4) - Session 496
    'PodcastCoordinatorAgent',
    'DebateAdvocateAgent',
    'DebateSkepticAgent',
    'ModeratorAgent',

    # Campaign Orchestrator Agent (1) - Session 513
    'CampaignOrchestratorAgent',
    'get_campaign_orchestrator_agent',

    # Markets Agents (3) - Session 558
    'PredictionMarketAnalyst',
    'SportsOddsAnalyst',
    'ArbitrageDetector',

    # Stock Audit Agents (9) - Session 461 + 637
    'StockAuditCoordinator',
    'StockAnalystAgent',
    'MarketMovementMonitorAgent',
    'InstitutionalWatcherAgent',
    'MarketAnomalyDetectorAgent',
    'BullCaseAgent',
    'BearCaseAgent',
    'SignalScannerAgent',
    'MarketIntelligenceCoordinator',

    # Thinking Agent (1) - Session 593
    'ThinkingAgent',

    # System Intelligence Agent (1) - Session 663
    'SystemIntelligenceAgent',

    # Decision Enforcer Agent (1) - Session 872
    'DecisionEnforcerAgent',
    'enforce_decision_after_synthesis',
]
