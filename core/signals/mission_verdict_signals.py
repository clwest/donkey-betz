"""
Mission verdict broadcast signals — Session 2734
================================================

Capability Chain §1 wire-up: when a MissionRunner run completes and
``emit_mission_verdict()`` writes an ``OpsRunEvent(label='verdict_issued:*')``,
broadcast a ``mission_verdict`` event to the ``system_events`` WebSocket
group so the Frontend Command Center NowHub refreshes without waiting
for the 15s active-work poll.

Chain:
    MissionRunner.run()
    → emit_mission_verdict()
    → OpsRunEvent(label='verdict_issued:*', run__domain='mission')
    → [this receiver, on_commit]
    → SystemEventsConsumer 'system_events' group
    → Frontend NowHub invalidates ['active-work'] query
"""
import logging

from django.db import transaction
from django.db.models.signals import post_save

logger = logging.getLogger(__name__)

_VERDICT_LABEL_PREFIX = "verdict_issued:"


def _broadcast_verdict(mission_id, verdict, run_id, label):
    """Emit a `mission_verdict` system event.

    Called via ``transaction.on_commit`` so a rolled-back OpsRunEvent
    row never triggers a phantom broadcast. Falls back silently if the
    channel layer is not configured (matches ``emit_system_event_sync``
    behaviour).
    """
    try:
        from core.consumers.system_events_consumer import emit_system_event_sync

        emit_system_event_sync(
            "mission_verdict",
            {
                "mission_id": str(mission_id) if mission_id else None,
                "verdict": verdict,
                "run_id": str(run_id) if run_id else None,
                "label": label,
            },
        )
    except Exception as e:  # pragma: no cover — defensive
        logger.warning(
            "[MISSION_VERDICT_BROADCAST] emit failed run_id=%s label=%s (%s: %s)",
            run_id, label, type(e).__name__, e,
        )


def broadcast_mission_verdict(sender, instance, created, **kwargs):
    """Post-save receiver on ``OpsRunEvent``.

    Fires ``mission_verdict`` system event when:
      * the row was newly created (not update);
      * ``label`` begins with ``'verdict_issued:'``;
      * the parent ``OpsRun`` is mission-domain.

    Any other OpsRunEvent (ops-loop, deploy-verify, step_fail on a
    non-verdict label) is ignored. Broadcast is scheduled on commit
    so a rolled-back transaction produces no phantom event.
    """
    if not created:
        return
    label = getattr(instance, "label", "") or ""
    if not label.startswith(_VERDICT_LABEL_PREFIX):
        return

    # Lazy attribute access; parent OpsRun row is guaranteed FK-loaded.
    run = getattr(instance, "run", None)
    if run is None:
        return
    if getattr(run, "domain", None) != "mission":
        # Only mission-domain runs carry mission verdicts. Skip
        # ops-domain rows even if they happen to reuse the label
        # prefix (defensive).
        return

    verdict = label[len(_VERDICT_LABEL_PREFIX):]
    mission_id = getattr(run, "mission_id", None)
    run_id = getattr(run, "id", None)

    transaction.on_commit(
        lambda: _broadcast_verdict(mission_id, verdict, run_id, label)
    )


def connect_mission_verdict_signals():
    """Wire the OpsRunEvent post_save receiver.

    Registered from ``core/apps.py::CoreConfig._register_signals`` at
    Django startup. Idempotent — Django dispatcher deduplicates
    identical (receiver, sender) pairs.
    """
    from core.models_ops_runs import OpsRunEvent
    post_save.connect(
        broadcast_mission_verdict,
        sender=OpsRunEvent,
        dispatch_uid="core.signals.mission_verdict_signals.broadcast_mission_verdict",
    )
    logger.info(
        "[MISSION_VERDICT_SIGNALS] receiver wired on OpsRunEvent.post_save"
    )
