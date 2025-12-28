"""
WebSocket consumer for real-time sports updates and odds refresh
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class SportsUpdatesConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time sports data updates"""

    async def connect(self):
        """Accept WebSocket connection"""
        self.room_name = 'sports_updates'
        self.room_group_name = f'sports_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to sports updates channel'
        }))

        logger.info(f"WebSocket connected: {self.channel_name}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        logger.info(f"WebSocket disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """Handle messages from WebSocket client"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'force_odds_update':
                await self.handle_force_odds_update(data)
            elif message_type == 'get_update_status':
                await self.handle_get_status(data)
            elif message_type == 'subscribe_game':
                await self.handle_subscribe_game(data)
            elif message_type == 'unsubscribe_game':
                await self.handle_unsubscribe_game(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def handle_force_odds_update(self, data):
        """Force update odds for a specific game or league"""
        game_id = data.get('game_id')
        league = data.get('league')

        await self.send(text_data=json.dumps({
            'type': 'update_started',
            'game_id': game_id,
            'league': league,
            'timestamp': timezone.now().isoformat()
        }))

        try:
            if game_id:
                # Update specific game
                result = await self.update_game_odds(game_id)

                await self.send(text_data=json.dumps({
                    'type': 'update_complete',
                    'game_id': game_id,
                    'result': result,
                    'timestamp': timezone.now().isoformat()
                }))

                # Broadcast to all clients in the room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'odds_updated',
                        'game_id': game_id,
                        'result': result
                    }
                )

            elif league:
                # Update entire league
                result = await self.update_league_odds(league)

                await self.send(text_data=json.dumps({
                    'type': 'update_complete',
                    'league': league,
                    'result': result,
                    'timestamp': timezone.now().isoformat()
                }))

                # Broadcast to all clients
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'league_updated',
                        'league': league,
                        'result': result
                    }
                )

        except Exception as e:
            logger.error(f"Error updating odds: {e}")
            await self.send(text_data=json.dumps({
                'type': 'update_failed',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }))

    async def handle_get_status(self, data):
        """Get current update status for games"""
        league = data.get('league', 'all')

        status = await self.get_games_status(league)

        await self.send(text_data=json.dumps({
            'type': 'status_update',
            'league': league,
            'status': status,
            'timestamp': timezone.now().isoformat()
        }))

    async def handle_subscribe_game(self, data):
        """Subscribe to updates for a specific game"""
        game_id = data.get('game_id')

        if game_id:
            game_group = f'game_{game_id}'
            await self.channel_layer.group_add(
                game_group,
                self.channel_name
            )

            await self.send(text_data=json.dumps({
                'type': 'subscribed',
                'game_id': game_id,
                'message': f'Subscribed to game {game_id} updates'
            }))

    async def handle_unsubscribe_game(self, data):
        """Unsubscribe from updates for a specific game"""
        game_id = data.get('game_id')

        if game_id:
            game_group = f'game_{game_id}'
            await self.channel_layer.group_discard(
                game_group,
                self.channel_name
            )

            await self.send(text_data=json.dumps({
                'type': 'unsubscribed',
                'game_id': game_id,
                'message': f'Unsubscribed from game {game_id} updates'
            }))

    # Database operations
    @database_sync_to_async
    def update_game_odds(self, game_id):
        """Update odds for a specific game"""
        try:
            from sports.data_enrichment import data_enricher
            result = data_enricher.enrich_game_odds(game_id, force_refresh=True)
            return result
        except Exception as e:
            logger.error(f"Failed to update game {game_id}: {e}")
            return {'error': str(e)}

    @database_sync_to_async
    def update_league_odds(self, league):
        """Update odds for entire league"""
        try:
            from sports.data_enrichment import data_enricher
            result = data_enricher.enrich_league_odds_batch(league.upper())
            return result
        except Exception as e:
            logger.error(f"Failed to update league {league}: {e}")
            return {'error': str(e)}

    @database_sync_to_async
    def get_games_status(self, league):
        """Get status of games and their last update times"""
        try:
            from sports.models import Game

            games_query = Game.objects.filter(
                is_active=True,
                status__in=['scheduled', 'live', 'status_in_progress']
            )

            if league != 'all':
                games_query = games_query.filter(league__abbreviation=league.upper())

            games = games_query.select_related('home_team', 'away_team', 'league')[:20]

            status_list = []
            for game in games:
                # Get last odds update time
                markets = game.markets.filter(is_active=True)
                last_update = None
                cache_status = 'no_data'

                if markets.exists():
                    last_update = markets.latest('updated_at').updated_at
                    time_since_update = timezone.now() - last_update

                    # Determine cache status
                    if game.status in ['live', 'status_in_progress']:
                        if time_since_update < timedelta(minutes=30):
                            cache_status = 'fresh'
                        else:
                            cache_status = 'stale'
                    else:
                        if time_since_update < timedelta(hours=2):
                            cache_status = 'fresh'
                        else:
                            cache_status = 'stale'

                status_list.append({
                    'game_id': str(game.id),
                    'matchup': f"{game.away_team.abbreviation} @ {game.home_team.abbreviation}",
                    'league': game.league.abbreviation,
                    'status': game.status,
                    'start_time': game.scheduled_start.isoformat(),
                    'last_odds_update': last_update.isoformat() if last_update else None,
                    'cache_status': cache_status,
                    'markets_count': markets.count()
                })

            return status_list

        except Exception as e:
            logger.error(f"Failed to get games status: {e}")
            return []

    # Handle messages from channel layer
    async def odds_updated(self, event):
        """Handle odds updated event"""
        await self.send(text_data=json.dumps({
            'type': 'odds_updated',
            'game_id': event['game_id'],
            'result': event['result'],
            'timestamp': timezone.now().isoformat()
        }))

    async def league_updated(self, event):
        """Handle league updated event"""
        await self.send(text_data=json.dumps({
            'type': 'league_updated',
            'league': event['league'],
            'result': event['result'],
            'timestamp': timezone.now().isoformat()
        }))