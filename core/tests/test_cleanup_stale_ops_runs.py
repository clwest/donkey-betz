"""S3037 Reliability Audit v0 Step 6 S4 — `cleanup_stale_ops_runs` task tests.

Discharges the S3037 finding that ``OpsRun`` had no cleanup layer (2 rows
were found stuck in ``status='running'`` for 383h and 434h at audit time,
directly violating Chris's ratified ``no lost dispatches`` reliability
rule). Mirrors the ``_impl_cleanup_stale_agent_executions`` test pattern
from ``core/tasks_agents.py``.

Run::

    python manage.py test core.tests.test_cleanup_stale_ops_runs -v2
"""
from datetime import timedelta
from unittest.mock import MagicMock

from django.test import TransactionTestCase
from django.utils import timezone

from core.models_ops_runs import OpsRun, OpsRunEvent
from core.tasks_ops import _impl_cleanup_stale_ops_runs


def _make_ops_run(status='running', started_minutes_ago=120, title='test', **kwargs):
    """Helper: create an OpsRun row. Overrides ``started_at`` after save
    since ``auto_now_add``/default may enforce ``timezone.now()``.
    """
    started_at = timezone.now() - timedelta(minutes=started_minutes_ago)
    r = OpsRun.objects.create(
        title=title,
        run_kind=kwargs.get('run_kind', 'test_run'),
        domain=kwargs.get('domain', 'test'),
        status=status,
        started_at=started_at,
    )
    OpsRun.objects.filter(id=r.id).update(started_at=started_at)
    r.refresh_from_db()
    return r


def _make_task_self():
    """Mock Celery task self object with request.id."""
    self_mock = MagicMock()
    self_mock.request.id = 'test-task-id-abc123'
    return self_mock


class CleanupStaleOpsRunsSweepTests(TransactionTestCase):
    """S3037 S4 core sweep behavior: stale rows flip to failed, fresh rows
    untouched, non-running statuses untouched, events emitted per sweep.
    """

    def test_stale_running_row_flipped_to_failed(self):
        """Row in ``status='running'`` with ``started_at`` older than
        threshold → flipped to ``status='failed'`` with ``finished_at`` set.
        Direct discharge of the S3037 audit finding (2 rows stuck 16+ days).
        """
        r = _make_ops_run(status='running', started_minutes_ago=120)
        self.assertEqual(r.status, 'running')
        self.assertIsNone(r.finished_at)

        result = _impl_cleanup_stale_ops_runs(_make_task_self(), minutes_threshold=60)

        r.refresh_from_db()
        self.assertEqual(r.status, 'failed', "Stale running row MUST flip to failed.")
        self.assertIsNotNone(r.finished_at, "finished_at MUST be set on cleanup.")
        self.assertEqual(result['cleaned'], 1)

    def test_fresh_running_row_untouched(self):
        """Row in ``status='running'`` with ``started_at`` NEWER than
        threshold → left alone. This is the guardrail against sweeping
        legitimate in-flight work."""
        r = _make_ops_run(status='running', started_minutes_ago=5)

        result = _impl_cleanup_stale_ops_runs(_make_task_self(), minutes_threshold=60)

        r.refresh_from_db()
        self.assertEqual(r.status, 'running',
                         "Fresh running row MUST NOT be swept.")
        self.assertEqual(result['cleaned'], 0)

    def test_stale_but_not_running_row_untouched(self):
        """A row that's OLD but in ``status='passed'`` (or any non-running
        status) is left alone. Cleanup only targets status='running'."""
        for stale_status in ('passed', 'failed', 'aborted'):
            with self.subTest(status=stale_status):
                r = _make_ops_run(status=stale_status, started_minutes_ago=200)
                _impl_cleanup_stale_ops_runs(_make_task_self(), minutes_threshold=60)
                r.refresh_from_db()
                self.assertEqual(r.status, stale_status,
                                 f"Non-running row (status={stale_status}) MUST NOT be swept.")

    def test_cleanup_event_recorded_per_stale_row(self):
        """Each swept row gets an ``OpsRunEvent(event_type='cleanup',
        label='stale_running_swept')`` with structured detail identifying
        it as a sweeper action (not an organic failure).
        """
        r = _make_ops_run(status='running', started_minutes_ago=120,
                          run_kind='morning_brief', domain='mission')

        _impl_cleanup_stale_ops_runs(_make_task_self(), minutes_threshold=60)

        events = OpsRunEvent.objects.filter(run=r, event_type='cleanup')
        self.assertEqual(events.count(), 1,
                         "Exactly one cleanup event per swept row.")
        evt = events.first()
        self.assertEqual(evt.label, 'stale_running_swept')
        self.assertIn('run_kind', evt.detail)
        self.assertEqual(evt.detail['run_kind'], 'morning_brief')
        self.assertEqual(evt.detail['transition'], 'running→failed')
        self.assertIn('sweeper_task_id', evt.detail)
        self.assertEqual(evt.detail['sweeper_task_id'], 'test-task-id-abc123')
        self.assertIn('age_hours_at_cleanup', evt.detail)
        self.assertGreater(evt.detail['age_hours_at_cleanup'], 1.5)

    def test_no_stale_rows_returns_zero_cleaned(self):
        """Task tolerates the empty case cleanly — no exceptions when
        there's nothing to sweep."""
        _make_ops_run(status='running', started_minutes_ago=5)  # fresh
        _make_ops_run(status='passed', started_minutes_ago=200)  # not running

        result = _impl_cleanup_stale_ops_runs(_make_task_self(), minutes_threshold=60)

        self.assertEqual(result['cleaned'], 0)
        self.assertEqual(result['total_running'], 1)

    def test_returns_stats_dict(self):
        """Return payload shape must include cleaned + total_running +
        task_id — matches the AgentExecution cleanup contract."""
        _make_ops_run(status='running', started_minutes_ago=120)
        _make_ops_run(status='running', started_minutes_ago=5)  # fresh

        result = _impl_cleanup_stale_ops_runs(_make_task_self(), minutes_threshold=60)

        self.assertIn('cleaned', result)
        self.assertIn('total_running', result)
        self.assertIn('task_id', result)
        self.assertEqual(result['cleaned'], 1)
        self.assertEqual(result['total_running'], 2)
        self.assertEqual(result['task_id'], 'test-task-id-abc123')

    def test_multiple_stale_rows_swept_together(self):
        """Simulates the S3037 finding — multiple rows stuck across
        different domains/kinds get swept in one pass."""
        r1 = _make_ops_run(status='running', started_minutes_ago=200,
                           run_kind='morning_brief', domain='mission',
                           title='morning_brief: stale row 1')
        r2 = _make_ops_run(status='running', started_minutes_ago=500,
                           run_kind='rur_safety_contract_failures',
                           domain='ops',
                           title='safety contract stale row 2')

        result = _impl_cleanup_stale_ops_runs(_make_task_self(), minutes_threshold=60)

        self.assertEqual(result['cleaned'], 2)
        r1.refresh_from_db()
        r2.refresh_from_db()
        self.assertEqual(r1.status, 'failed')
        self.assertEqual(r2.status, 'failed')
        # Each got its own cleanup event
        self.assertEqual(OpsRunEvent.objects.filter(event_type='cleanup').count(), 2)

    def test_threshold_parameter_respected(self):
        """Explicit threshold override changes what counts as stale.
        Row 30-min-old should be spared at threshold=60 but swept at
        threshold=20."""
        r = _make_ops_run(status='running', started_minutes_ago=30)

        # At threshold=60, row is fresh (30 < 60)
        _impl_cleanup_stale_ops_runs(_make_task_self(), minutes_threshold=60)
        r.refresh_from_db()
        self.assertEqual(r.status, 'running', "Row spared at threshold=60.")

        # At threshold=20, same row is stale (30 > 20)
        _impl_cleanup_stale_ops_runs(_make_task_self(), minutes_threshold=20)
        r.refresh_from_db()
        self.assertEqual(r.status, 'failed', "Row swept at threshold=20.")
