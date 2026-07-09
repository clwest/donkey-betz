"""
Regression tests for Session 2734 — Platform Closure §15 Worker Failure Item 14.

Exercises the failure_cluster escalation chain:

    Celery task_failure → CeleryTaskEvent(status='FAILURE') write
      → core.signals.failure_cluster_signals.escalate_failure_cluster
      → FailureClusterAggregator sliding-window compute
      → threshold + dedup gates
      → HumanAttentionBridge.create_failure_cluster_attention (patched)

Test discipline:

* Real DB, real ``CeleryTaskEvent`` writes, real
  :class:`~core.services.failure_cluster_aggregator.FailureClusterSnapshot`
  computation. No mocked querysets.
* ``HumanAttentionBridge.create_failure_cluster_attention`` is patched
  so we assert the *receiver's* contract (status filter, threshold,
  dedup key, kill switch, on_commit gating) without touching the
  ``HumanInterfaceService`` write path.
* Uses ``captureOnCommitCallbacks(execute=True)`` because the receiver
  schedules the escalation via ``transaction.on_commit``.

Run::

    python manage.py test core.tests.test_failure_cluster_attention -v2
"""
from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from core.models_celery_telemetry import CeleryTaskEvent
from core.models_human_interface import HumanAttentionItem
from core.services.failure_cluster_aggregator import compute_cluster

User = get_user_model()


def _admin_user():
    """Persistent admin user for HAI rows in dedup tests."""
    user, _ = User.objects.get_or_create(
        username='failure-cluster-fixture-admin',
        defaults={'is_staff': True, 'is_active': True},
    )
    return user


_BRIDGE_PATH = (
    "core.services.human_attention_bridge.HumanAttentionBridge."
    "create_failure_cluster_attention"
)


def _make_failure(
    *,
    task_name: str = 'core.tasks.example',
    task_id: str | None = None,
    finished_at=None,
    queue: str = 'default',
    worker: str = 'worker-1',
    error_type: str = 'ValueError',
) -> CeleryTaskEvent:
    """Insert a fully-populated FAILURE ``CeleryTaskEvent`` row.

    Uses ``update_or_create`` semantics via unique ``task_id`` to
    mirror the celery_telemetry path.
    """
    now = timezone.now()
    finished = finished_at or now
    task_id = task_id or f"task-{now.timestamp()}-{queue}-{task_name}"
    return CeleryTaskEvent.objects.create(
        task_id=task_id,
        task_name=task_name,
        status='FAILURE',
        queue=queue,
        worker=worker,
        started_at=finished - timedelta(seconds=1),
        finished_at=finished,
        error_type=error_type,
        error_message=f"synthetic {error_type} for tests",
    )


class FailureClusterHappyPathTests(TestCase):
    """Threshold breach triggers exactly one escalation."""

    def test_threshold_reached_escalates(self):
        """5 distinct-task-id failures for the same task_name within the
        default 5-min window → one on_commit dispatch."""
        # 4 pre-existing failures already in the window.
        for i in range(4):
            _make_failure(task_id=f'pre-{i}')
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            # 5th failure lands — cluster now meets threshold.
            _make_failure(task_id='trigger')
        mock_bridge.assert_called_once()
        (snapshot,) = mock_bridge.call_args.args
        self.assertEqual(snapshot.task_name, 'core.tasks.example')
        self.assertGreaterEqual(snapshot.distinct_task_id_count, 5)
        self.assertEqual(snapshot.urgency_band, 'high')
        self.assertIn(
            'failure_cluster:core.tasks.example', snapshot.idempotency_key,
        )
        self.assertIn(':high', snapshot.idempotency_key)

    def test_critical_threshold_reached_escalates_critical(self):
        """15 distinct-task-id failures within the window → critical band."""
        for i in range(14):
            _make_failure(task_id=f'pre-crit-{i}')
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_failure(task_id='trigger-crit')
        mock_bridge.assert_called_once()
        (snapshot,) = mock_bridge.call_args.args
        self.assertGreaterEqual(snapshot.distinct_task_id_count, 15)
        self.assertEqual(snapshot.urgency_band, 'critical')
        self.assertIn(':critical', snapshot.idempotency_key)


class FailureClusterFilteringTests(TestCase):
    """Non-failure saves and below-threshold saves do not escalate."""

    def test_started_status_does_not_escalate(self):
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            CeleryTaskEvent.objects.create(
                task_id='started-1',
                task_name='core.tasks.example',
                status='STARTED',
                started_at=timezone.now(),
            )
        mock_bridge.assert_not_called()

    def test_success_status_does_not_escalate(self):
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            CeleryTaskEvent.objects.create(
                task_id='success-1',
                task_name='core.tasks.example',
                status='SUCCESS',
                started_at=timezone.now(),
                finished_at=timezone.now(),
            )
        mock_bridge.assert_not_called()

    def test_empty_task_name_does_not_escalate(self):
        """Guard: the aggregator's task_name filter would degenerate."""
        # Pre-populate 5 empty-task-name failures.
        for i in range(4):
            CeleryTaskEvent.objects.create(
                task_id=f'empty-pre-{i}',
                task_name='',
                status='FAILURE',
                started_at=timezone.now(),
                finished_at=timezone.now(),
            )
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            CeleryTaskEvent.objects.create(
                task_id='empty-trigger',
                task_name='   ',  # whitespace-only
                status='FAILURE',
                started_at=timezone.now(),
                finished_at=timezone.now(),
            )
        mock_bridge.assert_not_called()

    def test_below_threshold_does_not_escalate(self):
        """4 failures (threshold is 5) → no escalation."""
        for i in range(4):
            _make_failure(task_id=f'below-{i}')
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            # Editing the last row (update, not create) — should not
            # accidentally re-fire.
            row = CeleryTaskEvent.objects.get(task_id='below-3')
            row.error_message = 'edited'
            row.save(update_fields=['error_message'])
        mock_bridge.assert_not_called()

    def test_transition_to_failure_escalates(self):
        """STARTED → FAILURE update path (celery_telemetry.on_task_failure
        line 203) also escalates when cluster meets threshold."""
        for i in range(4):
            _make_failure(task_id=f'transition-pre-{i}')
        # Create a STARTED row first (no bridge fire), then transition to FAILURE.
        with patch(_BRIDGE_PATH) as first_bridge, self.captureOnCommitCallbacks(execute=True):
            row = CeleryTaskEvent.objects.create(
                task_id='transition-target',
                task_name='core.tasks.example',
                status='STARTED',
                started_at=timezone.now(),
            )
        first_bridge.assert_not_called()

        with patch(_BRIDGE_PATH) as second_bridge, self.captureOnCommitCallbacks(execute=True):
            row.status = 'FAILURE'
            row.finished_at = timezone.now()
            row.error_type = 'RuntimeError'
            row.save(update_fields=['status', 'finished_at', 'error_type'])
        second_bridge.assert_called_once()

    @override_settings(FAILURE_CLUSTER_HAI_ENABLED=False)
    def test_kill_switch_disables_escalation(self):
        for i in range(4):
            _make_failure(task_id=f'kill-pre-{i}')
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_failure(task_id='kill-trigger')
        mock_bridge.assert_not_called()


class FailureClusterDedupTests(TestCase):
    """(task_name, urgency_band) dedup key allows critical re-escalation."""

    def _prepopulate_failures(self, n: int, prefix: str = 'dp'):
        for i in range(n):
            _make_failure(task_id=f'{prefix}-{i}')

    def _open_hai(
        self,
        *,
        task_name: str,
        urgency_band: str,
        created_ago: timedelta,
        decided: bool = False,
    ):
        item = HumanAttentionItem.objects.create(
            user=_admin_user(),
            source_type='failure_cluster',
            source_id=f'failure_cluster:{task_name}:synthetic:{urgency_band}',
            source_agent='CeleryTelemetry',
            item_type='alert',
            title='synthetic prior cluster',
            summary='pre-existing HAI for dedup test',
            urgency='critical' if urgency_band == 'critical' else 'high',
            payload={'task_name': task_name, 'urgency_band': urgency_band},
            decided_at=timezone.now() - timedelta(minutes=1) if decided else None,
        )
        HumanAttentionItem.objects.filter(id=item.id).update(
            created_at=timezone.now() - created_ago,
        )
        return item

    def test_recent_open_high_hai_suppresses_high_escalation(self):
        self._prepopulate_failures(4)
        self._open_hai(
            task_name='core.tasks.example',
            urgency_band='high',
            created_ago=timedelta(minutes=15),
        )
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_failure(task_id='post-dedup-trigger')
        mock_bridge.assert_not_called()

    def test_high_dedup_does_not_suppress_critical(self):
        """Rigby SIGN Q3 refinement: dedup on (task_name, urgency_band)
        so a previously-high cluster can still escalate to critical.
        """
        self._open_hai(
            task_name='core.tasks.example',
            urgency_band='high',
            created_ago=timedelta(minutes=15),
        )
        # 14 pre-existing failures + trigger = 15 distinct → critical.
        for i in range(14):
            _make_failure(task_id=f'high-then-crit-{i}')
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_failure(task_id='high-then-crit-trigger')
        mock_bridge.assert_called_once()
        (snapshot,) = mock_bridge.call_args.args
        self.assertEqual(snapshot.urgency_band, 'critical')

    def test_stale_open_hai_beyond_window_does_not_suppress(self):
        self._prepopulate_failures(4)
        self._open_hai(
            task_name='core.tasks.example',
            urgency_band='high',
            created_ago=timedelta(hours=2),
        )
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_failure(task_id='stale-hai-trigger')
        mock_bridge.assert_called_once()

    def test_decided_hai_does_not_suppress(self):
        self._prepopulate_failures(4)
        self._open_hai(
            task_name='core.tasks.example',
            urgency_band='high',
            created_ago=timedelta(minutes=10),
            decided=True,
        )
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_failure(task_id='decided-hai-trigger')
        mock_bridge.assert_called_once()

    def test_different_task_name_does_not_suppress(self):
        """Dedup is task_name-scoped — a cluster on task A does not
        block a cluster on task B."""
        self._open_hai(
            task_name='core.tasks.other',
            urgency_band='high',
            created_ago=timedelta(minutes=15),
        )
        for i in range(4):
            _make_failure(task_id=f'cross-task-pre-{i}')
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_failure(task_id='cross-task-trigger')
        mock_bridge.assert_called_once()

    def test_matching_idempotency_key_suppresses(self):
        """Idempotency-key dedup path (Rigby SIGN post-implementation
        Q2 refinement — narrows near-simultaneous race window)."""
        # Compute a snapshot to learn what idempotency_key would fire
        # for the upcoming FAILURE row.
        self._prepopulate_failures(5, prefix='idk-pre')
        pending_snapshot = compute_cluster('core.tasks.example')

        # Insert a synthetic HAI keyed on that exact idempotency_key
        # but with a task_name / urgency_band that will NOT match the
        # (task_name, urgency_band) fallback (proving the idempotency
        # key alone is sufficient to dedup).
        HumanAttentionItem.objects.create(
            user=_admin_user(),
            source_type='failure_cluster',
            source_id=pending_snapshot.idempotency_key,
            source_agent='CeleryTelemetry',
            item_type='alert',
            title='synthetic idempotency-key dedup',
            summary='prior HAI keyed on idempotency_key only',
            urgency='high',
            payload={
                'idempotency_key': pending_snapshot.idempotency_key,
                'task_name': 'sentinel-not-matching',
                'urgency_band': 'sentinel-not-matching',
            },
        )
        HumanAttentionItem.objects.filter(
            source_id=pending_snapshot.idempotency_key,
        ).update(created_at=timezone.now() - timedelta(minutes=5))

        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
            _make_failure(task_id='idk-trigger')
        mock_bridge.assert_not_called()


class FailureClusterTransactionSafetyTests(TestCase):
    """Escalation gated on transaction.on_commit — no phantom items."""

    def test_rolled_back_transaction_does_not_escalate(self):
        for i in range(4):
            _make_failure(task_id=f'rollback-pre-{i}')
        with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=False):
            _make_failure(task_id='rollback-trigger')
        mock_bridge.assert_not_called()

    def test_dedup_lookup_failure_defaults_to_escalation(self):
        """A raising ``HumanAttentionItem.objects`` from the dedup gate
        must NOT swallow the escalation — safer to duplicate than to
        miss a critical alert."""
        for i in range(4):
            _make_failure(task_id=f'raise-pre-{i}')

        raising_manager = MagicMock()
        raising_manager.filter.side_effect = Exception('simulated DB failure')

        with patch(
            'core.models_human_interface.HumanAttentionItem.objects',
            new=raising_manager,
        ):
            with patch(_BRIDGE_PATH) as mock_bridge, self.captureOnCommitCallbacks(execute=True):
                _make_failure(task_id='raise-trigger')
        mock_bridge.assert_called_once()


class FailureClusterAggregatorSnapshotTests(TestCase):
    """Direct exercise of :func:`compute_cluster` beyond the receiver path."""

    def test_snapshot_carries_diagnostic_dimensions(self):
        finished = timezone.now()
        _make_failure(
            task_id='diag-1', queue='pa', worker='pa@host',
            error_type='ValueError', finished_at=finished,
        )
        _make_failure(
            task_id='diag-2', queue='pa', worker='pa@host',
            error_type='ValueError', finished_at=finished,
        )
        _make_failure(
            task_id='diag-3', queue='default', worker='default@host',
            error_type='KeyError', finished_at=finished,
        )
        snapshot = compute_cluster('core.tasks.example')
        self.assertEqual(snapshot.distinct_task_id_count, 3)
        self.assertEqual(snapshot.total_event_count, 3)
        self.assertEqual(snapshot.distinct_queues, ('default', 'pa'))
        self.assertEqual(snapshot.distinct_workers, ('default@host', 'pa@host'))
        self.assertEqual(snapshot.distinct_error_types, ('KeyError', 'ValueError'))
        self.assertIn('ValueError', snapshot.top_error_signature)
        self.assertFalse(snapshot.exceeds_threshold)  # 3 < threshold=5
        self.assertEqual(snapshot.urgency_band, 'below')

    def test_snapshot_ignores_out_of_window_events(self):
        stale = timezone.now() - timedelta(minutes=30)
        for i in range(10):
            _make_failure(task_id=f'stale-{i}', finished_at=stale)
        fresh = timezone.now()
        _make_failure(task_id='fresh-1', finished_at=fresh)
        snapshot = compute_cluster('core.tasks.example')
        # Only the fresh row falls inside the default 5-min window.
        self.assertEqual(snapshot.distinct_task_id_count, 1)
