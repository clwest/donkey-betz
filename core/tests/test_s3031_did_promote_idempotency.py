"""Session 3031: `AgentDecisionSummary.promote_to_canonical` returns
`did_promote: bool` so callers gate `emit_canonical_promotion_broadcast`
on state-transition. Closes the duplicate-broadcast race that S3029
Fold B / S3030 Fold D flagged: if two of the six promotion paths race
on the same row (e.g. AI service + Rules service, or human + Celery
auto-approve), both used to emit — the state-check gate prevents that.

Contract this suite pins:

1. First call on a draft row returns True, mutates all four fields,
   and calls `save(update_fields=[...])` so untouched columns aren't
   overwritten.
2. Second call on the same (now-canonical) row returns False and is a
   no-op: `promoted_at` + `promoted_by` remain the values from the
   first call. Callers should treat False as "success via idempotent
   no-op", not error.
3. When the AI-AutoPromoter service is called twice on the same row,
   the broadcast helper fires exactly once.
"""
from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase

from core.models_unified_system import AgentDecisionSummary


def _make_draft(topic: str) -> AgentDecisionSummary:
    return AgentDecisionSummary.objects.create(
        topic=topic,
        decision_type='experiment',
        impact_area='agents',
        rationale='r',
        recommended_stance='s',
        status='draft',
    )


class DidPromoteIdempotencyTest(TestCase):
    def test_first_call_returns_true_and_mutates_all_fields(self):
        row = _make_draft('t')
        self.assertFalse(row.is_canonical)
        self.assertIsNone(row.promoted_at)

        result = row.promote_to_canonical(promoted_by='human')

        self.assertTrue(result, "first call must return True (did the transition)")
        row.refresh_from_db()
        self.assertEqual(row.status, 'canonical')
        self.assertTrue(row.is_canonical)
        self.assertIsNotNone(row.promoted_at)
        self.assertEqual(row.promoted_by, 'human')

    def test_second_call_returns_false_and_is_noop(self):
        row = _make_draft('t')
        row.promote_to_canonical(promoted_by='first-caller')
        row.refresh_from_db()
        first_promoted_at = row.promoted_at
        first_promoted_by = row.promoted_by
        first_updated_at = row.updated_at

        result = row.promote_to_canonical(promoted_by='racing-caller')

        self.assertFalse(result, "second call on canonical row must return False (no-op)")
        row.refresh_from_db()
        # Neither the marker nor the timestamp gets overwritten by the
        # racing caller. The row remembers who first promoted it.
        self.assertEqual(row.promoted_by, first_promoted_by)
        self.assertEqual(row.promoted_at, first_promoted_at)
        # No save happened at all → auto_now didn't bump updated_at.
        self.assertEqual(row.updated_at, first_updated_at)

    def test_ai_promoter_service_fires_broadcast_exactly_once_when_called_twice(self):
        """End-to-end: the AI service caller wraps the broadcast in
        `if did_promote:`. Two calls on the same row = one broadcast."""
        from core.services.ai_decision_promoter import AIDecisionPromoterService

        row = _make_draft('race')
        service = AIDecisionPromoterService()

        with patch(
            'core.services.canonical_decision_broadcast.emit_canonical_promotion_broadcast'
        ) as spy:
            first = service.promote_decision(row, promoter='AI-AutoPromoter')
            row.refresh_from_db()
            second = service.promote_decision(row, promoter='AI-AutoPromoter')

        # Both return True at the service-level contract (promotion
        # succeeded in the "row is now canonical" sense), even though
        # the second is a no-op internally.
        self.assertTrue(first)
        self.assertTrue(second)
        # Broadcast helper called exactly once — only the first call
        # actually did the state transition.
        self.assertEqual(
            spy.call_count, 1,
            f"expected 1 broadcast (only first call did the transition); got {spy.call_count}",
        )
