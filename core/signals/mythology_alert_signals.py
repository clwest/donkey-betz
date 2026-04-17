"""
Mythology alert → HumanAttentionItem bridge — Session 1095 Tier 1b.
====================================================================

When a `MythologyAlert` of severity `critical` or `high` is created,
surface it into the governance inbox as a `HumanAttentionItem`. Closes
the operator-visibility gap found in the Session 1095 mythology audit —
312 critical alerts had been sitting unacknowledged because nobody was
looking at /mythology-lab directly.

## Why signal instead of inline bridge call

The MythologyDetectionService has many creation paths (direct DB
writes, test fixtures, management commands, imports). Signal receivers
catch all of them without editing every writer.

## Why severity >= high only

Low/medium mythology alerts are too noisy to funnel into the governance
inbox (would be hundreds per day on a healthy platform). The inbox is
for things the operator needs to see — critical/high clear that bar.

## Failure posture

Signal must never break a MythologyAlert save. Any bridge exception is
logged and swallowed — the mythology record still persists, just
without the governance notification.
"""
import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


# Map mythology severity → HAI urgency (1:1 on these two levels)
_BRIDGED_SEVERITIES = {'critical', 'high'}


@receiver(post_save, sender='mythology.MythologyAlert')
def bridge_mythology_alert_to_hai(sender, instance, created, **kwargs):
    """Fire on new MythologyAlert creation for critical/high severity.

    Updates to existing alerts (acknowledgement, etc.) intentionally do
    NOT re-fire — one HAI per MythologyAlert.
    """
    if not created:
        return
    severity = (instance.severity or '').lower()
    if severity not in _BRIDGED_SEVERITIES:
        return

    try:
        from core.services.human_attention_bridge import attention_bridge
    except Exception as e:
        logger.debug(
            '[mythology_alert_signal] attention_bridge import failed (%s: %s) — '
            'HAI bridge skipped for MythologyAlert %s',
            type(e).__name__, e, instance.pk,
        )
        return

    # Build a concise summary — if the alert already has a description,
    # prefix it with the title for the inbox context; otherwise fall back
    # to just the title.
    title = (instance.title or 'Mythology Alert')[:200]
    description = (instance.description or '') or title

    # Payload carries provenance so the operator can jump back to the
    # full alert + source event.
    payload = {
        'mythology_alert_id': str(instance.pk),
        'mythology_event_id': (
            str(instance.mythology_event_id)
            if getattr(instance, 'mythology_event_id', None) else None
        ),
        'alert_type': instance.alert_type,
        'severity': severity,
        'source_data': instance.data or {},
    }

    try:
        attention_bridge.create_mythology_alert(
            mythology_alert_id=instance.pk,
            alert_type=instance.alert_type,
            title=title,
            summary=description,
            urgency=severity,
            payload=payload,
        )
    except Exception as e:
        # Never break the mythology save path.
        logger.warning(
            '[mythology_alert_signal] HAI bridge failed for alert %s '
            '(%s: %s) — mythology record saved, governance notify skipped',
            instance.pk, type(e).__name__, e,
        )


def connect_mythology_alert_signals():
    """Explicit connection point for apps.py (matches pattern of
    deliverable_status_signals, dream_signals, etc.).
    The @receiver decorator already binds at import time — this function
    exists for naming in the apps.py wiring.
    """
    logger.debug('[mythology_alert_signal] signals connected')
