"""Initiative no-orphan diagnostic signals — Session 1196 PR #2.

Post-save signal that marks newly-created Initiative rows ``diagnostic``
when they land without a ``target_workspace_id``. Mirrors Plan C Phase 1
``deliverable_factory.create_deliverable`` shape (Session 1195 PR #2403):
never block the write, label + TTL only, the daily sweep retires the row
once TTL passes.

Design (ratified by Rigby in pa-ea12236c83eb4826):

1. **Narrow trigger condition** — fires on ``created=True`` only. No
   side effects on normal updates beyond the explicit auto-clear that
   ships in PR #3.
2. **Kill switch + observability** — ``INITIATIVE_DIAGNOSTICS_ENABLED``
   setting controls the field mutation; the ``[ORPHAN-INITIATIVE]``
   warn-log fires regardless so we keep visibility when the switch is off.
3. **Stable warn-log schema** — ``initiative_id``, ``created_by``,
   ``callsite_hint``, ``diagnostic_code``, ``status``, ``expires_at``.
   Locked so downstream parsers + dashboards don't break.

Spec: ``docs/specs/INITIATIVES_FIRST_BACKBONE.md`` §3.C / §6.1.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _is_enabled() -> bool:
    """``INITIATIVE_DIAGNOSTICS_ENABLED`` setting check. Defaults True."""
    return bool(getattr(settings, 'INITIATIVE_DIAGNOSTICS_ENABLED', True))


def mark_initiative_diagnostic_on_create(sender, instance, created, **kwargs):
    """Post-save handler — marks newly created Initiative rows
    diagnostic when ``target_workspace_id`` is NULL.

    Never raises (signal handlers should not break create paths).
    The mutation runs only when ``INITIATIVE_DIAGNOSTICS_ENABLED`` is
    True; the warn-log fires regardless so we don't lose visibility
    when ops disables the switch in emergencies.
    """
    if not created:
        return
    try:
        from core.services.initiative_diagnostics import (
            evaluate_initiative_workspace_alignment,
            mark_initiative_diagnostic,
            DIAGNOSTIC_FIELDS,
        )
        diag_eval = evaluate_initiative_workspace_alignment(instance)
        if diag_eval is None:
            return

        code, payload_extras = diag_eval

        # Warn-log fires regardless of the kill switch — visibility is
        # the floor; only mutation is gated. Schema locked per Rigby's
        # PR #2 nit (don't drift the log shape).
        ttl_hours = getattr(settings, 'INITIATIVE_DIAGNOSTIC_TTL_HOURS', 168)
        logger.warning(
            "[ORPHAN-INITIATIVE] code=%s initiative_id=%s created_by=%s "
            "callsite_hint=%s status=%s ttl_hours=%s enabled=%s",
            code,
            str(instance.id),
            payload_extras.get('created_by') or '-',
            payload_extras.get('callsite_hint') or '-',
            payload_extras.get('status_at_mark') or '-',
            ttl_hours,
            _is_enabled(),
        )

        if not _is_enabled():
            return

        mark_initiative_diagnostic(instance, code, payload_extras)
        # update_fields keeps the write tight + dodges signal-storm
        # recursion (post_save with update_fields=DIAGNOSTIC_FIELDS
        # cannot itself re-trigger a created=True branch).
        instance.save(update_fields=list(DIAGNOSTIC_FIELDS))
    except Exception as _e:
        # Signal handler must never break the create path. Log and move on.
        logger.exception(
            "[ORPHAN-INITIATIVE] mark_initiative_diagnostic_on_create "
            "swallowed (%s: %s) — initiative_id=%s",
            type(_e).__name__, _e, getattr(instance, 'id', 'unknown'),
        )


def connect_initiative_diagnostic_signals() -> None:
    """Wire the post_save signal in core.apps.CoreConfig.ready()."""
    from core.models_document_registry import Initiative
    post_save.connect(
        mark_initiative_diagnostic_on_create,
        sender=Initiative,
        dispatch_uid='session_1196_initiative_diagnostic_post_save',
    )
    logger.debug("[initiative_diagnostic_signals] connected")
