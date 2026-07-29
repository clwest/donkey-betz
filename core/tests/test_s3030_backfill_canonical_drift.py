"""Session 3030: regression suite for `backfill_canonical_drift`.

The command heals rows created by the pre-Session 3029 tasks_ops bug:
`.update(status='canonical')` bypassed the model save so
`is_canonical=False`, `promoted_at=NULL`, `promoted_by=''` even though
`status='canonical'`. This suite pins:

1. Dry-run reports the correct drift count and writes nothing.
2. `--apply` heals every drift row: `is_canonical=True`,
   `promoted_at` restored to the pre-heal `updated_at` proxy,
   `promoted_by='backfill-s3030-tasks-ops-drift'`.
3. Rows that were never drifted (healthy canonical rows, draft rows)
   are not touched.
4. A second `--apply` run is a no-op — the filter naturally excludes
   healed rows, so the command is idempotent.
"""
from __future__ import annotations

from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import AgentDecisionSummary


BACKFILL_MARKER = 'backfill-s3030-tasks-ops-drift'


def _make_draft(topic: str) -> AgentDecisionSummary:
    return AgentDecisionSummary.objects.create(
        topic=topic,
        decision_type='experiment',
        impact_area='agents',
        rationale='r',
        recommended_stance='s',
        status='draft',
    )


class BackfillCanonicalDriftTest(TestCase):
    """`backfill_canonical_drift` heals drift rows, leaves others alone,
    is idempotent, and honors the dry-run default."""

    def _make_drift_row(self, topic: str) -> AgentDecisionSummary:
        """Create a row and mutate via bulk `.update()` — mimics the
        pre-S3029 bug that bypassed the model save + signals."""
        row = _make_draft(topic)
        # QuerySet.update() bypasses model save, exactly like the buggy
        # `_impl_auto_approve_boardroom_items` did pre-PR-3747.
        AgentDecisionSummary.objects.filter(pk=row.pk).update(status='canonical')
        row.refresh_from_db()
        # Assert we successfully reproduced the drift shape.
        self.assertEqual(row.status, 'canonical')
        self.assertFalse(row.is_canonical)
        self.assertIsNone(row.promoted_at)
        self.assertEqual(row.promoted_by, '')
        return row

    def _make_healthy_canonical(self, topic: str) -> AgentDecisionSummary:
        """Create a row promoted the correct way (via model method)."""
        row = _make_draft(topic)
        row.promote_to_canonical(promoted_by='human')
        row.refresh_from_db()
        # Confirm healthy shape.
        self.assertTrue(row.is_canonical)
        self.assertIsNotNone(row.promoted_at)
        self.assertEqual(row.promoted_by, 'human')
        return row

    def test_dry_run_reports_drift_and_writes_nothing(self):
        drift_a = self._make_drift_row('drift-a')
        drift_b = self._make_drift_row('drift-b')
        healthy = self._make_healthy_canonical('healthy')
        draft = _make_draft('draft')

        healthy_promoted_at_before = healthy.promoted_at
        drift_a_updated_before = drift_a.updated_at
        drift_b_updated_before = drift_b.updated_at

        out = StringIO()
        call_command('backfill_canonical_drift', stdout=out)
        output = out.getvalue()

        self.assertIn('DRY-RUN', output)
        self.assertIn('total_drift=2', output)
        self.assertIn('dry-run', output.lower())

        # No writes: reload and confirm drift shape unchanged.
        drift_a.refresh_from_db()
        drift_b.refresh_from_db()
        healthy.refresh_from_db()
        draft.refresh_from_db()

        self.assertFalse(drift_a.is_canonical)
        self.assertIsNone(drift_a.promoted_at)
        self.assertEqual(drift_a.updated_at, drift_a_updated_before)
        self.assertFalse(drift_b.is_canonical)
        self.assertIsNone(drift_b.promoted_at)
        self.assertEqual(drift_b.updated_at, drift_b_updated_before)
        self.assertTrue(healthy.is_canonical)
        self.assertEqual(healthy.promoted_at, healthy_promoted_at_before)
        self.assertEqual(draft.status, 'draft')

    def test_apply_heals_drift_rows_with_updated_at_proxy(self):
        drift_a = self._make_drift_row('drift-a')
        drift_b = self._make_drift_row('drift-b')
        drift_c = self._make_drift_row('drift-c')
        healthy = self._make_healthy_canonical('healthy')
        draft = _make_draft('draft')

        # Capture the pre-heal `updated_at` for each drift row — the
        # backfill contract is that `promoted_at` after heal equals this
        # value (proxy for the lost true promotion time).
        pre_heal_updated_at = {
            row.id: row.updated_at
            for row in AgentDecisionSummary.objects.filter(
                id__in=[drift_a.id, drift_b.id, drift_c.id]
            )
        }
        healthy_promoted_at_before = healthy.promoted_at

        out = StringIO()
        call_command('backfill_canonical_drift', '--apply', stdout=out)
        output = out.getvalue()

        self.assertIn('APPLY', output)
        self.assertIn('total_drift=3', output)
        self.assertIn('healed=3', output)
        self.assertIn('errors=0', output)

        # All three drift rows healed.
        for row in (drift_a, drift_b, drift_c):
            row.refresh_from_db()
            self.assertTrue(row.is_canonical, f'{row.topic} should be canonical')
            self.assertEqual(row.status, 'canonical')
            self.assertEqual(row.promoted_by, BACKFILL_MARKER)
            self.assertEqual(
                row.promoted_at,
                pre_heal_updated_at[row.id],
                f'{row.topic}.promoted_at should match pre-heal updated_at',
            )

        # Healthy row untouched (promoted_at + promoted_by preserved).
        healthy.refresh_from_db()
        self.assertTrue(healthy.is_canonical)
        self.assertEqual(healthy.promoted_by, 'human')
        self.assertEqual(healthy.promoted_at, healthy_promoted_at_before)

        # Draft row untouched.
        draft.refresh_from_db()
        self.assertEqual(draft.status, 'draft')
        self.assertFalse(draft.is_canonical)

    def test_apply_is_idempotent_on_second_run(self):
        self._make_drift_row('drift-a')
        self._make_drift_row('drift-b')

        # First apply heals both.
        out1 = StringIO()
        call_command('backfill_canonical_drift', '--apply', stdout=out1)
        self.assertIn('healed=2', out1.getvalue())

        # Snapshot healed-row state.
        healed_snapshot = {
            row.id: (row.is_canonical, row.promoted_at, row.promoted_by, row.updated_at)
            for row in AgentDecisionSummary.objects.filter(status='canonical')
        }

        # Second apply finds nothing — filter excludes healed rows.
        out2 = StringIO()
        call_command('backfill_canonical_drift', '--apply', stdout=out2)
        output2 = out2.getvalue()
        self.assertIn('total_drift=0', output2)
        self.assertIn('nothing to do', output2.lower())

        # No follow-up writes to already-healed rows.
        for row in AgentDecisionSummary.objects.filter(status='canonical'):
            snap = healed_snapshot[row.id]
            self.assertEqual(row.is_canonical, snap[0])
            self.assertEqual(row.promoted_at, snap[1])
            self.assertEqual(row.promoted_by, snap[2])
            self.assertEqual(row.updated_at, snap[3])

    def test_dry_run_and_apply_both_no_op_on_empty_db(self):
        """No drift rows at all — both modes short-circuit cleanly."""
        out_dry = StringIO()
        call_command('backfill_canonical_drift', stdout=out_dry)
        self.assertIn('total_drift=0', out_dry.getvalue())
        self.assertIn('nothing to do', out_dry.getvalue().lower())

        out_apply = StringIO()
        call_command('backfill_canonical_drift', '--apply', stdout=out_apply)
        self.assertIn('total_drift=0', out_apply.getvalue())

    def test_limit_flag_caps_batch_size(self):
        """--limit N processes at most N rows per run; the rest remain drift
        for a subsequent invocation."""
        for i in range(5):
            self._make_drift_row(f'drift-{i}')

        out = StringIO()
        call_command('backfill_canonical_drift', '--apply', '--limit', '2', stdout=out)
        output = out.getvalue()
        self.assertIn('total_drift=5', output)
        self.assertIn('healed=2', output)
        self.assertIn('remaining=3', output)

        # Confirm exactly 2 healed + 3 still drift.
        healed_count = AgentDecisionSummary.objects.filter(
            status='canonical', is_canonical=True
        ).count()
        drift_count = AgentDecisionSummary.objects.filter(
            status='canonical', is_canonical=False
        ).count()
        self.assertEqual(healed_count, 2)
        self.assertEqual(drift_count, 3)
