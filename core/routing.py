"""
WebSocket routing configuration for unified-donkey-betz platform.
Migrated from DBAO tools-manifest WebSocket capabilities.
"""

import json
from django.urls import re_path
from channels.db import database_sync_to_async
from . import consumers
from . import consumers_sports
from . import consumers_hallucination
from . import orchestra_consumers
from .unified_hub import UnifiedWebSocketHub
from . import generic_consumer
from .agent_platform_consumer import AgentPlatformConsumer
from .decision_command_consumer import DecisionCommandConsumer
from .real_job_execution_consumer import RealJobExecutionConsumer
from .project_progress_consumer import ProjectProgressConsumer, AllProjectsConsumer
from .agent_monitor_consumer_simple import AgentMonitorConsumer
from .deliverables_consumer import DeliverablesConsumer
from .freelance_consumer import FreelanceConsumer
from .consumers_ai_training import AITrainingConsumer
from .consumers_consciousness import ConsciousnessConsumer
from .command_center_ai import CommandCenterAIConsumer

# Import V2 consumers for new unified UI
from .consumers_unified_v2 import PersonalAssistantConsumer as PersonalAssistantV2Consumer
from .consumers_pa_conversation import PAConversationConsumer

# Import consumers from intelligence app
from intelligence.consumers import IncomeBuilderConsumer

# Import SpiderWebSocketConsumer properly
try:
    from ai_core.api.spider_websocket import SpiderWebSocketConsumer
except ImportError:
    SpiderWebSocketConsumer = None

# Import sports routing if available
try:
    from sports.routing import websocket_urlpatterns as sports_ws_patterns
except ImportError:
    sports_ws_patterns = []

# Import intelligence routing for new UI components
try:
    from ai_core.intelligence.routing import websocket_urlpatterns as intelligence_ws_patterns
except ImportError:
    intelligence_ws_patterns = []

websocket_urlpatterns = [
    # Generic WebSocket endpoint for basic connections
    re_path(r'^ws/$', generic_consumer.GenericWebSocketConsumer.as_asgi()),

    # Activity Stream WebSocket for real-time agent activity
    re_path(r'^ws/activity/$', consumers.AgentProgressConsumer.as_asgi()),

    # AI Training WebSocket for learning updates
    re_path(r'^ws/ai-training/$', AITrainingConsumer.as_asgi()),

    # Consciousness Stream WebSocket for real-time self-awareness updates
    re_path(r'^ws/consciousness/$', ConsciousnessConsumer.as_asgi()),
    re_path(r'^ws/unified-intelligence/$', ConsciousnessConsumer.as_asgi()),

    # Spider Dashboard WebSocket for real-time updates
    re_path(r'^ws/spider-updates/$', SpiderWebSocketConsumer.as_asgi() if SpiderWebSocketConsumer else consumers.AgentProgressConsumer.as_asgi()),

    # Freelance Opportunities WebSocket for real-time updates
    re_path(r'^ws/freelance/$', FreelanceConsumer.as_asgi()),

    # Agent Work Platform WebSocket - Real money-making system!
    re_path(r'^ws/agent-platform/$', AgentPlatformConsumer.as_asgi()),

    # 152 Agent Army Monitor WebSocket - Real agent status monitoring
    re_path(r'^ws/agent-monitor/$', AgentMonitorConsumer.as_asgi()),

    # Live Deliverables WebSocket - Real deliverable tracking
    re_path(r'^ws/deliverables/$', DeliverablesConsumer.as_asgi()),

    # Autonomous Revenue System WebSocket - 30-day autonomous run!
    re_path(r'^ws/autonomous-system/$', consumers.AutonomousSystemConsumer.as_asgi()),

    # Test endpoints
    re_path(r'^ws/test/echo/$', consumers.TestEchoConsumer.as_asgi()),

    # Orchestra and Control Panel WebSockets
    re_path(r'^ws/orchestra/$', orchestra_consumers.NeuralOrchestraConsumer.as_asgi()),
    re_path(r'^ws/neural-orchestra/$', orchestra_consumers.NeuralOrchestraConsumer.as_asgi()),
    re_path(r'^ws/enhanced-neural-orchestra/$', consumers.NeuralOrchestraConsumer.as_asgi()),
    re_path(r'^ws/control/$', orchestra_consumers.ControlConsumer.as_asgi()),

    # Command Center & Intelligence WebSockets - Enhanced with AI
    re_path(r'^ws/command-center/$', CommandCenterAIConsumer.as_asgi()),
    re_path(r'^ws/command-center-ai/$', CommandCenterAIConsumer.as_asgi()),  # AI-enhanced route
    re_path(r'^ws/opportunity-scanner/$', consumers.OpportunityScannerConsumer.as_asgi()),
    re_path(r'^ws/intelligence/$', consumers.CommandCenterConsumer.as_asgi()),
    re_path(r'^ws/decisions/$', consumers.CommandCenterConsumer.as_asgi()),
    re_path(r'^ws/decision/$', consumers.CommandCenterConsumer.as_asgi()),  # Add singular route

    # Real Decision Command WebSocket
    re_path(r'^ws/decision-command/$', DecisionCommandConsumer.as_asgi()),

    # Real Job Execution WebSocket - for recording and portfolio generation
    re_path(r'^ws/real-job-execution/$', RealJobExecutionConsumer.as_asgi()),

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
    re_path(r'^ws/sports/updates/$', consumers_sports.SportsUpdatesConsumer.as_asgi()),
    
    # PA Conversation WebSocket — real-time 3-way chat (User + Claude Code + Rigby)
    re_path(r'^ws/pa/conversations/(?P<conversation_id>[^/]+)/$', PAConversationConsumer.as_asgi()),

    # Assistant chat WebSocket (V2 - new unified UI)
    re_path(r'^ws/assistant/$', PersonalAssistantV2Consumer.as_asgi()),

    # Enhanced AI Assistant with full personalization
    re_path(r'^ws/ai-assistant/$', consumers.AssistantChatConsumer.as_asgi()),

    # Personal Assistant Interview WebSocket
    re_path(r'^ws/interview/$', consumers.AssistantChatConsumer.as_asgi()),
    
    # Multi-agent orchestration updates
    re_path(r'^ws/orchestration/(?P<orchestration_id>[^/]+)/$', consumers.OrchestrationConsumer.as_asgi()),
    
    # Agent Channels - "Slack for AI Agents" (integrated from donkey_betz)
    re_path(r'^ws/channels/$', consumers.AgentChannelsConsumer.as_asgi()),
    re_path(r'^ws/channels/(?P<channel_id>[^/]+)/$', consumers.AgentChannelsConsumer.as_asgi()),
    
    # System notifications and alerts
    re_path(r'^ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
    
    # Mythology/Content Review notifications
    re_path(r'^ws/mythology/$', consumers.MythologyConsumer.as_asgi()),

    # Hallucination Monitor WebSocket for real-time blocking display
    re_path(r'^ws/hallucination-monitor/$', consumers_hallucination.HallucinationMonitorConsumer.as_asgi()),

    # Project Progress WebSocket for real-time agent work tracking
    re_path(r'^ws/project-progress/(?P<project_id>[^/]+)/$', ProjectProgressConsumer.as_asgi()),
    re_path(r'^ws/all-projects/$', AllProjectsConsumer.as_asgi()),

    # Real Agent Orchestra WebSocket for live project building activity
    re_path(r'^ws/real-agent-orchestra/$', consumers.RealAgentOrchestraConsumer.as_asgi()),
    re_path(r'^ws/build-activity/$', consumers.RealAgentOrchestraConsumer.as_asgi()),

]

# Import new WebSocket consumers
from core.revenue_opportunities_consumer import RevenueOpportunitiesConsumer
from core.monetization_hub_consumer import MonetizationHubConsumer
from core.control_center_consumer import ControlCenterConsumer
from core.learning_dashboard_consumer import LearningDashboardConsumer

# Add new template WebSocket patterns
new_template_patterns = [
    re_path(r'^ws/revenue-opportunities/$', RevenueOpportunitiesConsumer.as_asgi()),
    re_path(r'^ws/monetization-hub/$', MonetizationHubConsumer.as_asgi()),
    re_path(r'^ws/control-center/$', ControlCenterConsumer.as_asgi()),
    re_path(r'^ws/learning-dashboard/$', LearningDashboardConsumer.as_asgi()),
]

websocket_urlpatterns.extend(new_template_patterns)

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
    # Income Builder - uses dedicated consumer with opportunity loading
    re_path(r'^ws/income-builder/$', IncomeBuilderConsumer.as_asgi()),
    # re_path(r'^ws/decision-command/$', UnifiedWebSocketHub.as_asgi()),  # Already defined above
    # Neural Orchestra uses dedicated consumer - see line 28
    # re_path(r'^ws/control-center/$', UnifiedWebSocketHub.as_asgi()),  # Already defined above
    # re_path(r'^ws/revenue-opportunities/$', UnifiedWebSocketHub.as_asgi()),  # Already defined above
    # re_path(r'^ws/monetization-hub/$', UnifiedWebSocketHub.as_asgi()),  # Already defined above
    re_path(r'^ws/diagnostic/$', UnifiedWebSocketHub.as_asgi()),  # Added for diagnostic dashboard

    # Alternative paths for component access
    re_path(r'^ws/decision/$', UnifiedWebSocketHub.as_asgi()),
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

# Import new page consumers
from .sports_consumer import SportsConsumer
from .personal_assistant_consumer import PersonalAssistantConsumer
from .new_pages_consumer import NewPagesConsumer

# Add new page WebSocket patterns
new_page_patterns = [
    # Sports WebSocket endpoints
    re_path(r'^ws/sports/$', SportsConsumer.as_asgi()),
    re_path(r'^ws/sports-hub/$', SportsConsumer.as_asgi()),

    # Personal Assistant WebSocket endpoint (override generic one)
    re_path(r'^ws/personal-assistant/$', PersonalAssistantConsumer.as_asgi()),

    # AI Nexus WebSocket endpoint
    re_path(r'^ws/ai-nexus/$', NewPagesConsumer.as_asgi()),

    # DBAO Dashboard WebSocket endpoint
    re_path(r'^ws/dbao/$', NewPagesConsumer.as_asgi()),
    re_path(r'^ws/dbao-dashboard/$', NewPagesConsumer.as_asgi()),

    # Profile WebSocket endpoint
    re_path(r'^ws/profile/$', NewPagesConsumer.as_asgi()),
]

websocket_urlpatterns.extend(new_page_patterns)

# Session 220: Real-Time Collaboration WebSocket
from .consumers_collaboration import CollaborationConsumer

collaboration_patterns = [
    # Project collaboration WebSocket - join with project_id
    re_path(r'^ws/collaboration/(?P<project_id>[^/]+)/$', CollaborationConsumer.as_asgi()),
    re_path(r'^ws/collab/(?P<project_id>[^/]+)/$', CollaborationConsumer.as_asgi()),
]

websocket_urlpatterns.extend(collaboration_patterns)

# Session 244: Agent Conversations WebSocket - Real-time agent chat streaming
from .agent_conversation_consumer import AgentConversationConsumer

agent_conversation_patterns = [
    # Agent conversations WebSocket - stream live agent chat
    re_path(r'^ws/agent-conversations/$', AgentConversationConsumer.as_asgi()),
    re_path(r'^ws/agent-chat/$', AgentConversationConsumer.as_asgi()),
]

websocket_urlpatterns.extend(agent_conversation_patterns)

# Session 250: Hive Mind Mode WebSocket - Real-time collective intelligence
from .hive_mind_consumer import HiveMindConsumer

hive_mind_patterns = [
    # Hive Mind WebSocket - stream live agent contributions
    re_path(r'^ws/hive-mind/$', HiveMindConsumer.as_asgi()),
    re_path(r'^ws/collective-intelligence/$', HiveMindConsumer.as_asgi()),
]

websocket_urlpatterns.extend(hive_mind_patterns)

# Session 319: Agent Slack WebSocket - Multi-agent channel communication
from .agent_slack_consumer import AgentSlackConsumer

agent_slack_patterns = [
    # Agent Slack WebSocket - Slack-like channels for agents
    re_path(r'^ws/agent-slack/$', AgentSlackConsumer.as_asgi()),
    re_path(r'^ws/agent-slack/(?P<channel_id>[^/]+)/$', AgentSlackConsumer.as_asgi()),
    re_path(r'^ws/agent-workspace/$', AgentSlackConsumer.as_asgi()),
]

websocket_urlpatterns.extend(agent_slack_patterns)

# Session 324: Learning Feed WebSocket - Real-time agent learning activity
from .learning_feed_consumer import LearningFeedConsumer
from .pipeline_progress_consumer import PipelineProgressConsumer

learning_feed_patterns = [
    # Learning Feed WebSocket - stream live learning events
    re_path(r'^ws/learning-feed/$', LearningFeedConsumer.as_asgi()),
    re_path(r'^ws/agent-learning/$', LearningFeedConsumer.as_asgi()),
]

websocket_urlpatterns.extend(learning_feed_patterns)

# Session 342: Pipeline Progress WebSocket - Real-time pipeline visualization
pipeline_progress_patterns = [
    # Pipeline Progress WebSocket - stream live pipeline stage updates
    re_path(r'^ws/pipeline-progress/$', PipelineProgressConsumer.as_asgi()),
    re_path(r'^ws/pipeline/$', PipelineProgressConsumer.as_asgi()),
]

websocket_urlpatterns.extend(pipeline_progress_patterns)

# Session 332: Project Intelligence Hub WebSocket - Real-time updates for all tabs
from .project_intelligence_consumer import ProjectIntelligenceConsumer

project_intelligence_patterns = [
    # Unified Project Intelligence WebSocket - all tabs (learning, conversations, dreams, boardroom)
    re_path(r'^ws/project-intelligence/(?P<project_id>[^/]+)/$', ProjectIntelligenceConsumer.as_asgi()),
    # Legacy route for backward compatibility
    re_path(r'^ws/project-conversations/(?P<project_id>[^/]+)/$', ProjectIntelligenceConsumer.as_asgi()),
]

websocket_urlpatterns.extend(project_intelligence_patterns)

# Session 714: System Events WebSocket - Real-time event broadcasting across all pages
from .consumers.system_events_consumer import SystemEventsConsumer

system_events_patterns = [
    # System Events WebSocket - broadcast events to all connected clients
    re_path(r'^ws/system-events/$', SystemEventsConsumer.as_asgi()),
]

websocket_urlpatterns.extend(system_events_patterns)

# Session 794: Agent Collaboration Monitor WebSocket - Real-time collaboration tracking
from .consumers_agent_collaboration import AgentCollaborationMonitorConsumer

agent_collaboration_patterns = [
    # Agent collaboration monitor WebSocket - live collaboration updates for all 213 agents
    re_path(r'^ws/agent-collaboration/$', AgentCollaborationMonitorConsumer.as_asgi()),
    re_path(r'^ws/agent-collab-monitor/$', AgentCollaborationMonitorConsumer.as_asgi()),
    re_path(r'^ws/collaboration-monitor/$', AgentCollaborationMonitorConsumer.as_asgi()),
]

websocket_urlpatterns.extend(agent_collaboration_patterns)
