"""
Push Notification Service
=========================

Session 562: Service for sending Web Push notifications.
Uses pywebpush for VAPID-authenticated push messages.
"""

import logging
import json
from typing import Dict
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from pywebpush import webpush, WebPushException

logger = logging.getLogger(__name__)


class PushNotificationService:
    """
    Service for sending Web Push notifications to subscribed browsers.

    Supports:
    - Arbitrage alerts
    - Line movement notifications
    - Game start reminders
    - Bet result notifications
    """

    def __init__(self):
        self.vapid_private_key = settings.VAPID_PRIVATE_KEY
        self.vapid_public_key = settings.VAPID_PUBLIC_KEY
        self.vapid_email = settings.VAPID_ADMIN_EMAIL
        self.enabled = settings.PUSH_NOTIFICATIONS_ENABLED

    def send_notification(self, subscription_info: Dict, title: str, body: str,
                         notification_type: str = 'system', data: Dict = None,
                         ttl: int = 3600) -> bool:
        """
        Send a push notification to a single subscription.

        Args:
            subscription_info: Dict with endpoint and keys
            title: Notification title
            body: Notification body text
            notification_type: Type of notification (arb, line_move, etc.)
            data: Additional data to include
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            logger.debug("Push notifications disabled, skipping")
            return False

        payload = {
            'title': title,
            'body': body,
            'type': notification_type,
            'data': data or {},
            'timestamp': datetime.now().isoformat()
        }

        # Add icon based on type
        if notification_type == 'arb':
            payload['icon'] = '/static/images/arb-alert.png'
            payload['requireInteraction'] = True

        try:
            response = webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims={
                    "sub": f"mailto:{self.vapid_email}"
                },
                ttl=ttl
            )
            logger.debug(f"Push notification sent successfully: {response.status_code}")
            return True

        except WebPushException as e:
            logger.error(f"Push notification failed: {e}")
            if e.response and e.response.status_code in [404, 410]:
                # Subscription no longer valid
                logger.warning("Subscription expired or invalid")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending push: {e}")
            return False

    def send_arb_alert(self, profit_pct: float, matchup: str,
                       home_book: str, away_book: str,
                       sport: str = None, game_time: str = None) -> int:
        """
        Send arbitrage alert to all subscribed users who want arb notifications.

        Returns:
            Number of notifications sent successfully
        """
        from core.models_push_notifications import PushSubscription, NotificationPreference, NotificationLog

        # Build notification content
        rating = "HOT" if profit_pct >= 1.5 else "GOOD" if profit_pct >= 1.0 else "ARB"
        title = f"{rating}: {profit_pct:.2f}% Guaranteed Profit"
        body = f"{matchup}\n{home_book} vs {away_book}"
        if game_time:
            body += f"\nGame: {game_time}"

        data = {
            'type': 'arb',
            'profit_pct': profit_pct,
            'matchup': matchup,
            'home_book': home_book,
            'away_book': away_book,
            'sport': sport,
            'url': '/ai-studio/?tab=betting&subtab=arbitrage'
        }

        sent_count = 0

        # Get active subscriptions with users who want arb alerts
        subscriptions = PushSubscription.objects.filter(
            is_active=True,
            user__isnull=False
        ).select_related('user')

        for sub in subscriptions:
            try:
                # Check user preferences
                prefs = NotificationPreference.objects.filter(user=sub.user).first()

                if prefs and not prefs.should_send_arb_notification(profit_pct, sport):
                    continue

                # Default: send if no preferences exist and profit is decent
                if not prefs and profit_pct < 1.0:
                    continue

                # Check rate limit (max notifications per hour)
                hour_ago = timezone.now() - timedelta(hours=1)
                recent_count = NotificationLog.objects.filter(
                    subscription=sub,
                    sent_at__gte=hour_ago
                ).count()

                max_per_hour = prefs.max_notifications_per_hour if prefs else 10
                if recent_count >= max_per_hour:
                    logger.debug(f"Rate limit reached for {sub.user.username}")
                    continue

                # Send notification
                success = self.send_notification(
                    subscription_info=sub.get_subscription_info(),
                    title=title,
                    body=body,
                    notification_type='arb',
                    data=data
                )

                # Log the notification
                NotificationLog.objects.create(
                    subscription=sub,
                    notification_type='arb',
                    title=title,
                    body=body,
                    data=data,
                    delivered=success
                )

                if success:
                    sub.mark_success()
                    sent_count += 1
                else:
                    sub.mark_failed()

            except Exception as e:
                logger.error(f"Error sending to subscription {sub.id}: {e}")

        logger.info(f"Arb alert sent to {sent_count} subscribers")
        return sent_count

    def send_line_movement_alert(self, game_id: str, matchup: str,
                                  spread_movement: float, total_movement: float,
                                  sport: str = None) -> int:
        """
        Send line movement alert to users who have movement alerts enabled.
        """
        from core.models_push_notifications import PushSubscription, NotificationLog

        # Determine which movement to highlight
        if abs(spread_movement) >= abs(total_movement):
            direction = "+" if spread_movement > 0 else ""
            title = f"Line Move: {direction}{spread_movement:.1f} points"
            movement_type = "spread"
        else:
            direction = "+" if total_movement > 0 else ""
            title = f"Total Move: {direction}{total_movement:.1f} points"
            movement_type = "total"

        body = matchup
        data = {
            'type': 'line_move',
            'game_id': game_id,
            'spread_movement': spread_movement,
            'total_movement': total_movement,
            'url': f'/ai-studio/?tab=betting&subtab=line-movement&game={game_id}'
        }

        sent_count = 0

        # Get subscriptions with line movement alerts enabled
        subscriptions = PushSubscription.objects.filter(
            is_active=True,
            user__isnull=False,
            user__notification_preferences__line_movement_enabled=True
        ).select_related('user', 'user__notification_preferences')

        for sub in subscriptions:
            try:
                prefs = sub.user.notification_preferences

                # Check threshold
                threshold = float(prefs.line_movement_threshold)
                max_movement = max(abs(spread_movement), abs(total_movement))
                if max_movement < threshold:
                    continue

                # Check quiet hours
                if prefs.quiet_hours_enabled:
                    current_hour = timezone.now().hour
                    if prefs.quiet_start_hour <= current_hour or current_hour < prefs.quiet_end_hour:
                        continue

                success = self.send_notification(
                    subscription_info=sub.get_subscription_info(),
                    title=title,
                    body=body,
                    notification_type='line_move',
                    data=data
                )

                NotificationLog.objects.create(
                    subscription=sub,
                    notification_type='line_move',
                    title=title,
                    body=body,
                    data=data,
                    delivered=success
                )

                if success:
                    sub.mark_success()
                    sent_count += 1
                else:
                    sub.mark_failed()

            except Exception as e:
                logger.error(f"Error sending line movement alert: {e}")

        return sent_count

    def send_test_notification(self, subscription_info: Dict) -> bool:
        """Send a test notification to verify subscription works."""
        return self.send_notification(
            subscription_info=subscription_info,
            title="Donkey Betz Test",
            body="Push notifications are working!",
            notification_type='system',
            data={'test': True}
        )


# Singleton instance
_service = None

def get_push_service() -> PushNotificationService:
    """Get or create the push notification service singleton."""
    global _service
    if _service is None:
        _service = PushNotificationService()
    return _service
