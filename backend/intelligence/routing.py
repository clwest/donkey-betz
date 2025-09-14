"""
WebSocket URL routing for Intelligence System
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/decision/$', consumers.DecisionCommandConsumer.as_asgi()),
    re_path(r'ws/orchestra/$', consumers.NeuralOrchestraConsumer.as_asgi()),
    re_path(r'ws/control/$', consumers.ControlCenterConsumer.as_asgi()),
]