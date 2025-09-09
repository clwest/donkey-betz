"""
Sports Analytics WebSocket Routing

WebSocket URL routing for real-time sports data streaming.
"""

from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    # Game updates - real-time game scores and status
    re_path(r'ws/sports/games/(?P<game_id>[0-9a-f-]{36})/$', consumers.GameConsumer.as_asgi()),
    
    # Odds updates - real-time odds changes for specific markets
    re_path(r'ws/sports/odds/market/(?P<market_id>[0-9a-f-]{36})/$', consumers.OddsConsumer.as_asgi()),
    
    # Odds updates - real-time odds changes for all markets in a game
    re_path(r'ws/sports/odds/game/(?P<game_id>[0-9a-f-]{36})/$', consumers.OddsConsumer.as_asgi()),
    
    # Arbitrage alerts - real-time arbitrage opportunities
    path('ws/sports/arbitrage/', consumers.ArbitrageConsumer.as_asgi()),
    
    # Betting recommendations - personalized recommendations
    path('ws/sports/recommendations/', consumers.RecommendationConsumer.as_asgi()),
    
    # Dashboard updates - real-time dashboard data
    path('ws/sports/dashboard/', consumers.DashboardConsumer.as_asgi()),
]

"""
WebSocket Endpoints Documentation:

1. Game Updates: /ws/sports/games/{game_id}/
   - Real-time game score updates
   - Game status changes (live, final, postponed, etc.)
   - Live game statistics
   - Period/quarter updates
   
   Messages sent:
   - initial_data: Initial game information
   - game_update: Game status changes
   - score_update: Score changes
   - market_update: Related betting market updates
   
   Messages received:
   - subscribe_markets: Subscribe to betting markets for this game
   - ping: Heartbeat message

2. Odds Updates (Market): /ws/sports/odds/market/{market_id}/
   - Real-time odds changes for specific betting market
   - Line movements and alerts
   - Sportsbook-specific updates
   
   Messages sent:
   - initial_odds: Current odds for the market
   - odds_update: New odds posted
   - line_movement: Significant line movements
   
   Messages received:
   - subscribe_sportsbook: Subscribe to specific sportsbook
   - unsubscribe_sportsbook: Unsubscribe from sportsbook
   - ping: Heartbeat message

3. Odds Updates (Game): /ws/sports/odds/game/{game_id}/
   - Real-time odds changes for all markets in a game
   - Cross-market arbitrage detection
   - Comprehensive odds comparison
   
   Messages sent:
   - initial_game_odds: All current odds for game
   - odds_update: New odds across markets
   - line_movement: Line movements across markets
   
   Messages received:
   - subscribe_sportsbook: Filter by sportsbook
   - ping: Heartbeat message

4. Arbitrage Alerts: /ws/sports/arbitrage/
   - Real-time arbitrage opportunity alerts
   - Opportunity expiration notifications
   - Profit calculations and recommendations
   
   Messages sent:
   - initial_opportunities: Current arbitrage opportunities
   - arbitrage_alert: New opportunity detected
   - arbitrage_expired: Opportunity no longer available
   
   Messages received:
   - set_min_profit: Set minimum profit threshold
   - subscribe_sport: Filter by sport type
   - ping: Heartbeat message

5. Betting Recommendations: /ws/sports/recommendations/
   - Personalized betting recommendations
   - AI-generated value betting opportunities
   - Kelly Criterion bet sizing suggestions
   
   Messages sent:
   - initial_recommendations: Current active recommendations
   - new_recommendation: New recommendation generated
   - recommendation_expired: Recommendation expired
   
   Messages received:
   - request_recommendations: Request new recommendations
   - accept_recommendation: Accept a recommendation
   - reject_recommendation: Reject a recommendation
   - ping: Heartbeat message

6. Dashboard Updates: /ws/sports/dashboard/
   - Real-time dashboard metrics
   - User performance statistics
   - System-wide statistics and alerts
   
   Messages sent:
   - dashboard_summary: Current dashboard data
   - dashboard_update: Updated metrics
   
   Messages received:
   - refresh_dashboard: Request data refresh
   - ping: Heartbeat message

Authentication:
- All WebSocket connections require user authentication
- User context is available in consumers via self.user
- Failed authentication results in connection closure (code 4001)

Connection Management:
- Automatic group management for subscriptions
- Graceful disconnection handling
- Error reporting with specific error codes
- JSON encoding with Django serializer support

Message Format:
All messages follow this structure:
{
    "type": "message_type",
    "data": {...},
    "timestamp": "2023-XX-XX XX:XX:XX"
}

Error messages:
{
    "type": "error",
    "error_code": "error_type",
    "message": "Human readable message",
    "timestamp": "2023-XX-XX XX:XX:XX"
}

Heartbeat/Ping:
Clients should send periodic ping messages:
{"type": "ping"}

Server will respond with:
{"type": "pong", "timestamp": "2023-XX-XX XX:XX:XX"}
"""