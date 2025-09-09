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
from sports.consumers import GameConsumer, OddsConsumer, ArbitrageConsumer, RecommendationConsumer, DashboardConsumer
from core.test_consumers import EchoTestConsumer

# WebSocket URL routing
websocket_urlpatterns = [
    # Test WebSocket (no auth required)
    path('ws/test/echo/', EchoTestConsumer.as_asgi()),
    
    # Content Management WebSockets
    path('ws/content/processing/', ContentProcessingConsumer.as_asgi()),
    path('ws/content/analytics/', ContentAnalyticsConsumer.as_asgi()),
    
    # Agent System WebSockets
    path('ws/agents/execution/', AgentExecutionConsumer.as_asgi()),
    path('ws/agents/orchestration/', AgentOrchestrationConsumer.as_asgi()),
    
    # Sports Analytics WebSockets
    path('ws/sports/games/<uuid:game_id>/', GameConsumer.as_asgi()),
    path('ws/sports/odds/market/<uuid:market_id>/', OddsConsumer.as_asgi()),
    path('ws/sports/odds/game/<uuid:game_id>/', OddsConsumer.as_asgi()),
    path('ws/sports/arbitrage/', ArbitrageConsumer.as_asgi()),
    path('ws/sports/recommendations/', RecommendationConsumer.as_asgi()),
    path('ws/sports/dashboard/', DashboardConsumer.as_asgi()),
]

# ASGI application with WebSocket support
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
