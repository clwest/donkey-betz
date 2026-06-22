"""Session 1196 — Plan C side-quest helpers for the Initiative no-orphan contract.

Mirrors ``core/services/deliverable_factory.py`` Plan C Phase 1 helpers
(``_evaluate_initiative_alignment`` + ``_resolve_caller_fingerprint``)
but targets the Initiative ``target_workspace_id`` write-path enforcement.

Public API:

- ``evaluate_initiative_workspace_alignment(initiative)`` — returns
  ``('missing_target_workspace_id', payload_extras)`` when the
  Initiative has no ``target_workspace_id``, else ``None``. Never raises.
- ``mark_initiative_diagnostic(initiative, code, payload_extras)`` —
  sets the 5 diagnostic fields on the row (no save; caller persists).
- ``clear_initiative_diagnostic(initiative)`` — clears all 5 fields
  back to NULL (used by PR #3 auto-clear once target_workspace_id is set).
- ``resolve_initiative_caller_fingerprint()`` — walks the stack past
  the Django ORM + signal plumbing and returns a
  ``<short_filename>:<lineno>:<funcname>`` string. Same shape as
  Phase 1's helper but with Initiative-specific skip-frames.

Spec: ``docs/specs/INITIATIVES_FIRST_BACKBONE.md`` §3.C / §6.1.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Optional, Tuple

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


# Frames inside these files are plumbing, not real callers.
# Keep the list narrow — over-skipping risks reporting 'unknown'.
# ``core/models_document_registry.py`` is here because Initiative.save()
# (lines ~472-488) is custom + always sits between Manager.create() and
# the post_save dispatch; without skipping it the fingerprint always
# lands at ``models_document_registry.py:save`` instead of the real
# caller (e.g., td_handlers_content.py:2524 PA path).
_CALLER_SKIP_FILES = (
    'core/services/initiative_diagnostics.py',
    'core/signals/initiative_diagnostic_signals.py',
    'core/models_document_registry.py',
    'django/db/models/',
    'django/dispatch/',
)


def resolve_initiative_caller_fingerprint() -> str:
    """Return ``<short_filename>:<lineno>:<funcname>`` for the first
    stack frame outside the Initiative diagnostic plumbing + Django ORM.

    Returns ``'unknown'`` when the stack can't be walked (rare —
    happens in odd async contexts).
    """
    try:
        import sys
        frame = sys._getframe(1)
        while frame is not None:
            fname = frame.f_code.co_filename
            if not any(skip in fname for skip in _CALLER_SKIP_FILES):
                short = fname.rsplit('/unified-donkey-betz/', 1)[-1]
                return f"{short}:{frame.f_lineno}:{frame.f_code.co_name}"
            frame = frame.f_back
        return 'unknown'
    except Exception:
        return 'unknown'


def evaluate_initiative_workspace_alignment(
    initiative,
) -> Optional[Tuple[str, dict]]:
    """Return ``('missing_target_workspace_id', payload_extras)`` when
    the Initiative has no ``target_workspace_id``, else ``None``.

    Never raises — alignment-check failure must never block an
    Initiative write. On unexpected error, logs and returns None so
    the create path proceeds without a diagnostic mark.

    ``payload_extras`` carries the structured detail that will land
    in ``diagnostic_payload``: created_by, callsite_hint, status_at_mark,
    plus marked_at and ttl_hours added by the caller.
    """
    try:
        target_ws = getattr(initiative, 'target_workspace_id', None)
        if target_ws is not None:
            return None
        payload_extras = {
            'created_by': getattr(initiative, 'created_by', '') or '',
            'callsite_hint': resolve_initiative_caller_fingerprint(),
            'status_at_mark': getattr(initiative, 'status', '') or '',
        }
        return ('missing_target_workspace_id', payload_extras)
    except Exception as _e:
        logger.exception(
            "[initiative_diagnostics] evaluate_initiative_workspace_alignment "
            "failed (%s: %s) — skipping diagnostic mark",
            type(_e).__name__, _e,
        )
        return None


def mark_initiative_diagnostic(
    initiative,
    code: str,
    payload_extras: dict,
) -> None:
    """Set the 5 diagnostic_* fields on ``initiative`` in-place.

    Caller is responsible for persisting via ``initiative.save(update_fields=...)``
    or letting the post_save signal handler write back the fields it set.
    Does not touch ``initiative.status`` — the canonical lifecycle field stays
    the owner; the daily sweep flips status='ARCHIVED' once TTL passes.

    TTL is controlled by ``INITIATIVE_DIAGNOSTIC_TTL_HOURS`` setting
    (default 168 = 7 days, same as Plan C).
    """
    ttl_hours = getattr(settings, 'INITIATIVE_DIAGNOSTIC_TTL_HOURS', 168)
    now = timezone.now()
    initiative.diagnostic_status = 'diagnostic'
    initiative.diagnostic_code = code
    initiative.diagnostic_marked_at = now
    initiative.diagnostic_expires_at = now + timedelta(hours=ttl_hours)
    initiative.diagnostic_payload = {
        **payload_extras,
        'marked_at': now.isoformat(),
        'ttl_hours': ttl_hours,
    }


def clear_initiative_diagnostic(initiative) -> bool:
    """Clear all 5 diagnostic_* fields on ``initiative`` in-place.

    Returns True when fields were actually cleared (i.e. the row was
    previously marked diagnostic), False when it was already NULL.
    Caller is responsible for persisting.

    Used by PR #3 auto-clear path: when ``target_workspace_id`` transitions
    from NULL to set, the Initiative is no longer in violation and the
    diagnostic annotation should retire.
    """
    if initiative.diagnostic_status is None:
        return False
    initiative.diagnostic_status = None
    initiative.diagnostic_code = None
    initiative.diagnostic_payload = None
    initiative.diagnostic_marked_at = None
    initiative.diagnostic_expires_at = None
    return True


DIAGNOSTIC_FIELDS = (
    'diagnostic_status',
    'diagnostic_code',
    'diagnostic_payload',
    'diagnostic_marked_at',
    'diagnostic_expires_at',
)
