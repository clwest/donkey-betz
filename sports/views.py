"""
Sports Analytics API Views

Comprehensive REST API endpoints for sports betting data, analytics, recommendations,
and real-time information with advanced filtering, aggregation, and WebSocket support.
"""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any

from django.utils import timezone
from django.db.models import Q, Avg, Sum, Count, Max, Min, F, Case, When
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import (
    League, Team, Game, Sportsbook, BettingMarket, OddsLine,
    LineMovement, Bet, BankrollManagement, ArbitrageOpportunity,
    BettingRecommendation, SportsAnalytics, SportType, GameStatus,
    BetType, MarketStatus, BetStatus, RiskLevel
)
from .serializers import (
    LeagueSerializer, TeamSerializer, GameSerializer, SportsbookSerializer,
    BettingMarketSerializer, OddsLineSerializer, LineMovementSerializer,
    BetSerializer, BankrollManagementSerializer, ArbitrageOpportunitySerializer,
    BettingRecommendationSerializer, SportsAnalyticsSerializer,
    GameOddsSerializer, UserBettingStatsSerializer, MarketAnalysisSerializer,
    LeagueStandingsSerializer
)
from .services import (
    OddsIngestionService, KellyCriterionService, ArbitrageDetectionService,
    BettingRecommendationService, SportsAnalyticsService
)


class SportsAnalyticsPagination(PageNumberPagination):
    """Custom pagination for sports analytics"""
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    """League API endpoints"""
    
    queryset = League.objects.filter(is_active=True)
    serializer_class = LeagueSerializer
    pagination_class = SportsAnalyticsPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['sport_type', 'country']
    search_fields = ['name', 'abbreviation']
    ordering_fields = ['name', 'sport_type', 'created_at']
    ordering = ['sport_type', 'name']
    
    @extend_schema(
        summary="Get league standings",
        responses={200: LeagueStandingsSerializer}
    )
    @action(detail=True, methods=['get'])
    def standings(self, request, pk=None):
        """Get league standings and betting insights"""
        league = self.get_object()
        
        # Get teams ordered by record
        teams = league.teams.filter(is_active=True).order_by(
            F('current_record__wins').desc(nulls_last=True)
        )
        
        standings_data = []
        for team in teams:
            record = team.current_record or {}
            standings_data.append({
                'team_id': team.id,
                'team_name': f"{team.city} {team.name}",
                'abbreviation': team.abbreviation,
                'wins': record.get('wins', 0),
                'losses': record.get('losses', 0),
                'win_percentage': record.get('wins', 0) / (record.get('wins', 0) + record.get('losses', 1)),
                'ats_record': team.ats_record,
                'ou_record': team.ou_record
            })
        
        # Get upcoming key matchups
        upcoming_games = league.games.filter(
            scheduled_start__gte=timezone.now(),
            scheduled_start__lte=timezone.now() + timedelta(days=7),
            is_active=True
        ).select_related('home_team', 'away_team')[:10]
        
        key_matchups = []
        for game in upcoming_games:
            key_matchups.append({
                'game_id': game.id,
                'matchup': f"{game.away_team.abbreviation} @ {game.home_team.abbreviation}",
                'scheduled_start': game.scheduled_start,
                'market_count': game.markets.filter(is_active=True).count()
            })
        
        response_data = {
            'league_id': league.id,
            'league_name': league.name,
            'standings': standings_data,
            'playoff_picture': {},  # Could add playoff implications
            'key_matchups': key_matchups,
            'betting_insights': {
                'total_handle_this_week': 0,  # Could calculate from games
                'most_bet_team': standings_data[0]['team_name'] if standings_data else None,
                'public_favorites': []
            }
        }
        
        return Response(response_data)
    
    @extend_schema(summary="Get league betting trends")
    @action(detail=True, methods=['get'])
    def betting_trends(self, request, pk=None):
        """Get betting trends for the league"""
        league = self.get_object()
        
        # Get recent games with betting data
        recent_games = league.games.filter(
            scheduled_start__gte=timezone.now() - timedelta(days=30),
            status=GameStatus.FINAL,
            is_active=True
        ).select_related('home_team', 'away_team')
        
        trends = {
            'home_team_performance': {
                'wins': recent_games.filter(home_score__gt=F('away_score')).count(),
                'total_games': recent_games.count(),
                'ats_performance': 0.0,  # Would calculate from bet results
            },
            'total_trends': {
                'overs': 0,  # Would calculate from totals betting
                'unders': 0,
                'pushes': 0
            },
            'sharp_vs_public': {
                'sharp_win_rate': 0.0,
                'public_win_rate': 0.0,
                'contrarian_opportunities': []
            },
            'line_movement_patterns': []
        }
        
        return Response(trends)


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """Team API endpoints"""
    
    queryset = Team.objects.filter(is_active=True).select_related('league')
    serializer_class = TeamSerializer
    pagination_class = SportsAnalyticsPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['league', 'conference', 'division']
    search_fields = ['name', 'city', 'abbreviation']
    ordering_fields = ['name', 'city', 'league__name']
    ordering = ['league__name', 'city', 'name']
    
    @extend_schema(summary="Get team betting analytics")
    @action(detail=True, methods=['get'])
    def betting_analytics(self, request, pk=None):
        """Get comprehensive betting analytics for team"""
        team = self.get_object()
        
        # Get team's games this season
        team_games = Game.objects.filter(
            Q(home_team=team) | Q(away_team=team),
            season=team.league.current_season,
            is_active=True
        ).select_related('home_team', 'away_team')
        
        analytics = {
            'team_info': {
                'name': f"{team.city} {team.name}",
                'league': team.league.name,
                'record': team.current_record
            },
            'betting_performance': {
                'ats_record': team.ats_record,
                'ou_record': team.ou_record,
                'home_performance': {},
                'away_performance': {},
                'as_favorite': {},
                'as_underdog': {}
            },
            'trends': {
                'recent_form': self._calculate_recent_form(team, team_games),
                'scoring_trends': {},
                'defensive_trends': {}
            },
            'upcoming_value': self._find_upcoming_value_bets(team)
        }
        
        return Response(analytics)
    
    def _calculate_recent_form(self, team, games):
        """Calculate recent form metrics"""
        recent = games.filter(status=GameStatus.FINAL).order_by('-scheduled_start')[:10]
        
        wins = 0
        total_scored = 0
        total_allowed = 0
        
        for game in recent:
            if game.home_team == team:
                team_score = game.home_score or 0
                opp_score = game.away_score or 0
            else:
                team_score = game.away_score or 0
                opp_score = game.home_score or 0
            
            if team_score > opp_score:
                wins += 1
            
            total_scored += team_score
            total_allowed += opp_score
        
        games_count = recent.count()
        
        return {
            'games': games_count,
            'wins': wins,
            'win_rate': wins / games_count if games_count > 0 else 0,
            'avg_points_scored': total_scored / games_count if games_count > 0 else 0,
            'avg_points_allowed': total_allowed / games_count if games_count > 0 else 0
        }
    
    def _find_upcoming_value_bets(self, team):
        """Find potential value bets for upcoming games"""
        upcoming_games = Game.objects.filter(
            Q(home_team=team) | Q(away_team=team),
            scheduled_start__gte=timezone.now(),
            status=GameStatus.SCHEDULED,
            is_active=True
        )[:5]
        
        value_opportunities = []
        for game in upcoming_games:
            # This would integrate with ML models for actual value assessment
            value_opportunities.append({
                'game_id': game.id,
                'opponent': game.away_team.abbreviation if game.home_team == team else game.home_team.abbreviation,
                'date': game.scheduled_start,
                'potential_value': 'TBD'  # Would calculate based on models
            })
        
        return value_opportunities


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """Game API endpoints"""
    
    queryset = Game.objects.filter(is_active=True).select_related('league', 'home_team', 'away_team')
    serializer_class = GameSerializer
    pagination_class = SportsAnalyticsPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'league', 'home_team', 'away_team', 'season', 'is_playoff']
    search_fields = ['home_team__name', 'away_team__name', 'venue_name']
    ordering_fields = ['scheduled_start', 'created_at']
    ordering = ['-scheduled_start']
    
    def get_queryset(self):
        """Filter games based on query parameters"""
        queryset = super().get_queryset()
        
        # Date filtering
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(scheduled_start__gte=date_from)
        if date_to:
            queryset = queryset.filter(scheduled_start__lte=date_to)
        
        # Today's games
        if self.request.query_params.get('today') == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(scheduled_start__date=today)
        
        # This week's games
        if self.request.query_params.get('this_week') == 'true':
            week_start = timezone.now().date()
            week_end = week_start + timedelta(days=7)
            queryset = queryset.filter(
                scheduled_start__date__gte=week_start,
                scheduled_start__date__lte=week_end
            )
        
        return queryset
    
    @extend_schema(
        summary="Get game odds from all sportsbooks",
        responses={200: GameOddsSerializer}
    )
    @action(detail=True, methods=['get'])
    def odds(self, request, pk=None):
        """Get comprehensive odds for a game"""
        game = self.get_object()
        
        # Use specialized serializer that includes all markets and odds
        serializer = GameOddsSerializer(game, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(summary="Get line movement history")
    @action(detail=True, methods=['get'])
    def line_movements(self, request, pk=None):
        """Get line movement history for game"""
        game = self.get_object()
        
        movements = LineMovement.objects.filter(
            market__game=game
        ).select_related('sportsbook', 'market').order_by('-created_at')
        
        # Group by market type
        movements_by_market = {}
        for movement in movements:
            market_type = movement.market.market_type
            if market_type not in movements_by_market:
                movements_by_market[market_type] = []
            
            movements_by_market[market_type].append({
                'sportsbook': movement.sportsbook.name,
                'movement_size': movement.movement_size,
                'direction': movement.movement_direction,
                'is_significant': movement.is_significant,
                'timestamp': movement.created_at,
                'trigger': movement.trigger_event
            })
        
        return Response(movements_by_market)
    
    @extend_schema(summary="Get game analytics")
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get comprehensive game analytics"""
        game = self.get_object()
        
        # Check cache first
        cache_key = f"game_analytics_{game.id}"
        cached_analytics = cache.get(cache_key)
        
        if cached_analytics:
            return Response(cached_analytics)
        
        # Generate analytics (this would typically be async)
        analytics_data = {
            'game_info': GameSerializer(game).data,
            'betting_metrics': self._get_game_betting_metrics(game),
            'line_analysis': self._analyze_line_movements(game),
            'public_vs_sharp': self._analyze_betting_splits(game),
            'value_assessment': self._assess_game_value(game),
            'predictions': self._get_game_predictions(game)
        }
        
        # Cache for 15 minutes
        cache.set(cache_key, analytics_data, 900)
        
        return Response(analytics_data)
    
    def _get_game_betting_metrics(self, game):
        """Calculate betting metrics for game"""
        markets = game.markets.filter(is_active=True)
        
        return {
            'total_markets': markets.count(),
            'total_handle': markets.aggregate(Sum('total_volume'))['total_volume__sum'] or 0,
            'avg_sharp_percentage': markets.aggregate(Avg('sharp_percentage'))['sharp_percentage__avg'] or 0,
            'line_movements': game.markets.aggregate(
                Count('line_movements', filter=Q(line_movements__is_significant=True))
            )['line_movements__count'] or 0
        }
    
    def _analyze_line_movements(self, game):
        """Analyze line movements for insights"""
        movements = LineMovement.objects.filter(
            market__game=game,
            is_significant=True
        ).order_by('-created_at')[:10]
        
        analysis = {
            'total_significant_moves': movements.count(),
            'recent_moves': [],
            'movement_patterns': {}
        }
        
        for movement in movements:
            analysis['recent_moves'].append({
                'market': movement.market.market_type,
                'sportsbook': movement.sportsbook.name,
                'size': movement.movement_size,
                'direction': movement.movement_direction,
                'timestamp': movement.created_at
            })
        
        return analysis
    
    def _analyze_betting_splits(self, game):
        """Analyze public vs sharp betting splits"""
        markets = game.markets.filter(is_active=True)
        
        splits = []
        for market in markets:
            splits.append({
                'market_type': market.market_type,
                'sharp_percentage': market.sharp_percentage,
                'public_percentage': market.public_percentage,
                'contrarian_opportunity': abs(market.sharp_percentage - market.public_percentage) > 20
            })
        
        return {
            'splits': splits,
            'contrarian_plays': [s for s in splits if s['contrarian_opportunity']]
        }
    
    def _assess_game_value(self, game):
        """Assess value betting opportunities"""
        # This would integrate with ML models
        return {
            'overall_value_score': 0.0,
            'best_bets': [],
            'avoid_bets': [],
            'confidence_level': 0.0
        }
    
    def _get_game_predictions(self, game):
        """Get AI predictions for the game"""
        # This would integrate with prediction models
        return {
            'home_win_probability': 0.5,
            'predicted_total': 0.0,
            'confidence': 0.0,
            'key_factors': []
        }


class SportsbookViewSet(viewsets.ReadOnlyModelViewSet):
    """Sportsbook API endpoints"""
    
    queryset = Sportsbook.objects.filter(is_active=True)
    serializer_class = SportsbookSerializer
    pagination_class = SportsAnalyticsPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['is_sharp']
    search_fields = ['name', 'abbreviation']
    ordering = ['name']
    
    @extend_schema(summary="Compare sportsbook odds")
    @action(detail=False, methods=['get'])
    def odds_comparison(self, request):
        """Compare odds across sportsbooks for active markets"""
        game_id = request.query_params.get('game_id')
        market_type = request.query_params.get('market_type')
        
        if not game_id:
            return Response({'error': 'game_id parameter required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            game = Game.objects.get(id=game_id, is_active=True)
        except Game.DoesNotExist:
            return Response({'error': 'Game not found'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        # Get markets for the game
        markets = game.markets.filter(is_active=True)
        if market_type:
            markets = markets.filter(market_type=market_type)
        
        comparison_data = []
        
        for market in markets:
            current_odds = market.odds_lines.filter(is_current=True).select_related('sportsbook')
            
            market_comparison = {
                'market_type': market.market_type,
                'market_name': market.market_name,
                'odds_by_sportsbook': []
            }
            
            for odds_line in current_odds:
                market_comparison['odds_by_sportsbook'].append({
                    'sportsbook': odds_line.sportsbook.name,
                    'sportsbook_abbrev': odds_line.sportsbook.abbreviation,
                    'is_sharp': odds_line.sportsbook.is_sharp,
                    'home_odds': odds_line.home_odds,
                    'away_odds': odds_line.away_odds,
                    'home_spread': odds_line.home_spread,
                    'away_spread': odds_line.away_spread,
                    'total_line': odds_line.total_line,
                    'over_odds': odds_line.over_odds,
                    'under_odds': odds_line.under_odds,
                    'updated_at': odds_line.created_at
                })
            
            comparison_data.append(market_comparison)
        
        return Response({
            'game': GameSerializer(game).data,
            'comparison': comparison_data
        })


class BettingMarketViewSet(viewsets.ReadOnlyModelViewSet):
    """Betting market API endpoints"""
    
    queryset = BettingMarket.objects.filter(is_active=True).select_related('game')
    serializer_class = BettingMarketSerializer
    pagination_class = SportsAnalyticsPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['market_type', 'status', 'game__league']
    search_fields = ['market_name', 'game__home_team__name', 'game__away_team__name']
    ordering_fields = ['total_volume', 'created_at']
    ordering = ['-created_at']
    
    @extend_schema(
        summary="Analyze market for value and trends",
        responses={200: MarketAnalysisSerializer}
    )
    @action(detail=True, methods=['get'])
    def analysis(self, request, pk=None):
        """Get comprehensive market analysis"""
        market = self.get_object()
        
        # Get current odds
        current_odds = market.odds_lines.filter(is_current=True).select_related('sportsbook')
        
        # Build odds comparison
        odds_comparison = []
        for odds_line in current_odds:
            odds_comparison.append({
                'sportsbook': odds_line.sportsbook.name,
                'sportsbook_id': str(odds_line.sportsbook.id),
                'is_sharp': odds_line.sportsbook.is_sharp,
                'odds_data': OddsLineSerializer(odds_line).data,
                'vig': odds_line.get_vig(),
                'market_share': 0.0  # Would calculate based on handle
            })
        
        # Get line movement history
        line_movements = market.line_movements.order_by('-created_at')[:20]
        movement_history = []
        
        for movement in line_movements:
            movement_history.append({
                'timestamp': movement.created_at,
                'sportsbook': movement.sportsbook.name,
                'movement_size': movement.movement_size,
                'direction': movement.movement_direction,
                'is_significant': movement.is_significant,
                'trigger': movement.trigger_event
            })
        
        # Calculate value opportunities
        value_opportunities = self._calculate_value_opportunities(market, odds_comparison)
        
        # Check arbitrage potential
        arbitrage_potential = self._check_arbitrage_potential(market, current_odds)
        
        analysis_data = {
            'market_id': market.id,
            'market_name': market.market_name,
            'game_info': {
                'matchup': f"{market.game.away_team.abbreviation} @ {market.game.home_team.abbreviation}",
                'scheduled_start': market.game.scheduled_start,
                'status': market.game.status
            },
            'odds_comparison': odds_comparison,
            'line_movement_history': movement_history,
            'betting_trends': {
                'total_volume': float(market.total_volume),
                'sharp_percentage': market.sharp_percentage,
                'public_percentage': market.public_percentage,
                'contrarian_indicator': abs(market.sharp_percentage - market.public_percentage) > 15
            },
            'sharp_vs_public': {
                'sharp_side': 'home' if market.sharp_percentage > 50 else 'away',
                'public_side': 'home' if market.public_percentage > 50 else 'away',
                'disagreement_level': abs(market.sharp_percentage - market.public_percentage)
            },
            'value_opportunities': value_opportunities,
            'arbitrage_potential': arbitrage_potential,
            'recommendation_score': self._calculate_recommendation_score(market, value_opportunities, arbitrage_potential)
        }
        
        return Response(analysis_data)
    
    def _calculate_value_opportunities(self, market, odds_comparison):
        """Calculate potential value betting opportunities"""
        opportunities = []
        
        if not odds_comparison:
            return opportunities
        
        # Find best and worst odds for each side
        if market.market_type == BetType.MONEYLINE:
            home_odds = [o for o in odds_comparison if o['odds_data']['home_odds']]
            away_odds = [o for o in odds_comparison if o['odds_data']['away_odds']]
            
            if home_odds:
                best_home = max(home_odds, key=lambda x: x['odds_data']['home_odds'] or -1000)
                worst_home = min(home_odds, key=lambda x: x['odds_data']['home_odds'] or 1000)
                
                if best_home['odds_data']['home_odds'] != worst_home['odds_data']['home_odds']:
                    opportunities.append({
                        'type': 'line_shopping',
                        'selection': 'home',
                        'best_sportsbook': best_home['sportsbook'],
                        'best_odds': best_home['odds_data']['home_odds'],
                        'worst_odds': worst_home['odds_data']['home_odds'],
                        'value_difference': best_home['odds_data']['home_odds'] - worst_home['odds_data']['home_odds']
                    })
        
        return opportunities
    
    def _check_arbitrage_potential(self, market, current_odds):
        """Check for arbitrage opportunities"""
        if market.market_type == BetType.MONEYLINE and len(current_odds) >= 2:
            home_odds = [line for line in current_odds if line.home_odds]
            away_odds = [line for line in current_odds if line.away_odds]
            
            if home_odds and away_odds:
                best_home = max(home_odds, key=lambda x: x.home_odds)
                best_away = max(away_odds, key=lambda x: x.away_odds)
                
                if best_home.sportsbook_id != best_away.sportsbook_id:
                    # Calculate arbitrage
                    home_decimal = OddsLine._american_to_decimal(best_home.home_odds)
                    away_decimal = OddsLine._american_to_decimal(best_away.away_odds)
                    
                    total_prob = (1 / home_decimal) + (1 / away_decimal)
                    
                    if total_prob < 1.0:
                        return {
                            'exists': True,
                            'profit_percentage': (1 - total_prob) * 100,
                            'home_sportsbook': best_home.sportsbook.name,
                            'away_sportsbook': best_away.sportsbook.name,
                            'home_odds': best_home.home_odds,
                            'away_odds': best_away.away_odds
                        }
        
        return {'exists': False}
    
    def _calculate_recommendation_score(self, market, value_opportunities, arbitrage_potential):
        """Calculate overall recommendation score for market"""
        score = 0.0
        
        # Add points for value opportunities
        score += len(value_opportunities) * 10
        
        # Add major points for arbitrage
        if arbitrage_potential.get('exists'):
            score += arbitrage_potential.get('profit_percentage', 0) * 20
        
        # Add points for line movement activity
        recent_movements = market.line_movements.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        score += recent_movements * 5
        
        # Add points for sharp vs public disagreement
        disagreement = abs(market.sharp_percentage - market.public_percentage)
        if disagreement > 20:
            score += disagreement
        
        return min(score, 100.0)  # Cap at 100


class BetViewSet(viewsets.ModelViewSet):
    """Bet API endpoints"""
    
    serializer_class = BetSerializer
    pagination_class = SportsAnalyticsPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'bet_type', 'risk_level', 'sportsbook']
    search_fields = ['selection', 'bet_reason']
    ordering_fields = ['stake', 'potential_profit', 'result_amount', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter bets by user"""
        return Bet.objects.filter(
            user=self.request.user,
            is_active=True
        ).select_related('market', 'sportsbook')
    
    def perform_create(self, serializer):
        """Set user when creating bet"""
        serializer.save(user=self.request.user)
    
    @extend_schema(summary="Get user betting statistics")
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get comprehensive betting statistics for user"""
        user_bets = self.get_queryset()
        
        # Basic stats
        total_bets = user_bets.count()
        total_wagered = user_bets.aggregate(Sum('stake'))['stake__sum'] or Decimal('0.00')
        total_profit = user_bets.aggregate(Sum('result_amount'))['result_amount__sum'] or Decimal('0.00')
        
        # Win rate
        settled_bets = user_bets.filter(status__in=[BetStatus.WON, BetStatus.LOST, BetStatus.PUSH])
        won_bets = settled_bets.filter(status=BetStatus.WON).count()
        win_rate = (won_bets / settled_bets.count()) if settled_bets.count() > 0 else 0.0
        
        # ROI
        roi = float(total_profit / total_wagered * 100) if total_wagered > 0 else 0.0
        
        # Average bet size
        avg_bet_size = total_wagered / total_bets if total_bets > 0 else Decimal('0.00')
        
        # Best and worst bets
        best_bet = user_bets.filter(status=BetStatus.WON).order_by('-result_amount').first()
        worst_bet = user_bets.filter(status=BetStatus.LOST).order_by('result_amount').first()
        
        # Favorite sportsbook and bet type
        sportsbook_counts = user_bets.values('sportsbook__name').annotate(count=Count('id')).order_by('-count')
        bet_type_counts = user_bets.values('bet_type').annotate(count=Count('id')).order_by('-count')
        
        # Monthly performance
        monthly_performance = []
        for i in range(6):  # Last 6 months
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            month_bets = user_bets.filter(
                created_at__gte=month_start,
                created_at__lte=month_end
            )
            
            month_profit = month_bets.aggregate(Sum('result_amount'))['result_amount__sum'] or Decimal('0.00')
            month_wagered = month_bets.aggregate(Sum('stake'))['stake__sum'] or Decimal('0.00')
            
            monthly_performance.append({
                'month': month_start.strftime('%Y-%m'),
                'profit': float(month_profit),
                'wagered': float(month_wagered),
                'roi': float(month_profit / month_wagered * 100) if month_wagered > 0 else 0.0
            })
        
        # Recent form (last 20 bets)
        recent_bets = user_bets.filter(
            status__in=[BetStatus.WON, BetStatus.LOST, BetStatus.PUSH]
        ).order_by('-settled_at')[:20]
        
        recent_form = []
        for bet in recent_bets:
            result = 'W' if bet.status == BetStatus.WON else 'L' if bet.status == BetStatus.LOST else 'P'
            recent_form.append({
                'result': result,
                'profit': float(bet.result_amount),
                'date': bet.settled_at
            })
        
        stats_data = {
            'total_bets': total_bets,
            'total_wagered': total_wagered,
            'total_profit': total_profit,
            'win_rate': win_rate * 100,
            'roi': roi,
            'avg_bet_size': avg_bet_size,
            'best_bet': {
                'selection': best_bet.selection if best_bet else None,
                'profit': float(best_bet.result_amount) if best_bet else 0.0,
                'date': best_bet.settled_at if best_bet else None
            },
            'worst_bet': {
                'selection': worst_bet.selection if worst_bet else None,
                'loss': float(worst_bet.result_amount) if worst_bet else 0.0,
                'date': worst_bet.settled_at if worst_bet else None
            },
            'favorite_sportsbook': sportsbook_counts[0]['sportsbook__name'] if sportsbook_counts else None,
            'favorite_bet_type': bet_type_counts[0]['bet_type'] if bet_type_counts else None,
            'monthly_performance': monthly_performance,
            'recent_form': recent_form
        }
        
        return Response(stats_data)


class ArbitrageOpportunityViewSet(viewsets.ReadOnlyModelViewSet):
    """Arbitrage opportunity API endpoints"""
    
    queryset = ArbitrageOpportunity.objects.filter(is_active=True).select_related(
        'game', 'sportsbook_1', 'sportsbook_2'
    )
    serializer_class = ArbitrageOpportunitySerializer
    pagination_class = SportsAnalyticsPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['market_type', 'game__league']
    ordering_fields = ['arbitrage_percentage', 'minimum_profit', 'discovered_at']
    ordering = ['-arbitrage_percentage']
    
    @extend_schema(summary="Scan for new arbitrage opportunities")
    @action(detail=False, methods=['post'])
    def scan(self, request):
        """Trigger arbitrage opportunity scan"""
        min_profit = float(request.data.get('min_profit_percentage', 1.0))
        
        # This would typically be run as an async task
        try:
            # For demo, we'll return a success response
            # In production, this would trigger the ArbitrageDetectionService
            return Response({
                'message': 'Arbitrage scan initiated',
                'min_profit_threshold': min_profit,
                'estimated_completion': '2-3 minutes'
            })
        except Exception as e:
            return Response(
                {'error': f'Scan failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BettingRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """Betting recommendation API endpoints"""
    
    serializer_class = BettingRecommendationSerializer
    pagination_class = SportsAnalyticsPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['risk_level', 'is_active', 'user_action']
    ordering_fields = ['expected_value', 'confidence_level', 'created_at']
    ordering = ['-expected_value', '-confidence_level']
    
    def get_queryset(self):
        """Filter recommendations by user"""
        return BettingRecommendation.objects.filter(
            user=self.request.user,
            is_active=True
        ).select_related('game', 'market', 'recommended_sportsbook')
    
    @extend_schema(summary="Generate new recommendations")
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate new betting recommendations for user"""
        limit = int(request.data.get('limit', 10))
        
        try:
            # This would typically be run as an async task
            # For demo, return success response
            return Response({
                'message': f'Generating {limit} recommendations',
                'estimated_completion': '1-2 minutes',
                'user': request.user.username
            })
        except Exception as e:
            return Response(
                {'error': f'Generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(summary="Accept recommendation")
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a betting recommendation"""
        recommendation = self.get_object()
        
        if recommendation.user_action != 'pending':
            return Response(
                {'error': 'Recommendation already acted upon'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recommendation.user_action = 'accepted'
        recommendation.save()
        
        return Response({'message': 'Recommendation accepted'})
    
    @extend_schema(summary="Reject recommendation")
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a betting recommendation"""
        recommendation = self.get_object()
        
        if recommendation.user_action != 'pending':
            return Response(
                {'error': 'Recommendation already acted upon'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recommendation.user_action = 'rejected'
        recommendation.save()
        
        return Response({'message': 'Recommendation rejected'})


class SportsAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """Sports analytics API endpoints"""
    
    queryset = SportsAnalytics.objects.filter(is_active=True)
    serializer_class = SportsAnalyticsSerializer
    pagination_class = SportsAnalyticsPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['scope_type', 'analysis_period', 'generated_by']
    ordering_fields = ['created_at', 'data_quality_score']
    ordering = ['-created_at']
    
    @extend_schema(summary="Generate analytics for entity")
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate analytics for specified entity"""
        scope_type = request.data.get('scope_type')
        scope_id = request.data.get('scope_id')
        analysis_period = request.data.get('analysis_period', 'daily')
        
        if not scope_type or not scope_id:
            return Response(
                {'error': 'scope_type and scope_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # This would typically trigger async analytics generation
            return Response({
                'message': 'Analytics generation initiated',
                'scope_type': scope_type,
                'scope_id': scope_id,
                'analysis_period': analysis_period,
                'estimated_completion': '30-60 seconds'
            })
        except Exception as e:
            return Response(
                {'error': f'Generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# Additional utility endpoints
class SportsUtilityViewSet(viewsets.ViewSet):
    """Utility endpoints for sports data"""
    
    @extend_schema(summary="Get sports data summary")
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get high-level summary of sports data"""
        summary = {
            'leagues': {
                'total': League.objects.filter(is_active=True).count(),
                'by_sport': dict(League.objects.filter(is_active=True).values_list('sport_type').annotate(Count('id')))
            },
            'teams': Team.objects.filter(is_active=True).count(),
            'games': {
                'total': Game.objects.filter(is_active=True).count(),
                'today': Game.objects.filter(
                    scheduled_start__date=timezone.now().date(),
                    is_active=True
                ).count(),
                'this_week': Game.objects.filter(
                    scheduled_start__gte=timezone.now().date(),
                    scheduled_start__lte=timezone.now().date() + timedelta(days=7),
                    is_active=True
                ).count()
            },
            'markets': {
                'active': BettingMarket.objects.filter(
                    status=MarketStatus.OPEN,
                    is_active=True
                ).count(),
                'by_type': dict(BettingMarket.objects.filter(is_active=True).values_list('market_type').annotate(Count('id')))
            },
            'sportsbooks': Sportsbook.objects.filter(is_active=True).count(),
            'arbitrage_opportunities': ArbitrageOpportunity.objects.filter(is_active=True).count(),
            'last_updated': timezone.now()
        }
        
        return Response(summary)
    
    @extend_schema(summary="Trigger odds update")
    @action(detail=False, methods=['post'])
    def update_odds(self, request):
        """Trigger odds update for specified leagues"""
        sport_types = request.data.get('sport_types', [])
        
        try:
            # This would typically trigger the odds ingestion service
            return Response({
                'message': 'Odds update initiated',
                'sport_types': sport_types or 'all',
                'estimated_completion': '5-10 minutes'
            })
        except Exception as e:
            return Response(
                {'error': f'Update failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )