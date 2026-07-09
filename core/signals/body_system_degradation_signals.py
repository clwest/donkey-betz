"""
Body-system degradation → HAI signals — Session 2734
=====================================================

Capability Chain §14 wire-up: when ``BodyCoordinator``'s 10-minute
health scan writes a ``HeartBeat`` with ``overall_status`` of
``critical`` or ``offline``, automatically create a
``HumanAttentionItem`` so a wake-someone-up degradation escalates to
the human inbox within seconds instead of relying on Discord alerts
alone (per ``core/services/heart.py:690``).

Chain:
    BodyCoordinator every-10-min scan
    → HeartBeat.save(overall_status='critical' | 'offline')
    → [this receiver, on_commit]
    → HumanAttentionBridge.create_body_system_degradation_attention(heartbeat)
    → HumanInterfaceService.create_attention_item(source_type='body_system_degradation')
    → HumanAttentionItem row

Filtering contract:
    * Only ``critical`` and ``offline`` escalate. ``degraded`` is
      deliberately excluded — audit §2.2 flagged the 6 existing
      HeartBeat readers as status-display + Discord-alert-only; the
      inbox must not accept every non-healthy pulse (~1 write per 10
      min → ~144/day) or the attention stream becomes noise.
    * Dedup: skip if any open (undecided) HAI with the same
      ``source_type`` was created in the last hour. Prevents 6
      identical HAI rows when a critical state persists across an
      hour of 10-min scans.

Kill switch:
    ``settings.BODY_SYSTEM_DEGRADATION_HAI_ENABLED`` (default True).
"""
import logging
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.utils import timezone

logger = logging.getLogger(__name__)

_ESCALATE_STATUSES = frozenset({'critical', 'offline'})
_DEDUP_WINDOW = timedelta(hours=1)


def _open_hai_exists_within_window() -> bool:
    """True if an undecided body-system HAI was created in the last hour.

    Fails safe to ``False`` on any error so that a broken lookup does
    NOT suppress escalation of a genuinely critical state — it is
    safer to duplicate an HAI than to swallow a critical alert.
    """
    try:
        from core.models_human_interface import HumanAttentionItem
        cutoff = timezone.now() - _DEDUP_WINDOW
        return HumanAttentionItem.objects.filter(
            source_type='body_system_degradation',
            decided_at__isnull=True,
            created_at__gte=cutoff,
        ).exists()
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            "[BODY_SYSTEM_DEGRADATION] dedup lookup failed "
            "(%s: %s); allowing escalation",
            type(e).__name__, e,
        )
        return False


def _create_attention(heartbeat):
    """Dispatch to the HumanAttentionBridge on-commit."""
    try:
        from core.services.human_attention_bridge import attention_bridge
        attention_bridge.create_body_system_degradation_attention(heartbeat)
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            "[BODY_SYSTEM_DEGRADATION] bridge dispatch failed "
            "heartbeat_id=%s (%s: %s)",
            getattr(heartbeat, 'id', None), type(e).__name__, e,
        )


def escalate_body_system_degradation(sender, instance, created, **kwargs):
    """Post-save receiver on ``HeartBeat``.

    Escalates to HAI when:
      * the row was newly created (not update — HeartBeat rows are
        immutable in practice but the guard is defensive);
      * ``overall_status in {'critical', 'offline'}``;
      * kill switch is not tripped;
      * no open (undecided) body-system HAI exists within the last hour.

    Escalation is scheduled via ``transaction.on_commit`` so a
    rolled-back HeartBeat produces no phantom HAI.
    """
    if not getattr(settings, 'BODY_SYSTEM_DEGRADATION_HAI_ENABLED', True):
        return
    if not created:
        return
    overall_status = getattr(instance, 'overall_status', None) or ''
    if overall_status not in _ESCALATE_STATUSES:
        return
    if _open_hai_exists_within_window():
        logger.info(
            "[BODY_SYSTEM_DEGRADATION] dedup suppressed heartbeat_id=%s "
            "status=%s (open HAI already present in last hour)",
            instance.id, overall_status,
        )
        return

    transaction.on_commit(lambda: _create_attention(instance))


def connect_body_system_degradation_signals():
    """Wire the HeartBeat post_save receiver.

    Registered from ``core/apps.py::CoreConfig._register_signals`` at
    Django startup. Idempotent via ``dispatch_uid``.
    """
    from core.models_heart import HeartBeat
    post_save.connect(
        escalate_body_system_degradation,
        sender=HeartBeat,
        dispatch_uid=(
            "core.signals.body_system_degradation_signals"
            ".escalate_body_system_degradation"
        ),
    )
    logger.info(
        "[BODY_SYSTEM_DEGRADATION_SIGNALS] receiver wired on "
        "HeartBeat.post_save (escalate statuses: %s)",
        sorted(_ESCALATE_STATUSES),
    )
