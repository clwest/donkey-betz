"""
WebSocket URL routing configuration
Updated: 9/26/25 11:55 AM MST
"""

from django.urls import re_path
from ai_core.consumers.build_activity_consumer import BuildActivityConsumer
from sports_betting.consumers import SportsBettingConsumer
from core.consumers_consciousness import ConsciousnessConsumer

websocket_urlpatterns = [
    re_path(r'ws/build-activity/$', BuildActivityConsumer.as_asgi()),
    re_path(r'ws/sports-betting/$', SportsBettingConsumer.as_asgi()),
    re_path(r'ws/unified-intelligence/$', ConsciousnessConsumer.as_asgi()),
]