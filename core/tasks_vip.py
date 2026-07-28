"""VIP invite lifecycle Celery tasks.

Ships as backstop enforcement for ADR-0005 §3.5 F-C-VIP-1 risk-gate.
Primary enforcement is at core/vip_middleware.py; this task guarantees
expired VIP users are marked inactive within one beat cycle even if
they never make another request.
"""

import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name='core.tasks_vip.cleanup_expired_vip_users')
def cleanup_expired_vip_users():
    """Deactivate VIP users whose redeeming invite has passed account_expires_at.

    Idempotent: only touches users currently is_active=True. Returns a dict
    summarizing the run for observability.
    """
    from core.models_vip_invite import VIPInvite

    User = get_user_model()
    now = timezone.now()

    expired_invites = (
        VIPInvite.objects
        .filter(
            account_expires_at__lt=now,
            redeemed_by__isnull=False,
            redeemed_by__is_active=True,
        )
        .select_related('redeemed_by')
    )

    deactivated = 0
    checked = 0
    for invite in expired_invites:
        checked += 1
        user = invite.redeemed_by
        if user is None or not user.is_active:
            continue
        user.is_active = False
        user.save(update_fields=['is_active'])
        deactivated += 1
        logger.info(
            "cleanup_expired_vip_users: deactivated user=%s invite=%s expired_at=%s",
            user.username, invite.id, invite.account_expires_at.isoformat(),
        )

    result = {
        'checked': checked,
        'deactivated': deactivated,
        'ran_at': now.isoformat(),
    }
    logger.info("cleanup_expired_vip_users complete: %s", result)
    return result
