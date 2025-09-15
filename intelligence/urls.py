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
    RevenueMetricsView
)

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
    path('income-builder/file/<str:filename>/', ViewGeneratedFileView.as_view(), name='view_generated_file'),

    # Revenue Integration Endpoints
    path('revenue/opportunities/', RevenueOpportunitiesView.as_view(), name='revenue_opportunities'),
    path('revenue/submit/', SubmitProposalView.as_view(), name='submit_proposal'),
    path('revenue/metrics/', RevenueMetricsView.as_view(), name='revenue_metrics'),
]