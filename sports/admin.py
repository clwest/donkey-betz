"""
Sports Analytics Admin Interface

Provides comprehensive admin interface for managing sports betting data,
odds, lines, bets, and analytics through Django's admin system.
"""

from django.contrib import admin
from django.db.models import Count, Avg, Sum
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    League, Team, Game, Sportsbook, BettingMarket, OddsLine,
    LineMovement, Bet, BankrollManagement, ArbitrageOpportunity,
    BettingRecommendation, SportsAnalytics
)


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'abbreviation', 'sport_type', 'country',
        'current_season', 'team_count', 'game_count'
    ]
    list_filter = ['sport_type', 'country', 'is_active']
    search_fields = ['name', 'abbreviation']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'abbreviation', 'sport_type', 'country', 'is_active']
        }),
        ('Season Information', {
            'fields': ['current_season', 'season_start_date', 'season_end_date']
        }),
        ('API Configuration', {
            'fields': ['api_provider', 'api_config'],
            'classes': ['collapse']
        }),
        ('Betting Rules', {
            'fields': ['betting_rules'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['metadata', 'version'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def team_count(self, obj):
        return obj.teams.count()
    team_count.short_description = 'Teams'
    
    def game_count(self, obj):
        return obj.games.count()
    game_count.short_description = 'Games'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'abbreviation', 'league', 'conference',
        'division', 'current_wins', 'current_losses'
    ]
    list_filter = ['league', 'conference', 'division', 'is_active']
    search_fields = ['name', 'city', 'abbreviation']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'city', 'abbreviation', 'league', 'is_active']
        }),
        ('Organization', {
            'fields': ['conference', 'division']
        }),
        ('External Data', {
            'fields': ['external_id', 'logo_url']
        }),
        ('Performance', {
            'fields': ['current_record', 'season_stats'],
            'classes': ['collapse']
        }),
        ('Betting Performance', {
            'fields': ['ats_record', 'ou_record'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['metadata', 'version'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def full_name(self, obj):
        return f"{obj.city} {obj.name}"
    full_name.short_description = 'Full Name'
    
    def current_wins(self, obj):
        return obj.current_record.get('wins', 0)
    current_wins.short_description = 'Wins'
    
    def current_losses(self, obj):
        return obj.current_record.get('losses', 0)
    current_losses.short_description = 'Losses'


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = [
        'matchup', 'scheduled_start', 'status', 'final_score',
        'league', 'market_count', 'bet_count'
    ]
    list_filter = [
        'status', 'league', 'scheduled_start', 'is_playoff', 'is_active'
    ]
    search_fields = [
        'home_team__name', 'away_team__name', 'home_team__city', 'away_team__city'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'scheduled_start'
    
    fieldsets = [
        ('Game Information', {
            'fields': ['league', 'home_team', 'away_team', 'status', 'is_active']
        }),
        ('Scheduling', {
            'fields': ['scheduled_start', 'actual_start', 'season', 'week', 'is_playoff']
        }),
        ('Venue', {
            'fields': ['venue_name', 'venue_city']
        }),
        ('External Data', {
            'fields': ['external_id']
        }),
        ('Results', {
            'fields': ['home_score', 'away_score', 'current_period', 'time_remaining']
        }),
        ('Live Data', {
            'fields': ['live_stats'],
            'classes': ['collapse']
        }),
        ('Weather', {
            'fields': ['weather_data'],
            'classes': ['collapse']
        }),
        ('Betting Context', {
            'fields': ['total_handle', 'sharp_action', 'public_betting'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['metadata', 'version'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def matchup(self, obj):
        return f"{obj.away_team.abbreviation} @ {obj.home_team.abbreviation}"
    matchup.short_description = 'Matchup'
    
    def final_score(self, obj):
        if obj.home_score is not None and obj.away_score is not None:
            return f"{obj.away_score} - {obj.home_score}"
        return "Not Final"
    final_score.short_description = 'Score'
    
    def market_count(self, obj):
        return obj.markets.count()
    market_count.short_description = 'Markets'
    
    def bet_count(self, obj):
        return sum(market.bets.count() for market in obj.markets.all())
    bet_count.short_description = 'Bets'


@admin.register(Sportsbook)
class SportsbookAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'abbreviation', 'is_sharp', 'line_speed',
        'accuracy_score', 'odds_count', 'is_active'
    ]
    list_filter = ['is_sharp', 'is_active']
    search_fields = ['name', 'abbreviation']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['name', 'abbreviation', 'is_active']
        }),
        ('Characteristics', {
            'fields': ['is_sharp', 'line_speed', 'accuracy_score']
        }),
        ('API Configuration', {
            'fields': ['api_endpoint', 'api_key_config'],
            'classes': ['collapse']
        }),
        ('Markets and Limits', {
            'fields': ['betting_limits', 'supported_markets'],
            'classes': ['collapse']
        }),
        ('Regional', {
            'fields': ['legal_states'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['metadata', 'version'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def odds_count(self, obj):
        return obj.odds_lines.count()
    odds_count.short_description = 'Odds Lines'


@admin.register(BettingMarket)
class BettingMarketAdmin(admin.ModelAdmin):
    list_display = [
        'market_display', 'market_type', 'status', 'game_date',
        'odds_count', 'bet_count', 'total_volume'
    ]
    list_filter = ['market_type', 'status', 'is_active']
    search_fields = ['market_name', 'game__home_team__name', 'game__away_team__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Market Information', {
            'fields': ['game', 'market_type', 'market_name', 'status', 'is_active']
        }),
        ('Parameters', {
            'fields': ['market_params']
        }),
        ('Settlement', {
            'fields': ['settlement_value', 'settled_at']
        }),
        ('Analytics', {
            'fields': ['total_volume', 'sharp_percentage', 'public_percentage']
        }),
        ('Metadata', {
            'fields': ['metadata', 'version'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def market_display(self, obj):
        return f"{obj.game.away_team.abbreviation} @ {obj.game.home_team.abbreviation} - {obj.market_name}"
    market_display.short_description = 'Market'
    
    def game_date(self, obj):
        return obj.game.scheduled_start.strftime('%Y-%m-%d %H:%M')
    game_date.short_description = 'Game Date'
    
    def odds_count(self, obj):
        return obj.odds_lines.count()
    odds_count.short_description = 'Odds'
    
    def bet_count(self, obj):
        return obj.bets.count()
    bet_count.short_description = 'Bets'


@admin.register(OddsLine)
class OddsLineAdmin(admin.ModelAdmin):
    list_display = [
        'line_display', 'sportsbook', 'line_sequence', 'is_current',
        'home_odds', 'away_odds', 'created_at'
    ]
    list_filter = ['is_current', 'sportsbook', 'sharp_move']
    search_fields = [
        'market__game__home_team__name',
        'market__game__away_team__name',
        'sportsbook__name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'implied_probabilities', 'decimal_odds']
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('Line Information', {
            'fields': ['market', 'sportsbook', 'line_sequence', 'is_current']
        }),
        ('Moneyline Odds', {
            'fields': ['home_odds', 'away_odds']
        }),
        ('Spread/Total', {
            'fields': ['home_spread', 'away_spread', 'total_line', 'over_odds', 'under_odds']
        }),
        ('Timing', {
            'fields': ['opened_at', 'closed_at']
        }),
        ('Movement Context', {
            'fields': ['movement_reason', 'sharp_move']
        }),
        ('Calculated Values', {
            'fields': ['implied_probabilities', 'decimal_odds'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['metadata', 'version'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def line_display(self, obj):
        game = obj.market.game
        return f"{game.away_team.abbreviation} @ {game.home_team.abbreviation} - {obj.market.market_type}"
    line_display.short_description = 'Line'


@admin.register(LineMovement)
class LineMovementAdmin(admin.ModelAdmin):
    list_display = [
        'movement_display', 'sportsbook', 'movement_direction',
        'movement_size', 'is_significant', 'created_at'
    ]
    list_filter = ['movement_direction', 'is_significant', 'sportsbook']
    search_fields = [
        'market__game__home_team__name',
        'market__game__away_team__name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def movement_display(self, obj):
        game = obj.market.game
        return f"{game.away_team.abbreviation} @ {game.home_team.abbreviation} - {obj.market.market_type}"
    movement_display.short_description = 'Movement'


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = [
        'bet_display', 'user', 'status', 'stake', 'odds_taken',
        'potential_profit', 'result_amount', 'placed_date'
    ]
    list_filter = ['status', 'bet_type', 'risk_level', 'sportsbook']
    search_fields = ['user__username', 'selection']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'potential_payout', 'potential_profit'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('Bet Information', {
            'fields': ['user', 'market', 'sportsbook', 'odds_line']
        }),
        ('Bet Details', {
            'fields': ['bet_type', 'selection', 'odds_taken', 'stake']
        }),
        ('Calculated Values', {
            'fields': ['potential_payout', 'potential_profit']
        }),
        ('Kelly Criterion', {
            'fields': ['kelly_percentage', 'edge_percentage', 'risk_level']
        }),
        ('Analytics', {
            'fields': ['expected_value', 'confidence_level']
        }),
        ('Result', {
            'fields': ['status', 'result_amount', 'settled_at']
        }),
        ('Context', {
            'fields': ['bet_reason', 'agent_recommendation'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['metadata', 'version'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def bet_display(self, obj):
        return f"{obj.selection} ${obj.stake} @ {obj.odds_taken}"
    bet_display.short_description = 'Bet'
    
    def placed_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    placed_date.short_description = 'Placed'


@admin.register(BankrollManagement)
class BankrollManagementAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'current_balance', 'total_profit', 'win_rate',
        'roi_percentage', 'risk_tolerance', 'current_streak'
    ]
    list_filter = ['risk_tolerance']
    search_fields = ['user__username']
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'total_wagered', 'total_profit',
        'win_rate', 'roi_percentage', 'current_streak', 'longest_winning_streak',
        'longest_losing_streak', 'volatility_score'
    ]
    
    fieldsets = [
        ('User', {
            'fields': ['user']
        }),
        ('Bankroll', {
            'fields': ['current_balance', 'initial_balance']
        }),
        ('Risk Management', {
            'fields': ['max_bet_percentage', 'kelly_multiplier', 'risk_tolerance']
        }),
        ('Performance Metrics', {
            'fields': [
                'total_wagered', 'total_profit', 'win_rate', 'roi_percentage'
            ]
        }),
        ('Streaks', {
            'fields': [
                'current_streak', 'longest_winning_streak', 'longest_losing_streak',
                'volatility_score'
            ]
        }),
        ('Limits', {
            'fields': ['daily_loss_limit', 'monthly_loss_limit']
        }),
        ('Metadata', {
            'fields': ['metadata', 'version'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]


@admin.register(ArbitrageOpportunity)
class ArbitrageOpportunityAdmin(admin.ModelAdmin):
    list_display = [
        'opportunity_display', 'arbitrage_percentage', 'minimum_profit',
        'is_active', 'confidence_score', 'discovered_at'
    ]
    list_filter = ['is_active', 'market_type']
    search_fields = [
        'game__home_team__name', 'game__away_team__name',
        'sportsbook_1__name', 'sportsbook_2__name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at', 'discovered_at']
    date_hierarchy = 'discovered_at'
    
    fieldsets = [
        ('Opportunity', {
            'fields': ['game', 'market_type', 'is_active']
        }),
        ('Sportsbooks', {
            'fields': [
                'sportsbook_1', 'sportsbook_2',
                'odds_1', 'odds_2',
                'selection_1', 'selection_2'
            ]
        }),
        ('Profit Analysis', {
            'fields': [
                'arbitrage_percentage', 'stake_1_percentage', 'stake_2_percentage',
                'minimum_profit'
            ]
        }),
        ('Lifecycle', {
            'fields': ['discovered_at', 'expires_at', 'closed_reason']
        }),
        ('Risk Assessment', {
            'fields': ['risk_factors', 'confidence_score']
        }),
        ('Metadata', {
            'fields': ['metadata', 'version'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def opportunity_display(self, obj):
        return f"{obj.game.away_team.abbreviation} @ {obj.game.home_team.abbreviation} - {obj.market_type}"
    opportunity_display.short_description = 'Opportunity'


@admin.register(BettingRecommendation)
class BettingRecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'recommendation_display', 'user', 'expected_value', 'confidence_level',
        'risk_level', 'user_action', 'is_active'
    ]
    list_filter = ['risk_level', 'user_action', 'is_active', 'generating_agent']
    search_fields = [
        'user__username', 'recommended_selection',
        'game__home_team__name', 'game__away_team__name'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = [
        ('Recommendation', {
            'fields': ['user', 'game', 'market', 'is_active']
        }),
        ('Details', {
            'fields': [
                'recommended_selection', 'recommended_sportsbook',
                'recommended_odds', 'recommended_stake'
            ]
        }),
        ('Analysis', {
            'fields': [
                'expected_value', 'win_probability', 'confidence_level',
                'edge_percentage'
            ]
        }),
        ('Risk', {
            'fields': ['risk_level', 'kelly_percentage']
        }),
        ('AI Analysis', {
            'fields': ['generating_agent', 'reasoning'],
            'classes': ['collapse']
        }),
        ('Model Data', {
            'fields': ['analysis_factors', 'model_predictions', 'historical_performance'],
            'classes': ['collapse']
        }),
        ('Lifecycle', {
            'fields': ['expires_at', 'user_action', 'bet_placed', 'actual_result']
        }),
        ('Metadata', {
            'fields': ['metadata', 'version'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def recommendation_display(self, obj):
        return f"{obj.recommended_selection} - EV: {obj.expected_value}"
    recommendation_display.short_description = 'Recommendation'


@admin.register(SportsAnalytics)
class SportsAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        'analytics_display', 'scope_type', 'analysis_period',
        'period_start', 'period_end', 'data_quality_score'
    ]
    list_filter = ['scope_type', 'analysis_period', 'generated_by']
    search_fields = ['scope_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'computation_time_seconds']
    date_hierarchy = 'created_at'
    
    fieldsets = [
        ('Analytics Scope', {
            'fields': ['scope_type', 'scope_id', 'analysis_period']
        }),
        ('Time Period', {
            'fields': ['period_start', 'period_end']
        }),
        ('Data', {
            'fields': ['metrics', 'trends', 'predictions', 'comparative_analysis'],
            'classes': ['collapse']
        }),
        ('Generation', {
            'fields': [
                'generated_by', 'computation_time_seconds', 'data_quality_score'
            ]
        }),
        ('Metadata', {
            'fields': ['metadata', 'version'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['id', 'created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def analytics_display(self, obj):
        return f"{obj.scope_type.title()} Analytics - {obj.analysis_period}"
    analytics_display.short_description = 'Analytics'


# Custom admin site configuration
admin.site.site_header = "Unified Donkey Betz - Sports Analytics"
admin.site.site_title = "Sports Analytics Admin"
admin.site.index_title = "Sports Betting Intelligence Platform"