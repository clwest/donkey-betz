"""
Mission-verdict → HAI signals — Session 2734 (Platform Closure Category B)
==========================================================================

Category B closure of Capability Chain §1 Item 9 HAI production. Producer
(``OpsRunEvent`` with ``label.startswith('verdict_issued:')`` on a
mission-domain run) and consumer (``HumanAttentionBridge``) both exist
at HEAD; this file adds the missing edge.

Chain:
    MissionRunner.run()
    → emit_mission_verdict(verdict='rejected' | 'deferred')
    → OpsRunEvent(label='verdict_issued:*', run.domain='mission')
    → [this receiver, on_commit]
    → HumanAttentionBridge.create_mission_verdict_attention(run, verdict)
    → HumanInterfaceService.create_attention_item(source_type='mission_verdict')
    → HumanAttentionItem row (inbox visible immediately)

Filtering contract:
    * Only ``rejected`` and ``deferred`` verdicts escalate. ``certified``
      is success — no HAI needed.
    * Mission-domain runs only. Ops-loop / smoke-test / deploy-verify
      runs never carry the mission-verdict semantic.
    * ``created=True`` — updates to existing rows do not re-fire.

Urgency policy (per Rigby SIGN pa-47bd5d75158948f5):
    Delegated to the bridge method: 'rejected' → 'high', 'deferred'
    → 'medium'. Explicitly NOT 'critical' so we do not cascade into
    Expo push (avoids double-alerting when another escalation for the
    same underlying incident already fired).

Kill switch:
    ``settings.MISSION_VERDICT_HAI_ENABLED`` (default True).

Coexistence note:
    This receiver runs alongside the pre-existing
    ``broadcast_mission_verdict`` receiver (S2734 §1) via a distinct
    ``dispatch_uid``. Both fire on the same ``OpsRunEvent`` post_save
    but perform independent work — WS broadcast for Frontend refresh
    vs HAI for human decision surface.
"""
import logging

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save

logger = logging.getLogger(__name__)

_VERDICT_LABEL_PREFIX = "verdict_issued:"
_ESCALATE_VERDICTS = frozenset({'rejected', 'deferred'})


def _create_attention(run, verdict):
    """Dispatch to the HumanAttentionBridge on-commit."""
    try:
        from core.services.human_attention_bridge import attention_bridge
        attention_bridge.create_mission_verdict_attention(run, verdict)
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            "[MISSION_VERDICT_HAI] bridge dispatch failed "
            "run_id=%s verdict=%s (%s: %s)",
            getattr(run, 'id', None), verdict, type(e).__name__, e,
        )


def escalate_mission_verdict_to_hai(sender, instance, created, **kwargs):
    """Post-save receiver on ``OpsRunEvent``.

    Escalates to HAI when:
      * kill switch is not tripped;
      * the row was newly created;
      * ``label.startswith('verdict_issued:')``;
      * parent ``OpsRun.domain == 'mission'``;
      * verdict is one of ``rejected`` / ``deferred``.

    Broadcast is scheduled via ``transaction.on_commit`` so a
    rolled-back OpsRunEvent produces no phantom HAI.
    """
    if not getattr(settings, 'MISSION_VERDICT_HAI_ENABLED', True):
        return
    if not created:
        return
    label = getattr(instance, "label", "") or ""
    if not label.startswith(_VERDICT_LABEL_PREFIX):
        return

    run = getattr(instance, "run", None)
    if run is None:
        return
    if getattr(run, "domain", None) != "mission":
        return

    verdict = label[len(_VERDICT_LABEL_PREFIX):].lower()
    if verdict not in _ESCALATE_VERDICTS:
        return

    transaction.on_commit(lambda: _create_attention(run, verdict))


def connect_mission_verdict_attention_signals():
    """Wire the OpsRunEvent post_save receiver for HAI escalation.

    Idempotent via ``dispatch_uid`` — distinct from the WS-broadcast
    receiver's uid so both coexist on the same signal.
    """
    from core.models_ops_runs import OpsRunEvent
    post_save.connect(
        escalate_mission_verdict_to_hai,
        sender=OpsRunEvent,
        dispatch_uid=(
            "core.signals.mission_verdict_attention_signals"
            ".escalate_mission_verdict_to_hai"
        ),
    )
    logger.info(
        "[MISSION_VERDICT_HAI_SIGNALS] receiver wired on "
        "OpsRunEvent.post_save (escalate verdicts: %s)",
        sorted(_ESCALATE_VERDICTS),
    )
