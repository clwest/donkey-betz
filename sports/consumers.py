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
        elif message_type == 'get_live_scores':
            await self.send_live_scores()
        elif message_type == 'get_ai_predictions':
            await self.send_ai_predictions()
        elif message_type == 'get_betting_history':
            await self.send_betting_history()
        elif message_type == 'get_sport_details':
            await self.send_sport_details(content.get('sport'))
        elif message_type == 'place_bet':
            await self.handle_place_bet(content.get('bet'))
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

    async def send_live_scores(self):
        """Send current live scores for all active games"""
        import random

        # Sample live scores data (in production, fetch from database or API)
        scores_data = {
            'nfl': [
                {
                    'game_id': 'nfl_1',
                    'home_team': 'Kansas City Chiefs',
                    'away_team': 'Buffalo Bills',
                    'home_score': random.randint(14, 35),
                    'away_score': random.randint(14, 35),
                    'quarter': random.choice(['Q1', 'Q2', 'Q3', 'Q4']),
                    'time_remaining': f"{random.randint(0, 15):02d}:{random.randint(0, 59):02d}",
                    'status': 'live'
                }
            ],
            'nba': [
                {
                    'game_id': 'nba_1',
                    'home_team': 'LA Lakers',
                    'away_team': 'Boston Celtics',
                    'home_score': random.randint(85, 120),
                    'away_score': random.randint(85, 120),
                    'quarter': random.choice(['1st', '2nd', '3rd', '4th']),
                    'time_remaining': f"{random.randint(0, 12):02d}:{random.randint(0, 59):02d}",
                    'status': 'live'
                }
            ],
            'soccer': [
                {
                    'game_id': 'ucl_1',
                    'home_team': 'Real Madrid',
                    'away_team': 'Manchester City',
                    'home_score': random.randint(0, 4),
                    'away_score': random.randint(0, 4),
                    'minute': random.randint(1, 90),
                    'status': 'live'
                }
            ]
        }

        await self.send_json({
            'type': 'live_scores',
            'data': scores_data,
            'timestamp': str(cache.get('last_update', 'N/A'))
        })

    async def send_ai_predictions(self):
        """Send AI-generated betting predictions"""
        import random

        predictions = {
            'featured_picks': [
                {
                    'game': 'Chiefs vs Bills',
                    'pick': 'Chiefs -3.5',
                    'confidence': random.randint(65, 95),
                    'reasoning': 'Chiefs home field advantage, 5-0 ATS in last 5 home games',
                    'potential_payout': '+110'
                },
                {
                    'game': 'Lakers vs Celtics',
                    'pick': 'Over 220.5',
                    'confidence': random.randint(70, 88),
                    'reasoning': 'Both teams averaging 115+ PPG in last 10 games',
                    'potential_payout': '-105'
                },
                {
                    'game': 'Real Madrid vs Man City',
                    'pick': 'Both Teams to Score',
                    'confidence': random.randint(75, 92),
                    'reasoning': 'High-scoring matchup history, both teams in form',
                    'potential_payout': '-120'
                }
            ],
            'system_performance': {
                'today': {'win_rate': 0.78, 'units': 12.5},
                'week': {'win_rate': 0.71, 'units': 45.2},
                'month': {'win_rate': 0.68, 'units': 156.8}
            }
        }

        await self.send_json({
            'type': 'ai_predictions',
            'predictions': predictions
        })

    async def send_betting_history(self):
        """Send user's betting history"""
        import random
        from datetime import datetime, timedelta

        # Generate sample betting history
        history = []
        for i in range(10):
            date = datetime.now() - timedelta(days=i)
            history.append({
                'date': date.strftime('%Y-%m-%d'),
                'game': random.choice(['NFL', 'NBA', 'MLB', 'NHL', 'Soccer']),
                'bet_type': random.choice(['Spread', 'Total', 'Moneyline']),
                'selection': random.choice(['Home -3.5', 'Away +7', 'Over 220', 'Under 48.5']),
                'odds': random.choice(['-110', '+105', '-120', '+150']),
                'stake': random.choice([50, 100, 200]),
                'result': random.choice(['Win', 'Loss', 'Push']),
                'payout': random.choice([0, 95, 190, 250])
            })

        stats = {
            'total_bets': len(history),
            'wins': sum(1 for h in history if h['result'] == 'Win'),
            'losses': sum(1 for h in history if h['result'] == 'Loss'),
            'pushes': sum(1 for h in history if h['result'] == 'Push'),
            'total_staked': sum(h['stake'] for h in history),
            'total_payout': sum(h['payout'] for h in history),
            'roi': random.uniform(-5, 25)
        }

        await self.send_json({
            'type': 'betting_history',
            'history': history,
            'stats': stats
        })

    async def send_sport_details(self, sport: str):
        """Send detailed information for a specific sport"""
        if not sport:
            await self.send_json({
                'type': 'error',
                'message': 'Sport name is required'
            })
            return

        import random

        # Generate sport-specific details
        details = {
            'sport': sport,
            'upcoming_games': [],
            'trending_bets': [],
            'ai_insights': []
        }

        # Add sample upcoming games
        for i in range(5):
            details['upcoming_games'].append({
                'game_id': f'{sport.lower()}_{i}',
                'home_team': f'Team {i*2}',
                'away_team': f'Team {i*2+1}',
                'start_time': f'{random.randint(12, 20)}:00',
                'spread': f'{random.choice(["+", "-"])}{random.randint(1, 10)}.5',
                'total': random.randint(180, 250),
                'ml_home': random.choice(['-150', '-120', '+105']),
                'ml_away': random.choice(['+130', '-105', '-110'])
            })

        # Add trending bets
        details['trending_bets'] = [
            f'{sport} Team A to win by 10+',
            f'Over 220.5 total points',
            f'First quarter winner'
        ]

        # Add AI insights
        details['ai_insights'] = [
            'Home teams are 8-2 ATS in last 10 games',
            'Unders hitting at 65% rate this week',
            'Public heavy on favorites, value on dogs'
        ]

        await self.send_json({
            'type': 'sport_details',
            'details': details
        })

    async def handle_place_bet(self, bet_data: dict):
        """Handle placing a bet"""
        if not bet_data:
            await self.send_json({
                'type': 'error',
                'message': 'Bet data is required'
            })
            return

        # In production, this would save to database and process the bet
        # For now, just acknowledge receipt
        import random

        bet_id = f'BET_{random.randint(10000, 99999)}'

        # Simulate bet processing
        await self.send_json({
            'type': 'bet_placed',
            'bet_id': bet_id,
            'status': 'pending',
            'message': f'Bet placed successfully: {bet_data.get("selection")} at {bet_data.get("odds")}',
            'bet_slip': {
                'id': bet_id,
                'selection': bet_data.get('selection'),
                'odds': bet_data.get('odds'),
                'timestamp': bet_data.get('timestamp'),
                'status': 'pending'
            }
        })

        # You could also broadcast to a betting group for real-time updates
        logger.info(f'Bet placed: {bet_id} - {bet_data}')
