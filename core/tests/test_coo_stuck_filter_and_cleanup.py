"""
COO stuck-initiative filter + cleanup_stale_initiatives management command.
============================================================================

Session 1094 follow-up: the COOAgent smoke test caught 147 historical ACTIVE
initiatives from earlier sessions (76d+ stale, never transitioned out of
status='ACTIVE'). Two narrow fixes to make the COO diagnostic production-safe
without pretending the sediment doesn't exist:

1. `COO_DIAG_STUCK_IGNORE_BEFORE` env var — excludes pre-cutoff initiatives
   from the stuck count when set to an ISO date. Default empty = no filter.

2. `cleanup_stale_initiatives` management command — one-time sediment
   cleanup with --dry-run default and --apply to commit. Archives rather
   than deletes (preserves rows, transitions status='ACTIVE' → 'ARCHIVED').

Run:
    python manage.py test core.tests.test_coo_stuck_filter_and_cleanup -v2
"""
from datetime import datetime, timedelta, timezone as dt_tz
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TransactionTestCase
from django.utils import timezone


def _make_initiative(name, *, status='ACTIVE', stage=1, updated_days_ago=80):
    """Create an Initiative for testing. Override updated_at after save since
    it has auto_now behavior (we need control over the staleness)."""
    from core.models import Initiative

    init = Initiative.objects.create(
        name=name,
        status=status,
        current_stage=stage,
    )
    target_updated_at = timezone.now() - timedelta(days=updated_days_ago)
    Initiative.objects.filter(pk=init.pk).update(updated_at=target_updated_at)
    init.refresh_from_db()
    return init


# =============================================================================
# COO_DIAG_STUCK_IGNORE_BEFORE filter
# =============================================================================

class StuckIgnoreBeforeFilterTests(TransactionTestCase):
    """When env var is set, pre-cutoff initiatives excluded from stuck_count."""

    def setUp(self):
        # 3 old initiatives (sediment), 2 fresh-stuck (72h–7d) initiatives
        _make_initiative('sediment-a', updated_days_ago=80)
        _make_initiative('sediment-b', updated_days_ago=60)
        _make_initiative('sediment-c', updated_days_ago=35)
        _make_initiative('fresh-stuck-1', updated_days_ago=4)
        _make_initiative('fresh-stuck-2', updated_days_ago=5)

    def _collect_stuck(self, env_overrides=None) -> dict:
        """Invoke the live metrics collector with an env override."""
        from core.services.diagnostics.coo_daily import collect_metrics
        now = timezone.now()
        cutoff_24h = now - timedelta(hours=24)
        cutoff_7d = now - timedelta(days=7)
        with patch.dict('os.environ', env_overrides or {}, clear=False):
            metrics = collect_metrics(now, cutoff_24h, cutoff_7d)
        return metrics['initiatives']

    def test_no_env_var_all_stale_counted(self):
        """Default behavior: all 5 ACTIVE stale initiatives counted."""
        result = self._collect_stuck()
        self.assertEqual(result['stuck_count'], 5)
        self.assertIsNone(result['ignore_before'])

    def test_ignore_before_30d_excludes_older_sediment(self):
        """Setting cutoff to 30d ago excludes 3 sediment, keeps 2 fresh-stuck."""
        cutoff = (timezone.now() - timedelta(days=30)).date().isoformat()
        result = self._collect_stuck({'COO_DIAG_STUCK_IGNORE_BEFORE': cutoff})
        # The 3 items at 35/60/80 days are excluded; 4/5 day items remain
        self.assertEqual(result['stuck_count'], 2)
        self.assertEqual(result['ignore_before'], cutoff)

    def test_ignore_before_excludes_all_older_than_now(self):
        """Pathological cutoff of 'right now' excludes everything."""
        cutoff = timezone.now().isoformat()
        result = self._collect_stuck({'COO_DIAG_STUCK_IGNORE_BEFORE': cutoff})
        self.assertEqual(result['stuck_count'], 0)

    def test_malformed_env_var_logged_and_ignored(self):
        """Invalid ISO date value falls back to no filtering — safe default."""
        with self.assertLogs('core.services.diagnostics.coo_daily', level='WARNING') as cm:
            result = self._collect_stuck({'COO_DIAG_STUCK_IGNORE_BEFORE': 'not-a-date'})
        self.assertEqual(result['stuck_count'], 5)  # filter did not apply
        self.assertIsNone(result['ignore_before'])
        self.assertTrue(any('COO_DIAG_STUCK_IGNORE_BEFORE' in msg for msg in cm.output))

    def test_naive_datetime_assumed_utc(self):
        """Naive ISO datetime is accepted (tzinfo attached as UTC).

        Operator convenience — they shouldn't have to remember ISO suffixes.
        """
        cutoff = (timezone.now() - timedelta(days=50)).replace(tzinfo=None).isoformat()
        result = self._collect_stuck({'COO_DIAG_STUCK_IGNORE_BEFORE': cutoff})
        # Should filter out the 80d and 60d items (pre-50d-cutoff); keep 35d, 4d, 5d
        self.assertEqual(result['stuck_count'], 3)


# =============================================================================
# cleanup_stale_initiatives management command
# =============================================================================

class CleanupStaleInitiativesTests(TransactionTestCase):
    """Command archives ACTIVE initiatives older than cutoff, dry-run default."""

    def setUp(self):
        from core.models import Initiative
        Initiative.objects.all().delete()
        self.sediment_a = _make_initiative('sediment-a', updated_days_ago=80, stage=1)
        self.sediment_b = _make_initiative('sediment-b', updated_days_ago=60, stage=2)
        self.sediment_c = _make_initiative('sediment-c', updated_days_ago=45, stage=1)
        self.fresh = _make_initiative('fresh', updated_days_ago=5, stage=1)
        # Already-archived should not be touched
        self.already_archived = _make_initiative(
            'already-archived', status='ARCHIVED', updated_days_ago=90
        )

    def _run(self, *args):
        from core.models import Initiative
        out = StringIO()
        call_command('cleanup_stale_initiatives', *args, stdout=out)
        return out.getvalue(), Initiative.objects

    def test_dry_run_is_default(self):
        """No args beyond --older-than-days means preview only (no writes)."""
        out, qs = self._run('--older-than-days', '30')
        self.assertIn('DRY-RUN', out)
        self.assertIn('Candidates matching filter: 3', out)  # a, b, c
        self.assertIn('Re-run with --apply', out)
        # Confirm nothing changed
        self.assertEqual(qs.filter(status='ACTIVE').count(), 4)  # a, b, c, fresh
        self.assertEqual(qs.filter(status='ARCHIVED').count(), 1)  # the pre-existing one

    def test_apply_archives_matching_rows(self):
        out, qs = self._run('--older-than-days', '30', '--apply')
        self.assertIn('APPLY', out)
        self.assertIn('Archived 3 initiatives', out)
        self.assertEqual(qs.filter(status='ARCHIVED').count(), 4)  # 3 new + 1 preexisting
        self.assertEqual(qs.filter(status='ACTIVE').count(), 1)  # fresh survives

    def test_only_stage_filter(self):
        """--only-stage restricts to a single current_stage value."""
        out, qs = self._run('--older-than-days', '30', '--only-stage', '1', '--apply')
        self.assertIn('stage 1: 2', out)  # a, c are stage 1
        self.assertNotIn('stage 2: 1', out)
        self.assertIn('Archived 2 initiatives', out)
        # sediment-b (stage=2) NOT archived
        self.sediment_b.refresh_from_db()
        self.assertEqual(self.sediment_b.status, 'ACTIVE')

    def test_idempotent_second_run_no_op(self):
        """After archiving, re-running finds nothing."""
        self._run('--older-than-days', '30', '--apply')
        out, _ = self._run('--older-than-days', '30')
        self.assertIn('No stale initiatives found', out)

    def test_limit_caps_candidates(self):
        """--limit restricts the batch size without changing the filter count."""
        out, qs = self._run('--older-than-days', '30', '--limit', '1', '--apply')
        self.assertIn('Candidates matching filter: 3', out)
        self.assertIn('Limited to first: 1', out)
        self.assertIn('Archived 1 initiatives', out)
        self.assertEqual(qs.filter(status='ACTIVE').count(), 3)  # still 2 old + fresh

    def test_already_archived_never_touched(self):
        """Command filters on status='ACTIVE' — ARCHIVED rows are skipped."""
        self._run('--older-than-days', '30', '--apply')
        self.already_archived.refresh_from_db()
        self.assertEqual(self.already_archived.status, 'ARCHIVED')
        # updated_at of the pre-existing archived row should NOT have been bumped
        self.assertLess(
            self.already_archived.updated_at,
            timezone.now() - timedelta(days=80)
        )

    def test_zero_or_negative_days_rejected(self):
        """--older-than-days must be positive."""
        from django.core.management.base import CommandError
        with self.assertRaises(CommandError):
            call_command('cleanup_stale_initiatives', '--older-than-days', '0')
        with self.assertRaises(CommandError):
            call_command('cleanup_stale_initiatives', '--older-than-days', '-5')


# =============================================================================
# COO_DIAG_PUBLISHABLE_TYPES filter (publishing pipeline investigation fix)
# =============================================================================

class PublishableTypesFilterTests(TransactionTestCase):
    """`COO_DIAG_PUBLISHABLE_TYPES` scopes velocity + review_backlog gates
    to only the deliverable_types that actually publish on this platform.

    Without the filter the PUBLISHING_JAM_CRIT gate permanently trips because
    scheduled-analysis agents create hundreds of `ready` deliverables daily
    (type=analysis, research, report, etc.) that are internal artifacts —
    not meant to publish.
    """

    def setUp(self):
        from core.models_deliverables import Deliverable
        Deliverable.objects.all().delete()

        # 15 internal-analysis outputs (the scheduled-agent noise)
        for i in range(15):
            Deliverable.objects.create(
                title=f'analysis-{i}',
                content='analysis content',
                agent_name='StockAnalystAgent',
                deliverable_type='analysis',
                status='ready',
            )
        # 3 publishable documents (what actually publishes)
        for i in range(3):
            Deliverable.objects.create(
                title=f'doc-{i}',
                content='document content',
                agent_name='InitiativePipeline',
                deliverable_type='document',
                status='ready',
            )
        # 2 already-published documents (the tiny actual publish throughput)
        for i in range(2):
            Deliverable.objects.create(
                title=f'pub-doc-{i}',
                content='published doc',
                agent_name='InitiativePipeline',
                deliverable_type='document',
                status='published',
            )

    def _collect_velocity_backlog(self, env_overrides=None):
        from core.services.diagnostics.coo_daily import collect_metrics
        now = timezone.now()
        cutoff_24h = now - timedelta(hours=24)
        cutoff_7d = now - timedelta(days=7)
        with patch.dict('os.environ', env_overrides or {}, clear=False):
            metrics = collect_metrics(now, cutoff_24h, cutoff_7d)
        return metrics['velocity'], metrics['review_backlog']

    def test_no_filter_counts_all_types(self):
        """Default: all 18 ready + 2 published are counted."""
        vel, backlog = self._collect_velocity_backlog()
        self.assertEqual(vel['created_24h'], 20)  # 18 ready + 2 published
        self.assertEqual(vel['published_24h'], 2)
        self.assertIsNone(vel['publishable_types_filter'])
        self.assertEqual(backlog['ready_count'], 18)  # 15 analysis + 3 document

    def test_filter_document_only_excludes_analysis_noise(self):
        """Filter to document → 15 analysis noise excluded from ready count."""
        vel, backlog = self._collect_velocity_backlog(
            {'COO_DIAG_PUBLISHABLE_TYPES': 'document'}
        )
        self.assertEqual(vel['created_24h'], 5)  # 3 ready docs + 2 published docs
        self.assertEqual(vel['published_24h'], 2)
        self.assertEqual(vel['publishable_types_filter'], ['document'])
        self.assertEqual(backlog['ready_count'], 3)  # only docs, not analyses

    def test_filter_csv_multiple_types(self):
        """CSV parses correctly with spaces + multiple values."""
        vel, backlog = self._collect_velocity_backlog(
            {'COO_DIAG_PUBLISHABLE_TYPES': 'document, video, edited_content'}
        )
        self.assertEqual(vel['publishable_types_filter'], ['document', 'video', 'edited_content'])
        self.assertEqual(backlog['ready_count'], 3)  # only docs match

    def test_filter_nonexistent_type_produces_zero_counts(self):
        """Defensive: garbage filter value produces empty counts, not crash."""
        vel, backlog = self._collect_velocity_backlog(
            {'COO_DIAG_PUBLISHABLE_TYPES': 'nonexistent_type_xyz'}
        )
        self.assertEqual(vel['created_24h'], 0)
        self.assertEqual(vel['published_24h'], 0)
        self.assertEqual(backlog['ready_count'], 0)

    def test_filter_gate_does_not_trip_when_filtered_published_is_nonzero(self):
        """With filter applied to types that DO publish, jam gate doesn't fire."""
        from core.services.diagnostics.coo_daily import evaluate_gate
        vel, backlog = self._collect_velocity_backlog(
            {'COO_DIAG_PUBLISHABLE_TYPES': 'document'}
        )
        # Build a minimal metrics dict for gate evaluation
        metrics = {
            'velocity': vel,
            'review_backlog': backlog,
            'action_items': {'pending_by_urgency': {}, 'pending_over_sla_by_urgency': {}, 'pending_total': 0, 'oldest_critical_hours': 0.0},
            'initiatives': {'stuck_count': 0, 'stuck_hours_threshold': 72, 'stuck_top': []},
        }
        gate = evaluate_gate(metrics)
        # Should NOT have PUBLISHING_JAM_CRIT because published_24h=2, not 0
        self.assertNotIn('PUBLISHING_JAM_CRIT', gate['reasons'])
