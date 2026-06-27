"""
Unified Agent Registry Models
=============================

Session 391: Migrated from agents/models.py to core/models/agents_registry/

This module provides the comprehensive agent registry system for the Unified Donkey Betz Platform.
It consolidates and enhances agent management from the donkey-betz-agent-orchestra into a
unified, scalable, and self-aware agent system.

Features:
- Unified agent templates with rich metadata
- Cross-domain capabilities (sports, content, orchestration)
- Version control and capability mapping
- Execution tracking and performance metrics
- Real-time status monitoring
- Self-aware registry system

Usage:
    from core.models.agents_registry import UnifiedAgentTemplate, AgentTaskExecution
    # or
    from core.models import UnifiedAgentTemplate  # after adding to __all__
"""

from .models import (
    # Enums/Choices
    AgentSpecialization,
    LLMProvider,
    AgentStatus,
    AgentPriority,

    # Models
    UnifiedAgentTemplate,
    AgentTaskExecution,
    AgentContribution,
    AgentOrchestration,
    AgentTool,
    AgentRegistry,
    AgentChannel,
    AgentChannelMessage,
    AgentChannelMembership,
    AgentPerformanceMetrics,
)

__all__ = [
    # Enums/Choices
    'AgentSpecialization',
    'LLMProvider',
    'AgentStatus',
    'AgentPriority',

    # Models
    'UnifiedAgentTemplate',
    'AgentTaskExecution',
    'AgentContribution',
    'AgentOrchestration',
    'AgentTool',
    'AgentRegistry',
    'AgentChannel',
    'AgentChannelMessage',
    'AgentChannelMembership',
    'AgentPerformanceMetrics',
]
