"""
WebSocket routing configuration for unified-donkey-betz platform.
Migrated from DBAO tools-manifest WebSocket capabilities.
"""

from django.urls import re_path
from . import consumers
from . import orchestra_consumers

# Import sports routing if available
try:
    from sports.routing import websocket_urlpatterns as sports_ws_patterns
except ImportError:
    sports_ws_patterns = []

# Import intelligence routing for new UI components
try:
    from intelligence.routing import websocket_urlpatterns as intelligence_ws_patterns
except ImportError:
    intelligence_ws_patterns = []

websocket_urlpatterns = [
    # Test endpoints
    re_path(r'^ws/test/echo/$', consumers.TestEchoConsumer.as_asgi()),

    # Orchestra and Control Panel WebSockets
    re_path(r'^ws/orchestra/$', orchestra_consumers.OrchestraConsumer.as_asgi()),
    re_path(r'^ws/control/$', orchestra_consumers.ControlConsumer.as_asgi()),

    # Command Center & Intelligence WebSockets
    re_path(r'^ws/command-center/$', consumers.CommandCenterConsumer.as_asgi()),
    re_path(r'^ws/opportunity-scanner/$', consumers.OpportunityScannerConsumer.as_asgi()),
    re_path(r'^ws/intelligence/$', consumers.CommandCenterConsumer.as_asgi()),
    re_path(r'^ws/decisions/$', consumers.CommandCenterConsumer.as_asgi()),

    # Agent orchestration WebSocket (for orchestra frontend)
    re_path(r'^ws/agents/$', consumers.AgentProgressConsumer.as_asgi()),
    
    # Agent execution and orchestration endpoints
    re_path(r'^ws/agents/execution/$', consumers.AgentExecutionConsumer.as_asgi()),
    re_path(r'^ws/agents/orchestration/$', consumers.AgentOrchestrationConsumer.as_asgi()),
    
    # Agent progress monitoring (from DBAO tools-manifest)
    re_path(r'^ws/agent-progress/$', consumers.AgentProgressConsumer.as_asgi()),
    re_path(r'^ws/agent-progress/(?P<instance_id>[^/]+)/$', consumers.AgentProgressConsumer.as_asgi()),
    
    # Agent updates WebSocket
    re_path(r'^ws/agent-updates/$', consumers.AgentProgressConsumer.as_asgi()),
    
    # Content processing and analytics
    re_path(r'^ws/content/processing/$', consumers.ContentProcessingConsumer.as_asgi()),
    re_path(r'^ws/content/analytics/$', consumers.ContentAnalyticsConsumer.as_asgi()),
    
    # Dashboard real-time updates (from DBAO tools-manifest)
    re_path(r'^ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
    
    # Live sports and betting updates
    re_path(r'^ws/live-sports/$', consumers.LiveSportsConsumer.as_asgi()),
    re_path(r'^ws/arbitrage/$', consumers.ArbitrageConsumer.as_asgi()),

    # Sports real-time updates and force refresh
    re_path(r'^ws/sports/updates/$', consumers.SportsUpdatesConsumer.as_asgi()),
    
    # Assistant chat WebSocket (from ai-content-studio)
    re_path(r'^ws/assistant/$', consumers.AssistantChatConsumer.as_asgi()),
    
    # Multi-agent orchestration updates
    re_path(r'^ws/orchestration/(?P<orchestration_id>[^/]+)/$', consumers.OrchestrationConsumer.as_asgi()),
    
    # Agent Channels - "Slack for AI Agents" (integrated from donkey_betz)
    re_path(r'^ws/channels/$', consumers.AgentChannelsConsumer.as_asgi()),
    re_path(r'^ws/channels/(?P<channel_id>[^/]+)/$', consumers.AgentChannelsConsumer.as_asgi()),
    
    # System notifications and alerts
    re_path(r'^ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    
    # Mythology/Content Review notifications
    re_path(r'^ws/mythology/$', consumers.MythologyConsumer.as_asgi()),
]

# Add sports WebSocket patterns if available
websocket_urlpatterns.extend(sports_ws_patterns)

# Add intelligence WebSocket patterns for new UI components
websocket_urlpatterns.extend(intelligence_ws_patterns)