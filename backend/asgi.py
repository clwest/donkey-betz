"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# Now import WebSocket-related code
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from core.routing import websocket_urlpatterns
from core.websocket_auth import TokenAuthMiddlewareStack
from django.urls import re_path

# Import consumers directly to ensure MythologyConsumer is available
from core import consumers

# Make absolutely sure mythology route is included
mythology_route = re_path(r'^ws/mythology/$', consumers.MythologyConsumer.as_asgi())
if mythology_route not in websocket_urlpatterns:
    websocket_urlpatterns.append(mythology_route)

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests
    "http": django_asgi_app,

    # WebSocket chat handler with token auth support
    "websocket": TokenAuthMiddlewareStack(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
