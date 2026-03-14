"""
Ops Autopilot — Stub module.

The original implementation was removed but the Celery beat task
still references it. This stub prevents NameError crashes.
"""

import logging

logger = logging.getLogger(__name__)


class OpsAutopilot:
    """Stub autopilot — returns no actions."""

    def run(self):
        logger.debug("[OpsAutopilot] Stub — no actions configured")
        return {"actions_taken": 0, "actions": []}
