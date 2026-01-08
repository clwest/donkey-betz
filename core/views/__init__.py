"""
Core Views Package

Session 728: Restructured as package to house both:
- Original platform views (from core/views.py, now in main.py)
- Agent views migrated from agents/views.py (in agents.py)
"""

# Import platform views from main.py (original core/views.py)
# These are used by core/urls.py
from core.views.main import (
    platform_info,
    platform_status,
    record_metric,
    health_check,
    blog_list,
    campaigns_list,
    styles_list,
    prompting_settings,
    execute_agent,
    agent_instances,
    agent_executions_list,
    prompt_diagnostics_dashboard,
    prompt_diagnostics_analyses,
    prompt_diagnostics_templates,
    feedback_analytics,
    feedback_history,
    feedback_submit,
    prompting_stats,
    prompting_test,
    assistant_context,
    assistant_chat,
    research_books,
    research_documents,
    personal_knowledge_list,
    agents_discovery_stats,
    ebooks_list,
    voice_history,
    llm_chat,
)

# Import agent views from agents.py (migrated from agents/views.py)
# These use different names to avoid conflict with platform views
from core.views.agents import (
    StandardResultsSetPagination,
    AgentExecutionFilter,
    UnifiedAgentTemplateViewSet,
    AgentExecutionViewSet,
    AgentOrchestrationViewSet,
    AgentToolViewSet,
    AgentRegistryViewSet,
    game_executions,
    discover_agents,
    orchestrations_list,
    AgentChannelViewSet,
    AgentChannelMessageViewSet,
    AgentChannelMembershipViewSet,
)
# Rename conflicting agent views
from core.views.agents import health_check as agent_health_check
from core.views.agents import execute_agent as agent_execute_agent

__all__ = [
    # Platform views (from main.py)
    'platform_info',
    'platform_status',
    'record_metric',
    'health_check',
    'blog_list',
    'campaigns_list',
    'styles_list',
    'prompting_settings',
    'execute_agent',
    'agent_instances',
    'agent_executions_list',
    'prompt_diagnostics_dashboard',
    'prompt_diagnostics_analyses',
    'prompt_diagnostics_templates',
    'feedback_analytics',
    'feedback_history',
    'feedback_submit',
    'prompting_stats',
    'prompting_test',
    'assistant_context',
    'assistant_chat',
    'research_books',
    'research_documents',
    'personal_knowledge_list',
    'agents_discovery_stats',
    'ebooks_list',
    'voice_history',
    'llm_chat',
    # Agent views (from agents.py)
    'StandardResultsSetPagination',
    'AgentExecutionFilter',
    'UnifiedAgentTemplateViewSet',
    'AgentExecutionViewSet',
    'AgentOrchestrationViewSet',
    'AgentToolViewSet',
    'AgentRegistryViewSet',
    'game_executions',
    'discover_agents',
    'orchestrations_list',
    'AgentChannelViewSet',
    'AgentChannelMessageViewSet',
    'AgentChannelMembershipViewSet',
    'agent_health_check',
    'agent_execute_agent',
]
