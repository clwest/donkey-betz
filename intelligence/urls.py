"""
🧠 INTELLIGENCE API URLs
URL routing for the Real-Time Intelligence Engine
"""

from django.urls import path
from .views import (
    SkynetStatusView,
    LiveOpportunitiesView,
    LivePredictionsView,
    IncomeBuilderAnalysisView,
    IncomeActionPlanView,
    ActionPlanPersistenceView,
    ExecuteActionPlanView,
    ViewGeneratedFileView,
    RevenueOpportunitiesView,
    SubmitProposalView,
    RevenueMetricsView,
    ExecuteAgentPlanView
)
from .views_agent_integration import (
    analyze_plan_for_automation,
    execute_plan_automation,
    get_available_agents,
    execute_specific_agent,
    get_execution_status
)
from .automation_workflows import (
    setup_automation_workflow,
    execute_daily_automation,
    get_automation_workflows,
    quick_start_setup
)
from .views_advisor_review import request_advisor_review

urlpatterns = [
    # Skynet Intelligence Engine
    path('skynet/status/', SkynetStatusView.as_view(), name='skynet_status'),

    # Live Intelligence Data
    path('opportunities/', LiveOpportunitiesView.as_view(), name='live_opportunities'),
    path('predictions/', LivePredictionsView.as_view(), name='live_predictions'),

    # AI Income Builder - Start from $0
    path('income-builder/', IncomeBuilderAnalysisView.as_view(), name='income_builder'),
    path('income-builder/action-plan/', IncomeActionPlanView.as_view(), name='income_action_plan'),
    path('income-builder/plans/', ActionPlanPersistenceView.as_view(), name='action_plan_persistence'),
    path('income-builder/execute/', ExecuteActionPlanView.as_view(), name='execute_action_plan'),
    path('income-builder/file/<path:filename>/', ViewGeneratedFileView.as_view(), name='view_generated_file'),

    # Revenue Integration Endpoints
    path('revenue/opportunities/', RevenueOpportunitiesView.as_view(), name='revenue_opportunities'),
    path('revenue/submit/', SubmitProposalView.as_view(), name='submit_proposal'),
    path('revenue/metrics/', RevenueMetricsView.as_view(), name='revenue_metrics'),

    # Agent Execution Endpoints
    path('agent-execute/', ExecuteAgentPlanView.as_view(), name='execute_agent_plan'),

    # Real Agent Integration Endpoints
    path('income-builder/analyze-plan/', analyze_plan_for_automation, name='analyze_plan_automation'),
    path('income-builder/process-plan/', execute_plan_automation, name='execute_plan_automation'),
    path('agents/available/', get_available_agents, name='get_available_agents'),
    path('agents/execute/', execute_specific_agent, name='execute_specific_agent'),
    path('agents/status/<str:execution_id>/', get_execution_status, name='get_execution_status'),

    # Automation Workflow Endpoints
    path('automation/workflows/', get_automation_workflows, name='get_automation_workflows'),
    path('automation/setup/', setup_automation_workflow, name='setup_automation_workflow'),
    path('automation/execute/', execute_daily_automation, name='execute_daily_automation'),
    path('automation/quick-start/', quick_start_setup, name='quick_start_setup'),

    # Advisor Review Endpoints
    path('advisor-review/', request_advisor_review, name='request_advisor_review'),
]