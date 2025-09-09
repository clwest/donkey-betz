"""
WebSocket routing configuration for unified-donkey-betz platform.
Migrated from DBAO tools-manifest WebSocket capabilities.
"""

from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from . import consumers

websocket_urlpatterns = [
    # Agent progress monitoring (from DBAO tools-manifest)
    re_path(r'^ws/agent-progress/$', consumers.AgentProgressConsumer.as_asgi()),
    re_path(r'^ws/agent-progress/(?P<instance_id>[^/]+)/$', consumers.AgentProgressConsumer.as_asgi()),
    
    # Dashboard real-time updates (from DBAO tools-manifest)
    re_path(r'^ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
    
    # Live sports and betting updates
    re_path(r'^ws/live-sports/$', consumers.LiveSportsConsumer.as_asgi()),
    re_path(r'^ws/arbitrage/$', consumers.ArbitrageConsumer.as_asgi()),
    
    # Assistant chat WebSocket (from ai-content-studio)
    re_path(r'^ws/assistant/$', consumers.AssistantChatConsumer.as_asgi()),
    
    # Multi-agent orchestration updates
    re_path(r'^ws/orchestration/(?P<orchestration_id>[^/]+)/$', consumers.OrchestrationConsumer.as_asgi()),
    
    # System notifications and alerts
    re_path(r'^ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})