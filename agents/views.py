"""
DEPRECATED: This module has been moved to core/views/agents.py

For new code, use:
    from core.views.agents import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/views/
"""
import warnings

warnings.warn(
    "Importing from 'agents.views' is deprecated. "
    "Use 'from core.views.agents import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.views.agents import (
    StandardResultsSetPagination,
    AgentExecutionFilter,
    UnifiedAgentTemplateViewSet,
    AgentExecutionViewSet,
    AgentOrchestrationViewSet,
    AgentToolViewSet,
    AgentRegistryViewSet,
    game_executions,
    health_check,
    discover_agents,
    execute_agent,
    orchestrations_list,
    AgentChannelViewSet,
    AgentChannelMessageViewSet,
    AgentChannelMembershipViewSet,
)
