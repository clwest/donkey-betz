"""
Super Platform - The Unified Intelligence Hub

This module contains the core coordination layer that unifies all platform
components into a single, coherent intelligence system.

Components:
- QueryClassifier: Understands user intent (question, creation, collaboration, etc.)
- PromptBuilder: Dynamically builds context-aware prompts
- ContextAggregator: Gathers context from spiders, memory, mood, relationships
- SuperPlatformCoordinator: The unified brain that orchestrates everything

Phase 2 (Spider-Agent Bridge):
- AgentContextService: Provides spider intelligence to agents
- SpiderContextMixin: Mixin for agents to access spider data

Phase 3 (Sci-Fi Integration):
- SciFiIntegrationService: Mood, memory, evolution, relationships
- SciFiContext: Complete sci-fi context for agents

Phase 4 (Revenue Pipeline):
- RevenueIntegrationService: Opportunity discovery, scoring, tracking
- RevenueOpportunity: Scored opportunity with automation eligibility
- RevenueSummary: Revenue metrics and attribution

Phase 5 (Learning Loop):
- LearningLoopService: Outcome recording, pattern detection, adaptive selection
- OutcomeRecord: Records coordinator execution outcomes
- AgentPerformance: Agent performance metrics

Phase 6 (Autonomy Engine):
- AutonomyEngine: Self-operating intelligence system
- AutonomousAction: Represents autonomous actions
- AutonomyConfig: User configuration for autonomy
- AutonomyLevel: Levels of autonomous operation
- ActionType: Types of autonomous actions
- RiskLevel: Risk levels for actions

Session 265: ALL 6 PHASES COMPLETE!
"""

from .query_classifier import QueryClassifier
from .prompt_builder import DynamicPromptBuilder
from .context_aggregator import ContextAggregator
from .coordinator import SuperPlatformCoordinator
from .agent_context_service import AgentContextService, AgentContext, get_agent_context_service
from .spider_context_mixin import SpiderContextMixin
from .scifi_integration import (
    SciFiIntegrationService,
    SciFiContext,
    MoodInfluence,
    EvolutionInfluence,
    RelationshipInfluence,
    MemoryInfluence,
    get_scifi_integration_service,
)
from .revenue_integration import (
    RevenueIntegrationService,
    RevenueOpportunity,
    RevenueSummary,
    get_revenue_integration_service,
)
from .learning_loop import (
    LearningLoopService,
    OutcomeRecord,
    AgentPerformance,
    OutcomeType,
    FeedbackType,
    get_learning_loop_service,
)
from .autonomy_engine import (
    AutonomyEngine,
    AutonomousAction,
    AutonomyConfig,
    AutonomyLevel,
    ActionType,
    RiskLevel,
    get_autonomy_engine,
)

__all__ = [
    # Phase 1: Foundation
    'QueryClassifier',
    'DynamicPromptBuilder',
    'ContextAggregator',
    'SuperPlatformCoordinator',
    # Phase 2: Spider-Agent Bridge
    'AgentContextService',
    'AgentContext',
    'get_agent_context_service',
    'SpiderContextMixin',
    # Phase 3: Sci-Fi Integration
    'SciFiIntegrationService',
    'SciFiContext',
    'MoodInfluence',
    'EvolutionInfluence',
    'RelationshipInfluence',
    'MemoryInfluence',
    'get_scifi_integration_service',
    # Phase 4: Revenue Pipeline
    'RevenueIntegrationService',
    'RevenueOpportunity',
    'RevenueSummary',
    'get_revenue_integration_service',
    # Phase 5: Learning Loop
    'LearningLoopService',
    'OutcomeRecord',
    'AgentPerformance',
    'OutcomeType',
    'FeedbackType',
    'get_learning_loop_service',
    # Phase 6: Autonomy Engine
    'AutonomyEngine',
    'AutonomousAction',
    'AutonomyConfig',
    'AutonomyLevel',
    'ActionType',
    'RiskLevel',
    'get_autonomy_engine',
]
