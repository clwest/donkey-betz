"""
Session 563: Bet Tracking Models
Database models for tracking placed bets, parlays, and betting history.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone


class PlacedWager(models.Model):
    """
    Session 563: A placed wager - can be a single bet or a parlay.
    Separate from models_bankroll.Wager to support multi-leg parlays.
    """
    WAGER_TYPE_CHOICES = [
        ('single', 'Single Bet'),
        ('parlay', 'Parlay'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('push', 'Push'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wagers',
        null=True,
        blank=True
    )

    # Wager details
    wager_type = models.CharField(max_length=20, choices=WAGER_TYPE_CHOICES, default='single')
    stake = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount wagered")
    odds = models.IntegerField(help_text="American odds for the wager")
    potential_payout = models.DecimalField(max_digits=12, decimal_places=2, help_text="Potential winnings including stake")

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    result_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Actual P/L")

    # Timestamps
    placed_at = models.DateTimeField(default=timezone.now)
    settled_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-placed_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['placed_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        legs = self.legs.count()
        if self.wager_type == 'parlay':
            return f"{legs}-leg Parlay @ {self.odds:+d} (${self.stake})"
        return f"Single @ {self.odds:+d} (${self.stake})"

    @property
    def decimal_odds(self):
        """Convert American odds to decimal."""
        if self.odds > 0:
            return 1 + (self.odds / 100)
        else:
            return 1 + (100 / abs(self.odds))

    @property
    def implied_probability(self):
        """Calculate implied probability from odds."""
        if self.odds > 0:
            return 100 / (self.odds + 100)
        else:
            return abs(self.odds) / (abs(self.odds) + 100)

    def calculate_payout(self):
        """Calculate potential payout based on stake and odds."""
        decimal = self.decimal_odds
        return round(float(self.stake) * decimal, 2)

    def settle(self, won: bool, push: bool = False):
        """Settle the wager."""
        if push:
            self.status = 'push'
            self.result_amount = Decimal('0.00')
        elif won:
            self.status = 'won'
            self.result_amount = Decimal(str(self.potential_payout)) - self.stake
        else:
            self.status = 'lost'
            self.result_amount = -self.stake

        self.settled_at = timezone.now()
        self.save()


class PlacedWagerLeg(models.Model):
    """
    Session 563: A single leg/pick within a wager.
    For single bets, there's one leg. For parlays, there are multiple.
    """
    MARKET_TYPE_CHOICES = [
        ('h2h', 'Moneyline'),
        ('spreads', 'Spread'),
        ('totals', 'Total'),
        ('props', 'Player Prop'),
        ('futures', 'Futures'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('push', 'Push'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wager = models.ForeignKey(PlacedWager, on_delete=models.CASCADE, related_name='legs')

    # Event details
    event_id = models.CharField(max_length=100, help_text="The Odds API event ID")
    sport = models.CharField(max_length=50)
    matchup = models.CharField(max_length=200, help_text="e.g., 'Lakers vs Celtics'")
    commence_time = models.DateTimeField(null=True, blank=True)

    # Pick details
    market_type = models.CharField(max_length=20, choices=MARKET_TYPE_CHOICES, default='h2h')
    pick = models.CharField(max_length=200, help_text="e.g., 'Lakers -5.5' or 'Over 220.5'")
    odds = models.IntegerField(help_text="American odds for this leg")
    line = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, help_text="Point spread or total")
    bookmaker = models.CharField(max_length=50)

    # Result
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    final_score = models.CharField(max_length=50, blank=True, help_text="e.g., '110-105'")

    class Meta:
        ordering = ['wager', 'id']

    def __str__(self):
        return f"{self.matchup}: {self.pick} @ {self.odds:+d}"

    @property
    def decimal_odds(self):
        """Convert American odds to decimal."""
        if self.odds > 0:
            return 1 + (self.odds / 100)
        else:
            return 1 + (100 / abs(self.odds))


class BettingStats(models.Model):
    """
    Aggregated betting statistics for a user.
    Updated periodically or on-demand.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='betting_stats',
        null=True,
        blank=True
    )

    # Overall stats
    total_wagers = models.IntegerField(default=0)
    total_stake = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_profit_loss = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    # Win/Loss record
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    pushes = models.IntegerField(default=0)
    pending = models.IntegerField(default=0)

    # Streaks
    current_streak = models.IntegerField(default=0, help_text="Positive = win streak, negative = loss streak")
    longest_win_streak = models.IntegerField(default=0)
    longest_loss_streak = models.IntegerField(default=0)

    # By type
    singles_record = models.JSONField(default=dict, help_text="{'wins': 0, 'losses': 0, 'profit': 0}")
    parlays_record = models.JSONField(default=dict, help_text="{'wins': 0, 'losses': 0, 'profit': 0}")

    # By sport
    stats_by_sport = models.JSONField(default=dict, help_text="{'nba': {'wins': 0, ...}, ...}")

    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Betting stats"

    def __str__(self):
        return f"Betting Stats: {self.wins}W-{self.losses}L ({self.total_profit_loss:+.2f})"

    @property
    def win_rate(self):
        """Calculate win rate percentage."""
        total = self.wins + self.losses
        if total == 0:
            return 0.0
        return round((self.wins / total) * 100, 1)

    @property
    def roi(self):
        """Calculate return on investment."""
        if self.total_stake == 0:
            return 0.0
        return round((float(self.total_profit_loss) / float(self.total_stake)) * 100, 1)

    def recalculate(self):
        """Recalculate all stats from wager history."""
        from django.db.models import Sum

        wagers = PlacedWager.objects.filter(user=self.user) if self.user else PlacedWager.objects.all()

        # Basic counts
        self.total_wagers = wagers.count()
        self.total_stake = wagers.aggregate(Sum('stake'))['stake__sum'] or Decimal('0.00')

        # Status counts
        self.wins = wagers.filter(status='won').count()
        self.losses = wagers.filter(status='lost').count()
        self.pushes = wagers.filter(status='push').count()
        self.pending = wagers.filter(status='pending').count()

        # Total P/L
        self.total_profit_loss = wagers.exclude(
            status__in=['pending', 'cancelled']
        ).aggregate(Sum('result_amount'))['result_amount__sum'] or Decimal('0.00')

        # Calculate streaks
        settled = wagers.exclude(status__in=['pending', 'cancelled', 'push']).order_by('-settled_at')
        current = 0
        max_win = 0
        max_loss = 0
        temp_win = 0
        temp_loss = 0

        for i, w in enumerate(settled):
            if i == 0:
                current = 1 if w.status == 'won' else -1

            if w.status == 'won':
                temp_win += 1
                temp_loss = 0
                max_win = max(max_win, temp_win)
                if i == 0 or (i > 0 and settled[i-1].status == 'won'):
                    current = temp_win
            else:
                temp_loss += 1
                temp_win = 0
                max_loss = max(max_loss, temp_loss)
                if i == 0 or (i > 0 and settled[i-1].status == 'lost'):
                    current = -temp_loss

        self.current_streak = current
        self.longest_win_streak = max_win
        self.longest_loss_streak = max_loss

        # By type
        singles = wagers.filter(wager_type='single')
        parlays = wagers.filter(wager_type='parlay')

        self.singles_record = {
            'wins': singles.filter(status='won').count(),
            'losses': singles.filter(status='lost').count(),
            'profit': float(singles.exclude(status__in=['pending', 'cancelled']).aggregate(Sum('result_amount'))['result_amount__sum'] or 0)
        }

        self.parlays_record = {
            'wins': parlays.filter(status='won').count(),
            'losses': parlays.filter(status='lost').count(),
            'profit': float(parlays.exclude(status__in=['pending', 'cancelled']).aggregate(Sum('result_amount'))['result_amount__sum'] or 0)
        }

        self.save()
