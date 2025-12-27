"""
Bankroll Tracker Models
=======================

Session 558: Track betting bankroll, wagers, and performance.

Models:
- Bankroll: User's betting account balance and settings
- Wager: Individual bets placed (pending, won, lost, pushed)
- BettingSession: Group wagers by session for analysis
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class Bankroll(models.Model):
    """
    User's betting bankroll account.

    Tracks balance, unit sizing, and overall performance.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='betting_bankroll'
    )

    # Balance tracking
    initial_balance = models.DecimalField(max_digits=12, decimal_places=2, default=1000)
    current_balance = models.DecimalField(max_digits=12, decimal_places=2, default=1000)
    highest_balance = models.DecimalField(max_digits=12, decimal_places=2, default=1000)
    lowest_balance = models.DecimalField(max_digits=12, decimal_places=2, default=1000)

    # Unit sizing
    unit_size = models.DecimalField(
        max_digits=12, decimal_places=2, default=10,
        help_text="Standard unit size for 1-unit bets"
    )
    max_bet_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.00,
        help_text="Maximum % of bankroll per single bet"
    )

    # Performance stats (cached, updated on wager resolution)
    total_wagers = models.PositiveIntegerField(default=0)
    total_won = models.PositiveIntegerField(default=0)
    total_lost = models.PositiveIntegerField(default=0)
    total_pushed = models.PositiveIntegerField(default=0)
    total_pending = models.PositiveIntegerField(default=0)

    # Financial stats
    total_wagered = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_returned = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Streak tracking
    current_streak = models.IntegerField(default=0)  # Positive = winning, negative = losing
    best_streak = models.IntegerField(default=0)
    worst_streak = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_wager_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Bankrolls"

    def __str__(self):
        return f"{self.user.username}'s Bankroll: ${self.current_balance}"

    @property
    def roi(self):
        """Return on investment percentage."""
        if self.total_wagered == 0:
            return Decimal('0')
        return (self.total_profit / self.total_wagered) * 100

    @property
    def win_rate(self):
        """Win percentage (excluding pushes and pending)."""
        resolved = self.total_won + self.total_lost
        if resolved == 0:
            return Decimal('0')
        return (Decimal(self.total_won) / resolved) * 100

    @property
    def profit_loss(self):
        """Current P/L from initial balance."""
        return self.current_balance - self.initial_balance

    def calculate_recommended_bet(self, confidence=1):
        """
        Calculate recommended bet size based on Kelly Criterion variant.

        Args:
            confidence: 1-3 units based on confidence level

        Returns:
            Decimal bet amount
        """
        # Simple unit-based sizing
        base_bet = self.unit_size * Decimal(str(confidence))

        # Cap at max_bet_percentage of bankroll
        max_bet = (self.max_bet_percentage / 100) * self.current_balance
        return min(base_bet, max_bet)

    def update_stats(self):
        """Recalculate stats from wager history."""
        from django.db.models import Sum, Count

        wagers = self.wagers.all()

        self.total_wagers = wagers.count()
        self.total_won = wagers.filter(status='won').count()
        self.total_lost = wagers.filter(status='lost').count()
        self.total_pushed = wagers.filter(status='pushed').count()
        self.total_pending = wagers.filter(status='pending').count()

        self.total_wagered = wagers.aggregate(Sum('stake'))['stake__sum'] or Decimal('0')
        self.total_returned = wagers.filter(status='won').aggregate(Sum('payout'))['payout__sum'] or Decimal('0')
        self.total_profit = self.total_returned - self.total_wagered

        # Update balance tracking
        if self.current_balance > self.highest_balance:
            self.highest_balance = self.current_balance
        if self.current_balance < self.lowest_balance:
            self.lowest_balance = self.current_balance

        self.save()


class Wager(models.Model):
    """
    Individual bet placed by user.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('pushed', 'Pushed'),
        ('cancelled', 'Cancelled'),
    ]

    BET_TYPE_CHOICES = [
        ('moneyline', 'Moneyline'),
        ('spread', 'Spread'),
        ('total', 'Over/Under'),
        ('prop', 'Prop Bet'),
        ('parlay', 'Parlay'),
        ('teaser', 'Teaser'),
        ('futures', 'Futures'),
        ('live', 'Live Bet'),
        ('prediction', 'Prediction Market'),
        ('other', 'Other'),
    ]

    bankroll = models.ForeignKey(
        Bankroll,
        on_delete=models.CASCADE,
        related_name='wagers'
    )

    # Bet details
    sport = models.CharField(max_length=50, blank=True)
    event_name = models.CharField(max_length=200)
    selection = models.CharField(max_length=200, help_text="What you bet on")
    bet_type = models.CharField(max_length=20, choices=BET_TYPE_CHOICES, default='moneyline')
    line = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="Spread or total line"
    )

    # Odds and stakes
    odds_american = models.IntegerField(help_text="American odds (e.g., -110, +150)")
    odds_decimal = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    stake = models.DecimalField(max_digits=12, decimal_places=2)
    units = models.DecimalField(
        max_digits=5, decimal_places=2, default=1,
        help_text="Units wagered (based on bankroll unit size)"
    )

    # Outcome
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payout = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    profit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # Source tracking
    bookmaker = models.CharField(max_length=100, blank=True)
    source = models.CharField(max_length=50, blank=True, help_text="discord, web, manual")
    agent_recommendation = models.BooleanField(default=False)
    recommendation_confidence = models.PositiveSmallIntegerField(null=True, blank=True)

    # Timestamps
    placed_at = models.DateTimeField(default=timezone.now)
    event_time = models.DateTimeField(null=True, blank=True)
    settled_at = models.DateTimeField(null=True, blank=True)

    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-placed_at']

    def __str__(self):
        odds_str = f"+{self.odds_american}" if self.odds_american > 0 else str(self.odds_american)
        return f"{self.selection} ({odds_str}) - ${self.stake} [{self.status}]"

    def save(self, *args, **kwargs):
        # Calculate decimal odds if not set
        if self.odds_decimal is None:
            if self.odds_american > 0:
                self.odds_decimal = Decimal(str((self.odds_american / 100) + 1))
            else:
                self.odds_decimal = Decimal(str((100 / abs(self.odds_american)) + 1))

        # Calculate payout and profit for won bets
        if self.status == 'won' and self.payout is None:
            self.payout = self.stake * self.odds_decimal
            self.profit = self.payout - self.stake
        elif self.status == 'lost':
            self.payout = Decimal('0')
            self.profit = -self.stake
        elif self.status == 'pushed':
            self.payout = self.stake
            self.profit = Decimal('0')

        # Set settled time
        if self.status in ('won', 'lost', 'pushed') and not self.settled_at:
            self.settled_at = timezone.now()

        super().save(*args, **kwargs)

        # Update bankroll stats
        if self.bankroll_id:
            self.bankroll.update_stats()

    def resolve(self, status, final_score=None):
        """
        Resolve the wager with outcome.

        Args:
            status: 'won', 'lost', or 'pushed'
            final_score: Optional score/result for notes
        """
        if self.status != 'pending':
            return False

        self.status = status
        if final_score:
            self.notes = f"Final: {final_score}\n" + self.notes

        # Update bankroll balance
        if status == 'won':
            self.payout = self.stake * self.odds_decimal
            self.profit = self.payout - self.stake
            self.bankroll.current_balance += self.profit
        elif status == 'lost':
            self.payout = Decimal('0')
            self.profit = -self.stake
            self.bankroll.current_balance += self.profit  # Negative
        elif status == 'pushed':
            self.payout = self.stake
            self.profit = Decimal('0')

        self.settled_at = timezone.now()
        self.save()
        self.bankroll.save()
        return True

    @property
    def potential_payout(self):
        """Calculate potential payout if bet wins."""
        if self.odds_decimal:
            return self.stake * self.odds_decimal
        return self.stake

    @property
    def potential_profit(self):
        """Calculate potential profit if bet wins."""
        return self.potential_payout - self.stake


class BettingSession(models.Model):
    """
    Group wagers into sessions for analysis.

    A session could be a single day, a weekend, or a specific event.
    """

    bankroll = models.ForeignKey(
        Bankroll,
        on_delete=models.CASCADE,
        related_name='sessions'
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Session timing
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Session stats (calculated)
    wager_count = models.PositiveIntegerField(default=0)
    total_staked = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    win_count = models.PositiveIntegerField(default=0)
    loss_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date})"

    @property
    def roi(self):
        """Session ROI."""
        if self.total_staked == 0:
            return Decimal('0')
        return (self.total_profit / self.total_staked) * 100

    @property
    def win_rate(self):
        """Session win rate."""
        total = self.win_count + self.loss_count
        if total == 0:
            return Decimal('0')
        return (Decimal(self.win_count) / total) * 100
