"""
COO daily diagnostic — unit tests for config + gate + section renderers.
=========================================================================

Session 1094: second consumer of the scheduled_diagnostic_runner primitive.
Validates the COO config wiring, gate evaluator branches (7 gates +
severity precedence), and section renderers against synthetic metrics
shapes. Does not hit the DB — collector has its own integration test
elsewhere (or will once the diagnostic is turned on).

Run:
    python manage.py test core.tests.test_coo_daily_diagnostic -v2
"""

from django.core.cache import cache
from django.test import SimpleTestCase

from core.services.diagnostics.coo_daily import (
    _p95_hours,
    build_agent_prompt,
    build_config,
    build_dedupe_payload,
    build_headline,
    build_title,
    evaluate_gate,
    render_action_items,
    render_gate_hang,
    render_mythology_quarantine,
    render_review_backlog,
    render_stuck_initiatives,
    render_velocity,
)


# =============================================================================
# Fixtures
# =============================================================================

def _metrics_healthy() -> dict:
    """All gates clear."""
    return {
        'window_24h': {'since': 's', 'until': 'u'},
        'window_7d': {'since': 's', 'until': 'u'},
        'velocity': {
            'created_24h': 10, 'published_24h': 8,
            'created_7d_avg_daily': 10.0, 'published_7d_avg_daily': 9.0,
            'created_delta_pct': 0.0, 'published_delta_pct': -0.11,
        },
        'review_backlog': {
            'ready_count': 2, 'ready_p95_age_hours': 3.0,
            'ready_over_threshold_count': 0, 'ready_over_threshold_hours': 24,
            'oldest_ready_hours': 5.0, 'oldest_ready_top': [],
        },
        'action_items': {
            'pending_by_urgency': {'medium': 2, 'low': 5},
            'pending_over_sla_by_urgency': {},
            'pending_total': 7, 'oldest_critical_hours': 0.0,
        },
        'initiatives': {
            'stuck_count': 0, 'stuck_hours_threshold': 72, 'stuck_top': [],
        },
        'gate_hang': {
            'pending_total': 0, 'new_24h': 0,
            'oldest_pending_hours': 0.0, 'top_pipelines': [],
        },
        'mythology_quarantine': {
            'enabled': False,
            'unacked_critical': 0, 'unacked_high': 0,
            'pending_flags_critical': 0, 'pending_flags_high': 0,
            'top_patterns_24h': [],
        },
    }


def _metrics_mythology_high() -> dict:
    """Unacked critical + high >= 10 AND < 25 → MYTHOLOGY_QUARANTINE_HIGH."""
    m = _metrics_healthy()
    m['mythology_quarantine'] = {
        'enabled': True,
        'unacked_critical': 8,
        'unacked_high': 5,
        'pending_flags_critical': 8,
        'pending_flags_high': 5,
        'top_patterns_24h': [
            {'pattern': 'spider_data_myth', 'count': 100},
            {'pattern': 'time_myth', 'count': 50},
        ],
    }
    return m


def _metrics_mythology_crit() -> dict:
    """Unacked critical >= 25 → MYTHOLOGY_QUARANTINE_CRIT."""
    m = _metrics_healthy()
    m['mythology_quarantine'] = {
        'enabled': True,
        'unacked_critical': 312,
        'unacked_high': 16,
        'pending_flags_critical': 312,
        'pending_flags_high': 16,
        'top_patterns_24h': [
            {'pattern': 'dangerous_myth', 'count': 3},
            {'pattern': 'spider_data_myth', 'count': 272},
        ],
    }
    return m


def _metrics_gate_hang_high() -> dict:
    """gate_hang total >= 10 → GATE_HANG_HIGH."""
    m = _metrics_healthy()
    m['gate_hang'] = {
        'pending_total': 12,
        'new_24h': 2,
        'oldest_pending_hours': 60.0,
        'top_pipelines': [
            {'pipeline': 'GateProgressionPipeline', 'count': 10},
            {'pipeline': 'PanelCoordinator', 'count': 2},
        ],
    }
    return m


def _metrics_gate_hang_new_surge() -> dict:
    """gate_hang new_24h >= 5 → GATE_HANG_NEW_HIGH (surge detector)."""
    m = _metrics_healthy()
    m['gate_hang'] = {
        'pending_total': 6,
        'new_24h': 6,  # all new
        'oldest_pending_hours': 4.0,
        'top_pipelines': [{'pipeline': 'GateProgressionPipeline', 'count': 6}],
    }
    return m


def _metrics_velocity_drop() -> dict:
    """Created down 50%, absolute delta > 5 → VELOCITY_DROP_HIGH."""
    m = _metrics_healthy()
    m['velocity']['created_24h'] = 3
    m['velocity']['created_7d_avg_daily'] = 12.0
    m['velocity']['created_delta_pct'] = -0.75
    return m


def _metrics_publishing_jam() -> dict:
    """Published=0 AND ready_count >= 10 → PUBLISHING_JAM_CRIT."""
    m = _metrics_healthy()
    m['velocity']['published_24h'] = 0
    m['velocity']['published_delta_pct'] = -1.0
    m['review_backlog']['ready_count'] = 15
    return m


def _metrics_review_age() -> dict:
    """p95 ready age > 24h OR over_threshold >= 5 → REVIEW_AGE_HIGH."""
    m = _metrics_healthy()
    m['review_backlog']['ready_p95_age_hours'] = 30.0
    m['review_backlog']['ready_over_threshold_count'] = 6
    return m


def _metrics_oldest_review() -> dict:
    """oldest > 48h → OLDEST_REVIEW_HIGH."""
    m = _metrics_healthy()
    m['review_backlog']['oldest_ready_hours'] = 60.0
    return m


def _metrics_action_backlog_high() -> dict:
    """pending critical >= 2 (but < 5) → ACTION_BACKLOG_HIGH."""
    m = _metrics_healthy()
    m['action_items']['pending_by_urgency'] = {'critical': 3, 'high': 2}
    m['action_items']['pending_total'] = 5
    return m


def _metrics_action_backlog_crit() -> dict:
    """pending critical >= 5 → ACTION_BACKLOG_CRIT."""
    m = _metrics_healthy()
    m['action_items']['pending_by_urgency'] = {'critical': 7, 'high': 3}
    m['action_items']['pending_total'] = 10
    return m


def _metrics_stuck_initiatives() -> dict:
    """stuck_count >= 5 → STUCK_INITIATIVES_HIGH."""
    m = _metrics_healthy()
    m['initiatives']['stuck_count'] = 8
    m['initiatives']['stuck_top'] = [
        {'name': 'Init A', 'current_stage': 'RESEARCH', 'stale_hours': 100.0}
    ]
    return m


# =============================================================================
# _p95_hours
# =============================================================================

class P95HoursTests(SimpleTestCase):

    def test_empty_returns_zero(self):
        self.assertEqual(_p95_hours([]), 0.0)

    def test_single_element(self):
        self.assertEqual(_p95_hours([5.0]), 5.0)

    def test_many_elements(self):
        # 100 elements evenly spaced 0..99 → p95 is approximately 95
        result = _p95_hours([float(i) for i in range(100)])
        self.assertGreaterEqual(result, 90)
        self.assertLessEqual(result, 99)

    def test_order_doesnt_matter(self):
        a = _p95_hours([1.0, 5.0, 3.0, 7.0, 2.0, 9.0])
        b = _p95_hours([9.0, 7.0, 5.0, 3.0, 1.0, 2.0])
        self.assertEqual(a, b)


# =============================================================================
# Gate evaluator — each branch + severity precedence
# =============================================================================

class EvaluateGateTests(SimpleTestCase):

    def test_healthy_no_trip(self):
        gate = evaluate_gate(_metrics_healthy())
        self.assertFalse(gate['tripped'])
        self.assertIsNone(gate['severity'])

    def test_velocity_drop_trips_high(self):
        gate = evaluate_gate(_metrics_velocity_drop())
        self.assertTrue(gate['tripped'])
        self.assertEqual(gate['severity'], 'high')
        self.assertIn('VELOCITY_DROP_HIGH', gate['reasons'])

    def test_velocity_drop_below_absolute_floor_ignored(self):
        """% drop alone should not trip when absolute delta is tiny.

        Rigby's feedback: low-volume environments would otherwise page on
        meaningless +/- 1 deltas that happen to be high %.
        """
        m = _metrics_healthy()
        m['velocity']['created_24h'] = 2
        m['velocity']['created_7d_avg_daily'] = 4.0  # delta = -2, pct = -50%
        m['velocity']['created_delta_pct'] = -0.50
        # Absolute delta is 2, floor is 5 → should NOT trip
        gate = evaluate_gate(m)
        self.assertNotIn('VELOCITY_DROP_HIGH', gate['reasons'])

    def test_publishing_jam_trips_critical(self):
        gate = evaluate_gate(_metrics_publishing_jam())
        self.assertTrue(gate['tripped'])
        self.assertEqual(gate['severity'], 'critical')
        self.assertIn('PUBLISHING_JAM_CRIT', gate['reasons'])

    def test_publishing_jam_without_ready_floor_ignored(self):
        """Published=0 alone isn't a jam if there's nothing in ready either
        (weekend / quiet day, not a blockage)."""
        m = _metrics_healthy()
        m['velocity']['published_24h'] = 0
        m['review_backlog']['ready_count'] = 2  # below jam_ready_min
        gate = evaluate_gate(m)
        self.assertNotIn('PUBLISHING_JAM_CRIT', gate['reasons'])

    def test_review_age_trips_high(self):
        gate = evaluate_gate(_metrics_review_age())
        self.assertTrue(gate['tripped'])
        self.assertIn('REVIEW_AGE_HIGH', gate['reasons'])

    def test_oldest_review_trips_high(self):
        gate = evaluate_gate(_metrics_oldest_review())
        self.assertTrue(gate['tripped'])
        self.assertIn('OLDEST_REVIEW_HIGH', gate['reasons'])

    def test_action_backlog_high(self):
        gate = evaluate_gate(_metrics_action_backlog_high())
        self.assertTrue(gate['tripped'])
        self.assertIn('ACTION_BACKLOG_HIGH', gate['reasons'])
        self.assertEqual(gate['severity'], 'high')

    def test_action_backlog_critical(self):
        gate = evaluate_gate(_metrics_action_backlog_crit())
        self.assertTrue(gate['tripped'])
        self.assertIn('ACTION_BACKLOG_CRIT', gate['reasons'])
        self.assertEqual(gate['severity'], 'critical')
        # Not-also-high: mutually exclusive with ACTION_BACKLOG_HIGH at the same severity
        self.assertNotIn('ACTION_BACKLOG_HIGH', gate['reasons'])

    def test_stuck_initiatives_trips_high(self):
        gate = evaluate_gate(_metrics_stuck_initiatives())
        self.assertTrue(gate['tripped'])
        self.assertIn('STUCK_INITIATIVES_HIGH', gate['reasons'])

    def test_gate_hang_high_trips_on_pending_total(self):
        gate = evaluate_gate(_metrics_gate_hang_high())
        self.assertTrue(gate['tripped'])
        self.assertIn('GATE_HANG_HIGH', gate['reasons'])
        self.assertEqual(gate['severity'], 'high')
        # Gate reason detail should name the top pipeline
        detail_text = ' '.join(gate['reason_details'])
        self.assertIn('GateProgressionPipeline', detail_text)

    def test_gate_hang_new_high_trips_on_surge(self):
        """new_24h >= 5 trips the surge gate even when total is low."""
        gate = evaluate_gate(_metrics_gate_hang_new_surge())
        self.assertTrue(gate['tripped'])
        self.assertIn('GATE_HANG_NEW_HIGH', gate['reasons'])

    def test_mythology_quarantine_high_trips(self):
        """Unacked critical+high >= 10 AND critical < 25 → HIGH."""
        gate = evaluate_gate(_metrics_mythology_high())
        self.assertTrue(gate['tripped'])
        self.assertIn('MYTHOLOGY_QUARANTINE_HIGH', gate['reasons'])
        self.assertEqual(gate['severity'], 'high')

    def test_mythology_quarantine_critical_trips(self):
        """Unacked critical >= 25 → CRITICAL."""
        gate = evaluate_gate(_metrics_mythology_crit())
        self.assertTrue(gate['tripped'])
        self.assertIn('MYTHOLOGY_QUARANTINE_CRIT', gate['reasons'])
        self.assertEqual(gate['severity'], 'critical')
        # Mutually exclusive with HIGH at same severity tier
        self.assertNotIn('MYTHOLOGY_QUARANTINE_HIGH', gate['reasons'])
        detail = ' '.join(gate['reason_details'])
        self.assertIn('spider_data_myth', detail)

    def test_mythology_skipped_when_app_unavailable(self):
        """When `mythology_quarantine.enabled=False`, gate is skipped
        entirely — COO stays healthy even without the mythology app."""
        m = _metrics_healthy()
        m['mythology_quarantine']['enabled'] = False
        m['mythology_quarantine']['unacked_critical'] = 999  # ignored because disabled
        gate = evaluate_gate(m)
        self.assertNotIn('MYTHOLOGY_QUARANTINE_HIGH', gate.get('reasons', []))
        self.assertNotIn('MYTHOLOGY_QUARANTINE_CRIT', gate.get('reasons', []))

    def test_mythology_below_threshold_no_trip(self):
        m = _metrics_healthy()
        m['mythology_quarantine'] = {
            'enabled': True,
            'unacked_critical': 3, 'unacked_high': 2,
            'pending_flags_critical': 3, 'pending_flags_high': 2,
            'top_patterns_24h': [],
        }
        gate = evaluate_gate(m)
        self.assertNotIn('MYTHOLOGY_QUARANTINE_HIGH', gate.get('reasons', []))

    def test_gate_hang_below_threshold_no_trip(self):
        """pending_total < 10 AND new_24h < 5 → no gate_hang reasons."""
        m = _metrics_healthy()
        m['gate_hang'] = {
            'pending_total': 3, 'new_24h': 2,
            'oldest_pending_hours': 2.0, 'top_pipelines': [],
        }
        gate = evaluate_gate(m)
        self.assertNotIn('GATE_HANG_HIGH', gate.get('reasons', []))
        self.assertNotIn('GATE_HANG_NEW_HIGH', gate.get('reasons', []))

    def test_missing_gate_hang_key_backward_compat(self):
        """Old callers that built metrics dicts before Session 1095 didn't
        include gate_hang. Gate must not crash — just skip the gate_hang
        branch gracefully.
        """
        m = _metrics_healthy()
        del m['gate_hang']
        gate = evaluate_gate(m)
        # Should not raise, and gate_hang reasons should be absent
        self.assertNotIn('GATE_HANG_HIGH', gate.get('reasons', []))
        self.assertNotIn('GATE_HANG_NEW_HIGH', gate.get('reasons', []))

    def test_multiple_gates_severity_precedence_critical_over_high(self):
        """If any gate is critical, final severity is critical."""
        m = _metrics_action_backlog_crit()
        # Layer a high-only gate on top
        m['review_backlog']['ready_p95_age_hours'] = 30.0
        gate = evaluate_gate(m)
        self.assertEqual(gate['severity'], 'critical')
        self.assertIn('ACTION_BACKLOG_CRIT', gate['reasons'])
        self.assertIn('REVIEW_AGE_HIGH', gate['reasons'])


# =============================================================================
# Section renderers
# =============================================================================

class SectionRendererTests(SimpleTestCase):

    def test_render_velocity_includes_both_created_and_published(self):
        lines = render_velocity(_metrics_healthy(), {})
        joined = '\n'.join(lines)
        self.assertIn('Created', joined)
        self.assertIn('Published', joined)
        self.assertIn('10.0/day', joined)

    def test_render_review_backlog_includes_oldest_top_when_present(self):
        m = _metrics_healthy()
        m['review_backlog']['oldest_ready_top'] = [
            {'title': 'My Blog Post', 'age_hours': 30.5},
        ]
        lines = render_review_backlog(m, {})
        joined = '\n'.join(lines)
        self.assertIn('Oldest ready items:', joined)
        self.assertIn('My Blog Post', joined)

    def test_render_review_backlog_empty_oldest_top_omits_section(self):
        m = _metrics_healthy()
        m['review_backlog']['oldest_ready_top'] = []
        lines = render_review_backlog(m, {})
        joined = '\n'.join(lines)
        self.assertNotIn('Oldest ready items:', joined)

    def test_render_action_items_shows_sla_breaches(self):
        m = _metrics_action_backlog_high()
        m['action_items']['pending_over_sla_by_urgency'] = {'critical': 2}
        lines = render_action_items(m, {})
        joined = '\n'.join(lines)
        self.assertIn('Critical: 3', joined)
        self.assertIn('past SLA', joined)

    def test_render_action_items_skips_zero_urgencies(self):
        m = _metrics_healthy()  # only medium + low
        lines = render_action_items(m, {})
        joined = '\n'.join(lines)
        # Critical/high should be omitted since zero
        self.assertNotIn('Critical:', joined)
        self.assertNotIn('High:', joined)
        self.assertIn('Medium:', joined)

    def test_render_stuck_initiatives_empty_returns_empty(self):
        lines = render_stuck_initiatives(_metrics_healthy(), {})
        self.assertEqual(lines, [])

    def test_render_stuck_initiatives_shows_top(self):
        lines = render_stuck_initiatives(_metrics_stuck_initiatives(), {})
        joined = '\n'.join(lines)
        self.assertIn('Top stuck:', joined)
        self.assertIn('Init A', joined)

    def test_render_gate_hang_empty_when_zero(self):
        """No pending gate_stuck → section fully omitted (empty list returned)."""
        lines = render_gate_hang(_metrics_healthy(), {})
        self.assertEqual(lines, [])

    def test_render_gate_hang_shows_pipelines(self):
        lines = render_gate_hang(_metrics_gate_hang_high(), {})
        joined = '\n'.join(lines)
        self.assertIn('Pending gate_stuck', joined)
        self.assertIn('Top hanging pipelines:', joined)
        self.assertIn('GateProgressionPipeline', joined)
        self.assertIn('PanelCoordinator', joined)

    def test_render_gate_hang_tolerates_missing_metric_key(self):
        """Backward-compat: missing gate_hang key returns [] (no crash)."""
        m = _metrics_healthy()
        del m['gate_hang']
        self.assertEqual(render_gate_hang(m, {}), [])

    def test_render_mythology_skipped_when_disabled(self):
        """enabled=False → section fully omitted."""
        self.assertEqual(render_mythology_quarantine(_metrics_healthy(), {}), [])

    def test_render_mythology_shows_patterns_and_tuning_note(self):
        lines = render_mythology_quarantine(_metrics_mythology_crit(), {})
        joined = '\n'.join(lines)
        self.assertIn('328', joined)  # total unacked
        self.assertIn('spider_data_myth', joined)
        # False-positive tuning hint must surface
        self.assertIn('Audit the Mythology Lab for pattern tuning', joined)

    def test_render_mythology_tolerates_missing_key(self):
        """Backward-compat: missing mythology_quarantine key returns []."""
        m = _metrics_healthy()
        del m['mythology_quarantine']
        self.assertEqual(render_mythology_quarantine(m, {}), [])


# =============================================================================
# Headline + title
# =============================================================================

class HeadlineTitleTests(SimpleTestCase):

    def test_headline_includes_severity_metrics_reason(self):
        gate = {'severity': 'high', 'reasons': ['VELOCITY_DROP_HIGH']}
        headline = build_headline(_metrics_velocity_drop(), gate)
        self.assertIn('HIGH', headline)
        self.assertIn('published', headline)
        self.assertIn('in review', headline)
        self.assertIn('`VELOCITY_DROP_HIGH`', headline)

    def test_title_format(self):
        gate = {'severity': 'critical', 'reasons': ['PUBLISHING_JAM_CRIT']}
        title = build_title(_metrics_publishing_jam(), gate, '2026-04-16')
        self.assertIn('COO Daily Ops Diagnostic', title)
        self.assertIn('2026-04-16', title)
        self.assertIn('CRITICAL', title)


# =============================================================================
# Dedupe payload
# =============================================================================

class DedupePayloadTests(SimpleTestCase):

    def test_payload_has_bucketed_continuous_fields(self):
        """Age fields are bucketed (6h) so small drifts don't change the hash."""
        m = _metrics_healthy()
        # 20h and 23h are both in the [18, 24) bucket → both round to 18
        m['review_backlog']['ready_p95_age_hours'] = 20.0
        p1 = build_dedupe_payload(m, {'severity': 'high', 'reasons': []}, '2026-04-16')
        m['review_backlog']['ready_p95_age_hours'] = 23.9
        p2 = build_dedupe_payload(m, {'severity': 'high', 'reasons': []}, '2026-04-16')
        self.assertEqual(p1['ready_p95_age_bucket'], p2['ready_p95_age_bucket'])

    def test_payload_hash_changes_across_buckets(self):
        """Values that cross a bucket boundary DO produce different hashes
        (this is intentional — the whole point of bucketing is that each
        bucket is a distinct equivalence class)."""
        m = _metrics_healthy()
        m['review_backlog']['ready_p95_age_hours'] = 20.0   # bucket 18
        p1 = build_dedupe_payload(m, {'severity': 'high', 'reasons': []}, 'd')
        m['review_backlog']['ready_p95_age_hours'] = 30.0   # bucket 30
        p2 = build_dedupe_payload(m, {'severity': 'high', 'reasons': []}, 'd')
        self.assertNotEqual(p1['ready_p95_age_bucket'], p2['ready_p95_age_bucket'])

    def test_sort_reasons_stable(self):
        p1 = build_dedupe_payload({'velocity': {}, 'review_backlog': {},
                                   'action_items': {}, 'initiatives': {}},
                                  {'severity': 'high', 'reasons': ['A', 'B']}, 'd')
        p2 = build_dedupe_payload({'velocity': {}, 'review_backlog': {},
                                   'action_items': {}, 'initiatives': {}},
                                  {'severity': 'high', 'reasons': ['B', 'A']}, 'd')
        self.assertEqual(p1['gate_reasons'], p2['gate_reasons'])


# =============================================================================
# Config wiring
# =============================================================================

class CooConfigTests(SimpleTestCase):

    def test_identity_fields(self):
        config = build_config()
        self.assertEqual(config.name, 'coo_daily_diagnostic')
        self.assertEqual(config.diagnostic_type, 'coo_daily_diagnostic')
        self.assertEqual(config.agent_name, 'COOAgent')
        self.assertEqual(config.source_agent, 'COOAgent')
        self.assertEqual(config.cache_key_prefix, 'coo_diag')
        self.assertEqual(config.enabled_env, 'COO_DIAGNOSTIC_ENABLED')
        self.assertEqual(config.posting_enabled_env, 'COO_DIAGNOSTIC_POSTING_ENABLED')

    def test_post_task_import_path_resolves(self):
        from core.services.scheduled_diagnostic_runner import _resolve_import_path
        config = build_config()
        post_task = _resolve_import_path(config.post_task_import_path)
        self.assertTrue(hasattr(post_task, 'apply_async'))

    def test_extra_sections_order(self):
        config = build_config()
        names = [s[0] for s in config.extra_sections]
        self.assertEqual(names, [
            '24h Velocity',
            'Review Backlog',
            'Action Items',
            'Stuck Initiatives',
            'Gate Hang Health',           # Session 1095 (Rigby's #2 gate)
            'Rework / Bounce Rate',       # Session 1095 (Rigby's #1 gate)
            'Mythology Lab Backlog',      # Session 1095 (Rigby's #3 gate)
        ])

    def test_prompt_builder_coo_voice(self):
        m = _metrics_publishing_jam()
        gate = {'severity': 'critical', 'reasons': ['PUBLISHING_JAM_CRIT'],
                'reason_details': ['jam']}
        prompt = build_agent_prompt(m, gate)
        self.assertIn('COO', prompt)
        self.assertIn('concise', prompt.lower())
        self.assertIn('bullets not paragraphs', prompt.lower())
        self.assertIn('Recommended actions', prompt)
        self.assertIn('Confidence', prompt)


# =============================================================================
# End-to-end shim via runner
# =============================================================================

class RunnerIntegrationTests(SimpleTestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_flag_off_skips(self):
        """COO_DIAGNOSTIC_ENABLED not set → skipped, no DB hit."""
        from core.services.scheduled_diagnostic_runner import run_diagnostic
        config = build_config()
        result = run_diagnostic(config)
        self.assertEqual(result['status'], 'skipped')


# =============================================================================
# Beat schedule entry
# =============================================================================

class BeatScheduleTests(SimpleTestCase):

    def test_coo_daily_diagnostic_registered_in_beat_schedule(self):
        from core.celery import app
        schedule = app.conf.beat_schedule
        self.assertIn('coo-daily-diagnostic', schedule)
        entry = schedule['coo-daily-diagnostic']
        self.assertEqual(entry['task'], 'core.tasks.run_coo_daily_diagnostic')
        self.assertEqual(entry['options']['queue'], 'long_running')

    def test_cto_and_coo_dont_collide_on_minute(self):
        """COO fires 15 min after CTO so they don't hit long_running simultaneously."""
        from core.celery import app
        cto = app.conf.beat_schedule['cto-daily-diagnostic']['schedule']
        coo = app.conf.beat_schedule['coo-daily-diagnostic']['schedule']
        # Both are crontab objects — compare minute/hour
        self.assertNotEqual(cto._orig_minute, coo._orig_minute)
        self.assertEqual(cto._orig_hour, coo._orig_hour)  # Same hour


# =============================================================================
# tasks.py Celery wrappers exist + are callable
# =============================================================================

class TasksWrappersTests(SimpleTestCase):

    def test_run_wrapper_exists(self):
        from core.tasks import run_coo_daily_diagnostic
        self.assertTrue(hasattr(run_coo_daily_diagnostic, 'apply_async'))

    def test_post_wrapper_exists(self):
        from core.tasks import post_coo_daily_diagnostic
        self.assertTrue(hasattr(post_coo_daily_diagnostic, 'apply_async'))
