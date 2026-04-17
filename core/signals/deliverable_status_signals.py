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

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


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

    try:
        from core.models_deliverables import DeliverableEvent
        DeliverableEvent.objects.create(
            deliverable=instance,
            event_type='status_transition',
            source='deliverable_status_signal',
            metadata={
                'from': prior,
                'to': new,
                'direction': direction,
            },
        )
    except Exception as e:
        # Never break a deliverable save. Log and move on.
        logger.warning(
            '[deliverable_status] event log write failed (%s: %s) '
            '— deliverable %s %s→%s transition not tracked',
            type(e).__name__, e, instance.pk, prior, new,
        )


def connect_deliverable_status_signals():
    """Called from AppConfig.ready() to ensure signals are registered.

    The @receiver decorator already registers them at import time — this
    function exists for explicit naming in the apps.py wiring (matches
    pattern of dream_signals, revenue_signals, etc.).
    """
    logger.debug('[deliverable_status] signals connected')
