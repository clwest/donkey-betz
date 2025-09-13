"""
WebSocket routing for sports app real-time updates
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/sports/$', consumers.SportsConsumer.as_asgi()),
    re_path(r'^ws/sports/odds/$', consumers.OddsConsumer.as_asgi()),
    re_path(r'^ws/sports/games/$', consumers.GamesConsumer.as_asgi()),
]
