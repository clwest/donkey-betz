"""
Sports WebSocket Consumer for live sports data and betting analytics
"""

import json
import asyncio
import logging
import random
from datetime import datetime, timedelta
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class SportsConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for sports hub real-time updates"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_task = None
        self.live_scores = {}
        self.odds_data = {}

    async def connect(self):
        """Handle WebSocket connection"""
        await self.accept()

        logger.info(f"Sports WebSocket connected: {self.channel_name}")

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to sports updates',
            'timestamp': timezone.now().isoformat()
        }))

        # Start periodic updates
        self.update_task = asyncio.create_task(self.send_live_updates())

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if self.update_task:
            self.update_task.cancel()

        logger.info(f"Sports WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            logger.info(f"Sports WebSocket received: {message_type}")

            if message_type == 'get_live_scores':
                await self.send_live_scores()
            elif message_type == 'get_odds':
                await self.send_odds_update()
            elif message_type == 'get_predictions':
                await self.send_ai_predictions()
            elif message_type == 'place_bet':
                await self.handle_bet_placement(data)
            elif message_type == 'get_analytics':
                await self.send_analytics()
            else:
                # Send generic response for unknown types
                await self.send(text_data=json.dumps({
                    'type': 'response',
                    'message': f'Received {message_type}',
                    'timestamp': timezone.now().isoformat()
                }))

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON received: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_live_scores(self):
        """Send current live scores"""
        # Generate sample live scores (in production, fetch from real API)
        scores = {
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

        await self.send(text_data=json.dumps({
            'type': 'live_scores',
            'data': scores,
            'timestamp': timezone.now().isoformat()
        }))

    async def send_odds_update(self):
        """Send current odds data"""
        odds = {
            'featured_games': [
                {
                    'game_id': 'nfl_1',
                    'sport': 'NFL',
                    'home_team': 'Chiefs',
                    'away_team': 'Bills',
                    'spread': {
                        'home': '-3.5',
                        'home_odds': -110,
                        'away': '+3.5',
                        'away_odds': -110
                    },
                    'moneyline': {
                        'home': -165,
                        'away': +145
                    },
                    'total': {
                        'over': '47.5',
                        'over_odds': -110,
                        'under': '47.5',
                        'under_odds': -110
                    }
                }
            ],
            'best_value': [
                {
                    'description': 'Chiefs to cover -3.5',
                    'odds': -110,
                    'confidence': 72,
                    'expected_value': 1.24
                }
            ]
        }

        await self.send(text_data=json.dumps({
            'type': 'odds_update',
            'data': odds,
            'timestamp': timezone.now().isoformat()
        }))

    async def send_ai_predictions(self):
        """Send AI-generated predictions"""
        predictions = {
            'top_picks': [
                {
                    'game': 'Chiefs vs Bills',
                    'pick': 'Chiefs -3.5',
                    'confidence': 87,
                    'ai_reasoning': 'Home advantage, recent performance metrics favor Chiefs',
                    'projected_score': 'Chiefs 27-24'
                },
                {
                    'game': 'Lakers vs Celtics',
                    'pick': 'Under 220.5',
                    'confidence': 76,
                    'ai_reasoning': 'Both teams playing second night of back-to-back',
                    'projected_score': 'Lakers 105-103'
                }
            ],
            'win_rate_today': 87.3,
            'units_profit': 24.5,
            'total_predictions': 156
        }

        await self.send(text_data=json.dumps({
            'type': 'ai_predictions',
            'data': predictions,
            'timestamp': timezone.now().isoformat()
        }))

    async def send_analytics(self):
        """Send betting analytics"""
        analytics = {
            'performance': {
                'today': {
                    'wins': 12,
                    'losses': 3,
                    'pushes': 1,
                    'win_rate': 80.0,
                    'profit': 8.75
                },
                'week': {
                    'wins': 67,
                    'losses': 28,
                    'pushes': 5,
                    'win_rate': 70.5,
                    'profit': 32.25
                },
                'month': {
                    'wins': 234,
                    'losses': 142,
                    'pushes': 24,
                    'win_rate': 62.2,
                    'profit': 87.50
                }
            },
            'by_sport': {
                'nfl': {'win_rate': 68.5, 'profit': 42.3},
                'nba': {'win_rate': 71.2, 'profit': 28.7},
                'mlb': {'win_rate': 59.8, 'profit': 16.5}
            },
            'hot_streaks': [
                'NFL Over/Under: 8-2 last 10',
                'NBA Home Favorites: 12-3 last 15',
                'Soccer Draw No Bet: 9-1 last 10'
            ]
        }

        await self.send(text_data=json.dumps({
            'type': 'analytics',
            'data': analytics,
            'timestamp': timezone.now().isoformat()
        }))

    async def handle_bet_placement(self, data):
        """Handle bet placement request"""
        bet_data = data.get('bet', {})

        # In production, this would actually place the bet
        # For now, simulate successful placement
        result = {
            'success': True,
            'bet_id': f"BET_{random.randint(100000, 999999)}",
            'game': bet_data.get('game', 'Unknown'),
            'type': bet_data.get('bet_type', 'spread'),
            'pick': bet_data.get('pick', ''),
            'odds': bet_data.get('odds', -110),
            'amount': bet_data.get('amount', 100),
            'potential_win': bet_data.get('amount', 100) * 1.91,
            'status': 'pending'
        }

        await self.send(text_data=json.dumps({
            'type': 'bet_placed',
            'data': result,
            'timestamp': timezone.now().isoformat()
        }))

    async def send_live_updates(self):
        """Send periodic live updates"""
        while True:
            try:
                await asyncio.sleep(10)  # Update every 10 seconds

                # Send live score updates
                await self.send_live_scores()

                # Occasionally send odds updates
                if random.random() > 0.7:
                    await self.send_odds_update()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in live updates: {e}")
                await asyncio.sleep(10)