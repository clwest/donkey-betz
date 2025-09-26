"""
WebSocket URL routing configuration
Updated: 9/26/25 11:55 AM MST
"""

from django.urls import re_path
from backend.consumers.build_activity_consumer import BuildActivityConsumer

websocket_urlpatterns = [
    re_path(r'ws/build-activity/$', BuildActivityConsumer.as_asgi()),
]