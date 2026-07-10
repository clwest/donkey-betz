"""
HAI → Inbox signal receiver — CDR-001 §7 Gap 1 (§16 wrap-up bundle)
====================================================================

Wires ``HumanAttentionItem.post_save`` to the pre-existing Inbox
``DirectMessage`` substrate via a ``transaction.on_commit`` → Celery
task handoff. Same shape as the Discord receiver (PR #3038) and Web
Push receiver (PR #3040) — no new abstraction; extension of the
canonical fanout pattern documented in CDR-001 §2.3.

The Inbox lane was dark to HAI fanout before this receiver:
seven imperative ``DirectMessage.objects.create`` sites exist
(``views_inbox.py:141,165,223`` — ``employees/comms.py:343`` —
``services/user_onboarding_service.py:123,209`` —
``services/td_handlers_core.py:3830``) but no
``@receiver(post_save, sender='core.HumanAttentionItem')`` wired the
Inbox substrate to critical HAI items. This module closes that gap.

Ratified rules governing this receiver:
- PLAYBOOK-2.2.2 (CDR discipline) — CDR-001 §7 Gap 1 covers scope
- PLAYBOOK-3.2.2 (acceptance-tests-first) — AT16-1 pre-drafted
- PLAYBOOK-5.2.2 (Tool Autonomy) — governs SIGN dispatch of this file

Chain::

    HumanAttentionBridge.create_*_attention
      → HumanInterfaceService.create_attention_item
        → HumanAttentionItem.objects.create      (post_save fires)
      → on_hai_inbox_dispatch (this receiver, fast sync guards)
      → transaction.on_commit
      → notify_hai_inbox.delay(item.id)          (Celery task)
      → task re-loads HAI + re-applies all gates
      → DirectMessage.objects.create (Inbox row)
      → HAIDispatchLog.objects.create (cross-channel audit)

Kill switch: ``settings.HAI_INBOX_DISPATCH_ENABLED`` (default True).

Filters (parallel to Discord + Web Push receivers):
* ``created=True`` only — urgency-upgraded-via-update does not re-fire.
* Urgency floor: ``critical`` only for v1 (matches Discord + Web Push).
* Cross-channel dedup via ``payload_has_channel_fired(payload, 'inbox')``
  — check the CDR-001 §7 Gap 3 canonical ``channels_fired`` list.
* Per-user preference gates re-applied inside the task after re-loading
  the row (same discipline as Discord + Web Push tasks).
* Rollback safety: ``transaction.on_commit`` ensures the Celery task is
  only enqueued if the HAI row actually committed.
"""
from __future__ import annotations

import logging

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.services.hai_dispatch_state import payload_has_channel_fired

logger = logging.getLogger(__name__)


def _enqueue_inbox_dispatch(item_id):
    """Enqueue the ``notify_hai_inbox`` Celery task.

    Wrapped in a helper so ``transaction.on_commit`` can call it via
    ``lambda`` without name-binding gotchas.
    """
    try:
        from core.tasks_push_notifications import notify_hai_inbox
        notify_hai_inbox.delay(str(item_id))
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[HAI_INBOX] failed to enqueue notify_hai_inbox for %s '
            '(%s: %s); HAI write unaffected',
            item_id, type(e).__name__, e,
        )


@receiver(post_save, sender='core.HumanAttentionItem')
def on_hai_inbox_dispatch(sender, instance, created, **kwargs):
    """Enqueue an Inbox DirectMessage for critical HAI items on transaction commit.

    Fast synchronous guards here (kill switch, created, urgency floor,
    channels_fired check) so we do not enqueue Celery tasks for HAIs
    that will obviously be skipped. Preference gates are re-checked
    inside the task against the committed row so a stale in-flight
    receiver snapshot cannot fire an alert the current DB state would
    suppress.
    """
    if not getattr(settings, 'HAI_INBOX_DISPATCH_ENABLED', True):
        return
    if not created:
        return
    urgency = getattr(instance, 'urgency', None) or ''
    if urgency != 'critical':
        return
    payload = getattr(instance, 'payload', None) or {}
    if payload_has_channel_fired(payload, 'inbox'):
        logger.info(
            '[HAI_INBOX] skip enqueue source_type=%s source_id=%s — '
            "payload flagged channels_fired includes 'inbox'",
            getattr(instance, 'source_type', ''),
            getattr(instance, 'source_id', ''),
        )
        return

    item_id = getattr(instance, 'id', None)
    if not item_id:
        return

    transaction.on_commit(lambda: _enqueue_inbox_dispatch(item_id))
