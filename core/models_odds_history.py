"""
Odds History Models
===================

Session 561: Store historical odds snapshots for line movement charts.

Models:
- OddsSnapshot: Point-in-time odds capture for a specific game/bookmaker/market
"""

from django.db import models
from django.utils import timezone


class OddsSnapshot(models.Model):
    """
    Historical snapshot of odds for line movement tracking.

    Captures odds at regular intervals to show how lines move over time.
    """

    # Game identification
    game_id = models.CharField(max_length=100, db_index=True, help_text="The Odds API game ID")
    sport_key = models.CharField(max_length=50, db_index=True)
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    commence_time = models.DateTimeField(help_text="Game start time")

    # Bookmaker info
    bookmaker = models.CharField(max_length=50, db_index=True)
    bookmaker_title = models.CharField(max_length=100, blank=True)

    # Market type
    MARKET_CHOICES = [
        ('h2h', 'Moneyline'),
        ('spreads', 'Spread'),
        ('totals', 'Totals'),
    ]
    market = models.CharField(max_length=20, choices=MARKET_CHOICES, db_index=True)

    # Outcome details
    outcome_name = models.CharField(max_length=100, help_text="Team name, Over, or Under")
    price = models.IntegerField(help_text="American odds (e.g., -110, +150)")
    point = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True,
        help_text="Spread or total line (e.g., -3.5, 45.5)"
    )

    # Snapshot metadata
    captured_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        verbose_name = "Odds Snapshot"
        verbose_name_plural = "Odds Snapshots"
        ordering = ['-captured_at']
        indexes = [
            models.Index(fields=['game_id', 'bookmaker', 'market', 'outcome_name']),
            models.Index(fields=['sport_key', 'captured_at']),
            models.Index(fields=['game_id', 'captured_at']),
        ]

    def __str__(self):
        return f"{self.away_team}@{self.home_team} | {self.bookmaker} | {self.outcome_name}: {self.price}"

    @property
    def decimal_odds(self):
        """Convert American odds to decimal."""
        if self.price > 0:
            return round(1 + (self.price / 100), 3)
        else:
            return round(1 + (100 / abs(self.price)), 3)

    @property
    def implied_probability(self):
        """Convert American odds to implied probability."""
        if self.price > 0:
            return round(100 / (self.price + 100), 4)
        else:
            return round(abs(self.price) / (abs(self.price) + 100), 4)


class GameLineHistory(models.Model):
    """
    Aggregated line movement summary for a game.

    Stores opening line, current line, and key movement stats.
    Denormalized for fast dashboard queries.
    """

    game_id = models.CharField(max_length=100, unique=True, db_index=True)
    sport_key = models.CharField(max_length=50, db_index=True)
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    commence_time = models.DateTimeField()

    # Opening lines (first snapshot)
    open_spread_home = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    open_spread_price = models.IntegerField(null=True, blank=True)
    open_total = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    open_ml_home = models.IntegerField(null=True, blank=True)
    open_ml_away = models.IntegerField(null=True, blank=True)

    # Current lines (latest snapshot)
    current_spread_home = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    current_spread_price = models.IntegerField(null=True, blank=True)
    current_total = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    current_ml_home = models.IntegerField(null=True, blank=True)
    current_ml_away = models.IntegerField(null=True, blank=True)

    # Movement tracking
    spread_movement = models.DecimalField(
        max_digits=5, decimal_places=1, default=0,
        help_text="Change in spread from open to current"
    )
    total_movement = models.DecimalField(
        max_digits=5, decimal_places=1, default=0,
        help_text="Change in total from open to current"
    )

    # Snapshot counts
    snapshot_count = models.PositiveIntegerField(default=0)
    first_snapshot_at = models.DateTimeField(null=True, blank=True)
    last_snapshot_at = models.DateTimeField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Game Line History"
        verbose_name_plural = "Game Line Histories"
        ordering = ['-commence_time']

    def __str__(self):
        return f"{self.away_team} @ {self.home_team} ({self.sport_key})"

    @property
    def has_significant_movement(self):
        """Check if line has moved significantly (> 0.5 points or 1 full point total)."""
        spread_sig = abs(self.spread_movement or 0) >= 0.5
        total_sig = abs(self.total_movement or 0) >= 1
        return spread_sig or total_sig
