"""
WebSocket Consumers Package - Session 714/715

This package contains WebSocket consumers for real-time communication.
Re-exports all consumers from consumers_base.py for backward compatibility.
"""

# Session 714: New SystemEventsConsumer
from .system_events_consumer import (
    SystemEventsConsumer,
    emit_system_event,
    emit_system_event_sync,
)

# Re-export all consumers from consumers_base.py (the original consumers.py)
from core.consumers_base import (
    SafeWebSocketMixin,
    AgentProgressConsumer,
    DashboardConsumer,
    LiveSportsConsumer,
    ArbitrageConsumer,
    AssistantChatConsumer,
    OrchestrationConsumer,
    NotificationConsumer,
    AgentChannelsConsumer,
    TestEchoConsumer,
    ContentProcessingConsumer,
    ContentAnalyticsConsumer,
    AgentExecutionConsumer,
    AgentOrchestrationConsumer,
    MythologyConsumer,
    SportsArbitrageConsumer,
    SportsRecommendationConsumer,
    CommandCenterConsumer,
    CommandCenterConsumerLegacy,
    OpportunityScannerConsumer,
    SportsDashboardConsumer,
    NeuralOrchestraConsumer,
    RealAgentOrchestraConsumer,
    AutonomousSystemConsumer,
)

__all__ = [
    # Session 714: System Events
    'SystemEventsConsumer',
    'emit_system_event',
    'emit_system_event_sync',
    # Original consumers from consumers_base.py
    'SafeWebSocketMixin',
    'AgentProgressConsumer',
    'DashboardConsumer',
    'LiveSportsConsumer',
    'ArbitrageConsumer',
    'AssistantChatConsumer',
    'OrchestrationConsumer',
    'NotificationConsumer',
    'AgentChannelsConsumer',
    'TestEchoConsumer',
    'ContentProcessingConsumer',
    'ContentAnalyticsConsumer',
    'AgentExecutionConsumer',
    'AgentOrchestrationConsumer',
    'MythologyConsumer',
    'SportsArbitrageConsumer',
    'SportsRecommendationConsumer',
    'CommandCenterConsumer',
    'CommandCenterConsumerLegacy',
    'OpportunityScannerConsumer',
    'SportsDashboardConsumer',
    'NeuralOrchestraConsumer',
    'RealAgentOrchestraConsumer',
    'AutonomousSystemConsumer',
]
