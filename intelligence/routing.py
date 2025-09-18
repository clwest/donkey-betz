"""
WebSocket routing for Intelligence module
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Commented out - using UnifiedWebSocketHub instead
    # re_path(r'^ws/income-builder/$', consumers.IncomeBuilderConsumer.as_asgi()),
    re_path(r'^ws/revenue-income/$', consumers.RevenueIncomeConsumer.as_asgi()),
]