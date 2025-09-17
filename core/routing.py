"""
WebSocket routing configuration for unified-donkey-betz platform.
Migrated from DBAO tools-manifest WebSocket capabilities.
"""

import json
from django.urls import re_path
from channels.db import database_sync_to_async
from . import consumers
from . import orchestra_consumers
from .unified_hub import UnifiedWebSocketHub

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
    re_path(r'^ws/orchestra/$', orchestra_consumers.NeuralOrchestraConsumer.as_asgi()),
    re_path(r'^ws/neural-orchestra/$', UnifiedWebSocketHub.as_asgi()),
    re_path(r'^ws/control/$', orchestra_consumers.ControlConsumer.as_asgi()),

    # Command Center & Intelligence WebSockets
    re_path(r'^ws/command-center/$', consumers.CommandCenterConsumer.as_asgi()),
    re_path(r'^ws/opportunity-scanner/$', consumers.OpportunityScannerConsumer.as_asgi()),
    re_path(r'^ws/intelligence/$', consumers.CommandCenterConsumer.as_asgi()),
    re_path(r'^ws/decisions/$', consumers.CommandCenterConsumer.as_asgi()),
    re_path(r'^ws/decision/$', consumers.CommandCenterConsumer.as_asgi()),  # Add singular route

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

# Reality Checking WebSocket Consumer
class RealityCheckConsumer(UnifiedWebSocketHub):
    """Specialized consumer for reality checking and system monitoring"""

    async def connect(self):
        self.component_type = 'reality_checker'
        await super().connect()

        # Send initial reality status
        await self.send_reality_status()

    async def receive(self, text_data):
        """Handle reality checking specific messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'reality_check_all':
                await self.send_reality_status()
            elif message_type == 'trace_data_flow':
                flow_type = data.get('flow_type', 'opportunity_pipeline')
                await self.trace_data_flow(flow_type)
            elif message_type == 'get_dashboard_data':
                await self.send_dashboard_data()
            else:
                await super().receive(text_data)

        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Reality check error: {str(e)}'
            }))

    async def trace_data_flow(self, flow_type):
        """Initiate data flow tracing"""
        from .data_flow_tracer import data_flow_tracer, FlowType

        flow_map = {
            'opportunity_pipeline': FlowType.OPPORTUNITY_PIPELINE,
            'revenue_pipeline': FlowType.REVENUE_PIPELINE,
            'websocket_pipeline': FlowType.WEBSOCKET_PIPELINE
        }

        if flow_type in flow_map:
            # Start a test trace
            test_data = {'id': 'reality_check_trace', 'type': 'test'}

            if flow_type == 'opportunity_pipeline':
                trace_id = data_flow_tracer.trace_opportunity_pipeline(test_data)
            elif flow_type == 'revenue_pipeline':
                trace_id = data_flow_tracer.trace_revenue_pipeline(test_data)
            else:
                trace_id = data_flow_tracer.trace_websocket_pipeline(test_data, 'income_builder')

            # Get completed trace
            completed_trace = data_flow_tracer.get_trace_by_id(trace_id)

            await self.send(text_data=json.dumps({
                'type': 'trace_completed',
                'flow_type': flow_type,
                'trace_id': trace_id,
                'success': completed_trace.success if completed_trace else False,
                'processing_time_ms': completed_trace.total_processing_time_ms if completed_trace else 0,
                'stages_completed': len(completed_trace.trace_points) if completed_trace else 0
            }))

    async def send_dashboard_data(self):
        """Send truth dashboard data"""
        from .truth_dashboard import truth_dashboard

        try:
            dashboard_data = await database_sync_to_async(truth_dashboard.generate_dashboard_data)()

            await self.send(text_data=json.dumps({
                'type': 'dashboard_data',
                'data': dashboard_data
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Dashboard data error: {str(e)}'
            }))

# Production WebSocket endpoints with enhanced reliability
from .production_websocket import ProductionRevenueConsumer
from .revenue_dashboard_consumer import RevenueDashboardConsumer

unified_endpoints = [
    # Production Revenue Dashboard with real-time updates
    re_path(r'^ws/revenue-dashboard/$', RevenueDashboardConsumer.as_asgi()),
    re_path(r'^ws/revenue/$', RevenueDashboardConsumer.as_asgi()),

    # Fallback to production consumer
    re_path(r'^ws/revenue-production/$', ProductionRevenueConsumer.as_asgi()),

    # Other component endpoints (will upgrade to production one by one)
    re_path(r'^ws/income-builder/$', UnifiedWebSocketHub.as_asgi()),
    re_path(r'^ws/decision-command/$', UnifiedWebSocketHub.as_asgi()),
    # Neural Orchestra uses dedicated consumer - see line 28
    re_path(r'^ws/control-center/$', UnifiedWebSocketHub.as_asgi()),
    re_path(r'^ws/revenue-opportunities/$', UnifiedWebSocketHub.as_asgi()),
    re_path(r'^ws/monetization-hub/$', UnifiedWebSocketHub.as_asgi()),

    # Alternative paths for component access
    re_path(r'^ws/decision/$', UnifiedWebSocketHub.as_asgi()),
    re_path(r'^ws/orchestra/$', UnifiedWebSocketHub.as_asgi()),
    re_path(r'^ws/control/$', UnifiedWebSocketHub.as_asgi()),
    re_path(r'^ws/opportunities/$', UnifiedWebSocketHub.as_asgi()),
    re_path(r'^ws/monetization/$', UnifiedWebSocketHub.as_asgi()),

    # Legacy bridge endpoints (fallback)
    re_path(r'^ws/bridge/income-builder/$', UnifiedWebSocketHub.as_asgi()),
    re_path(r'^ws/bridge/revenue/$', ProductionRevenueConsumer.as_asgi()),
    re_path(r'^ws/bridge/decision/$', UnifiedWebSocketHub.as_asgi()),
    re_path(r'^ws/bridge/orchestra/$', UnifiedWebSocketHub.as_asgi()),

    # Reality Checking and System Monitoring
    re_path(r'^ws/reality-check/$', RealityCheckConsumer.as_asgi()),
    re_path(r'^ws/truth-dashboard/$', RealityCheckConsumer.as_asgi()),
    re_path(r'^ws/system-monitor/$', RealityCheckConsumer.as_asgi()),
]

# Platform Unification Orchestrator endpoints
from .platform_unification_orchestrator import PlatformUnificationConsumer

unification_endpoints = [
    # Platform Unification Control
    re_path(r'^ws/platform-orchestrator/$', PlatformUnificationConsumer.as_asgi()),
    re_path(r'^ws/unified-platform/$', PlatformUnificationConsumer.as_asgi()),

    # Content-Intelligence Pipeline
    re_path(r'^ws/content-intelligence-pipeline/$', PlatformUnificationConsumer.as_asgi()),
    re_path(r'^ws/spider-content-feed/$', PlatformUnificationConsumer.as_asgi()),

    # Agent Content Factory
    re_path(r'^ws/agent-content-factory/$', PlatformUnificationConsumer.as_asgi()),
    re_path(r'^ws/content-workflow-monitor/$', PlatformUnificationConsumer.as_asgi()),

    # Advisor Content Streams
    re_path(r'^ws/advisor-content-streams/$', PlatformUnificationConsumer.as_asgi()),
    re_path(r'^ws/expert-consultation-updates/$', PlatformUnificationConsumer.as_asgi()),

    # Semantic Search Interface
    re_path(r'^ws/semantic-search/$', PlatformUnificationConsumer.as_asgi()),
    re_path(r'^ws/knowledge-discovery/$', PlatformUnificationConsumer.as_asgi()),

    # Revenue Pipeline Monitoring
    re_path(r'^ws/revenue-pipeline-monitor/$', PlatformUnificationConsumer.as_asgi()),
    re_path(r'^ws/content-monetization-tracker/$', PlatformUnificationConsumer.as_asgi()),
]

# Add unified platform endpoints
websocket_urlpatterns.extend(unified_endpoints)

# Add platform unification endpoints
websocket_urlpatterns.extend(unification_endpoints)