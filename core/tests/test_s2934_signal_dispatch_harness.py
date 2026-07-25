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


class TestSignalDispatchResolveClusterEndpoint(TestCase):
    """S2947 A8 — GET /api/v1/agents/signal-dispatches/resolve-cluster/<uuid>/"""

    def setUp(self):
        self.user = User.objects.create_user(username='sd-resolve', password='x')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_returns_cluster_metadata_and_matching_rules(self):
        cluster = _make_cluster(pattern_type='trend_emergence', strength=0.75, confidence=0.6)
        url = reverse('signal-dispatch-resolve-cluster', args=[str(cluster.id)])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body['success'])
        data = body['data']
        self.assertEqual(data['id'], str(cluster.id))
        self.assertEqual(data['pattern_type'], 'trend_emergence')
        self.assertEqual(data['strength'], 0.75)
        self.assertEqual(data['confidence'], 0.6)
        self.assertEqual(data['status'], 'active')
        self.assertTrue(data['is_actionable'])
        rule_keys = {r['key'] for r in data['matching_rules']}
        self.assertIn('trend_emergence__trend_analysis', rule_keys)

    def test_returns_empty_matching_rules_for_unmapped_pattern(self):
        cluster = _make_cluster(pattern_type='sentiment_shift')
        url = reverse('signal-dispatch-resolve-cluster', args=[str(cluster.id)])
        resp = self.client.get(url)
        body = resp.json()
        self.assertTrue(body['success'])
        self.assertEqual(body['data']['matching_rules'], [])

    def test_returns_404_for_unknown_cluster(self):
        url = reverse('signal-dispatch-resolve-cluster', args=['00000000-0000-0000-0000-000000000000'])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        body = resp.json()
        self.assertFalse(body['success'])
        self.assertEqual(body['error_code'], 'cluster_not_found')


class TestSignalDispatchesManualEndpoint(TestCase):
    """S2947 A8 — POST /api/v1/agents/signal-dispatches/manual/"""

    def setUp(self):
        self.user = User.objects.create_user(username='sd-manual', password='x')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('signal-dispatches-manual')

    def test_missing_cluster_id_returns_400(self):
        resp = self.client.post(self.url, {}, format='json')
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertEqual(body['error_code'], 'missing_cluster_id')

    def test_auto_picks_rule_and_enqueues(self):
        cluster = _make_cluster(pattern_type='trend_emergence')
        with patch('core.tasks.dispatch_agent_for_signal_cluster.delay') as mock_delay:
            resp = self.client.post(self.url, {'cluster_id': str(cluster.id)}, format='json')
        self.assertEqual(resp.status_code, 201)
        body = resp.json()
        self.assertTrue(body['success'])
        self.assertEqual(body['rule_key'], 'trend_emergence__trend_analysis')
        self.assertEqual(body['agent_name'], 'TrendAnalysisAgent')
        self.assertEqual(body['cluster_id'], str(cluster.id))
        mock_delay.assert_called_once_with(body['dispatch_id'])
        row = SignalDispatch.objects.get(id=body['dispatch_id'])
        self.assertEqual(row.scan_run_id, 'manual')
        self.assertEqual(row.outcome, 'queued')

    def test_explicit_rule_key_pattern_mismatch_returns_400(self):
        cluster = _make_cluster(pattern_type='trend_emergence')
        resp = self.client.post(
            self.url,
            {'cluster_id': str(cluster.id), 'rule_key': 'content_gap__content_strategy'},
            format='json',
        )
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertEqual(body['error_code'], 'rule_pattern_mismatch')

    def test_unknown_rule_key_returns_400(self):
        cluster = _make_cluster(pattern_type='trend_emergence')
        resp = self.client.post(
            self.url,
            {'cluster_id': str(cluster.id), 'rule_key': 'nope__nope'},
            format='json',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['error_code'], 'unknown_rule_key')

    def test_no_matching_rule_returns_400(self):
        cluster = _make_cluster(pattern_type='sentiment_shift')
        resp = self.client.post(self.url, {'cluster_id': str(cluster.id)}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json()['error_code'], 'no_matching_rule')

    def test_unknown_cluster_returns_404(self):
        resp = self.client.post(
            self.url,
            {'cluster_id': '00000000-0000-0000-0000-000000000000'},
            format='json',
        )
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()['error_code'], 'cluster_not_found')

    def test_idempotent_guard_returns_409(self):
        cluster = _make_cluster(pattern_type='trend_emergence')
        rule = get_rule('trend_emergence__trend_analysis')
        assert rule is not None
        existing = SignalDispatch.objects.create(
            rule_key=rule.key,
            pattern_type=cluster.pattern_type,
            agent_name=rule.agent_name,
            signal_cluster=cluster,
            outcome='succeeded',
            scan_run_id='previous_scan',
        )
        resp = self.client.post(self.url, {'cluster_id': str(cluster.id)}, format='json')
        self.assertEqual(resp.status_code, 409)
        body = resp.json()
        self.assertEqual(body['error_code'], 'guard_blocked')
        self.assertEqual(body['existing_dispatch_id'], str(existing.id))
        # No new row created.
        self.assertEqual(
            SignalDispatch.objects.filter(signal_cluster=cluster).count(), 1,
        )

    def test_api_does_not_expose_force_param(self):
        """v1 policy: force must NOT be honorable via the API."""
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
        # Even with force=True in the body, guard must still block.
        resp = self.client.post(
            self.url,
            {'cluster_id': str(cluster.id), 'force': True},
            format='json',
        )
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(resp.json()['error_code'], 'guard_blocked')


class TestSignalDispatchesEligibleEndpoint(TestCase):
    """S2948 NEW-4 — GET /api/v1/agents/signal-dispatches/eligible/"""

    def setUp(self):
        self.user = User.objects.create_user(username='sd-elig', password='x')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = reverse('signal-dispatches-eligible')

    def test_returns_active_clusters_with_matching_rules(self):
        c1 = _make_cluster(pattern_type='trend_emergence', name='trend-a', strength=0.8)
        c2 = _make_cluster(pattern_type='content_gap', name='gap-b', strength=0.6)
        # Cluster whose pattern has no rule — should NOT appear.
        _make_cluster(pattern_type='sentiment_shift', name='sent-c')
        # Detecting cluster — should NOT appear (only active).
        _make_cluster(pattern_type='trend_emergence', name='trend-d', status='detecting')

        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body['success'])
        ids = {row['id'] for row in body['data']['eligible']}
        self.assertEqual(ids, {str(c1.id), str(c2.id)})

    def test_orders_by_strength_desc(self):
        low = _make_cluster(pattern_type='trend_emergence', name='low', strength=0.55)
        high = _make_cluster(pattern_type='trend_emergence', name='high', strength=0.9)
        mid = _make_cluster(pattern_type='trend_emergence', name='mid', strength=0.7)

        resp = self.client.get(self.url)
        rows = resp.json()['data']['eligible']
        self.assertEqual([r['id'] for r in rows], [str(high.id), str(mid.id), str(low.id)])

    def test_pattern_type_filter(self):
        _make_cluster(pattern_type='trend_emergence', name='trend-only')
        gap = _make_cluster(pattern_type='content_gap', name='gap-only')
        resp = self.client.get(self.url, {'pattern_type': 'content_gap'})
        rows = resp.json()['data']['eligible']
        self.assertEqual([r['id'] for r in rows], [str(gap.id)])

    def test_matching_rules_populated(self):
        c = _make_cluster(pattern_type='trend_emergence', name='trend-r')
        resp = self.client.get(self.url)
        rows = resp.json()['data']['eligible']
        self.assertEqual(len(rows), 1)
        rules = rows[0]['matching_rules']
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]['key'], 'trend_emergence__trend_analysis')
        self.assertEqual(rules[0]['agent_name'], 'TrendAnalysisAgent')

    def test_guard_blocked_hidden_by_default(self):
        c = _make_cluster(pattern_type='trend_emergence', name='blocked')
        rule = get_rule('trend_emergence__trend_analysis')
        assert rule is not None
        # Recent non-failed dispatch → guard-blocks the only matching rule
        SignalDispatch.objects.create(
            rule_key=rule.key,
            pattern_type=c.pattern_type,
            agent_name=rule.agent_name,
            signal_cluster=c,
            outcome='succeeded',
            scan_run_id='previous',
        )
        resp = self.client.get(self.url)
        self.assertEqual(resp.json()['data']['eligible'], [])

    def test_include_blocked_surfaces_them_with_flag(self):
        c = _make_cluster(pattern_type='trend_emergence', name='blocked-visible')
        rule = get_rule('trend_emergence__trend_analysis')
        assert rule is not None
        SignalDispatch.objects.create(
            rule_key=rule.key,
            pattern_type=c.pattern_type,
            agent_name=rule.agent_name,
            signal_cluster=c,
            outcome='succeeded',
            scan_run_id='previous',
        )
        resp = self.client.get(self.url, {'include_blocked': 'true'})
        rows = resp.json()['data']['eligible']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['guard_blocked_rules'], [rule.key])

    def test_limit_capped_at_200(self):
        _make_cluster(pattern_type='trend_emergence', name='one')
        resp = self.client.get(self.url, {'limit': 9999})
        self.assertEqual(resp.json()['data']['limit'], 200)
