"""
TrendAnalysis daily diagnostic — unit tests.
=============================================

Session 1094: third consumer of the scheduled_diagnostic_runner primitive.
Validates gate evaluator branches (7 gates + severity precedence) and
section renderers against synthetic metrics.

Run:
    python manage.py test core.tests.test_trend_daily_diagnostic -v2
"""

from django.core.cache import cache
from django.test import SimpleTestCase

from core.services.diagnostics.trend_analysis_daily import (
    _herfindahl,
    build_agent_prompt,
    build_config,
    build_dedupe_payload,
    build_headline,
    build_title,
    evaluate_gate,
    render_clusters,
    render_concentration,
    render_spider_coverage,
    render_spider_volume,
)


def _metrics_healthy() -> dict:
    """All gates clear."""
    return {
        'window_24h': {'since': 's', 'until': 'u'},
        'window_7d': {'since': 's', 'until': 'u'},
        'spider_volume': {
            'records_24h': 100, 'records_7d': 700,
            'records_7d_avg_daily': 100.0,
            'volume_delta_pct': 0.0,
            'by_data_type_24h': {'tech': 50, 'jobs': 50},
            'by_spider_24h_top': [
                {'spider_name': 'hackernews', 'c': 30},
                {'spider_name': 'reddit', 'c': 25},
                {'spider_name': 'adzuna', 'c': 25},
                {'spider_name': 'remoteok', 'c': 20},
            ],
        },
        'spider_coverage': {
            'active_7d_count': 20, 'active_24h_count': 18,
            'silent_in_24h_count': 2, 'silent_spiders': ['spider_a', 'spider_b'],
        },
        'concentration': {
            'top_spider_name': 'hackernews', 'top_spider_count': 30,
            'top_spider_share': 0.30, 'herfindahl_index': 0.26,
        },
        'clusters': {
            'new_24h': 10, 'new_7d': 70, 'new_7d_avg_daily': 10.0,
            'velocity_ratio': 1.0,
            'by_pattern_type_24h': {'trend_emergence': 5, 'demand_spike': 5},
            'prior_7d_pattern_count': 4,
            'novel_patterns_24h': [],
        },
    }


def _metrics_volume_drop_high() -> dict:
    m = _metrics_healthy()
    m['spider_volume']['records_24h'] = 30
    m['spider_volume']['records_7d_avg_daily'] = 100.0
    m['spider_volume']['volume_delta_pct'] = -0.70
    return m


def _metrics_volume_drop_crit() -> dict:
    m = _metrics_healthy()
    m['spider_volume']['records_24h'] = 10
    m['spider_volume']['records_7d_avg_daily'] = 100.0
    m['spider_volume']['volume_delta_pct'] = -0.90
    return m


def _metrics_volume_drop_below_floor() -> dict:
    """Big % drop but baseline < abs floor → should NOT trip."""
    m = _metrics_healthy()
    m['spider_volume']['records_24h'] = 2
    m['spider_volume']['records_7d_avg_daily'] = 10.0  # < 20 floor
    m['spider_volume']['volume_delta_pct'] = -0.80
    return m


def _metrics_silent_spiders() -> dict:
    m = _metrics_healthy()
    m['spider_coverage']['silent_in_24h_count'] = 7
    m['spider_coverage']['silent_spiders'] = [f's{i}' for i in range(7)]
    return m


def _metrics_concentration() -> dict:
    m = _metrics_healthy()
    m['concentration']['top_spider_share'] = 0.75
    m['concentration']['herfindahl_index'] = 0.60
    return m


def _metrics_cluster_velocity_high() -> dict:
    m = _metrics_healthy()
    m['clusters']['new_24h'] = 35
    m['clusters']['new_7d_avg_daily'] = 10.0
    m['clusters']['velocity_ratio'] = 3.5
    return m


def _metrics_cluster_velocity_crit() -> dict:
    m = _metrics_healthy()
    m['clusters']['new_24h'] = 55
    m['clusters']['new_7d_avg_daily'] = 10.0
    m['clusters']['velocity_ratio'] = 5.5
    return m


def _metrics_novel_patterns() -> dict:
    m = _metrics_healthy()
    m['clusters']['novel_patterns_24h'] = ['knowledge_gap', 'sentiment_shift']
    m['clusters']['by_pattern_type_24h'] = {
        'trend_emergence': 5, 'demand_spike': 3,
        'knowledge_gap': 2, 'sentiment_shift': 1,
    }
    return m


# =============================================================================
# _herfindahl
# =============================================================================

class HerfindahlTests(SimpleTestCase):

    def test_monopoly(self):
        self.assertEqual(_herfindahl([1.0]), 1.0)

    def test_perfect_diversity_two(self):
        # Two equal 0.5 shares → sum of squares = 0.5
        self.assertEqual(_herfindahl([0.5, 0.5]), 0.5)

    def test_perfect_diversity_ten(self):
        # Ten equal 0.1 shares → sum of squares = 0.1
        self.assertEqual(_herfindahl([0.1] * 10), 0.1)

    def test_empty(self):
        self.assertEqual(_herfindahl([]), 0.0)


# =============================================================================
# Gate evaluator
# =============================================================================

class EvaluateGateTests(SimpleTestCase):

    def test_healthy_no_trip(self):
        gate = evaluate_gate(_metrics_healthy())
        self.assertFalse(gate['tripped'])

    def test_volume_drop_high(self):
        gate = evaluate_gate(_metrics_volume_drop_high())
        self.assertTrue(gate['tripped'])
        self.assertEqual(gate['severity'], 'high')
        self.assertIn('VOLUME_DROP_HIGH', gate['reasons'])

    def test_volume_drop_critical(self):
        gate = evaluate_gate(_metrics_volume_drop_crit())
        self.assertTrue(gate['tripped'])
        self.assertEqual(gate['severity'], 'critical')
        self.assertIn('VOLUME_DROP_CRIT', gate['reasons'])
        # Not HIGH too — mutually exclusive tiers
        self.assertNotIn('VOLUME_DROP_HIGH', gate['reasons'])

    def test_volume_drop_below_absolute_floor_ignored(self):
        """Low baseline → % drops are noise. Should not trip."""
        gate = evaluate_gate(_metrics_volume_drop_below_floor())
        self.assertNotIn('VOLUME_DROP_HIGH', gate.get('reasons', []))
        self.assertNotIn('VOLUME_DROP_CRIT', gate.get('reasons', []))

    def test_silent_spiders_high(self):
        gate = evaluate_gate(_metrics_silent_spiders())
        self.assertTrue(gate['tripped'])
        self.assertIn('SILENT_SPIDERS_HIGH', gate['reasons'])

    def test_concentration_high(self):
        gate = evaluate_gate(_metrics_concentration())
        self.assertTrue(gate['tripped'])
        self.assertIn('CONCENTRATION_HIGH', gate['reasons'])

    def test_cluster_velocity_high(self):
        gate = evaluate_gate(_metrics_cluster_velocity_high())
        self.assertTrue(gate['tripped'])
        self.assertEqual(gate['severity'], 'high')
        self.assertIn('CLUSTER_VELOCITY_HIGH', gate['reasons'])

    def test_cluster_velocity_critical(self):
        gate = evaluate_gate(_metrics_cluster_velocity_crit())
        self.assertTrue(gate['tripped'])
        self.assertEqual(gate['severity'], 'critical')
        self.assertIn('CLUSTER_VELOCITY_CRIT', gate['reasons'])

    def test_velocity_ignored_when_baseline_zero(self):
        """No 7d baseline → can't compute ratio meaningfully."""
        m = _metrics_healthy()
        m['clusters']['new_7d_avg_daily'] = 0.0
        m['clusters']['velocity_ratio'] = 0.0
        gate = evaluate_gate(m)
        self.assertNotIn('CLUSTER_VELOCITY_HIGH', gate.get('reasons', []))
        self.assertNotIn('CLUSTER_VELOCITY_CRIT', gate.get('reasons', []))

    def test_novel_pattern_high(self):
        gate = evaluate_gate(_metrics_novel_patterns())
        self.assertTrue(gate['tripped'])
        self.assertIn('NOVEL_PATTERN_HIGH', gate['reasons'])

    def test_multiple_gates_critical_takes_precedence(self):
        m = _metrics_volume_drop_crit()
        m['spider_coverage']['silent_in_24h_count'] = 10
        m['clusters']['novel_patterns_24h'] = ['new_pattern']
        gate = evaluate_gate(m)
        self.assertEqual(gate['severity'], 'critical')
        # Stacked reasons
        self.assertIn('VOLUME_DROP_CRIT', gate['reasons'])
        self.assertIn('SILENT_SPIDERS_HIGH', gate['reasons'])
        self.assertIn('NOVEL_PATTERN_HIGH', gate['reasons'])


# =============================================================================
# Section renderers
# =============================================================================

class SectionRendererTests(SimpleTestCase):

    def test_render_volume_includes_breakdown(self):
        lines = render_spider_volume(_metrics_healthy(), {})
        joined = '\n'.join(lines)
        self.assertIn('Records (24h)', joined)
        self.assertIn('Breakdown by data_type:', joined)
        self.assertIn('tech: 50', joined)

    def test_render_coverage_shows_silent_names(self):
        lines = render_spider_coverage(_metrics_silent_spiders(), {})
        joined = '\n'.join(lines)
        self.assertIn('Silent in 24h', joined)
        self.assertIn('Silent spider names:', joined)

    def test_render_concentration_with_no_activity(self):
        m = _metrics_healthy()
        m['concentration']['top_spider_name'] = None
        m['concentration']['top_spider_count'] = 0
        lines = render_concentration(m, {})
        joined = '\n'.join(lines)
        self.assertIn('No 24h spider activity', joined)

    def test_render_clusters_marks_novel(self):
        lines = render_clusters(_metrics_novel_patterns(), {})
        joined = '\n'.join(lines)
        self.assertIn('**(NEW)**', joined)
        self.assertIn('knowledge_gap', joined)


# =============================================================================
# Headline + title + dedupe
# =============================================================================

class HeadlineTitleTests(SimpleTestCase):

    def test_headline_format(self):
        gate = {'severity': 'critical', 'reasons': ['VOLUME_DROP_CRIT']}
        headline = build_headline(_metrics_volume_drop_crit(), gate)
        self.assertIn('CRITICAL', headline)
        self.assertIn('vol24h', headline)
        self.assertIn('`VOLUME_DROP_CRIT`', headline)

    def test_title_format(self):
        gate = {'severity': 'critical', 'reasons': ['CLUSTER_VELOCITY_CRIT']}
        title = build_title(_metrics_cluster_velocity_crit(), gate, '2026-04-16')
        self.assertIn('TrendAnalysis Daily Anomaly', title)
        self.assertIn('2026-04-16', title)
        self.assertIn('CRITICAL', title)


class DedupePayloadTests(SimpleTestCase):

    def test_velocity_ratio_bucketed(self):
        """Tiny drift within a 0.5x bucket produces same hash component.

        Bucket math: round(x*2)/2 → half-integer-centered 0.5-wide buckets.
        [3.25, 3.75) → 3.5. Both 3.3 and 3.6 fall in this bucket.
        """
        m = _metrics_healthy()
        m['clusters']['velocity_ratio'] = 3.3
        p1 = build_dedupe_payload(m, {'severity': 'high', 'reasons': []}, 'd')
        m['clusters']['velocity_ratio'] = 3.6
        p2 = build_dedupe_payload(m, {'severity': 'high', 'reasons': []}, 'd')
        self.assertEqual(p1['velocity_ratio_bucket'], p2['velocity_ratio_bucket'])

    def test_concentration_bucketed(self):
        m = _metrics_healthy()
        m['concentration']['top_spider_share'] = 0.61
        p1 = build_dedupe_payload(m, {'severity': 'high', 'reasons': []}, 'd')
        m['concentration']['top_spider_share'] = 0.64
        p2 = build_dedupe_payload(m, {'severity': 'high', 'reasons': []}, 'd')
        self.assertEqual(p1['concentration_bucket'], p2['concentration_bucket'])

    def test_reasons_sorted(self):
        p1 = build_dedupe_payload(_metrics_healthy(),
                                  {'severity': 'high', 'reasons': ['A', 'B']}, 'd')
        p2 = build_dedupe_payload(_metrics_healthy(),
                                  {'severity': 'high', 'reasons': ['B', 'A']}, 'd')
        self.assertEqual(p1['gate_reasons'], p2['gate_reasons'])


# =============================================================================
# Config + integration
# =============================================================================

class TrendConfigTests(SimpleTestCase):

    def test_identity_fields(self):
        config = build_config()
        self.assertEqual(config.name, 'trend_daily_diagnostic')
        self.assertEqual(config.agent_name, 'TrendAnalysisAgent')
        self.assertEqual(config.cache_key_prefix, 'trend_diag')
        self.assertEqual(config.enabled_env, 'TREND_DIAGNOSTIC_ENABLED')

    def test_post_task_import_path_resolves(self):
        from core.services.scheduled_diagnostic_runner import _resolve_import_path
        config = build_config()
        post_task = _resolve_import_path(config.post_task_import_path)
        self.assertTrue(hasattr(post_task, 'apply_async'))

    def test_extra_sections_order(self):
        config = build_config()
        names = [s[0] for s in config.extra_sections]
        self.assertEqual(names, [
            'Spider Volume (24h)',
            'Spider Coverage',
            'Concentration',
            'SignalCluster Activity',
        ])

    def test_prompt_includes_diagnostic_ask(self):
        gate = {'severity': 'high', 'reasons': ['VOLUME_DROP_HIGH'],
                'reason_details': ['drop']}
        prompt = build_agent_prompt(_metrics_volume_drop_high(), gate)
        self.assertIn('TrendAnalysis', prompt)
        self.assertIn('anomaly', prompt.lower())
        self.assertIn('Root-cause hypotheses', prompt)
        self.assertIn('Recommended actions', prompt)


class RunnerIntegrationTests(SimpleTestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_flag_off_skips(self):
        from core.services.scheduled_diagnostic_runner import run_diagnostic
        result = run_diagnostic(build_config())
        self.assertEqual(result['status'], 'skipped')


class BeatScheduleTests(SimpleTestCase):

    def test_registered_in_beat_schedule(self):
        from core.celery import app
        schedule = app.conf.beat_schedule
        self.assertIn('trend-daily-diagnostic', schedule)
        entry = schedule['trend-daily-diagnostic']
        self.assertEqual(entry['task'], 'core.tasks.run_trend_daily_diagnostic')

    def test_three_diagnostics_stagger_on_minute(self):
        """CTO/COO/Trend each fire at different minute within same hour."""
        from core.celery import app
        s = app.conf.beat_schedule
        minutes = {
            'cto': s['cto-daily-diagnostic']['schedule']._orig_minute,
            'coo': s['coo-daily-diagnostic']['schedule']._orig_minute,
            'trend': s['trend-daily-diagnostic']['schedule']._orig_minute,
        }
        # All three distinct
        self.assertEqual(len(set(minutes.values())), 3)


class TasksWrappersTests(SimpleTestCase):

    def test_run_wrapper_exists(self):
        from core.tasks import run_trend_daily_diagnostic
        self.assertTrue(hasattr(run_trend_daily_diagnostic, 'apply_async'))

    def test_post_wrapper_exists(self):
        from core.tasks import post_trend_daily_diagnostic
        self.assertTrue(hasattr(post_trend_daily_diagnostic, 'apply_async'))
