"""
URLs for Agent Deployment System
"""

# PARTIAL — Session 1113 review (Session 1111 PR-B/PR-E queue).
# Classification: built but not URL-mounted.
# Why: this URLConf is fully implemented (8 deployment endpoints + execute,
# outputs, downloads, live stream, plus all-agents listings) but is NOT
# included from any active urls.py — `core/urls.py` and `core/urls_unified.py`
# do not `include('agents.urls_deployment')`. Imports work; the URLs simply
# never reach the request router.
# Decision pending: Rigby/Chris call on whether to wire this in (the
# "deploy a stack of agents to a project" feature is ~80% done) or treat
# it as dormant. See PR-E in the deeper-review queue.
# See: docs/handoffs/SESSION_1111_DEEPER_REVIEW_MAP.md

from django.urls import path
from agents.views_deployment import (
    list_available_agents,
    get_agent_recommendations,
    deploy_agents_to_project,
    get_deployment_status,
    create_integration_plan,
    get_project_agents,
    execute_agent_on_project,
    get_agent_categories
)
from agents.views_deployment_execute import (
    execute_deployed_agents,
    get_agent_outputs,
    download_generated_file,
    get_live_output_stream
)
from agents.views_all_agents import list_all_concrete_agents
from agents.views_all_agents_simple import list_all_agents_simple

app_name = 'agent_deployment'

urlpatterns = [
    # Agent browsing and discovery
    path('agents/list/', list_available_agents, name='list-agents'),
    path('agents/all/', list_all_concrete_agents, name='all-concrete-agents'),
    path('agents/simple/', list_all_agents_simple, name='all-agents-simple'),
    path('agents/categories/', get_agent_categories, name='agent-categories'),
    path('agents/recommendations/', get_agent_recommendations, name='agent-recommendations'),

    # Project agent management
    path('projects/agents/', get_project_agents, name='project-agents'),
    path('projects/deploy/', deploy_agents_to_project, name='deploy-agents'),
    path('projects/execute/', execute_agent_on_project, name='execute-agent'),

    # Deployment and orchestration
    path('deployment/status/', get_deployment_status, name='deployment-status'),
    path('deployment/plan/', create_integration_plan, name='integration-plan'),

    # Agent execution and output
    path('execute/', execute_deployed_agents, name='execute-agents'),
    path('outputs/', get_agent_outputs, name='agent-outputs'),
    path('download/', download_generated_file, name='download-file'),
    path('stream/', get_live_output_stream, name='live-stream'),
]