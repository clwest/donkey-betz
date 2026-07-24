"""Session 2933 A3 v1 — SignalDispatchService regression coverage.

Covers the Rigby-signed contract from the S2933 SIGN cycle:

  Q1 — scanner shape (periodic, code-driven mapping)
  Q2 — fan-out via per-cluster enqueue (asserted by patched .delay)
  Q3 — fire-once semantics + retry lever (outcome + error_summary)
  Q4 — SignalDispatch audit row shape (rule_key, outcome, agent_execution_id)
  Q5 — v1 hard-coded mappings match SIGNAL_DISPATCH_RULES
  Q6 — throttles (global cap + per-rule daily cap + is_actionable gate)

Tests avoid live LLM calls — AgentRouter.route is patched throughout.
"""
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.utils import timezone

from core.agents.base_agent import AgentResult
from core.models_signal_dispatch import SignalDispatch
from core.models_signal_intelligence import SignalCluster
from core.services.signal_dispatch_service import (
    DEFAULT_MAX_DISPATCHES_PER_SCAN,
    SIGNAL_DISPATCH_RULES,
    SignalDispatchRuleDef,
    SignalDispatchService,
    get_rule,
)


def _make_cluster(pattern_type='trend_emergence', strength=0.7, confidence=0.7, status='active', name=None):
    return SignalCluster.objects.create(
        name=name or f'test-cluster-{pattern_type}',
        pattern_type=pattern_type,
        strength=strength,
        confidence=confidence,
        status=status,
        keywords=['ai', 'signal-dispatch', 'v1'],
    )


class TestSignalDispatchRulesRegistry(TestCase):
    """Q5 — hard-coded v1 mappings match Rigby-verified agent names."""

    def test_v1_ships_trend_and_content_gap_pairs(self):
        keys = {r.key for r in SIGNAL_DISPATCH_RULES}
        self.assertIn('trend_emergence__trend_analysis', keys)
        self.assertIn('content_gap__content_strategy', keys)

    def test_trend_rule_maps_to_TrendAnalysisAgent(self):
        rule = get_rule('trend_emergence__trend_analysis')
        self.assertIsNotNone(rule)
        assert rule is not None  # for pyright
        self.assertEqual(rule.pattern_type, 'trend_emergence')
        self.assertEqual(rule.agent_name, 'TrendAnalysisAgent')

    def test_content_gap_rule_maps_to_ContentStrategyAgent(self):
        rule = get_rule('content_gap__content_strategy')
        self.assertIsNotNone(rule)
        assert rule is not None
        self.assertEqual(rule.pattern_type, 'content_gap')
        self.assertEqual(rule.agent_name, 'ContentStrategyAgent')

    def test_opportunity_window_rule_maps_to_OpportunityScoringAgent(self):
        # S2934 A5: third rule shipped this session.
        rule = get_rule('opportunity_window__opportunity_scoring')
        self.assertIsNotNone(rule)
        assert rule is not None
        self.assertEqual(rule.pattern_type, 'opportunity_window')
        self.assertEqual(rule.agent_name, 'OpportunityScoringAgent')

    def test_s2934_ships_three_rules_total(self):
        # Anchor: v1 shipped 2 rules (trend_emergence + content_gap); S2934
        # added a third (opportunity_window). Anti-regression on registry size.
        self.assertEqual(len(SIGNAL_DISPATCH_RULES), 3)

    def test_get_rule_returns_none_for_unknown(self):
        self.assertIsNone(get_rule('nonexistent__nowhere'))


class TestScanner(TestCase):
    """Q1 / Q2 / Q6 — scanner enqueues, throttles, gates."""

    def setUp(self):
        self.enqueued: list[str] = []

        def _capture_delay(dispatch_id):
            self.enqueued.append(str(dispatch_id))
            return MagicMock()

        self.delay_patcher = patch(
            'core.services.signal_dispatch_service.SignalDispatchService._enqueue',
            side_effect=lambda dispatch_id: self.enqueued.append(str(dispatch_id)),
        )
        self.delay_patcher.start()

    def tearDown(self):
        self.delay_patcher.stop()

    def test_scan_enqueues_dispatch_for_matching_active_cluster(self):
        cluster = _make_cluster(pattern_type='trend_emergence', strength=0.8, confidence=0.7)
        service = SignalDispatchService()
        summary = service.scan_and_dispatch()

        self.assertEqual(summary['enqueued'], 1)
        self.assertEqual(SignalDispatch.objects.count(), 1)
        d = SignalDispatch.objects.get()
        self.assertEqual(d.rule_key, 'trend_emergence__trend_analysis')
        self.assertEqual(d.agent_name, 'TrendAnalysisAgent')
        self.assertEqual(d.signal_cluster_id, cluster.id)
        self.assertEqual(d.outcome, 'queued')
        self.assertEqual(len(self.enqueued), 1)

    def test_scan_skips_cluster_below_min_strength(self):
        _make_cluster(pattern_type='trend_emergence', strength=0.3, confidence=0.7)
        service = SignalDispatchService()
        summary = service.scan_and_dispatch()
        self.assertEqual(summary['enqueued'], 0)
        self.assertEqual(SignalDispatch.objects.count(), 0)

    def test_scan_skips_non_active_cluster(self):
        _make_cluster(pattern_type='trend_emergence', strength=0.8, confidence=0.7, status='detecting')
        service = SignalDispatchService()
        summary = service.scan_and_dispatch()
        self.assertEqual(summary['enqueued'], 0)

    def test_scan_dedups_already_queued_dispatch(self):
        cluster = _make_cluster(pattern_type='trend_emergence', strength=0.8, confidence=0.7)
        service = SignalDispatchService()
        service.scan_and_dispatch()
        service.scan_and_dispatch()  # second scan
        self.assertEqual(SignalDispatch.objects.filter(signal_cluster=cluster).count(), 1)

    def test_scan_re_dispatches_after_prior_failure(self):
        cluster = _make_cluster(pattern_type='trend_emergence', strength=0.8, confidence=0.7)
        SignalDispatch.objects.create(
            rule_key='trend_emergence__trend_analysis',
            pattern_type='trend_emergence',
            agent_name='TrendAnalysisAgent',
            signal_cluster=cluster,
            outcome='failed',
            error_summary='transient err',
        )
        service = SignalDispatchService()
        service.scan_and_dispatch()
        # failed dispatch does NOT block — retry created
        self.assertEqual(SignalDispatch.objects.filter(signal_cluster=cluster).count(), 2)

    @override_settings(SIGNAL_DISPATCH_MAX_PER_SCAN=2)
    def test_scan_enforces_global_cap_per_run(self):
        for i in range(5):
            _make_cluster(pattern_type='trend_emergence', strength=0.9, confidence=0.9, name=f'c{i}')
        service = SignalDispatchService()
        summary = service.scan_and_dispatch()
        self.assertEqual(summary['enqueued'], 2)
        self.assertGreaterEqual(summary['skipped_cap'], 1)

    def test_scan_enforces_per_rule_daily_cap(self):
        rule = get_rule('trend_emergence__trend_analysis')
        assert rule is not None
        # Seed 10 recent succeeded rows to hit max_per_day=10
        seed_cluster = _make_cluster(pattern_type='trend_emergence', strength=0.8, confidence=0.7, name='seed')
        for i in range(rule.max_per_day):
            SignalDispatch.objects.create(
                rule_key=rule.key,
                pattern_type='trend_emergence',
                agent_name='TrendAnalysisAgent',
                signal_cluster=seed_cluster,
                outcome='succeeded',
            )
        # Now create a fresh eligible cluster
        _make_cluster(pattern_type='trend_emergence', strength=0.95, confidence=0.9, name='fresh')
        service = SignalDispatchService()
        summary = service.scan_and_dispatch()
        # Fresh cluster should NOT dispatch because per-rule daily cap already reached
        self.assertEqual(summary['per_rule'].get('trend_emergence__trend_analysis', 0), 0)

    @override_settings(SIGNAL_DISPATCH_ENABLED=False)
    def test_scan_short_circuits_when_kill_switch_off(self):
        _make_cluster(pattern_type='trend_emergence', strength=0.9, confidence=0.9)
        service = SignalDispatchService()
        summary = service.scan_and_dispatch()
        self.assertEqual(summary['enqueued'], 0)
        self.assertTrue(summary.get('disabled'))
        self.assertEqual(SignalDispatch.objects.count(), 0)

    def test_scan_default_global_cap_matches_documented(self):
        # Sanity: DEFAULT_MAX_DISPATCHES_PER_SCAN is what code documents to Chris.
        self.assertEqual(DEFAULT_MAX_DISPATCHES_PER_SCAN, 10)


class TestExecuteDispatch(TestCase):
    """Q3 / Q4 — per-dispatch executor writes outcome + error_summary."""

    def _make_dispatch(self, rule_key='trend_emergence__trend_analysis', pattern_type='trend_emergence'):
        cluster = _make_cluster(pattern_type=pattern_type, strength=0.8, confidence=0.7)
        rule = get_rule(rule_key)
        assert rule is not None
        return SignalDispatch.objects.create(
            rule_key=rule.key,
            pattern_type=cluster.pattern_type,
            agent_name=rule.agent_name,
            signal_cluster=cluster,
            outcome='queued',
            input_payload={'dispatch_source': 'signal_dispatch_v1'},
        )

    def test_success_result_marks_dispatch_succeeded_with_execution_id(self):
        import uuid as _uuid
        exec_id = _uuid.uuid4()
        d = self._make_dispatch()
        fake_result = AgentResult(success=True, message='ok', execution_id=str(exec_id))
        with patch('core.agent_router.AgentRouter') as MockRouter:
            router_inst = MockRouter.return_value
            router_inst.AGENT_MAP = {'TrendAnalysisAgent': object}
            router_inst.route.return_value = fake_result
            result = SignalDispatchService().execute_dispatch(str(d.id))

        d.refresh_from_db()
        self.assertEqual(d.outcome, 'succeeded')
        self.assertEqual(str(d.agent_execution_id), str(exec_id))
        self.assertIsNotNone(d.completed_at)
        self.assertEqual(result['outcome'], 'succeeded')

    def test_failed_result_marks_failed_with_error_summary(self):
        d = self._make_dispatch()
        fake_result = AgentResult(success=False, error='downstream tool timeout')
        with patch('core.agent_router.AgentRouter') as MockRouter:
            router_inst = MockRouter.return_value
            router_inst.AGENT_MAP = {'TrendAnalysisAgent': object}
            router_inst.route.return_value = fake_result
            SignalDispatchService().execute_dispatch(str(d.id))

        d.refresh_from_db()
        self.assertEqual(d.outcome, 'failed')
        self.assertIn('downstream tool timeout', d.error_summary)
        self.assertIsNotNone(d.completed_at)

    def test_agent_not_in_registry_marks_rejected_agent_missing(self):
        d = self._make_dispatch()
        with patch('core.agent_router.AgentRouter') as MockRouter:
            router_inst = MockRouter.return_value
            router_inst.AGENT_MAP = {}  # empty registry
            SignalDispatchService().execute_dispatch(str(d.id))

        d.refresh_from_db()
        self.assertEqual(d.outcome, 'rejected_agent_missing')
        self.assertIn('TrendAnalysisAgent', d.error_summary)

    def test_unknown_rule_key_marks_rejected_unknown_rule(self):
        cluster = _make_cluster(pattern_type='trend_emergence', strength=0.8, confidence=0.7)
        d = SignalDispatch.objects.create(
            rule_key='ghost__nowhere',
            pattern_type='trend_emergence',
            agent_name='Whatever',
            signal_cluster=cluster,
            outcome='queued',
        )
        SignalDispatchService().execute_dispatch(str(d.id))
        d.refresh_from_db()
        self.assertEqual(d.outcome, 'rejected_unknown_rule')
        self.assertIn('ghost__nowhere', d.error_summary)

    def test_router_exception_marks_failed_not_stranded(self):
        """Rigby Q3 F-BLOCKING — transient exception must record + allow retry, not strand."""
        d = self._make_dispatch()
        with patch('core.agent_router.AgentRouter') as MockRouter:
            router_inst = MockRouter.return_value
            router_inst.AGENT_MAP = {'TrendAnalysisAgent': object}
            router_inst.route.side_effect = RuntimeError('boom')
            SignalDispatchService().execute_dispatch(str(d.id))

        d.refresh_from_db()
        self.assertEqual(d.outcome, 'failed')
        self.assertIn('RuntimeError', d.error_summary)
        self.assertIn('boom', d.error_summary)


class TestPayloadShape(TestCase):
    """Q2 — payload sent to agent carries structured cluster context (Rigby recommendation)."""

    def test_payload_includes_structured_cluster_fields(self):
        cluster = _make_cluster(pattern_type='content_gap', strength=0.6, confidence=0.55)
        rule = get_rule('content_gap__content_strategy')
        assert rule is not None
        payload = SignalDispatchService()._build_payload(rule, cluster)
        self.assertEqual(payload['dispatch_source'], 'signal_dispatch_v1')
        self.assertEqual(payload['rule_key'], rule.key)
        self.assertEqual(payload['pattern_type'], 'content_gap')
        self.assertEqual(payload['cluster_id'], str(cluster.id))
        self.assertIn('keywords', payload)
        self.assertIn('strength', payload)
        self.assertIn('confidence', payload)


class TestDedupIsPerRulePerCluster(TestCase):
    """Multiple rules can dispatch on the same cluster (per Rigby Q5 shape)."""

    def test_two_rules_on_same_cluster_both_dispatch_once(self):
        # Add a temporary custom rule so both rules match the same pattern_type
        extra = SignalDispatchRuleDef(
            key='trend_emergence__extra',
            pattern_type='trend_emergence',
            agent_name='TrendAnalysisAgent',
            max_per_day=10,
        )
        cluster = _make_cluster(pattern_type='trend_emergence', strength=0.8, confidence=0.7)

        with patch(
            'core.services.signal_dispatch_service.SignalDispatchService._enqueue',
            lambda self, dispatch_id: None,
        ):
            service = SignalDispatchService(rules=(*SIGNAL_DISPATCH_RULES, extra))
            summary = service.scan_and_dispatch()

        # Only the base rule matches (trend_emergence__trend_analysis) + the extra
        # both matching pattern_type=trend_emergence should dispatch once each.
        self.assertEqual(
            SignalDispatch.objects.filter(signal_cluster=cluster).count(),
            2,
        )
        self.assertEqual(summary['enqueued'], 2)
