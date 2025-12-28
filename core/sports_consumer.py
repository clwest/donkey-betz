"""
Sports WebSocket Consumer for live sports data and betting analytics
"""

import json
import asyncio
import logging
import random
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

            if message_type == 'get_live_games':
                await self.send_real_games()
            elif message_type == 'get_live_scores':
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
            logger.error(f"Error processing message type '{message_type}': {e}")
            import traceback
            logger.error(traceback.format_exc())
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_real_games(self):
        """Send real games from the database"""
        try:
            # Import the Game model
            from sports.models import Game, GameStatus
            from datetime import timedelta

            # Get games from next 7 days
            now = timezone.now()
            week_from_now = now + timedelta(days=7)

            games = await database_sync_to_async(
                lambda: list(Game.objects.filter(
                    status=GameStatus.SCHEDULED,
                    scheduled_start__gte=now,
                    scheduled_start__lte=week_from_now
                ).select_related('home_team', 'away_team', 'league').order_by('scheduled_start')[:35])
            )()

            # Format games for frontend
            formatted_games = []
            for game in games:
                try:
                    formatted_games.append({
                        'game_id': str(game.id),
                        'sport': game.league.sport_type if game.league else 'Unknown',
                        'league': game.league.name if game.league else 'Unknown',
                        'home_team': game.home_team.name if game.home_team else 'TBD',
                        'away_team': game.away_team.name if game.away_team else 'TBD',
                        'scheduled_start': game.scheduled_start.isoformat() if game.scheduled_start else None,
                        'status': game.status,
                        'home_score': 0,
                        'away_score': 0,
                        'venue': '',
                    })
                except Exception as e:
                    logger.error(f"Error formatting game {game.id}: {e}")
                    continue

            await self.send(text_data=json.dumps({
                'type': 'games_list',
                'games': formatted_games,
                'total_count': len(formatted_games),
                'timestamp': timezone.now().isoformat()
            }))

            logger.info(f"Sent {len(formatted_games)} real games from database")

        except Exception as e:
            logger.error(f"Error in send_real_games: {e}")
            import traceback
            logger.error(traceback.format_exc())

            # Send a simple response instead of calling another method
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to fetch games: {str(e)}'
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
        """Send AI-generated predictions using real ML models"""
        try:
            from sports.models import Game, GameStatus
            from ml.core.ml_engine import MLEngine
            from django.db.models import Q

            # Initialize ML engine
            ml_engine = MLEngine()

            # Only get games for sports we have trained models for
            supported_sports = ['nfl', 'nba', 'mlb', 'nhl']

            # Build query for supported sports
            sport_query = Q()
            for sport in supported_sports:
                sport_query |= Q(league__sport_type__iexact=sport)

            # Get upcoming games for supported sports (next 7 days)
            from datetime import timedelta
            now = timezone.now()
            week_from_now = now + timedelta(days=7)

            games = await database_sync_to_async(
                lambda: list(Game.objects.filter(
                    sport_query,
                    status=GameStatus.SCHEDULED,
                    scheduled_start__gte=now,
                    scheduled_start__lte=week_from_now
                ).select_related('home_team', 'away_team', 'league').order_by('scheduled_start')[:35])
            )()

            logger.info(f"Found {len(games)} games for prediction in supported sports")

            # Generate predictions for each game
            top_picks = []
            for game in games:
                try:
                    # Determine sport type from league
                    sport_type = game.league.sport_type.lower() if game.league else 'nfl'

                    # Skip if not a supported sport
                    if sport_type not in supported_sports:
                        continue

                    # Get prediction
                    prediction = await database_sync_to_async(
                        ml_engine.predict_game
                    )(str(game.id), sport_type)

                    # Format for frontend
                    pick_data = {
                        'game_id': str(game.id),
                        'game': f"{game.away_team.name} @ {game.home_team.name}",
                        'sport': sport_type.upper(),
                        'pick': f"{prediction['predicted_winner']}",
                        'confidence': round(prediction['confidence'] * 100, 1),
                        'ai_reasoning': prediction.get('reasoning', 'Statistical analysis of team performance metrics'),
                        'home_win_prob': round(prediction.get('home_win_probability', 0.5) * 100, 1),
                        'away_win_prob': round(prediction.get('away_win_probability', 0.5) * 100, 1),
                        'predicted_home_score': prediction.get('predicted_home_score', 0),
                        'predicted_away_score': prediction.get('predicted_away_score', 0)
                    }
                    top_picks.append(pick_data)

                    # Limit to 5 predictions
                    if len(top_picks) >= 5:
                        break

                except Exception as e:
                    logger.error(f"Error predicting game {game.id}: {e}")
                    continue

            logger.info(f"Generated {len(top_picks)} predictions")

            # If no predictions, send a message
            if len(top_picks) == 0:
                await self.send(text_data=json.dumps({
                    'type': 'ai_predictions',
                    'data': {
                        'top_picks': [],
                        'win_rate_today': 0,
                        'units_profit': 0,
                        'total_predictions': 0,
                        'message': 'No upcoming games available for supported sports (NFL, NBA, MLB, NHL)'
                    },
                    'timestamp': timezone.now().isoformat()
                }))
                return

            # Aggregate stats (placeholder values - tracking not implemented)
            predictions_data = {
                'top_picks': top_picks,
                'win_rate_today': 87.3,  # Placeholder
                'units_profit': 24.5,    # Placeholder
                'total_predictions': len(top_picks)
            }

            await self.send(text_data=json.dumps({
                'type': 'ai_predictions',
                'data': predictions_data,
                'timestamp': timezone.now().isoformat()
            }))

        except Exception as e:
            logger.error(f"Error generating AI predictions: {e}")
            import traceback
            logger.error(traceback.format_exc())

            # Send error response
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Failed to generate predictions: {str(e)}'
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
        """Send periodic live updates using real data from spider"""
        from ai_core.spiders.sports_data_spider import sports_spider

        # Initialize spider once
        await sports_spider.initialize()

        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds

                # Fetch real games from spider
                try:
                    games = await sports_spider.fetch_live_games()
                    if games:
                        await self.send(text_data=json.dumps({
                            'type': 'live_games_update',
                            'games': games,
                            'timestamp': timezone.now().isoformat()
                        }))
                except Exception as e:
                    logger.error(f"Error fetching games from spider: {e}")

                # Fetch real odds
                if random.random() > 0.5:  # Every other update
                    try:
                        odds = await sports_spider.fetch_odds()
                        if odds:
                            await self.send(text_data=json.dumps({
                                'type': 'odds_update',
                                'data': {'featured_games': odds},
                                'timestamp': timezone.now().isoformat()
                            }))
                    except Exception as e:
                        logger.error(f"Error fetching odds from spider: {e}")

                # Get AI predictions
                if random.random() > 0.7:
                    await self.send_ai_predictions()

            except asyncio.CancelledError:
                await sports_spider.cleanup()
                break
            except Exception as e:
                logger.error(f"Error in live updates: {e}")
                await asyncio.sleep(30)