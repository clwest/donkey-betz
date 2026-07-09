"""
HAI → Web Push signal receiver — Session 2735, HAI Delivery Fanout Extension PR 2.

Same Cat A extension pattern as PR 1 (Discord). Wires
``HumanAttentionItem.post_save`` to the pre-existing Web Push substrate
via a ``transaction.on_commit`` → Celery task handoff. No new
architecture beyond one signal receiver + one Celery task.

Substrate that already exists at HEAD:

* ``PushSubscription`` model at ``core/models_push_notifications.py:14``
  stores Web Push subscription data per user (browser endpoint + VAPID
  keys).
* ``PushNotificationService`` at ``core/services/push_notification_service.py:20``
  wraps ``pywebpush`` for VAPID-authenticated dispatch. Handles
  subscription-expired detection (404/410 → mark inactive).
* ``NotificationLog`` at ``core/models_push_notifications.py:183`` audits
  per-subscription dispatch with delivered=True/False.
* ``HumanPreference`` gate substrate matches the Discord receiver.

Missing wire (Cat B closure): no receiver connects HAI creation to
Web Push dispatch. ``PushNotificationService`` is only called from
arbitrage-scan (``tasks_misc.py:2566``) today — HAI escalations get
Expo push and now Discord (PR 1) but NOT browser Web Push.

Chain::

    HumanAttentionBridge.create_*_attention
      → HumanInterfaceService.create_attention_item
        → HumanAttentionItem.objects.create           (post_save fires)
      → [this receiver — fast synchronous guards]
      → transaction.on_commit
      → notify_hai_webpush.delay(item.id)             (Celery task)
      → task re-loads HAI + re-applies gates
      → PushNotificationService.send_notification     (per subscription)
      → NotificationLog audit row per dispatch

Kill switch: ``settings.HAI_WEBPUSH_DISPATCH_ENABLED`` (default True).
Independent from ``HAI_DISCORD_DISPATCH_ENABLED`` and from Expo push's
implicit enable state.

Filters (mirrors PR 1's receiver pattern for consistency; Web Push
differs from Discord only in that per-user preferences ALWAYS apply
because Web Push is per-subscription, never broadcast):

* ``created=True`` only.
* Urgency floor: ``critical`` only for v1. Matches Discord + Expo
  policies. Follow-up PR expands if operators evidence noise-tolerance.
* Payload flag guard: ``payload['webpush_sent']=True`` from producers
  that already fired imperative Web Push blocks re-dispatch. No known
  imperative Web Push producers of HAI exist at HEAD (the arb-scan
  path does not create HAI), so no producer methods are flagged in
  this PR — but the guard is in place for future consistency.
* Per-user HumanPreference gates (re-applied inside the task):
  ``min_urgency_to_notify`` + ``quiet_hours_start`` / ``quiet_hours_end``
  + ``blocked_sources``. Fail-open on any preference-lookup exception.
* Rollback safety via ``transaction.on_commit`` — rolled-back HAI
  creates do NOT enqueue.
"""
from __future__ import annotations

import logging

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _enqueue_webpush(item_id):
    """Enqueue notify_hai_webpush. Wrapped so on_commit lambda name-binding
    behaves correctly for the item_id closure."""
    try:
        from core.tasks_push_notifications import notify_hai_webpush
        notify_hai_webpush.delay(str(item_id))
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[HAI_WEBPUSH] failed to enqueue notify_hai_webpush for %s '
            '(%s: %s); HAI write unaffected',
            item_id, type(e).__name__, e,
        )


@receiver(post_save, sender='core.HumanAttentionItem')
def on_hai_webpush_dispatch(sender, instance, created, **kwargs):
    """Enqueue a Web Push dispatch for critical HAI items on commit.

    Fast synchronous guards here (kill switch, created, urgency floor,
    webpush_sent flag). Preference gates + per-subscription iteration
    happen inside the Celery task against the committed row.
    """
    if not getattr(settings, 'HAI_WEBPUSH_DISPATCH_ENABLED', True):
        return
    if not created:
        return
    urgency = getattr(instance, 'urgency', None) or ''
    if urgency != 'critical':
        return
    payload = getattr(instance, 'payload', None) or {}
    if payload.get('webpush_sent') is True:
        logger.info(
            '[HAI_WEBPUSH] skip enqueue source_type=%s source_id=%s — '
            'producer flagged webpush_sent=True',
            getattr(instance, 'source_type', ''),
            getattr(instance, 'source_id', ''),
        )
        return

    item_id = getattr(instance, 'id', None)
    if not item_id:
        return

    transaction.on_commit(lambda: _enqueue_webpush(item_id))
