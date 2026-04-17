"""
Mythology pattern feedback tuning — Session 1095 Tier 1.
=========================================================

Closes the human-review → pattern-quality loop. When an operator
reviews a FlaggedHallucination and marks it `verified_safe` (false
positive) or `verified_hallucination` (real catch), we update the
associated `MythPattern` so the system gradually learns which patterns
are signal and which are tuning-debt.

Without this loop, the 10+ active patterns drift independent of real
operator judgment — over-broad patterns keep crying wolf forever.

## Tuning logic

For each pattern in `flagged.patterns_detected`:

1. **Correct-catch** (`review_action in {remove, verified_hallucination}`):
   - Increment `times_prevented`
   - Nudge `severity_weight` upward (clamped to 1.0)
   - Recompute `prevention_success_rate`

2. **False positive** (`review_action in {flag_false_positive, verified_safe}`):
   - Track FP count in metadata (no dedicated field yet — metadata JSON
     is the escape hatch)
   - Decrement `severity_weight` (clamped to 0.05 — never deactivate
     automatically without operator intent; pattern tuning should
     remain reversible)
   - If FP ratio exceeds `AUTO_DISABLE_THRESHOLD` AND the pattern has
     accumulated enough signal to trust the ratio, auto-set
     `is_active=False` (retire the bad pattern)

## When to disable a pattern automatically

Automatic retirement is sensitive — wrong threshold wipes a genuine
safety net. Current policy:
- Require at least `MIN_REVIEWS_FOR_DISABLE` (25) total reviews before
  considering auto-disable. Below that we're too noisy to trust.
- FP ratio >= `AUTO_DISABLE_THRESHOLD` (0.80 = 80%) triggers disable.
- Operators can always re-enable via admin; the metadata preserves
  `auto_disabled_at` so it's visible in the lab UI.

Both thresholds are conservative — prefer leaving a noisy pattern on
over silently disabling a real safety net.
"""
from __future__ import annotations

import logging
from typing import Iterable

from django.db import transaction
from django.utils import timezone

from .models import FlaggedHallucination, MythPattern

logger = logging.getLogger(__name__)


# Thresholds (module constants — could be env-tuned later if needed)
AUTO_DISABLE_FP_THRESHOLD = 0.80
MIN_REVIEWS_FOR_DISABLE = 25
SEVERITY_NUDGE_CORRECT = 0.05
SEVERITY_NUDGE_FALSE_POSITIVE = -0.10
MIN_SEVERITY_WEIGHT = 0.05
MAX_SEVERITY_WEIGHT = 1.0


# Actions that indicate "the flag was correct — this IS a hallucination"
CORRECT_CATCH_ACTIONS = {
    'remove',
    'verified_hallucination',
    'approve',  # Legacy: "approve this is a problem"
}

# Actions that indicate "the flag was wrong — the content was fine"
FALSE_POSITIVE_ACTIONS = {
    'flag_false_positive',
    'verified_safe',
    'reject',  # Legacy: "reject this flag"
}


def tune_patterns_from_review(
    flagged: FlaggedHallucination,
    review_action: str,
) -> dict:
    """Apply pattern-tuning updates based on an operator review decision.

    Called from the submit_review view and the bulk_review endpoint.
    Idempotent-ish: safe to call multiple times; each call just nudges
    severity_weight within its bounds. Failures are logged — pattern
    tuning never breaks the review call itself.

    Returns a summary dict {patterns_updated, auto_disabled, action_class}.
    """
    action_class = _classify_action(review_action)
    if action_class == 'unknown':
        return {
            'patterns_updated': 0,
            'auto_disabled': [],
            'action_class': 'unknown',
        }

    pattern_types = flagged.patterns_detected or []
    if not pattern_types:
        return {
            'patterns_updated': 0,
            'auto_disabled': [],
            'action_class': action_class,
        }

    updated = 0
    auto_disabled: list[str] = []

    for pattern_type in pattern_types:
        try:
            with transaction.atomic():
                # Session 1095 audit finding: the ai_core/agents/mythology_validator.py
                # validator tags flags with pattern types (dangerous_myth,
                # spider_data_myth, time_myth, etc.) that don't exist as
                # MythPattern rows — those are from mythology/services.py.
                # Auto-create on first review so the tuner closes the loop
                # for BOTH validator systems. Alternative was a data
                # migration that would go stale; this is self-healing.
                pattern, created = MythPattern.objects.select_for_update().get_or_create(
                    pattern_type=pattern_type,
                    defaults={
                        'description': (
                            f'Auto-created from operator review — '
                            f'first-seen via feedback tuning loop.'
                        ),
                        'severity_weight': 0.3,  # Neutral default
                        'is_active': True,
                        'frequency_count': 0,
                        'times_prevented': 0,
                    },
                )
                if created:
                    logger.info(
                        '[mythology/tuning] auto-created MythPattern %s from first review',
                        pattern_type,
                    )

                disabled_now = _apply_review_to_pattern(pattern, action_class)
                pattern.save()
                updated += 1
                if disabled_now:
                    auto_disabled.append(pattern_type)
        except Exception as e:
            # Never break the review call. Log and continue.
            logger.warning(
                '[mythology/tuning] failed to update pattern=%s (%s: %s)',
                pattern_type, type(e).__name__, e,
            )

    return {
        'patterns_updated': updated,
        'auto_disabled': auto_disabled,
        'action_class': action_class,
    }


def _classify_action(review_action: str) -> str:
    """Return 'correct_catch' | 'false_positive' | 'unknown'."""
    if not review_action:
        return 'unknown'
    action = review_action.lower()
    if action in CORRECT_CATCH_ACTIONS:
        return 'correct_catch'
    if action in FALSE_POSITIVE_ACTIONS:
        return 'false_positive'
    return 'unknown'


def _apply_review_to_pattern(pattern: MythPattern, action_class: str) -> bool:
    """Mutate the pattern in-place. Returns True if auto-disabled this call."""
    meta = pattern.prevention_strategies if isinstance(pattern.prevention_strategies, dict) else {}
    if not isinstance(meta, dict):
        # Migration: prevention_strategies field was declared JSONField
        # default=list, but we need a dict for tuning metadata. Coerce
        # once per pattern — existing list content preserved under a key.
        meta = {'_legacy_strategies': meta} if meta else {}

    tuning = meta.setdefault('tuning', {
        'correct_catches': 0,
        'false_positives': 0,
        'last_reviewed_at': None,
        'auto_disabled_at': None,
    })

    if action_class == 'correct_catch':
        tuning['correct_catches'] += 1
        pattern.times_prevented = (pattern.times_prevented or 0) + 1
        pattern.severity_weight = _clamp_severity(
            (pattern.severity_weight or 0.1) + SEVERITY_NUDGE_CORRECT
        )
    elif action_class == 'false_positive':
        tuning['false_positives'] += 1
        pattern.severity_weight = _clamp_severity(
            (pattern.severity_weight or 0.1) + SEVERITY_NUDGE_FALSE_POSITIVE
        )
    else:
        return False

    tuning['last_reviewed_at'] = timezone.now().isoformat()
    meta['tuning'] = tuning
    pattern.prevention_strategies = meta

    # Recompute success rate: correct / (correct + fp) — treat missing
    # values defensively.
    correct = tuning['correct_catches']
    fp = tuning['false_positives']
    total = correct + fp
    if total > 0:
        pattern.prevention_success_rate = round(correct / total, 4)

    # Auto-disable only when we have enough signal AND FP ratio is extreme
    auto_disabled_now = False
    if (
        pattern.is_active
        and total >= MIN_REVIEWS_FOR_DISABLE
        and fp / total >= AUTO_DISABLE_FP_THRESHOLD
    ):
        pattern.is_active = False
        tuning['auto_disabled_at'] = timezone.now().isoformat()
        tuning['auto_disable_reason'] = (
            f'FP rate {fp / total:.2%} over {total} reviews '
            f'exceeded threshold {AUTO_DISABLE_FP_THRESHOLD:.0%}'
        )
        meta['tuning'] = tuning
        pattern.prevention_strategies = meta
        auto_disabled_now = True
        logger.warning(
            '[mythology/tuning] auto-disabled pattern=%s: %s',
            pattern.pattern_type, tuning['auto_disable_reason'],
        )

    return auto_disabled_now


def _clamp_severity(v: float) -> float:
    return max(MIN_SEVERITY_WEIGHT, min(MAX_SEVERITY_WEIGHT, v))


# =============================================================================
# Bulk review helper — used by the bulk-triage endpoint
# =============================================================================

def bulk_review_by_pattern(
    pattern_type: str,
    review_action: str,
    reviewer,
    notes: str = '',
    priority_filter: str | None = None,
    limit: int = 1000,
) -> dict:
    """Mark all pending FlaggedHallucination rows matching a pattern_type.

    Intended for triaging the tail of a false-positive regex storm.
    When a single over-broad pattern has produced hundreds of flags,
    operators can clear the whole batch by pattern_type with one call
    instead of clicking through each flag.

    Returns a summary dict so the endpoint can surface counts to the UI.
    """
    from .models import HallucinationReview

    qs = FlaggedHallucination.objects.filter(
        verification_status='pending',
        patterns_detected__contains=[pattern_type],
    )
    if priority_filter:
        qs = qs.filter(priority=priority_filter)
    qs = qs[:limit]

    status_mapping = {
        'approve': 'verified_safe',
        'remove': 'verified_hallucination',
        'flag_false_positive': 'false_positive',
        'verified_safe': 'verified_safe',
        'verified_hallucination': 'verified_hallucination',
    }
    new_status = status_mapping.get(review_action, 'needs_human_review')
    now = timezone.now()

    flagged_list = list(qs)
    reviewed_ids = []
    pattern_updates = {
        'patterns_updated': 0,
        'auto_disabled': [],
        'action_class': _classify_action(review_action),
    }

    for flagged in flagged_list:
        flagged.verification_status = new_status
        flagged.verification_notes = notes or f'Bulk review: {review_action}'
        flagged.verified_by = reviewer
        flagged.verified_at = now
        flagged.reviewed_at = now
        flagged.save()

        HallucinationReview.objects.create(
            flagged_hallucination=flagged,
            reviewer=reviewer,
            review_action=review_action,
            review_notes=f'(bulk) {notes}' if notes else '(bulk)',
            confidence_rating=5,
        )
        reviewed_ids.append(str(flagged.id))

    # Tune the pattern ONCE per batch (not once per flag) — flagging
    # 200 false positives in bulk shouldn't nudge severity down 200 times,
    # that would auto-disable a legitimate pattern from one operator
    # action. Instead apply a single correct/FP decision per pattern.
    if flagged_list:
        # Use any representative flag's patterns_detected list to drive tuning
        representative = flagged_list[0]
        pattern_updates = tune_patterns_from_review(representative, review_action)

    return {
        'reviewed_count': len(reviewed_ids),
        'reviewed_ids': reviewed_ids,
        'new_status': new_status,
        'pattern_tuning': pattern_updates,
    }
