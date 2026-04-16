"""
Agent Router - Deterministic Routing to Specialized Agents
===========================================================

Session 268: Phase 1 & 2 - Complete Agent Ecosystem
Session 280: Phase 2 - Added Strategy and Executive Agents
Session 280: Phase 3 - Added Analysis, Training, and Security Agents
Session 488: Semantic Routing Integration - Use embeddings to find best agent

This router provides DETERMINISTIC routing to specialized agents.
No LLM is involved in routing decisions - it's a simple dictionary lookup.
NEW: Semantic routing option uses embeddings for intelligent agent selection.

This prevents the current problem where GPT picks the wrong tool
(e.g., video_generation_agent for a logo request).

Architecture:
    User → Personal Assistant → Agent Router → Specialized Agent → Tools

The Personal Assistant calls delegate_to_agent("ImageAgent", task).
The router looks up "ImageAgent" in the AGENT_MAP and executes it.

Key Design Decisions:
1. Routing is deterministic (string match on agent_name)
2. Each agent is instantiated fresh per request
3. Sci-Fi and Spider context are injected before execution
4. Results are returned as AgentResult objects

Usage:
    from core.agent_router import AgentRouter

    router = AgentRouter(user=request.user)
    result = router.route("ImageAgent", "create a cyberpunk logo", context={})

Available Agents:
    Creation:
    - ImageAgent: Image generation (logos, banners, illustrations)
    - VideoAgent: Video generation (text-to-video, animations)
    - AudioAgent: Audio generation (TTS, voiceovers)
    - ThreeDAgent: 3D model generation

    Editing:
    - ImageEditingAgent: Image editing (upscale, remove bg, variations)
    - VideoEditingAgent: Video editing (trim, effects, text)

    Research:
    - ResearchAgent: Web search + spider network queries

    Strategy (Session 280):
    - ContentStrategyAgent: Content recommendations based on trends
    - BrandIdentityAgent: Brand consistency management
    - SEOOptimizerAgent: Hashtags, keywords, metadata
    - SocialMediaAgent: Platform-specific content strategy

    Executive (Session 280):
    - CTOAgent: Technical planning and analysis
    - COOAgent: Operations planning and risk analysis
    - CreativeDirectorAgent: Creative guidance and prompt enhancement
    - MeetingCoordinatorAgent: Coordinates meetings between agents

    Analysis (Session 280 Phase 3):
    - TrendAnalysisAgent: Spider intelligence analysis
    - OpportunityScoringAgent: Opportunity scoring engine

    Training (Session 280 Phase 3):
    - CharacterTrainingAgent: FLUX LoRA character training
    - TrainedCreationAgent: LoRA image generation

    Security (Session 280 Phase 3):
    - MemoryIsolationAgent: Memory isolation and security

    Business Research (Session 293):
    - CompetitorAnalysisAgent: Competitor analysis and SWOT
    - CustomerResearchAgent: Customer personas and pain points

    Markets (Session 558):
    - PredictionMarketAnalyst: Kalshi prediction market analysis
    - SportsOddsAnalyst: Sports betting odds analysis (The Odds API)

    Orchestration:
    - WorkflowAgent: Multi-step workflow coordination
"""

import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Dict, Any, Optional, Type
from django.utils import timezone
from django.db.models import F

from core.agents.base_agent import BaseAgent, AgentResult
from core.agents.image_agent import ImageAgent
from core.agents.video_agent import VideoAgent
from core.agents.audio_agent import AudioAgent
from core.agents.talking_character_agent import TalkingCharacterAgent
from core.agents.three_d_agent import ThreeDAgent
from core.agents.image_editing_agent import ImageEditingAgent
from core.agents.video_editing_agent import VideoEditingAgent
from core.agents.research_agent import ResearchAgent
from core.agents.workflow_agent import WorkflowAgent
# PersonalAssistantAgent removed — all PA traffic routes through Rigby (UnifiedPAEntrypoint)

# Session 280: Strategy Agents
from core.agents.strategy import (
    ContentStrategyAgent,
    BrandIdentityAgent,
    SEOOptimizerAgent,
    SocialMediaAgent,
)

# Session 280: Executive Agents
from core.agents.executive import (
    CTOAgent,
    COOAgent,
    CreativeDirectorAgent,
    MeetingCoordinatorAgent,
)

# Session 280 Phase 3: Analysis Agents
from core.agents.analysis import (
    TrendAnalysisAgent,
    OpportunityScoringAgent,
)

# Session 280 Phase 3: Training Agents
from core.agents.training import (
    CharacterTrainingAgent,
    TrainedCreationAgent,
)

# Session 280 Phase 3: Security Agents
from core.agents.security import (
    MemoryIsolationAgent,
)

# Session 779/790: Prompt Engineering Agent
from core.agents.prompt_engineering_agent import PromptEngineeringAgent

# Session 293: Business Research Agents (+ Session 637)
from core.agents.business import (
    CompetitorAnalysisAgent,
    CustomerResearchAgent,
    BrandStrategyAgent,
    MarketingStrategyAgent,
)

# Session 385: Market Intelligence Agent (from analysis)
from core.agents.analysis import MarketIntelligenceAgent

# Session 403: Legal Agents
from core.agents.legal import (
    LegalDocDrafterAgent,
)

# Session 436: Development Agents
from core.agents.code_generator_agent import CodeGeneratorAgent
from core.agents.fullstack_developer_agent import FullStackDeveloperAgent
from core.agents.code_review_agent import CodeReviewAgent
from core.agents.devops_agent import DevOpsAgent

# Session 461: Security Agents (full set)
from core.agents.security import ContentAuditAgent

# Session 461: Stock Audit Agents (full set - Session 637)
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

# Session 461: Blockchain Audit Agents (full set - Session 637)
from core.agents.blockchain import (
    BlockchainAuditCoordinator,
    SmartContractAuditorAgent,
    TransactionMonitorAgent,
    WhaleWatcherAgent,
    ExploitDetectorAgent,
)

# Session 471: Narrative Drift Agents (Session 637)
from core.agents.narrative import (
    NarrativeDriftCoordinator,
    NarrativeHistorianAgent,
    TrendBreakDetectorAgent,
    CulturalImpactAgent,
)

# Session 445: Series Workflow Agent
from core.agents.ai_series_workflow_agent import AISeriesWorkflowAgent

# Session 466: Autonomous Content Studio
from core.agents.autonomous_content_studio_coordinator import AutonomousContentStudioCoordinator
from core.agents.content import TopicMinerAgent, ContrarianAgent, PerformanceAnalystAgent, VoiceCriticAgent
from core.agents.distribution_agent import DistributionAgent
# Session 743: Content Diversity Orchestrator
from core.agents.content_diversity_orchestrator import ContentDiversityOrchestrator

# Session 478: DaVinci Resolve Integration
from core.agents.resolve_agent import ResolveAgent

# Session 496: Content Writer Agent
from core.agents.content_writer_agent import ContentWriterAgent

# Session 864: Editor Agent for content enhancement
from core.agents.editor_agent import EditorAgent

# Session 496: Podcast Studio Agents
from core.agents.podcast import (
    PodcastCoordinatorAgent,
    DebateAdvocateAgent,
    DebateSkepticAgent,
    ModeratorAgent,
)

# Session 513: Campaign Orchestrator Agent
from core.agents.campaign_orchestrator_agent import CampaignOrchestratorAgent

# Session 558: Markets Agents
# Session 995B: Added GamePredictor, LineMovementAnalyzer, SharpActionDetector
from core.agents.markets import (
    PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector,
    GamePredictor, LineMovementAnalyzer, SharpActionDetector,
)

# Session 1000: BookmakerAgent
from core.agents.bookmaker_agent import BookmakerAgent

# Session 637: Missing agents from root directory
from core.agents.opportunity_pipeline_agent import OpportunityPipelineAgent
from core.agents.content_executor_agent import ContentExecutorAgent
from core.agents.workflow_orchestration_agent import WorkflowOrchestrationAgent
from core.agents.thinking_agent import ThinkingAgent
from core.agents.technical_document_agent import TechnicalDocumentAgent

# Session 663: System Intelligence Agent
from core.agents.system_intelligence_agent import SystemIntelligenceAgent

# Session 1000: DecisionEnforcerAgent
from core.agents.decision_enforcer_agent import DecisionEnforcerAgent

# Session 857: Platform Audit Agent
from core.agents.platform_audit_agent import PlatformAuditAgent

logger = logging.getLogger(__name__)

# Session 488: Semantic routing confidence threshold
# If semantic match confidence is above this, use semantic routing
# Otherwise fall back to keyword matching or default agent
# Note: Cosine similarity scores for embeddings typically range 0.3-0.6 for good matches
SEMANTIC_CONFIDENCE_THRESHOLD = 0.35


class AgentNotFoundError(Exception):
    """Raised when an unknown agent is requested."""


class AgentRouter:
    """
    Simple deterministic router for specialized agents.

    This router:
    1. Receives an agent_name and task
    2. Looks up the agent class in AGENT_MAP
    3. Injects sci-fi and spider context
    4. Executes the agent
    5. Returns the result

    No LLM involved in routing - just dictionary lookup.
    """

    # Map agent names to agent classes
    # Session 268: Complete agent ecosystem
    # Session 280: Added Strategy and Executive agents
    AGENT_MAP: Dict[str, Type[BaseAgent]] = {
        # Creation Agents
        "ImageAgent": ImageAgent,
        "VideoAgent": VideoAgent,
        "AudioAgent": AudioAgent,
        "TalkingCharacterAgent": TalkingCharacterAgent,
        "ThreeDAgent": ThreeDAgent,

        # Editing Agents
        "ImageEditingAgent": ImageEditingAgent,
        "VideoEditingAgent": VideoEditingAgent,

        # Research Agents
        "ResearchAgent": ResearchAgent,

        # Audit Agents (Session 857)
        "PlatformAuditAgent": PlatformAuditAgent,

        # Writing Agents (Session 496)
        "ContentWriterAgent": ContentWriterAgent,

        # Content Enhancement (Session 864)
        "EditorAgent": EditorAgent,

        # Strategy Agents (Session 280)
        "ContentStrategyAgent": ContentStrategyAgent,
        "BrandIdentityAgent": BrandIdentityAgent,
        "SEOOptimizerAgent": SEOOptimizerAgent,
        "SocialMediaAgent": SocialMediaAgent,

        # Executive Agents (Session 280)
        "CTOAgent": CTOAgent,
        "COOAgent": COOAgent,
        "CreativeDirectorAgent": CreativeDirectorAgent,
        "MeetingCoordinatorAgent": MeetingCoordinatorAgent,

        # Analysis Agents (Session 280 Phase 3)
        "TrendAnalysisAgent": TrendAnalysisAgent,
        "OpportunityScoringAgent": OpportunityScoringAgent,

        # Training Agents (Session 280 Phase 3)
        "CharacterTrainingAgent": CharacterTrainingAgent,
        "TrainedCreationAgent": TrainedCreationAgent,

        # Security Agents (Session 280 Phase 3)
        "MemoryIsolationAgent": MemoryIsolationAgent,

        # Prompt Engineering (Session 779/790)
        "PromptEngineeringAgent": PromptEngineeringAgent,

        # Business Research Agents (Session 293 + 637)
        "CompetitorAnalysisAgent": CompetitorAnalysisAgent,
        "CustomerResearchAgent": CustomerResearchAgent,
        "BrandStrategyAgent": BrandStrategyAgent,
        "MarketingStrategyAgent": MarketingStrategyAgent,
        "MarketIntelligenceAgent": MarketIntelligenceAgent,

        # Legal Agents (Session 403)
        "LegalDocDrafterAgent": LegalDocDrafterAgent,

        # Development Agents (Session 436)
        "CodeGeneratorAgent": CodeGeneratorAgent,
        "FullStackDeveloperAgent": FullStackDeveloperAgent,
        "CodeReviewAgent": CodeReviewAgent,
        "DevOpsAgent": DevOpsAgent,

        # Security Agents (Session 461)
        "ContentAuditAgent": ContentAuditAgent,

        # Stock Audit Agents (Session 461 + 637)
        "StockAuditCoordinator": StockAuditCoordinator,
        "StockAnalystAgent": StockAnalystAgent,
        "MarketMovementMonitorAgent": MarketMovementMonitorAgent,
        "InstitutionalWatcherAgent": InstitutionalWatcherAgent,
        "MarketAnomalyDetectorAgent": MarketAnomalyDetectorAgent,
        "BullCaseAgent": BullCaseAgent,
        "BearCaseAgent": BearCaseAgent,
        "SignalScannerAgent": SignalScannerAgent,
        "MarketIntelligenceCoordinator": MarketIntelligenceCoordinator,

        # Blockchain Audit Agents (Session 461 + 637)
        "BlockchainAuditCoordinator": BlockchainAuditCoordinator,
        "SmartContractAuditorAgent": SmartContractAuditorAgent,
        "TransactionMonitorAgent": TransactionMonitorAgent,
        "WhaleWatcherAgent": WhaleWatcherAgent,
        "ExploitDetectorAgent": ExploitDetectorAgent,

        # Narrative Drift Agents (Session 471 + 637)
        "NarrativeDriftCoordinator": NarrativeDriftCoordinator,
        "NarrativeHistorianAgent": NarrativeHistorianAgent,
        "TrendBreakDetectorAgent": TrendBreakDetectorAgent,
        "CulturalImpactAgent": CulturalImpactAgent,

        # Series Workflow Agent (Session 445)
        "AISeriesWorkflowAgent": AISeriesWorkflowAgent,

        # Autonomous Content Studio (Session 466)
        "AutonomousContentStudioCoordinator": AutonomousContentStudioCoordinator,
        "TopicMinerAgent": TopicMinerAgent,
        "ContrarianAgent": ContrarianAgent,
        "PerformanceAnalystAgent": PerformanceAnalystAgent,
        "DistributionAgent": DistributionAgent,
        # Session 784: Voice Critic Agent
        "VoiceCriticAgent": VoiceCriticAgent,
        # Session 743: Content Diversity Orchestrator
        "ContentDiversityOrchestrator": ContentDiversityOrchestrator,

        # Rendering Agents (Session 478)
        "ResolveAgent": ResolveAgent,

        # Podcast Studio Agents (Session 496)
        "PodcastCoordinatorAgent": PodcastCoordinatorAgent,
        "DebateAdvocateAgent": DebateAdvocateAgent,
        "DebateSkepticAgent": DebateSkepticAgent,
        "ModeratorAgent": ModeratorAgent,

        # Orchestration Agents
        "WorkflowAgent": WorkflowAgent,

        # Campaign Orchestrator (Session 513)
        "CampaignOrchestratorAgent": CampaignOrchestratorAgent,

        # Markets Agents (Session 558, 995B)
        "PredictionMarketAnalyst": PredictionMarketAnalyst,
        "SportsOddsAnalyst": SportsOddsAnalyst,
        "ArbitrageDetector": ArbitrageDetector,
        "GamePredictor": GamePredictor,
        "LineMovementAnalyzer": LineMovementAnalyzer,
        "SharpActionDetector": SharpActionDetector,
        "BookmakerAgent": BookmakerAgent,

        # Session 637: Orchestration & Utility Agents
        "OpportunityPipelineAgent": OpportunityPipelineAgent,
        "ContentExecutorAgent": ContentExecutorAgent,
        "WorkflowOrchestrationAgent": WorkflowOrchestrationAgent,
        "ThinkingAgent": ThinkingAgent,
        "TechnicalDocumentAgent": TechnicalDocumentAgent,

        # Session 663: System Intelligence Agent
        "SystemIntelligenceAgent": SystemIntelligenceAgent,

        # Session 1000: Decision Enforcement Agent
        "DecisionEnforcerAgent": DecisionEnforcerAgent,

        # PersonalAssistantAgent removed — deprecated, all PA traffic routes through Rigby
    }

    def __init__(self, user=None):
        """
        Initialize the router.

        Args:
            user: Django User object for agent execution
        """
        self.user = user
        self._scifi_service = None
        self._spider_service = None
        self._semantic_router = None  # Session 488: Semantic routing

    @property
    def scifi_service(self):
        """Lazy-load SciFi integration service."""
        if self._scifi_service is None:
            from core.super_platform.scifi_integration import get_scifi_integration_service
            self._scifi_service = get_scifi_integration_service()
        return self._scifi_service

    @property
    def spider_service(self):
        """Lazy-load Spider intelligence service."""
        if self._spider_service is None:
            from core.services.spider_intelligence import SpiderIntelligenceService
            self._spider_service = SpiderIntelligenceService()
        return self._spider_service

    @property
    def spider_context_builder(self):
        """Session 744: Lazy-load Spider context builder for agent-specific context."""
        if not hasattr(self, '_spider_context_builder') or self._spider_context_builder is None:
            from core.services.spider_context_builder import get_spider_context_builder
            self._spider_context_builder = get_spider_context_builder()
        return self._spider_context_builder

    @property
    def learning_pattern_engine(self):
        """Session 744 Phase 3: Lazy-load Learning pattern engine for memory reuse."""
        if not hasattr(self, '_learning_pattern_engine') or self._learning_pattern_engine is None:
            from core.services.learning_pattern_engine import get_learning_pattern_engine
            self._learning_pattern_engine = get_learning_pattern_engine()
        return self._learning_pattern_engine

    @property
    def advisor_context_builder(self):
        """Session 744 Phase 4: Lazy-load Advisor context builder for legendary advisor wisdom."""
        if not hasattr(self, '_advisor_context_builder') or self._advisor_context_builder is None:
            from core.services.advisor_context_builder import get_advisor_context_builder
            self._advisor_context_builder = get_advisor_context_builder()
        return self._advisor_context_builder

    @property
    def feedback_loop_engine(self):
        """Session 744 Phase 5: Lazy-load Feedback loop engine for performance-based tuning."""
        if not hasattr(self, '_feedback_loop_engine') or self._feedback_loop_engine is None:
            from core.services.feedback_loop_engine import get_feedback_loop_engine
            self._feedback_loop_engine = get_feedback_loop_engine()
        return self._feedback_loop_engine

    @property
    def docs_context_builder(self):
        """Session 798: Lazy-load Docs context builder for documentation awareness."""
        if not hasattr(self, '_docs_context_builder') or self._docs_context_builder is None:
            from core.services.docs_context_builder import get_docs_context_builder
            self._docs_context_builder = get_docs_context_builder()
        return self._docs_context_builder

    @property
    def semantic_router(self):
        """Session 488: Lazy-load Semantic routing service."""
        if self._semantic_router is None:
            from core.services.semantic_routing import get_semantic_router
            self._semantic_router = get_semantic_router()
        return self._semantic_router

    @property
    def knowledge_first_router(self):
        """Session 744: Lazy-load Knowledge-first router for intelligent knowledge lookup."""
        if not hasattr(self, '_knowledge_first_router') or self._knowledge_first_router is None:
            from core.services.knowledge_first_router import get_knowledge_first_router
            self._knowledge_first_router = get_knowledge_first_router()
        return self._knowledge_first_router

    def get_agent_class(self, agent_name: str) -> Optional[Type[BaseAgent]]:
        """
        Session 695: Get the agent class for direct instantiation.

        Used by SKIN layer to instantiate workspace-aware agents directly
        rather than going through the standard route() method.

        Args:
            agent_name: Name of the agent class

        Returns:
            The agent class or None if not found
        """
        return self.AGENT_MAP.get(agent_name)

    def route_by_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        fallback_agent: str = "ThinkingAgent"
    ) -> AgentResult:
        """
        Session 488: Route a query to the best agent using semantic matching.
        Apr 2026: Fallback changed from PersonalAssistantAgent (deprecated) to
        ThinkingAgent. All PA traffic routes through UnifiedPAEntrypoint (Rigby).

        Args:
            query: The user's natural language query
            context: Optional additional context
            fallback_agent: Agent to use if semantic matching fails (default: ThinkingAgent)

        Returns:
            AgentResult from the selected agent
        """
        try:
            # Get semantic routing result
            routing_result = self.semantic_router.route_query(query)

            logger.info(
                f"Semantic routing: {routing_result.agent_name} "
                f"(confidence={routing_result.confidence:.2f}, method={routing_result.method})"
            )

            # Check if agent exists in our map
            if routing_result.agent_name not in self.AGENT_MAP:
                logger.warning(
                    f"Semantic router suggested unknown agent: {routing_result.agent_name}, "
                    f"falling back to {fallback_agent}"
                )
                return self.route(fallback_agent, query, context)

            # Use semantic result if confidence is high enough
            if routing_result.confidence >= SEMANTIC_CONFIDENCE_THRESHOLD:
                logger.info(
                    f"Using semantic routing: {routing_result.agent_name} "
                    f"(confidence {routing_result.confidence:.2f} >= threshold {SEMANTIC_CONFIDENCE_THRESHOLD})"
                )
                return self.route(routing_result.agent_name, query, context)
            else:
                logger.info(
                    f"Semantic confidence too low ({routing_result.confidence:.2f} < {SEMANTIC_CONFIDENCE_THRESHOLD}), "
                    f"using fallback: {fallback_agent}"
                )
                return self.route(fallback_agent, query, context)

        except Exception as e:
            logger.error(f"Semantic routing failed: {e}, using fallback: {fallback_agent}")
            return self.route(fallback_agent, query, context)

    def get_semantic_suggestion(self, query: str) -> Dict[str, Any]:
        """
        Session 488: Get semantic routing suggestion without executing.

        Useful for debugging or showing the user which agent would be selected.

        Args:
            query: The user's natural language query

        Returns:
            Dict with agent suggestion, confidence, and explanation
        """
        try:
            return self.semantic_router.explain_routing(query)
        except Exception as e:
            logger.error(f"Failed to get semantic suggestion: {e}")
            return {
                'query': query,
                'selected_agent': 'ThinkingAgent',
                'confidence': 0.0,
                'method': 'error_fallback',
                'error': str(e)
            }

    def gather_context(
        self,
        agent_name: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Session 769: Gather all context for an agent without executing.

        This allows callers to pre-gather context before starting a timeout,
        so the timeout only applies to agent execution, not context gathering.

        Args:
            agent_name: Name of the agent
            task: The task to perform
            context: Optional additional context

        Returns:
            Dict with 'scifi_context', 'spider_context', 'learning_context', etc.
        """
        context = context or {}

        # Validate agent name
        agent_class = self.AGENT_MAP.get(agent_name)
        if not agent_class:
            return {'error': f'Unknown agent: {agent_name}'}

        # Gather all context types
        scifi_context = self._get_scifi_context(agent_name, task)
        spider_context = self._get_spider_context(task, agent_name=agent_name)
        learning_context = self._get_learning_context(agent_name, task)
        advisor_context = self._get_advisor_context(agent_name, task)
        feedback_context = self._get_feedback_context(agent_name, task)
        knowledge_context = self._get_knowledge_context(agent_name, task)
        workspace_context = self._get_workspace_context(agent_name, task)  # Session 798
        docs_context = self._get_docs_context(agent_name, task)  # Session 798
        user_context = self._get_user_context(agent_name, task)  # Session 858
        risk_context = self._get_risk_aware_context(task)  # Session 949
        platform_tools_context = self._get_platform_tools_context()  # Session 992
        user_docs_context = self._get_user_documents_context(task)  # Session 1035

        # Merge contexts (same logic as in route())
        if learning_context and learning_context.get('has_patterns'):
            spider_context['learning_patterns'] = learning_context
            spider_context['learned_best_practices'] = learning_context.get('best_practices', [])
            spider_context['learning_summary'] = learning_context.get('summary', '')

        if advisor_context and advisor_context.get('has_advice'):
            spider_context['advisor_insights'] = advisor_context
            spider_context['advisor_principles'] = advisor_context.get('key_principles', [])
            spider_context['advisor_frameworks'] = advisor_context.get('decision_frameworks', [])
            spider_context['advisor_summary'] = advisor_context.get('summary', '')
            spider_context['advisor_approach'] = advisor_context.get('recommended_approach', '')

        if feedback_context and feedback_context.get('has_feedback'):
            spider_context['performance_feedback'] = feedback_context
            spider_context['reliability_score'] = feedback_context.get('reliability_score', 0)
            spider_context['performance_rating'] = feedback_context.get('performance_rating', 'unknown')
            spider_context['performance_recommendations'] = feedback_context.get('recommendations', [])
            spider_context['feedback_summary'] = feedback_context.get('summary', '')

        if feedback_context and feedback_context.get('pa_review_feedback'):
            spider_context['pa_content_feedback'] = feedback_context['pa_review_feedback']
            spider_context['pa_review_summary'] = feedback_context.get('pa_review_summary', '')

        if knowledge_context and knowledge_context.get('has_knowledge'):
            spider_context['knowledge_state'] = knowledge_context
            spider_context['knowledge_decision'] = knowledge_context.get('knowledge_decision', 'unknown')
            spider_context['knowledge_coverage'] = knowledge_context.get('knowledge_coverage', 0)
            spider_context['knowledge_freshness'] = knowledge_context.get('knowledge_freshness', 0)
            spider_context['knowledge_summary'] = knowledge_context.get('knowledge_summary', '')
            spider_context['relevant_knowledge'] = knowledge_context.get('relevant_knowledge', [])
            spider_context['use_cached_knowledge'] = knowledge_context.get('use_cached_knowledge', False)

        # Session 798: Merge workspace context into spider context
        if workspace_context and workspace_context.get('has_workspace'):
            spider_context['workspace'] = workspace_context
            spider_context['workspace_name'] = workspace_context.get('workspace_name')
            spider_context['workspace_tech_stack'] = workspace_context.get('tech_stack', {})
            spider_context['workspace_key_files'] = workspace_context.get('key_files', {})
            spider_context['workspace_directories'] = workspace_context.get('directory_purposes', {})

        # Session 798: Merge docs context into spider context
        if docs_context and docs_context.get('has_docs'):
            spider_context['docs'] = docs_context
            spider_context['docs_summary'] = docs_context.get('summary', '')
            spider_context['relevant_docs'] = docs_context.get('relevant_docs', [])
            spider_context['recent_sessions'] = docs_context.get('recent_sessions', [])

        # Session 949: Merge risk-aware RAG context into spider context
        if risk_context and risk_context.get('has_risk_context'):
            spider_context['risk_context'] = risk_context
            spider_context['critical_docs'] = risk_context.get('critical_docs', [])
            spider_context['incident_docs'] = risk_context.get('incident_docs', [])
            spider_context['audit_findings'] = risk_context.get('audit_findings', [])
            spider_context['critical_docs_text'] = risk_context.get('critical_docs_text', '')
            spider_context['incident_docs_text'] = risk_context.get('incident_docs_text', '')
            spider_context['audit_findings_text'] = risk_context.get('audit_findings_text', '')

        # Session 990: Surface agent learned preferences from AgentLearningService
        if user_context and user_context.get('agent_learned_preferences'):
            spider_context['agent_learned_preferences'] = user_context['agent_learned_preferences']

        # Session 1078: Surface UserAgentLearning preferences for prompt injection
        if user_context and user_context.get('learned_user_preferences'):
            spider_context['learned_user_preferences'] = user_context['learned_user_preferences']

        # Session 992: Platform tools directive for router-executed agents
        if platform_tools_context:
            spider_context['platform_tools_directive'] = platform_tools_context

        # Session 1035: Merge user-uploaded documents into spider context
        if user_docs_context and user_docs_context.get('has_user_documents'):
            spider_context['user_documents'] = user_docs_context
            spider_context['user_documents_text'] = user_docs_context.get('user_documents_text', '')
            spider_context['user_documents_sources'] = user_docs_context.get('user_documents_sources', [])

        return {
            'scifi_context': scifi_context,
            'spider_context': spider_context,
            'learning_context': learning_context,
            'advisor_context': advisor_context,
            'feedback_context': feedback_context,
            'knowledge_context': knowledge_context,
            'workspace_context': workspace_context,  # Session 798
            'docs_context': docs_context,  # Session 798
            'user_context': user_context,  # Session 858
            'risk_context': risk_context,  # Session 949
            'user_docs_context': user_docs_context,  # Session 1035
            'gathered': True,
        }

    def route(
        self,
        agent_name: str,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        pre_gathered_context: Optional[Dict[str, Any]] = None,
        create_execution_record: bool = True,
        existing_execution_record: Optional[Any] = None,
        trigger_source: Optional[str] = None,
    ) -> AgentResult:
        """
        Route a task to the appropriate agent.

        This is the main entry point. It:
        1. Validates the agent name
        2. Consults the priority router (Session 1086 PR 3a, behind env gate)
        3. Instantiates the agent
        4. Gathers sci-fi and spider context (unless pre_gathered_context provided)
        5. Executes the agent
        6. Returns the result

        Args:
            agent_name: Name of the agent to route to (e.g., "ImageAgent")
            task: The task to perform in natural language
            context: Optional additional context (count, style, reference_id, etc.)
            pre_gathered_context: Session 769: Pre-gathered context to skip context gathering
            create_execution_record: Session 1084 — when True (default), the
                router creates its own AgentExecution row via
                ``_create_execution_record()``. When False, the caller
                is expected to pass ``existing_execution_record`` — used
                to prevent duplicate row creation when the caller (e.g.
                ``tasks_agents._impl_execute_agent_task``) already has
                its own execution row.
            existing_execution_record: Session 1084 — an AgentExecution
                instance created by the caller. Used by the router for
                status updates / completion tracking in place of a newly
                created row. Only honored when
                ``create_execution_record=False``.
            trigger_source: Session 1086 PR 3a — identifies where this
                dispatch came from. The only value with behavioral meaning
                right now is ``"user_chat"``, which exempts the dispatch
                from throttling unconditionally (user-triggered work is
                never throttled). Other values (``"autonomous_beat"``,
                ``"direct_dispatch"``, ``None``) go through the full
                matching pipeline. Back-compat: default ``None`` means
                existing callers work unchanged.

        Returns:
            AgentResult from the agent execution

        Raises:
            AgentNotFoundError: If agent_name is not in AGENT_MAP
        """
        from core.services.context_tracing import ContextTracer, auto_repair_context

        # Session 875: Initialize tracer and log context at router stage
        tracer = ContextTracer(source=f"AgentRouter.route:{agent_name}")
        tracer.log_router(
            context=context,
            agent_name=agent_name,
            task=task[:100] if task else ""
        )

        # Session 875: Ensure context is a dict (defensive fix for list being passed)
        if not isinstance(context, dict):
            logger.warning(f"AgentRouter.route received non-dict context (type={type(context).__name__}), using empty dict")
            context = auto_repair_context(context)
        else:
            context = context or {}

        # Validate agent name
        agent_class = self.AGENT_MAP.get(agent_name)
        if not agent_class:
            # Session 1038: Fall back to DynamicPersonaAgent for DB-only personas
            from core.agents.dynamic_persona_agent import DynamicPersonaAgent
            try:
                from core.models_unified_system import Agent as AgentModel
                if AgentModel.objects.filter(name=agent_name, is_active=True).exists():
                    logger.info(f"[routing] '{agent_name}' not in AGENT_MAP, using DynamicPersonaAgent")
                    agent_class = DynamicPersonaAgent
                else:
                    available = ", ".join(self.AGENT_MAP.keys())
                    raise AgentNotFoundError(
                        f"Unknown agent: '{agent_name}'. Available agents: {available}"
                    )
            except AgentNotFoundError:
                raise
            except Exception as e:
                logger.warning(f"[routing] DynamicPersonaAgent fallback failed for '{agent_name}': {e}")
                available = ", ".join(self.AGENT_MAP.keys())
                raise AgentNotFoundError(
                    f"Unknown agent: '{agent_name}'. Available agents: {available}"
                )

        # Session 1031: Reroute specialist tasks away from non-specialist agents.
        # E.g. "competitor audit" should go to CompetitorAnalysisAgent, not WorkflowAgent.
        # Session 1032: Broadened competitor patterns — "Step 3 competitor audit" variants
        # were slipping through because LLM generates many phrasings.
        import re as _re
        _ROUTING_OVERRIDES = [
            (_re.compile(r'competitor\s*(audit|analysis|landscape|benchmark|coverage)', _re.I), 'CompetitorAnalysisAgent'),
            (_re.compile(r'Step\s+\d+\s+competitor', _re.I), 'CompetitorAnalysisAgent'),
            (_re.compile(r'CompetitorAnalysisAgent\s+output', _re.I), 'CompetitorAnalysisAgent'),
            (_re.compile(r'trend\s+(analysis|report|summary)', _re.I), 'TrendAnalysisAgent'),
            (_re.compile(r'customer\s+(research|interview|persona)', _re.I), 'CustomerResearchAgent'),
            (_re.compile(r'brand\s+(strategy|positioning|audit)', _re.I), 'BrandStrategyAgent'),
            (_re.compile(r'market(ing)?\s+(strategy|plan|recommendation)', _re.I), 'MarketingStrategyAgent'),
        ]
        _NON_SPECIALIST = frozenset({
            'WorkflowAgent', 'VideoAgent', 'CodeGeneratorAgent', 'DevOpsAgent',
            'FullStackDeveloperAgent', 'CodeReviewAgent', 'ContentDistributionAgent',
            'COOAgent', 'CTOAgent', 'AudioAgent',
        })
        for pattern, correct_agent in _ROUTING_OVERRIDES:
            if pattern.search(task or ''):
                if agent_name != correct_agent and agent_name in _NON_SPECIALIST:
                    correct_class = self.AGENT_MAP.get(correct_agent)
                    if correct_class:
                        logger.info(
                            f"[routing-override] Rerouting '{(task or '')[:60]}' "
                            f"from {agent_name} -> {correct_agent}"
                        )
                        agent_name = correct_agent
                        agent_class = correct_class
                    break

        # Session 1032: Task text intercept — replace known unbounded tasks
        # with bounded versions. The old text is embedded in 73+ AgentMemory
        # records and keeps resurfacing from the system's learning infrastructure.
        _BOUNDED_TREND_TASK = (
            'Summarize the top 3 market or technology trends from the last '
            '24 hours of spider data. Keep the report under 500 words. '
            'Do NOT attempt comprehensive analysis — focus on the 3 '
            'strongest signals only.'
        )
        _TASK_TEXT_OVERRIDES = {
            'TrendAnalysisAgent': [
                # Session 1032: Original unbounded task text
                (_re.compile(r'^Analyze current market and content trends', _re.I), _BOUNDED_TREND_TASK),
                # Session 1035: Broader patterns — LLM generates many phrasings
                (_re.compile(r'^Analyze\s+(all|latest|recent|current|comprehensive)', _re.I), _BOUNDED_TREND_TASK),
                (_re.compile(r'^(Comprehensive|Full|Complete|Detailed|In-depth)\s+(trend|market|industry)', _re.I), _BOUNDED_TREND_TASK),
                (_re.compile(r'trend.{0,20}(report|analysis|summary|overview|landscape)', _re.I), _BOUNDED_TREND_TASK),
            ],
        }
        if agent_name in _TASK_TEXT_OVERRIDES:
            for pattern, replacement in _TASK_TEXT_OVERRIDES[agent_name]:
                if pattern.search(task or ''):
                    logger.info(
                        f"[task-text-override] Replacing unbounded task for "
                        f"{agent_name}: '{(task or '')[:60]}' -> bounded version"
                    )
                    task = replacement
                    break

        logger.info(f"Routing to {agent_name}: {task[:50]}...")

        # Session 1032: Hard-block agents that can't do useful work on Railway.
        # Session 1080: Centralized in AgentControlEntry (DB-backed, PA-manageable)
        from core.models_unified_system import AgentControlEntry
        if AgentControlEntry.is_blocked(agent_name):
            logger.warning(
                f"[route] BLOCKED: {agent_name} disabled on Railway "
                f"(task='{(task or '')[:50]}...')"
            )
            from core.agents.base_agent import AgentResult
            return AgentResult(
                success=False,
                message=f'{agent_name} disabled on Railway (Session 1032)',
            )

        # Session 1086 PR 3a: Priority-aware routing (observer-only, gated).
        # Behind ``PRIORITY_ROUTER_ENABLED`` env var (default FALSE). When the
        # gate is OFF this is a no-op and returns None. When ON, consults the
        # active priority set and returns a PriorityDecision. PR 3a logs the
        # decision but does NOT throttle — PR 3b wires the semaphore.
        #
        # Fail-open everywhere: the entire priority path is wrapped in
        # try/except inside check_priority() so a bug here can never break
        # the dispatch path. See initiative 2dcb79d7 and the design review
        # in conversation pa-ba134ae68c21 for the locked contract.
        from core.services.priority.enforce import check_priority, log_decision
        priority_decision = check_priority(
            agent_name=agent_name,
            task=task,
            context=context,
            trigger_source=trigger_source,
        )
        log_decision(priority_decision, agent_name)

        # Instantiate the agent
        # Session 1038: DynamicPersonaAgent needs persona_name kwarg
        if agent_class.__name__ == 'DynamicPersonaAgent':
            agent = agent_class(persona_name=agent_name, user=self.user)
        else:
            agent = agent_class(user=self.user)

        # Inject workspace_id into agent so deliverables get assigned correctly.
        # Priority: explicit context > initiative workspace > active workspace fallback.
        # Session 1103c: both fallbacks used to swallow exceptions silently,
        # which is one of the paths that let orphan deliverables slip through
        # — if the Initiative lookup or the active workspace query raised,
        # the agent ran unscoped and whatever it produced got saved as an
        # orphan. Now loud on every swallow.
        workspace_id = context.get('workspace_id') if context else None
        if not workspace_id and context and context.get('initiative_id'):
            try:
                from core.models_document_registry import Initiative
                init = Initiative.objects.filter(id=context['initiative_id']).first()
                if init and init.target_workspace_id:
                    workspace_id = str(init.target_workspace_id)
            except Exception as e:
                logger.warning(
                    "agent_router: initiative→workspace lookup failed for "
                    "initiative_id=%s (%s: %s) — falling back to global "
                    "active workspace",
                    context.get('initiative_id'), type(e).__name__, e,
                )
        if not workspace_id:
            try:
                from core.models_skin_layer import ProjectWorkspace
                active_ws = ProjectWorkspace.objects.filter(is_active=True).first()
                if active_ws:
                    workspace_id = str(active_ws.id)
                else:
                    logger.error(
                        "agent_router: no is_active ProjectWorkspace exists "
                        "— agent %s will run UNSCOPED and any deliverables "
                        "it produces will be orphaned",
                        agent_name,
                    )
            except Exception as e:
                logger.error(
                    "agent_router: active workspace lookup failed "
                    "(%s: %s) — agent %s will run UNSCOPED and any "
                    "deliverables it produces will be orphaned",
                    type(e).__name__, e, agent_name,
                )
        if workspace_id:
            agent._workspace_id = workspace_id
            if context is None:
                context = {}
            context['workspace_id'] = workspace_id

        # Session 769: Use pre-gathered context if provided (for timeout isolation)
        if pre_gathered_context and pre_gathered_context.get('gathered'):
            scifi_context = pre_gathered_context.get('scifi_context', {})
            spider_context = pre_gathered_context.get('spider_context', {})
            learning_context = pre_gathered_context.get('learning_context', {})
            advisor_context = pre_gathered_context.get('advisor_context', {})
            feedback_context = pre_gathered_context.get('feedback_context', {})
            knowledge_context = pre_gathered_context.get('knowledge_context', {})
            workspace_context = pre_gathered_context.get('workspace_context', {})  # Session 798
            docs_context = pre_gathered_context.get('docs_context', {})  # Session 798
            user_context = pre_gathered_context.get('user_context', {})  # Session 858
            risk_context = pre_gathered_context.get('risk_context', {})  # Session 949
            user_docs_context = pre_gathered_context.get('user_docs_context', {})  # Session 1035
            logger.info(f"Using pre-gathered context for {agent_name} (context gathering done outside timeout)")
        else:
            # Session 1069: Parallel context gathering with per-call timeout.
            # Previously sequential (11 calls × up to 30s each = 5+ min risk).
            # Now parallel with 10s timeout per call — total max ~10s.
            def _safe_ctx(fn):
                """Wrap context call with DB connection cleanup for thread safety."""
                try:
                    from django.db import close_old_connections
                    close_old_connections()
                    return fn()
                except Exception as e:
                    logger.warning(f"[CONTEXT] {fn.__name__ if hasattr(fn, '__name__') else 'unknown'} failed: {e}")
                    return {}
                finally:
                    from django.db import close_old_connections
                    close_old_connections()

            _ctx_fns = {
                'scifi_context': lambda: self._get_scifi_context(agent_name, task),
                'spider_context': lambda: self._get_spider_context(task, agent_name=agent_name),
                'learning_context': lambda: self._get_learning_context(agent_name, task),
                'advisor_context': lambda: self._get_advisor_context(agent_name, task),
                'feedback_context': lambda: self._get_feedback_context(agent_name, task),
                'knowledge_context': lambda: self._get_knowledge_context(agent_name, task),
                'workspace_context': lambda: self._get_workspace_context(agent_name, task),
                'docs_context': lambda: self._get_docs_context(agent_name, task),
                'user_context': lambda: self._get_user_context(agent_name, task),
                'risk_context': lambda: self._get_risk_aware_context(task),
                'user_docs_context': lambda: self._get_user_documents_context(task),
            }

            _gathered = {}
            with ThreadPoolExecutor(max_workers=11) as _pool:
                _futures = {key: _pool.submit(_safe_ctx, fn) for key, fn in _ctx_fns.items()}
                for key, future in _futures.items():
                    try:
                        _gathered[key] = future.result(timeout=10)
                    except FuturesTimeoutError:
                        logger.warning(f"[CONTEXT] {key} timed out (10s)")
                        _gathered[key] = {}
                    except Exception as e:
                        logger.warning(f"[CONTEXT] {key} failed: {type(e).__name__}: {e}")
                        _gathered[key] = {}

            scifi_context = _gathered['scifi_context']
            spider_context = _gathered['spider_context']
            learning_context = _gathered['learning_context']
            advisor_context = _gathered['advisor_context']
            feedback_context = _gathered['feedback_context']
            knowledge_context = _gathered['knowledge_context']
            workspace_context = _gathered['workspace_context']
            docs_context = _gathered['docs_context']
            user_context = _gathered['user_context']
            risk_context = _gathered['risk_context']
            user_docs_context = _gathered['user_docs_context']

        # Session 522: Special handling for ContentWriterAgent - use SmartTrendingService
        # with dynamic year references and DuckDuckGo fallback for fresh 2025 data
        if agent_name == 'ContentWriterAgent' and context.get('content_type') != 'internal_document':
            from datetime import datetime
            try:
                from core.services.smart_trending_service import SmartTrendingService
                trending_service = SmartTrendingService()
                trending_data = trending_service.get_trending_for_query(
                    query=task,
                    hours=72,
                    article_limit=10,
                    use_cache=True
                )

                if trending_data:
                    now = datetime.now()
                    today = now.strftime('%B %d, %Y')
                    month_year = now.strftime('%B %Y')
                    year = now.year
                    old_years = f"{year-2} or {year-1}"

                    research_parts = [
                        f"## Real-Time Research Data (as of {today})",
                        f"**CRITICAL: This content is for {year}. DO NOT reference {old_years}. Use ONLY the data provided below.**\n"
                    ]

                    trends = trending_data.get('trends') or trending_data.get('trending_keywords', [])
                    if trends:
                        research_parts.append(f"### Current Trending Topics ({month_year}):")
                        for kw in trends[:10]:
                            research_parts.append(f"- {kw}")

                    articles = trending_data.get('articles', [])
                    if articles:
                        research_parts.append(f"\n### Latest Articles ({len(articles)} found) - ALL FROM {year}:")
                        research_parts.append("**CITE THESE SOURCES in your content!**\n")
                        for i, article in enumerate(articles[:8], 1):
                            title = article.get('title', 'Unknown')
                            source = article.get('source', 'Unknown')
                            url = article.get('url', article.get('link', ''))
                            pub_date = article.get('published', '')
                            summary = article.get('summary', article.get('content', ''))[:200]
                            date_str = f" - Published: {pub_date[:10]}" if pub_date else ""

                            # Session 523: Include URL for source citation
                            research_parts.append(f"\n**{i}. {title}**")
                            research_parts.append(f"   Source: {source}{date_str}")
                            if url and not url.startswith('internal'):
                                research_parts.append(f"   URL: {url}")
                            if summary:
                                research_parts.append(f"   Summary: {summary}...")

                    if trending_data.get('categories'):
                        research_parts.append(f"\n### Relevant Categories: {', '.join(trending_data['categories'])}")

                    # Inject research into CONTEXT (not spider_context) for ContentWriterAgent
                    # ContentWriterAgent uses context.get('research', '') at line 173
                    research_text = "\n".join(research_parts)
                    if not context.get('research'):
                        context['research'] = research_text
                    else:
                        # Prepend our fresh data to any existing research
                        context['research'] = research_text + "\n\n" + context['research']
                    context['year'] = year
                    context['month_year'] = month_year
                    logger.info(f"📊 Session 522: Built {len(research_text)} chars of research for ContentWriterAgent")

            except Exception as e:
                logger.warning(f"⚠️ Session 522: SmartTrendingService failed for ContentWriterAgent: {e}")

        # Session 744 Phase 3: Merge learning context into spider context
        # This allows agents to receive learning patterns through the existing spider_context parameter
        if learning_context and learning_context.get('has_patterns'):
            spider_context['learning_patterns'] = learning_context
            spider_context['learned_best_practices'] = learning_context.get('best_practices', [])
            spider_context['learning_summary'] = learning_context.get('summary', '')
            logger.debug(
                f"📚 [Session 744] Injected learning patterns into spider_context for {agent_name}"
            )

        # Session 744 Phase 4: Merge advisor context into spider context
        # This allows agents to receive legendary advisor wisdom through the existing spider_context parameter
        if advisor_context and advisor_context.get('has_advice'):
            spider_context['advisor_insights'] = advisor_context
            spider_context['advisor_principles'] = advisor_context.get('key_principles', [])
            spider_context['advisor_frameworks'] = advisor_context.get('decision_frameworks', [])
            spider_context['advisor_summary'] = advisor_context.get('summary', '')
            spider_context['advisor_approach'] = advisor_context.get('recommended_approach', '')
            logger.debug(
                f"🧙 [Session 744] Injected advisor wisdom into spider_context for {agent_name}"
            )

        # Session 744 Phase 5: Merge feedback context into spider context
        # This gives agents awareness of their historical performance for self-improvement
        if feedback_context and feedback_context.get('has_feedback'):
            spider_context['performance_feedback'] = feedback_context
            spider_context['reliability_score'] = feedback_context.get('reliability_score', 0)
            spider_context['performance_rating'] = feedback_context.get('performance_rating', 'unknown')
            spider_context['performance_recommendations'] = feedback_context.get('recommendations', [])
            spider_context['feedback_summary'] = feedback_context.get('summary', '')
            logger.debug(
                f"📊 [Session 744] Injected performance feedback into spider_context for {agent_name}"
            )

        # Session 744: Merge knowledge-first routing context into spider context
        # This gives agents awareness of what knowledge already exists before making new queries
        if knowledge_context and knowledge_context.get('has_knowledge'):
            spider_context['knowledge_state'] = knowledge_context
            spider_context['knowledge_decision'] = knowledge_context.get('knowledge_decision', 'unknown')
            spider_context['knowledge_coverage'] = knowledge_context.get('knowledge_coverage', 0)
            spider_context['knowledge_freshness'] = knowledge_context.get('knowledge_freshness', 0)
            spider_context['knowledge_summary'] = knowledge_context.get('knowledge_summary', '')
            spider_context['relevant_knowledge'] = knowledge_context.get('relevant_knowledge', [])
            spider_context['use_cached_knowledge'] = knowledge_context.get('use_cached_knowledge', False)
            logger.debug(
                f"🧠 [Session 744] Injected knowledge context into spider_context for {agent_name}: "
                f"decision={knowledge_context.get('knowledge_decision')}"
            )

        # Session 798: Merge workspace context into spider context
        # This gives agents awareness of the project structure for file operations
        if workspace_context and workspace_context.get('has_workspace'):
            spider_context['workspace'] = workspace_context
            spider_context['workspace_name'] = workspace_context.get('workspace_name')
            spider_context['workspace_tech_stack'] = workspace_context.get('tech_stack', {})
            spider_context['workspace_key_files'] = workspace_context.get('key_files', {})
            spider_context['workspace_directories'] = workspace_context.get('directory_purposes', {})
            logger.debug(
                f"📁 [Session 798] Injected workspace context into spider_context for {agent_name}: "
                f"workspace={workspace_context.get('workspace_name')}"
            )

        # Session 798: Merge docs context into spider context
        # This gives agents awareness of system documentation and recent sessions
        if docs_context and docs_context.get('has_docs'):
            spider_context['docs'] = docs_context
            spider_context['docs_summary'] = docs_context.get('summary', '')
            spider_context['relevant_docs'] = docs_context.get('relevant_docs', [])
            spider_context['recent_sessions'] = docs_context.get('recent_sessions', [])
            logger.debug(
                f"📚 [Session 798] Injected docs context into spider_context for {agent_name}: "
                f"{len(docs_context.get('relevant_docs', []))} docs"
            )

        # Session 949: Merge risk-aware RAG context into spider context
        # This ensures critical docs, incidents, and audit findings are always available
        if risk_context and risk_context.get('has_risk_context'):
            spider_context['risk_context'] = risk_context
            spider_context['critical_docs'] = risk_context.get('critical_docs', [])
            spider_context['incident_docs'] = risk_context.get('incident_docs', [])
            spider_context['audit_findings'] = risk_context.get('audit_findings', [])
            spider_context['critical_docs_text'] = risk_context.get('critical_docs_text', '')
            spider_context['incident_docs_text'] = risk_context.get('incident_docs_text', '')
            spider_context['audit_findings_text'] = risk_context.get('audit_findings_text', '')
            logger.debug(
                f"🚨 [Session 949] Injected risk-aware context for {agent_name}: "
                f"critical={len(risk_context.get('critical_docs', []))}, "
                f"incidents={len(risk_context.get('incident_docs', []))}, "
                f"findings={len(risk_context.get('audit_findings', []))}"
            )

        # Session 858: Inject user context into context dict
        # This makes user data available to ALL agents without changing execute() signature
        if user_context and user_context.get('has_user_context'):
            context['user'] = user_context
            context['user_name'] = user_context.get('name', '')
            context['user_goals'] = user_context.get('goals', [])
            context['user_skills'] = user_context.get('skills', [])
            context['user_communication_style'] = user_context.get('communication_style', 'professional')
            logger.debug(
                f"👤 [Session 858] Injected user context for {agent_name}: "
                f"user={user_context.get('username', 'Unknown')}, "
                f"style={user_context.get('communication_style', 'professional')}"
            )

        # Session 1035: Merge user-uploaded documents into spider context
        if user_docs_context and user_docs_context.get('has_user_documents'):
            spider_context['user_documents'] = user_docs_context
            spider_context['user_documents_text'] = user_docs_context.get('user_documents_text', '')
            spider_context['user_documents_sources'] = user_docs_context.get('user_documents_sources', [])

        # Execute the agent with tracking
        start_time = timezone.now()
        execution_record = None

        # Session 758: Log context injection summary for observability
        context_summary = {
            'spider_data': spider_context.get('has_data', False),
            'spider_trends': len(spider_context.get('relevant_trends', [])),
            'spider_discussions': len(spider_context.get('discussions', [])),
            'learning_patterns': bool(spider_context.get('learning_patterns')),
            'advisor_insights': bool(spider_context.get('advisor_insights')),
            'performance_feedback': bool(spider_context.get('performance_feedback')),
            'knowledge_state': bool(spider_context.get('knowledge_state')),
            'workspace': bool(spider_context.get('workspace')),  # Session 798
            'docs': bool(spider_context.get('docs')),  # Session 798
            'risk_context': bool(spider_context.get('risk_context')),  # Session 949
            'scifi_context': bool(scifi_context),
            'user_context': bool(context.get('user')),  # Session 858
            'user_documents': bool(spider_context.get('user_documents')),  # Session 1035
        }
        logger.info(
            f"🔌 [Session 758] Context injection for {agent_name}: "
            f"spider={context_summary['spider_data']} ({context_summary['spider_trends']} trends), "
            f"learning={context_summary['learning_patterns']}, "
            f"advisor={context_summary['advisor_insights']}, "
            f"feedback={context_summary['performance_feedback']}, "
            f"workspace={context_summary['workspace']}, "
            f"docs={context_summary['docs']}, "
            f"risk={context_summary['risk_context']}, "  # Session 949
            f"user={context_summary['user_context']}, "  # Session 858
            f"user_docs={context_summary['user_documents']}, "  # Session 1035
            f"scifi={context_summary['scifi_context']}"
        )

        try:
            # Create execution record with context tracking
            # Session 841: Pass experiment_id for proper error rate scoping
            # Session 1084: Honor create_execution_record / existing_execution_record
            # kwargs to prevent duplicate-row creation when tasks_agents
            # already wrote one. See PR #1887.
            experiment_id = context.get('experiment_id')
            if create_execution_record:
                execution_record = self._create_execution_record(
                    agent_name, task, context_summary=context_summary, experiment_id=experiment_id
                )
                if execution_record is not None:
                    logger.info(
                        f"[execution_record_created_by=router] agent={agent_name} "
                        f"execution_id={getattr(execution_record, 'id', None)}"
                    )
            else:
                execution_record = existing_execution_record
                if execution_record is not None:
                    logger.info(
                        f"[execution_record_created_by=caller] agent={agent_name} "
                        f"execution_id={getattr(execution_record, 'id', None)}"
                    )
                else:
                    logger.warning(
                        f"[execution_record] route() called with "
                        f"create_execution_record=False but no "
                        f"existing_execution_record for agent={agent_name}. "
                        f"Downstream completion tracking will be a no-op."
                    )

            # Session 908: Use execute_with_workspace when workspace is available
            # This ensures all agent outputs are written to the SKIN layer workspace
            has_workspace = workspace_context and workspace_context.get('has_workspace')
            write_to_workspace = context.get('write_to_workspace', True)  # Default to True

            # Session 1086 PR 3b: Wrap the execute() call in the priority
            # semaphore. acquire_for_decision is a no-op when
            # PRIORITY_THROTTLE_ENABLED is off OR when priority_decision is
            # None (gate off) OR when trigger_source was 'user_chat'
            # (user work is never throttled). See core/services/priority/
            # semaphore.py for the acquire semantics.
            from core.services.priority.semaphore import acquire_for_decision
            with acquire_for_decision(priority_decision, agent_name):
                if has_workspace and write_to_workspace and hasattr(agent, 'execute_with_workspace'):
                    # Execute with workspace - outputs will be written to SKIN layer
                    logger.info(f"📁 [Session 908] Using execute_with_workspace for {agent_name}")
                    # Inject scifi_context and spider_context into context for execute_with_workspace
                    enriched_context = {
                        **context,
                        'scifi_context': scifi_context,
                        'spider_context': spider_context,
                    }
                    result = agent.execute_with_workspace(
                        task=task,
                        context=enriched_context,
                        user=self.user,
                        write_to_workspace=True,
                        base_path=context.get('workspace_base_path', '')
                    )
                else:
                    # Standard execution without workspace write
                    if not has_workspace:
                        logger.debug(f"[Session 908] No workspace for {agent_name}, using standard execute")
                    # Store execution context on agent for search strategy enhancement
                    agent._execution_context = context
                    result = agent.execute(
                        task=task,
                        context=context,
                        scifi_context=scifi_context,
                        spider_context=spider_context
                    )

            # Session 735: Inject accumulated cost/tokens from agent into result
            # This captures cost even if agent doesn't use _make_result() helper
            if hasattr(agent, '_accumulated_cost') and hasattr(agent, '_accumulated_tokens'):
                if result.cost == 0.0 and agent._accumulated_cost > 0:
                    result.cost = agent._accumulated_cost
                if result.tokens_used == 0 and agent._accumulated_tokens > 0:
                    result.tokens_used = agent._accumulated_tokens

            # Track execution result
            # Session 641: Use result.message (not result.output which doesn't exist on AgentResult)
            # Session 744: Pass tokens_used and cost to execution record
            # Session 757: Save FULL result data (not just preview) so blog content is accessible
            # Session 759: Include result.error for failed executions
            # Session 766: Pass applied_pattern_ids for tracking
            applied_pattern_ids = learning_context.get('applied_pattern_ids', []) if learning_context else []
            self._complete_execution(
                execution_record,
                agent_name,
                success=result.success,
                execution_time_ms=result.execution_time_ms,
                output_data={
                    'result_preview': str(result.message)[:500] if result.message else None,
                    'data': result.data,  # Full result data including generated content
                    'message': result.message,
                    'error': result.error if not result.success else None,  # Session 759: Include error
                    'tool_calls': result.tool_calls if result.tool_calls else [],  # Session 769: Include tool calls
                },
                error_message=result.error if not result.success else None,  # Session 759: Pass to record
                tokens_used=result.tokens_used,
                cost=result.cost,
                applied_pattern_ids=applied_pattern_ids  # Session 766: Track pattern application
            )

            # Session 765: Set execution_id on result for orchestration linking
            if execution_record and hasattr(execution_record, 'id'):
                result.execution_id = str(execution_record.id)

            logger.info(
                f"{agent_name} completed: success={result.success}, "
                f"time={result.execution_time_ms}ms, execution_id={result.execution_id}"
            )

            # Session 858: Record success for user learning feedback loop
            if result.success:
                self._record_user_learning(agent_name, task, result, context.get('user', {}))

            # Session 990: Record interaction for AgentLearningService (Redis-based preferences)
            self._record_agent_learning_interaction(agent_name, task, result, context)

            return result

        except Exception as e:
            # Track failed execution
            execution_time_ms = int((timezone.now() - start_time).total_seconds() * 1000)
            self._complete_execution(
                execution_record,
                agent_name,
                success=False,
                execution_time_ms=execution_time_ms,
                error_message=str(e)
            )

            logger.error(f"Agent execution error ({agent_name}): {e}", exc_info=True)
            return AgentResult(
                success=False,
                error=str(e),
                agent_name=agent_name
            )

    def _get_scifi_context(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Get sci-fi context for an agent.

        This includes:
        - Mood (affects style and confidence)
        - Evolution (level, XP, title)
        - Relationships (allies, rivals)
        - Memory (past successes, learned patterns)
        - Dreams (recent creative insights)

        Args:
            agent_name: Agent to get context for
            task: Task for context relevance

        Returns:
            Dict with sci-fi context
        """
        try:
            context = self.scifi_service.get_scifi_context(
                agent_name=agent_name,
                task=task,
                user=self.user
            )
            return context.to_dict() if hasattr(context, 'to_dict') else {}
        except Exception as e:
            logger.warning(f"Failed to get sci-fi context: {e}")
            return {}

    def _get_spider_context(self, task: str, agent_name: str = None) -> Dict[str, Any]:
        """
        Session 744: Get spider intelligence context for a task using SpiderContextBuilder.

        This method now uses the SpiderContextBuilder to provide agent-specific
        spider context. The builder maps agent types to relevant spider categories
        and provides richer, more targeted data.

        This includes:
        - Relevant trends (agent-specific categories)
        - Market data (for financial/prediction agents)
        - Related discussions
        - Creative trends (for creative agents)
        - Job market data (for job/career agents)
        - Freshness indicators

        Args:
            task: Task to get context for
            agent_name: Name of the agent to get context for (Session 744)

        Returns:
            Dict with spider context
        """
        try:
            # Session 744: Use SpiderContextBuilder for agent-specific context
            if agent_name:
                context = self.spider_context_builder.build_context_for_agent(
                    agent_name=agent_name,
                    task=task,
                    hours=48,
                    max_trends=10,
                    max_discussions=5
                )
                logger.debug(f"🕷️ [Session 744] Spider context built for {agent_name}: has_data={context.get('has_data')}")
                return context

            # Fallback to legacy method if no agent_name provided
            context = self.spider_service.get_insights_for_prompt(task)

            # Also get creative trends for image/design tasks
            if any(word in task.lower() for word in ['logo', 'image', 'design', 'banner', 'illustration']):
                creative = self.spider_service.get_creative_trends(hours=48)
                context['creative_trends'] = creative

            # Session 558: Get market data for betting/prediction tasks
            if any(word in task.lower() for word in ['betting', 'odds', 'sports', 'prediction', 'kalshi', 'market', 'wager']):
                context['market_analysis'] = True

            return context
        except Exception as e:
            logger.warning(f"Failed to get spider context: {e}")
            return {}

    def _get_learning_context(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Session 744 Phase 3: Get learning patterns for an agent.

        This mines past successful executions and knowledge transfers
        to provide agents with awareness of their proven strategies.

        Args:
            agent_name: Name of the agent
            task: Current task description

        Returns:
            Dict with learning patterns and recommendations
        """
        try:
            patterns = self.learning_pattern_engine.get_patterns_for_agent(
                agent_name=agent_name,
                task=task,
                days_back=30,
                max_patterns=5
            )
            if patterns.get('has_patterns'):
                logger.debug(
                    f"📚 [Session 744] Learning patterns for {agent_name}: "
                    f"summary='{patterns.get('summary', '')[:50]}...'"
                )
            return patterns
        except Exception as e:
            logger.warning(f"Failed to get learning context: {e}")
            return {}

    def _get_advisor_context(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Session 744 Phase 4: Get advisor wisdom for an agent.

        This consults legendary advisors (Warren Buffett, Elon Musk, etc.)
        and injects their decision frameworks and principles into agent context.

        Args:
            agent_name: Name of the agent
            task: Current task description

        Returns:
            Dict with advisor insights and recommendations
        """
        try:
            advisor_context = self.advisor_context_builder.build_context_for_agent(
                agent_name=agent_name,
                task=task,
                max_advisors=3
            )
            if advisor_context.get('has_advice'):
                logger.debug(
                    f"🧙 [Session 744] Advisor context for {agent_name}: "
                    f"summary='{advisor_context.get('summary', '')[:50]}...'"
                )
            return advisor_context
        except Exception as e:
            logger.warning(f"Failed to get advisor context: {e}")
            return {}

    def _get_feedback_context(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Session 744 Phase 5: Get performance feedback for an agent.

        This provides agents with awareness of their historical performance,
        enabling self-improvement and better decision-making.

        Args:
            agent_name: Name of the agent
            task: Current task description

        Returns:
            Dict with performance metrics and recommendations
        """
        try:
            feedback_context = self.feedback_loop_engine.get_feedback_for_agent(
                agent_name=agent_name,
                task=task,
                days_back=30
            )
            if feedback_context.get('has_feedback'):
                logger.debug(
                    f"📊 [Session 744] Feedback for {agent_name}: "
                    f"reliability={feedback_context.get('reliability_score', 0):.2f}"
                )
            return feedback_context
        except Exception as e:
            logger.warning(f"Failed to get feedback context: {e}")
            return {}

    def _get_knowledge_context(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Session 744: Get knowledge-first routing context for a task.

        This checks existing knowledge sources (embeddings, learnings, spider data)
        BEFORE making external queries. The result includes:
        - Whether cached knowledge is sufficient
        - Relevant knowledge snippets
        - Routing recommendations
        - Freshness scores

        Args:
            agent_name: Name of the agent
            task: Current task description

        Returns:
            Dict with knowledge state and routing recommendation
        """
        try:
            knowledge_result = self.knowledge_first_router.route_with_knowledge(
                task=task,
                agent_name=agent_name
            )

            knowledge_context = {
                'has_knowledge': len(knowledge_result.cached_knowledge) > 0,
                'knowledge_decision': knowledge_result.decision.value,
                'knowledge_confidence': knowledge_result.confidence,
                'knowledge_reasoning': knowledge_result.reasoning,
                'knowledge_coverage': knowledge_result.knowledge_coverage,
                'knowledge_freshness': knowledge_result.freshness_avg,
                'knowledge_summary': knowledge_result.knowledge_summary,
                'use_cached_knowledge': knowledge_result.use_cached,
                'needs_spider_refresh': knowledge_result.refresh_spiders,
                'spider_categories_to_refresh': knowledge_result.spider_categories_to_refresh,
            }

            if knowledge_result.cached_knowledge:
                # Include top knowledge snippets for agent context
                knowledge_context['relevant_knowledge'] = [
                    {
                        'source': k.source,
                        'content': k.content[:300],
                        'relevance': round(k.relevance_score, 3),
                        'freshness': round(k.freshness_score, 3)
                    }
                    for k in knowledge_result.cached_knowledge[:5]
                ]

            logger.debug(
                f"🧠 [Session 744] Knowledge context for {agent_name}: "
                f"decision={knowledge_result.decision.value}, "
                f"coverage={knowledge_result.knowledge_coverage:.2f}"
            )

            return knowledge_context
        except Exception as e:
            logger.warning(f"Failed to get knowledge context: {e}")
            return {}

    def _get_workspace_context(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Session 798: Get workspace context for an agent.

        This provides agents with information about the active workspace:
        - Project structure (directories, key files)
        - Tech stack (React, Django, etc.)
        - Coding patterns and conventions
        - Where to put generated files

        Args:
            agent_name: Name of the agent
            task: Current task description

        Returns:
            Dict with workspace structure info, or empty dict if no workspace
        """
        try:
            from core.services.workspace_manager import get_workspace_manager, WorkspaceManager
            from core.models_skin_layer import ProjectWorkspace

            # Session 893: Get workspace for ALL agents, including system tasks
            # Previously skipped workspace for system tasks (no user) - now fall back to default workspace
            # Session 895: Fixed workspace lookup - search for primary project first
            # Session 908: Order by total_operations to prefer established workspace
            # Session 910: Use centralized platform_config for configurable workspace
            manager = None
            if self.user is None:
                # Session 910: Use centralized platform config for primary workspace
                try:
                    from core.services.platform_config import get_primary_workspace
                    workspace = get_primary_workspace()
                except Exception:
                    workspace = None

                # Fallback if platform config fails
                if not workspace:
                    workspace = (
                        ProjectWorkspace.objects.filter(is_active=True, total_operations__gt=0).order_by('-total_operations').first()
                        or ProjectWorkspace.objects.filter(is_active=True).first()
                    )

                if not workspace:
                    logger.debug(f"📁 [Session 893] No default workspace available for system task {agent_name}")
                    return {}

                logger.debug(f"📁 [Session 910] Using workspace '{workspace.name}' for system task {agent_name}")
            else:
                manager = get_workspace_manager(self.user)
                workspace = manager.get_active_workspace()

                if not workspace:
                    logger.debug(f"📁 [Session 798] No active workspace for {agent_name}")
                    return {}

            # Get workspace context for this agent
            if manager:
                context = manager.get_workspace_context_for_agent(
                    workspace=workspace,
                    agent_name=agent_name,
                    task=task
                )
            else:
                # Session 893: Build basic context directly from workspace for system tasks
                # Session 908: Get WorkspaceContext if it exists (fields are on context, not workspace)
                ws_context = getattr(workspace, 'context', None)
                context = {
                    'workspace_name': workspace.name,
                    'root_path': workspace.root_path,
                    'tech_stack': workspace.tech_stack or {},
                    'key_files': getattr(ws_context, 'key_files', {}) if ws_context else {},
                    'directory_purposes': getattr(ws_context, 'directory_purposes', {}) if ws_context else {},
                    'coding_patterns': getattr(ws_context, 'coding_patterns', {}) if ws_context else {},
                    'import_aliases': getattr(ws_context, 'import_aliases', {}) if ws_context else {},
                    'protected_paths': workspace.protected_paths or [],
                    'total_files': getattr(ws_context, 'total_files', 0) if ws_context else 0,
                }

            workspace_context = {
                'has_workspace': True,
                'workspace_name': context.get('workspace_name'),
                'root_path': context.get('root_path'),
                'tech_stack': context.get('tech_stack', {}),
                'key_files': context.get('key_files', {}),
                'directory_purposes': context.get('directory_purposes', {}),
                'coding_patterns': context.get('coding_patterns', {}),
                'import_aliases': context.get('import_aliases', {}),
                'protected_paths': context.get('protected_paths', []),
                'total_files': context.get('total_files', 0),
            }

            logger.debug(
                f"📁 [Session 798] Workspace context for {agent_name}: "
                f"workspace={workspace.name}, tech={context.get('tech_stack', {}).get('frontend', 'unknown')}"
            )

            return workspace_context
        except Exception as e:
            logger.warning(f"Failed to get workspace context: {e}")
            return {}

    def _get_docs_context(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Session 798: Get documentation context for an agent.

        This provides agents with awareness of system documentation:
        - Relevant architecture docs
        - Recent session handoffs
        - Agent capabilities docs
        - Database model references

        Args:
            agent_name: Name of the agent
            task: Current task description

        Returns:
            Dict with documentation context, or empty dict if unavailable
        """
        try:
            docs_context = self.docs_context_builder.build_context_for_agent(
                agent_name=agent_name,
                task=task,
                max_docs=10,
                include_recent_sessions=True,
                include_content_snippets=False  # Keep context size manageable
            )

            if docs_context.get('has_docs'):
                logger.debug(
                    f"📚 [Session 798] Docs context for {agent_name}: "
                    f"{len(docs_context.get('relevant_docs', []))} relevant docs, "
                    f"{len(docs_context.get('recent_sessions', []))} recent sessions"
                )
            else:
                logger.debug(f"📚 [Session 798] No docs context for {agent_name}")

            return docs_context
        except Exception as e:
            logger.warning(f"Failed to get docs context: {e}")
            return {}

    # ==================== Session 949: Risk-Aware RAG Context ====================

    def _get_risk_aware_context(self, task: str) -> Dict[str, Any]:
        """
        Session 949: Get risk-aware RAG context using dual-channel retrieval.

        This provides agents with:
        - Critical docs that should never be missed
        - Recent incident reports and postmortems
        - Open audit findings (P0/P1)

        These are protected sections that won't be truncated during budget enforcement.

        Args:
            task: The task being performed (used for semantic search)

        Returns:
            Dict with 'critical_docs', 'incident_docs', 'audit_findings'
        """
        try:
            from core.services.scoped_retrieval import get_scoped_retrieval_service

            service = get_scoped_retrieval_service()

            # Get dual-channel results
            result = service.dual_channel_search(
                query=task,
                include_critical=True,
                include_incidents=True,
                include_findings=True,
                limit=10
            )

            # Format critical docs for context injection
            critical_docs_text = ""
            if result.get('critical_docs'):
                docs_list = [
                    f"- [{doc.document_class.upper()}] {doc.title}"
                    for doc in result['critical_docs'][:3]
                ]
                critical_docs_text = "CRITICAL DOCS (always review):\n" + "\n".join(docs_list)

            # Format incident docs
            incident_docs_text = ""
            if result.get('incident_docs'):
                docs_list = [
                    f"- [{doc.risk_level.upper()}] {doc.title}"
                    for doc in result['incident_docs'][:3]
                ]
                incident_docs_text = "RECENT INCIDENTS/CONSTRAINTS:\n" + "\n".join(docs_list)

            # Format audit findings
            audit_findings_text = ""
            if result.get('audit_findings'):
                findings_list = [
                    f"- [{f['priority']}] {f['title']}: {f['description'][:100]}..."
                    for f in result['audit_findings'][:3]
                ]
                audit_findings_text = "OPEN AUDIT FINDINGS:\n" + "\n".join(findings_list)

            risk_context = {
                'has_risk_context': bool(
                    result.get('critical_docs') or
                    result.get('incident_docs') or
                    result.get('audit_findings')
                ),
                'critical_docs': result.get('critical_docs', []),
                'incident_docs': result.get('incident_docs', []),
                'audit_findings': result.get('audit_findings', []),
                'critical_docs_text': critical_docs_text,
                'incident_docs_text': incident_docs_text,
                'audit_findings_text': audit_findings_text,
                'merged_results': result.get('merged_results', []),
            }

            if risk_context['has_risk_context']:
                logger.info(
                    f"🛡️ [Session 949] Risk-aware context: "
                    f"{len(result.get('critical_docs', []))} critical, "
                    f"{len(result.get('incident_docs', []))} incidents, "
                    f"{len(result.get('audit_findings', []))} findings"
                )

            return risk_context

        except Exception as e:
            logger.warning(f"Failed to get risk-aware context: {e}")
            return {
                'has_risk_context': False,
                'critical_docs': [],
                'incident_docs': [],
                'audit_findings': [],
            }

    # ==================== Session 1035: User-Uploaded Documents via RAG ====================

    def _get_user_documents_context(self, task: str) -> Dict[str, Any]:
        """Session 1035: Retrieve user-uploaded documents relevant to the task via RAG."""
        if not self.user:
            return {}
        try:
            from core.services.embedding_service import get_embedding_service
            from content.models import DocumentEmbedding

            service = get_embedding_service()
            query_vec = service.get_embedding_sync(task[:500])

            from pgvector.django import CosineDistance
            results = DocumentEmbedding.objects.filter(
                document__file_path__isnull=False,
            ).exclude(
                document__file_path='',
            ).annotate(
                distance=CosineDistance('embedding_vector', query_vec)
            ).filter(
                document__owner=self.user,
                document__status='processed',
                distance__lt=0.45,  # similarity > 0.55
            ).select_related('document').order_by('distance')[:5]

            if not results.exists():
                return {}

            doc_parts = []
            sources = []
            for emb in results:
                doc = emb.document
                similarity = round(1 - emb.distance, 2)
                doc_parts.append(
                    f"[{doc.title} | {doc.get_document_type_display()} | relevance={similarity:.0%}]\n"
                    f"{emb.chunk_text}"
                )
                if doc.title not in sources:
                    sources.append(doc.title)

            return {
                'has_user_documents': True,
                'user_documents_text': "\n---\n".join(doc_parts),
                'user_documents_sources': sources,
                'user_documents_count': len(doc_parts),
            }
        except Exception as e:
            logger.debug(f"User documents context unavailable: {e}")
            return {}

    # ==================== Session 992: Platform Tools Context ====================

    def _get_platform_tools_context(self) -> str:
        """
        Session 992: Get platform integration tools prompt.

        Injects a directive telling agents to use internal platform tools
        (image generation, agent network, etc.) instead of external services.
        Previously only injected in tasks_agents.py for Celery-executed agents.
        """
        try:
            from core.services.platform_integration import inject_platform_tools_prompt
            return inject_platform_tools_prompt()
        except Exception as _e:
            logger.warning(
                "agent_router._get_platform_tools_context: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return ''

    # ==================== Session 858: User Context Injection ====================
    # Session 877: Added 'personal_assistant' category for full user context

    # Agent category mappings for injection policy
    # Controls what user data each agent type receives to avoid prompt bloat
    AGENT_INJECTION_POLICIES = {
        # Career/Job agents get full professional context
        'career': ['skills', 'job_preferences', 'salary_range', 'work_history', 'success_patterns'],

        # Content agents get tone/style preferences
        'content': ['communication_style', 'tone_preferences', 'goals'],

        # Financial agents get risk tolerance and betting preferences
        'financial': ['risk_tolerance', 'betting_preferences', 'investment_goals'],

        # Development agents get tech stack and skills
        'development': ['skills', 'tech_stack', 'github_username'],

        # Research agents get interests and learning goals
        'research': ['interests', 'learning_goals', 'preferred_topics'],

        # Session 877: Personal Assistant needs comprehensive user context
        # PA is the main user-facing agent and needs to know the user well
        'personal_assistant': [
            'skills', 'goals', 'communication_style', 'job_preferences',
            'work_history', 'success_patterns', 'interests', 'risk_tolerance'
        ],

        # Default: minimal context for all others
        'default': ['name', 'goals', 'communication_style']
    }

    AGENT_CATEGORY_MAP = {
        # PersonalAssistantAgent removed — was 'personal_assistant' category

        # Career agents
        'OpportunityPipelineAgent': 'career',
        'CustomerResearchAgent': 'career',
        'OpportunityScoringAgent': 'career',

        # Content agents
        'ContentWriterAgent': 'content',
        'ContentStrategyAgent': 'content',
        'PodcastCoordinatorAgent': 'content',
        'AutonomousContentStudioCoordinator': 'content',
        'TopicMinerAgent': 'content',
        'VoiceCriticAgent': 'content',
        'BrandIdentityAgent': 'content',
        'SEOOptimizerAgent': 'content',
        'SocialMediaAgent': 'content',

        # Financial agents
        'StockAnalystAgent': 'financial',
        'StockAuditCoordinator': 'financial',
        'SportsOddsAnalyst': 'financial',
        'PredictionMarketAnalyst': 'financial',
        'ArbitrageDetector': 'financial',
        'BullCaseAgent': 'financial',
        'BearCaseAgent': 'financial',
        'MarketIntelligenceAgent': 'financial',
        'MarketIntelligenceCoordinator': 'financial',

        # Development agents
        'CodeGeneratorAgent': 'development',
        'FullStackDeveloperAgent': 'development',
        'CodeReviewAgent': 'development',
        'DevOpsAgent': 'development',
        'TechnicalDocumentAgent': 'development',

        # Research agents
        'ResearchAgent': 'research',
        'TrendAnalysisAgent': 'research',
        'CompetitorAnalysisAgent': 'research',
        'MarketIntelligenceAgent': 'research',
    }

    def _get_user_context(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Session 858: Get user context for personalized agent execution.

        Uses AgentContextMiddleware for structured profile data and
        MemoryContextService for dynamic memory/preferences.

        Returns minimal context by default, with agent-specific enrichment
        based on the injection policy.

        Args:
            agent_name: Name of the agent
            task: Current task description

        Returns:
            Dict with user context, or empty dict if no user
        """
        try:
            # Skip for system tasks (no user)
            if self.user is None:
                logger.debug(f"👤 [Session 858] Skipping user context for {agent_name} (no user)")
                return {}

            from core.agent_context_middleware import get_user_context_for_agent
            from core.services.memory_context_service import get_memory_context_service

            # Get structured profile context
            profile_context = get_user_context_for_agent(self.user)

            # Get memory context (preferences, goals, decisions)
            memory_service = get_memory_context_service(self.user)
            memory_context = memory_service.get_prompt_context(self.user)

            # Build user context with injection policy
            user_context = self._apply_injection_policy(
                agent_name=agent_name,
                task=task,
                profile_context=profile_context,
                memory_context=memory_context
            )

            # Session 930: Enhance context with agent-specific learning
            user_context = self._apply_agent_learning(agent_name, user_context)

            # Session 990: Inject AgentLearningService adaptive preferences
            adaptive_text = self._get_agent_learning_adaptive_context(agent_name)
            if adaptive_text:
                user_context['agent_learned_preferences'] = adaptive_text

            # Phase 3: Inject UserAgentLearning preferences into prompt.
            # Session 1103c: was 'except Exception: pass' which silently
            # dropped the user's learned preferences for this agent on
            # any failure. The agent would then run without the user's
            # personalization, producing generic responses with no
            # visible cause.
            try:
                from core.services.learning_read_service import get_learned_preferences_for_prompt
                learned_prefs = get_learned_preferences_for_prompt(self.user.id, agent_name)
                if learned_prefs:
                    user_context['learned_user_preferences'] = learned_prefs
            except Exception as e:
                logger.warning(
                    "agent_router: learned_preferences lookup failed for "
                    "user=%s agent=%s (%s: %s) — agent will run without "
                    "user personalization this cycle",
                    getattr(self.user, 'id', '<unknown>'), agent_name,
                    type(e).__name__, e,
                )

            user_context['has_user_context'] = True

            logger.debug(
                f"👤 [Session 858] Built user context for {agent_name}: "
                f"user={self.user.username}, fields={list(user_context.keys())}"
            )

            return user_context

        except Exception as e:
            logger.warning(f"Failed to get user context for {agent_name}: {e}")
            return {}

    def _apply_injection_policy(
        self,
        agent_name: str,
        task: str,
        profile_context: Dict[str, Any],
        memory_context: str
    ) -> Dict[str, Any]:
        """
        Session 858: Apply injection policy to avoid prompt bloat.

        Different agents get different slices of user data based on
        their category and needs.

        Args:
            agent_name: Name of the agent
            task: Current task
            profile_context: Full profile from AgentContextMiddleware
            memory_context: Memory string from MemoryContextService

        Returns:
            Dict with filtered user context for this agent
        """
        # Always include (small footprint)
        prof = profile_context.get('professional_profile', {})
        basic = profile_context.get('basic_profile', {})
        prefs = basic.get('preferences', {})

        user_context = {
            'name': prof.get('full_name', '') or profile_context.get('first_name', ''),
            'username': profile_context.get('username', ''),
            'communication_style': prefs.get('content_tone', 'professional'),
            'memory_summary': memory_context[:500] if memory_context else '',
        }

        # Get agent category
        category = self.AGENT_CATEGORY_MAP.get(agent_name, 'default')
        policy_fields = self.AGENT_INJECTION_POLICIES.get(category, self.AGENT_INJECTION_POLICIES['default'])

        # Conditionally add based on policy
        if 'skills' in policy_fields:
            skills_data = profile_context.get('skills', {})
            user_context['skills'] = skills_data.get('skills_list', [])[:10]
            user_context['top_skills'] = skills_data.get('top_skills', [])[:5]

        if 'job_preferences' in policy_fields:
            user_context['job_preferences'] = profile_context.get('job_preferences', {})

        if 'salary_range' in policy_fields:
            user_context['salary_range'] = prof.get('salary_range', {})

        if 'work_history' in policy_fields:
            background = profile_context.get('background', {})
            user_context['work_history'] = background.get('work_history', [])[:3]
            user_context['education'] = background.get('education', [])[:2]

        if 'goals' in policy_fields:
            personalization = profile_context.get('personalization', {})
            user_context['goals'] = personalization.get('goals', [])[:3]

        if 'success_patterns' in policy_fields:
            patterns = profile_context.get('success_patterns', {})
            user_context['success_patterns'] = patterns.get('success_patterns', [])[:3]
            user_context['application_success_patterns'] = patterns.get('application_success_patterns', [])[:3]

        if 'risk_tolerance' in policy_fields:
            user_context['risk_tolerance'] = prefs.get('risk_tolerance', 'moderate')

        if 'betting_preferences' in policy_fields:
            # Extended profile has betting data
            user_context['betting_preferences'] = {
                'enabled': prof.get('sports_betting_enabled', False),
                'favorite_sports': prof.get('favorite_sports', []),
                'risk_level': prof.get('betting_risk_level', 'conservative'),
                'bankroll': prof.get('betting_bankroll'),
            }

        if 'tech_stack' in policy_fields:
            user_context['github_username'] = prof.get('github_username', '')
            user_context['portfolio_url'] = prof.get('portfolio_url', '')

        if 'tone_preferences' in policy_fields:
            user_context['preferred_ai_model'] = prefs.get('ai_model', 'gpt-5-mini')
            user_context['dark_mode'] = prefs.get('dark_mode', True)

        if 'interests' in policy_fields or 'learning_goals' in policy_fields:
            # Would come from EnhancedUserProfile
            user_context['research_interests'] = basic.get('research_topics', [])

        return user_context

    def _apply_agent_learning(
        self,
        agent_name: str,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Session 930: Enhance context with agent-specific learning.

        Uses AgentFeedbackService to inject learning metadata based on
        past feedback for this user+agent combination.

        Args:
            agent_name: Name of the agent
            user_context: Base context to enhance

        Returns:
            Enhanced context with learning metadata
        """
        if self.user is None:
            return user_context

        try:
            from core.services.agent_feedback_service import get_agent_feedback_service
            from core.models import Agent

            # Find the agent
            agent = Agent.objects.filter(name=agent_name).first()
            if not agent:
                return user_context

            # Get feedback service and adjust context
            feedback_service = get_agent_feedback_service()
            enhanced_context = feedback_service.adjust_context_for_agent(
                user=self.user,
                agent=agent,
                base_context=user_context,
            )

            return enhanced_context

        except Exception as e:
            logger.debug(f"Agent learning context failed for {agent_name}: {e}")
            return user_context

    def _record_user_learning(
        self,
        agent_name: str,
        task: str,
        result: 'AgentResult',
        user_context: Dict[str, Any]
    ) -> None:
        """
        Session 858: Record successful patterns for user learning.

        This creates UserMemoryContext entries when agents succeed,
        enabling the system to learn what works for this user.

        Args:
            agent_name: Name of the agent that executed
            task: The task that was performed
            result: The AgentResult from execution
            user_context: The user context that was used
        """
        if not self.user or not result.success:
            return

        try:
            from core.models import UserMemoryContext, EnhancedUserProfile

            # Get or create enhanced profile
            profile, _ = EnhancedUserProfile.objects.get_or_create(user=self.user)

            # Record success pattern
            UserMemoryContext.objects.create(
                user=self.user,
                profile=profile,
                memory_type='success_pattern',
                content=f"Successfully used {agent_name} for: {task[:200]}",
                source=f'agent:{agent_name}',
                importance=7,
                context_metadata={
                    'agent_name': agent_name,
                    'task_summary': task[:500],
                    'execution_time_ms': result.execution_time_ms,
                    'tokens_used': result.tokens_used,
                }
            )

            logger.debug(f"📝 [Session 858] Recorded success pattern for {self.user.username}: {agent_name}")

        except Exception as e:
            logger.debug(f"Could not record user learning (non-critical): {e}")

    def _record_agent_learning_interaction(
        self,
        agent_name: str,
        task: str,
        result: AgentResult,
        context: Dict[str, Any]
    ):
        """
        Session 990: Record interaction for AgentLearningService (Redis-based preferences).

        Fires on every execution (success or failure) so the learning service
        can build preference models from usage patterns.
        """
        try:
            from core.services.agent_learning_service import get_learning_service, InteractionType

            get_learning_service().record_interaction(
                user_id=self.user.id,
                agent_name=agent_name,
                interaction_type=InteractionType.CREATED,
                input_data={'task': task[:500]},
                output_data={
                    'success': result.success,
                    'execution_time_ms': result.execution_time_ms,
                    'message_preview': str(result.message or '')[:200],
                },
            )
        except Exception as e:
            logger.debug(f"AgentLearningService record_interaction failed (non-critical): {e}")

    def _get_agent_learning_adaptive_context(self, agent_name: str) -> str:
        """
        Session 990: Get adaptive context string from AgentLearningService.

        Returns a short preference summary built from Redis-tracked signals,
        or empty string on any error.
        """
        try:
            from core.services.agent_learning_service import get_learning_service
            return get_learning_service().get_adaptive_context(self.user.id, agent_name)
        except Exception as _e:
            logger.warning(
                "agent_router._get_agent_learning_adaptive_context: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return ''

    def _create_execution_record(self, agent_name: str, task: str, context_summary: dict = None, experiment_id=None):
        """
        Create an execution record for tracking.
        Session 641: Added for Agent Performance Dashboard.
        Session 758: Added context_summary for integration observability.
        Session 841: Added experiment_id for proper error rate scoping.
        Session 843: Added trace_id and project_id for orchestration contract.
        """
        try:
            from core.models_unified_system import Agent, AgentExecution
            from core.services.trace_attachment_service import TraceAttachmentService

            # Get or create the Agent record (always do this for stats tracking)
            agent_record, created = Agent.objects.get_or_create(
                name=agent_name,
                defaults={
                    'agent_type': 'routable',
                    'description': f'{agent_name} - Routable agent',
                    'specialization': '',
                    'is_active': True,
                }
            )

            # Session 758: Build input_data with context tracking
            input_data = {
                'task': task,
                'context_injected': context_summary or {},
            }

            # Session 841: Resolve experiment from ID if provided
            experiment = None
            if experiment_id:
                try:
                    from core.models import Experiment
                    experiment = Experiment.objects.filter(id=experiment_id).first()
                except Exception as e:
                    logger.debug(f"Could not resolve experiment {experiment_id}: {e}")

            # Session 843: Resolve trace_id and project_id
            context = context_summary or {}
            trace_id = TraceAttachmentService.resolve_trace_id(context)
            project_id = TraceAttachmentService.resolve_project_id(context, user=self.user)

            # Session 642: User field is now nullable - always create execution record
            # Create execution record (user can be None for Celery/API tasks)
            # Session 1083 (Rigby audit): set last_heartbeat_at on create,
            # matching tasks_agents._impl_execute_agent_task. Without this,
            # executions born via agent_router.route() directly (bypassing
            # the execute_agent_task Celery wrapper's heartbeat thread)
            # show last_heartbeat_at=null forever and the cleanup watchdog
            # kills them at 60 min with "no heartbeat". This was why
            # ResearchAgent had 0/11 success in the last 7 days — every
            # dispatch through the PA universal_agent_tool path (round
            # 23 fix) creates one record here AND nothing touches its
            # heartbeat. Graceful fall-back for envs that haven't run
            # migration 0301 yet.
            _create_kwargs = dict(
                agent=agent_record,
                user=self.user,  # Can be None now
                task=task[:500],  # Truncate long tasks
                status='in_progress',
                input_data=input_data,
                experiment=experiment,  # Session 841: Link to experiment for scoped metrics
                # Session 843: Orchestration contract fields
                trace_id=trace_id,
                project_id=project_id,
                owner_agent=agent_name,
                parent_object_type=context.get('parent_object_type', ''),
                parent_object_id=context.get('parent_object_id'),
                last_heartbeat_at=timezone.now(),
            )
            try:
                execution = AgentExecution.objects.create(**_create_kwargs)
            except Exception:
                # Migration 0301 not yet applied — retry without the field
                _create_kwargs.pop('last_heartbeat_at', None)
                execution = AgentExecution.objects.create(**_create_kwargs)

            # Session 1083 round 40: round-36 set last_heartbeat_at at
            # create but never updated it — after 60 min the cleanup
            # watchdog still killed long-running agents. Spawn a daemon
            # thread that touches the heartbeat every 2 min until the
            # execution leaves 'in_progress'. Mirrors the thread in
            # tasks_agents._impl_execute_agent_task but self-terminates
            # so the caller doesn't need to manage thread lifetime.
            # Session 1084: Hoisted imports out of thread body + replaced
            # silent `except: return` with logger.exception so failures
            # are diagnosable. See tasks_agents.py:1887 for rationale —
            # C-level socket hangs can hold the Python import lock, and
            # any thread-local import at tick time would block forever.
            try:
                import threading as _hb_threading
                import time as _hb_time
                from django.db import close_old_connections as _hb_close
                _execution_id = execution.id
                _hb_agent_name = agent_name

                def _router_heartbeat_loop():
                    logger.info(
                        f"[router_heartbeat] thread start agent={_hb_agent_name} "
                        f"execution_id={_execution_id} interval=120s"
                    )
                    tick_count = 0
                    try:
                        while True:
                            _hb_time.sleep(120)
                            try:
                                _hb_close()
                                _cur_status = AgentExecution.objects.filter(
                                    id=_execution_id
                                ).values_list('status', flat=True).first()
                                if _cur_status != 'in_progress':
                                    return
                                AgentExecution.objects.filter(
                                    id=_execution_id
                                ).update(last_heartbeat_at=timezone.now())
                                tick_count += 1
                                if tick_count == 1 or tick_count % 5 == 0:
                                    logger.info(
                                        f"[router_heartbeat] tick agent={_hb_agent_name} "
                                        f"execution_id={_execution_id} tick={tick_count}"
                                    )
                            except Exception as _tick_exc:
                                logger.exception(
                                    f"[router_heartbeat] tick failed agent={_hb_agent_name} "
                                    f"execution_id={_execution_id}: {_tick_exc}"
                                )
                                return
                    finally:
                        logger.info(
                            f"[router_heartbeat] thread exit agent={_hb_agent_name} "
                            f"execution_id={_execution_id} total_ticks={tick_count}"
                        )

                _hb_thread = _hb_threading.Thread(
                    target=_router_heartbeat_loop,
                    daemon=True,
                    name=f"router_heartbeat_{agent_name}",
                )
                _hb_thread.start()
                logger.info(
                    f"[router_heartbeat] thread spawned agent={agent_name} "
                    f"execution_id={execution.id} thread_name={_hb_thread.name}"
                )
            except Exception as e:
                logger.exception(f"[router_heartbeat] Failed to start thread: {e}")

            return execution
        except Exception as e:
            logger.warning(f"Failed to create execution record: {e}")
            return None

    def _complete_execution(
        self,
        execution_record,
        agent_name: str,
        success: bool,
        execution_time_ms: int,
        output_data: dict = None,
        error_message: str = None,
        tokens_used: int = 0,
        cost: float = 0.0,
        applied_pattern_ids: Optional[list] = None  # Session 766
    ):
        """
        Complete an execution record and update agent stats.
        Session 641: Added for Agent Performance Dashboard.
        Session 729: Added AgentExecutionMemory creation for intelligent recommendations.
        Session 744: Added tokens_used and cost tracking.
        Session 766: Added applied_pattern_ids for learning pattern tracking.
        """
        try:
            from core.models_unified_system import Agent

            # Update execution record
            if execution_record:
                execution_record.status = 'completed' if success else 'failed'
                execution_record.execution_time_ms = execution_time_ms
                execution_record.completed_at = timezone.now()
                # Session 744: Track token usage and cost
                execution_record.tokens_used = tokens_used
                execution_record.cost = cost
                # Session 1084 round 48: Use update_fields to exclude
                # last_heartbeat_at from this save(). Full-instance save()
                # reads every field from the in-memory object and writes it
                # back to the DB — including the stale last_heartbeat_at
                # captured at create time. The heartbeat thread writes
                # last_heartbeat_at via queryset update() from a daemon
                # thread; those writes were being silently stomped here on
                # completion. See round 40 / round 48 investigation.
                _update_fields = [
                    'status', 'execution_time_ms', 'completed_at',
                    'tokens_used', 'cost',
                ]
                if output_data:
                    execution_record.output_data = output_data
                    _update_fields.append('output_data')
                if error_message:
                    execution_record.error_message = error_message[:500]
                    _update_fields.append('error_message')
                execution_record.save(update_fields=_update_fields)

            # Update agent stats
            Agent.objects.filter(name=agent_name).update(
                total_executions=F('total_executions') + 1,
                successful_executions=F('successful_executions') + (1 if success else 0),
                last_active=timezone.now()
            )

            # Session 729: Create AgentExecutionMemory for intelligent agent recommendations
            # This enables the system to remember which agents work best for specific tasks
            if self.user:
                try:
                    from core.models_agent_memory import AgentExecutionMemory

                    # Get task from execution record
                    task = ''
                    if execution_record and execution_record.input_data:
                        task = execution_record.input_data.get('task', '')

                    # Calculate success score (1.0 for success, 0.0 for failure)
                    success_score = 1.0 if success else 0.0

                    # Determine task type from task text
                    task_type = self._detect_task_type(task) if task else 'other'

                    # Build outcome description
                    if success:
                        outcome_desc = output_data.get('result_preview', 'Agent execution completed')[:500] if output_data else 'Agent execution completed'
                    else:
                        outcome_desc = f"Execution failed: {error_message[:200]}" if error_message else 'Execution failed'

                    AgentExecutionMemory.objects.create(
                        user=self.user,
                        agent_name=agent_name,
                        task_type=task_type,
                        task_description=task[:500] if task else 'No task description',
                        original_prompt=task[:1000] if task else '',
                        success_score=success_score,
                        execution_time_seconds=execution_time_ms / 1000.0,
                        outcome_description=outcome_desc,
                        outcome_metrics=output_data or {}
                    )
                    logger.debug(f"Created AgentExecutionMemory for {agent_name}")
                except Exception as mem_error:
                    logger.debug(f"AgentExecutionMemory creation failed (non-critical): {mem_error}")

            # Session 766: Track learning pattern application
            if applied_pattern_ids:
                try:
                    tracking_result = self.learning_pattern_engine.track_pattern_application(
                        pattern_ids=applied_pattern_ids,
                        was_successful=success
                    )
                    if tracking_result.get('tracked', 0) > 0:
                        logger.debug(
                            f"📊 [Session 766] Tracked {tracking_result['tracked']} patterns "
                            f"for {agent_name}"
                        )
                except Exception as pattern_error:
                    logger.debug(f"Pattern tracking failed (non-critical): {pattern_error}")

            logger.debug(f"Tracked execution for {agent_name}: success={success}, time={execution_time_ms}ms")

        except Exception as e:
            logger.warning(f"Failed to complete execution record: {e}")

    def _detect_task_type(self, task: str) -> str:
        """
        Session 729: Detect task type from task text for AgentExecutionMemory categorization.
        """
        if not task:
            return 'other'
        task_lower = task.lower()
        if any(w in task_lower for w in ['create', 'generate', 'make', 'design', 'build']):
            return 'creation'
        elif any(w in task_lower for w in ['edit', 'modify', 'change', 'update', 'fix']):
            return 'editing'
        elif any(w in task_lower for w in ['research', 'analyze', 'find', 'search', 'investigate']):
            return 'research'
        elif any(w in task_lower for w in ['write', 'draft', 'compose', 'blog', 'article']):
            return 'writing'
        elif any(w in task_lower for w in ['review', 'audit', 'check', 'evaluate']):
            return 'review'
        elif any(w in task_lower for w in ['what', 'how', 'why', 'when', 'who', '?']):
            return 'question'
        else:
            return 'other'

    def get_available_agents(self) -> list:
        """
        Get list of available agents.

        Returns:
            List of agent names and descriptions
        """
        agents = []
        for name, agent_class in self.AGENT_MAP.items():
            agents.append({
                'name': name,
                'description': agent_class.system_prompt[:100] + "..." if len(agent_class.system_prompt) > 100 else agent_class.system_prompt
            })
        return agents

    def is_valid_agent(self, agent_name: str) -> bool:
        """
        Check if an agent name is valid.

        Args:
            agent_name: Name to check

        Returns:
            True if agent exists
        """
        return agent_name in self.AGENT_MAP

    @staticmethod
    def execute_tool(
        tool_name: str,
        arguments: Dict[str, Any],
        user=None,
        session=None,
        project=None
    ) -> Dict[str, Any]:
        """
        Session 495: Execute a tool by name with arguments.

        This static method provides a way to execute tools through the router
        without needing an instance. It maps GPT tool names to agents and executes them.

        Args:
            tool_name: Name of the tool to execute (e.g., 'workflow_orchestration_agent')
            arguments: Tool arguments from GPT
            user: Django User object
            session: Optional session object
            project: Optional project object

        Returns:
            Dict with execution results including 'success' key
        """
        # Map GPT tool names to agent names
        TOOL_TO_AGENT_MAP = {
            'workflow_orchestration_agent': 'WorkflowOrchestrationAgent',
            'web_search': 'ResearchAgent',
            'research_topic': 'ResearchAgent',
            'research': 'ResearchAgent',
            'character_training_agent': 'CharacterTrainingAgent',
            'competitor_analysis_agent': 'CompetitorAnalysisAgent',
            'customer_research_agent': 'CustomerResearchAgent',
            'brand_strategy_agent': 'BrandStrategyAgent',
            # Session 496: Content Writer Agent
            'content_writer_agent': 'ContentWriterAgent',
            # Session 558: Markets Agents
            'prediction_market_analyst': 'PredictionMarketAnalyst',
            'sports_odds_analyst': 'SportsOddsAnalyst',
            'arbitrage_detector': 'ArbitrageDetector',
            'market_analysis': 'PredictionMarketAnalyst',
            'sports_betting': 'SportsOddsAnalyst',
            'kalshi': 'PredictionMarketAnalyst',
            'odds': 'SportsOddsAnalyst',
            'arbitrage': 'ArbitrageDetector',
            'arb': 'ArbitrageDetector',
            'sure_bet': 'ArbitrageDetector',
        }

        try:
            # Get agent name from mapping
            agent_name = TOOL_TO_AGENT_MAP.get(tool_name)
            if not agent_name:
                return {
                    'success': False,
                    'error': f"No agent mapping for tool: {tool_name}"
                }

            # Special handling for WorkflowOrchestrationAgent
            if agent_name == 'WorkflowOrchestrationAgent':
                from core.agents.workflow_orchestration_agent import WorkflowOrchestrationAgent

                # Extract project_id from project object or arguments
                project_id = None
                if project:
                    project_id = str(project.id)
                elif arguments.get('project_id'):
                    project_id = arguments['project_id']

                agent = WorkflowOrchestrationAgent(user=user, project_id=project_id)

                # Build context from arguments
                context = {
                    'workflow': arguments.get('workflow', 'research_and_create_images'),
                    'topic': arguments.get('topic', ''),
                    'count': arguments.get('count', 3),
                    'style_preferences': arguments.get('style_preferences', ''),
                    'user_message': arguments.get('user_message', ''),
                }

                # Execute the agent
                result = agent.execute(
                    task=arguments.get('user_message', arguments.get('topic', '')),
                    context=context,
                    scifi_context={},
                    spider_context={}
                )

                # Convert AgentResult to dict
                if result.success:
                    return {
                        'success': True,
                        'message': result.message,
                        'data': result.data,
                        'agent_name': result.agent_name
                    }
                else:
                    return {
                        'success': False,
                        'error': result.error
                    }

            # Session 496: Special handling for ContentWriterAgent
            # Session 522: Added real-time spider data fetching
            if agent_name == 'ContentWriterAgent':
                from core.agents.content_writer_agent import ContentWriterAgent
                from datetime import datetime

                project_id = None
                if project:
                    project_id = str(project.id)
                elif arguments.get('project_id'):
                    project_id = arguments['project_id']

                agent = ContentWriterAgent(user=user, project_id=project_id)

                # Extract research from research_context or user message
                research = arguments.get('research_context', '')
                if not research and '--- RESEARCH CONTEXT ---' in arguments.get('topic', ''):
                    # Extract from topic if it contains research
                    parts = arguments['topic'].split('--- RESEARCH CONTEXT ---', 1)
                    if len(parts) > 1:
                        research = parts[1].strip()

                # Session 522: Fetch real-time spider data if no research provided
                spider_context = {}
                topic = arguments.get('topic', '')
                if not research and topic:
                    logger.info(f"🕷️ Session 522: Fetching real-time spider data for topic: {topic}")
                    try:
                        from core.services.smart_trending_service import SmartTrendingService
                        trending_service = SmartTrendingService()
                        trending_data = trending_service.get_trending_for_query(
                            query=topic,
                            hours=72,
                            article_limit=10,
                            use_cache=True
                        )

                        if trending_data:
                            spider_context = trending_data
                            now = datetime.now()
                            today = now.strftime('%B %d, %Y')
                            month_year = now.strftime('%B %Y')
                            year = now.year
                            old_years = f"{year-2} or {year-1}"

                            research_parts = [
                                f"## Real-Time Research Data (as of {today})",
                                f"**IMPORTANT: This content is for {year}. DO NOT reference {old_years}.**\n"
                            ]

                            trends = trending_data.get('trends') or trending_data.get('trending_keywords', [])
                            if trends:
                                research_parts.append(f"### Current Trending Topics ({month_year}):")
                                for kw in trends[:10]:
                                    research_parts.append(f"- {kw}")

                            articles = trending_data.get('articles', [])
                            if articles:
                                research_parts.append(f"\n### Latest Articles ({len(articles)} found) - ALL FROM {year}:")
                                for i, article in enumerate(articles[:8], 1):
                                    title = article.get('title', 'Unknown')
                                    source = article.get('source', 'Unknown')
                                    pub_date = article.get('published', '')
                                    summary = article.get('summary', article.get('content', ''))[:200]
                                    date_str = f" - Published: {pub_date[:10]}" if pub_date else ""
                                    research_parts.append(f"\n**{i}. {title}** (Source: {source}{date_str})")
                                    if summary:
                                        research_parts.append(f"   {summary}...")

                            if trending_data.get('categories'):
                                research_parts.append(f"\n### Relevant Categories: {', '.join(trending_data['categories'])}")

                            research = "\n".join(research_parts)
                            logger.info(f"📊 Session 522: Built {len(research)} chars of research from spider data")

                    except Exception as e:
                        logger.warning(f"⚠️ Session 522: Spider data fetch failed: {e}")

                # Build context
                context = {
                    'content_type': arguments.get('content_type', 'blog_post'),
                    'research': research,
                    'tone': arguments.get('tone', 'professional'),
                    'target_audience': arguments.get('target_audience', 'general audience'),
                    'word_count': arguments.get('word_count', 1500),
                    'topic': topic,
                }

                result = agent.execute(
                    task=f"Write {context['content_type']} about {context['topic']}",
                    context=context,
                    scifi_context={},
                    spider_context=spider_context
                )

                if result.success:
                    return {
                        'success': True,
                        'message': result.message,
                        'data': result.data,
                        'agent_name': result.agent_name
                    }
                else:
                    return {
                        'success': False,
                        'error': result.error
                    }

            # For other agents, use the router
            router = AgentRouter(user=user)
            agent_result = router.route(
                agent_name=agent_name,
                task=arguments.get('query', arguments.get('topic', str(arguments))),
                context=arguments
            )

            return {
                'success': agent_result.success,
                'message': agent_result.message if agent_result.success else None,
                'error': agent_result.error if not agent_result.success else None,
                'data': agent_result.data
            }

        except Exception as e:
            logger.error(f"execute_tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }


# Convenience function
def get_agent_router(user=None) -> AgentRouter:
    """Get an AgentRouter instance."""
    return AgentRouter(user=user)
