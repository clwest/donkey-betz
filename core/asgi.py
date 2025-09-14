"""
ASGI config for Unified Donkey Betz platform.

This ASGI configuration supports:
- HTTP requests via Django
- WebSocket connections via Channels
- Real-time communication for agent orchestration
- Live sports data streaming
- AI content generation updates
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize Django ASGI application early
django_asgi_app = get_asgi_application()

# Import WebSocket consumers after Django is set up
from content.consumers import ContentProcessingConsumer, ContentAnalyticsConsumer
from agents.consumers import AgentExecutionConsumer, AgentOrchestrationConsumer
from sports.consumers import SportsConsumer, OddsConsumer, GamesConsumer
from core.test_consumers import EchoTestConsumer
from core.consumers import (
    AgentProgressConsumer, SportsArbitrageConsumer, SportsDashboardConsumer,
    LiveSportsConsumer, AssistantChatConsumer, OrchestrationConsumer,
    AgentChannelsConsumer, NotificationConsumer, MythologyConsumer,
    ArbitrageConsumer, CommandCenterConsumer, OpportunityScannerConsumer
)

# WebSocket URL routing
websocket_urlpatterns = [
    # Test WebSocket (no auth required)
    path('ws/test/echo/', EchoTestConsumer.as_asgi()),

    # Command Center & Intelligence WebSockets
    path('ws/command-center/', CommandCenterConsumer.as_asgi()),
    path('ws/opportunity-scanner/', OpportunityScannerConsumer.as_asgi()),
    path('ws/intelligence/', CommandCenterConsumer.as_asgi()),
    path('ws/decisions/', CommandCenterConsumer.as_asgi()),
    path('ws/channels/', AgentChannelsConsumer.as_asgi()),

    # Content Management WebSockets
    path('ws/content/processing/', ContentProcessingConsumer.as_asgi()),
    path('ws/content/analytics/', ContentAnalyticsConsumer.as_asgi()),

    # Agent System WebSockets
    path('ws/agents/', AgentOrchestrationConsumer.as_asgi()),  # Main agents WebSocket endpoint
    path('ws/agents/execution/', AgentExecutionConsumer.as_asgi()),
    path('ws/agents/orchestration/', AgentOrchestrationConsumer.as_asgi()),
    path('ws/assistant/', AgentOrchestrationConsumer.as_asgi()),  # Generic assistant endpoint

    # Sports Analytics WebSockets
    path('ws/sports/', SportsConsumer.as_asgi()),
    path('ws/sports/odds/', OddsConsumer.as_asgi()),
    path('ws/sports/games/', GamesConsumer.as_asgi()),
    path('ws/sports/updates/', SportsConsumer.as_asgi()),
    path('ws/sports/arbitrage/', ArbitrageConsumer.as_asgi()),
    path('ws/sports/dashboard/', SportsDashboardConsumer.as_asgi()),
    path('ws/live-sports/', LiveSportsConsumer.as_asgi()),
]

# ASGI application with WebSocket support
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
