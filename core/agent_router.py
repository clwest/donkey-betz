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
from typing import Dict, Any, Optional, Type
from django.utils import timezone
from django.db.models import F

from core.agents.base_agent import BaseAgent, AgentResult
from core.agents.image_agent import ImageAgent
from core.agents.video_agent import VideoAgent
from core.agents.audio_agent import AudioAgent
from core.agents.three_d_agent import ThreeDAgent
from core.agents.image_editing_agent import ImageEditingAgent
from core.agents.video_editing_agent import VideoEditingAgent
from core.agents.research_agent import ResearchAgent
from core.agents.workflow_agent import WorkflowAgent
from core.agents.personal_assistant_agent import PersonalAssistantAgent

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
from core.agents.content import TopicMinerAgent, ContrarianAgent, PerformanceAnalystAgent
# Session 743: Content Diversity Orchestrator
from core.agents.content_diversity_orchestrator import ContentDiversityOrchestrator

# Session 478: DaVinci Resolve Integration
from core.agents.resolve_agent import ResolveAgent

# Session 496: Content Writer Agent
from core.agents.content_writer_agent import ContentWriterAgent

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
from core.agents.markets import PredictionMarketAnalyst, SportsOddsAnalyst, ArbitrageDetector

# Session 637: Missing agents from root directory
from core.agents.opportunity_pipeline_agent import OpportunityPipelineAgent
from core.agents.content_executor_agent import ContentExecutorAgent
from core.agents.workflow_orchestration_agent import WorkflowOrchestrationAgent
from core.agents.thinking_agent import ThinkingAgent
from core.agents.technical_document_agent import TechnicalDocumentAgent

# Session 663: System Intelligence Agent
from core.agents.system_intelligence_agent import SystemIntelligenceAgent

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
        "ThreeDAgent": ThreeDAgent,

        # Editing Agents
        "ImageEditingAgent": ImageEditingAgent,
        "VideoEditingAgent": VideoEditingAgent,

        # Research Agents
        "ResearchAgent": ResearchAgent,

        # Writing Agents (Session 496)
        "ContentWriterAgent": ContentWriterAgent,

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

        # Markets Agents (Session 558)
        "PredictionMarketAnalyst": PredictionMarketAnalyst,
        "SportsOddsAnalyst": SportsOddsAnalyst,
        "ArbitrageDetector": ArbitrageDetector,

        # Session 637: Orchestration & Utility Agents
        "OpportunityPipelineAgent": OpportunityPipelineAgent,
        "ContentExecutorAgent": ContentExecutorAgent,
        "WorkflowOrchestrationAgent": WorkflowOrchestrationAgent,
        "ThinkingAgent": ThinkingAgent,
        "TechnicalDocumentAgent": TechnicalDocumentAgent,

        # Session 663: System Intelligence Agent
        "SystemIntelligenceAgent": SystemIntelligenceAgent,

        # Entry Point Agent
        "PersonalAssistantAgent": PersonalAssistantAgent,
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
    def semantic_router(self):
        """Session 488: Lazy-load Semantic routing service."""
        if self._semantic_router is None:
            from core.services.semantic_routing import get_semantic_router
            self._semantic_router = get_semantic_router()
        return self._semantic_router

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
        fallback_agent: str = "PersonalAssistantAgent"
    ) -> AgentResult:
        """
        Session 488: Route a query to the best agent using semantic matching.

        This method uses embeddings to find the most semantically similar agent
        for the given query. If confidence is high enough, it routes directly
        to that agent. Otherwise, it falls back to the specified fallback agent.

        Args:
            query: The user's natural language query
            context: Optional additional context
            fallback_agent: Agent to use if semantic matching fails (default: PersonalAssistantAgent)

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
                'selected_agent': 'PersonalAssistantAgent',
                'confidence': 0.0,
                'method': 'error_fallback',
                'error': str(e)
            }

    def route(
        self,
        agent_name: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """
        Route a task to the appropriate agent.

        This is the main entry point. It:
        1. Validates the agent name
        2. Instantiates the agent
        3. Gathers sci-fi and spider context
        4. Executes the agent
        5. Returns the result

        Args:
            agent_name: Name of the agent to route to (e.g., "ImageAgent")
            task: The task to perform in natural language
            context: Optional additional context (count, style, reference_id, etc.)

        Returns:
            AgentResult from the agent execution

        Raises:
            AgentNotFoundError: If agent_name is not in AGENT_MAP
        """
        context = context or {}

        # Validate agent name
        agent_class = self.AGENT_MAP.get(agent_name)
        if not agent_class:
            available = ", ".join(self.AGENT_MAP.keys())
            raise AgentNotFoundError(
                f"Unknown agent: '{agent_name}'. Available agents: {available}"
            )

        logger.info(f"Routing to {agent_name}: {task[:50]}...")

        # Instantiate the agent
        agent = agent_class(user=self.user)

        # Gather context
        scifi_context = self._get_scifi_context(agent_name, task)
        # Session 744: Use SpiderContextBuilder for agent-specific spider context
        spider_context = self._get_spider_context(task, agent_name=agent_name)
        # Session 744 Phase 3: Get learning patterns for this agent
        learning_context = self._get_learning_context(agent_name, task)
        # Session 744 Phase 4: Get advisor wisdom for this agent
        advisor_context = self._get_advisor_context(agent_name, task)
        # Session 744 Phase 5: Get performance feedback for this agent
        feedback_context = self._get_feedback_context(agent_name, task)

        # Session 522: Special handling for ContentWriterAgent - use SmartTrendingService
        # with dynamic year references and DuckDuckGo fallback for fresh 2025 data
        if agent_name == 'ContentWriterAgent':
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

        # Execute the agent with tracking
        start_time = timezone.now()
        execution_record = None

        try:
            # Create execution record
            execution_record = self._create_execution_record(agent_name, task)

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

            # Track successful execution
            # Session 641: Use result.message (not result.output which doesn't exist on AgentResult)
            # Session 744: Pass tokens_used and cost to execution record
            self._complete_execution(
                execution_record,
                agent_name,
                success=result.success,
                execution_time_ms=result.execution_time_ms,
                output_data={'result_preview': str(result.message)[:500] if result.message else None},
                tokens_used=result.tokens_used,
                cost=result.cost
            )

            logger.info(
                f"{agent_name} completed: success={result.success}, "
                f"time={result.execution_time_ms}ms"
            )

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

            logger.error(f"Agent execution error ({agent_name}): {e}")
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

    def _create_execution_record(self, agent_name: str, task: str):
        """
        Create an execution record for tracking.
        Session 641: Added for Agent Performance Dashboard.
        """
        try:
            from core.models_unified_system import Agent, AgentExecution

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

            # Session 642: User field is now nullable - always create execution record
            # Create execution record (user can be None for Celery/API tasks)
            execution = AgentExecution.objects.create(
                agent=agent_record,
                user=self.user,  # Can be None now
                task=task[:500],  # Truncate long tasks
                status='in_progress',
                input_data={'task': task}
            )

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
        cost: float = 0.0
    ):
        """
        Complete an execution record and update agent stats.
        Session 641: Added for Agent Performance Dashboard.
        Session 729: Added AgentExecutionMemory creation for intelligent recommendations.
        Session 744: Added tokens_used and cost tracking.
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
                if output_data:
                    execution_record.output_data = output_data
                if error_message:
                    execution_record.error_message = error_message[:500]
                execution_record.save()

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
            'coleadership_agent': 'CoLeadershipAgent',
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
