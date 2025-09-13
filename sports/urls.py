"""
Sports Analytics API URLs

Comprehensive URL routing for sports betting analytics, odds management,
betting recommendations, and real-time data endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    LeagueViewSet, TeamViewSet, GameViewSet, SportsbookViewSet,
    BettingMarketViewSet, BetViewSet, ArbitrageOpportunityViewSet,
    BettingRecommendationViewSet, SportsAnalyticsViewSet,
    SportsUtilityViewSet
)
from .dashboard_views import (
    SportsDashboardView, dashboard_metrics, arbitrage_dashboard,
    recommendations_dashboard, market_overview
)

# Import enhanced multi-sport endpoints
from core.views_odds_sports import (
    sports_summary, sports_leagues, sports_teams, sports_games,
    sports_games_trending, sports_sync, live_odds
)

# Create router for ViewSets
router = DefaultRouter()

# Register ViewSets
router.register(r'leagues', LeagueViewSet, basename='league')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'games', GameViewSet, basename='game')
router.register(r'sportsbooks', SportsbookViewSet, basename='sportsbook')
router.register(r'markets', BettingMarketViewSet, basename='bettingmarket')
router.register(r'bets', BetViewSet, basename='bet')
router.register(r'arbitrage', ArbitrageOpportunityViewSet, basename='arbitrageopportunity')
router.register(r'recommendations', BettingRecommendationViewSet, basename='bettingrecommendation')
router.register(r'analytics', SportsAnalyticsViewSet, basename='sportsanalytics')
router.register(r'utils', SportsUtilityViewSet, basename='sportsutility')

app_name = 'sports'

urlpatterns = [
    # Dashboard views (no API prefix here as it's added in main urls.py)
    path('dashboard/', SportsDashboardView.as_view(), name='sports-dashboard'),
    
    # Dashboard API endpoints (prefix removed as it's added in main urls.py)
    path('dashboard/metrics/', dashboard_metrics, name='dashboard-metrics'),
    path('dashboard/arbitrage/', arbitrage_dashboard, name='dashboard-arbitrage'),
    path('dashboard/recommendations/', recommendations_dashboard, name='dashboard-recommendations'),
    path('dashboard/market/', market_overview, name='dashboard-market'),
    
    # Enhanced Multi-Sport API Endpoints
    path('summary/', sports_summary, name='sports-summary'),
    path('leagues/', sports_leagues, name='sports-leagues'),  
    path('teams/', sports_teams, name='sports-teams'),
    path('games/', sports_games, name='sports-games'),
    path('games/trending/', sports_games_trending, name='sports-games-trending'),
    path('sync/', sports_sync, name='sports-sync'),
    path('odds/live/', live_odds, name='live-odds'),
    
    # Main API router (prefix removed as it's added in main urls.py)
    path('', include(router.urls)),
    
    # Additional custom endpoints could be added here
    # path('custom-endpoint/', custom_view, name='custom-endpoint'),
]

"""
API Endpoints Overview:

Base URL: /api/v1/sports/

Leagues:
- GET /leagues/ - List all leagues
- GET /leagues/{id}/ - Get specific league
- GET /leagues/{id}/standings/ - Get league standings
- GET /leagues/{id}/betting_trends/ - Get betting trends

Teams:
- GET /teams/ - List all teams
- GET /teams/{id}/ - Get specific team
- GET /teams/{id}/betting_analytics/ - Get team betting analytics

Games:
- GET /games/ - List games (filterable by date, league, etc.)
- GET /games/{id}/ - Get specific game
- GET /games/{id}/odds/ - Get game odds from all sportsbooks
- GET /games/{id}/line_movements/ - Get line movement history
- GET /games/{id}/analytics/ - Get comprehensive game analytics

Sportsbooks:
- GET /sportsbooks/ - List all sportsbooks
- GET /sportsbooks/{id}/ - Get specific sportsbook
- GET /sportsbooks/odds_comparison/ - Compare odds across books

Markets:
- GET /markets/ - List betting markets
- GET /markets/{id}/ - Get specific market
- GET /markets/{id}/analysis/ - Get market analysis

Bets:
- GET /bets/ - List user's bets
- POST /bets/ - Place new bet
- GET /bets/{id}/ - Get specific bet
- PUT /bets/{id}/ - Update bet
- DELETE /bets/{id}/ - Cancel bet
- GET /bets/stats/ - Get user betting statistics

Arbitrage:
- GET /arbitrage/ - List arbitrage opportunities
- GET /arbitrage/{id}/ - Get specific opportunity
- POST /arbitrage/scan/ - Trigger arbitrage scan

Recommendations:
- GET /recommendations/ - List user recommendations
- GET /recommendations/{id}/ - Get specific recommendation
- POST /recommendations/generate/ - Generate new recommendations
- POST /recommendations/{id}/accept/ - Accept recommendation
- POST /recommendations/{id}/reject/ - Reject recommendation

Analytics:
- GET /analytics/ - List analytics
- GET /analytics/{id}/ - Get specific analytics
- POST /analytics/generate/ - Generate new analytics

Utilities:
- GET /utils/summary/ - Get sports data summary
- POST /utils/update_odds/ - Trigger odds update

Query Parameters:
- page: Page number for pagination
- page_size: Items per page (max 100)
- ordering: Sort by field (prefix with - for descending)
- search: Search term for searchable fields
- Various filters per endpoint (league, team, status, etc.)

Date Filtering (for games):
- date_from: Start date (YYYY-MM-DD)
- date_to: End date (YYYY-MM-DD)
- today: true/false for today's games
- this_week: true/false for this week's games

Authentication:
- All endpoints require authentication
- User-specific endpoints (bets, recommendations) filter by authenticated user
- Rate limiting applied per user/IP

Response Format:
- All responses are JSON
- Paginated endpoints include: count, next, previous, results
- Error responses include: error message and appropriate HTTP status codes

WebSocket Endpoints (for real-time data):
- /ws/sports/odds/{game_id}/ - Real-time odds updates
- /ws/sports/lines/{market_id}/ - Real-time line movements
- /ws/sports/games/{game_id}/ - Real-time game updates
"""