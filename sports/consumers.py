"""
WebSocket consumers for real-time sports data updates
"""
import json
import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SportsConsumer(AsyncJsonWebsocketConsumer):
    """
    Main sports WebSocket consumer for real-time updates.
    Handles game updates, odds changes, and score updates.
    """
    
    async def connect(self):
        """Accept WebSocket connection and join sports update group"""
        self.room_group_name = 'sports_updates'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial connection confirmation
        await self.send_json({
            'type': 'connection_established',
            'message': 'Connected to sports updates'
        })
        
        logger.info(f"WebSocket connected: {self.channel_name}")
    
    async def disconnect(self, close_code):
        """Leave sports update group on disconnect"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"WebSocket disconnected: {self.channel_name}, code: {close_code}")
    
    async def receive_json(self, content: Dict[str, Any]):
        """
        Handle incoming WebSocket messages from client.
        
        Supported message types:
        - subscribe_game: Subscribe to updates for a specific game
        - unsubscribe_game: Unsubscribe from game updates
        - subscribe_league: Subscribe to all games in a league
        - get_live_odds: Request current odds for a game
        """
        message_type = content.get('type')
        
        if message_type == 'subscribe_game':
            await self.subscribe_to_game(content.get('game_id'))
        elif message_type == 'unsubscribe_game':
            await self.unsubscribe_from_game(content.get('game_id'))
        elif message_type == 'subscribe_league':
            await self.subscribe_to_league(content.get('league'))
        elif message_type == 'get_live_odds':
            await self.send_live_odds(content.get('game_id'))
        else:
            await self.send_json({
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            })
    
    async def subscribe_to_game(self, game_id: str):
        """Subscribe to updates for a specific game"""
        if not game_id:
            await self.send_json({
                'type': 'error',
                'message': 'game_id is required'
            })
            return
        
        game_group = f'game_{game_id}'
        await self.channel_layer.group_add(
            game_group,
            self.channel_name
        )
        
        await self.send_json({
            'type': 'subscribed',
            'game_id': game_id,
            'message': f'Subscribed to game {game_id} updates'
        })
    
    async def unsubscribe_from_game(self, game_id: str):
        """Unsubscribe from game updates"""
        if not game_id:
            return
        
        game_group = f'game_{game_id}'
        await self.channel_layer.group_discard(
            game_group,
            self.channel_name
        )
        
        await self.send_json({
            'type': 'unsubscribed',
            'game_id': game_id,
            'message': f'Unsubscribed from game {game_id} updates'
        })
    
    async def subscribe_to_league(self, league: str):
        """Subscribe to all games in a league"""
        if not league:
            await self.send_json({
                'type': 'error',
                'message': 'league is required'
            })
            return
        
        league_group = f'league_{league}'
        await self.channel_layer.group_add(
            league_group,
            self.channel_name
        )
        
        await self.send_json({
            'type': 'subscribed',
            'league': league,
            'message': f'Subscribed to {league} updates'
        })
    
    async def send_live_odds(self, game_id: str):
        """Send current odds for a specific game"""
        if not game_id:
            await self.send_json({
                'type': 'error',
                'message': 'game_id is required'
            })
            return
        
        # Check cache first for latest odds
        cache_key = f'odds_{game_id}'
        odds_data = cache.get(cache_key)
        
        if odds_data:
            await self.send_json({
                'type': 'live_odds',
                'game_id': game_id,
                'odds': odds_data
            })
        else:
            await self.send_json({
                'type': 'no_odds',
                'game_id': game_id,
                'message': 'No odds available for this game'
            })
    
    # Channel layer message handlers
    async def sports_update(self, event):
        """Handle sports update messages from channel layer"""
        await self.send_json({
            'type': 'sports_update',
            'data': event['data']
        })
    
    async def odds_update(self, event):
        """Handle odds update messages from channel layer"""
        await self.send_json({
            'type': 'odds_update',
            'game_id': event['game_id'],
            'odds': event['odds']
        })
    
    async def score_update(self, event):
        """Handle score update messages from channel layer"""
        await self.send_json({
            'type': 'score_update',
            'game_id': event['game_id'],
            'score': event['score']
        })
    
    async def game_status_update(self, event):
        """Handle game status changes (started, final, postponed, etc.)"""
        await self.send_json({
            'type': 'game_status',
            'game_id': event['game_id'],
            'status': event['status']
        })


class OddsConsumer(AsyncJsonWebsocketConsumer):
    """
    Specialized consumer for odds-specific updates.
    Handles real-time odds changes and line movements.
    """
    
    async def connect(self):
        """Accept connection and join odds updates group"""
        self.room_group_name = 'odds_updates'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        await self.send_json({
            'type': 'connection_established',
            'message': 'Connected to odds updates'
        })
        
        logger.info(f"Odds WebSocket connected: {self.channel_name}")
    
    async def disconnect(self, close_code):
        """Leave odds update group"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"Odds WebSocket disconnected: {self.channel_name}")
    
    async def receive_json(self, content: Dict[str, Any]):
        """
        Handle incoming messages for odds subscriptions.
        
        Supported message types:
        - subscribe_market: Subscribe to a specific betting market
        - subscribe_all_markets: Subscribe to all markets for a game
        - get_line_history: Get historical line movements
        """
        message_type = content.get('type')
        
        if message_type == 'subscribe_market':
            await self.subscribe_to_market(
                content.get('game_id'),
                content.get('market_type')
            )
        elif message_type == 'subscribe_all_markets':
            await self.subscribe_to_all_markets(content.get('game_id'))
        elif message_type == 'get_line_history':
            await self.send_line_history(
                content.get('game_id'),
                content.get('market_type')
            )
        else:
            await self.send_json({
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            })
    
    async def subscribe_to_market(self, game_id: str, market_type: str):
        """Subscribe to specific market updates (spread, total, moneyline)"""
        if not game_id or not market_type:
            await self.send_json({
                'type': 'error',
                'message': 'game_id and market_type are required'
            })
            return
        
        market_group = f'market_{game_id}_{market_type}'
        await self.channel_layer.group_add(
            market_group,
            self.channel_name
        )
        
        await self.send_json({
            'type': 'subscribed',
            'game_id': game_id,
            'market_type': market_type,
            'message': f'Subscribed to {market_type} updates for game {game_id}'
        })
    
    async def subscribe_to_all_markets(self, game_id: str):
        """Subscribe to all betting markets for a game"""
        if not game_id:
            await self.send_json({
                'type': 'error',
                'message': 'game_id is required'
            })
            return
        
        # Subscribe to all market types
        market_types = ['spread', 'total', 'moneyline']
        for market_type in market_types:
            market_group = f'market_{game_id}_{market_type}'
            await self.channel_layer.group_add(
                market_group,
                self.channel_name
            )
        
        await self.send_json({
            'type': 'subscribed_all',
            'game_id': game_id,
            'markets': market_types,
            'message': f'Subscribed to all markets for game {game_id}'
        })
    
    async def send_line_history(self, game_id: str, market_type: str):
        """Send historical line movement data"""
        if not game_id or not market_type:
            await self.send_json({
                'type': 'error',
                'message': 'game_id and market_type are required'
            })
            return
        
        # Get line history from cache
        cache_key = f'line_history_{game_id}_{market_type}'
        history = cache.get(cache_key, [])
        
        await self.send_json({
            'type': 'line_history',
            'game_id': game_id,
            'market_type': market_type,
            'history': history
        })
    
    # Channel layer message handlers
    async def odds_change(self, event):
        """Handle odds change notifications"""
        await self.send_json({
            'type': 'odds_change',
            'game_id': event['game_id'],
            'market_type': event['market_type'],
            'old_value': event.get('old_value'),
            'new_value': event['new_value'],
            'timestamp': event.get('timestamp')
        })
    
    async def line_movement(self, event):
        """Handle significant line movements"""
        await self.send_json({
            'type': 'line_movement',
            'game_id': event['game_id'],
            'market_type': event['market_type'],
            'movement': event['movement'],
            'timestamp': event.get('timestamp')
        })


class GamesConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumer for game-specific updates and live game tracking.
    """
    
    async def connect(self):
        """Accept connection and set up game tracking"""
        self.subscribed_games = set()
        await self.accept()
        
        await self.send_json({
            'type': 'connection_established',
            'message': 'Connected to games updates'
        })
        
        logger.info(f"Games WebSocket connected: {self.channel_name}")
    
    async def disconnect(self, close_code):
        """Clean up game subscriptions on disconnect"""
        # Leave all subscribed game groups
        for game_id in self.subscribed_games:
            game_group = f'live_game_{game_id}'
            await self.channel_layer.group_discard(
                game_group,
                self.channel_name
            )
        
        logger.info(f"Games WebSocket disconnected: {self.channel_name}")
    
    async def receive_json(self, content: Dict[str, Any]):
        """
        Handle game tracking requests.
        
        Supported message types:
        - track_game: Start tracking a live game
        - untrack_game: Stop tracking a game
        - get_game_stats: Get current game statistics
        """
        message_type = content.get('type')
        
        if message_type == 'track_game':
            await self.track_game(content.get('game_id'))
        elif message_type == 'untrack_game':
            await self.untrack_game(content.get('game_id'))
        elif message_type == 'get_game_stats':
            await self.send_game_stats(content.get('game_id'))
        else:
            await self.send_json({
                'type': 'error',
                'message': f'Unknown message type: {message_type}'
            })
    
    async def track_game(self, game_id: str):
        """Start tracking a live game"""
        if not game_id:
            await self.send_json({
                'type': 'error',
                'message': 'game_id is required'
            })
            return
        
        if game_id not in self.subscribed_games:
            game_group = f'live_game_{game_id}'
            await self.channel_layer.group_add(
                game_group,
                self.channel_name
            )
            self.subscribed_games.add(game_id)
        
        await self.send_json({
            'type': 'tracking_started',
            'game_id': game_id,
            'message': f'Now tracking game {game_id}'
        })
    
    async def untrack_game(self, game_id: str):
        """Stop tracking a game"""
        if not game_id:
            return
        
        if game_id in self.subscribed_games:
            game_group = f'live_game_{game_id}'
            await self.channel_layer.group_discard(
                game_group,
                self.channel_name
            )
            self.subscribed_games.remove(game_id)
        
        await self.send_json({
            'type': 'tracking_stopped',
            'game_id': game_id,
            'message': f'Stopped tracking game {game_id}'
        })
    
    async def send_game_stats(self, game_id: str):
        """Send current game statistics"""
        if not game_id:
            await self.send_json({
                'type': 'error',
                'message': 'game_id is required'
            })
            return
        
        # Get game stats from cache
        cache_key = f'game_stats_{game_id}'
        stats = cache.get(cache_key)
        
        if stats:
            await self.send_json({
                'type': 'game_stats',
                'game_id': game_id,
                'stats': stats
            })
        else:
            await self.send_json({
                'type': 'no_stats',
                'game_id': game_id,
                'message': 'No statistics available for this game'
            })
    
    # Channel layer message handlers
    async def game_update(self, event):
        """Handle general game updates"""
        await self.send_json({
            'type': 'game_update',
            'game_id': event['game_id'],
            'data': event['data']
        })
    
    async def play_by_play(self, event):
        """Handle play-by-play updates for live games"""
        await self.send_json({
            'type': 'play_by_play',
            'game_id': event['game_id'],
            'play': event['play'],
            'timestamp': event.get('timestamp')
        })
    
    async def quarter_end(self, event):
        """Handle quarter/period end notifications"""
        await self.send_json({
            'type': 'quarter_end',
            'game_id': event['game_id'],
            'quarter': event['quarter'],
            'score': event['score']
        })
