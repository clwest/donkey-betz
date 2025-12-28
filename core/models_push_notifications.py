"""
Push Notification Models
========================

Session 562: Store Web Push subscriptions and notification preferences.
Uses the Web Push Protocol (RFC 8030) with VAPID authentication.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import json


class PushSubscription(models.Model):
    """
    Stores Web Push API subscription data for browser push notifications.

    Each subscription is unique per browser/device endpoint.
    VAPID (Voluntary Application Server Identification) keys are used
    to authenticate the server to the push service.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
        null=True,
        blank=True,
        help_text="Associated user (null for anonymous subscriptions)"
    )

    # Push subscription data from browser
    endpoint = models.URLField(
        max_length=500,
        unique=True,
        help_text="Push service endpoint URL"
    )

    p256dh_key = models.CharField(
        max_length=200,
        help_text="Client's P-256 ECDH public key"
    )

    auth_key = models.CharField(
        max_length=50,
        help_text="Authentication secret"
    )

    # Device info
    browser = models.CharField(max_length=50, blank=True, default='')
    device_type = models.CharField(max_length=20, blank=True, default='')  # desktop, mobile, tablet
    user_agent = models.TextField(blank=True, default='')

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_used_at = models.DateTimeField(null=True, blank=True)
    failed_count = models.IntegerField(default=0, help_text="Consecutive failed push attempts")

    class Meta:
        db_table = 'push_subscriptions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['is_active', 'created_at']),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else "anonymous"
        return f"PushSub: {user_str} ({self.browser or 'unknown'})"

    def get_subscription_info(self):
        """Return subscription dict for pywebpush."""
        return {
            "endpoint": self.endpoint,
            "keys": {
                "p256dh": self.p256dh_key,
                "auth": self.auth_key
            }
        }

    def mark_failed(self):
        """Increment failure count, deactivate after 3 failures."""
        self.failed_count += 1
        if self.failed_count >= 3:
            self.is_active = False
        self.save()

    def mark_success(self):
        """Reset failure count on successful push."""
        self.failed_count = 0
        self.last_used_at = timezone.now()
        self.save()


class NotificationPreference(models.Model):
    """
    User preferences for what notifications to receive and thresholds.
    """

    NOTIFICATION_TYPES = [
        ('arb_hot', 'Hot Arbitrage (1.5%+)'),
        ('arb_good', 'Good Arbitrage (1.0-1.5%)'),
        ('arb_any', 'Any Arbitrage (0.5%+)'),
        ('line_movement', 'Significant Line Movement'),
        ('game_start', 'Game Starting Soon'),
        ('bet_result', 'Bet Results'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_notification_preferences'
    )

    # Master switch
    notifications_enabled = models.BooleanField(default=True)

    # Arbitrage alerts
    arb_alerts_enabled = models.BooleanField(default=True)
    arb_min_profit_pct = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=1.0,
        help_text="Minimum profit % to trigger notification"
    )
    arb_sports = models.JSONField(
        default=list,
        blank=True,
        help_text="List of sports to alert on (empty = all)"
    )

    # Line movement alerts
    line_movement_enabled = models.BooleanField(default=False)
    line_movement_threshold = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=1.0,
        help_text="Minimum point movement to trigger alert"
    )

    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_start_hour = models.IntegerField(default=22, help_text="Hour to start quiet time (0-23)")
    quiet_end_hour = models.IntegerField(default=8, help_text="Hour to end quiet time (0-23)")

    # Rate limiting
    max_notifications_per_hour = models.IntegerField(default=10)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'

    def __str__(self):
        return f"NotifPrefs: {self.user.username}"

    def should_send_arb_notification(self, profit_pct: float, sport: str = None) -> bool:
        """Check if we should send an arb notification based on preferences."""
        if not self.notifications_enabled:
            return False

        if not self.arb_alerts_enabled:
            return False

        if profit_pct < float(self.arb_min_profit_pct):
            return False

        # Check sport filter
        if self.arb_sports and sport:
            if sport.lower() not in [s.lower() for s in self.arb_sports]:
                return False

        # Check quiet hours
        if self.quiet_hours_enabled:
            current_hour = timezone.now().hour
            if self.quiet_start_hour <= current_hour or current_hour < self.quiet_end_hour:
                return False

        return True


class NotificationLog(models.Model):
    """
    Log of sent notifications for rate limiting and history.
    """

    NOTIFICATION_TYPES = [
        ('arb', 'Arbitrage Alert'),
        ('line_move', 'Line Movement'),
        ('game_start', 'Game Starting'),
        ('bet_result', 'Bet Result'),
        ('system', 'System Message'),
    ]

    subscription = models.ForeignKey(
        PushSubscription,
        on_delete=models.CASCADE,
        related_name='notification_logs'
    )

    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)

    # Delivery status
    sent_at = models.DateTimeField(default=timezone.now)
    delivered = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'notification_logs'
        indexes = [
            models.Index(fields=['subscription', 'sent_at']),
            models.Index(fields=['notification_type', 'sent_at']),
        ]
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.notification_type}: {self.title[:30]}"
