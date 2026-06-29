"""
Deliverable status-transition signals — Session 1095
====================================================

Captures Deliverable.status transitions as `DeliverableEvent` rows so the
COO rework/bounce gate (Rigby's priority-#1 future gate) can measure
"moving fast but leaking quality" signal without a new table.

Why `DeliverableEvent` (not a new model)?
  - Already exists, already has `metadata` JSONField
  - Already has indexed `event_type` + `created_at` for cheap queries
  - Existing `EVENT_TYPES` gets one new value: `'status_transition'`

What counts as "rework/backward"?
  - `ready → draft`        (reviewer bounced the draft)
  - `ready → blocked`      (got flagged during review)
  - `published → ready`    (unpublished for edits — rare)
  - any status → `rejected` / `blocked`  (explicit regression)

What's NOT rework:
  - `ready → published`       (forward)
  - `ready → archived`        (discarded — terminal, not rework)
  - `published → archived`    (retired — terminal, not rework)
  - same status               (noise from bulk updates / resaves)
"""
import logging

from django.conf import settings
from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _enqueue_rigby_intake(event_ref: str, deliverable_id) -> None:
    """Enqueue the Rigby Event Intake task for a status_transition event.

    Session 1250 PR 5: gated by ``settings.RIGBY_EVENT_INTAKE_ENABLED``
    (default False). When False, this function is a no-op. When True,
    the intake task is enqueued with ``dry_run=True``; PR 6 will be
    the first PR allowed to flip dry_run.

    Called via ``transaction.on_commit`` so we never enqueue a task
    that references a row that was rolled back.
    """
    if not getattr(settings, 'RIGBY_EVENT_INTAKE_ENABLED', False):
        return
    # Lazy import keeps signal-module import cheap and avoids any
    # circular-import risk between core.services.* and core.signals.*.
    from core.services.rigby_event_intake import rigby_event_intake

    try:
        async_result = rigby_event_intake.apply_async(
            args=[event_ref],
            kwargs={'dry_run': True},
        )
        task_id = getattr(async_result, 'id', None)
        logger.info(
            '[RIGBY_INTAKE_SUBSCRIBE] enqueued event_ref=%s task_id=%s '
            'deliverable_id=%s dry_run=True flag=ON',
            event_ref, task_id, deliverable_id,
        )
    except Exception as e:
        # Never break the deliverable save path. Log + swallow.
        logger.warning(
            '[RIGBY_INTAKE_SUBSCRIBE] enqueue failed for event_ref=%s '
            'deliverable_id=%s (%s: %s)',
            event_ref, deliverable_id, type(e).__name__, e,
        )


# Progress ordering. Higher rank = further along. Terminal statuses
# handled as special cases in the classifier.
_STATUS_ORDER = {
    'draft': 0,
    'ready': 1,
    'completed': 2,
    'published': 2,
}


def classify_transition(old_status: str, new_status: str) -> str:
    """Return one of: 'forward' | 'backward' | 'terminal' | 'same' | 'unknown'.

    - `archived` = terminal retirement, never counted as rework
    - `blocked` / `rejected` = explicit regression, always backward
    - Unknown status values fall back to 'unknown' (conservative — not
      counted as rework so we don't poison the metric with mystery data)
    """
    if not old_status or not new_status:
        return 'unknown'
    if old_status == new_status:
        return 'same'
    if new_status == 'archived':
        return 'terminal'
    if new_status in ('blocked', 'rejected'):
        return 'backward'
    old_rank = _STATUS_ORDER.get(old_status)
    new_rank = _STATUS_ORDER.get(new_status)
    if old_rank is None or new_rank is None:
        return 'unknown'
    if new_rank > old_rank:
        return 'forward'
    if new_rank < old_rank:
        return 'backward'
    return 'same'  # ranks equal but statuses differ (e.g. completed ↔ published)


@receiver(pre_save, sender='core.Deliverable')
def stash_prior_status(sender, instance, **kwargs):
    """Cache the pre-save status on the instance so the post_save receiver
    can classify the transition. Avoids double-querying in post_save.
    """
    if not instance.pk:
        instance._prior_status = None
        return
    try:
        old = sender.objects.only('status').get(pk=instance.pk)
        instance._prior_status = old.status
    except sender.DoesNotExist:
        instance._prior_status = None
    except Exception as e:
        # Defensive: signal must never break a save. Log + mark unknown.
        logger.debug(
            '[deliverable_status] pre_save prior-fetch failed '
            '(%s: %s) — transition will be skipped',
            type(e).__name__, e,
        )
        instance._prior_status = None


@receiver(post_save, sender='core.Deliverable')
def record_status_transition(sender, instance, created, **kwargs):
    """Write a DeliverableEvent row capturing status transitions.

    Silent on:
      - newly-created rows (no prior status to compare)
      - same-status saves (most update_fields=[...] paths)
      - pre_save stash failed

    Session 1227 PR3 — reads an optional ephemeral context dict
    `instance._transition_context` set by callers that want to
    enrich the event row beyond the default `{from, to, direction}`.
    Recognized keys (Session 1252 PR 2 added `ops_run_id` +
    `error_signature` for Docs Manager escalation auditability —
    Rigby's PR 2 sign-off requirement): `reason`, `actor_user_id`,
    `trace_id`, `source`, `ops_run_id`, `error_signature`.
    The context is namespaced under `metadata['ctx']` to avoid
    collisions with the authoritative transition fields, and the
    attribute is removed after consumption so it can't leak to a
    later save on the same instance. `actor_user_id`, when present
    and resolvable, also populates the `DeliverableEvent.user` FK.
    """
    if created:
        return
    prior = getattr(instance, '_prior_status', None)
    if prior is None:
        return
    new = instance.status
    if prior == new:
        return
    direction = classify_transition(prior, new)
    if direction in ('same', 'unknown'):
        return

    # Session 1227 PR3 — consume ephemeral context (delete after read).
    ctx = getattr(instance, '_transition_context', None) or {}
    try:
        delattr(instance, '_transition_context')
    except AttributeError:
        pass

    metadata = {
        'from': prior,
        'to': new,
        'direction': direction,
    }
    if ctx:
        # Namespace under 'ctx' so the {from, to, direction} authoritative
        # fields can't collide with caller-supplied keys.
        # Session 1252 PR 2: added ``ops_run_id`` + ``error_signature``
        # to the whitelist so the Docs Manager escalation flow can
        # attach run + dedupe-signature pointers to the audit row.
        # Rigby's PR 2 sign-off required these as queryable evidence
        # fields, not just human-readable reason text.
        metadata['ctx'] = {
            k: v for k, v in ctx.items()
            if k in (
                'reason',
                'actor_user_id',
                'trace_id',
                'source',
                'ops_run_id',
                'error_signature',
            )
            and v is not None
        }

    event_user_id = ctx.get('actor_user_id') if ctx else None
    event_source = ctx.get('source') if ctx else None

    try:
        from core.models_deliverables import DeliverableEvent
        de = DeliverableEvent.objects.create(
            deliverable=instance,
            event_type='status_transition',
            source=event_source or 'deliverable_status_signal',
            user_id=event_user_id if event_user_id else None,
            metadata=metadata,
        )
    except Exception as e:
        # Never break a deliverable save. Log and move on.
        logger.warning(
            '[deliverable_status] event log write failed (%s: %s) '
            '— deliverable %s %s→%s transition not tracked',
            type(e).__name__, e, instance.pk, prior, new,
        )
        return

    # Session 1250 PR 5: enqueue Rigby Event Intake on commit. Gated by
    # settings.RIGBY_EVENT_INTAKE_ENABLED (default False). The
    # transaction.on_commit() guard ensures we never enqueue a task
    # whose target DeliverableEvent was rolled back. Inside a
    # ``transaction.atomic`` block that rolls back, the callback is
    # discarded; outside any transaction, the callback fires
    # immediately.
    event_ref = f'deliverable_event:{de.id}'
    deliverable_id = instance.pk
    transaction.on_commit(
        lambda: _enqueue_rigby_intake(event_ref, deliverable_id)
    )


def connect_deliverable_status_signals():
    """Called from AppConfig.ready() to ensure signals are registered.

    The @receiver decorator already registers them at import time — this
    function exists for explicit naming in the apps.py wiring (matches
    pattern of dream_signals, revenue_signals, etc.).
    """
    logger.debug('[deliverable_status] signals connected')
