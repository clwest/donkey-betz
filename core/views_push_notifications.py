"""
Push Notification API Views
===========================

Session 562: API endpoints for Web Push subscription management.
"""

import logging
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

from core.models_push_notifications import PushSubscription, NotificationPreference
from core.services.push_notification_service import get_push_service

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_vapid_public_key(request):
    """
    Get the VAPID public key for push subscription.

    GET /api/v1/push/vapid-key/

    Returns:
        {
            "publicKey": "BASE64_ENCODED_VAPID_PUBLIC_KEY"
        }
    """
    return JsonResponse({
        'publicKey': settings.VAPID_PUBLIC_KEY,
        'enabled': settings.PUSH_NOTIFICATIONS_ENABLED
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow anonymous subscriptions but prefer authenticated
def subscribe_push(request):
    """
    Subscribe to push notifications.

    POST /api/v1/push/subscribe/

    Body:
        {
            "endpoint": "https://fcm.googleapis.com/...",
            "keys": {
                "p256dh": "BASE64_KEY",
                "auth": "BASE64_AUTH"
            }
        }

    Returns:
        { "success": true, "message": "Subscribed successfully" }
    """
    try:
        data = request.data

        endpoint = data.get('endpoint')
        keys = data.get('keys', {})
        p256dh = keys.get('p256dh')
        auth = keys.get('auth')

        if not all([endpoint, p256dh, auth]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields: endpoint, keys.p256dh, keys.auth'
            }, status=400)

        # Get or update subscription
        subscription, created = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'p256dh_key': p256dh,
                'auth_key': auth,
                'user': request.user if request.user.is_authenticated else None,
                'browser': request.META.get('HTTP_USER_AGENT', '')[:50],
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'is_active': True,
                'failed_count': 0
            }
        )

        # Create default notification preferences for authenticated users
        if request.user.is_authenticated:
            NotificationPreference.objects.get_or_create(
                user=request.user,
                defaults={
                    'notifications_enabled': True,
                    'arb_alerts_enabled': True,
                    'arb_min_profit_pct': settings.PUSH_ARB_MIN_PROFIT_DEFAULT
                }
            )

        # Send test notification
        push_service = get_push_service()
        test_sent = push_service.send_test_notification(subscription.get_subscription_info())

        return JsonResponse({
            'success': True,
            'message': 'Subscribed successfully' if created else 'Subscription updated',
            'subscription_id': subscription.id,
            'test_sent': test_sent
        })

    except Exception as e:
        logger.error(f"Push subscription error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def unsubscribe_push(request):
    """
    Unsubscribe from push notifications.

    POST /api/v1/push/unsubscribe/

    Body:
        { "endpoint": "https://fcm.googleapis.com/..." }
    """
    try:
        endpoint = request.data.get('endpoint')

        if not endpoint:
            return JsonResponse({
                'success': False,
                'error': 'Missing endpoint'
            }, status=400)

        deleted, _ = PushSubscription.objects.filter(endpoint=endpoint).delete()

        return JsonResponse({
            'success': True,
            'message': 'Unsubscribed successfully' if deleted else 'Subscription not found'
        })

    except Exception as e:
        logger.error(f"Push unsubscribe error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def notification_preferences(request):
    """
    Get or update notification preferences.

    GET /api/v1/push/preferences/
        Returns current preferences

    PUT /api/v1/push/preferences/
        Updates preferences
    """
    try:
        prefs, created = NotificationPreference.objects.get_or_create(
            user=request.user,
            defaults={
                'notifications_enabled': True,
                'arb_alerts_enabled': True,
                'arb_min_profit_pct': settings.PUSH_ARB_MIN_PROFIT_DEFAULT
            }
        )

        if request.method == 'GET':
            return JsonResponse({
                'success': True,
                'preferences': {
                    'notifications_enabled': prefs.notifications_enabled,
                    'arb_alerts_enabled': prefs.arb_alerts_enabled,
                    'arb_min_profit_pct': float(prefs.arb_min_profit_pct),
                    'arb_sports': prefs.arb_sports,
                    'line_movement_enabled': prefs.line_movement_enabled,
                    'line_movement_threshold': float(prefs.line_movement_threshold),
                    'quiet_hours_enabled': prefs.quiet_hours_enabled,
                    'quiet_start_hour': prefs.quiet_start_hour,
                    'quiet_end_hour': prefs.quiet_end_hour,
                    'max_notifications_per_hour': prefs.max_notifications_per_hour
                }
            })

        # PUT - Update preferences
        data = request.data

        if 'notifications_enabled' in data:
            prefs.notifications_enabled = data['notifications_enabled']
        if 'arb_alerts_enabled' in data:
            prefs.arb_alerts_enabled = data['arb_alerts_enabled']
        if 'arb_min_profit_pct' in data:
            prefs.arb_min_profit_pct = data['arb_min_profit_pct']
        if 'arb_sports' in data:
            prefs.arb_sports = data['arb_sports']
        if 'line_movement_enabled' in data:
            prefs.line_movement_enabled = data['line_movement_enabled']
        if 'line_movement_threshold' in data:
            prefs.line_movement_threshold = data['line_movement_threshold']
        if 'quiet_hours_enabled' in data:
            prefs.quiet_hours_enabled = data['quiet_hours_enabled']
        if 'quiet_start_hour' in data:
            prefs.quiet_start_hour = data['quiet_start_hour']
        if 'quiet_end_hour' in data:
            prefs.quiet_end_hour = data['quiet_end_hour']
        if 'max_notifications_per_hour' in data:
            prefs.max_notifications_per_hour = data['max_notifications_per_hour']

        prefs.save()

        return JsonResponse({
            'success': True,
            'message': 'Preferences updated'
        })

    except Exception as e:
        logger.error(f"Notification preferences error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_subscription_status(request):
    """
    Check if user has an active push subscription.

    GET /api/v1/push/status/
    """
    try:
        subscriptions = PushSubscription.objects.filter(
            user=request.user,
            is_active=True
        )

        return JsonResponse({
            'success': True,
            'subscribed': subscriptions.exists(),
            'subscription_count': subscriptions.count(),
            'subscriptions': [
                {
                    'id': s.id,
                    'browser': s.browser,
                    'created_at': s.created_at.isoformat(),
                    'last_used_at': s.last_used_at.isoformat() if s.last_used_at else None
                }
                for s in subscriptions
            ]
        })

    except Exception as e:
        logger.error(f"Subscription status error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_test_push(request):
    """
    Send a test push notification to verify subscription works.

    POST /api/v1/push/test/
    """
    try:
        subscriptions = PushSubscription.objects.filter(
            user=request.user,
            is_active=True
        )

        if not subscriptions.exists():
            return JsonResponse({
                'success': False,
                'error': 'No active subscriptions found'
            }, status=400)

        push_service = get_push_service()
        sent_count = 0

        for sub in subscriptions:
            if push_service.send_test_notification(sub.get_subscription_info()):
                sent_count += 1

        return JsonResponse({
            'success': True,
            'message': f'Test notification sent to {sent_count} device(s)'
        })

    except Exception as e:
        logger.error(f"Test push error: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
