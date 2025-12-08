"""
Agent Registry Models - Compatibility Shim
==========================================

Session 391: These models have been migrated to core/models/agents_registry/

This file exists for backwards compatibility. All imports will work, but
new code should import from core.models.agents_registry directly.

Migration Path:
    Old: from agents.models import UnifiedAgentTemplate
    New: from core.models.agents_registry import UnifiedAgentTemplate

The actual model definitions are now in:
    core/models/agents_registry/models.py

IMPORTANT: The models still use app_label='agents' in their Meta class,
so Django continues to use the same database tables. No migration needed.
"""

# Re-export everything from the new location for backwards compatibility
from core.models.agents_registry import (
    # Enums/Choices
    AgentSpecialization,
    LLMProvider,
    AgentStatus,
    AgentPriority,

    # Models
    UnifiedAgentTemplate,
    AgentExecution,
    AgentContribution,
    AgentOrchestration,
    AgentTool,
    AgentRegistry,
    AgentChannel,
    AgentChannelMessage,
    AgentChannelMembership,
    AgentPerformanceMetrics,
)

# Backwards compatibility - some code imports Agent from here expecting UnifiedAgentTemplate
Agent = UnifiedAgentTemplate

__all__ = [
    # Enums/Choices
    'AgentSpecialization',
    'LLMProvider',
    'AgentStatus',
    'AgentPriority',

    # Models
    'UnifiedAgentTemplate',
    'AgentExecution',
    'AgentContribution',
    'AgentOrchestration',
    'AgentTool',
    'AgentRegistry',
    'AgentChannel',
    'AgentChannelMessage',
    'AgentChannelMembership',
    'AgentPerformanceMetrics',

    # Alias
    'Agent',
]
