"""
Unified Sports Analytics & Betting Intelligence Models

Comprehensive models for sports betting analytics, odds management, Kelly Criterion calculations,
real-time data tracking, and betting recommendation systems integrated with the Unified Donkey Betz Platform.

Features:
- Complete sports data hierarchy (leagues, teams, games, markets, lines)
- Real-time odds tracking and line movement analysis
- Kelly Criterion bet sizing with advanced risk management
- Arbitrage detection and alert systems
- Expected Value (EV) calculations and betting recommendations
- Integration with agent orchestration system for sports intelligence
- WebSocket support for live data streaming
- Comprehensive analytics and performance tracking
"""

import math
from decimal import Decimal
from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import Avg, Sum

from core.models import UnifiedBaseModel

User = get_user_model()


class SportType(models.TextChoices):
    """Supported sports types"""
    NFL = 'nfl', 'National Football League'
    NCAAF = 'ncaaf', 'NCAA Football'
    NBA = 'nba', 'National Basketball Association'
    NCAAB = 'ncaab', 'NCAA Basketball'
    MLB = 'mlb', 'Major League Baseball'
    NHL = 'nhl', 'National Hockey League'
    SOCCER = 'soccer', 'Soccer'
    MMA = 'mma', 'Mixed Martial Arts'
    TENNIS = 'tennis', 'Tennis'
    GOLF = 'golf', 'Golf'
    BOXING = 'boxing', 'Boxing'
    ESPORTS = 'esports', 'E-Sports'


class GameStatus(models.TextChoices):
    """Game status values"""
    SCHEDULED = 'scheduled', 'Scheduled'
    LIVE = 'live', 'Live'
    HALFTIME = 'halftime', 'Halftime'
    FINAL = 'final', 'Final'
    POSTPONED = 'postponed', 'Postponed'
    CANCELLED = 'cancelled', 'Cancelled'
    SUSPENDED = 'suspended', 'Suspended'


class BetType(models.TextChoices):
    """Types of bets available"""
    MONEYLINE = 'moneyline', 'Moneyline'
    SPREAD = 'spread', 'Point Spread'
    TOTAL = 'total', 'Over/Under Total'
    PROP = 'prop', 'Player/Team Prop'
    FUTURES = 'futures', 'Futures'
    PARLAY = 'parlay', 'Parlay'
    TEASER = 'teaser', 'Teaser'
    LIVE = 'live', 'Live Bet'


class MarketStatus(models.TextChoices):
    """Market availability status"""
    OPEN = 'open', 'Open for Betting'
    CLOSED = 'closed', 'Closed'
    SUSPENDED = 'suspended', 'Suspended'
    RESULTED = 'resulted', 'Resulted'
    VOIDED = 'voided', 'Voided'


class BetStatus(models.TextChoices):
    """Individual bet status"""
    PENDING = 'pending', 'Pending'
    WON = 'won', 'Won'
    LOST = 'lost', 'Lost'
    PUSH = 'push', 'Push'
    VOIDED = 'voided', 'Voided'
    PARTIAL = 'partial', 'Partial Win/Loss'


class RiskLevel(models.TextChoices):
    """Risk assessment levels"""
    VERY_LOW = 'very_low', 'Very Low Risk'
    LOW = 'low', 'Low Risk'
    MODERATE = 'moderate', 'Moderate Risk'
    HIGH = 'high', 'High Risk'
    VERY_HIGH = 'very_high', 'Very High Risk'
    EXTREME = 'extreme', 'Extreme Risk'


class League(UnifiedBaseModel):
    """Sports leagues and conferences"""
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="League/conference name"
    )
    
    abbreviation = models.CharField(
        max_length=10,
        unique=True,
        help_text="League abbreviation (e.g., NFL, NBA)"
    )
    
    sport_type = models.CharField(
        max_length=20,
        choices=SportType.choices,
        help_text="Type of sport"
    )
    
    country = models.CharField(
        max_length=100,
        default='USA',
        help_text="Primary country"
    )
    
    # Season information
    current_season = models.CharField(
        max_length=20,
        help_text="Current season (e.g., '2023-2024')"
    )
    
    season_start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Season start date"
    )
    
    season_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Season end date"
    )
    
    # API and data configuration
    api_provider = models.CharField(
        max_length=100,
        blank=True,
        help_text="Primary data provider"
    )
    
    api_config = models.JSONField(
        default=dict,
        help_text="API configuration and endpoints"
    )
    
    # League-specific betting rules
    betting_rules = models.JSONField(
        default=dict,
        help_text="League-specific betting rules and limits"
    )
    
    class Meta:
        verbose_name = "League"
        verbose_name_plural = "Leagues"
        ordering = ['sport_type', 'name']
        indexes = [
            models.Index(fields=['sport_type']),
            models.Index(fields=['abbreviation']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.abbreviation})"


class Team(UnifiedBaseModel):
    """Teams participating in leagues"""
    
    name = models.CharField(
        max_length=200,
        help_text="Team name"
    )
    
    abbreviation = models.CharField(
        max_length=10,
        help_text="Team abbreviation"
    )
    
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name='teams'
    )
    
    city = models.CharField(
        max_length=100,
        help_text="Team city"
    )
    
    conference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Conference/division"
    )
    
    division = models.CharField(
        max_length=100,
        blank=True,
        help_text="Division within conference"
    )
    
    # Team identification
    external_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="External API identifier"
    )
    
    logo_url = models.URLField(
        blank=True,
        help_text="Team logo URL"
    )
    
    # Team performance metrics
    current_record = models.JSONField(
        default=dict,
        help_text="Current season record (wins, losses, etc.)"
    )
    
    season_stats = models.JSONField(
        default=dict,
        help_text="Season statistics"
    )
    
    # Betting performance
    ats_record = models.JSONField(
        default=dict,
        help_text="Against The Spread record"
    )
    
    ou_record = models.JSONField(
        default=dict,
        help_text="Over/Under record"
    )
    
    class Meta:
        verbose_name = "Team"
        verbose_name_plural = "Teams"
        ordering = ['league', 'name']
        unique_together = [['league', 'abbreviation']]
        indexes = [
            models.Index(fields=['league']),
            models.Index(fields=['external_id']),
        ]
    
    def __str__(self):
        return f"{self.city} {self.name}"


class Game(UnifiedBaseModel):
    """Individual games/matches"""
    
    # Game identification
    external_id = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        help_text="External API identifier"
    )
    
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name='games'
    )
    
    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='home_games'
    )
    
    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='away_games'
    )
    
    # Game scheduling
    scheduled_start = models.DateTimeField(
        help_text="Scheduled game start time"
    )
    
    actual_start = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual game start time"
    )
    
    status = models.CharField(
        max_length=20,
        choices=GameStatus.choices,
        default=GameStatus.SCHEDULED
    )
    
    # Venue information
    venue_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Venue name"
    )
    
    venue_city = models.CharField(
        max_length=100,
        blank=True,
        help_text="Venue city"
    )
    
    # Game context
    season = models.CharField(
        max_length=20,
        help_text="Season identifier"
    )
    
    week = models.IntegerField(
        null=True,
        blank=True,
        help_text="Week number (for sports with weeks)"
    )
    
    is_playoff = models.BooleanField(
        default=False,
        help_text="Whether this is a playoff game"
    )
    
    # Weather (for outdoor sports)
    weather_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Weather conditions (temperature, wind, etc.)"
    )
    
    # Game results
    home_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Home team final score"
    )
    
    away_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Away team final score"
    )
    
    # Live game data
    current_period = models.CharField(
        max_length=20,
        blank=True,
        help_text="Current period/quarter"
    )
    
    time_remaining = models.CharField(
        max_length=20,
        blank=True,
        help_text="Time remaining in current period"
    )
    
    live_stats = models.JSONField(
        default=dict,
        help_text="Live game statistics"
    )
    
    # Betting context
    total_handle = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total betting handle for this game"
    )
    
    sharp_action = models.JSONField(
        default=dict,
        help_text="Sharp betting action indicators"
    )
    
    public_betting = models.JSONField(
        default=dict,
        help_text="Public betting percentages"
    )
    
    class Meta:
        verbose_name = "Game"
        verbose_name_plural = "Games"
        ordering = ['-scheduled_start']
        indexes = [
            models.Index(fields=['league', '-scheduled_start']),
            models.Index(fields=['status']),
            models.Index(fields=['external_id']),
            models.Index(fields=['scheduled_start']),
        ]
    
    def __str__(self):
        return f"{self.away_team.abbreviation} @ {self.home_team.abbreviation} ({self.scheduled_start.strftime('%Y-%m-%d')})"
    
    @property
    def is_live(self):
        """Check if game is currently live"""
        return self.status in [GameStatus.LIVE, GameStatus.HALFTIME]
    
    @property
    def is_finished(self):
        """Check if game is finished"""
        return self.status == GameStatus.FINAL
    
    def get_winning_team(self):
        """Get the winning team if game is final"""
        if not self.is_finished or self.home_score is None or self.away_score is None:
            return None
        
        if self.home_score > self.away_score:
            return self.home_team
        elif self.away_score > self.home_score:
            return self.away_team
        else:
            return None  # Tie


class Sportsbook(UnifiedBaseModel):
    """Sportsbooks providing odds and lines"""
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Sportsbook name"
    )
    
    abbreviation = models.CharField(
        max_length=20,
        unique=True,
        help_text="Short abbreviation"
    )
    
    # API configuration
    api_endpoint = models.URLField(
        blank=True,
        help_text="API endpoint for odds data"
    )
    
    api_key_config = models.JSONField(
        default=dict,
        help_text="API authentication configuration"
    )
    
    # Sportsbook characteristics
    is_sharp = models.BooleanField(
        default=False,
        help_text="Whether this is considered a sharp book"
    )
    
    betting_limits = models.JSONField(
        default=dict,
        help_text="Betting limits by market type"
    )
    
    supported_markets = models.JSONField(
        default=list,
        help_text="List of supported market types"
    )
    
    # Data quality metrics
    line_speed = models.FloatField(
        default=0.0,
        help_text="How quickly lines move (seconds)"
    )
    
    accuracy_score = models.FloatField(
        default=0.0,
        help_text="Historical accuracy of closing lines"
    )
    
    # Regional information
    legal_states = models.JSONField(
        default=list,
        help_text="States/regions where this book is legal"
    )
    
    class Meta:
        verbose_name = "Sportsbook"
        verbose_name_plural = "Sportsbooks"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class BettingMarket(UnifiedBaseModel):
    """Betting markets for games"""
    
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='markets'
    )
    
    market_type = models.CharField(
        max_length=20,
        choices=BetType.choices,
        help_text="Type of betting market"
    )
    
    market_name = models.CharField(
        max_length=200,
        help_text="Descriptive market name"
    )
    
    status = models.CharField(
        max_length=20,
        choices=MarketStatus.choices,
        default=MarketStatus.OPEN
    )
    
    # Market parameters
    market_params = models.JSONField(
        default=dict,
        help_text="Market-specific parameters (spread value, total, etc.)"
    )
    
    # Settlement
    settlement_value = models.JSONField(
        null=True,
        blank=True,
        help_text="Settlement value when market is resulted"
    )
    
    settled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When market was settled"
    )
    
    # Market analytics
    total_volume = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total betting volume"
    )
    
    sharp_percentage = models.FloatField(
        default=0.0,
        help_text="Percentage of sharp money"
    )
    
    public_percentage = models.FloatField(
        default=0.0,
        help_text="Percentage of public money"
    )
    
    class Meta:
        verbose_name = "Betting Market"
        verbose_name_plural = "Betting Markets"
        ordering = ['game', 'market_type']
        indexes = [
            models.Index(fields=['game', 'market_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.game} - {self.market_name}"


class OddsLine(UnifiedBaseModel):
    """Individual odds lines from sportsbooks"""
    
    market = models.ForeignKey(
        BettingMarket,
        on_delete=models.CASCADE,
        related_name='odds_lines'
    )
    
    sportsbook = models.ForeignKey(
        Sportsbook,
        on_delete=models.CASCADE,
        related_name='odds_lines'
    )
    
    # Odds values (American format)
    home_odds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Home team odds (American format)"
    )
    
    away_odds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Away team odds (American format)"
    )
    
    # For spread/total bets
    home_spread = models.FloatField(
        null=True,
        blank=True,
        help_text="Home team spread"
    )
    
    away_spread = models.FloatField(
        null=True,
        blank=True,
        help_text="Away team spread"
    )
    
    total_line = models.FloatField(
        null=True,
        blank=True,
        help_text="Over/Under total"
    )
    
    over_odds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Over odds"
    )
    
    under_odds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Under odds"
    )
    
    # Line metadata
    line_sequence = models.PositiveIntegerField(
        default=1,
        help_text="Sequence number for this line"
    )
    
    is_current = models.BooleanField(
        default=True,
        help_text="Whether this is the current line"
    )
    
    # Timing
    opened_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this line was first posted"
    )
    
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this line was taken down"
    )
    
    # Additional odds formats
    decimal_odds = models.JSONField(
        default=dict,
        help_text="Decimal format odds"
    )
    
    implied_probabilities = models.JSONField(
        default=dict,
        help_text="Calculated implied probabilities"
    )
    
    # Line movement context
    movement_reason = models.CharField(
        max_length=200,
        blank=True,
        help_text="Reason for line movement"
    )
    
    sharp_move = models.BooleanField(
        default=False,
        help_text="Whether this movement was due to sharp action"
    )
    
    class Meta:
        verbose_name = "Odds Line"
        verbose_name_plural = "Odds Lines"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['market', 'sportsbook']),
            models.Index(fields=['is_current']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.market} - {self.sportsbook.abbreviation} (Line #{self.line_sequence})"
    
    def save(self, *args, **kwargs):
        """Calculate implied probabilities on save"""
        # Only calculate if not already being updated
        update_fields = kwargs.get('update_fields', None)
        skip_calc = update_fields and 'implied_probabilities' in update_fields
        
        if not skip_calc:
            self._calculate_fields()
        
        super().save(*args, **kwargs)
    
    def _calculate_fields(self):
        """Calculate implied probabilities from American odds (internal use)"""
        probabilities = {}
        
        # Calculate for moneyline odds
        if self.home_odds is not None:
            probabilities['home'] = self._american_to_probability(self.home_odds)
        if self.away_odds is not None:
            probabilities['away'] = self._american_to_probability(self.away_odds)
        
        # Calculate for over/under
        if self.over_odds is not None:
            probabilities['over'] = self._american_to_probability(self.over_odds)
        if self.under_odds is not None:
            probabilities['under'] = self._american_to_probability(self.under_odds)
        
        # Calculate decimal odds
        decimal = {}
        if self.home_odds is not None:
            decimal['home'] = self._american_to_decimal(self.home_odds)
        if self.away_odds is not None:
            decimal['away'] = self._american_to_decimal(self.away_odds)
        if self.over_odds is not None:
            decimal['over'] = self._american_to_decimal(self.over_odds)
        if self.under_odds is not None:
            decimal['under'] = self._american_to_decimal(self.under_odds)
        
        self.implied_probabilities = probabilities
        self.decimal_odds = decimal
    
    def calculate_implied_probabilities(self):
        """Calculate implied probabilities from American odds (public API)"""
        self._calculate_fields()
        self.save(update_fields=['implied_probabilities', 'decimal_odds'])
    
    @staticmethod
    def _american_to_probability(american_odds):
        """Convert American odds to implied probability"""
        if american_odds > 0:
            return 100 / (american_odds + 100)
        else:
            return abs(american_odds) / (abs(american_odds) + 100)
    
    @staticmethod
    def _american_to_decimal(american_odds):
        """Convert American odds to decimal odds"""
        if american_odds > 0:
            return (american_odds / 100) + 1
        else:
            return (100 / abs(american_odds)) + 1
    
    def get_vig(self, other_line=None):
        """Calculate the vigorish/juice for this line"""
        if not other_line and self.market.market_type == BetType.MONEYLINE:
            # For moneyline, find the opposing line
            opposing_lines = self.market.odds_lines.filter(
                sportsbook=self.sportsbook,
                is_current=True
            ).exclude(id=self.id)
            
            if opposing_lines.exists():
                other_line = opposing_lines.first()
        
        if other_line:
            prob_1 = self.implied_probabilities.get('home', 0) or self.implied_probabilities.get('over', 0)
            prob_2 = other_line.implied_probabilities.get('away', 0) or other_line.implied_probabilities.get('under', 0)
            
            if prob_1 and prob_2:
                return (prob_1 + prob_2 - 1) * 100
        
        return 0.0


class LineMovement(UnifiedBaseModel):
    """Track line movements for analytics"""
    
    market = models.ForeignKey(
        BettingMarket,
        on_delete=models.CASCADE,
        related_name='line_movements'
    )
    
    sportsbook = models.ForeignKey(
        Sportsbook,
        on_delete=models.CASCADE,
        related_name='line_movements'
    )
    
    # Movement details
    old_line = models.ForeignKey(
        OddsLine,
        on_delete=models.CASCADE,
        related_name='movements_from'
    )
    
    new_line = models.ForeignKey(
        OddsLine,
        on_delete=models.CASCADE,
        related_name='movements_to'
    )
    
    # Movement analysis
    movement_size = models.FloatField(
        help_text="Size of the movement (in odds or spread points)"
    )
    
    movement_direction = models.CharField(
        max_length=10,
        choices=[
            ('up', 'Line Moved Up'),
            ('down', 'Line Moved Down'),
        ]
    )
    
    is_significant = models.BooleanField(
        default=False,
        help_text="Whether this is a significant movement"
    )
    
    # Context
    trigger_event = models.CharField(
        max_length=200,
        blank=True,
        help_text="Event that triggered the movement"
    )
    
    betting_volume_factor = models.FloatField(
        default=0.0,
        help_text="How much betting volume influenced this move"
    )
    
    news_factor = models.FloatField(
        default=0.0,
        help_text="How much news/information influenced this move"
    )
    
    class Meta:
        verbose_name = "Line Movement"
        verbose_name_plural = "Line Movements"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['market', '-created_at']),
            models.Index(fields=['is_significant']),
        ]
    
    def __str__(self):
        return f"{self.market} - {self.sportsbook.abbreviation} moved {self.movement_direction} by {self.movement_size}"


class Bet(UnifiedBaseModel):
    """Individual bets placed by users"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bets'
    )
    
    market = models.ForeignKey(
        BettingMarket,
        on_delete=models.CASCADE,
        related_name='bets'
    )
    
    sportsbook = models.ForeignKey(
        Sportsbook,
        on_delete=models.CASCADE,
        related_name='bets'
    )
    
    odds_line = models.ForeignKey(
        OddsLine,
        on_delete=models.CASCADE,
        related_name='bets',
        help_text="The specific odds line when bet was placed"
    )
    
    # Bet details
    bet_type = models.CharField(
        max_length=20,
        choices=BetType.choices
    )
    
    selection = models.CharField(
        max_length=200,
        help_text="What was bet on (team, over, under, etc.)"
    )
    
    odds_taken = models.IntegerField(
        help_text="Odds when bet was placed (American format)"
    )
    
    stake = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Amount wagered"
    )
    
    potential_payout = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Potential payout including stake"
    )
    
    potential_profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Potential profit (payout - stake)"
    )
    
    # Status and result
    status = models.CharField(
        max_length=20,
        choices=BetStatus.choices,
        default=BetStatus.PENDING
    )
    
    result_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Actual result amount (profit/loss)"
    )
    
    settled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When bet was settled"
    )
    
    # Kelly Criterion and risk management
    kelly_percentage = models.FloatField(
        null=True,
        blank=True,
        help_text="Kelly Criterion recommended bet size percentage"
    )
    
    edge_percentage = models.FloatField(
        null=True,
        blank=True,
        help_text="Calculated edge percentage"
    )
    
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.MODERATE
    )
    
    # Analytics
    expected_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0000'),
        help_text="Expected value of this bet"
    )
    
    confidence_level = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Confidence in this bet (0-1)"
    )
    
    # Bet context
    bet_reason = models.TextField(
        blank=True,
        help_text="Reason for placing this bet"
    )
    
    agent_recommendation = models.JSONField(
        default=dict,
        help_text="Agent recommendation that led to this bet"
    )
    
    class Meta:
        verbose_name = "Bet"
        verbose_name_plural = "Bets"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['market']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.selection} ${self.stake} @ {self.odds_taken}"
    
    def save(self, *args, **kwargs):
        """Calculate potential payouts on save"""
        if self.odds_taken and self.stake:
            self.potential_payout = self._calculate_payout(self.odds_taken, self.stake)
            self.potential_profit = self.potential_payout - self.stake
        
        super().save(*args, **kwargs)
    
    @staticmethod
    def _calculate_payout(american_odds, stake):
        """Calculate payout from American odds and stake"""
        if american_odds > 0:
            return stake * (american_odds / 100) + stake
        else:
            return stake * (100 / abs(american_odds)) + stake
    
    def settle_bet(self, won=True, amount=None):
        """Settle the bet"""
        if amount is None:
            if won:
                amount = self.potential_profit
            else:
                amount = -self.stake
        
        self.result_amount = amount
        self.settled_at = timezone.now()
        
        if won:
            if amount == self.potential_profit:
                self.status = BetStatus.WON
            else:
                self.status = BetStatus.PARTIAL
        elif amount == 0:
            self.status = BetStatus.PUSH
        else:
            self.status = BetStatus.LOST
        
        self.save()


class BankrollManagement(UnifiedBaseModel):
    """User bankroll management and Kelly Criterion calculations"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='bankroll'
    )
    
    # Current bankroll
    current_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('1000.00'),
        help_text="Current bankroll balance"
    )
    
    initial_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Starting bankroll amount"
    )
    
    # Risk management
    max_bet_percentage = models.FloatField(
        default=0.05,
        validators=[MinValueValidator(0.001), MaxValueValidator(0.25)],
        help_text="Maximum bet size as percentage of bankroll"
    )
    
    kelly_multiplier = models.FloatField(
        default=0.25,
        validators=[MinValueValidator(0.1), MaxValueValidator(2.0)],
        help_text="Kelly Criterion multiplier (fractional Kelly)"
    )
    
    risk_tolerance = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.MODERATE
    )
    
    # Performance tracking
    total_wagered = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total amount wagered"
    )
    
    total_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total profit/loss"
    )
    
    win_rate = models.FloatField(
        default=0.0,
        help_text="Overall win rate percentage"
    )
    
    roi_percentage = models.FloatField(
        default=0.0,
        help_text="Return on investment percentage"
    )
    
    # Streaks and volatility
    current_streak = models.IntegerField(
        default=0,
        help_text="Current winning/losing streak (positive = wins)"
    )
    
    longest_winning_streak = models.IntegerField(
        default=0
    )
    
    longest_losing_streak = models.IntegerField(
        default=0
    )
    
    volatility_score = models.FloatField(
        default=0.0,
        help_text="Bankroll volatility measure"
    )
    
    # Daily/Monthly limits
    daily_loss_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum daily loss limit"
    )
    
    monthly_loss_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum monthly loss limit"
    )
    
    class Meta:
        verbose_name = "Bankroll Management"
        verbose_name_plural = "Bankroll Management"
    
    def __str__(self):
        return f"{self.user.username} - ${self.current_balance}"
    
    def calculate_kelly_bet_size(self, edge_percentage, odds, confidence=1.0):
        """
        Calculate optimal bet size using Kelly Criterion
        
        Args:
            edge_percentage: Expected edge (as decimal, e.g., 0.05 for 5%)
            odds: American odds
            confidence: Confidence multiplier (0-1)
        
        Returns:
            Recommended bet amount
        """
        # Convert American odds to decimal probability
        if odds > 0:
            win_probability = 100 / (odds + 100)
            payout_ratio = odds / 100
        else:
            win_probability = abs(odds) / (abs(odds) + 100)
            payout_ratio = 100 / abs(odds)
        
        # Adjust win probability by edge
        true_probability = win_probability + edge_percentage
        
        # Kelly formula: f = (bp - q) / b
        # where b = payout ratio, p = win probability, q = lose probability
        lose_probability = 1 - true_probability
        
        if payout_ratio > 0:
            kelly_fraction = (payout_ratio * true_probability - lose_probability) / payout_ratio
        else:
            kelly_fraction = 0
        
        # Apply multiplier and confidence
        kelly_fraction *= self.kelly_multiplier * confidence
        
        # Cap at maximum bet percentage
        kelly_fraction = min(kelly_fraction, self.max_bet_percentage)
        
        # Ensure positive and reasonable
        kelly_fraction = max(0, kelly_fraction)
        
        # Calculate bet amount
        bet_amount = self.current_balance * Decimal(str(kelly_fraction))
        
        return {
            'recommended_amount': bet_amount,
            'kelly_percentage': kelly_fraction * 100,
            'risk_level': self._assess_risk_level(kelly_fraction),
            'edge_used': edge_percentage * 100,
            'confidence_factor': confidence
        }
    
    def _assess_risk_level(self, kelly_fraction):
        """Assess risk level based on Kelly fraction"""
        if kelly_fraction <= 0.01:
            return RiskLevel.VERY_LOW
        elif kelly_fraction <= 0.03:
            return RiskLevel.LOW
        elif kelly_fraction <= 0.06:
            return RiskLevel.MODERATE
        elif kelly_fraction <= 0.10:
            return RiskLevel.HIGH
        elif kelly_fraction <= 0.15:
            return RiskLevel.VERY_HIGH
        else:
            return RiskLevel.EXTREME
    
    def update_performance(self):
        """Update performance metrics based on bet history"""
        bets = self.user.bets.filter(status__in=[BetStatus.WON, BetStatus.LOST, BetStatus.PUSH])
        
        if not bets.exists():
            return
        
        # Basic metrics
        total_bets = bets.count()
        won_bets = bets.filter(status=BetStatus.WON).count()
        self.win_rate = (won_bets / total_bets) * 100 if total_bets > 0 else 0
        
        # Financial metrics
        self.total_wagered = bets.aggregate(Sum('stake'))['stake__sum'] or Decimal('0.00')
        self.total_profit = bets.aggregate(Sum('result_amount'))['result_amount__sum'] or Decimal('0.00')
        self.current_balance = self.initial_balance + self.total_profit
        
        if self.total_wagered > 0:
            self.roi_percentage = float(self.total_profit / self.total_wagered) * 100
        
        # Update streaks
        self._update_streaks()
        
        # Calculate volatility
        self._calculate_volatility()
        
        self.save()
    
    def _update_streaks(self):
        """Update winning/losing streaks"""
        recent_bets = self.user.bets.filter(
            status__in=[BetStatus.WON, BetStatus.LOST]
        ).order_by('-settled_at')[:50]  # Look at last 50 bets
        
        current_streak = 0
        longest_win = 0
        longest_lose = 0
        temp_win = 0
        temp_lose = 0
        
        for bet in recent_bets:
            if bet.status == BetStatus.WON:
                if current_streak >= 0:
                    current_streak += 1
                    temp_win += 1
                    temp_lose = 0
                else:
                    current_streak = 1
                    temp_win = 1
                    temp_lose = 0
                
                longest_win = max(longest_win, temp_win)
            
            elif bet.status == BetStatus.LOST:
                if current_streak <= 0:
                    current_streak -= 1
                    temp_lose += 1
                    temp_win = 0
                else:
                    current_streak = -1
                    temp_lose = 1
                    temp_win = 0
                
                longest_lose = max(longest_lose, temp_lose)
        
        self.current_streak = current_streak
        self.longest_winning_streak = longest_win
        self.longest_losing_streak = longest_lose
    
    def _calculate_volatility(self):
        """Calculate bankroll volatility"""
        # Simple volatility based on bet size variance
        bets = self.user.bets.all()
        if bets.count() < 5:
            self.volatility_score = 0.0
            return
        
        stake_amounts = [float(bet.stake) for bet in bets]
        avg_stake = sum(stake_amounts) / len(stake_amounts)
        variance = sum((x - avg_stake) ** 2 for x in stake_amounts) / len(stake_amounts)
        self.volatility_score = math.sqrt(variance) / avg_stake if avg_stake > 0 else 0.0


class ArbitrageOpportunity(UnifiedBaseModel):
    """Detected arbitrage opportunities"""
    
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='arbitrage_opportunities'
    )
    
    market_type = models.CharField(
        max_length=20,
        choices=BetType.choices
    )
    
    # Arbitrage details
    sportsbook_1 = models.ForeignKey(
        Sportsbook,
        on_delete=models.CASCADE,
        related_name='arb_opportunities_1'
    )
    
    sportsbook_2 = models.ForeignKey(
        Sportsbook,
        on_delete=models.CASCADE,
        related_name='arb_opportunities_2'
    )
    
    odds_1 = models.IntegerField(
        help_text="Odds at sportsbook 1"
    )
    
    odds_2 = models.IntegerField(
        help_text="Odds at sportsbook 2"
    )
    
    selection_1 = models.CharField(
        max_length=200,
        help_text="What to bet on at sportsbook 1"
    )
    
    selection_2 = models.CharField(
        max_length=200,
        help_text="What to bet on at sportsbook 2"
    )
    
    # Profit calculations
    arbitrage_percentage = models.FloatField(
        help_text="Arbitrage profit percentage"
    )
    
    stake_1_percentage = models.FloatField(
        help_text="Percentage of total stake for bet 1"
    )
    
    stake_2_percentage = models.FloatField(
        help_text="Percentage of total stake for bet 2"
    )
    
    minimum_profit = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Minimum guaranteed profit percentage"
    )
    
    # Opportunity lifecycle
    discovered_at = models.DateTimeField(
        auto_now_add=True
    )
    
    expires_at = models.DateTimeField(
        help_text="When this opportunity expires"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether opportunity is still available"
    )
    
    closed_reason = models.CharField(
        max_length=200,
        blank=True,
        help_text="Why opportunity was closed"
    )
    
    # Risk factors
    risk_factors = models.JSONField(
        default=list,
        help_text="Identified risk factors"
    )
    
    confidence_score = models.FloatField(
        default=0.0,
        help_text="Confidence in this arbitrage opportunity"
    )
    
    class Meta:
        verbose_name = "Arbitrage Opportunity"
        verbose_name_plural = "Arbitrage Opportunities"
        ordering = ['-arbitrage_percentage', '-discovered_at']
        indexes = [
            models.Index(fields=['is_active', '-arbitrage_percentage']),
            models.Index(fields=['game']),
        ]
    
    def __str__(self):
        return f"{self.game} - {self.arbitrage_percentage:.2f}% profit"
    
    @classmethod
    def detect_opportunities(cls, market_type=None, min_profit=0.01):
        """
        Detect arbitrage opportunities across sportsbooks
        
        Args:
            market_type: Filter by specific market type
            min_profit: Minimum profit percentage (e.g., 0.01 for 1%)
        
        Returns:
            List of detected opportunities
        """
        
        # Get all current odds for games
        current_time = timezone.now()
        future_games = Game.objects.filter(
            scheduled_start__gt=current_time,
            status=GameStatus.SCHEDULED
        )
        
        opportunities = []
        
        for game in future_games:
            markets = game.markets.filter(status=MarketStatus.OPEN)
            
            if market_type:
                markets = markets.filter(market_type=market_type)
            
            for market in markets:
                opportunities.extend(
                    cls._check_market_for_arbitrage(market, min_profit)
                )
        
        return opportunities
    
    @classmethod
    def _check_market_for_arbitrage(cls, market, min_profit):
        """Check a specific market for arbitrage opportunities"""
        opportunities = []
        current_lines = market.odds_lines.filter(is_current=True)
        
        if market.market_type == BetType.MONEYLINE:
            # Check moneyline arbitrage
            home_lines = current_lines.filter(home_odds__isnull=False)
            away_lines = current_lines.filter(away_odds__isnull=False)
            
            for home_line in home_lines:
                for away_line in away_lines:
                    if home_line.sportsbook != away_line.sportsbook:
                        arb_data = cls._calculate_arbitrage(
                            home_line.home_odds,
                            away_line.away_odds,
                            min_profit
                        )
                        
                        if arb_data['is_arbitrage']:
                            opportunities.append({
                                'game': market.game,
                                'market_type': market.market_type,
                                'sportsbook_1': home_line.sportsbook,
                                'sportsbook_2': away_line.sportsbook,
                                'odds_1': home_line.home_odds,
                                'odds_2': away_line.away_odds,
                                'selection_1': f"{market.game.home_team.abbreviation} ML",
                                'selection_2': f"{market.game.away_team.abbreviation} ML",
                                **arb_data
                            })
        
        return opportunities
    
    @staticmethod
    def _calculate_arbitrage(odds_1, odds_2, min_profit=0.01):
        """Calculate arbitrage details for two odds"""
        # Convert to decimal odds
        decimal_1 = OddsLine._american_to_decimal(odds_1)
        decimal_2 = OddsLine._american_to_decimal(odds_2)
        
        # Calculate implied probabilities
        prob_1 = 1 / decimal_1
        prob_2 = 1 / decimal_2
        
        # Check if arbitrage exists
        total_probability = prob_1 + prob_2
        
        if total_probability < 1.0:
            # Arbitrage exists
            arbitrage_percentage = (1 - total_probability) * 100
            
            if arbitrage_percentage >= min_profit * 100:
                # Calculate stake percentages
                stake_1_pct = prob_1 / total_probability * 100
                stake_2_pct = prob_2 / total_probability * 100
                
                return {
                    'is_arbitrage': True,
                    'arbitrage_percentage': arbitrage_percentage,
                    'stake_1_percentage': stake_1_pct,
                    'stake_2_percentage': stake_2_pct,
                    'minimum_profit': Decimal(str(arbitrage_percentage))
                }
        
        return {
            'is_arbitrage': False,
            'arbitrage_percentage': 0.0,
            'stake_1_percentage': 0.0,
            'stake_2_percentage': 0.0,
            'minimum_profit': Decimal('0.0000')
        }


class BettingRecommendation(UnifiedBaseModel):
    """AI-powered betting recommendations"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='betting_recommendations'
    )
    
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    
    market = models.ForeignKey(
        BettingMarket,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    
    # Recommendation details
    recommended_selection = models.CharField(
        max_length=200,
        help_text="Recommended bet selection"
    )
    
    recommended_sportsbook = models.ForeignKey(
        Sportsbook,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    
    recommended_odds = models.IntegerField(
        help_text="Recommended odds to take"
    )
    
    recommended_stake = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Recommended stake amount"
    )
    
    # Analysis
    expected_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Expected value of recommendation"
    )
    
    win_probability = models.FloatField(
        help_text="Estimated win probability"
    )
    
    confidence_level = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="AI confidence in recommendation"
    )
    
    edge_percentage = models.FloatField(
        help_text="Calculated edge percentage"
    )
    
    # Risk assessment
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices
    )
    
    kelly_percentage = models.FloatField(
        help_text="Kelly Criterion recommended size"
    )
    
    # AI analysis
    generating_agent = models.CharField(
        max_length=200,
        help_text="Agent that generated this recommendation"
    )
    
    analysis_factors = models.JSONField(
        default=dict,
        help_text="Factors considered in analysis"
    )
    
    reasoning = models.TextField(
        help_text="Detailed reasoning for recommendation"
    )
    
    # Model predictions
    model_predictions = models.JSONField(
        default=dict,
        help_text="Raw model predictions and probabilities"
    )
    
    historical_performance = models.JSONField(
        default=dict,
        help_text="Historical performance of similar recommendations"
    )
    
    # Recommendation lifecycle
    expires_at = models.DateTimeField(
        help_text="When recommendation expires"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether recommendation is still active"
    )
    
    user_action = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('modified', 'Modified'),
            ('expired', 'Expired'),
        ],
        default='pending'
    )
    
    # Tracking
    bet_placed = models.ForeignKey(
        Bet,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='recommendation'
    )
    
    actual_result = models.CharField(
        max_length=20,
        blank=True,
        help_text="Actual outcome for performance tracking"
    )
    
    class Meta:
        verbose_name = "Betting Recommendation"
        verbose_name_plural = "Betting Recommendations"
        ordering = ['-confidence_level', '-expected_value', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['game', '-confidence_level']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.recommended_selection} (EV: {self.expected_value})"


class SportsAnalytics(UnifiedBaseModel):
    """Sports analytics and performance metrics"""
    
    # Analytics scope
    scope_type = models.CharField(
        max_length=20,
        choices=[
            ('game', 'Individual Game'),
            ('team', 'Team Analysis'),
            ('league', 'League Analysis'),
            ('player', 'Player Analysis'),
            ('market', 'Market Analysis'),
            ('user', 'User Performance'),
        ]
    )
    
    scope_id = models.CharField(
        max_length=100,
        help_text="ID of the entity being analyzed"
    )
    
    # Time period
    analysis_period = models.CharField(
        max_length=20,
        choices=[
            ('game', 'Single Game'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('season', 'Season'),
            ('historical', 'Historical'),
        ]
    )
    
    period_start = models.DateTimeField(
        help_text="Start of analysis period"
    )
    
    period_end = models.DateTimeField(
        help_text="End of analysis period"
    )
    
    # Analytics data
    metrics = models.JSONField(
        default=dict,
        help_text="Calculated metrics and KPIs"
    )
    
    trends = models.JSONField(
        default=dict,
        help_text="Trend analysis data"
    )
    
    predictions = models.JSONField(
        default=dict,
        help_text="Predictive analytics results"
    )
    
    comparative_analysis = models.JSONField(
        default=dict,
        help_text="Comparisons with benchmarks"
    )
    
    # Generation details
    generated_by = models.CharField(
        max_length=200,
        help_text="Agent or system that generated analytics"
    )
    
    computation_time_seconds = models.FloatField(
        default=0.0,
        help_text="Time taken to compute analytics"
    )
    
    data_quality_score = models.FloatField(
        default=1.0,
        help_text="Quality score of underlying data"
    )
    
    class Meta:
        verbose_name = "Sports Analytics"
        verbose_name_plural = "Sports Analytics"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['scope_type', 'scope_id']),
            models.Index(fields=['analysis_period', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.scope_type.title()} Analytics - {self.analysis_period}"


class MLPrediction(UnifiedBaseModel):
    """
    ML-generated predictions for games
    Tracks predictions from the multi-sport ML Engine for accuracy analysis
    """

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='ml_predictions',
        help_text="Game being predicted"
    )

    # Agent who made this prediction (for agent learning)
    agent = models.ForeignKey(
        'agents.UnifiedAgentTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='predictions',
        help_text="Agent who made this prediction"
    )

    predicted_winner = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='predicted_wins',
        help_text="Team predicted to win"
    )

    # Prediction confidence and probabilities
    confidence = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Prediction confidence (0-100%)"
    )

    home_win_probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Home team win probability (0-100%)"
    )

    away_win_probability = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Away team win probability (0-100%)"
    )

    # Model information
    model_used = models.CharField(
        max_length=100,
        help_text="ML model identifier (e.g., 'nfl_predictor', 'mlb_predictor')"
    )

    sport_type = models.CharField(
        max_length=20,
        choices=SportType.choices,
        help_text="Sport type for this prediction"
    )

    # Spread and score predictions
    predicted_spread = models.FloatField(
        null=True,
        blank=True,
        help_text="Predicted point spread"
    )

    predicted_home_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Predicted home team score"
    )

    predicted_away_score = models.IntegerField(
        null=True,
        blank=True,
        help_text="Predicted away team score"
    )

    # AI reasoning and key factors
    key_factors = models.JSONField(
        default=list,
        help_text="Key factors influencing the prediction"
    )

    ai_reasoning = models.TextField(
        blank=True,
        help_text="Human-readable AI reasoning"
    )

    # Odds snapshot at prediction time (for ROI/CLV calculation)
    odds_at_prediction = models.IntegerField(
        null=True,
        blank=True,
        help_text="American odds on predicted winner at time of prediction (e.g. -110, +150)"
    )

    closing_odds = models.IntegerField(
        null=True,
        blank=True,
        help_text="Closing odds on predicted winner (captured when game goes FINAL)"
    )

    bookmaker_count = models.IntegerField(
        default=0,
        help_text="Number of bookmakers in consensus at prediction time"
    )

    # Evaluation and accuracy
    was_correct = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether prediction was correct (set after game completes)"
    )

    evaluated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When prediction was evaluated"
    )

    # User interaction
    shown_to_users = models.IntegerField(
        default=0,
        help_text="Number of times shown to users"
    )

    user_acted_on = models.IntegerField(
        default=0,
        help_text="Number of users who acted on this prediction"
    )

    class Meta:
        verbose_name = "ML Prediction"
        verbose_name_plural = "ML Predictions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['game', '-created_at']),
            models.Index(fields=['sport_type', '-created_at']),
            models.Index(fields=['model_used', '-created_at']),
            models.Index(fields=['was_correct']),
            models.Index(fields=['created_at']),
        ]
        unique_together = [('game', 'model_used', 'created_at')]

    def __str__(self):
        game_str = f"{self.game.away_team.abbreviation} @ {self.game.home_team.abbreviation}"
        return f"{game_str}: {self.predicted_winner.abbreviation} ({self.confidence}%)"

    def evaluate(self):
        """
        Evaluate prediction accuracy after game completes
        Returns True if correct, False if incorrect, None if game not finished
        """
        if self.game.status != GameStatus.FINAL:
            return None

        if self.game.home_score is None or self.game.away_score is None:
            return None

        # Determine actual winner
        if self.game.home_score > self.game.away_score:
            actual_winner = self.game.home_team
        elif self.game.away_score > self.game.home_score:
            actual_winner = self.game.away_team
        else:
            # Tie - prediction is incorrect if we picked a winner
            self.was_correct = False
            self.evaluated_at = timezone.now()
            self.save()
            return False

        # Check if prediction was correct
        self.was_correct = (self.predicted_winner == actual_winner)
        self.evaluated_at = timezone.now()
        self.save()

        return self.was_correct

    @classmethod
    def calculate_accuracy(cls, sport_type=None, model_used=None, days=1):
        """
        Calculate prediction accuracy for given filters

        Args:
            sport_type: Filter by sport type (e.g., 'nfl', 'mlb')
            model_used: Filter by model (e.g., 'nfl_predictor')
            days: Number of days to look back (default: today only)

        Returns:
            dict: Accuracy metrics
        """
        cutoff_date = timezone.now() - timedelta(days=days)

        queryset = cls.objects.filter(
            created_at__gte=cutoff_date,
            was_correct__isnull=False  # Only evaluated predictions
        )

        if sport_type:
            queryset = queryset.filter(sport_type=sport_type)

        if model_used:
            queryset = queryset.filter(model_used=model_used)

        total = queryset.count()
        if total == 0:
            return {
                'total_predictions': 0,
                'correct_predictions': 0,
                'accuracy_percentage': 0.0,
                'confidence_avg': 0.0
            }

        correct = queryset.filter(was_correct=True).count()
        confidence_avg = queryset.aggregate(Avg('confidence'))['confidence__avg'] or 0.0

        return {
            'total_predictions': total,
            'correct_predictions': correct,
            'accuracy_percentage': round((correct / total) * 100, 2),
            'confidence_avg': round(confidence_avg, 2)
        }


class UserBet(UnifiedBaseModel):
    """
    User bets placed on predictions
    Tracks which predictions users actually bet on for profit/loss calculation
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sports_bets',
        help_text="User who placed the bet"
    )

    prediction = models.ForeignKey(
        MLPrediction,
        on_delete=models.CASCADE,
        related_name='user_bets',
        help_text="ML prediction this bet is based on"
    )

    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='user_bets',
        help_text="Game being bet on"
    )

    # Bet details
    bet_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Amount wagered (in units)"
    )

    bet_type = models.CharField(
        max_length=20,
        choices=BetType.choices,
        default=BetType.MONEYLINE,
        help_text="Type of bet placed"
    )

    selected_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='bets_on_team',
        help_text="Team selected to win"
    )

    odds_at_placement = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Odds when bet was placed (e.g., -110, +150)"
    )

    # Bet outcome
    status = models.CharField(
        max_length=20,
        choices=BetStatus.choices,
        default=BetStatus.PENDING,
        help_text="Bet status"
    )

    profit_loss = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Profit or loss from this bet (+ for win, - for loss)"
    )

    settled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When bet was settled"
    )

    # Tracking
    is_simulated = models.BooleanField(
        default=True,
        help_text="Whether this is a simulated bet (paper trading) or real money"
    )

    class Meta:
        verbose_name = "User Bet"
        verbose_name_plural = "User Bets"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['game', 'user']),
            models.Index(fields=['prediction']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.bet_amount} units on {self.selected_team.abbreviation}"

    def settle(self):
        """
        Settle the bet after game completes
        Calculates profit/loss based on odds and outcome
        """
        if self.status != BetStatus.PENDING:
            return  # Already settled

        if self.game.status != GameStatus.FINAL:
            return  # Game not finished

        if self.game.home_score is None or self.game.away_score is None:
            return  # No scores available

        # Determine winner
        if self.game.home_score > self.game.away_score:
            actual_winner = self.game.home_team
        elif self.game.away_score > self.game.home_score:
            actual_winner = self.game.away_team
        else:
            # Tie/Push
            self.status = BetStatus.PUSH
            self.profit_loss = Decimal('0.00')
            self.settled_at = timezone.now()
            self.save()
            return

        # Check if bet won
        if self.selected_team == actual_winner:
            # Calculate profit based on odds
            if self.odds_at_placement < 0:
                # Negative odds (e.g., -110 means bet $110 to win $100)
                profit = self.bet_amount * (Decimal('100') / abs(self.odds_at_placement))
            else:
                # Positive odds (e.g., +150 means bet $100 to win $150)
                profit = self.bet_amount * (self.odds_at_placement / Decimal('100'))

            self.status = BetStatus.WON
            self.profit_loss = profit
        else:
            # Lost bet
            self.status = BetStatus.LOST
            self.profit_loss = -self.bet_amount

        self.settled_at = timezone.now()
        self.save()

    @classmethod
    def calculate_user_stats(cls, user, days=1):
        """
        Calculate betting statistics for a user

        Args:
            user: User object
            days: Number of days to look back (default: today only)

        Returns:
            dict: User betting statistics
        """
        cutoff_date = timezone.now() - timedelta(days=days)

        bets = cls.objects.filter(
            user=user,
            created_at__gte=cutoff_date
        )

        settled_bets = bets.exclude(status=BetStatus.PENDING)
        won_bets = bets.filter(status=BetStatus.WON)

        total_bets = bets.count()
        total_settled = settled_bets.count()
        total_won = won_bets.count()

        if total_settled == 0:
            win_rate = 0.0
        else:
            win_rate = (total_won / total_settled) * 100

        # Calculate profit/loss
        profit_loss = settled_bets.aggregate(
            total=Sum('profit_loss')
        )['total'] or Decimal('0.00')

        return {
            'total_bets': total_bets,
            'settled_bets': total_settled,
            'won_bets': total_won,
            'lost_bets': settled_bets.filter(status=BetStatus.LOST).count(),
            'push_bets': settled_bets.filter(status=BetStatus.PUSH).count(),
            'win_rate_percentage': round(float(win_rate), 2),
            'profit_loss': float(profit_loss),
            'roi_percentage': round(float(profit_loss / bets.aggregate(total=Sum('bet_amount'))['total'] or 1) * 100, 2) if bets.count() > 0 else 0.0
        }