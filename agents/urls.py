"""
URL configuration for the Agent Registry API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import views_monitoring

# Create router and register viewsets
router = DefaultRouter()
router.register(r'templates', views.UnifiedAgentTemplateViewSet, basename='agent-templates')
router.register(r'executions', views.AgentExecutionViewSet, basename='agent-executions')
router.register(r'orchestrations', views.AgentOrchestrationViewSet, basename='agent-orchestrations')
router.register(r'tools', views.AgentToolViewSet, basename='agent-tools')
router.register(r'registry', views.AgentRegistryViewSet, basename='agent-registry')

# Agent Channels - "Slack for AI Agents"
router.register(r'channels', views.AgentChannelViewSet, basename='agent-channels')
router.register(r'messages', views.AgentChannelMessageViewSet, basename='agent-messages')
router.register(r'memberships', views.AgentChannelMembershipViewSet, basename='agent-memberships')

urlpatterns = [
    # Include router URLs directly (prefix added in main urls.py)
    path('', include(router.urls)),
    # Additional endpoints
    path('discover/', views.discover_agents, name='agent-discover'),
    path('execute/', views.execute_agent, name='agent-execute'),
    path('health/', views.health_check, name='agent-health'),
    path('game/<str:game_id>/executions/', views.game_executions, name='agent-game-executions'),
    
    # Monitoring endpoints
    path('monitoring/dashboard/', views_monitoring.agent_metrics_dashboard, name='agent-monitoring-dashboard'),
    path('monitoring/agent/<str:agent_name>/', views_monitoring.agent_performance_detail, name='agent-performance-detail'),
    path('monitoring/report/', views_monitoring.performance_report, name='agent-performance-report'),
    path('monitoring/real-time/', views_monitoring.real_time_metrics, name='agent-realtime-metrics'),
    path('monitoring/alerts/', views_monitoring.alert_status, name='agent-alert-status'),
    path('monitoring/cache/clear/', views_monitoring.clear_metrics_cache, name='agent-clear-cache'),
]