"""
URL configuration for the Agent Registry API
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'templates', views.UnifiedAgentTemplateViewSet, basename='agent-templates')
router.register(r'executions', views.AgentExecutionViewSet, basename='agent-executions')
router.register(r'orchestrations', views.AgentOrchestrationViewSet, basename='agent-orchestrations')
router.register(r'tools', views.AgentToolViewSet, basename='agent-tools')
router.register(r'registry', views.AgentRegistryViewSet, basename='agent-registry')

urlpatterns = [
    # Include router URLs directly (prefix added in main urls.py)
    path('', include(router.urls)),
    # Additional endpoints
    path('discover/', views.discover_agents, name='agent-discover'),
    path('health/', views.health_check, name='agent-health'),
]