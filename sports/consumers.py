"""
Sports Analytics WebSocket Consumers

Real-time WebSocket consumers for live sports data streaming including:
- Live odds updates
- Line movement notifications
- Game score updates
- Arbitrage alerts
- Betting recommendations
"""

import json
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder

from .models import (
    Game, BettingMarket, OddsLine, LineMovement, ArbitrageOpportunity,
    BettingRecommendation, GameStatus, MarketStatus
)
from .serializers import (
    GameSerializer, OddsLineSerializer, LineMovementSerializer,
    ArbitrageOpportunitySerializer, BettingRecommendationSerializer
)

logger = logging.getLogger(__name__)


class SportsBaseConsumer(AsyncWebsocketConsumer):
    """Base consumer with common functionality"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.groups = []
        
    async def connect(self):
        """Handle WebSocket connection"""
        # Get user from scope (set by AuthMiddleware)
        self.user = self.scope.get('user')
        
        # Allow anonymous connections for development/testing
        from django.contrib.auth.models import AnonymousUser
        if not self.user or isinstance(self.user, AnonymousUser):
            # For anonymous users, we still accept but with limited functionality
            self.user = AnonymousUser()
        
        await self.accept()
        
        # Add user to their personal group
        from django.contrib.auth.models import AnonymousUser
        if not isinstance(self.user, AnonymousUser):
            user_group = f"user_{self.user.id}"
            await self.channel_layer.group_add(user_group, self.channel_name)
            self.groups.append(user_group)
            logger.info(f"WebSocket connected: {self.user.username}")
        else:
            logger.info("WebSocket connected: anonymous user")
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Remove from all groups
        for group in self.groups:
            await self.channel_layer.group_discard(group, self.channel_name)
        
        logger.info(f"WebSocket disconnected: {self.user.username if self.user else 'anonymous'}")
    
    async def send_json_data(self, data: Dict[str, Any]):
        """Send JSON data with proper encoding"""
        await self.send(text_data=json.dumps(data, cls=DjangoJSONEncoder))
    
    async def send_error(self, message: str, error_code: str = "generic_error"):
        """Send error message"""
        await self.send_json_data({
            'type': 'error',
            'error_code': error_code,
            'message': message,
            'timestamp': timezone.now()
        })


class GameConsumer(SportsBaseConsumer):
    """Consumer for real-time game updates"""
    
    async def connect(self):
        """Connect to game updates"""
        await super().connect()
        
        if not self.user:
            return
        
        # Get game ID from URL
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        
        # Verify game exists
        try:
            self.game = await self.get_game(self.game_id)
        except Game.DoesNotExist:
            await self.send_error("Game not found", "game_not_found")
            await self.close()
            return
        
        # Join game group
        self.game_group = f"game_{self.game_id}"
        await self.channel_layer.group_add(self.game_group, self.channel_name)
        self.groups.append(self.game_group)
        
        # Send initial game data
        await self.send_initial_data()
    
    @database_sync_to_async
    def get_game(self, game_id):
        """Get game from database"""
        return Game.objects.select_related('league', 'home_team', 'away_team').get(id=game_id)
    
    async def send_initial_data(self):
        """Send initial game data"""
        game_data = await self.serialize_game(self.game)
        
        await self.send_json_data({
            'type': 'initial_data',
            'game': game_data,
            'subscribed_to': f"game_{self.game_id}",
            'timestamp': timezone.now()
        })
    
    @database_sync_to_async
    def serialize_game(self, game):
        """Serialize game data"""
        return GameSerializer(game).data
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_markets':
                await self.subscribe_to_markets()
            elif message_type == 'ping':
                await self.send_json_data({'type': 'pong', 'timestamp': timezone.now()})
            else:
                await self.send_error(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON", "invalid_json")
    
    async def subscribe_to_markets(self):
        """Subscribe to betting markets for this game"""
        markets_group = f"markets_{self.game_id}"
        await self.channel_layer.group_add(markets_group, self.channel_name)
        self.groups.append(markets_group)
        
        await self.send_json_data({
            'type': 'subscribed',
            'subscription': 'markets',
            'game_id': str(self.game_id)
        })
    
    # Message handlers for different types of updates
    async def game_update(self, event):
        """Handle game status updates"""
        await self.send_json_data({
            'type': 'game_update',
            'data': event['data'],
            'timestamp': timezone.now()
        })
    
    async def score_update(self, event):
        """Handle score updates"""
        await self.send_json_data({
            'type': 'score_update',
            'data': event['data'],
            'timestamp': timezone.now()
        })
    
    async def market_update(self, event):
        """Handle betting market updates"""
        await self.send_json_data({
            'type': 'market_update',
            'data': event['data'],
            'timestamp': timezone.now()
        })


class OddsConsumer(SportsBaseConsumer):
    """Consumer for real-time odds updates"""
    
    async def connect(self):
        """Connect to odds updates"""
        await super().connect()
        
        if not self.user:
            return
        
        # Get market ID from URL
        self.market_id = self.scope['url_route']['kwargs'].get('market_id')
        self.game_id = self.scope['url_route']['kwargs'].get('game_id')
        
        if self.market_id:
            # Subscribe to specific market
            try:
                self.market = await self.get_market(self.market_id)
                self.odds_group = f"odds_{self.market_id}"
                await self.channel_layer.group_add(self.odds_group, self.channel_name)
                self.groups.append(self.odds_group)
                
                await self.send_initial_odds_data()
                
            except BettingMarket.DoesNotExist:
                await self.send_error("Market not found", "market_not_found")
                await self.close()
                return
                
        elif self.game_id:
            # Subscribe to all markets for a game
            try:
                self.game = await self.get_game(self.game_id)
                self.odds_group = f"odds_game_{self.game_id}"
                await self.channel_layer.group_add(self.odds_group, self.channel_name)
                self.groups.append(self.odds_group)
                
                await self.send_initial_game_odds()
                
            except Game.DoesNotExist:
                await self.send_error("Game not found", "game_not_found")
                await self.close()
                return
        else:
            await self.send_error("Market ID or Game ID required", "missing_id")
            await self.close()
            return
    
    @database_sync_to_async
    def get_market(self, market_id):
        """Get market from database"""
        return BettingMarket.objects.select_related('game').get(id=market_id)
    
    @database_sync_to_async
    def get_game(self, game_id):
        """Get game from database"""
        return Game.objects.get(id=game_id)
    
    async def send_initial_odds_data(self):
        """Send initial odds data for market"""
        current_odds = await self.get_current_odds(self.market_id)
        odds_data = [await self.serialize_odds(odds) for odds in current_odds]
        
        await self.send_json_data({
            'type': 'initial_odds',
            'market_id': str(self.market_id),
            'odds': odds_data,
            'timestamp': timezone.now()
        })
    
    async def send_initial_game_odds(self):
        """Send initial odds data for all game markets"""
        markets = await self.get_game_markets(self.game_id)
        
        game_odds = {}
        for market in markets:
            odds = await self.get_current_odds(market.id)
            game_odds[str(market.id)] = {
                'market_type': market.market_type,
                'market_name': market.market_name,
                'odds': [await self.serialize_odds(odds_line) for odds_line in odds]
            }
        
        await self.send_json_data({
            'type': 'initial_game_odds',
            'game_id': str(self.game_id),
            'markets': game_odds,
            'timestamp': timezone.now()
        })
    
    @database_sync_to_async
    def get_current_odds(self, market_id):
        """Get current odds for market"""
        return list(OddsLine.objects.filter(
            market_id=market_id,
            is_current=True
        ).select_related('sportsbook'))
    
    @database_sync_to_async
    def get_game_markets(self, game_id):
        """Get markets for game"""
        return list(BettingMarket.objects.filter(
            game_id=game_id,
            is_active=True,
            status=MarketStatus.OPEN
        ))
    
    @database_sync_to_async
    def serialize_odds(self, odds_line):
        """Serialize odds line"""
        return OddsLineSerializer(odds_line).data
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_sportsbook':
                sportsbook_id = data.get('sportsbook_id')
                if sportsbook_id:
                    await self.subscribe_sportsbook(sportsbook_id)
            elif message_type == 'unsubscribe_sportsbook':
                sportsbook_id = data.get('sportsbook_id')
                if sportsbook_id:
                    await self.unsubscribe_sportsbook(sportsbook_id)
            elif message_type == 'ping':
                await self.send_json_data({'type': 'pong', 'timestamp': timezone.now()})
            else:
                await self.send_error(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON", "invalid_json")
    
    async def subscribe_sportsbook(self, sportsbook_id):
        """Subscribe to specific sportsbook odds"""
        sportsbook_group = f"sportsbook_{sportsbook_id}"
        await self.channel_layer.group_add(sportsbook_group, self.channel_name)
        self.groups.append(sportsbook_group)
        
        await self.send_json_data({
            'type': 'subscribed',
            'subscription': 'sportsbook',
            'sportsbook_id': sportsbook_id
        })
    
    async def unsubscribe_sportsbook(self, sportsbook_id):
        """Unsubscribe from sportsbook odds"""
        sportsbook_group = f"sportsbook_{sportsbook_id}"
        await self.channel_layer.group_discard(sportsbook_group, self.channel_name)
        if sportsbook_group in self.groups:
            self.groups.remove(sportsbook_group)
        
        await self.send_json_data({
            'type': 'unsubscribed',
            'subscription': 'sportsbook',
            'sportsbook_id': sportsbook_id
        })
    
    # Message handlers
    async def odds_update(self, event):
        """Handle odds updates"""
        await self.send_json_data({
            'type': 'odds_update',
            'data': event['data'],
            'timestamp': timezone.now()
        })
    
    async def line_movement(self, event):
        """Handle line movement notifications"""
        await self.send_json_data({
            'type': 'line_movement',
            'data': event['data'],
            'timestamp': timezone.now()
        })


class ArbitrageConsumer(SportsBaseConsumer):
    """Consumer for arbitrage opportunity alerts"""
    
    async def connect(self):
        """Connect to arbitrage alerts"""
        await super().connect()
        
        if not self.user:
            return
        
        # Join arbitrage alerts group
        arbitrage_group = "arbitrage_alerts"
        await self.channel_layer.group_add(arbitrage_group, self.channel_name)
        self.groups.append(arbitrage_group)
        
        # Send initial arbitrage opportunities
        await self.send_initial_opportunities()
    
    async def send_initial_opportunities(self):
        """Send current arbitrage opportunities"""
        opportunities = await self.get_active_opportunities()
        opportunities_data = [await self.serialize_opportunity(opp) for opp in opportunities]
        
        await self.send_json_data({
            'type': 'initial_opportunities',
            'opportunities': opportunities_data,
            'count': len(opportunities_data),
            'timestamp': timezone.now()
        })
    
    @database_sync_to_async
    def get_active_opportunities(self):
        """Get active arbitrage opportunities"""
        return list(ArbitrageOpportunity.objects.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        ).select_related('game', 'sportsbook_1', 'sportsbook_2')[:20])
    
    @database_sync_to_async
    def serialize_opportunity(self, opportunity):
        """Serialize arbitrage opportunity"""
        return ArbitrageOpportunitySerializer(opportunity).data
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'set_min_profit':
                min_profit = data.get('min_profit', 1.0)
                await self.set_profit_filter(min_profit)
            elif message_type == 'subscribe_sport':
                sport_type = data.get('sport_type')
                if sport_type:
                    await self.subscribe_sport(sport_type)
            elif message_type == 'ping':
                await self.send_json_data({'type': 'pong', 'timestamp': timezone.now()})
            else:
                await self.send_error(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON", "invalid_json")
    
    async def set_profit_filter(self, min_profit):
        """Set minimum profit filter for user"""
        # Store user preference (could save to database)
        await self.send_json_data({
            'type': 'filter_set',
            'filter': 'min_profit',
            'value': min_profit,
            'message': f'Minimum profit filter set to {min_profit}%'
        })
    
    async def subscribe_sport(self, sport_type):
        """Subscribe to arbitrage alerts for specific sport"""
        sport_group = f"arbitrage_{sport_type}"
        await self.channel_layer.group_add(sport_group, self.channel_name)
        self.groups.append(sport_group)
        
        await self.send_json_data({
            'type': 'subscribed',
            'subscription': 'sport',
            'sport_type': sport_type
        })
    
    # Message handlers
    async def arbitrage_alert(self, event):
        """Handle new arbitrage opportunity alerts"""
        await self.send_json_data({
            'type': 'arbitrage_alert',
            'data': event['data'],
            'timestamp': timezone.now()
        })
    
    async def arbitrage_expired(self, event):
        """Handle arbitrage opportunity expiration"""
        await self.send_json_data({
            'type': 'arbitrage_expired',
            'data': event['data'],
            'timestamp': timezone.now()
        })


class RecommendationConsumer(SportsBaseConsumer):
    """Consumer for betting recommendations"""
    
    async def connect(self):
        """Connect to betting recommendations"""
        await super().connect()
        
        from django.contrib.auth.models import AnonymousUser
        if not self.user or isinstance(self.user, AnonymousUser):
            return
        
        # Join user's recommendation group
        rec_group = f"recommendations_{self.user.id}"
        await self.channel_layer.group_add(rec_group, self.channel_name)
        self.groups.append(rec_group)
        
        # Send initial recommendations
        await self.send_initial_recommendations()
    
    async def send_initial_recommendations(self):
        """Send current active recommendations for user"""
        recommendations = await self.get_user_recommendations()
        rec_data = [await self.serialize_recommendation(rec) for rec in recommendations]
        
        await self.send_json_data({
            'type': 'initial_recommendations',
            'recommendations': rec_data,
            'count': len(rec_data),
            'timestamp': timezone.now()
        })
    
    @database_sync_to_async
    def get_user_recommendations(self):
        """Get user's active recommendations"""
        from django.contrib.auth.models import AnonymousUser
        if isinstance(self.user, AnonymousUser):
            return []  # Return empty list for anonymous users
        
        return list(BettingRecommendation.objects.filter(
            user=self.user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).select_related('game', 'market', 'recommended_sportsbook')[:10])
    
    @database_sync_to_async
    def serialize_recommendation(self, recommendation):
        """Serialize recommendation"""
        return BettingRecommendationSerializer(recommendation).data
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'request_recommendations':
                sport_type = data.get('sport_type')
                await self.request_recommendations(sport_type)
            elif message_type == 'accept_recommendation':
                rec_id = data.get('recommendation_id')
                if rec_id:
                    await self.accept_recommendation(rec_id)
            elif message_type == 'reject_recommendation':
                rec_id = data.get('recommendation_id')
                if rec_id:
                    await self.reject_recommendation(rec_id)
            elif message_type == 'ping':
                await self.send_json_data({'type': 'pong', 'timestamp': timezone.now()})
            else:
                await self.send_error(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON", "invalid_json")
    
    async def request_recommendations(self, sport_type=None):
        """Request new recommendations"""
        # This would trigger the recommendation service
        await self.send_json_data({
            'type': 'generation_started',
            'sport_type': sport_type,
            'estimated_time': '30-60 seconds',
            'message': 'Generating new recommendations...'
        })
    
    @database_sync_to_async
    def update_recommendation_status(self, rec_id, status):
        """Update recommendation status"""
        try:
            rec = BettingRecommendation.objects.get(
                id=rec_id,
                user=self.user
            )
            rec.user_action = status
            rec.save()
            return True
        except BettingRecommendation.DoesNotExist:
            return False
    
    async def accept_recommendation(self, rec_id):
        """Accept a recommendation"""
        success = await self.update_recommendation_status(rec_id, 'accepted')
        
        if success:
            await self.send_json_data({
                'type': 'recommendation_accepted',
                'recommendation_id': rec_id,
                'message': 'Recommendation accepted'
            })
        else:
            await self.send_error("Recommendation not found", "rec_not_found")
    
    async def reject_recommendation(self, rec_id):
        """Reject a recommendation"""
        success = await self.update_recommendation_status(rec_id, 'rejected')
        
        if success:
            await self.send_json_data({
                'type': 'recommendation_rejected',
                'recommendation_id': rec_id,
                'message': 'Recommendation rejected'
            })
        else:
            await self.send_error("Recommendation not found", "rec_not_found")
    
    # Message handlers
    async def new_recommendation(self, event):
        """Handle new recommendation alerts"""
        await self.send_json_data({
            'type': 'new_recommendation',
            'data': event['data'],
            'timestamp': timezone.now()
        })
    
    async def recommendation_expired(self, event):
        """Handle recommendation expiration"""
        await self.send_json_data({
            'type': 'recommendation_expired',
            'data': event['data'],
            'timestamp': timezone.now()
        })


class DashboardConsumer(SportsBaseConsumer):
    """Consumer for dashboard real-time updates"""
    
    async def connect(self):
        """Connect to dashboard updates"""
        await super().connect()
        
        from django.contrib.auth.models import AnonymousUser
        if not self.user or isinstance(self.user, AnonymousUser):
            return
        
        # Join dashboard group
        dashboard_group = f"dashboard_{self.user.id}"
        await self.channel_layer.group_add(dashboard_group, self.channel_name)
        self.groups.append(dashboard_group)
        
        # Send initial dashboard data
        await self.send_dashboard_summary()
    
    async def send_dashboard_summary(self):
        """Send dashboard summary data"""
        summary = await self.get_dashboard_data()
        
        await self.send_json_data({
            'type': 'dashboard_summary',
            'data': summary,
            'timestamp': timezone.now()
        })
    
    @database_sync_to_async
    def get_dashboard_data(self):
        """Get dashboard data for user"""
        from django.db.models import Sum, Count, Avg
        from django.contrib.auth.models import AnonymousUser
        
        if isinstance(self.user, AnonymousUser):
            # Return demo data for anonymous users
            return {
                'user_stats': {
                    'total_bets': 0,
                    'total_wagered': '0.00',
                    'total_profit': '0.00',
                    'roi': 0.0
                },
                'system_stats': {
                    'active_arbitrage': 0,
                    'total_games': Game.objects.filter(status='scheduled').count(),
                    'active_markets': Market.objects.filter(is_active=True).count()
                },
                'recent_activity': []
            }
        
        # User's betting stats
        user_bets = self.user.bets.filter(is_active=True)
        total_bets = user_bets.count()
        total_wagered = user_bets.aggregate(Sum('stake'))['stake__sum'] or Decimal('0.00')
        total_profit = user_bets.aggregate(Sum('result_amount'))['result_amount__sum'] or Decimal('0.00')
        
        # Active opportunities
        active_arbitrage = ArbitrageOpportunity.objects.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        ).count()
        
        active_recommendations = BettingRecommendation.objects.filter(
            user=self.user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).count()
        
        # Today's games
        today_games = Game.objects.filter(
            scheduled_start__date=timezone.now().date(),
            is_active=True
        ).count()
        
        return {
            'user_stats': {
                'total_bets': total_bets,
                'total_wagered': float(total_wagered),
                'total_profit': float(total_profit),
                'roi': float(total_profit / total_wagered * 100) if total_wagered > 0 else 0.0
            },
            'opportunities': {
                'arbitrage': active_arbitrage,
                'recommendations': active_recommendations
            },
            'games': {
                'today': today_games
            },
            'last_updated': timezone.now()
        }
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'refresh_dashboard':
                await self.send_dashboard_summary()
            elif message_type == 'ping':
                await self.send_json_data({'type': 'pong', 'timestamp': timezone.now()})
            else:
                await self.send_error(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON", "invalid_json")
    
    # Message handlers
    async def dashboard_update(self, event):
        """Handle dashboard updates"""
        await self.send_json_data({
            'type': 'dashboard_update',
            'data': event['data'],
            'timestamp': timezone.now()
        })