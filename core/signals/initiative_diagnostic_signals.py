"""Initiative no-orphan diagnostic signals — Session 1196.

Two responsibilities:

1. **PR #2 — Mark on create.** ``post_save`` handler with ``created=True``
   marks Initiative rows ``diagnostic`` when ``target_workspace_id`` is
   NULL. Mirrors Plan C Phase 1 ``deliverable_factory.create_deliverable``
   shape (Session 1195 PR #2403): never block the write, label + TTL
   only, the daily sweep retires the row once TTL passes.
2. **PR #3 — Auto-clear on transition.** ``pre_save`` stashes the prior
   ``target_workspace_id``; ``post_save`` (with ``created=False``)
   detects the NULL → set transition and clears all 5 diagnostic_*
   fields via ``QuerySet.update()`` to dodge recursion. Independent of
   the create-mark handler — gated separately on transition.

Design (ratified by Rigby in pa-ea12236c83eb4826):

1. **Narrow trigger** — create-mark only on ``created=True``; clear
   only on ``old_ws is None and new_ws is not None``. No double-fire.
2. **Kill switch + observability** — ``INITIATIVE_DIAGNOSTICS_ENABLED``
   setting controls the create-path mutation; the ``[ORPHAN-INITIATIVE]``
   warn-log fires regardless so we keep visibility when the switch is
   off. Auto-clear ignores the switch (clearing a stale diagnostic when
   the row resolves is always safe).
3. **Stable warn-log schema** — ``initiative_id``, ``created_by``,
   ``callsite_hint``, ``diagnostic_code``, ``status``, ``expires_at``.
4. **No save recursion** — auto-clear uses
   ``Initiative.objects.filter(pk=...).update(...)`` per Rigby's PR #3
   guardrail #1, NOT ``instance.save()``.

Spec: ``docs/specs/INITIATIVES_FIRST_BACKBONE.md`` §3.C / §6.1.
"""

from __future__ import annotations

import logging

from django.conf import settings
from django.db.models.signals import post_save, pre_save
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


def stash_prior_target_workspace_id(sender, instance, **kwargs):
    """Pre-save snapshot of ``target_workspace_id`` for transition
    detection in ``clear_initiative_diagnostic_on_workspace_set``.

    Stashes onto ``instance._prior_target_workspace_id``. New rows (no
    pk yet) get ``None``. DB-fetch failures fall back to ``None`` and
    log at DEBUG — the post_save clear path then treats the transition
    as undetectable and no-ops, which is the safe default (worst case:
    a stale diagnostic stays until the next legitimate update).

    Mirrors ``deliverable_status_signals.stash_prior_status`` (Session
    1095).
    """
    if not instance.pk:
        instance._prior_target_workspace_id = None
        return
    try:
        old = sender.objects.only('target_workspace_id').get(pk=instance.pk)
        instance._prior_target_workspace_id = old.target_workspace_id
    except sender.DoesNotExist:
        instance._prior_target_workspace_id = None
    except Exception as e:
        logger.debug(
            '[initiative_diagnostic_signals] pre_save prior-ws fetch '
            'failed (%s: %s) — clear path will skip this save',
            type(e).__name__, e,
        )
        instance._prior_target_workspace_id = None


def clear_initiative_diagnostic_on_workspace_set(
    sender, instance, created, update_fields=None, **kwargs,
):
    """Post-save handler — clears diagnostic_* fields when
    ``target_workspace_id`` transitions from NULL to set.

    Guardrails (Rigby's PR #3 review):
    1. ``QuerySet.update()`` instead of ``instance.save()`` — no recursion.
    2. Gate strictly on ``old is None and new is not None``.
    3. Early-return if ``update_fields`` is set + doesn't include
       ``target_workspace_id`` (caller couldn't have changed it).
    4. No-op if nothing to clear (``clear_initiative_diagnostic()``
       returns False when ``diagnostic_status`` is already NULL).
    5. Independent of the create handler: ``if created: return``.

    Never raises — clearing a diagnostic is safe-by-default; failures
    fall through and the daily sweep eventually retires the row anyway.
    """
    if created:
        return
    if update_fields is not None and 'target_workspace_id' not in update_fields:
        return
    try:
        old_ws = getattr(instance, '_prior_target_workspace_id', None)
        new_ws = instance.target_workspace_id
        # Transition guard: only act on NULL → set.
        if not (old_ws is None and new_ws is not None):
            return
        from core.services.initiative_diagnostics import (
            clear_initiative_diagnostic,
            DIAGNOSTIC_FIELDS,
        )
        # Helper returns False when diagnostic_status was already NULL;
        # acts as the "nothing to clear" guard per Rigby's nit #3.
        cleared = clear_initiative_diagnostic(instance)
        if not cleared:
            return
        # Persist via .update() — bypasses save() so we don't re-enter
        # the post_save dispatch. Mirror the helper's NULL semantics
        # column-by-column to avoid drift.
        sender.objects.filter(pk=instance.pk).update(
            diagnostic_status=None,
            diagnostic_code=None,
            diagnostic_payload=None,
            diagnostic_marked_at=None,
            diagnostic_expires_at=None,
        )
        logger.info(
            "[INITIATIVE-DIAGNOSTIC-CLEARED] initiative_id=%s "
            "old_ws=%s new_ws=%s",
            str(instance.id),
            'null',
            str(new_ws),
        )
    except Exception as _e:
        logger.exception(
            "[INITIATIVE-DIAGNOSTIC-CLEARED] auto-clear swallowed "
            "(%s: %s) — initiative_id=%s",
            type(_e).__name__, _e, getattr(instance, 'id', 'unknown'),
        )


def connect_initiative_diagnostic_signals() -> None:
    """Wire the create-mark + auto-clear signals in
    ``core.apps.CoreConfig.ready()``.

    Three handlers, three distinct dispatch_uids — keeps each
    independently disablable for debugging.
    """
    from core.models_document_registry import Initiative

    # PR #2: post_save create-mark
    post_save.connect(
        mark_initiative_diagnostic_on_create,
        sender=Initiative,
        dispatch_uid='session_1196_initiative_diagnostic_post_save',
    )
    # PR #3: pre_save stash + post_save auto-clear
    pre_save.connect(
        stash_prior_target_workspace_id,
        sender=Initiative,
        dispatch_uid='session_1196_initiative_diagnostic_pre_save_stash',
    )
    post_save.connect(
        clear_initiative_diagnostic_on_workspace_set,
        sender=Initiative,
        dispatch_uid='session_1196_initiative_diagnostic_post_save_clear',
    )
    logger.debug("[initiative_diagnostic_signals] connected (mark + auto-clear)")
