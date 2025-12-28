"""
The Bookmaker Agent - AI-Powered Odds Analysis and Line Prediction
This agent thinks like a Vegas bookmaker, analyzing games to predict line movements,
identify value, and provide professional betting insights.

Session 306: Added learning infrastructure hooks for cross-agent knowledge sharing.
"""

import json
import logging
from typing import Dict, List, Any
from django.utils import timezone

logger = logging.getLogger(__name__)


class LearningMixin:
    """
    Learning infrastructure mixin for standalone agents.
    Session 306: Enables cross-agent knowledge sharing without requiring inheritance.

    Provides:
    - _record_learning_outcome(): Record execution for XP and patterns
    - _create_execution_memory(): Create memories from interactions
    - _share_knowledge(): Share learned patterns cross-agent
    - _get_shared_knowledge(): Retrieve knowledge from other agents
    """

    _learning_loop = None
    _memory_service = None
    _agent_model = None

    @property
    def learning_loop(self):
        """Lazy-load LearningLoopService."""
        if self._learning_loop is None:
            try:
                from core.super_platform.learning_loop import get_learning_loop_service
                self._learning_loop = get_learning_loop_service(None)  # No user context for this agent
            except ImportError:
                logger.debug("LearningLoopService not available")
                return None
        return self._learning_loop

    @property
    def memory_service(self):
        """Lazy-load MemoryEmbeddingService."""
        if self._memory_service is None:
            try:
                from core.services.memory_embedding_service import get_memory_embedding_service
                self._memory_service = get_memory_embedding_service()
            except ImportError:
                logger.debug("MemoryEmbeddingService not available")
                return None
        return self._memory_service

    @property
    def agent_model(self):
        """Lazy-load or create Agent model instance."""
        if self._agent_model is None:
            try:
                from core.models_unified_system import Agent
                agent_name = getattr(self, 'name', self.__class__.__name__)
                self._agent_model, _ = Agent.objects.get_or_create(
                    name=agent_name,
                    defaults={
                        'agent_type': 'standalone',
                        'specialization': 'sports_analysis',
                        'description': getattr(self, 'description', f'Standalone agent: {agent_name}'),
                        'is_active': True,
                    }
                )
            except ImportError:
                logger.debug("Agent model not available")
                return None
        return self._agent_model

    def _record_learning_outcome(
        self,
        result: Dict[str, Any],
        task: str,
        context: Dict[str, Any] = None,
        spider_data_used: bool = False,
        scifi_context_used: bool = False
    ):
        """Record execution outcome for XP and pattern learning."""
        if not self.learning_loop:
            return None

        try:
            outcome_id = self.learning_loop.record_outcome(
                query_type=self._detect_query_type(task),
                query_text=task,
                execution_mode='agent',
                agents_used=[getattr(self, 'name', self.__class__.__name__)],
                response=result.get('message', str(result.get('analysis', ''))),
                execution_time_ms=result.get('execution_time_ms', 0),
                success=not result.get('error'),
                spider_data_used=spider_data_used,
                scifi_context_used=scifi_context_used,
                context=context or {}
            )
            return outcome_id
        except Exception as e:
            logger.debug(f"Failed to record learning outcome: {e}")
            return None

    def _detect_query_type(self, task: str) -> str:
        """Detect the type of query from the task text."""
        task_lower = task.lower()
        if any(word in task_lower for word in ['analyze', 'predict', 'forecast']):
            return 'analysis'
        elif any(word in task_lower for word in ['odds', 'line', 'spread', 'value']):
            return 'betting'
        elif any(word in task_lower for word in ['game', 'match', 'team']):
            return 'sports'
        return 'general'

    def _create_execution_memory(
        self,
        result: Dict[str, Any],
        task: str,
        memory_type: str = "interaction",
        importance: float = 0.5
    ):
        """Create a memory from the interaction."""
        if not self.memory_service or not self.agent_model:
            return None

        try:
            memory = self.memory_service.create_memory(
                agent=self.agent_model,
                title=f"{getattr(self, 'name', self.__class__.__name__)}: {task[:50]}...",
                content=result.get('message', str(result.get('analysis', ''))),
                memory_type=memory_type,
                valence="positive" if not result.get('error') else "negative",
                importance_score=importance,
                source_type='agent_execution',
                tags=['sports_analysis', 'bookmaker', 'success' if not result.get('error') else 'failure']
            )
            return memory
        except Exception as e:
            logger.debug(f"Failed to create execution memory: {e}")
            return None

    def _share_knowledge(
        self,
        knowledge_type: str,
        title: str,
        knowledge_value: Dict[str, Any],
        confidence: float = 0.8
    ):
        """Share learned knowledge for cross-agent learning."""
        if not self.agent_model:
            return None

        try:
            from core.models_unified_system import AgentKnowledgeSource

            # Map generic types to model's choices
            type_mapping = {
                'technique': 'tool_discovery',
                'insight': 'market',
                'pattern': 'user_behavior',
                'prediction': 'market',
                'betting': 'pricing',
            }
            mapped_type = type_mapping.get(knowledge_type, knowledge_type)

            valid_types = ['trend', 'market', 'opportunity', 'competitor',
                          'pricing', 'user_behavior', 'content_idea', 'tool_discovery']
            if mapped_type not in valid_types:
                mapped_type = 'market'

            knowledge, created = AgentKnowledgeSource.objects.update_or_create(
                agent=self.agent_model,
                title=title,
                knowledge_type=mapped_type,
                defaults={
                    'summary': json.dumps(knowledge_value),
                    'confidence_score': confidence,
                    'is_active': True,
                }
            )
            return knowledge
        except Exception as e:
            logger.debug(f"Failed to share knowledge: {e}")
            return None

    def _get_shared_knowledge(
        self,
        knowledge_type: str = None,
        title_contains: str = None,
        from_agents: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve knowledge from other agents."""
        try:
            from core.models_unified_system import AgentKnowledgeSource

            queryset = AgentKnowledgeSource.objects.filter(is_active=True)

            if knowledge_type:
                type_mapping = {
                    'technique': 'tool_discovery',
                    'insight': 'market',
                    'pattern': 'user_behavior',
                    'prediction': 'market',
                }
                mapped_type = type_mapping.get(knowledge_type, knowledge_type)
                queryset = queryset.filter(knowledge_type=mapped_type)

            if title_contains:
                queryset = queryset.filter(title__icontains=title_contains)

            if from_agents:
                queryset = queryset.filter(agent__name__in=from_agents)

            # Exclude own knowledge to learn from others
            if self.agent_model:
                queryset = queryset.exclude(agent=self.agent_model)

            return [
                {
                    'source_agent': ks.agent.name,
                    'title': ks.title,
                    'type': ks.knowledge_type,
                    'value': json.loads(ks.summary) if ks.summary else {},
                    'confidence': ks.confidence_score,
                    'created': ks.created_at.isoformat() if ks.created_at else None,
                }
                for ks in queryset.order_by('-confidence_score')[:10]
            ]
        except Exception as e:
            logger.debug(f"Failed to get shared knowledge: {e}")
            return []


class BookmakerAgent(LearningMixin):
    """
    The Bookmaker Agent - Your AI Vegas Insider

    Capabilities:
    - Predict line movements before they happen
    - Identify sharp vs public money
    - Calculate true odds using advanced models
    - Detect arbitrage opportunities
    - Analyze injury impacts on lines
    - Track steam moves and reverse line movement
    - Provide closing line value predictions

    Session 306: Now includes learning infrastructure for cross-agent knowledge sharing.
    """

    def __init__(self):
        self.name = "Vegas AI"
        self.description = "AI Bookmaker analyzing odds like a Vegas professional"
        self.confidence_threshold = 0.65
        # Initialize learning mixin attributes
        self._learning_loop = None
        self._memory_service = None
        self._agent_model = None

    def analyze_game(self, game_id: str) -> Dict[str, Any]:
        """
        Complete bookmaker analysis of a game
        """
        from sports.models import Game

        try:
            game = Game.objects.get(id=game_id)

            analysis = {
                'game_id': game_id,
                'timestamp': timezone.now().isoformat(),
                'agent': self.name,
                'analysis': {
                    'line_prediction': self.predict_line_movement(game),
                    'sharp_money': self.detect_sharp_money(game),
                    'true_odds': self.calculate_true_odds(game),
                    'value_bets': self.identify_value_bets(game),
                    'injury_impact': self.analyze_injury_impact(game),
                    'weather_impact': self.analyze_weather_impact(game),
                    'public_bias': self.detect_public_bias(game),
                    'closing_line_prediction': self.predict_closing_line(game),
                    'confidence_rating': self.calculate_confidence(game),
                    'key_factors': self.identify_key_factors(game)
                },
                'recommendations': self.generate_recommendations(game),
                'alerts': self.generate_alerts(game)
            }

            # Session 306: Learning Infrastructure Hooks
            task = f"Analyze game {game_id}: {game.home_team.name} vs {game.away_team.name}"

            # Record learning outcome
            self._record_learning_outcome(
                result={'success': True, 'analysis': analysis},
                task=task,
                context={'game_id': game_id, 'league': game.league.abbreviation}
            )

            # Create high-importance memory for game analysis
            self._create_execution_memory(
                result={'success': True, 'analysis': analysis},
                task=task,
                memory_type="success",
                importance=0.7
            )

            # Share valuable insights for cross-agent learning
            sharp_money = analysis['analysis']['sharp_money']
            if sharp_money.get('sharp_probability', 0) > 0.6:
                self._share_knowledge(
                    knowledge_type='prediction',
                    title=f"Sharp money on {sharp_money.get('sharp_side', 'UNKNOWN')} - {game_id}",
                    knowledge_value={
                        'game_id': game_id,
                        'sharp_side': sharp_money.get('sharp_side'),
                        'probability': sharp_money.get('sharp_probability'),
                        'indicators': sharp_money.get('indicators', {}),
                    },
                    confidence=sharp_money.get('sharp_probability', 0.5)
                )

            # Share value bet insights
            value_bets = analysis['analysis']['value_bets']
            if value_bets:
                for bet in value_bets[:2]:  # Top 2 value bets
                    self._share_knowledge(
                        knowledge_type='betting',
                        title=f"Value bet: {bet.get('type')} on {bet.get('team', bet.get('direction'))}",
                        knowledge_value=bet,
                        confidence=0.8 if bet.get('confidence') == 'HIGH' else 0.6
                    )

            return analysis

        except Game.DoesNotExist:
            error_result = {'error': f'Game {game_id} not found'}
            # Record failed outcome
            self._record_learning_outcome(
                result=error_result,
                task=f"Analyze game {game_id}",
                context={'game_id': game_id}
            )
            return error_result

    def predict_line_movement(self, game) -> Dict[str, Any]:
        """
        Predict how the line will move based on multiple factors
        """
        markets = game.markets.filter(is_active=True, market_type='spreads')

        if not markets.exists():
            return {'prediction': 'No spread data available'}

        # Get current consensus line
        current_lines = []
        line_history = []

        for market in markets:
            lines = market.odds_lines.filter(is_current=True)
            for line in lines:
                if line.home_spread:
                    current_lines.append(float(line.home_spread))

            # Get historical lines
            historical = market.odds_lines.order_by('created_at')[:10]
            for h_line in historical:
                if h_line.home_spread:
                    line_history.append({
                        'spread': float(h_line.home_spread),
                        'time': h_line.created_at.isoformat()
                    })

        if not current_lines:
            return {'prediction': 'No spread lines available'}

        current_consensus = sum(current_lines) / len(current_lines)

        # Analyze movement patterns
        movement_velocity = 0
        if len(line_history) > 1:
            recent_movement = line_history[-1]['spread'] - line_history[0]['spread']
            movement_velocity = recent_movement / max(len(line_history), 1)

        # Factors affecting line movement
        factors = {
            'current_spread': current_consensus,
            'movement_velocity': movement_velocity,
            'time_to_game': (game.scheduled_start - timezone.now()).total_seconds() / 3600,
            'sharp_indicator': self._detect_sharp_movement(line_history),
            'public_lean': self._calculate_public_lean(game)
        }

        # Predict movement
        predicted_movement = 0

        # Sharp money influence
        if factors['sharp_indicator'] > 0.7:
            predicted_movement += movement_velocity * 2

        # Public money counter-movement
        if abs(factors['public_lean']) > 0.6:
            predicted_movement -= factors['public_lean'] * 0.5

        # Time decay factor
        if factors['time_to_game'] < 24:  # Less than 24 hours
            predicted_movement *= 1.5

        prediction = {
            'current_line': current_consensus,
            'predicted_close': current_consensus + predicted_movement,
            'predicted_movement': predicted_movement,
            'confidence': min(0.85, 0.5 + abs(movement_velocity) * 2),
            'factors': factors,
            'direction': 'HOME' if predicted_movement < 0 else 'AWAY',
            'recommendation': self._get_movement_recommendation(predicted_movement)
        }

        return prediction

    def detect_sharp_money(self, game) -> Dict[str, Any]:
        """
        Detect sharp money vs public money patterns
        """
        markets = game.markets.filter(is_active=True)

        sharp_indicators = {
            'reverse_line_movement': False,
            'steam_move': False,
            'line_freeze': False,
            'sharp_books_different': False,
            'early_movement': False,
            'sharp_percentage': 0.0
        }

        # Check for reverse line movement
        # (Line moves opposite to public betting percentage)
        spreads = markets.filter(market_type='spreads').first()
        if spreads:
            lines = spreads.odds_lines.order_by('created_at')
            if lines.count() > 2:
                early_line = lines.first()
                current_line = lines.filter(is_current=True).first()

                if early_line and current_line:
                    if early_line.home_spread and current_line.home_spread:
                        movement = float(current_line.home_spread) - float(early_line.home_spread)

                        # If line moved towards home but public is on away (or vice versa)
                        public_on_away = self._calculate_public_lean(game) > 0
                        line_moved_to_home = movement < 0

                        if (public_on_away and line_moved_to_home) or (not public_on_away and not line_moved_to_home):
                            sharp_indicators['reverse_line_movement'] = True
                            sharp_indicators['sharp_percentage'] += 0.3

        # Check for steam moves (rapid line movement across multiple books)
        rapid_movements = self._detect_steam_moves(markets)
        if rapid_movements > 3:
            sharp_indicators['steam_move'] = True
            sharp_indicators['sharp_percentage'] += 0.25

        # Check sharp books vs public books
        sharp_books = ['pinnacle', 'betcris', 'bookmaker']
        public_books = ['draftkings', 'fanduel', 'betmgm']

        sharp_lines = []
        public_lines = []

        for market in markets.filter(market_type='spreads'):
            for line in market.odds_lines.filter(is_current=True):
                if any(sharp in line.sportsbook.name.lower() for sharp in sharp_books):
                    if line.home_spread:
                        sharp_lines.append(float(line.home_spread))
                elif any(public in line.sportsbook.name.lower() for public in public_books):
                    if line.home_spread:
                        public_lines.append(float(line.home_spread))

        if sharp_lines and public_lines:
            sharp_avg = sum(sharp_lines) / len(sharp_lines)
            public_avg = sum(public_lines) / len(public_lines)

            if abs(sharp_avg - public_avg) > 0.5:
                sharp_indicators['sharp_books_different'] = True
                sharp_indicators['sharp_percentage'] += 0.2

        # Calculate overall sharp probability
        sharp_indicators['sharp_percentage'] = min(1.0, sharp_indicators['sharp_percentage'] + 0.2)

        # Determine sharp side
        sharp_side = 'UNKNOWN'
        if sharp_indicators['reverse_line_movement']:
            sharp_side = 'HOME' if movement < 0 else 'AWAY'
        elif sharp_indicators['sharp_books_different']:
            sharp_side = 'HOME' if sharp_avg < public_avg else 'AWAY'

        return {
            'indicators': sharp_indicators,
            'sharp_probability': sharp_indicators['sharp_percentage'],
            'sharp_side': sharp_side,
            'analysis': self._generate_sharp_analysis(sharp_indicators, sharp_side)
        }

    def calculate_true_odds(self, game) -> Dict[str, Any]:
        """
        Calculate true odds removing the vig and accounting for market inefficiencies
        """

        # Get team stats
        home_team = game.home_team
        away_team = game.away_team

        # Simple power rating model
        home_rating = self._calculate_team_rating(home_team)
        away_rating = self._calculate_team_rating(away_team)

        # Home field advantage (varies by sport)
        home_advantage = {
            'NFL': 2.5,
            'NCAAF': 3.5,
            'NBA': 3.0,
            'NCAAB': 4.0,
            'MLB': 0.5,
            'NHL': 0.3
        }.get(game.league.abbreviation, 2.0)

        # Calculate expected margin
        expected_margin = (home_rating - away_rating) + home_advantage

        # Calculate win probability
        # Using a simple logistic model
        import math
        k = 0.04  # Scaling factor
        home_win_prob = 1 / (1 + math.exp(-k * expected_margin))
        away_win_prob = 1 - home_win_prob

        # Convert to American odds
        def prob_to_american(prob):
            if prob >= 0.5:
                return -100 / ((1/prob) - 1)
            else:
                return 100 * ((1/prob) - 1)

        true_moneyline = {
            'home': int(prob_to_american(home_win_prob)),
            'away': int(prob_to_american(away_win_prob))
        }

        # Calculate true spread
        true_spread = -expected_margin

        # Calculate true total
        pace_factor = self._calculate_pace_factor(game)
        true_total = 48.5 * pace_factor  # Base total adjusted by pace

        # Get current market odds for comparison
        current_ml = self._get_current_moneyline(game)
        current_spread = self._get_current_spread(game)
        current_total = self._get_current_total(game)

        return {
            'true_odds': {
                'moneyline': true_moneyline,
                'spread': round(true_spread, 1),
                'total': round(true_total, 1),
                'home_win_probability': round(home_win_prob, 3),
                'away_win_probability': round(away_win_prob, 3)
            },
            'market_odds': {
                'moneyline': current_ml,
                'spread': current_spread,
                'total': current_total
            },
            'edge': {
                'moneyline_edge': self._calculate_ml_edge(true_moneyline, current_ml),
                'spread_edge': abs(true_spread - current_spread) if current_spread else 0,
                'total_edge': abs(true_total - current_total) if current_total else 0
            },
            'model_confidence': 0.72,  # Would be based on model backtesting
            'key_factors': {
                'home_rating': home_rating,
                'away_rating': away_rating,
                'home_advantage': home_advantage,
                'expected_margin': expected_margin
            }
        }

    def identify_value_bets(self, game) -> List[Dict[str, Any]]:
        """
        Identify bets with positive expected value
        """
        value_bets = []

        # Get true odds
        true_odds = self.calculate_true_odds(game)

        # Check each market for value
        markets = game.markets.filter(is_active=True)

        for market in markets:
            for line in market.odds_lines.filter(is_current=True):
                # Check moneyline value
                if market.market_type == 'h2h':
                    if line.home_odds and true_odds['true_odds']['moneyline']['home']:
                        home_value = self._calculate_ev(
                            line.home_odds,
                            true_odds['true_odds']['home_win_probability']
                        )
                        if home_value > 2:  # 2% edge threshold
                            value_bets.append({
                                'type': 'MONEYLINE',
                                'team': 'HOME',
                                'book': line.sportsbook.name,
                                'odds': line.home_odds,
                                'true_probability': true_odds['true_odds']['home_win_probability'],
                                'expected_value': round(home_value, 2),
                                'confidence': 'HIGH' if home_value > 5 else 'MEDIUM',
                                'bet_sizing': self._kelly_criterion(
                                    true_odds['true_odds']['home_win_probability'],
                                    line.home_odds
                                )
                            })

                # Check spread value
                elif market.market_type == 'spreads':
                    if line.home_spread and true_odds['true_odds']['spread']:
                        spread_diff = abs(float(line.home_spread) - true_odds['true_odds']['spread'])
                        if spread_diff > 1.5:
                            value_bets.append({
                                'type': 'SPREAD',
                                'team': 'HOME' if line.home_spread > true_odds['true_odds']['spread'] else 'AWAY',
                                'book': line.sportsbook.name,
                                'line': line.home_spread,
                                'true_line': true_odds['true_odds']['spread'],
                                'edge': spread_diff,
                                'confidence': 'HIGH' if spread_diff > 3 else 'MEDIUM'
                            })

                # Check total value
                elif market.market_type == 'totals':
                    if line.total_line and true_odds['true_odds']['total']:
                        total_diff = abs(float(line.total_line) - true_odds['true_odds']['total'])
                        if total_diff > 2:
                            value_bets.append({
                                'type': 'TOTAL',
                                'direction': 'OVER' if line.total_line < true_odds['true_odds']['total'] else 'UNDER',
                                'book': line.sportsbook.name,
                                'line': line.total_line,
                                'true_total': true_odds['true_odds']['total'],
                                'edge': total_diff,
                                'confidence': 'HIGH' if total_diff > 4 else 'MEDIUM'
                            })

        # Sort by expected value
        value_bets.sort(key=lambda x: x.get('expected_value', x.get('edge', 0)), reverse=True)

        return value_bets[:5]  # Top 5 value bets

    def analyze_injury_impact(self, game) -> Dict[str, Any]:
        """
        Analyze how injuries affect the line
        """
        # This would integrate with injury reports
        # For now, return a structured response
        return {
            'home_team_impact': {
                'key_injuries': [],
                'line_impact': 0,
                'total_impact': 0
            },
            'away_team_impact': {
                'key_injuries': [],
                'line_impact': 0,
                'total_impact': 0
            },
            'overall_impact': 'MINIMAL'
        }

    def analyze_weather_impact(self, game) -> Dict[str, Any]:
        """
        Analyze weather impact on totals and spreads
        """
        if not game.weather_data:
            return {'impact': 'No weather data available'}

        weather = game.weather_data
        impact = {
            'temperature_impact': 0,
            'wind_impact': 0,
            'precipitation_impact': 0,
            'total_adjustment': 0,
            'spread_adjustment': 0
        }

        # Temperature impact
        temp = weather.get('temperature', 70)
        if temp < 32:  # Freezing
            impact['temperature_impact'] = -3
            impact['total_adjustment'] -= 3
        elif temp > 85:  # Hot
            impact['temperature_impact'] = -1
            impact['total_adjustment'] -= 1

        # Wind impact (for outdoor games)
        wind = weather.get('wind_mph', 0)
        if wind > 20:
            impact['wind_impact'] = -5
            impact['total_adjustment'] -= 5
        elif wind > 10:
            impact['wind_impact'] = -2
            impact['total_adjustment'] -= 2

        # Precipitation
        if 'rain' in weather.get('condition', '').lower():
            impact['precipitation_impact'] = -4
            impact['total_adjustment'] -= 4
        elif 'snow' in weather.get('condition', '').lower():
            impact['precipitation_impact'] = -6
            impact['total_adjustment'] -= 6

        impact['recommendation'] = self._get_weather_recommendation(impact)

        return impact

    def detect_public_bias(self, game) -> Dict[str, Any]:
        """
        Detect public betting bias and fade opportunities
        """
        public_lean = self._calculate_public_lean(game)

        bias_factors = {
            'primetime_game': game.scheduled_start.hour >= 20,  # 8 PM or later
            'popular_team': self._is_popular_team(game),
            'recent_performance': self._check_recent_performance(game),
            'media_narrative': self._analyze_media_sentiment(game)
        }

        fade_opportunity = abs(public_lean) > 0.65 and sum(bias_factors.values()) >= 2

        return {
            'public_lean': public_lean,
            'public_side': 'HOME' if public_lean < 0 else 'AWAY',
            'public_percentage': abs(public_lean) * 100,
            'bias_factors': bias_factors,
            'fade_opportunity': fade_opportunity,
            'fade_confidence': min(0.9, abs(public_lean) + sum(bias_factors.values()) * 0.1)
        }

    def predict_closing_line(self, game) -> Dict[str, Any]:
        """
        Predict where the line will close
        """
        line_movement = self.predict_line_movement(game)
        sharp_money = self.detect_sharp_money(game)
        public_bias = self.detect_public_bias(game)

        current_spread = self._get_current_spread(game)
        current_total = self._get_current_total(game)

        # Combine factors for closing line prediction
        spread_adjustment = 0
        total_adjustment = 0

        # Sharp money influence (strongest factor)
        if sharp_money['sharp_probability'] > 0.6:
            if sharp_money['sharp_side'] == 'HOME':
                spread_adjustment -= 1
            else:
                spread_adjustment += 1

        # Line movement momentum
        spread_adjustment += line_movement.get('predicted_movement', 0)

        # Public money counter-adjustment (books shade against public)
        if public_bias['public_percentage'] > 70:
            if public_bias['public_side'] == 'HOME':
                spread_adjustment += 0.5
            else:
                spread_adjustment -= 0.5

        # Weather adjustments for total
        weather_impact = self.analyze_weather_impact(game)
        total_adjustment += weather_impact.get('total_adjustment', 0)

        return {
            'current_spread': current_spread,
            'predicted_closing_spread': current_spread + spread_adjustment if current_spread else None,
            'spread_confidence': line_movement.get('confidence', 0.5),
            'current_total': current_total,
            'predicted_closing_total': current_total + total_adjustment if current_total else None,
            'total_confidence': 0.65,
            'key_factors': {
                'sharp_influence': sharp_money['sharp_probability'],
                'public_influence': public_bias['public_percentage'],
                'momentum': line_movement.get('predicted_movement', 0)
            },
            'bet_now': spread_adjustment != 0 or total_adjustment != 0,
            'wait_reason': self._get_wait_reason(game, spread_adjustment)
        }

    def calculate_confidence(self, game) -> float:
        """
        Calculate overall confidence in analysis
        """
        factors = []

        # Data quality
        markets = game.markets.filter(is_active=True)
        if markets.count() > 5:
            factors.append(0.2)

        # Line stability
        line_movement = self.predict_line_movement(game)
        if line_movement.get('confidence', 0) > 0.7:
            factors.append(0.2)

        # Sharp money clarity
        sharp = self.detect_sharp_money(game)
        if sharp['sharp_probability'] > 0.6:
            factors.append(0.3)

        # Model confidence
        true_odds = self.calculate_true_odds(game)
        if true_odds.get('model_confidence', 0) > 0.7:
            factors.append(0.3)

        return min(0.95, sum(factors))

    def identify_key_factors(self, game) -> List[str]:
        """
        Identify the most important factors for this game
        """
        factors = []

        # Check sharp money
        sharp = self.detect_sharp_money(game)
        if sharp['sharp_probability'] > 0.6:
            factors.append(f"Sharp money detected on {sharp['sharp_side']}")

        # Check line movement
        movement = self.predict_line_movement(game)
        if abs(movement.get('predicted_movement', 0)) > 1:
            factors.append(f"Line expected to move {movement.get('predicted_movement', 0):.1f} points")

        # Check value
        value_bets = self.identify_value_bets(game)
        if value_bets:
            factors.append(f"{len(value_bets)} value betting opportunities identified")

        # Check weather
        if game.weather_data:
            weather = self.analyze_weather_impact(game)
            if abs(weather['total_adjustment']) > 3:
                factors.append(f"Weather impacting total by {weather['total_adjustment']} points")

        # Check public bias
        public = self.detect_public_bias(game)
        if public['fade_opportunity']:
            factors.append(f"Fade opportunity: {public['public_percentage']:.0f}% on {public['public_side']}")

        return factors[:3]  # Top 3 factors

    def generate_recommendations(self, game) -> List[Dict[str, Any]]:
        """
        Generate specific betting recommendations
        """
        recommendations = []

        # Get all analysis
        value_bets = self.identify_value_bets(game)
        sharp_money = self.detect_sharp_money(game)
        closing_line = self.predict_closing_line(game)
        public_bias = self.detect_public_bias(game)

        # Priority 1: Follow sharp money with value
        if sharp_money['sharp_probability'] > 0.7 and value_bets:
            for bet in value_bets[:2]:
                if (sharp_money['sharp_side'] == 'HOME' and bet.get('team') == 'HOME') or \
                   (sharp_money['sharp_side'] == 'AWAY' and bet.get('team') == 'AWAY'):
                    recommendations.append({
                        'priority': 'HIGH',
                        'type': bet['type'],
                        'pick': bet.get('team', bet.get('direction')),
                        'reasoning': f"Sharp money aligned with {bet.get('expected_value', bet.get('edge'))}% edge",
                        'confidence': 0.85,
                        'units': 2.5
                    })

        # Priority 2: Fade the public
        if public_bias['fade_opportunity'] and public_bias['fade_confidence'] > 0.7:
            fade_side = 'HOME' if public_bias['public_side'] == 'AWAY' else 'AWAY'
            recommendations.append({
                'priority': 'MEDIUM',
                'type': 'SPREAD',
                'pick': fade_side,
                'reasoning': f"Fade {public_bias['public_percentage']:.0f}% public on {public_bias['public_side']}",
                'confidence': public_bias['fade_confidence'],
                'units': 1.5
            })

        # Priority 3: Beat the closing line
        if closing_line['bet_now'] and closing_line['spread_confidence'] > 0.7:
            recommendations.append({
                'priority': 'MEDIUM',
                'type': 'SPREAD',
                'pick': 'HOME' if closing_line['predicted_closing_spread'] > closing_line['current_spread'] else 'AWAY',
                'reasoning': f"Line moving from {closing_line['current_spread']} to {closing_line['predicted_closing_spread']}",
                'confidence': closing_line['spread_confidence'],
                'units': 1.0
            })

        return recommendations[:3]  # Top 3 recommendations

    def generate_alerts(self, game) -> List[Dict[str, Any]]:
        """
        Generate real-time alerts for important changes
        """
        alerts = []

        # Steam move alert
        sharp = self.detect_sharp_money(game)
        if sharp['indicators'].get('steam_move'):
            alerts.append({
                'type': 'STEAM_MOVE',
                'urgency': 'HIGH',
                'message': 'Steam move detected - line moving rapidly across books',
                'action': 'Check line immediately'
            })

        # Reverse line movement
        if sharp['indicators'].get('reverse_line_movement'):
            alerts.append({
                'type': 'REVERSE_LINE_MOVEMENT',
                'urgency': 'HIGH',
                'message': f"Line moving opposite to public money - sharp action on {sharp['sharp_side']}",
                'action': f"Consider {sharp['sharp_side']} side"
            })

        # Value threshold
        value_bets = self.identify_value_bets(game)
        if value_bets and value_bets[0].get('expected_value', 0) > 5:
            alerts.append({
                'type': 'HIGH_VALUE',
                'urgency': 'MEDIUM',
                'message': f"{value_bets[0].get('expected_value')}% edge identified",
                'action': f"Place {value_bets[0]['type']} bet on {value_bets[0].get('team', value_bets[0].get('direction'))}"
            })

        # Closing line value
        closing = self.predict_closing_line(game)
        if closing['bet_now']:
            alerts.append({
                'type': 'CLV_OPPORTUNITY',
                'urgency': 'MEDIUM',
                'message': 'Positive CLV opportunity detected',
                'action': 'Bet before line moves'
            })

        return alerts

    # Helper methods
    def _calculate_team_rating(self, team) -> float:
        """Calculate simple team power rating"""
        record = team.current_record
        if record:
            wins = record.get('wins', 0)
            losses = record.get('losses', 0)
            if wins + losses > 0:
                return (wins / (wins + losses)) * 100
        return 50.0

    def _calculate_pace_factor(self, game) -> float:
        """Calculate pace adjustment for totals"""
        # This would use actual pace stats
        # For now, return sport-based defaults
        pace_map = {
            'NBA': 1.0,
            'NCAAB': 0.9,
            'NFL': 1.0,
            'NCAAF': 1.1
        }
        return pace_map.get(game.league.abbreviation, 1.0)

    def _calculate_public_lean(self, game) -> float:
        """Calculate public betting lean (-1 to 1, negative = home)"""
        # This would use actual public betting data
        # For now, simulate based on team popularity
        import random
        return random.uniform(-0.8, 0.8)

    def _detect_sharp_movement(self, line_history) -> float:
        """Detect sharp betting patterns in line movement"""
        if len(line_history) < 2:
            return 0.0

        # Look for sudden movements
        max_move = 0
        for i in range(1, len(line_history)):
            move = abs(line_history[i]['spread'] - line_history[i-1]['spread'])
            max_move = max(max_move, move)

        # Sharp indicator based on movement size
        if max_move > 2:
            return 0.8
        elif max_move > 1:
            return 0.5
        return 0.2

    def _detect_steam_moves(self, markets) -> int:
        """Count rapid movements across books"""
        rapid_moves = 0
        for market in markets:
            lines = market.odds_lines.order_by('-created_at')[:5]
            if lines.count() >= 2:
                recent = lines[0]
                previous = lines[1]

                # Check time difference
                time_diff = (recent.created_at - previous.created_at).total_seconds()
                if time_diff < 300:  # Less than 5 minutes
                    rapid_moves += 1

        return rapid_moves

    def _get_current_spread(self, game):
        """Get current consensus spread"""
        spreads = []
        markets = game.markets.filter(market_type='spreads', is_active=True)
        for market in markets:
            for line in market.odds_lines.filter(is_current=True):
                if line.home_spread:
                    spreads.append(float(line.home_spread))

        return sum(spreads) / len(spreads) if spreads else None

    def _get_current_total(self, game):
        """Get current consensus total"""
        totals = []
        markets = game.markets.filter(market_type='totals', is_active=True)
        for market in markets:
            for line in market.odds_lines.filter(is_current=True):
                if line.total_line:
                    totals.append(float(line.total_line))

        return sum(totals) / len(totals) if totals else None

    def _get_current_moneyline(self, game):
        """Get current moneyline odds"""
        ml = {'home': [], 'away': []}
        markets = game.markets.filter(market_type='h2h', is_active=True)
        for market in markets:
            for line in market.odds_lines.filter(is_current=True):
                if line.home_odds:
                    ml['home'].append(line.home_odds)
                if line.away_odds:
                    ml['away'].append(line.away_odds)

        return {
            'home': sum(ml['home']) / len(ml['home']) if ml['home'] else None,
            'away': sum(ml['away']) / len(ml['away']) if ml['away'] else None
        }

    def _calculate_ml_edge(self, true_ml, current_ml):
        """Calculate moneyline edge"""
        if not current_ml['home'] or not true_ml['home']:
            return 0

        # Convert to probabilities and compare
        def american_to_prob(odds):
            if odds < 0:
                return abs(odds) / (abs(odds) + 100)
            else:
                return 100 / (odds + 100)

        true_prob = american_to_prob(true_ml['home'])
        current_prob = american_to_prob(current_ml['home'])

        return (true_prob - current_prob) * 100

    def _calculate_ev(self, odds, true_probability):
        """Calculate expected value"""
        # Convert American odds to decimal
        if odds < 0:
            decimal = (100 / abs(odds)) + 1
        else:
            decimal = (odds / 100) + 1

        # EV = (probability * profit) - (1 - probability) * stake
        ev = (true_probability * (decimal - 1)) - (1 - true_probability)
        return ev * 100  # Return as percentage

    def _kelly_criterion(self, probability, odds):
        """Calculate Kelly criterion bet sizing"""
        if odds < 0:
            decimal = (100 / abs(odds)) + 1
        else:
            decimal = (odds / 100) + 1

        # Kelly formula: f = (p * b - q) / b
        # where p = probability of winning, q = 1-p, b = decimal odds - 1
        b = decimal - 1
        q = 1 - probability

        kelly = (probability * b - q) / b

        # Use fractional Kelly for safety (25%)
        return max(0, min(0.05, kelly * 0.25))  # Cap at 5% of bankroll

    def _is_popular_team(self, game):
        """Check if popular teams are playing"""
        popular_teams = ['cowboys', 'patriots', 'packers', 'steelers', 'lakers', 'yankees']
        home_popular = any(team in game.home_team.name.lower() for team in popular_teams)
        away_popular = any(team in game.away_team.name.lower() for team in popular_teams)
        return home_popular or away_popular

    def _check_recent_performance(self, game):
        """Check recent winning streaks"""
        # Would check actual recent games
        return False

    def _analyze_media_sentiment(self, game):
        """Analyze media coverage sentiment"""
        # Would integrate with news analysis
        return False

    def _generate_sharp_analysis(self, indicators, side):
        """Generate sharp money analysis text"""
        analysis = []

        if indicators['reverse_line_movement']:
            analysis.append(f"Reverse line movement detected - line moving toward {side} despite public on opposite side")

        if indicators['steam_move']:
            analysis.append("Steam move across multiple books indicates coordinated sharp action")

        if indicators['sharp_books_different']:
            analysis.append("Sharp books showing different line than public books")

        return " | ".join(analysis) if analysis else "No clear sharp money indicators"

    def _get_movement_recommendation(self, movement):
        """Get line movement recommendation"""
        if abs(movement) < 0.5:
            return "Line stable - no urgency"
        elif movement > 0:
            return f"Line moving toward away team - bet home now or wait for better away line"
        else:
            return f"Line moving toward home team - bet away now or wait for better home line"

    def _get_weather_recommendation(self, impact):
        """Get weather betting recommendation"""
        if impact['total_adjustment'] < -5:
            return "Strong UNDER conditions - consider under bet"
        elif impact['total_adjustment'] < -2:
            return "Moderate UNDER conditions - lean under"
        else:
            return "Minimal weather impact"

    def _get_wait_reason(self, game, adjustment):
        """Determine if should wait to bet"""
        hours_to_game = (game.scheduled_start - timezone.now()).total_seconds() / 3600

        if hours_to_game > 24 and abs(adjustment) < 0.5:
            return "Wait for more information closer to game time"
        elif adjustment > 1:
            return "Line moving in favorable direction - wait for better number"
        else:
            return None


# Singleton instance
bookmaker_agent = BookmakerAgent()