"""
Learning Loop Models - Session 463
Tracks prediction accuracy and user feedback for the Market Intelligence Desk

These models enable the autonomous situation to learn from outcomes and improve over time.
"""

import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class PredictionOutcome(models.Model):
    """
    Tracks a single stock prediction (bull or bear case) and its actual outcome.

    This enables:
    1. Measuring bull/bear prediction accuracy over time
    2. Identifying which market conditions lead to accurate predictions
    3. Calibrating confidence scores based on track record
    4. Learning which debate patterns predict actual outcomes
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the brief that made this prediction
    brief = models.ForeignKey(
        'core.MarketIntelligenceBrief',
        on_delete=models.CASCADE,
        related_name='prediction_outcomes',
        help_text="The Market Intelligence Brief that made this prediction"
    )

    # Stock identification
    ticker = models.CharField(
        max_length=10,
        help_text="Stock ticker symbol (e.g., AAPL, MSFT)"
    )

    # Prediction details
    prediction_type = models.CharField(
        max_length=10,
        choices=[
            ('BULL', 'Bull Case'),
            ('BEAR', 'Bear Case'),
        ],
        help_text="Whether this was a bull or bear prediction"
    )
    conviction_level = models.CharField(
        max_length=10,
        choices=[
            ('HIGH', 'High Conviction'),
            ('MEDIUM', 'Medium Conviction'),
            ('LOW', 'Low Conviction'),
        ],
        help_text="Conviction level at prediction time"
    )
    predicted_move = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Predicted percentage move (e.g., +25.00 for bull, -15.00 for bear)"
    )

    # Price data at prediction time
    price_at_prediction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Stock price when prediction was made"
    )
    prediction_date = models.DateField(
        help_text="Date prediction was made"
    )

    # Actual outcome data
    price_after_7_days = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Stock price 7 days after prediction"
    )
    price_after_30_days = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Stock price 30 days after prediction"
    )
    actual_move_7_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual percentage move after 7 days"
    )
    actual_move_30_days = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual percentage move after 30 days"
    )

    # Accuracy assessment
    was_correct_7_days = models.BooleanField(
        null=True,
        blank=True,
        help_text="True if prediction direction was correct after 7 days"
    )
    was_correct_30_days = models.BooleanField(
        null=True,
        blank=True,
        help_text="True if prediction direction was correct after 30 days"
    )
    accuracy_score_7_days = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Accuracy score 0-1 (considers direction + magnitude)"
    )
    accuracy_score_30_days = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Accuracy score 0-1 (considers direction + magnitude)"
    )

    # Market context at prediction time (for pattern learning)
    market_regime = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=[
            ('STRONG_BULL', 'Strong Bull Market'),
            ('BULL', 'Bull Market'),
            ('NEUTRAL', 'Neutral/Ranging'),
            ('BEAR', 'Bear Market'),
            ('STRONG_BEAR', 'Strong Bear Market'),
        ],
        help_text="Market regime at prediction time"
    )
    volatility_level = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=[
            ('EXTREME', 'Extreme Volatility'),
            ('HIGH', 'High Volatility'),
            ('MODERATE', 'Moderate Volatility'),
            ('LOW', 'Low Volatility'),
        ],
        help_text="Volatility level at prediction time"
    )

    # Debate zone context
    was_in_debate_zone = models.BooleanField(
        default=False,
        help_text="True if this stock was in the debate zone (bull vs bear disagreed)"
    )
    opposite_conviction = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Conviction level of the opposite case (bull if this is bear, vice versa)"
    )

    # Outcome status
    outcome_calculated = models.BooleanField(
        default=False,
        help_text="True if we've calculated the actual outcome"
    )
    outcome_calculated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When outcome was calculated"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Prediction Outcome"
        verbose_name_plural = "Prediction Outcomes"
        ordering = ['-prediction_date', 'ticker']
        indexes = [
            models.Index(fields=['-prediction_date']),
            models.Index(fields=['ticker', '-prediction_date']),
            models.Index(fields=['prediction_type', 'conviction_level']),
            models.Index(fields=['was_correct_7_days']),
            models.Index(fields=['was_in_debate_zone']),
            models.Index(fields=['outcome_calculated']),
        ]

    def __str__(self):
        return f"{self.ticker} {self.prediction_type} ({self.conviction_level}) - {self.prediction_date}"

    def calculate_outcome(self, current_price=None, days_elapsed=None):
        """
        Calculate prediction accuracy based on actual price movement.

        Args:
            current_price: Current stock price (if checking now)
            days_elapsed: How many days since prediction (7 or 30)
        """
        from datetime import date, timedelta

        if days_elapsed is None:
            # Auto-detect based on date
            days_since = (date.today() - self.prediction_date).days
            if days_since >= 30:
                days_elapsed = 30
            elif days_since >= 7:
                days_elapsed = 7
            else:
                return  # Not enough time has passed

        if current_price is None:
            # Fetch current price from market data service
            from core.services.market_data_service import MarketDataService
            service = MarketDataService()
            data = service.get_stock_details(self.ticker)
            if not data or 'current_price' not in data:
                return
            current_price = Decimal(str(data['current_price']))

        # Calculate actual move
        actual_move = ((current_price - self.price_at_prediction) / self.price_at_prediction) * 100

        # Store price and move
        if days_elapsed == 7:
            self.price_after_7_days = current_price
            self.actual_move_7_days = actual_move

            # Determine if prediction was correct
            predicted_up = self.predicted_move > 0
            actual_up = actual_move > 0
            self.was_correct_7_days = (predicted_up == actual_up)

            # Calculate accuracy score (0-1)
            # Perfect prediction = 1.0, wrong direction = 0.0, partial credit for magnitude
            if self.was_correct_7_days:
                # Same direction - score based on magnitude accuracy
                magnitude_ratio = min(abs(float(actual_move)) / abs(float(self.predicted_move)), 2.0)
                self.accuracy_score_7_days = 0.5 + (0.5 * (1.0 / magnitude_ratio))
            else:
                # Wrong direction - score decreases with magnitude of mistake
                self.accuracy_score_7_days = max(0.0, 0.3 - (abs(float(actual_move)) / 100.0))

        elif days_elapsed == 30:
            self.price_after_30_days = current_price
            self.actual_move_30_days = actual_move

            predicted_up = self.predicted_move > 0
            actual_up = actual_move > 0
            self.was_correct_30_days = (predicted_up == actual_up)

            if self.was_correct_30_days:
                magnitude_ratio = min(abs(float(actual_move)) / abs(float(self.predicted_move)), 2.0)
                self.accuracy_score_30_days = 0.5 + (0.5 * (1.0 / magnitude_ratio))
            else:
                self.accuracy_score_30_days = max(0.0, 0.3 - (abs(float(actual_move)) / 100.0))

        self.outcome_calculated = True
        from django.utils import timezone
        self.outcome_calculated_at = timezone.now()
        self.save()


class UserBriefFeedback(models.Model):
    """
    Captures user feedback and actions on Market Intelligence Briefs.

    This enables:
    1. Tracking which briefs were useful vs not useful
    2. Measuring which stocks users acted on (buy/sell/hold)
    3. Learning which recommendations users follow
    4. Improving brief quality based on user engagement
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to user and brief
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='brief_feedback',
        help_text="User who provided feedback"
    )
    brief = models.ForeignKey(
        'core.MarketIntelligenceBrief',
        on_delete=models.CASCADE,
        related_name='user_feedback',
        help_text="The brief being rated"
    )

    # Overall brief rating
    was_helpful = models.BooleanField(
        null=True,
        blank=True,
        help_text="Did user find the brief helpful?"
    )
    helpfulness_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1-5 star rating of brief quality"
    )

    # Specific stock actions
    actions_taken = models.JSONField(
        default=list,
        help_text="List of actions: [{'ticker': 'AAPL', 'action': 'buy', 'reason': 'bull_case'}]"
    )

    # User engagement metrics
    viewed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When user first viewed the brief"
    )
    acted_on_brief = models.BooleanField(
        default=False,
        help_text="True if user took any action based on brief"
    )
    time_to_action = models.IntegerField(
        null=True,
        blank=True,
        help_text="Minutes between viewing and taking action"
    )

    # Follow-through tracking
    followed_bullish_recommendation = models.BooleanField(
        default=False,
        help_text="Did user buy/hold stocks from bullish_opportunities?"
    )
    followed_bearish_warning = models.BooleanField(
        default=False,
        help_text="Did user sell/avoid stocks from bearish_warnings?"
    )
    explored_debate_zone = models.BooleanField(
        default=False,
        help_text="Did user research stocks in debate zone?"
    )

    # Free-form feedback
    comment = models.TextField(
        blank=True,
        help_text="Optional user comment about the brief"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'core'
        verbose_name = "User Brief Feedback"
        verbose_name_plural = "User Brief Feedback"
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['user', '-viewed_at']),
            models.Index(fields=['brief', 'user']),
            models.Index(fields=['was_helpful']),
            models.Index(fields=['acted_on_brief']),
        ]
        # One feedback entry per user per brief
        unique_together = [['user', 'brief']]

    def __str__(self):
        helpful = "Helpful" if self.was_helpful else "Not Helpful" if self.was_helpful is False else "Not Rated"
        return f"{self.user.username} - {self.brief.brief_date} ({helpful})"

    def record_action(self, ticker, action, reason=None):
        """
        Record a user action (buy/sell/hold/ignore) on a specific stock.

        Args:
            ticker: Stock ticker
            action: 'buy', 'sell', 'hold', 'ignore'
            reason: Optional reason (e.g., 'bull_case', 'bear_warning', 'debate_zone')
        """
        action_entry = {
            'ticker': ticker,
            'action': action,
            'reason': reason,
            'timestamp': timezone.now().isoformat(),
        }

        if not self.actions_taken:
            self.actions_taken = []

        self.actions_taken.append(action_entry)
        self.acted_on_brief = True

        # Update follow-through flags
        if reason == 'bull_case' and action in ['buy', 'hold']:
            self.followed_bullish_recommendation = True
        elif reason == 'bear_warning' and action in ['sell', 'avoid']:
            self.followed_bearish_warning = True
        elif reason == 'debate_zone':
            self.explored_debate_zone = True

        # Calculate time to action
        if not self.time_to_action and self.viewed_at:
            from django.utils import timezone
            time_diff = timezone.now() - self.viewed_at
            self.time_to_action = int(time_diff.total_seconds() / 60)  # Convert to minutes

        self.save()


class AgentAccuracyMetrics(models.Model):
    """
    Rolling accuracy metrics for Bull Case Agent and Bear Case Agent.

    This enables:
    1. Tracking agent performance over time
    2. Adjusting confidence scores based on track record
    3. Identifying which market conditions each agent performs best in
    4. Building trust scores for different prediction types
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Agent identification
    agent_name = models.CharField(
        max_length=50,
        choices=[
            ('BullCaseAgent', 'Bull Case Agent'),
            ('BearCaseAgent', 'Bear Case Agent'),
        ],
        help_text="Which agent these metrics track"
    )

    # Time period
    period_start = models.DateField(help_text="Start of measurement period")
    period_end = models.DateField(help_text="End of measurement period")

    # Overall accuracy
    total_predictions = models.IntegerField(
        default=0,
        help_text="Total predictions made in this period"
    )
    correct_predictions_7_days = models.IntegerField(
        default=0,
        help_text="Correct predictions after 7 days"
    )
    correct_predictions_30_days = models.IntegerField(
        default=0,
        help_text="Correct predictions after 30 days"
    )
    accuracy_rate_7_days = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Percentage accuracy after 7 days"
    )
    accuracy_rate_30_days = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Percentage accuracy after 30 days"
    )

    # Conviction calibration
    high_conviction_accuracy = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Accuracy rate for HIGH conviction predictions"
    )
    medium_conviction_accuracy = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Accuracy rate for MEDIUM conviction predictions"
    )
    low_conviction_accuracy = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Accuracy rate for LOW conviction predictions"
    )

    # Market regime performance
    bull_market_accuracy = models.FloatField(
        default=0.0,
        null=True,
        blank=True,
        help_text="Accuracy during bull markets"
    )
    bear_market_accuracy = models.FloatField(
        default=0.0,
        null=True,
        blank=True,
        help_text="Accuracy during bear markets"
    )
    neutral_market_accuracy = models.FloatField(
        default=0.0,
        null=True,
        blank=True,
        help_text="Accuracy during neutral/ranging markets"
    )

    # Debate zone insights
    debate_zone_accuracy = models.FloatField(
        default=0.0,
        null=True,
        blank=True,
        help_text="Accuracy when agent was in debate zone (disagreed with opposite agent)"
    )
    debate_zone_win_rate = models.FloatField(
        default=0.0,
        null=True,
        blank=True,
        help_text="Win rate when in debate zone (agent was right, opposite was wrong)"
    )

    # Confidence adjustment multiplier
    confidence_multiplier = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0.5), MaxValueValidator(1.5)],
        help_text="Multiplier to adjust confidence scores based on track record (0.5-1.5)"
    )

    # Timestamps
    calculated_at = models.DateTimeField(
        auto_now=True,
        help_text="When metrics were last calculated"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'core'
        verbose_name = "Agent Accuracy Metrics"
        verbose_name_plural = "Agent Accuracy Metrics"
        ordering = ['-period_end', 'agent_name']
        indexes = [
            models.Index(fields=['agent_name', '-period_end']),
            models.Index(fields=['-calculated_at']),
        ]
        # One metrics entry per agent per period
        unique_together = [['agent_name', 'period_start', 'period_end']]

    def __str__(self):
        return f"{self.agent_name} - {self.period_start} to {self.period_end} ({self.accuracy_rate_7_days:.1f}% accurate)"

    def calculate_metrics(self):
        """
        Calculate all accuracy metrics based on prediction outcomes in this period.
        """
        from django.db.models import Avg, Count, Q

        # Get all predictions for this agent in this period
        predictions = PredictionOutcome.objects.filter(
            prediction_type='BULL' if self.agent_name == 'BullCaseAgent' else 'BEAR',
            prediction_date__gte=self.period_start,
            prediction_date__lte=self.period_end,
            outcome_calculated=True
        )

        self.total_predictions = predictions.count()

        if self.total_predictions == 0:
            return

        # Overall accuracy
        self.correct_predictions_7_days = predictions.filter(was_correct_7_days=True).count()
        self.correct_predictions_30_days = predictions.filter(was_correct_30_days=True).count()

        if self.total_predictions > 0:
            self.accuracy_rate_7_days = (self.correct_predictions_7_days / self.total_predictions) * 100
            self.accuracy_rate_30_days = (self.correct_predictions_30_days / self.total_predictions) * 100

        # Conviction calibration
        for conviction in ['HIGH', 'MEDIUM', 'LOW']:
            conviction_preds = predictions.filter(conviction_level=conviction)
            if conviction_preds.exists():
                correct = conviction_preds.filter(was_correct_7_days=True).count()
                total = conviction_preds.count()
                accuracy = (correct / total) * 100

                if conviction == 'HIGH':
                    self.high_conviction_accuracy = accuracy
                elif conviction == 'MEDIUM':
                    self.medium_conviction_accuracy = accuracy
                elif conviction == 'LOW':
                    self.low_conviction_accuracy = accuracy

        # Debate zone performance
        debate_preds = predictions.filter(was_in_debate_zone=True)
        if debate_preds.exists():
            debate_correct = debate_preds.filter(was_correct_7_days=True).count()
            self.debate_zone_accuracy = (debate_correct / debate_preds.count()) * 100

        # Calculate confidence multiplier based on overall performance
        # If accuracy > 60%: increase confidence (up to 1.5x)
        # If accuracy < 40%: decrease confidence (down to 0.5x)
        # If accuracy = 50%: neutral (1.0x)
        if self.accuracy_rate_7_days >= 60:
            self.confidence_multiplier = 1.0 + ((self.accuracy_rate_7_days - 60) / 100)
        elif self.accuracy_rate_7_days <= 40:
            self.confidence_multiplier = 0.5 + (self.accuracy_rate_7_days / 80)
        else:
            self.confidence_multiplier = 1.0

        # Ensure within bounds
        self.confidence_multiplier = max(0.5, min(1.5, self.confidence_multiplier))

        self.save()
