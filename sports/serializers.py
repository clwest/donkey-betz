"""
Sports Analytics API Serializers

Comprehensive serializers for REST API endpoints providing sports betting data,
odds, analytics, and betting recommendations with advanced filtering and aggregation.
"""

from rest_framework import serializers
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import models

from .models import (
    League, Team, Game, Sportsbook, BettingMarket, OddsLine,
    LineMovement, Bet, BankrollManagement, ArbitrageOpportunity,
    BettingRecommendation, SportsAnalytics
)


class LeagueSerializer(serializers.ModelSerializer):
    """League serializer with team and game counts"""
    
    team_count = serializers.SerializerMethodField()
    game_count = serializers.SerializerMethodField()
    active_markets = serializers.SerializerMethodField()
    
    class Meta:
        model = League
        fields = [
            'id', 'name', 'abbreviation', 'sport_type', 'country',
            'current_season', 'season_start_date', 'season_end_date',
            'team_count', 'game_count', 'active_markets', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_team_count(self, obj):
        return obj.teams.filter(is_active=True).count()
    
    def get_game_count(self, obj):
        return obj.games.filter(is_active=True).count()
    
    def get_active_markets(self, obj):
        return obj.games.filter(is_active=True).aggregate(
            count=models.Count('markets', filter=models.Q(markets__is_active=True))
        )['count'] or 0


class TeamSerializer(serializers.ModelSerializer):
    """Team serializer with performance metrics"""
    
    league_name = serializers.CharField(source='league.name', read_only=True)
    full_name = serializers.SerializerMethodField()
    recent_form = serializers.SerializerMethodField()
    upcoming_games = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'city', 'full_name', 'abbreviation', 'league',
            'league_name', 'conference', 'division', 'external_id',
            'logo_url', 'current_record', 'season_stats', 'ats_record',
            'ou_record', 'recent_form', 'upcoming_games', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_full_name(self, obj):
        return f"{obj.city} {obj.name}"
    
    def get_recent_form(self, obj):
        """Get recent game results"""
        from django.db.models import Q
        recent_games = Game.objects.filter(
            Q(home_team=obj) | Q(away_team=obj),
            status='final',
            is_active=True
        ).order_by('-scheduled_start')[:5]
        
        form = []
        for game in recent_games:
            if game.home_team == obj:
                team_score = game.home_score or 0
                opp_score = game.away_score or 0
                opponent = game.away_team.abbreviation
                home_away = 'H'
            else:
                team_score = game.away_score or 0
                opp_score = game.home_score or 0
                opponent = game.home_team.abbreviation
                home_away = 'A'
            
            result = 'W' if team_score > opp_score else 'L' if opp_score > team_score else 'T'
            form.append({
                'result': result,
                'score': f"{team_score}-{opp_score}",
                'opponent': opponent,
                'home_away': home_away,
                'date': game.scheduled_start.date()
            })
        
        return form
    
    def get_upcoming_games(self, obj):
        """Get upcoming games"""
        from django.db.models import Q
        from django.utils import timezone
        
        upcoming = Game.objects.filter(
            Q(home_team=obj) | Q(away_team=obj),
            scheduled_start__gte=timezone.now(),
            is_active=True
        ).order_by('scheduled_start')[:3]
        
        games = []
        for game in upcoming:
            if game.home_team == obj:
                opponent = game.away_team.abbreviation
                home_away = 'vs'
            else:
                opponent = game.home_team.abbreviation
                home_away = '@'
            
            games.append({
                'game_id': game.id,
                'opponent': opponent,
                'home_away': home_away,
                'date': game.scheduled_start,
                'venue': game.venue_name
            })
        
        return games


class GameSerializer(serializers.ModelSerializer):
    """Game serializer with detailed information"""
    
    home_team_name = serializers.CharField(source='home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.name', read_only=True)
    home_team_abbreviation = serializers.CharField(source='home_team.abbreviation', read_only=True)
    away_team_abbreviation = serializers.CharField(source='away_team.abbreviation', read_only=True)
    league_name = serializers.CharField(source='league.name', read_only=True)
    matchup = serializers.SerializerMethodField()
    final_score = serializers.SerializerMethodField()
    market_count = serializers.SerializerMethodField()
    total_handle = serializers.SerializerMethodField()
    time_to_start = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = [
            'id', 'external_id', 'league', 'league_name', 'home_team',
            'away_team', 'home_team_name', 'away_team_name',
            'home_team_abbreviation', 'away_team_abbreviation', 'matchup',
            'scheduled_start', 'actual_start', 'status', 'venue_name',
            'venue_city', 'season', 'week', 'is_playoff', 'weather_data',
            'home_score', 'away_score', 'final_score', 'current_period',
            'time_remaining', 'live_stats', 'total_handle', 'sharp_action',
            'public_betting', 'market_count', 'time_to_start', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_matchup(self, obj):
        return f"{obj.away_team.abbreviation} @ {obj.home_team.abbreviation}"
    
    def get_final_score(self, obj):
        if obj.home_score is not None and obj.away_score is not None:
            return f"{obj.away_score} - {obj.home_score}"
        return None
    
    def get_market_count(self, obj):
        return obj.markets.filter(is_active=True).count()
    
    def get_total_handle(self, obj):
        from django.db.models import Sum
        return obj.markets.aggregate(Sum('total_volume'))['total_volume__sum'] or 0
    
    def get_time_to_start(self, obj):
        from django.utils import timezone
        if obj.scheduled_start > timezone.now():
            delta = obj.scheduled_start - timezone.now()
            return {
                'seconds': int(delta.total_seconds()),
                'human_readable': str(delta).split('.')[0]  # Remove microseconds
            }
        return None


class SportsbookSerializer(serializers.ModelSerializer):
    """Sportsbook serializer"""
    
    odds_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Sportsbook
        fields = [
            'id', 'name', 'abbreviation', 'is_sharp', 'line_speed',
            'accuracy_score', 'betting_limits', 'supported_markets',
            'legal_states', 'odds_count', 'is_active', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'api_endpoint': {'write_only': True},
            'api_key_config': {'write_only': True}
        }
    
    def get_odds_count(self, obj):
        return obj.odds_lines.filter(is_current=True).count()


class BettingMarketSerializer(serializers.ModelSerializer):
    """Betting market serializer with odds"""
    
    game_matchup = serializers.CharField(source='game.__str__', read_only=True)
    odds_lines = serializers.SerializerMethodField()
    best_odds = serializers.SerializerMethodField()
    line_movements = serializers.SerializerMethodField()
    
    class Meta:
        model = BettingMarket
        fields = [
            'id', 'game', 'game_matchup', 'market_type', 'market_name',
            'status', 'market_params', 'settlement_value', 'settled_at',
            'total_volume', 'sharp_percentage', 'public_percentage',
            'odds_lines', 'best_odds', 'line_movements', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_odds_lines(self, obj):
        current_lines = obj.odds_lines.filter(is_current=True).select_related('sportsbook')
        return OddsLineSerializer(current_lines, many=True, context=self.context).data
    
    def get_best_odds(self, obj):
        """Find best odds across sportsbooks"""
        current_lines = obj.odds_lines.filter(is_current=True)
        
        best = {}
        if obj.market_type == 'moneyline':
            # Best home odds (most positive or least negative)
            home_lines = current_lines.filter(home_odds__isnull=False)
            if home_lines:
                best_home = max(home_lines, key=lambda x: x.home_odds)
                best['home'] = {
                    'odds': best_home.home_odds,
                    'sportsbook': best_home.sportsbook.abbreviation
                }
            
            # Best away odds
            away_lines = current_lines.filter(away_odds__isnull=False)
            if away_lines:
                best_away = max(away_lines, key=lambda x: x.away_odds)
                best['away'] = {
                    'odds': best_away.away_odds,
                    'sportsbook': best_away.sportsbook.abbreviation
                }
        
        elif obj.market_type == 'total':
            # Best over odds
            over_lines = current_lines.filter(over_odds__isnull=False)
            if over_lines:
                best_over = max(over_lines, key=lambda x: x.over_odds)
                best['over'] = {
                    'odds': best_over.over_odds,
                    'line': best_over.total_line,
                    'sportsbook': best_over.sportsbook.abbreviation
                }
            
            # Best under odds
            under_lines = current_lines.filter(under_odds__isnull=False)
            if under_lines:
                best_under = max(under_lines, key=lambda x: x.under_odds)
                best['under'] = {
                    'odds': best_under.under_odds,
                    'line': best_under.total_line,
                    'sportsbook': best_under.sportsbook.abbreviation
                }
        
        return best
    
    def get_line_movements(self, obj):
        """Recent significant line movements"""
        movements = obj.line_movements.filter(is_significant=True).order_by('-created_at')[:5]
        return LineMovementSerializer(movements, many=True).data


class OddsLineSerializer(serializers.ModelSerializer):
    """Odds line serializer"""
    
    sportsbook_name = serializers.CharField(source='sportsbook.name', read_only=True)
    sportsbook_abbreviation = serializers.CharField(source='sportsbook.abbreviation', read_only=True)
    vig = serializers.SerializerMethodField()
    
    class Meta:
        model = OddsLine
        fields = [
            'id', 'sportsbook', 'sportsbook_name', 'sportsbook_abbreviation',
            'home_odds', 'away_odds', 'home_spread', 'away_spread',
            'total_line', 'over_odds', 'under_odds', 'line_sequence',
            'is_current', 'opened_at', 'closed_at', 'implied_probabilities',
            'decimal_odds', 'movement_reason', 'sharp_move', 'vig',
            'created_at', 'updated_at'
        ]
    
    def get_vig(self, obj):
        """Calculate vigorish/juice"""
        return obj.get_vig()


class LineMovementSerializer(serializers.ModelSerializer):
    """Line movement serializer"""
    
    sportsbook_name = serializers.CharField(source='sportsbook.name', read_only=True)
    market_name = serializers.CharField(source='market.market_name', read_only=True)
    
    class Meta:
        model = LineMovement
        fields = [
            'id', 'sportsbook', 'sportsbook_name', 'market_name',
            'movement_size', 'movement_direction', 'is_significant',
            'trigger_event', 'betting_volume_factor', 'news_factor',
            'created_at'
        ]


class BetSerializer(serializers.ModelSerializer):
    """Bet serializer"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    game_matchup = serializers.CharField(source='market.game.__str__', read_only=True)
    sportsbook_name = serializers.CharField(source='sportsbook.name', read_only=True)
    profit_loss = serializers.SerializerMethodField()
    roi = serializers.SerializerMethodField()
    
    class Meta:
        model = Bet
        fields = [
            'id', 'user', 'username', 'market', 'game_matchup', 'sportsbook',
            'sportsbook_name', 'bet_type', 'selection', 'odds_taken',
            'stake', 'potential_payout', 'potential_profit', 'status',
            'result_amount', 'profit_loss', 'roi', 'settled_at',
            'kelly_percentage', 'edge_percentage', 'risk_level',
            'expected_value', 'confidence_level', 'bet_reason',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'agent_recommendation': {'write_only': True}
        }
    
    def get_profit_loss(self, obj):
        if obj.status in ['won', 'lost', 'push']:
            return float(obj.result_amount)
        return None
    
    def get_roi(self, obj):
        if obj.status in ['won', 'lost', 'push'] and obj.stake > 0:
            return float(obj.result_amount / obj.stake * 100)
        return None


class BankrollManagementSerializer(serializers.ModelSerializer):
    """Bankroll management serializer"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    performance_summary = serializers.SerializerMethodField()
    risk_metrics = serializers.SerializerMethodField()
    
    class Meta:
        model = BankrollManagement
        fields = [
            'id', 'user', 'username', 'current_balance', 'initial_balance',
            'max_bet_percentage', 'kelly_multiplier', 'risk_tolerance',
            'total_wagered', 'total_profit', 'win_rate', 'roi_percentage',
            'current_streak', 'longest_winning_streak', 'longest_losing_streak',
            'volatility_score', 'daily_loss_limit', 'monthly_loss_limit',
            'performance_summary', 'risk_metrics', 'created_at', 'updated_at'
        ]
    
    def get_performance_summary(self, obj):
        """Performance summary metrics"""
        return {
            'total_return': float(obj.total_profit),
            'return_percentage': float(obj.total_profit / obj.initial_balance * 100) if obj.initial_balance > 0 else 0,
            'total_bets': obj.user.bets.count(),
            'avg_bet_size': float(obj.total_wagered / obj.user.bets.count()) if obj.user.bets.count() > 0 else 0,
            'profitable': obj.total_profit > 0
        }
    
    def get_risk_metrics(self, obj):
        """Risk assessment metrics"""
        return {
            'kelly_utilization': 'conservative' if obj.kelly_multiplier < 0.5 else 'moderate' if obj.kelly_multiplier < 1.0 else 'aggressive',
            'volatility_level': 'low' if obj.volatility_score < 0.2 else 'medium' if obj.volatility_score < 0.5 else 'high',
            'current_risk_status': obj.risk_tolerance
        }


class ArbitrageOpportunitySerializer(serializers.ModelSerializer):
    """Arbitrage opportunity serializer"""
    
    game_matchup = serializers.CharField(source='game.__str__', read_only=True)
    sportsbook_1_name = serializers.CharField(source='sportsbook_1.name', read_only=True)
    sportsbook_2_name = serializers.CharField(source='sportsbook_2.name', read_only=True)
    profit_calculation = serializers.SerializerMethodField()
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = ArbitrageOpportunity
        fields = [
            'id', 'game', 'game_matchup', 'market_type', 'sportsbook_1',
            'sportsbook_2', 'sportsbook_1_name', 'sportsbook_2_name',
            'odds_1', 'odds_2', 'selection_1', 'selection_2',
            'arbitrage_percentage', 'stake_1_percentage', 'stake_2_percentage',
            'minimum_profit', 'discovered_at', 'expires_at', 'is_active',
            'confidence_score', 'risk_factors', 'profit_calculation',
            'time_remaining', 'created_at'
        ]
        extra_kwargs = {
            'closed_reason': {'write_only': True}
        }
    
    def get_profit_calculation(self, obj):
        """Calculate profit for different stake amounts"""
        return {
            '$100_stake': {
                'bet_1': float(100 * obj.stake_1_percentage / 100),
                'bet_2': float(100 * obj.stake_2_percentage / 100),
                'guaranteed_profit': float(100 * obj.arbitrage_percentage / 100)
            },
            '$500_stake': {
                'bet_1': float(500 * obj.stake_1_percentage / 100),
                'bet_2': float(500 * obj.stake_2_percentage / 100),
                'guaranteed_profit': float(500 * obj.arbitrage_percentage / 100)
            },
            '$1000_stake': {
                'bet_1': float(1000 * obj.stake_1_percentage / 100),
                'bet_2': float(1000 * obj.stake_2_percentage / 100),
                'guaranteed_profit': float(1000 * obj.arbitrage_percentage / 100)
            }
        }
    
    def get_time_remaining(self, obj):
        from django.utils import timezone
        if obj.expires_at > timezone.now():
            delta = obj.expires_at - timezone.now()
            return {
                'seconds': int(delta.total_seconds()),
                'human_readable': str(delta).split('.')[0]
            }
        return None


class BettingRecommendationSerializer(serializers.ModelSerializer):
    """Betting recommendation serializer"""
    
    username = serializers.CharField(source='user.username', read_only=True)
    game_matchup = serializers.CharField(source='game.__str__', read_only=True)
    sportsbook_name = serializers.CharField(source='recommended_sportsbook.name', read_only=True)
    recommendation_summary = serializers.SerializerMethodField()
    time_to_game = serializers.SerializerMethodField()
    
    class Meta:
        model = BettingRecommendation
        fields = [
            'id', 'user', 'username', 'game', 'game_matchup', 'market',
            'recommended_selection', 'recommended_sportsbook', 'sportsbook_name',
            'recommended_odds', 'recommended_stake', 'expected_value',
            'win_probability', 'confidence_level', 'edge_percentage',
            'risk_level', 'kelly_percentage', 'generating_agent',
            'reasoning', 'expires_at', 'is_active', 'user_action',
            'recommendation_summary', 'time_to_game', 'created_at'
        ]
        extra_kwargs = {
            'analysis_factors': {'write_only': True},
            'model_predictions': {'write_only': True},
            'historical_performance': {'write_only': True}
        }
    
    def get_recommendation_summary(self, obj):
        """Summary of recommendation key points"""
        return {
            'selection': obj.recommended_selection,
            'stake': f"${obj.recommended_stake}",
            'odds': obj.recommended_odds,
            'expected_profit': f"${obj.expected_value}",
            'confidence': f"{obj.confidence_level:.0%}",
            'risk': obj.risk_level,
            'kelly_size': f"{obj.kelly_percentage:.1f}%"
        }
    
    def get_time_to_game(self, obj):
        from django.utils import timezone
        if obj.game.scheduled_start > timezone.now():
            delta = obj.game.scheduled_start - timezone.now()
            return {
                'seconds': int(delta.total_seconds()),
                'human_readable': str(delta).split('.')[0]
            }
        return None


class SportsAnalyticsSerializer(serializers.ModelSerializer):
    """Sports analytics serializer"""
    
    analytics_summary = serializers.SerializerMethodField()
    key_insights = serializers.SerializerMethodField()
    
    class Meta:
        model = SportsAnalytics
        fields = [
            'id', 'scope_type', 'scope_id', 'analysis_period',
            'period_start', 'period_end', 'metrics', 'trends',
            'predictions', 'comparative_analysis', 'generated_by',
            'computation_time_seconds', 'data_quality_score',
            'analytics_summary', 'key_insights', 'created_at'
        ]
    
    def get_analytics_summary(self, obj):
        """High-level summary of analytics"""
        summary = {
            'analysis_type': f"{obj.scope_type} {obj.analysis_period}",
            'data_quality': 'High' if obj.data_quality_score >= 0.8 else 'Medium' if obj.data_quality_score >= 0.6 else 'Low',
            'computation_time': f"{obj.computation_time_seconds:.2f}s",
            'generated_by': obj.generated_by
        }
        
        # Add key metrics if available
        if obj.metrics:
            if 'win_rate' in obj.metrics:
                summary['win_rate'] = f"{obj.metrics['win_rate']:.1%}"
            if 'total_handle' in obj.metrics:
                summary['betting_volume'] = f"${obj.metrics['total_handle']:,.0f}"
        
        return summary
    
    def get_key_insights(self, obj):
        """Extract key insights from analytics data"""
        insights = []
        
        if obj.trends:
            if 'home_team_form' in obj.trends:
                form = obj.trends['home_team_form']
                if form.get('win_rate', 0) > 0.7:
                    insights.append("Home team in excellent form")
                elif form.get('win_rate', 0) < 0.3:
                    insights.append("Home team struggling recently")
        
        if obj.predictions:
            if 'home_win_probability' in obj.predictions:
                prob = obj.predictions['home_win_probability']
                if prob > 0.65:
                    insights.append("Strong home team advantage predicted")
                elif prob < 0.35:
                    insights.append("Away team heavily favored")
        
        return insights[:5]  # Return top 5 insights


# Custom serializers for specific API endpoints
class GameOddsSerializer(serializers.ModelSerializer):
    """Specialized serializer for game odds display"""
    
    matchup = serializers.SerializerMethodField()
    markets = BettingMarketSerializer(many=True, read_only=True)
    
    class Meta:
        model = Game
        fields = ['id', 'matchup', 'scheduled_start', 'status', 'markets']
    
    def get_matchup(self, obj):
        return f"{obj.away_team.abbreviation} @ {obj.home_team.abbreviation}"


class UserBettingStatsSerializer(serializers.Serializer):
    """Custom serializer for user betting statistics"""
    
    total_bets = serializers.IntegerField()
    total_wagered = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    win_rate = serializers.FloatField()
    roi = serializers.FloatField()
    avg_bet_size = serializers.DecimalField(max_digits=10, decimal_places=2)
    best_bet = serializers.DictField()
    worst_bet = serializers.DictField()
    favorite_sportsbook = serializers.CharField()
    favorite_bet_type = serializers.CharField()
    monthly_performance = serializers.ListField()
    recent_form = serializers.ListField()


class MarketAnalysisSerializer(serializers.Serializer):
    """Custom serializer for market analysis"""
    
    market_id = serializers.UUIDField()
    market_name = serializers.CharField()
    game_info = serializers.DictField()
    odds_comparison = serializers.ListField()
    line_movement_history = serializers.ListField()
    betting_trends = serializers.DictField()
    sharp_vs_public = serializers.DictField()
    value_opportunities = serializers.ListField()
    arbitrage_potential = serializers.DictField()
    recommendation_score = serializers.FloatField()


class LeagueStandingsSerializer(serializers.Serializer):
    """Custom serializer for league standings"""
    
    league_id = serializers.UUIDField()
    league_name = serializers.CharField()
    standings = serializers.ListField()
    playoff_picture = serializers.DictField()
    key_matchups = serializers.ListField()
    betting_insights = serializers.DictField()