"""
Expo Push Notification Service — sends push notifications via Expo's push API.

Usage:
    from core.services.expo_push import send_push_to_user

    send_push_to_user(
        user_id=42,
        title="New critical boardroom item",
        body="Agent flagged a high-priority issue",
        route="/boardroom/attention/abc-123",
        object_type="boardroom_attention",
        object_id="abc-123",
    )
"""

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

EXPO_PUSH_URL = 'https://exp.host/--/api/v2/push/send'
EXPO_PUSH_TIMEOUT = 10  # seconds


def send_expo_push(
    token: str,
    title: str,
    body: str,
    data: Optional[dict] = None,
) -> bool:
    """Send a single push notification via Expo's push API."""
    payload = {
        'to': token,
        'title': title,
        'body': body,
        'sound': 'default',
        'priority': 'high',
    }
    if data:
        payload['data'] = data

    try:
        resp = requests.post(
            EXPO_PUSH_URL,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=EXPO_PUSH_TIMEOUT,
        )
        resp.raise_for_status()
        result = resp.json()
        # Expo returns {"data": {"status": "ok"}} on success
        status = result.get('data', {}).get('status', 'unknown')
        if status == 'ok':
            logger.info('[ExpoPush] Sent to %s...', token[:20])
            return True
        else:
            logger.warning('[ExpoPush] Non-ok status for %s: %s', token[:20], result)
            return False
    except Exception as e:
        logger.error('[ExpoPush] Failed to send to %s: %s', token[:20], e)
        return False


def send_push_to_user(
    user_id: int,
    title: str,
    body: str,
    route: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
) -> int:
    """
    Send push notification to all active devices for a user.
    Returns the number of successful sends.
    """
    from core.models_mobile import MobilePushToken

    tokens = MobilePushToken.objects.filter(
        user_id=user_id,
        revoked_at__isnull=True,
    ).values_list('token', flat=True)

    if not tokens:
        logger.debug('[ExpoPush] No tokens for user %s', user_id)
        return 0

    data = {}
    if route:
        data['route'] = route
    if object_type:
        data['object_type'] = object_type
    if object_id:
        data['object_id'] = str(object_id)

    sent = 0
    for token in tokens:
        if send_expo_push(token, title, body, data or None):
            sent += 1

    return sent


def send_push_to_admins(
    title: str,
    body: str,
    route: Optional[str] = None,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None,
) -> int:
    """
    Send push notification to all admin users with registered tokens.
    Returns the number of successful sends.
    """
    from django.contrib.auth import get_user_model
    from core.models_mobile import MobilePushToken

    User = get_user_model()
    admin_ids = User.objects.filter(
        is_staff=True,
    ).values_list('id', flat=True)

    tokens = MobilePushToken.objects.filter(
        user_id__in=admin_ids,
        revoked_at__isnull=True,
    ).values_list('token', flat=True)

    if not tokens:
        return 0

    data = {}
    if route:
        data['route'] = route
    if object_type:
        data['object_type'] = object_type
    if object_id:
        data['object_id'] = str(object_id)

    sent = 0
    for token in tokens:
        if send_expo_push(token, title, body, data or None):
            sent += 1

    return sent
