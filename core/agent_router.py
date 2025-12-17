"""
Agent Router - Deterministic Routing to Specialized Agents
===========================================================

Session 268: Phase 1 & 2 - Complete Agent Ecosystem
Session 280: Phase 2 - Added Strategy and Executive Agents
Session 280: Phase 3 - Added Analysis, Training, and Security Agents

This router provides DETERMINISTIC routing to specialized agents.
No LLM is involved in routing decisions - it's a simple dictionary lookup.

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

    Orchestration:
    - WorkflowAgent: Multi-step workflow coordination
"""

import logging
from typing import Dict, Any, Optional, Type

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

# Session 293: Business Research Agents
from core.agents.business import (
    CompetitorAnalysisAgent,
    CustomerResearchAgent,
)

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

# Session 461: Stock Audit Agents
from core.agents.stocks import StockAuditCoordinator

# Session 461: Blockchain Audit Agents
from core.agents.blockchain import BlockchainAuditCoordinator

# Session 445: Series Workflow Agent
from core.agents.ai_series_workflow_agent import AISeriesWorkflowAgent

# Session 466: Autonomous Content Studio
from core.agents.autonomous_content_studio_coordinator import AutonomousContentStudioCoordinator
from core.agents.content import TopicMinerAgent, ContrarianAgent, PerformanceAnalystAgent

# Session 478: DaVinci Resolve Integration
from core.agents.resolve_agent import ResolveAgent

logger = logging.getLogger(__name__)


class AgentNotFoundError(Exception):
    """Raised when an unknown agent is requested."""
    pass


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

        # Business Research Agents (Session 293)
        "CompetitorAnalysisAgent": CompetitorAnalysisAgent,
        "CustomerResearchAgent": CustomerResearchAgent,

        # Legal Agents (Session 403)
        "LegalDocDrafterAgent": LegalDocDrafterAgent,

        # Development Agents (Session 436)
        "CodeGeneratorAgent": CodeGeneratorAgent,
        "FullStackDeveloperAgent": FullStackDeveloperAgent,
        "CodeReviewAgent": CodeReviewAgent,
        "DevOpsAgent": DevOpsAgent,

        # Security Agents (Session 461)
        "ContentAuditAgent": ContentAuditAgent,

        # Stock Audit Agents (Session 461)
        "StockAuditCoordinator": StockAuditCoordinator,

        # Blockchain Audit Agents (Session 461)
        "BlockchainAuditCoordinator": BlockchainAuditCoordinator,

        # Series Workflow Agent (Session 445)
        "AISeriesWorkflowAgent": AISeriesWorkflowAgent,

        # Autonomous Content Studio (Session 466)
        "AutonomousContentStudioCoordinator": AutonomousContentStudioCoordinator,
        "TopicMinerAgent": TopicMinerAgent,
        "ContrarianAgent": ContrarianAgent,
        "PerformanceAnalystAgent": PerformanceAnalystAgent,

        # Rendering Agents (Session 478)
        "ResolveAgent": ResolveAgent,

        # Orchestration Agents
        "WorkflowAgent": WorkflowAgent,

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
        spider_context = self._get_spider_context(task)

        # Execute the agent
        try:
            result = agent.execute(
                task=task,
                context=context,
                scifi_context=scifi_context,
                spider_context=spider_context
            )

            logger.info(
                f"{agent_name} completed: success={result.success}, "
                f"time={result.execution_time_ms}ms"
            )

            return result

        except Exception as e:
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

    def _get_spider_context(self, task: str) -> Dict[str, Any]:
        """
        Get spider intelligence context for a task.

        This includes:
        - Relevant trends
        - Market data (if applicable)
        - Related discussions
        - Creative trends (styles, colors)

        Args:
            task: Task to get context for

        Returns:
            Dict with spider context
        """
        try:
            context = self.spider_service.get_insights_for_prompt(task)

            # Also get creative trends for image/design tasks
            if any(word in task.lower() for word in ['logo', 'image', 'design', 'banner', 'illustration']):
                creative = self.spider_service.get_creative_trends(hours=48)
                context['creative_trends'] = creative

            return context
        except Exception as e:
            logger.warning(f"Failed to get spider context: {e}")
            return {}

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


# Convenience function
def get_agent_router(user=None) -> AgentRouter:
    """Get an AgentRouter instance."""
    return AgentRouter(user=user)
