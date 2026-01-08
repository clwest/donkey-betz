"""
Core Views Package

Session 728: Created as package to house agent views migrated from agents/
"""

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

__all__ = [
    'StandardResultsSetPagination',
    'AgentExecutionFilter',
    'UnifiedAgentTemplateViewSet',
    'AgentExecutionViewSet',
    'AgentOrchestrationViewSet',
    'AgentToolViewSet',
    'AgentRegistryViewSet',
    'game_executions',
    'health_check',
    'discover_agents',
    'execute_agent',
    'orchestrations_list',
    'AgentChannelViewSet',
    'AgentChannelMessageViewSet',
    'AgentChannelMembershipViewSet',
]
