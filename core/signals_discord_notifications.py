"""
HAI → Discord signal receiver — Session 2735, HAI Delivery Fanout Extension.

Wires ``HumanAttentionItem.post_save`` to the pre-existing Discord
notification substrate via a ``transaction.on_commit`` → Celery task
handoff, so the Discord HTTP call:

  1. Never happens inside a not-yet-committed transaction (would emit
     an alert for a row that later rolls back).
  2. Never stalls the caller of ``HumanAttentionItem.objects.create()``
     on Discord API latency.

The same receiver-driven fanout pattern is already used by
``signals_push_notifications.on_critical_attention_item`` for Expo push
(which enqueues ``notify_critical_attention_item.delay(item_id)``). No
new fanout service is introduced — this module wires the existing HAI
substrate to the existing Discord adapter via the pre-existing Celery
worker infrastructure.

Cat A discipline: NO new architecture beyond one signal receiver + one
Celery task. Dedup + priority + urgency semantics live in
``HumanInterfaceService.create_attention_item``. The Discord adapter
lives in ``discord_notifications.py``. The Celery worker + queue
infrastructure already exists.

Chain::

    HumanAttentionBridge.create_*_attention  (or any create_attention_item caller)
      → HumanInterfaceService.create_attention_item
        → HumanAttentionItem.objects.create      (post_save fires)
      → [this receiver, fast synchronous guards]
      → transaction.on_commit
      → notify_hai_discord.delay(item.id)          (Celery task)
      → task re-loads HAI + re-applies all gates
      → send_status_notification (Discord CHANNEL_STATUS)

Kill switch: ``settings.HAI_DISCORD_DISPATCH_ENABLED`` (default True).
Applied both at receiver enqueue time and at task run time so a
mid-flight config change during a queued task's wait cannot leak an
alert.

Filters (per Rigby SIGN pa-247f1595c5934325 refinements — pre + post
implementation):

* ``created=True`` only. Urgency-upgraded-via-update does not re-fire —
  consistent with the Expo receiver at
  ``signals_push_notifications.py:14``.
* Urgency floor: ``critical`` only for v1 (Q3 tightening). High is
  inbox-only. Matches Expo's default; conservative first ship. If
  evidence shows real operator need for 'high' as well, that becomes
  a follow-up PR.
* Payload-flag double-Discord guard (Q4 REQUIRED refinement): if the
  producer already fired an imperative Discord alert for the same
  incident, it must set ``payload['discord_sent']=True`` when creating
  the row. This receiver AND the task both skip those items —
  preventing spam from producers like
  ``BodyCoordinator._handle_digestive_blocked`` (imperative Discord
  before HAI create) and ``heart.alert_if_critical`` (imperative
  Discord for critical HeartBeat rows).
* Per-user preference gates (Q1 refinement) — applied inside the task
  after re-loading the row, so the gates see the committed DB state:
  ``HumanPreference.min_urgency_to_notify``, ``quiet_hours_start`` /
  ``quiet_hours_end``, ``blocked_sources``. Fail-open on any
  preference-lookup exception.
* Rollback safety (Q3 REQUIRED refinement): ``transaction.on_commit``
  ensures the Celery task is only enqueued if the HAI row actually
  committed. Rolled-back transactions produce no Discord alerts.
"""
from __future__ import annotations

import logging
from datetime import time as _time
from typing import Optional

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger(__name__)


def _in_quiet_hours(pref) -> bool:
    """True if current wall time falls inside the user's quiet-hours window."""
    start: Optional[_time] = getattr(pref, 'quiet_hours_start', None)
    end: Optional[_time] = getattr(pref, 'quiet_hours_end', None)
    if not start or not end:
        return False
    now = timezone.localtime().time()
    if start <= end:
        return start <= now < end
    # Window crosses midnight, e.g. 22:00 → 08:00.
    return now >= start or now < end


def _urgency_ge(a: str, floor: str) -> bool:
    """Order-aware compare against the URGENCY_CHOICES ranking."""
    order = ['low', 'medium', 'high', 'critical']
    try:
        return order.index(a) >= order.index(floor)
    except ValueError:
        return True  # Unknown values fail-open so we don't swallow alerts.


def _pref_gates_pass(user_id, source_type: str, urgency: str) -> bool:
    """Consult HumanPreference for the item's user. Fail-open on error.

    Exported for use by ``core.tasks_push_notifications.notify_hai_discord``
    so gate logic stays single-sourced across the receiver + task.
    """
    if not user_id:
        return True
    try:
        from core.models_human_interface import HumanPreference
        pref = HumanPreference.objects.filter(user_id=user_id).first()
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[HAI_DISCORD] HumanPreference lookup failed user_id=%s (%s: %s); '
            'firing anyway',
            user_id, type(e).__name__, e,
        )
        return True
    if pref is None:
        return True
    try:
        floor = getattr(pref, 'min_urgency_to_notify', 'medium') or 'medium'
        if not _urgency_ge(urgency, floor):
            return False
        blocked = list(getattr(pref, 'blocked_sources', []) or [])
        if source_type in blocked:
            return False
        if _in_quiet_hours(pref):
            return False
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[HAI_DISCORD] preference gate raised user_id=%s (%s: %s); '
            'firing anyway',
            user_id, type(e).__name__, e,
        )
        return True
    return True


def _enqueue_dispatch(item_id):
    """Enqueue the notify_hai_discord Celery task. Wrapped in a helper so
    on_commit can call it via lambda without name-binding gotchas."""
    try:
        from core.tasks_push_notifications import notify_hai_discord
        notify_hai_discord.delay(str(item_id))
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            '[HAI_DISCORD] failed to enqueue notify_hai_discord for %s '
            '(%s: %s); HAI write unaffected',
            item_id, type(e).__name__, e,
        )


@receiver(post_save, sender='core.HumanAttentionItem')
def on_hai_discord_dispatch(sender, instance, created, **kwargs):
    """Enqueue a Discord alert for critical HAI items on transaction commit.

    Fast synchronous guards here (kill switch, created, urgency floor,
    discord_sent flag) so we do not enqueue Celery tasks for HAIs that
    will obviously be skipped. Preference gates are re-checked inside
    the task against the committed row so a stale in-flight receiver
    snapshot cannot fire an alert the current DB state would suppress.
    """
    if not getattr(settings, 'HAI_DISCORD_DISPATCH_ENABLED', True):
        return
    if not created:
        return
    urgency = getattr(instance, 'urgency', None) or ''
    if urgency != 'critical':
        return
    payload = getattr(instance, 'payload', None) or {}
    if payload.get('discord_sent') is True:
        logger.info(
            '[HAI_DISCORD] skip enqueue source_type=%s source_id=%s — '
            'producer flagged discord_sent=True',
            getattr(instance, 'source_type', ''),
            getattr(instance, 'source_id', ''),
        )
        return

    item_id = getattr(instance, 'id', None)
    if not item_id:
        return

    transaction.on_commit(lambda: _enqueue_dispatch(item_id))
