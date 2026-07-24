"""
Signal dispatch task impls — Session 2933 A3 v1.

Thin `_impl_*` layer called from ``core.tasks``. Keeps the wrapper in
``core.tasks`` (@shared_task) minimal so autodiscovery + inspection stay
predictable; real logic lives here.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def _impl_scan_signal_dispatch(self):
    """Periodic scanner impl. Called by ``core.tasks.scan_signal_dispatch_rules``."""
    from core.services.signal_dispatch_service import SignalDispatchService

    service = SignalDispatchService()
    summary = service.scan_and_dispatch()
    logger.info("[SIGNAL_DISPATCH_SCAN] summary=%s", summary)
    return summary


def _impl_dispatch_agent_for_signal_cluster(self, dispatch_id: str):
    """Per-dispatch agent execution. Called by ``core.tasks.dispatch_agent_for_signal_cluster``."""
    from core.services.signal_dispatch_service import SignalDispatchService

    service = SignalDispatchService()
    try:
        result = service.execute_dispatch(dispatch_id)
    except Exception as e:
        logger.exception(
            "[SIGNAL_DISPATCH_DISPATCH] unhandled error dispatch_id=%s: %s",
            dispatch_id, e,
        )
        raise
    logger.info(
        "[SIGNAL_DISPATCH_DISPATCH] dispatch_id=%s outcome=%s",
        dispatch_id, result.get('outcome'),
    )
    return result
