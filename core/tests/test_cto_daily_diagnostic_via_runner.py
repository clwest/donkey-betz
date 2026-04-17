"""
CTO daily diagnostic — behavior equivalence to Session 1093 implementation
===========================================================================

Session 1094 refactored the ~580-line CTO-specific implementation in
core/tasks_ops.py into:
  - a generic scheduled_diagnostic_runner primitive
  - a CTO-specific config module (core/services/diagnostics/cto_daily.py)
  - a ~60-line delegation shim still in core/tasks_ops.py

This test proves the refactor is behavior-preserving: same env vars,
same gate behavior, same Template v1 body shape, same cache key prefix
(`cto_diag:*`), same MT date bucket, same structured payload keys.

Where the original tests already exist elsewhere (e.g. test_cto_gate_evaluator
or similar), we keep those. This file adds end-to-end coverage of the
integration surface — the glue between the CTO config and the runner.

Run:
    python manage.py test core.tests.test_cto_daily_diagnostic_via_runner -v2
"""

from datetime import datetime, timedelta, timezone as dt_tz
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from core.services.diagnostics.cto_daily import (
    build_agent_prompt,
    build_config,
    build_dedupe_payload,
    build_headline,
    build_title,
    evaluate_gate,
    render_24h_metrics,
    render_new_signatures,
    render_top_failing_agents,
    render_top_signatures,
)


def _synthetic_metrics_clean():
    """Metrics below all thresholds — gate should NOT trip."""
    return {
        'window_24h': {
            'total': 100, 'failed': 3, 'fail_rate': 0.03,
            'timeout_failed': 1,
            'since': 'x', 'until': 'y',
        },
        'window_7d': {
            'total': 700, 'failed': 20, 'fail_rate': 0.029,
            'since': 'x', 'until': 'y',
        },
        'delta_vs_7d': 0.001,
        'top_failing_agents_24h': [{'agent__name': 'A', 'count': 2}],
        'agent_7d_failed_counts': {'A': 14},
        'top_signatures_24h': [],
        'new_signatures_24h': [],
    }


def _synthetic_metrics_high_failrate():
    """Metrics with 8% fail rate — GLOBAL_FAILRATE_HIGH trips."""
    return {
        'window_24h': {
            'total': 200, 'failed': 16, 'fail_rate': 0.08,
            'timeout_failed': 5,
            'since': 'x', 'until': 'y',
        },
        'window_7d': {
            'total': 1400, 'failed': 70, 'fail_rate': 0.05,
            'since': 'x', 'until': 'y',
        },
        'delta_vs_7d': 0.03,
        'top_failing_agents_24h': [
            {'agent__name': 'Alpha', 'count': 10},
            {'agent__name': 'Beta', 'count': 6},
        ],
        'agent_7d_failed_counts': {'Alpha': 14, 'Beta': 21},
        'top_signatures_24h': [
            {'task_name': 'task.a', 'error_type': 'TimeoutError', 'count': 5},
            {'task_name': 'task.b', 'error_type': 'ConnectionError', 'count': 3},
        ],
        'new_signatures_24h': [],
    }


def _synthetic_metrics_critical():
    """Metrics at 12% fail rate — GLOBAL_FAILRATE_CRIT trips."""
    m = _synthetic_metrics_high_failrate()
    m['window_24h']['failed'] = 24
    m['window_24h']['fail_rate'] = 0.12
    m['delta_vs_7d'] = 0.07
    return m


# =============================================================================
# Gate evaluator — preserved behavior
# =============================================================================

class CtoGateEvaluatorTests(SimpleTestCase):

    def test_insufficient_data_under_threshold(self):
        metrics = _synthetic_metrics_clean()
        metrics['window_24h']['total'] = 10  # under default min_total=50
        gate = evaluate_gate(metrics)
        self.assertFalse(gate['tripped'])
        self.assertIn('INSUFFICIENT_DATA', gate['reasons'])

    def test_clean_metrics_no_trip(self):
        gate = evaluate_gate(_synthetic_metrics_clean())
        self.assertFalse(gate['tripped'])
        self.assertIsNone(gate['severity'])

    def test_high_failrate_trips_high(self):
        gate = evaluate_gate(_synthetic_metrics_high_failrate())
        self.assertTrue(gate['tripped'])
        self.assertEqual(gate['severity'], 'high')
        self.assertIn('GLOBAL_FAILRATE_HIGH', gate['reasons'])

    def test_critical_failrate_trips_critical(self):
        gate = evaluate_gate(_synthetic_metrics_critical())
        self.assertTrue(gate['tripped'])
        self.assertEqual(gate['severity'], 'critical')
        self.assertIn('GLOBAL_FAILRATE_CRIT', gate['reasons'])

    def test_delta_gate_adds_reason(self):
        metrics = _synthetic_metrics_high_failrate()
        # delta is 0.03 which is > 0.02 threshold
        gate = evaluate_gate(metrics)
        self.assertIn('DELTA_VS_7D_HIGH', gate['reasons'])

    def test_agent_spike_detection(self):
        metrics = _synthetic_metrics_high_failrate()
        # Alpha: 10 fails in 24h, 7d daily avg = 14/7 = 2 → spike_floor = 6.
        #   10 >= 6 AND 10 >= 5 (agent_spike_min) → SPIKE.
        # Beta: 6 fails in 24h, 7d daily avg = 21/7 = 3 → spike_floor = 9.
        #   6 < 9 → NOT a spike.
        gate = evaluate_gate(metrics)
        self.assertIn('AGENT_SPIKE', gate['reasons'])
        self.assertEqual(len(gate.get('spiking_agents', [])), 1)
        self.assertEqual(gate['spiking_agents'][0]['agent'], 'Alpha')

    def test_new_signature_high_gate(self):
        metrics = _synthetic_metrics_clean()
        metrics['window_24h']['total'] = 200
        metrics['new_signatures_24h'] = [
            {'task_name': 'task.x', 'error_type': 'NewError', 'count': 8},
        ]
        gate = evaluate_gate(metrics)
        self.assertIn('NEW_SIGNATURE_HIGH', gate['reasons'])

    def test_new_signature_critical_gate(self):
        metrics = _synthetic_metrics_clean()
        metrics['window_24h']['total'] = 200
        metrics['new_signatures_24h'] = [
            {'task_name': 'task.x', 'error_type': 'NewError', 'count': 8},
            {'task_name': 'task.y', 'error_type': 'AnotherError', 'count': 10},
        ]
        gate = evaluate_gate(metrics)
        self.assertIn('NEW_SIGNATURE_CRIT', gate['reasons'])
        self.assertEqual(gate['severity'], 'critical')


# =============================================================================
# Section renderers
# =============================================================================

class CtoSectionRenderersTests(SimpleTestCase):

    def test_render_24h_metrics_format(self):
        metrics = _synthetic_metrics_high_failrate()
        lines = render_24h_metrics(metrics, {})
        self.assertEqual(len(lines), 4)
        self.assertIn('Total executions: 200', lines[0])
        self.assertIn('8.00%', lines[1])  # fail_rate formatted
        self.assertIn('+3.00pp', lines[2])  # delta
        self.assertIn('Timeout failures: 5', lines[3])

    def test_render_top_failing_agents_truncates_to_5(self):
        metrics = _synthetic_metrics_high_failrate()
        metrics['top_failing_agents_24h'] = [
            {'agent__name': f'Agent{i}', 'count': i}
            for i in range(10)
        ]
        lines = render_top_failing_agents(metrics, {})
        self.assertEqual(len(lines), 5)

    def test_render_top_signatures_format(self):
        metrics = _synthetic_metrics_high_failrate()
        lines = render_top_signatures(metrics, {})
        self.assertEqual(len(lines), 2)
        self.assertIn('`task.a`', lines[0])
        self.assertIn('`TimeoutError`', lines[0])

    def test_render_new_signatures_empty_returns_empty(self):
        metrics = _synthetic_metrics_high_failrate()
        lines = render_new_signatures(metrics, {})
        self.assertEqual(lines, [])

    def test_render_new_signatures_with_data(self):
        metrics = _synthetic_metrics_high_failrate()
        metrics['new_signatures_24h'] = [
            {'task_name': 'task.x', 'error_type': 'E', 'count': 7},
        ]
        lines = render_new_signatures(metrics, {})
        self.assertEqual(len(lines), 1)
        self.assertIn('task.x', lines[0])


# =============================================================================
# Headline + title
# =============================================================================

class CtoHeadlineTitleTests(SimpleTestCase):

    def test_headline_format(self):
        metrics = _synthetic_metrics_high_failrate()
        gate = {'severity': 'high', 'reasons': ['GLOBAL_FAILRATE_HIGH']}
        headline = build_headline(metrics, gate)
        self.assertIn('HIGH', headline)
        self.assertIn('8.0%', headline)
        self.assertIn('+3.0pp', headline)
        self.assertIn('`GLOBAL_FAILRATE_HIGH`', headline)

    def test_title_includes_date_label(self):
        metrics = _synthetic_metrics_critical()
        gate = {'severity': 'critical', 'reasons': ['GLOBAL_FAILRATE_CRIT']}
        title = build_title(metrics, gate, '2026-04-16')
        self.assertIn('CTO Daily Diagnostic', title)
        self.assertIn('2026-04-16', title)
        self.assertIn('CRITICAL', title)
        self.assertIn('12.0%', title)


# =============================================================================
# Dedupe payload shape (preserved from Session 1093)
# =============================================================================

class CtoDedupePayloadTests(SimpleTestCase):

    def test_payload_shape(self):
        metrics = _synthetic_metrics_high_failrate()
        gate = {'severity': 'high', 'reasons': ['R1', 'R2']}
        payload = build_dedupe_payload(metrics, gate, '2026-04-16')
        self.assertEqual(payload['date_bucket'], '2026-04-16')
        self.assertEqual(payload['severity'], 'high')
        self.assertEqual(payload['gate_reasons'], ['R1', 'R2'])  # sorted
        # Rounded to 3 digits
        self.assertEqual(payload['fail_rate_24h'], 0.08)
        self.assertEqual(payload['delta_vs_7d'], 0.03)
        # Top agents / signatures are tuples
        self.assertEqual(payload['top_agents'][0], ('Alpha', 10))
        self.assertEqual(payload['top_signatures'][0], ('task.a', 'TimeoutError', 5))

    def test_sort_reasons_stable(self):
        gate1 = {'severity': 'high', 'reasons': ['A', 'B']}
        gate2 = {'severity': 'high', 'reasons': ['B', 'A']}  # different order
        p1 = build_dedupe_payload(_synthetic_metrics_clean(), gate1, 'd')
        p2 = build_dedupe_payload(_synthetic_metrics_clean(), gate2, 'd')
        self.assertEqual(p1['gate_reasons'], p2['gate_reasons'])


# =============================================================================
# Config wiring
# =============================================================================

class CtoConfigTests(SimpleTestCase):

    def test_config_identity_fields(self):
        config = build_config()
        self.assertEqual(config.name, 'cto_daily_diagnostic')
        self.assertEqual(config.diagnostic_type, 'cto_daily_diagnostic')
        self.assertEqual(config.agent_name, 'CTOAgent')
        self.assertEqual(config.source_agent, 'CTOAgent')
        self.assertEqual(config.cache_key_prefix, 'cto_diag')
        self.assertEqual(config.enabled_env, 'CTO_DIAGNOSTIC_ENABLED')
        self.assertEqual(config.posting_enabled_env, 'CTO_DIAGNOSTIC_POSTING_ENABLED')

    def test_post_task_import_path_resolves(self):
        from core.services.scheduled_diagnostic_runner import _resolve_import_path
        config = build_config()
        # Should resolve without exception to a Celery task
        post_task = _resolve_import_path(config.post_task_import_path)
        self.assertTrue(hasattr(post_task, 'apply_async'))

    def test_extra_sections_order(self):
        config = build_config()
        section_names = [s[0] for s in config.extra_sections]
        # Session 1093 preserved order: 24h → Agents → Signatures → New Signatures
        self.assertEqual(section_names, [
            '24h Metrics',
            'Top Failing Agents (24h)',
            'Top Failure Signatures (24h)',
            'New Failure Signatures (24h)',
        ])

    def test_prompt_builder_includes_metrics_and_ask(self):
        metrics = _synthetic_metrics_high_failrate()
        gate = {'severity': 'high', 'reasons': ['R'], 'reason_details': ['d']}
        prompt = build_agent_prompt(metrics, gate)
        self.assertIn('daily CTO platform reliability diagnostic', prompt)
        self.assertIn('```json', prompt)
        self.assertIn('Recommended actions', prompt)
        self.assertIn('Confidence', prompt)


# =============================================================================
# End-to-end: tasks_ops.py delegation shim
# =============================================================================

def _build_cto_config_with_mocked_collector(metrics_value):
    """Build a real CTO config but replace its metrics_collector with a stub.

    Avoids patching the module-level `collect_metrics` (which doesn't reach
    the already-bound field on `config.metrics_collector`) and avoids
    SimpleTestCase DB restrictions.
    """
    from core.services.diagnostics.cto_daily import build_config
    config = build_config()
    config.metrics_collector = lambda now, c24, c7: metrics_value
    return config


class TasksOpsShimTests(SimpleTestCase):

    def setUp(self):
        cache.clear()
        # Reset the singleton so each test starts with a fresh config
        import core.tasks_ops as _tops
        _tops._cto_config_singleton = None

    def tearDown(self):
        cache.clear()
        import core.tasks_ops as _tops
        _tops._cto_config_singleton = None

    def test_feature_flag_off_returns_skipped(self):
        # Default: CTO_DIAGNOSTIC_ENABLED not set → False. Metrics collector
        # won't be called so DB restriction doesn't matter.
        from core.tasks_ops import _impl_run_cto_daily_diagnostic
        result = _impl_run_cto_daily_diagnostic()
        self.assertEqual(result['status'], 'skipped')
        self.assertEqual(result['reason'], 'disabled')

    @override_settings(CTO_DIAGNOSTIC_ENABLED='true', CTO_DIAGNOSTIC_POSTING_ENABLED='false')
    def test_observation_mode_logs_without_enqueue(self):
        from core.tasks_ops import _impl_run_cto_daily_diagnostic
        mocked_config = _build_cto_config_with_mocked_collector(
            _synthetic_metrics_high_failrate()
        )
        with patch('core.tasks_ops._get_cto_config', return_value=mocked_config), \
             patch('core.tasks.execute_agent_task.apply_async') as dispatch:
            dispatch.return_value = MagicMock(id='fake-cto-id')
            result = _impl_run_cto_daily_diagnostic()
        self.assertEqual(result['status'], 'log_only')
        self.assertEqual(result['agent_async_task_id'], 'fake-cto-id')
        self.assertIn('HIGH', result['title'])

    @override_settings(CTO_DIAGNOSTIC_ENABLED='true', CTO_DIAGNOSTIC_POSTING_ENABLED='true')
    def test_full_dispatch_uses_post_task_import_path(self):
        from core.tasks_ops import _impl_run_cto_daily_diagnostic
        mocked_config = _build_cto_config_with_mocked_collector(
            _synthetic_metrics_high_failrate()
        )
        with patch('core.tasks_ops._get_cto_config', return_value=mocked_config), \
             patch('core.tasks.execute_agent_task.apply_async') as dispatch_agent, \
             patch('core.tasks.post_cto_daily_diagnostic.apply_async') as dispatch_post:
            dispatch_agent.return_value = MagicMock(id='fake-cto-id')
            dispatch_post.return_value = MagicMock(id='fake-post-id')
            result = _impl_run_cto_daily_diagnostic()
        self.assertEqual(result['status'], 'dispatched')
        dispatch_post.assert_called_once()
        kwargs = dispatch_post.call_args.kwargs
        self.assertEqual(kwargs['countdown'], 240)  # Session 1093 default
        self.assertEqual(kwargs['queue'], 'long_running')
        call_kwargs = kwargs['kwargs']
        self.assertEqual(call_kwargs['agent_async_task_id'], 'fake-cto-id')
        self.assertEqual(call_kwargs['severity'], 'high')
        self.assertIn('window_24h', call_kwargs['metrics'])

    def test_post_impl_maps_cto_async_task_id_to_agent_async_task_id(self):
        from core.tasks_ops import _impl_post_cto_daily_diagnostic
        with patch(
            'core.services.human_attention_bridge.attention_bridge.create_diagnostic_alert'
        ) as bridge:
            result = _impl_post_cto_daily_diagnostic(
                cto_async_task_id='test-cto-id',
                title='Test Title',
                severity='high',
                gate={'severity': 'high', 'reasons': ['R'], 'reason_details': ['d']},
                metrics=_synthetic_metrics_high_failrate(),
                structured_payload={'dedupe_hash': 'ab' * 20},
            )
        self.assertEqual(result['status'], 'posted')
        bridge.assert_called_once()
        kwargs = bridge.call_args.kwargs
        self.assertEqual(kwargs['diagnostic_type'], 'cto_daily_diagnostic')
        self.assertEqual(kwargs['source_agent'], 'CTOAgent')

    def test_post_impl_is_idempotent(self):
        from core.tasks_ops import _impl_post_cto_daily_diagnostic
        dedupe_hash = 'deadbeef' * 5
        posted_key = f'cto_diag:posted:{dedupe_hash[:12]}'
        cache.set(posted_key, '1', timeout=3600)
        with patch(
            'core.services.human_attention_bridge.attention_bridge.create_diagnostic_alert'
        ) as bridge:
            result = _impl_post_cto_daily_diagnostic(
                cto_async_task_id='',
                title='x', severity='high',
                gate={'severity': 'high', 'reasons': [], 'reason_details': []},
                metrics=_synthetic_metrics_high_failrate(),
                structured_payload={'dedupe_hash': dedupe_hash},
            )
        self.assertEqual(result['status'], 'already_posted')
        bridge.assert_not_called()


# =============================================================================
# Cache key preservation (Session 1093 `cto_diag:*` prefix)
# =============================================================================

class CtoCacheKeyTests(SimpleTestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_dedupe_key_uses_cto_diag_prefix(self):
        from core.services.scheduled_diagnostic_runner import _dedupe_and_cooldown_check
        config = build_config()
        gate = evaluate_gate(_synthetic_metrics_high_failrate())
        now = timezone.now()
        result = _dedupe_and_cooldown_check(
            config, now, gate, _synthetic_metrics_high_failrate()
        )
        self.assertTrue(result['dedupe_key'].startswith('cto_diag:dedupe:'))
        self.assertTrue(result['cooldown_key'].startswith('cto_diag:cooldown:'))
