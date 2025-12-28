"""
WebSocket consumers for real-time sports data updates
"""
import logging
from datetime import datetime
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from typing import Any, Dict

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
        elif message_type == 'get_live_games':
            await self.send_live_games()
        elif message_type == 'get_live_scores':
            await self.send_live_scores()
        elif message_type == 'get_ai_predictions':
            await self.send_ai_predictions()
        elif message_type == 'get_predictions':  # Alias for get_ai_predictions
            await self.send_ai_predictions()
        elif message_type == 'get_betting_history':
            await self.send_betting_history()
        elif message_type == 'get_sport_details':
            await self.send_sport_details(content.get('sport'))
        elif message_type == 'place_bet':
            await self.handle_place_bet(content.get('bet'))
        elif message_type == 'get_nfl_news':
            await self.send_nfl_news()
        elif message_type == 'get_game_prediction':
            await self.send_game_prediction(content.get('game_id'))
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

    async def send_live_games(self):
        """Send real games from the database (next 36 hours)"""
        from .models import Game
        from datetime import timedelta

        try:
            # Use local time to determine "today" - convert to UTC for database query
            local_now = datetime.now()
            local_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
            local_end = local_start + timedelta(hours=48)  # Today + tomorrow

            # Convert local times to UTC for database query (MST/MDT timezone)
            import pytz
            mountain = pytz.timezone('America/Denver')
            local_start_aware = mountain.localize(local_start)
            local_end_aware = mountain.localize(local_end)

            now_utc = local_start_aware.astimezone(pytz.UTC)
            end_time = local_end_aware.astimezone(pytz.UTC)

            # Get upcoming games (today + tomorrow in local time)
            games = await database_sync_to_async(
                lambda: list(Game.objects.filter(
                    scheduled_start__gte=now_utc,
                    scheduled_start__lt=end_time
                ).select_related('home_team', 'away_team', 'league').order_by('scheduled_start'))
            )()

            # Format games for frontend
            formatted_games = []
            for game in games:
                # Get team names with cities if available
                home_team_name = game.home_team.name if game.home_team else 'TBD'
                away_team_name = game.away_team.name if game.away_team else 'TBD'

                # Add city if available
                if game.home_team and game.home_team.city:
                    home_team_name = f"{game.home_team.city} {home_team_name}"
                if game.away_team and game.away_team.city:
                    away_team_name = f"{game.away_team.city} {away_team_name}"

                formatted_games.append({
                    'game_id': str(game.id),
                    'sport': game.league.sport_type.lower() if game.league and game.league.sport_type else 'unknown',
                    'league': game.league.name if game.league else 'Unknown',
                    'league_abbr': game.league.abbreviation if game.league else 'N/A',
                    'home_team': home_team_name,
                    'home_team_name': home_team_name,  # Add for frontend compatibility
                    'away_team': away_team_name,
                    'away_team_name': away_team_name,  # Add for frontend compatibility
                    'scheduled_start': game.scheduled_start.isoformat() if game.scheduled_start else None,
                    'game_time': game.scheduled_start.isoformat() if game.scheduled_start else None,
                    'status': game.status,
                    'home_score': game.home_score or 0,
                    'home_team_score': game.home_score or 0,  # Add for frontend compatibility
                    'away_score': game.away_score or 0,
                    'away_team_score': game.away_score or 0,  # Add for frontend compatibility
                    'venue': game.venue_name if hasattr(game, 'venue_name') else '',
                })

            await self.send_json({
                'type': 'games_list',
                'games': formatted_games,
                'total_count': len(formatted_games)
            })

            logger.info(f"Sent {len(formatted_games)} games for today+tomorrow (local: {local_now.strftime('%Y-%m-%d %H:%M %Z')})")

        except Exception as e:
            logger.error(f"Error fetching real games: {e}")
            # Send empty list on error
            await self.send_json({
                'type': 'games_list',
                'games': [],
                'error': str(e)
            })

    async def send_live_scores(self):
        """Send real live scores from ESPN API (fallback to database if ESPN unavailable)"""
        from datetime import datetime
        import requests

        try:
            # Use local datetime for ESPN API (ESPN uses local game times, not UTC)
            local_now = datetime.now()
            today = local_now.strftime('%Y%m%d')

            logger.info(f"Fetching ESPN scores for date: {today} (local time: {local_now.strftime('%Y-%m-%d %H:%M:%S')})")
            url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={today}"

            # Fetch live data from ESPN
            response = await database_sync_to_async(requests.get)(url, timeout=10)
            data = response.json()

            live_games = []
            for event in data.get('events', []):
                competition = event.get('competitions', [{}])[0]
                competitors = competition.get('competitors', [])

                if len(competitors) >= 2:
                    # competitors[0] is home, competitors[1] is away
                    home_competitor = competitors[0]
                    away_competitor = competitors[1]

                    # Get game situation data
                    situation = competition.get('situation', {})

                    game_data = {
                        'game_id': event.get('id'),
                        'status': event.get('status', {}).get('type', {}).get('name', 'Unknown'),
                        'period': event.get('status', {}).get('period', 0),
                        'clock': event.get('status', {}).get('displayClock', ''),
                        'home_team': home_competitor.get('team', {}).get('displayName', ''),
                        'home_team_abbr': home_competitor.get('team', {}).get('abbreviation', ''),
                        'home_score': int(home_competitor.get('score', 0)),
                        'home_logo': home_competitor.get('team', {}).get('logo', ''),
                        'away_team': away_competitor.get('team', {}).get('displayName', ''),
                        'away_team_abbr': away_competitor.get('team', {}).get('abbreviation', ''),
                        'away_score': int(away_competitor.get('score', 0)),
                        'away_logo': away_competitor.get('team', {}).get('logo', ''),
                        'possession': situation.get('possession', ''),
                        'down': situation.get('downDistanceText', ''),
                        'field_position': situation.get('possessionText', ''),
                        'last_play': situation.get('lastPlay', {}).get('text', ''),
                        'broadcast': competition.get('broadcast', ''),
                    }
                    live_games.append(game_data)

            logger.info(f"ESPN API returned {len(live_games)} live NFL games for {today}")

            await self.send_json({
                'type': 'live_scores',
                'games': live_games,
                'timestamp': local_now.isoformat(),
                'count': len(live_games)
            })

        except Exception as e:
            logger.error(f"Error fetching live scores from ESPN: {e}")
            await self.send_json({
                'type': 'live_scores',
                'games': [],
                'error': str(e)
            })

    async def send_nfl_news(self):
        """Fetch and send NFL news from ESPN"""
        import requests

        try:
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/news"

            # Fetch news from ESPN
            response = await database_sync_to_async(requests.get)(url, timeout=10)
            data = response.json()

            articles_data = data.get('articles', [])
            news_items = []

            for article in articles_data[:15]:  # Get top 15 articles
                # Extract image URL if available
                image_url = ''
                if article.get('images'):
                    image_url = article['images'][0].get('url', '')

                news_item = {
                    'headline': article.get('headline', ''),
                    'description': article.get('description', ''),
                    'link': article.get('links', {}).get('web', {}).get('href', ''),
                    'published': article.get('published', ''),
                    'image': image_url,
                    'type': article.get('type', 'news')
                }
                news_items.append(news_item)

            await self.send_json({
                'type': 'nfl_news',
                'articles': news_items,
                'count': len(news_items)
            })

            logger.info(f"Sent {len(news_items)} NFL news articles")

        except Exception as e:
            logger.error(f"Error fetching NFL news from ESPN: {e}")
            await self.send_json({
                'type': 'nfl_news',
                'articles': [],
                'error': str(e)
            })

    async def send_game_prediction(self, game_id: str, sport_type: str = None):
        """
        Send AI prediction for a specific game (multi-sport support)

        Args:
            game_id: ID of game to predict
            sport_type: Optional sport type ('nfl', 'nba', 'mlb', 'nhl')
                       If not provided, auto-detects from game's league
        """
        from ml.core.ml_engine import MLEngine
        from sports.models import Game

        try:
            # Initialize ML engine
            ml_engine = await database_sync_to_async(MLEngine)()

            # Auto-detect sport if not provided
            if not sport_type:
                game = await database_sync_to_async(
                    Game.objects.select_related('league').get
                )(id=game_id)
                sport_type = game.league.sport_type

            # Get prediction using multi-sport method
            prediction = await database_sync_to_async(
                ml_engine.predict_game
            )(game_id, sport_type)

            await self.send_json({
                'type': 'game_prediction',
                'game_id': game_id,
                'sport': sport_type,
                'prediction': prediction
            })

            logger.info(f"Sent {sport_type.upper()} prediction for game {game_id}")

        except Exception as e:
            logger.error(f"Prediction error for game {game_id}: {e}")
            await self.send_json({
                'type': 'error',
                'message': f'Prediction failed: {str(e)}'
            })

    async def send_ai_predictions(self):
        """Send AI-generated predictions using real ML models with database tracking"""
        from sports.models import Game, GameStatus
        from ml.core.ml_engine import MLEngine
        from django.db.models import Q
        from datetime import datetime, timedelta
        import pytz
        from sports.prediction_tracker import save_ml_prediction, calculate_today_stats, format_prediction_for_frontend

        try:
            # Initialize ML engine
            ml_engine = MLEngine()

            # Only get games for sports we have trained models for
            supported_sports = ['nfl', 'nba', 'mlb', 'nhl']

            # Build query for supported sports
            sport_query = Q()
            for sport in supported_sports:
                sport_query |= Q(league__sport_type__iexact=sport)

            # Use local time to determine "today" - convert to UTC for database query
            # This matches the logic in send_games_list() for consistency
            local_now = datetime.now()
            local_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
            local_end = local_start + timedelta(hours=48)  # Today + tomorrow

            # Convert local times to UTC for database query (MST/MDT timezone)
            mountain = pytz.timezone('America/Denver')
            local_start_aware = mountain.localize(local_start)
            local_end_aware = mountain.localize(local_end)

            now_utc = local_start_aware.astimezone(pytz.UTC)
            end_time = local_end_aware.astimezone(pytz.UTC)

            # Get upcoming games for supported sports (today + tomorrow in local time)
            games = await database_sync_to_async(
                lambda: list(Game.objects.filter(
                    sport_query,
                    status=GameStatus.SCHEDULED,
                    scheduled_start__gte=now_utc,
                    scheduled_start__lt=end_time
                ).select_related('home_team', 'away_team', 'league').order_by('scheduled_start')[:10])
            )()

            logger.info(f"Found {len(games)} games for prediction in supported sports (today+tomorrow)")

            # Generate predictions for each game
            top_picks = []
            for game in games:
                try:
                    # Determine sport type from league
                    sport_type = game.league.sport_type.lower() if game.league else 'nfl'

                    # Skip if not a supported sport
                    if sport_type not in supported_sports:
                        continue

                    # Get prediction from ML Engine
                    prediction = await database_sync_to_async(
                        ml_engine.predict_game
                    )(str(game.id), sport_type)

                    # Save prediction to database
                    ml_prediction = await database_sync_to_async(
                        save_ml_prediction
                    )(game, prediction, sport_type)

                    # Format for frontend
                    pick_data = await database_sync_to_async(
                        format_prediction_for_frontend
                    )(game, prediction, ml_prediction, sport_type)

                    top_picks.append(pick_data)

                    # Limit to 5 predictions
                    if len(top_picks) >= 5:
                        break

                except Exception as e:
                    logger.error(f"Error predicting game {game.id}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    continue

            logger.info(f"Generated {len(top_picks)} predictions")

            # If no predictions, send a message
            if len(top_picks) == 0:
                await self.send_json({
                    'type': 'ai_predictions',
                    'data': {
                        'top_picks': [],
                        'win_rate_today': 0,
                        'units_profit': 0,
                        'total_predictions': 0,
                        'message': 'No upcoming games available for supported sports (NFL, NBA, MLB, NHL)'
                    }
                })
                return

            # Calculate REAL win rate and profit from database
            stats = await database_sync_to_async(calculate_today_stats)()

            # Build response with REAL data
            predictions_data = {
                'top_picks': top_picks,
                'win_rate_today': stats['win_rate'],  # REAL win rate from tracked predictions
                'units_profit': stats['profit'],       # REAL profit calculation
                'total_predictions': len(top_picks),
                'predictions_evaluated_today': stats['total_evaluated']
            }

            await self.send_json({
                'type': 'ai_predictions',
                'data': predictions_data
            })

        except Exception as e:
            logger.error(f"Error generating AI predictions: {e}")
            import traceback
            logger.error(traceback.format_exc())

            # Send error response
            await self.send_json({
                'type': 'error',
                'message': f'Failed to generate predictions: {str(e)}'
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

    async def send_live_games(self):
        """Send real games from the database (next 36 hours)"""
        from .models import Game
        from datetime import timedelta

        try:
            # Use local time to determine "today" - convert to UTC for database query
            local_now = datetime.now()
            local_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
            local_end = local_start + timedelta(hours=48)  # Today + tomorrow

            # Convert local times to UTC for database query (MST/MDT timezone)
            import pytz
            mountain = pytz.timezone('America/Denver')
            local_start_aware = mountain.localize(local_start)
            local_end_aware = mountain.localize(local_end)

            now_utc = local_start_aware.astimezone(pytz.UTC)
            end_time = local_end_aware.astimezone(pytz.UTC)

            # Get upcoming games (today + tomorrow in local time)
            games = await database_sync_to_async(
                lambda: list(Game.objects.filter(
                    scheduled_start__gte=now_utc,
                    scheduled_start__lt=end_time
                ).select_related('home_team', 'away_team', 'league').order_by('scheduled_start'))
            )()

            # Format games for frontend
            formatted_games = []
            for game in games:
                # Get team names with cities if available
                home_team_name = game.home_team.name if game.home_team else 'TBD'
                away_team_name = game.away_team.name if game.away_team else 'TBD'

                # Add city if available
                if game.home_team and game.home_team.city:
                    home_team_name = f"{game.home_team.city} {home_team_name}"
                if game.away_team and game.away_team.city:
                    away_team_name = f"{game.away_team.city} {away_team_name}"

                formatted_games.append({
                    'game_id': str(game.id),
                    'sport': game.league.sport_type.lower() if game.league and game.league.sport_type else 'unknown',
                    'league': game.league.name if game.league else 'Unknown',
                    'league_abbr': game.league.abbreviation if game.league else 'N/A',
                    'home_team': home_team_name,
                    'home_team_name': home_team_name,  # Add for frontend compatibility
                    'away_team': away_team_name,
                    'away_team_name': away_team_name,  # Add for frontend compatibility
                    'scheduled_start': game.scheduled_start.isoformat() if game.scheduled_start else None,
                    'game_time': game.scheduled_start.isoformat() if game.scheduled_start else None,
                    'status': game.status,
                    'home_score': game.home_score or 0,
                    'home_team_score': game.home_score or 0,  # Add for frontend compatibility
                    'away_score': game.away_score or 0,
                    'away_team_score': game.away_score or 0,  # Add for frontend compatibility
                    'venue': game.venue_name if hasattr(game, 'venue_name') else '',
                })

            await self.send_json({
                'type': 'games_list',
                'games': formatted_games,
                'total_count': len(formatted_games)
            })

            logger.info(f"Sent {len(formatted_games)} games for today+tomorrow (local: {local_now.strftime('%Y-%m-%d %H:%M %Z')})")

        except Exception as e:
            logger.error(f"Error fetching real games: {e}")
            # Send empty list on error
            await self.send_json({
                'type': 'games_list',
                'games': [],
                'error': str(e)
            })

    async def send_live_scores(self):
        """Send real live scores from ESPN API (fallback to database if ESPN unavailable)"""
        from datetime import datetime
        import requests

        try:
            # Use local datetime for ESPN API (ESPN uses local game times, not UTC)
            local_now = datetime.now()
            today = local_now.strftime('%Y%m%d')

            logger.info(f"Fetching ESPN scores for date: {today} (local time: {local_now.strftime('%Y-%m-%d %H:%M:%S')})")
            url = f"https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={today}"

            # Fetch live data from ESPN
            response = await database_sync_to_async(requests.get)(url, timeout=10)
            data = response.json()

            live_games = []
            for event in data.get('events', []):
                competition = event.get('competitions', [{}])[0]
                competitors = competition.get('competitors', [])

                if len(competitors) >= 2:
                    # competitors[0] is home, competitors[1] is away
                    home_competitor = competitors[0]
                    away_competitor = competitors[1]

                    # Get game situation data
                    situation = competition.get('situation', {})

                    game_data = {
                        'game_id': event.get('id'),
                        'status': event.get('status', {}).get('type', {}).get('name', 'Unknown'),
                        'period': event.get('status', {}).get('period', 0),
                        'clock': event.get('status', {}).get('displayClock', ''),
                        'home_team': home_competitor.get('team', {}).get('displayName', ''),
                        'home_team_abbr': home_competitor.get('team', {}).get('abbreviation', ''),
                        'home_score': int(home_competitor.get('score', 0)),
                        'home_logo': home_competitor.get('team', {}).get('logo', ''),
                        'away_team': away_competitor.get('team', {}).get('displayName', ''),
                        'away_team_abbr': away_competitor.get('team', {}).get('abbreviation', ''),
                        'away_score': int(away_competitor.get('score', 0)),
                        'away_logo': away_competitor.get('team', {}).get('logo', ''),
                        'possession': situation.get('possession', ''),
                        'down': situation.get('downDistanceText', ''),
                        'field_position': situation.get('possessionText', ''),
                        'last_play': situation.get('lastPlay', {}).get('text', ''),
                        'broadcast': competition.get('broadcast', ''),
                    }
                    live_games.append(game_data)

            logger.info(f"ESPN API returned {len(live_games)} live NFL games for {today}")

            await self.send_json({
                'type': 'live_scores',
                'games': live_games,
                'timestamp': local_now.isoformat(),
                'count': len(live_games)
            })

        except Exception as e:
            logger.error(f"Error fetching live scores from ESPN: {e}")
            await self.send_json({
                'type': 'live_scores',
                'games': [],
                'error': str(e)
            })

    async def send_nfl_news(self):
        """Fetch and send NFL news from ESPN"""
        import requests

        try:
            url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/news"

            # Fetch news from ESPN
            response = await database_sync_to_async(requests.get)(url, timeout=10)
            data = response.json()

            articles_data = data.get('articles', [])
            news_items = []

            for article in articles_data[:15]:  # Get top 15 articles
                # Extract image URL if available
                image_url = ''
                if article.get('images'):
                    image_url = article['images'][0].get('url', '')

                news_item = {
                    'headline': article.get('headline', ''),
                    'description': article.get('description', ''),
                    'link': article.get('links', {}).get('web', {}).get('href', ''),
                    'published': article.get('published', ''),
                    'image': image_url,
                    'type': article.get('type', 'news')
                }
                news_items.append(news_item)

            await self.send_json({
                'type': 'nfl_news',
                'articles': news_items,
                'count': len(news_items)
            })

            logger.info(f"Sent {len(news_items)} NFL news articles")

        except Exception as e:
            logger.error(f"Error fetching NFL news from ESPN: {e}")
            await self.send_json({
                'type': 'nfl_news',
                'articles': [],
                'error': str(e)
            })

    async def send_game_prediction(self, game_id: str, sport_type: str = None):
        """
        Send AI prediction for a specific game (multi-sport support)

        Args:
            game_id: ID of game to predict
            sport_type: Optional sport type ('nfl', 'nba', 'mlb', 'nhl')
                       If not provided, auto-detects from game's league
        """
        from ml.core.ml_engine import MLEngine
        from sports.models import Game

        try:
            # Initialize ML engine
            ml_engine = await database_sync_to_async(MLEngine)()

            # Auto-detect sport if not provided
            if not sport_type:
                game = await database_sync_to_async(
                    Game.objects.select_related('league').get
                )(id=game_id)
                sport_type = game.league.sport_type

            # Get prediction using multi-sport method
            prediction = await database_sync_to_async(
                ml_engine.predict_game
            )(game_id, sport_type)

            await self.send_json({
                'type': 'game_prediction',
                'game_id': game_id,
                'sport': sport_type,
                'prediction': prediction
            })

            logger.info(f"Sent {sport_type.upper()} prediction for game {game_id}")

        except Exception as e:
            logger.error(f"Prediction error for game {game_id}: {e}")
            await self.send_json({
                'type': 'error',
                'message': f'Prediction failed: {str(e)}'
            })

    async def send_ai_predictions(self):
        """Send AI-generated predictions using real ML models with database tracking"""
        from sports.models import Game, GameStatus
        from ml.core.ml_engine import MLEngine
        from django.db.models import Q
        from datetime import datetime, timedelta
        import pytz
        from sports.prediction_tracker import save_ml_prediction, calculate_today_stats, format_prediction_for_frontend

        try:
            # Initialize ML engine
            ml_engine = MLEngine()

            # Only get games for sports we have trained models for
            supported_sports = ['nfl', 'nba', 'mlb', 'nhl']

            # Build query for supported sports
            sport_query = Q()
            for sport in supported_sports:
                sport_query |= Q(league__sport_type__iexact=sport)

            # Use local time to determine "today" - convert to UTC for database query
            # This matches the logic in send_games_list() for consistency
            local_now = datetime.now()
            local_start = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
            local_end = local_start + timedelta(hours=48)  # Today + tomorrow

            # Convert local times to UTC for database query (MST/MDT timezone)
            mountain = pytz.timezone('America/Denver')
            local_start_aware = mountain.localize(local_start)
            local_end_aware = mountain.localize(local_end)

            now_utc = local_start_aware.astimezone(pytz.UTC)
            end_time = local_end_aware.astimezone(pytz.UTC)

            # Get upcoming games for supported sports (today + tomorrow in local time)
            games = await database_sync_to_async(
                lambda: list(Game.objects.filter(
                    sport_query,
                    status=GameStatus.SCHEDULED,
                    scheduled_start__gte=now_utc,
                    scheduled_start__lt=end_time
                ).select_related('home_team', 'away_team', 'league').order_by('scheduled_start')[:10])
            )()

            logger.info(f"Found {len(games)} games for prediction in supported sports (today+tomorrow)")

            # Generate predictions for each game
            top_picks = []
            for game in games:
                try:
                    # Determine sport type from league
                    sport_type = game.league.sport_type.lower() if game.league else 'nfl'

                    # Skip if not a supported sport
                    if sport_type not in supported_sports:
                        continue

                    # Get prediction from ML Engine
                    prediction = await database_sync_to_async(
                        ml_engine.predict_game
                    )(str(game.id), sport_type)

                    # Save prediction to database
                    ml_prediction = await database_sync_to_async(
                        save_ml_prediction
                    )(game, prediction, sport_type)

                    # Format for frontend
                    pick_data = await database_sync_to_async(
                        format_prediction_for_frontend
                    )(game, prediction, ml_prediction, sport_type)

                    top_picks.append(pick_data)

                    # Limit to 5 predictions
                    if len(top_picks) >= 5:
                        break

                except Exception as e:
                    logger.error(f"Error predicting game {game.id}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    continue

            logger.info(f"Generated {len(top_picks)} predictions")

            # If no predictions, send a message
            if len(top_picks) == 0:
                await self.send_json({
                    'type': 'ai_predictions',
                    'data': {
                        'top_picks': [],
                        'win_rate_today': 0,
                        'units_profit': 0,
                        'total_predictions': 0,
                        'message': 'No upcoming games available for supported sports (NFL, NBA, MLB, NHL)'
                    }
                })
                return

            # Calculate REAL win rate and profit from database
            stats = await database_sync_to_async(calculate_today_stats)()

            # Build response with REAL data
            predictions_data = {
                'top_picks': top_picks,
                'win_rate_today': stats['win_rate'],  # REAL win rate from tracked predictions
                'units_profit': stats['profit'],       # REAL profit calculation
                'total_predictions': len(top_picks),
                'predictions_evaluated_today': stats['total_evaluated']
            }

            await self.send_json({
                'type': 'ai_predictions',
                'data': predictions_data
            })

        except Exception as e:
            logger.error(f"Error generating AI predictions: {e}")
            import traceback
            logger.error(traceback.format_exc())

            # Send error response
            await self.send_json({
                'type': 'error',
                'message': f'Failed to generate predictions: {str(e)}'
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
