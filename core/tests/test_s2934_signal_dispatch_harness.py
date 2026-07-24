"""Session 2934 A7 + A4 regression tests.

Covers:
  - `manage.py dispatch_signal` — on-demand harness with idempotent
    guard + --force + --sync + explicit --rule-key + auto-pick logic.
  - `/api/v1/agents/signal-dispatches/` — read-only list endpoint
    with limit/offset/filter shape.
"""
from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from core.models_signal_dispatch import SignalDispatch
from core.models_signal_intelligence import SignalCluster
from core.services.signal_dispatch_service import get_rule

User = get_user_model()


def _make_cluster(pattern_type='trend_emergence', **overrides):
    defaults = dict(
        name=f'test-cluster-{pattern_type}',
        pattern_type=pattern_type,
        strength=0.7,
        confidence=0.7,
        status='active',
        keywords=['a', 'b'],
    )
    defaults.update(overrides)
    return SignalCluster.objects.create(**defaults)


class TestDispatchSignalCommand(TestCase):
    """A7 — mgmt command shape + safety conditions."""

    def _run(self, **opts):
        buf = StringIO()
        call_command('dispatch_signal', stdout=buf, **opts)
        return buf.getvalue()

    def test_creates_dispatch_labeled_manual_when_rule_auto_picked(self):
        cluster = _make_cluster(pattern_type='trend_emergence')
        # Async path: mock the Celery enqueue so the test doesn't hit a worker.
        with patch('core.tasks.dispatch_agent_for_signal_cluster.delay') as mock_delay:
            out = self._run(cluster_id=str(cluster.id))

        self.assertIn('Created manual dispatch', out)
        self.assertIn('Enqueued to Celery', out)
        mock_delay.assert_called_once()

        row = SignalDispatch.objects.get(signal_cluster=cluster)
        self.assertEqual(row.scan_run_id, 'manual')
        self.assertEqual(row.rule_key, 'trend_emergence__trend_analysis')
        self.assertEqual(row.outcome, 'queued')

    def test_explicit_rule_key_that_mismatches_cluster_pattern_errors(self):
        cluster = _make_cluster(pattern_type='trend_emergence')
        with self.assertRaises(CommandError) as ctx:
            self._run(
                cluster_id=str(cluster.id),
                rule_key='content_gap__content_strategy',
            )
        self.assertIn("pattern_type='content_gap'", str(ctx.exception))

    def test_no_matching_rule_errors(self):
        cluster = _make_cluster(pattern_type='sentiment_shift')
        with self.assertRaises(CommandError) as ctx:
            self._run(cluster_id=str(cluster.id))
        self.assertIn('No rule in SIGNAL_DISPATCH_RULES matches', str(ctx.exception))

    def test_unknown_cluster_id_errors(self):
        with self.assertRaises(CommandError) as ctx:
            self._run(cluster_id='00000000-0000-0000-0000-000000000000')
        self.assertIn('not found', str(ctx.exception))

    def test_idempotent_guard_blocks_re_dispatch_within_window(self):
        cluster = _make_cluster(pattern_type='trend_emergence')
        rule = get_rule('trend_emergence__trend_analysis')
        assert rule is not None
        # Seed a recent succeeded dispatch inside the guard window.
        SignalDispatch.objects.create(
            rule_key=rule.key,
            pattern_type=cluster.pattern_type,
            agent_name=rule.agent_name,
            signal_cluster=cluster,
            outcome='succeeded',
            scan_run_id='previous_scan',
        )
        with self.assertRaises(CommandError) as ctx:
            self._run(cluster_id=str(cluster.id))
        self.assertIn('Idempotent guard', str(ctx.exception))
        # And no new row created
        self.assertEqual(
            SignalDispatch.objects.filter(signal_cluster=cluster).count(), 1,
        )

    def test_idempotent_guard_permits_after_failed_prior(self):
        # Failed dispatches don't block — matches scanner semantics.
        cluster = _make_cluster(pattern_type='trend_emergence')
        rule = get_rule('trend_emergence__trend_analysis')
        assert rule is not None
        SignalDispatch.objects.create(
            rule_key=rule.key,
            pattern_type=cluster.pattern_type,
            agent_name=rule.agent_name,
            signal_cluster=cluster,
            outcome='failed',
            error_summary='transient',
            scan_run_id='previous_scan',
        )
        with patch('core.tasks.dispatch_agent_for_signal_cluster.delay'):
            self._run(cluster_id=str(cluster.id))
        # New manual row created alongside the failed one
        rows = SignalDispatch.objects.filter(signal_cluster=cluster).order_by('dispatched_at')
        self.assertEqual(rows.count(), 2)
        self.assertEqual(rows[0].outcome, 'failed')
        self.assertEqual(rows[1].scan_run_id, 'manual')

    def test_force_bypasses_idempotent_guard(self):
        cluster = _make_cluster(pattern_type='trend_emergence')
        rule = get_rule('trend_emergence__trend_analysis')
        assert rule is not None
        SignalDispatch.objects.create(
            rule_key=rule.key,
            pattern_type=cluster.pattern_type,
            agent_name=rule.agent_name,
            signal_cluster=cluster,
            outcome='succeeded',
            scan_run_id='previous_scan',
        )
        with patch('core.tasks.dispatch_agent_for_signal_cluster.delay'):
            self._run(cluster_id=str(cluster.id), force=True)
        self.assertEqual(
            SignalDispatch.objects.filter(signal_cluster=cluster).count(), 2,
        )

    def test_guard_window_ignores_dispatches_older_than_window(self):
        cluster = _make_cluster(pattern_type='trend_emergence')
        rule = get_rule('trend_emergence__trend_analysis')
        assert rule is not None
        old = SignalDispatch.objects.create(
            rule_key=rule.key,
            pattern_type=cluster.pattern_type,
            agent_name=rule.agent_name,
            signal_cluster=cluster,
            outcome='succeeded',
            scan_run_id='previous_scan',
        )
        # Backdate past the default 5-min window
        SignalDispatch.objects.filter(id=old.id).update(
            dispatched_at=timezone.now() - timedelta(hours=1),
        )
        with patch('core.tasks.dispatch_agent_for_signal_cluster.delay'):
            self._run(cluster_id=str(cluster.id))
        self.assertEqual(
            SignalDispatch.objects.filter(signal_cluster=cluster).count(), 2,
        )

    def test_sync_flag_executes_inline(self):
        cluster = _make_cluster(pattern_type='trend_emergence')
        with patch(
            'core.services.signal_dispatch_service.SignalDispatchService.execute_dispatch',
            return_value={'outcome': 'succeeded', 'dispatch_id': 'stub'},
        ) as mock_exec:
            out = self._run(cluster_id=str(cluster.id), sync=True)
        mock_exec.assert_called_once()
        self.assertIn('Sync result', out)


class TestSignalDispatchesListEndpoint(TestCase):
    """A4 — /api/v1/agents/signal-dispatches/ shape + filters."""

    def setUp(self):
        self.user = User.objects.create_user(username='sd-tester', password='x')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def _seed(self, n=3, pattern_type='trend_emergence', outcome='succeeded'):
        rows = []
        for i in range(n):
            cluster = _make_cluster(pattern_type=pattern_type, name=f'c-{i}')
            rule = get_rule('trend_emergence__trend_analysis') if pattern_type == 'trend_emergence' else get_rule('content_gap__content_strategy')
            assert rule is not None
            rows.append(SignalDispatch.objects.create(
                rule_key=rule.key,
                pattern_type=pattern_type,
                agent_name=rule.agent_name,
                signal_cluster=cluster,
                outcome=outcome,
                scan_run_id=f'scan-{i}',
            ))
        return rows

    def test_returns_success_envelope_and_row_shape(self):
        self._seed(n=2)
        url = reverse('signal-dispatches-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body['success'])
        self.assertEqual(body['data']['total_count'], 2)
        row = body['data']['dispatches'][0]
        for field in [
            'id', 'rule_key', 'pattern_type', 'agent_name', 'outcome',
            'error_summary', 'signal_cluster_id', 'signal_cluster_name',
            'agent_execution_id', 'scan_run_id', 'dispatched_at',
            'completed_at', 'input_payload',
        ]:
            self.assertIn(field, row, f"missing field: {field}")

    def test_pattern_type_filter(self):
        self._seed(n=2, pattern_type='trend_emergence')
        self._seed(n=3, pattern_type='content_gap')
        url = reverse('signal-dispatches-list')
        resp = self.client.get(url, {'pattern_type': 'content_gap'})
        body = resp.json()
        self.assertEqual(body['data']['total_count'], 3)
        for row in body['data']['dispatches']:
            self.assertEqual(row['pattern_type'], 'content_gap')

    def test_outcome_filter(self):
        self._seed(n=2, outcome='succeeded')
        self._seed(n=1, outcome='failed')
        url = reverse('signal-dispatches-list')
        resp = self.client.get(url, {'outcome': 'failed'})
        body = resp.json()
        self.assertEqual(body['data']['total_count'], 1)
        self.assertEqual(body['data']['dispatches'][0]['outcome'], 'failed')

    def test_pagination_shape(self):
        self._seed(n=30)
        url = reverse('signal-dispatches-list')
        resp = self.client.get(url, {'limit': 10, 'offset': 0})
        body = resp.json()
        self.assertEqual(body['data']['count'], 10)
        self.assertEqual(body['data']['total_count'], 30)
        self.assertTrue(body['data']['has_more'])

        resp2 = self.client.get(url, {'limit': 10, 'offset': 25})
        body2 = resp2.json()
        self.assertEqual(body2['data']['count'], 5)
        self.assertFalse(body2['data']['has_more'])

    def test_limit_capped_at_200(self):
        self._seed(n=3)
        url = reverse('signal-dispatches-list')
        resp = self.client.get(url, {'limit': 9999})
        body = resp.json()
        self.assertEqual(body['data']['limit'], 200)
