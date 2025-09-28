import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime
import random
from decimal import Decimal

class SportsBettingConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time sports betting updates"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = 'sports_betting_live'
        self.user_subscriptions = set()
        self.ai_agents = {
            'odds_scraper': {'status': 'active', 'updates_per_min': 0},
            'value_finder': {'status': 'analyzing', 'opportunities': 0},
            'line_predictor': {'status': 'calculating', 'accuracy': 87.5},
            'arbitrage_hunter': {'status': 'scanning', 'arbs_found': 0},
            'sentiment_analyzer': {'status': 'active', 'signals': 0},
            'weather_impact': {'status': 'monitoring', 'alerts': 0},
            'injury_report': {'status': 'active', 'updates': 0},
            'pattern_analyzer': {'status': 'processing', 'patterns': 0},
            'sharp_tracker': {'status': 'tracking', 'sharp_bets': 0},
            'live_betting': {'status': 'ready', 'opportunities': 0}
        }

    async def connect(self):
        """Handle WebSocket connection"""
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to Sports AI Betting System',
            'timestamp': datetime.now().isoformat(),
            'agents': self.ai_agents
        }))

        # Start simulated data updates
        asyncio.create_task(self.simulate_odds_updates())
        asyncio.create_task(self.simulate_agent_activity())
        asyncio.create_task(self.simulate_ai_insights())

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'subscribe':
                await self.handle_subscription(data)
            elif message_type == 'change_sport':
                await self.handle_sport_change(data)
            elif message_type == 'place_bet':
                await self.handle_place_bet(data)
            elif message_type == 'voice_command':
                await self.handle_voice_command(data)
            elif message_type == 'get_ai_recommendation':
                await self.handle_ai_recommendation(data)
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

    async def handle_subscription(self, data):
        """Handle subscription to specific sports/updates"""
        sports = data.get('sports', [])
        updates = data.get('updates', [])

        self.user_subscriptions.update(sports)

        await self.send(text_data=json.dumps({
            'type': 'subscription_confirmed',
            'sports': list(self.user_subscriptions),
            'updates': updates
        }))

    async def handle_sport_change(self, data):
        """Handle sport selection change"""
        sport = data.get('sport')

        # Send sport-specific odds
        await self.send_sport_odds(sport)

    async def handle_place_bet(self, data):
        """Handle bet placement"""
        bet_details = data.get('bet')

        # Simulate bet processing
        await self.send(text_data=json.dumps({
            'type': 'bet_confirmation',
            'status': 'processing',
            'bet': bet_details,
            'timestamp': datetime.now().isoformat()
        }))

        # Simulate processing delay
        await asyncio.sleep(1)

        # Confirm bet
        await self.send(text_data=json.dumps({
            'type': 'bet_placed',
            'status': 'success',
            'bet_id': f"BET{random.randint(100000, 999999)}",
            'bet': bet_details,
            'timestamp': datetime.now().isoformat()
        }))

    async def handle_voice_command(self, data):
        """Handle voice commands"""
        command = data.get('command', '').lower()

        response = self.process_voice_command(command)

        await self.send(text_data=json.dumps({
            'type': 'voice_response',
            'command': command,
            'response': response,
            'timestamp': datetime.now().isoformat()
        }))

    async def handle_ai_recommendation(self, data):
        """Generate AI betting recommendation"""
        game_id = data.get('game_id')

        # Simulate AI analysis
        recommendation = {
            'game_id': game_id,
            'confidence': random.uniform(75, 95),
            'recommended_bet': random.choice(['spread', 'total', 'moneyline']),
            'reasoning': 'Based on 247 data points including recent performance, injuries, and weather conditions',
            'expected_value': f"+{random.uniform(2, 8):.1f}%"
        }

        await self.send(text_data=json.dumps({
            'type': 'ai_recommendation',
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }))

    async def send_sport_odds(self, sport):
        """Send odds for specific sport"""
        # Generate mock odds data
        games = self.generate_mock_games(sport)

        await self.send(text_data=json.dumps({
            'type': 'sport_odds',
            'sport': sport,
            'games': games,
            'timestamp': datetime.now().isoformat()
        }))

    def process_voice_command(self, command):
        """Process voice commands and return response"""
        if 'best bet' in command:
            return "Lakers -7.5 shows the highest expected value at +3.2%"
        elif 'bankroll' in command:
            return "Your current bankroll is $10,000 with $2,500 available for betting"
        elif 'nfl' in command:
            return "Switching to NFL games"
        elif 'value' in command:
            return "I found 3 value betting opportunities with positive expected value"
        else:
            return f"Processing command: {command}"

    def generate_mock_games(self, sport):
        """Generate mock game data"""
        teams = {
            'nfl': [('Chiefs', 'Bills'), ('Cowboys', 'Eagles'), ('Packers', 'Bears')],
            'nba': [('Lakers', 'Suns'), ('Celtics', 'Heat'), ('Warriors', 'Clippers')],
            'mlb': [('Yankees', 'Red Sox'), ('Dodgers', 'Giants'), ('Astros', 'Rangers')]
        }

        sport_teams = teams.get(sport, teams['nfl'])
        games = []

        for home, away in sport_teams:
            games.append({
                'id': f"GAME{random.randint(1000, 9999)}",
                'home_team': home,
                'away_team': away,
                'spread': {
                    'home': random.uniform(-10, 10),
                    'away': random.uniform(-10, 10),
                    'home_odds': random.choice([-110, -105, -115, -120]),
                    'away_odds': random.choice([-110, -105, -115, -120])
                },
                'total': random.uniform(200, 250) if sport == 'nba' else random.uniform(40, 60),
                'moneyline': {
                    'home': random.choice([-150, -200, +110, +150]),
                    'away': random.choice([-150, -200, +110, +150])
                },
                'ai_confidence': random.uniform(60, 95),
                'value_indicator': random.choice(['high', 'medium', 'low', None])
            })

        return games

    async def simulate_odds_updates(self):
        """Simulate real-time odds updates"""
        while True:
            await asyncio.sleep(random.uniform(3, 8))

            # Generate odds update
            update = {
                'type': 'odds_update',
                'payload': {
                    'gameId': f"GAME{random.randint(1000, 9999)}",
                    'spread': random.uniform(-10, 10),
                    'total': random.uniform(200, 250),
                    'movement': random.choice(['up', 'down']),
                    'timestamp': datetime.now().isoformat()
                }
            }

            await self.send(text_data=json.dumps(update))

            # Update agent metrics
            self.ai_agents['odds_scraper']['updates_per_min'] = random.randint(200, 300)

    async def simulate_agent_activity(self):
        """Simulate AI agent activity"""
        while True:
            await asyncio.sleep(random.uniform(5, 10))

            # Random agent update
            agent_name = random.choice(list(self.ai_agents.keys()))

            if agent_name == 'value_finder':
                self.ai_agents[agent_name]['opportunities'] = random.randint(1, 5)
            elif agent_name == 'arbitrage_hunter':
                self.ai_agents[agent_name]['arbs_found'] = random.randint(0, 2)
            elif agent_name == 'sharp_tracker':
                self.ai_agents[agent_name]['sharp_bets'] = random.randint(1, 4)

            update = {
                'type': 'agent_update',
                'payload': {
                    'agent': agent_name,
                    'status': self.ai_agents[agent_name],
                    'timestamp': datetime.now().isoformat()
                }
            }

            await self.send(text_data=json.dumps(update))

    async def simulate_ai_insights(self):
        """Simulate AI insights generation"""
        insights = [
            {
                'type': 'value_bet',
                'title': 'High Value Alert',
                'message': 'Lakers -7.5 showing +3.2% expected value based on injury reports',
                'severity': 'high'
            },
            {
                'type': 'line_movement',
                'title': 'Line Movement Detected',
                'message': 'Chiefs line moving from -3.5 to -3.0, sharp money on Bills',
                'severity': 'medium'
            },
            {
                'type': 'weather',
                'title': 'Weather Impact',
                'message': 'Wind 15mph+ expected for TNF, consider under 48.5',
                'severity': 'low'
            },
            {
                'type': 'arbitrage',
                'title': 'Arbitrage Opportunity',
                'message': '2.3% guaranteed profit between DraftKings and FanDuel on Celtics game',
                'severity': 'high'
            },
            {
                'type': 'injury',
                'title': 'Injury Update',
                'message': 'Star player questionable for tonight, line expected to move',
                'severity': 'high'
            }
        ]

        while True:
            await asyncio.sleep(random.uniform(10, 20))

            insight = random.choice(insights)

            update = {
                'type': 'insight',
                'payload': {
                    **insight,
                    'timestamp': datetime.now().isoformat()
                }
            }

            await self.send(text_data=json.dumps(update))