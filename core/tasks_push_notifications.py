"""
Push notification Celery tasks — dispatched by Django signals or inline calls.

Four trigger events:
1. Critical boardroom attention item created
2. New artifact needs classification
3. Deploy verification failure
4. Studio job (content generation) completed
"""

import logging
from celery import shared_task

logger = logging.getLogger(__name__)


# ── Generic send task ─────────────────────────────────────────────────────────

@shared_task(
    name='send_expo_push_to_user',
    queue='default',
    ignore_result=True,
    soft_time_limit=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=2,
)
def send_expo_push_to_user(user_id, title, body, route=None, object_type=None, object_id=None):
    """Send push notification to a specific user's devices."""
    from core.services.expo_push import send_push_to_user
    sent = send_push_to_user(user_id, title, body, route, object_type, object_id)
    logger.info('[PushTask] Sent %d notifications to user %s: %s', sent, user_id, title)


@shared_task(
    name='send_expo_push_to_admins',
    queue='default',
    ignore_result=True,
    soft_time_limit=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=2,
)
def send_expo_push_to_admins(title, body, route=None, object_type=None, object_id=None):
    """Send push notification to all admin users."""
    from core.services.expo_push import send_push_to_admins
    sent = send_push_to_admins(title, body, route, object_type, object_id)
    logger.info('[PushTask] Sent %d admin notifications: %s', sent, title)


# ── Trigger 1: Critical boardroom attention item ─────────────────────────────

@shared_task(
    name='notify_critical_attention_item',
    queue='default',
    ignore_result=True,
    soft_time_limit=30,
)
def notify_critical_attention_item(item_id):
    """Send push when a critical boardroom attention item is created."""
    try:
        from core.models_human_interface import HumanAttentionItem
        item = HumanAttentionItem.objects.select_related('user').get(id=item_id)

        title = 'Critical Boardroom Item'
        body = item.title[:200] if item.title else 'New critical item requires attention'
        route = f'/boardroom/attention/{item.id}'

        if item.user_id:
            send_expo_push_to_user.delay(
                item.user_id, title, body,
                route=route,
                object_type='boardroom_attention',
                object_id=str(item.id),
            )
        else:
            # No specific user — notify admins
            send_expo_push_to_admins.delay(
                title, body,
                route=route,
                object_type='boardroom_attention',
                object_id=str(item.id),
            )
    except Exception as e:
        logger.error('[PushTrigger] Critical attention notification failed: %s', e)


# ── Trigger 1b: Session 2735 — HAI Delivery Fanout Extension PR 1 ───────────
#
# Discord fanout for HumanAttentionItem creations. Dispatched via
# transaction.on_commit from core.signals_discord_notifications, so the
# Discord API call cannot happen inside a rolled-back transaction and
# cannot stall the caller of HumanAttentionItem.objects.create().
#
# Applies the same gates as the receiver (kill switch, urgency floor,
# payload discord_sent flag, HumanPreference min_urgency + blocked_sources
# + quiet_hours) after re-loading the row inside the worker, because
# the caller's transaction has committed by the time this task runs.

@shared_task(
    name='notify_hai_discord',
    queue='default',
    ignore_result=True,
    soft_time_limit=30,
)
def notify_hai_discord(item_id):
    """Fire a Discord CHANNEL_STATUS alert for a critical HAI item.

    Re-applies all guard logic against the just-committed row so a stale
    receiver payload cannot fire an alert that the current DB state
    would have suppressed.
    """
    from django.conf import settings
    from core.models_human_interface import HumanAttentionItem
    from core.signals_discord_notifications import _pref_gates_pass

    if not getattr(settings, 'HAI_DISCORD_DISPATCH_ENABLED', True):
        return {'skipped': 'kill_switch'}

    try:
        item = HumanAttentionItem.objects.get(id=item_id)
    except HumanAttentionItem.DoesNotExist:
        logger.warning('[HAI_DISCORD] HAI %s missing at task time', item_id)
        return {'skipped': 'missing'}

    if item.urgency != 'critical':
        return {'skipped': 'urgency_not_critical'}

    payload = item.payload or {}
    if payload.get('discord_sent') is True:
        logger.info(
            '[HAI_DISCORD] task skip source_type=%s source_id=%s — '
            'payload flagged discord_sent=True',
            item.source_type, item.source_id,
        )
        return {'skipped': 'discord_sent_flag'}

    if not _pref_gates_pass(item.user_id, item.source_type, item.urgency):
        return {'skipped': 'preference_gate'}

    try:
        from core.services.discord_notifications import send_status_notification
        title = f'[{item.urgency.upper()}] {(item.title or "")[:120]}'
        summary = (item.summary or '')[:400]
        # 'critical' → 'critical'; 'high' → 'warning' (unused in v1 floor)
        status_type = 'critical' if item.urgency == 'critical' else 'warning'
        send_status_notification(
            title=title,
            message=summary,
            status_type=status_type,
        )
        logger.info(
            '[HAI_DISCORD] task dispatched source_type=%s source_id=%s '
            'user_id=%s urgency=%s',
            item.source_type, item.source_id, item.user_id, item.urgency,
        )
        return {'dispatched': True, 'item_id': str(item.id)}
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[HAI_DISCORD] task dispatch failed source_type=%s (%s: %s); '
            'HAI write unaffected',
            item.source_type, type(e).__name__, e,
        )
        return {'skipped': f'adapter_error:{type(e).__name__}'}


# ── Trigger 1c: Session 2735 — HAI Delivery Fanout Extension PR 2 ───────────
#
# Web Push fanout for HumanAttentionItem creations. Same async/on_commit
# structure as notify_hai_discord (PR 1). Iterates the item.user's
# active PushSubscription rows and dispatches Web Push per subscription
# via the pre-existing PushNotificationService. Writes NotificationLog
# audit rows per dispatch (delivered=True/False).

@shared_task(
    name='notify_hai_webpush',
    queue='default',
    ignore_result=True,
    soft_time_limit=60,
)
def notify_hai_webpush(item_id):
    """Fan out a critical HAI item to the target user's active browser
    Web Push subscriptions.

    Re-applies all guard logic against the just-committed row so state
    changes between receiver enqueue and worker run cannot leak a
    dispatch the current DB state would suppress.
    """
    from django.conf import settings
    from core.models_human_interface import HumanAttentionItem
    from core.models_push_notifications import (
        NotificationLog,
        PushSubscription,
    )
    from core.signals_discord_notifications import _pref_gates_pass

    if not getattr(settings, 'HAI_WEBPUSH_DISPATCH_ENABLED', True):
        return {'skipped': 'kill_switch'}

    try:
        item = HumanAttentionItem.objects.get(id=item_id)
    except HumanAttentionItem.DoesNotExist:
        logger.warning('[HAI_WEBPUSH] HAI %s missing at task time', item_id)
        return {'skipped': 'missing'}

    if item.urgency != 'critical':
        return {'skipped': 'urgency_not_critical'}

    payload = item.payload or {}
    if payload.get('webpush_sent') is True:
        logger.info(
            '[HAI_WEBPUSH] task skip source_type=%s source_id=%s — '
            'payload flagged webpush_sent=True',
            item.source_type, item.source_id,
        )
        return {'skipped': 'webpush_sent_flag'}

    if not item.user_id:
        # Web Push is per-user by definition — no subscription rows means
        # nothing to dispatch. Not an error; just no-op.
        return {'skipped': 'no_user'}

    if not _pref_gates_pass(item.user_id, item.source_type, item.urgency):
        return {'skipped': 'preference_gate'}

    subscriptions = list(
        PushSubscription.objects.filter(user_id=item.user_id, is_active=True)
    )
    if not subscriptions:
        return {'skipped': 'no_active_subscriptions'}

    try:
        from core.services.push_notification_service import get_push_service
        push_service = get_push_service()
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[HAI_WEBPUSH] push_service init failed (%s: %s); HAI write '
            'unaffected',
            type(e).__name__, e,
        )
        return {'skipped': f'service_error:{type(e).__name__}'}

    dispatched = 0
    failed = 0
    title = f'[{item.urgency.upper()}] {(item.title or "")[:100]}'
    body = (item.summary or '')[:200]
    data = {
        'type': 'system',
        'source_type': item.source_type,
        'source_id': item.source_id,
        'item_id': str(item.id),
        'urgency': item.urgency,
    }

    for sub in subscriptions:
        try:
            success = push_service.send_notification(
                subscription_info=sub.get_subscription_info(),
                title=title,
                body=body,
                notification_type='system',
                data=data,
            )
            NotificationLog.objects.create(
                subscription=sub,
                notification_type='system',
                title=title,
                body=body,
                data=data,
                delivered=bool(success),
            )
            if success:
                sub.mark_success()
                dispatched += 1
            else:
                sub.mark_failed()
                failed += 1
        except Exception as e:  # pragma: no cover — defensive
            logger.warning(
                '[HAI_WEBPUSH] dispatch to sub %s failed (%s: %s)',
                sub.id, type(e).__name__, e,
            )
            failed += 1

    logger.info(
        '[HAI_WEBPUSH] task dispatched source_type=%s source_id=%s '
        'user_id=%s sent=%d failed=%d',
        item.source_type, item.source_id, item.user_id, dispatched, failed,
    )
    return {
        'dispatched': dispatched,
        'failed': failed,
        'item_id': str(item.id),
    }


# ── Trigger 2: Artifact needs classification ─────────────────────────────────

@shared_task(
    name='notify_needs_classification',
    queue='default',
    ignore_result=True,
    soft_time_limit=30,
)
def notify_needs_classification(artifact_id):
    """Send push when an artifact enters needs-classification state."""
    try:
        from core.models_conversation_artifacts import ExtractedArtifact
        artifact = ExtractedArtifact.objects.get(id=artifact_id)

        title = 'New Artifact Needs Classification'
        body = (artifact.title or 'Unclassified artifact')[:200]

        send_expo_push_to_admins.delay(
            title, body,
            route=f'/governance',
            object_type='artifact_classification',
            object_id=str(artifact.id),
        )
    except Exception as e:
        logger.error('[PushTrigger] Needs classification notification failed: %s', e)


# ── Trigger 3: Deploy verification failure ───────────────────────────────────

@shared_task(
    name='notify_deploy_verify_failure',
    queue='default',
    ignore_result=True,
    soft_time_limit=30,
)
def notify_deploy_verify_failure(failure_summary=''):
    """Send push when deploy verification detects failures."""
    try:
        title = 'Deploy Verification Failed'
        body = failure_summary[:200] if failure_summary else 'One or more deploy checks failed'

        send_expo_push_to_admins.delay(
            title, body,
            route='/dashboard',
            object_type='deploy_verify',
        )
    except Exception as e:
        logger.error('[PushTrigger] Deploy verify notification failed: %s', e)


# ── Trigger 4: Studio job completed ──────────────────────────────────────────

@shared_task(
    name='notify_studio_job_completed',
    queue='default',
    ignore_result=True,
    soft_time_limit=30,
)
def notify_studio_job_completed(job_id, user_id=None, job_type='content'):
    """Send push when a content/media generation job completes."""
    try:
        title = f'{job_type.replace("_", " ").title()} Ready'
        body = f'Your {job_type.replace("_", " ")} generation job has completed'

        if user_id:
            send_expo_push_to_user.delay(
                user_id, title, body,
                route='/content',
                object_type='studio_job',
                object_id=str(job_id),
            )
        else:
            send_expo_push_to_admins.delay(
                title, body,
                route='/content',
                object_type='studio_job',
                object_id=str(job_id),
            )
    except Exception as e:
        logger.error('[PushTrigger] Studio job notification failed: %s', e)
