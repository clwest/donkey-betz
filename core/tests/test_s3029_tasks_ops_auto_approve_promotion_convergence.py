"""Session 3029 PR #3747 (S3028 Fold A follow-up sweep discovery):
`_impl_auto_approve_boardroom_items` in `core/tasks_ops.py` was the 4th
silent canonical-promotion site — bulk `.update(status='canonical')`
that bypassed the model method entirely, leaving `is_canonical=False`,
`promoted_at=NULL`, `promoted_by=NULL` (data-integrity breach) AND
skipping the S3028 broadcast.

The Rigby A2 zoom-out sweep uncovered this in the same session as the
initial S3029 convergence PR (#3746). Per Rigby A1 REVISE, fix landed
in follow-up PR #3747 same session — task now loops per-row through
`decision.promote_to_canonical(...)` + emits broadcast, matching the
other 5 promotion paths.

This suite pins the fix. Backfill of existing drift rows (created by
5 years of `.update(status='canonical')` calls) is deferred to S3030
as a separate management command.
"""
from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase

from core.models_unified_system import AgentDecisionSummary
from core.tasks_ops import _impl_auto_approve_boardroom_items


def _make_draft(
    *,
    topic: str = "Draft",
    decision_type: str = "experiment",
    rationale: str = "reason",
    recommended_stance: str = "stance",
    impact_area: str = "agents",
) -> AgentDecisionSummary:
    return AgentDecisionSummary.objects.create(
        conversation=None,
        hive_session=None,
        topic=topic,
        decision_type=decision_type,
        impact_area=impact_area,
        rationale=rationale,
        recommended_stance=recommended_stance,
        status='draft',
    )


class AutoApproveCanonicalPromotionTest(TestCase):
    """`_impl_auto_approve_boardroom_items` must set all 4 canonical
    fields (status, is_canonical, promoted_at, promoted_by) AND fire the
    S3028 broadcast for each auto-promoted decision."""

    def test_auto_approve_sets_all_4_canonical_fields_and_broadcasts(self) -> None:
        # One row per auto-promote decision_type so we exercise all 4
        # branches in a single run.
        rows = {
            dtype: _make_draft(topic=f"tasks-ops-{dtype}", decision_type=dtype)
            for dtype in ["experiment", "pipeline", "research", "guideline"]
        }

        with patch("redis.Redis") as mock_redis_cls:
            mock_pub = mock_redis_cls.from_url.return_value.publish
            mock_pub.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            result = _impl_auto_approve_boardroom_items()

        # Task returns overall stats dict, not just the promotion counts.
        # Assert each decision_type counter reflects 1 promoted row.
        self.assertEqual(result["experiments_promoted"], 1)
        self.assertEqual(result["pipelines_promoted"], 1)
        self.assertEqual(result["research_promoted"], 1)
        self.assertEqual(result["guidelines_promoted"], 1)

        # Every row now has ALL 4 canonical fields correctly set (this is
        # what the pre-S3029 bulk-update path was silently leaving broken).
        for dtype, row in rows.items():
            row.refresh_from_db()
            self.assertEqual(row.status, "canonical", f"{dtype} status")
            self.assertTrue(row.is_canonical, f"{dtype} is_canonical")
            self.assertIsNotNone(row.promoted_at, f"{dtype} promoted_at")
            self.assertEqual(
                row.promoted_by, "system-auto-approve", f"{dtype} promoted_by"
            )

        # Broadcast fired once per promoted row (4 total).
        self.assertEqual(mock_pub.call_count, 4)
        # All to the same channel; each event carries the S3026 shape.
        for call in mock_pub.call_args_list:
            channel, _payload = call.args
            self.assertEqual(channel, "agent_learning")

    def test_auto_approve_skips_non_draft_rows(self) -> None:
        """Tight filter (Rigby A1 REVISE): task should NOT re-promote rows
        that are already canonical or in any other non-draft state."""
        already_canonical = _make_draft(topic="already", decision_type="experiment")
        already_canonical.status = 'canonical'
        already_canonical.is_canonical = True
        already_canonical.save()

        with patch("redis.Redis") as mock_redis_cls:
            mock_redis_cls.from_url.return_value.publish.return_value = None
            mock_redis_cls.from_url.return_value.incr.return_value = None
            result = _impl_auto_approve_boardroom_items()

        # No experiment rows in draft → counter stays 0.
        self.assertEqual(result["experiments_promoted"], 0)

    def test_auto_approve_survives_broadcast_failure(self) -> None:
        """Redis-down must not fail the promotion or roll it back — the
        4 canonical fields are still written, only the broadcast is
        skipped for that batch."""
        row = _make_draft(topic="redis-down-auto", decision_type="pipeline")

        with patch("redis.Redis") as mock_redis_cls:
            mock_redis_cls.from_url.side_effect = RuntimeError("redis unreachable")
            result = _impl_auto_approve_boardroom_items()

        self.assertEqual(result["pipelines_promoted"], 1)
        row.refresh_from_db()
        self.assertEqual(row.status, "canonical")
        self.assertTrue(row.is_canonical)
        self.assertIsNotNone(row.promoted_at)
        self.assertEqual(row.promoted_by, "system-auto-approve")
