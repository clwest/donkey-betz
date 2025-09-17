
"""
URL Configuration for Real Data Endpoints
"""

from django.urls import path
from . import views_real_data as views

urlpatterns = [
    # Income Builder
    path('api/income-builder/opportunities/', views.get_income_opportunities, name='income-opportunities'),

    # Sports
    path('api/sports/predictions/', views.get_sports_predictions, name='sports-predictions'),

    # Agents
    path('api/agents/list/', views.get_agent_registry, name='agent-registry'),
    path('api/agents/execute/', views.execute_agent, name='execute-agent'),

    # Revenue
    path('api/revenue/summary/', views.get_revenue_summary, name='revenue-summary'),

    # System
    path('api/metrics/', views.get_system_metrics, name='system-metrics'),
    path('api/orchestration/active/', views.get_active_orchestrations, name='active-orchestrations'),

    # User
    path('api/profile/', views.get_user_profile, name='user-profile'),
    path('api/executions/recent/', views.get_recent_executions, name='recent-executions'),
]
