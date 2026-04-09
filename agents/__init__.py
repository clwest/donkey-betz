"""
Agent Registry Module - Unified AI Agent Management System
==========================================================

DEPRECATION NOTICE (Session 280):
---------------------------------
This module is DEPRECATED. Import from core.agents instead.

Old (deprecated):
    from agents import ImageAgent
    from agents.image_agent import ImageAgent

New (correct):
    from core.agents import ImageAgent

The agents package is being unified under core/agents/ for:
1. Consistent BaseAgent with TimeTravelMixin
2. Tool isolation (each agent has ONLY its domain tools)
3. Integrated sci-fi context (mood, memory, evolution)
4. Spider data integration
5. Deterministic routing via AgentRouter

This compatibility shim will emit deprecation warnings and redirect
imports to the new core.agents location.

Session 186: Original BaseContentAgent for Task 3.7 Agent System Cleanup
Session 280: Added deprecation warnings, migration to core.agents
"""

import warnings
from typing import TYPE_CHECKING

# Session 728: Make imports lazy to avoid circular import during Django app loading
# The imports from agents.base_agent are now lazy-loaded via __getattr__

default_app_config = 'agents.apps.AgentsConfig'

# Lazy-loaded modules
_BaseContentAgent = None
_LegacyAgentResult = None


def _deprecated_warning(name: str, stacklevel: int = 3):
    """Emit a deprecation warning for legacy imports."""
    warnings.warn(
        f"Importing {name} from 'agents' is deprecated. "
        f"Use 'from core.agents import {name}' instead. "
        f"This compatibility shim will be removed in a future version.",
        DeprecationWarning,
        stacklevel=stacklevel
    )


# Map legacy agent names to their clean architecture equivalents
_CLEAN_AGENT_MAP = {
    # Core agents (clean architecture)
    'ImageAgent': 'core.agents.image_agent.ImageAgent',
    'VideoAgent': 'core.agents.video_agent.VideoAgent',
    'AudioAgent': 'core.agents.audio_agent.AudioAgent',
    'ThreeDAgent': 'core.agents.three_d_agent.ThreeDAgent',
    'ImageEditingAgent': 'core.agents.image_editing_agent.ImageEditingAgent',
    'VideoEditingAgent': 'core.agents.video_editing_agent.VideoEditingAgent',
    'ResearchAgent': 'core.agents.research_agent.ResearchAgent',
    'WorkflowAgent': 'core.agents.workflow_agent.WorkflowAgent',
    # PersonalAssistantAgent removed — deprecated, all PA traffic routes through Rigby
    'BaseAgent': 'core.agents.base_agent.BaseAgent',
    'AgentResult': 'core.agents.base_agent.AgentResult',

    # Strategy agents (Session 280 - migrated to clean architecture)
    'ContentStrategyAgent': 'core.agents.strategy.content_strategy_agent.ContentStrategyAgent',
    'BrandIdentityAgent': 'core.agents.strategy.brand_identity_agent.BrandIdentityAgent',
    'SEOOptimizerAgent': 'core.agents.strategy.seo_optimizer_agent.SEOOptimizerAgent',
    'SocialMediaAgent': 'core.agents.strategy.social_media_agent.SocialMediaAgent',

    # Executive agents (Session 280 - migrated to clean architecture)
    'CTOAgent': 'core.agents.executive.cto_agent.CTOAgent',
    'COOAgent': 'core.agents.executive.coo_agent.COOAgent',
    'CreativeDirectorAgent': 'core.agents.executive.creative_director_agent.CreativeDirectorAgent',
    'MeetingCoordinatorAgent': 'core.agents.executive.meeting_coordinator_agent.MeetingCoordinatorAgent',

    # Analysis agents (Session 280 Phase 3 - migrated to clean architecture)
    'TrendAnalysisAgent': 'core.agents.analysis.trend_analysis_agent.TrendAnalysisAgent',
    'OpportunityScoringAgent': 'core.agents.analysis.opportunity_scoring_agent.OpportunityScoringAgent',

    # Training agents (Session 280 Phase 3 - migrated to clean architecture)
    'CharacterTrainingAgent': 'core.agents.training.character_training_agent.CharacterTrainingAgent',
    'TrainedCreationAgent': 'core.agents.training.trained_creation_agent.TrainedCreationAgent',

    # Security agents (Session 280 Phase 3 - migrated to clean architecture)
    'MemoryIsolationAgent': 'core.agents.security.memory_isolation_agent.MemoryIsolationAgent',
}

# Legacy agents that haven't been migrated yet (use old path)
_LEGACY_ONLY_AGENTS = {
    'BookmakerAgent': 'agents.bookmaker_agent.BookmakerAgent',
    'CreationAgent': 'agents.creation_agent.CreationAgent',
    'WorkflowOrchestrationAgent': 'agents.workflow_orchestration_agent.WorkflowOrchestrationAgent',
}


def __getattr__(name: str):
    """
    Dynamic attribute access for agent classes.

    This enables:
        from agents import ImageAgent  # Deprecated, but works with warning

    Redirects to core.agents for clean agents, or loads legacy agents.
    """
    # Check if it's a clean agent that should come from core.agents
    if name in _CLEAN_AGENT_MAP:
        _deprecated_warning(name)

        # Import from core.agents
        module_path = _CLEAN_AGENT_MAP[name]
        parts = module_path.rsplit('.', 1)
        module_name, class_name = parts[0], parts[1]

        import importlib
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    # Check if it's a legacy-only agent
    if name in _LEGACY_ONLY_AGENTS:
        module_path = _LEGACY_ONLY_AGENTS[name]
        parts = module_path.rsplit('.', 1)
        module_name, class_name = parts[0], parts[1]

        import importlib
        module = importlib.import_module(module_name)
        return getattr(module, class_name)

    # Handle legacy base classes (Session 728: lazy-loaded)
    if name == 'BaseContentAgent':
        global _BaseContentAgent
        if _BaseContentAgent is None:
            from core.agents.base_content_agent import BaseContentAgent as _BC
            _BaseContentAgent = _BC
        return _BaseContentAgent

    if name == 'LegacyAgentResult':
        global _LegacyAgentResult
        if _LegacyAgentResult is None:
            from core.agents.base_content_agent import AgentResult as _AR
            _LegacyAgentResult = _AR
        return _LegacyAgentResult

    if name == 'AgentResult':
        _deprecated_warning(name)
        from core.agents.base_agent import AgentResult
        return AgentResult

    raise AttributeError(f"module 'agents' has no attribute '{name}'")


# Explicit exports for type checking and IDE support
if TYPE_CHECKING:
    from core.agents import (
        BaseAgent,
        AgentResult,
        ImageAgent,
        VideoAgent,
        AudioAgent,
        ThreeDAgent,
        ImageEditingAgent,
        VideoEditingAgent,
        ResearchAgent,
        WorkflowAgent,
    )

__all__ = [
    # Legacy (for backwards compatibility)
    'BaseContentAgent',
    'LegacyAgentResult',

    # Clean architecture (preferred - these redirect to core.agents)
    'BaseAgent',
    'AgentResult',
    'ImageAgent',
    'VideoAgent',
    'AudioAgent',
    'ThreeDAgent',
    'ImageEditingAgent',
    'VideoEditingAgent',
    'ResearchAgent',
    'WorkflowAgent',
]