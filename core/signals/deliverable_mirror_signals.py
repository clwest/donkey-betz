"""Cycle 1A KFI-1 (ADR-0110) — Deliverable → Document mirror signal.

Strict live signal (F2 Option D refined, Chris directive 2026-07-08):
fires only on freshly created ratification_record Deliverables. Historical
document-typed RATIFICATION_* records are handled by the management
command, not this signal.

Signal registration uses ``dispatch_uid`` (A12) to guard against
duplicate receivers under Django autoreload / test setup where
``AppConfig.ready()`` runs multiple times.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

_DISPATCH_UID = 'deliverable_mirror_post_save'


def connect_deliverable_mirror_signals():
    """Wire the mirror signal receiver. Called from ``core.apps.ready()``.

    Idempotent via ``dispatch_uid``: repeated invocation registers the
    receiver exactly once.
    """
    from core.models import Deliverable

    @receiver(
        post_save,
        sender=Deliverable,
        dispatch_uid=_DISPATCH_UID,
    )
    def on_ratification_record_created(sender, instance, created, **kwargs):
        if not created:
            return
        if getattr(instance, 'deliverable_type', None) != 'ratification_record':
            return
        # Deferred import to avoid Django app-loading cycles.
        from core.tasks import mirror_deliverable_to_document

        mirror_deliverable_to_document.delay(
            ratification_record_id=str(instance.id),
        )

    logger.debug('[deliverable_mirror] signal receiver connected')
