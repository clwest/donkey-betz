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
from django.urls import path

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Initialize Django ASGI application early
django_asgi_app = get_asgi_application()

# Import WebSocket routing configuration
# This imports all the WebSocket URL patterns including the bridges and new UI components
from core.routing import websocket_urlpatterns
from core.ws_auth_middleware import TokenAuthMiddlewareStack

# ASGI application with WebSocket support
application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
