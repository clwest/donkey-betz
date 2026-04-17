"""
Scheduled diagnostic runner — unit tests
=========================================

Session 1094: covers the generic `run_diagnostic` / `post_diagnostic`
primitive in isolation (using a synthetic config). CTO-specific behavior
tests live in `test_cto_daily_diagnostic_via_runner.py`.

Run:
    python manage.py test core.tests.test_scheduled_diagnostic_runner -v2
"""

from datetime import datetime, timedelta, timezone as dt_tz
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from core.services.scheduled_diagnostic_runner import (
    DiagnosticConfig,
    _apply_payload_cap,
    _compose_body,
    _date_bucket,
    _dedupe_and_cooldown_check,
    _env_bool,
    _resolve_import_path,
    default_extract_recommended_actions,
    post_diagnostic,
    run_diagnostic,
)


# =============================================================================
# Fixtures — minimal synthetic config that exercises every runner branch
# =============================================================================

def _build_metrics_collector(return_value):
    collector = MagicMock()
    collector.return_value = return_value
    return collector


def _build_gate_evaluator(gate_value):
    evaluator = MagicMock()
    evaluator.return_value = gate_value
    return evaluator


def _minimal_config(**overrides) -> DiagnosticConfig:
    defaults = dict(
        name='test_diag',
        diagnostic_type='test_diagnostic',
        agent_name='FakeTestAgent',
        source_agent='FakeTestAgent',
        log_prefix='TEST-DIAG',
        metrics_collector=_build_metrics_collector({
            'window_24h': {'total': 100, 'failed': 10, 'fail_rate': 0.1, 'timeout_failed': 2},
            'window_7d': {'total': 700, 'failed': 35, 'fail_rate': 0.05},
            'delta_vs_7d': 0.05,
            'top_failing_agents_24h': [{'agent__name': 'A', 'count': 5}],
            'top_signatures_24h': [],
            'new_signatures_24h': [],
        }),
        gate_evaluator=_build_gate_evaluator({
            'tripped': True,
            'severity': 'high',
            'reasons': ['TEST_REASON'],
            'reason_details': ['test detail'],
        }),
        prompt_builder=lambda m, g: 'test prompt',
        dedupe_payload_builder=lambda m, g, db: {'date': db, 'key': 'v1'},
        headline_builder=lambda m, g: 'test headline',
        title_builder=lambda m, g, d: f'Test Title — {d}',
        enabled_env='TEST_DIAGNOSTIC_ENABLED',
        posting_enabled_env='TEST_DIAGNOSTIC_POSTING_ENABLED',
        cache_key_prefix='test_diag',
    )
    defaults.update(overrides)
    return DiagnosticConfig(**defaults)


# =============================================================================
# Env helpers
# =============================================================================

class EnvBoolTests(SimpleTestCase):

    def test_empty_name_returns_default(self):
        self.assertFalse(_env_bool('', default=False))
        self.assertTrue(_env_bool('', default=True))

    def test_unset_var_returns_default(self):
        self.assertFalse(_env_bool('DEFINITELY_NOT_SET_XYZ_123', default=False))

    @override_settings(TEST_DIAGNOSTIC_ENABLED='true')
    def test_settings_truthy_values(self):
        self.assertTrue(_env_bool('TEST_DIAGNOSTIC_ENABLED'))

    @override_settings(TEST_DIAGNOSTIC_ENABLED='1')
    def test_settings_numeric_truthy(self):
        self.assertTrue(_env_bool('TEST_DIAGNOSTIC_ENABLED'))

    @override_settings(TEST_DIAGNOSTIC_ENABLED='false')
    def test_settings_falsy(self):
        self.assertFalse(_env_bool('TEST_DIAGNOSTIC_ENABLED'))


# =============================================================================
# Import resolver
# =============================================================================

class ResolveImportPathTests(SimpleTestCase):

    def test_resolves_valid_path(self):
        fn = _resolve_import_path('os.path:join')
        import os
        self.assertIs(fn, os.path.join)

    def test_missing_colon_raises(self):
        with self.assertRaises(ValueError):
            _resolve_import_path('no.colon.here')

    def test_missing_attr_raises(self):
        with self.assertRaises(AttributeError):
            _resolve_import_path('os.path:definitely_not_a_real_attr_xyz')


# =============================================================================
# Default Recommended Actions extractor
# =============================================================================

class DefaultExtractRecommendedActionsTests(SimpleTestCase):

    def test_empty_input(self):
        self.assertEqual(default_extract_recommended_actions(''), [])
        self.assertEqual(default_extract_recommended_actions(None), [])  # type: ignore[arg-type]

    def test_markdown_heading_with_hyphen_bullets(self):
        narrative = """
## Recommended Actions

- First action
- Second action
- Third action
- Fourth action
- Fifth action
"""
        result = default_extract_recommended_actions(narrative, max_actions=3)
        self.assertEqual(result, ['First action', 'Second action', 'Third action'])

    def test_bold_heading_with_asterisk_bullets(self):
        narrative = "**Recommended Actions:**\n\n* First\n* Second\n"
        self.assertEqual(default_extract_recommended_actions(narrative), ['First', 'Second'])

    def test_numbered_bullets(self):
        narrative = "### Recommended actions\n\n1. First\n2) Second\n"
        self.assertEqual(default_extract_recommended_actions(narrative), ['First', 'Second'])

    def test_heading_with_max_suffix(self):
        narrative = "## Recommended Actions (max 3)\n- A\n- B\n"
        self.assertEqual(default_extract_recommended_actions(narrative), ['A', 'B'])

    def test_stops_at_confidence_section(self):
        narrative = """
## Recommended Actions
- A
- B
## Confidence
high
"""
        self.assertEqual(default_extract_recommended_actions(narrative), ['A', 'B'])

    def test_stops_at_next_heading(self):
        narrative = """
## Recommended Actions
- A
## Other Section
- not an action
"""
        self.assertEqual(default_extract_recommended_actions(narrative), ['A'])

    def test_hard_cap_enforced(self):
        narrative = "## Recommended Actions\n" + "\n".join(f"- Action {i}" for i in range(10))
        self.assertEqual(len(default_extract_recommended_actions(narrative, max_actions=3)), 3)
        self.assertEqual(len(default_extract_recommended_actions(narrative, max_actions=5)), 5)

    def test_no_section_returns_empty(self):
        self.assertEqual(default_extract_recommended_actions("Some narrative without the heading"), [])

    def test_multiline_bullet_content_preserved(self):
        narrative = """
## Recommended Actions
- This action has
  some continuation
- Short one
"""
        result = default_extract_recommended_actions(narrative)
        # Internal whitespace collapsed to single space
        self.assertEqual(result[0], 'This action has some continuation')


# =============================================================================
# Date bucket (MT default)
# =============================================================================

class DateBucketTests(SimpleTestCase):

    def test_mt_rolls_at_local_midnight(self):
        # 2026-04-16 05:00 UTC = 2026-04-15 23:00 MDT → bucket is '2026-04-15'
        now_utc = datetime(2026, 4, 16, 5, 0, 0, tzinfo=dt_tz.utc)
        self.assertEqual(_date_bucket(now_utc, 'America/Denver'), '2026-04-15')

    def test_mt_before_rollover(self):
        # 2026-04-16 08:00 UTC = 2026-04-16 02:00 MDT → bucket is '2026-04-16'
        now_utc = datetime(2026, 4, 16, 8, 0, 0, tzinfo=dt_tz.utc)
        self.assertEqual(_date_bucket(now_utc, 'America/Denver'), '2026-04-16')

    def test_invalid_timezone_falls_back_to_utc(self):
        now_utc = datetime(2026, 4, 16, 5, 0, 0, tzinfo=dt_tz.utc)
        # Invalid tz should fall back silently
        self.assertEqual(_date_bucket(now_utc, 'Not/A_Real_Zone'), '2026-04-16')


# =============================================================================
# Dedupe + cooldown
# =============================================================================

class DedupeCooldownTests(SimpleTestCase):

    def setUp(self):
        # Ensure clean cache for each test
        cache.clear()

    def tearDown(self):
        cache.clear()

    def _gate(self, severity='high', reasons=None):
        return {
            'tripped': True,
            'severity': severity,
            'reasons': reasons or ['R'],
            'reason_details': ['detail'],
        }

    def _metrics(self):
        return {'x': 1}

    def test_clean_cache_allows_post(self):
        config = _minimal_config()
        now = timezone.now()
        result = _dedupe_and_cooldown_check(config, now, self._gate(), self._metrics())
        self.assertTrue(result['should_post'])
        self.assertEqual(result['reason'], 'gates_clear')

    def test_dedupe_hit_blocks(self):
        config = _minimal_config()
        now = timezone.now()
        first = _dedupe_and_cooldown_check(config, now, self._gate(), self._metrics())
        cache.set(first['dedupe_key'], '1', timeout=3600)
        second = _dedupe_and_cooldown_check(config, now, self._gate(), self._metrics())
        self.assertFalse(second['should_post'])
        self.assertIn('dedupe_hit', second['reason'])

    def test_cooldown_hit_blocks(self):
        config = _minimal_config()
        now = timezone.now()
        first = _dedupe_and_cooldown_check(config, now, self._gate(severity='high'), self._metrics())
        cache.set(first['cooldown_key'], 'x', timeout=3600)
        # Different dedupe payload → dedupe wouldn't hit, but cooldown should
        second_gate = self._gate(severity='high', reasons=['DIFFERENT'])
        second = _dedupe_and_cooldown_check(config, now, second_gate, self._metrics())
        self.assertFalse(second['should_post'])
        self.assertIn('cooldown_active', second['reason'])

    def test_cooldown_is_per_severity(self):
        config = _minimal_config()
        now = timezone.now()
        # Populate cooldown for high only
        high_result = _dedupe_and_cooldown_check(config, now, self._gate(severity='high'), self._metrics())
        cache.set(high_result['cooldown_key'], 'x', timeout=3600)
        # Critical severity should NOT be blocked by high cooldown
        crit_result = _dedupe_and_cooldown_check(
            config, now, self._gate(severity='critical', reasons=['DIFF']), self._metrics()
        )
        self.assertTrue(crit_result['should_post'])

    def test_critical_gets_shorter_cooldown(self):
        config = _minimal_config(cooldown_critical_hours=6, cooldown_high_hours=20)
        now = timezone.now()
        crit = _dedupe_and_cooldown_check(config, now, self._gate(severity='critical'), self._metrics())
        high = _dedupe_and_cooldown_check(config, now, self._gate(severity='high', reasons=['DIFF']), self._metrics())
        self.assertEqual(crit['cooldown_hours'], 6)
        self.assertEqual(high['cooldown_hours'], 20)

    def test_same_shape_same_hash(self):
        config = _minimal_config()
        now = timezone.now()
        a = _dedupe_and_cooldown_check(config, now, self._gate(), self._metrics())
        b = _dedupe_and_cooldown_check(config, now, self._gate(), self._metrics())
        self.assertEqual(a['dedupe_hash'], b['dedupe_hash'])

    def test_different_shape_different_hash(self):
        config = _minimal_config(
            dedupe_payload_builder=lambda m, g, db: {'date': db, 'x': m.get('x')}
        )
        now = timezone.now()
        a = _dedupe_and_cooldown_check(config, now, self._gate(), {'x': 1})
        b = _dedupe_and_cooldown_check(config, now, self._gate(), {'x': 2})
        self.assertNotEqual(a['dedupe_hash'], b['dedupe_hash'])


# =============================================================================
# Body composition (Template v1)
# =============================================================================

class ComposeBodyTests(SimpleTestCase):

    def test_locked_heading_order(self):
        config = _minimal_config()
        gate = {
            'tripped': True, 'severity': 'high',
            'reasons': ['R1', 'R2'],
            'reason_details': ['d1', 'd2'],
        }
        body, actions = _compose_body(
            config, {'x': 1}, gate,
            narrative='## Recommended Actions\n- A\n- B\n',
            narrative_error=None,
        )
        # Heading order: Headline, Severity, [extras], Agent Analysis, Recommended
        heading_positions = {}
        for h in ('## Headline', '## Severity & Gate Reasons', '## FakeTestAgent Analysis',
                  '## Recommended Actions'):
            self.assertIn(h, body)
            heading_positions[h] = body.index(h)
        self.assertLess(heading_positions['## Headline'], heading_positions['## Severity & Gate Reasons'])
        self.assertLess(heading_positions['## Severity & Gate Reasons'],
                        heading_positions['## FakeTestAgent Analysis'])
        self.assertLess(heading_positions['## FakeTestAgent Analysis'],
                        heading_positions['## Recommended Actions'])

    def test_actions_extracted_from_narrative(self):
        config = _minimal_config()
        gate = {'severity': 'high', 'reasons': [], 'reason_details': []}
        narrative = "## Recommended Actions\n- First\n- Second\n- Third\n- Fourth\n"
        body, actions = _compose_body(config, {}, gate, narrative, None)
        self.assertEqual(actions, ['First', 'Second', 'Third'])
        self.assertIn('1. First', body)
        self.assertIn('3. Third', body)
        self.assertNotIn('4. Fourth', body)

    def test_narrative_unavailable_renders_error(self):
        config = _minimal_config()
        gate = {'severity': 'high', 'reasons': [], 'reason_details': []}
        body, actions = _compose_body(config, {}, gate, None, 'agent timed out')
        self.assertIn('FakeTestAgent narrative unavailable: agent timed out', body)
        self.assertEqual(actions, [])
        self.assertIn('_None extracted from FakeTestAgent narrative', body)

    def test_extra_sections_rendered_between_severity_and_analysis(self):
        config = _minimal_config(extra_sections=[
            ('Metrics', lambda m, g: [f'- total: {m.get("total", 0)}']),
            ('Agents', lambda m, g: ['- A: 5']),
        ])
        gate = {'severity': 'high', 'reasons': [], 'reason_details': []}
        body, _ = _compose_body(config, {'total': 99}, gate, 'x', None)
        self.assertIn('## Metrics', body)
        self.assertIn('- total: 99', body)
        self.assertIn('## Agents', body)
        # Extra sections come between Severity and Analysis
        self.assertLess(body.index('## Metrics'), body.index('## FakeTestAgent Analysis'))

    def test_empty_extra_section_omitted(self):
        """Section that returns [] must be completely omitted (no heading, no blank lines)."""
        config = _minimal_config(extra_sections=[
            ('Optional Section', lambda m, g: []),
            ('Always Present', lambda m, g: ['- value']),
        ])
        gate = {'severity': 'high', 'reasons': [], 'reason_details': []}
        body, _ = _compose_body(config, {}, gate, 'x', None)
        self.assertNotIn('## Optional Section', body)
        self.assertIn('## Always Present', body)

    def test_renderer_exception_does_not_crash(self):
        def broken(m, g):
            raise ValueError('oops')
        config = _minimal_config(extra_sections=[('Broken', broken)])
        gate = {'severity': 'high', 'reasons': [], 'reason_details': []}
        body, _ = _compose_body(config, {}, gate, 'x', None)
        self.assertIn('## Broken', body)
        self.assertIn('Section renderer failed: ValueError', body)


# =============================================================================
# Payload cap
# =============================================================================

class ApplyPayloadCapTests(SimpleTestCase):

    def test_under_cap_untouched(self):
        payload = {'a': 1, 'b': 'x' * 100}
        result = _apply_payload_cap(payload, cap_bytes=10_000)
        self.assertEqual(result, payload)

    def test_stage1_trims_long_lists(self):
        payload = {'items': list(range(100))}  # small ints, but many
        result = _apply_payload_cap(payload, cap_bytes=100)
        self.assertEqual(len(result['items']), 5)

    def test_stage2_truncates_long_error_strings(self):
        payload = {'error': 'x' * 5000}
        result = _apply_payload_cap(payload, cap_bytes=2000)
        self.assertIn('[truncated]', result['error'])
        self.assertLessEqual(len(result['error']), 1100)

    def test_stage3_drops_optional_sections_as_last_resort(self):
        payload = {
            'new_signatures_24h': [{'k': 'x' * 1000} for _ in range(50)],
            'spiking_agents': [{'k': 'x' * 1000} for _ in range(50)],
            'essential': 'keep me',
        }
        result = _apply_payload_cap(payload, cap_bytes=500)
        self.assertNotIn('new_signatures_24h', result)
        self.assertNotIn('spiking_agents', result)
        self.assertEqual(result['essential'], 'keep me')
        self.assertTrue(result.get('_payload_truncated'))

    def test_input_not_mutated(self):
        original = {'items': list(range(100)), 'error': 'x' * 5000}
        snapshot = {'items': list(original['items']), 'error': original['error']}
        _apply_payload_cap(original, cap_bytes=500)
        self.assertEqual(original['items'], snapshot['items'])
        self.assertEqual(original['error'], snapshot['error'])


# =============================================================================
# run_diagnostic — status branches
# =============================================================================

class RunDiagnosticTests(SimpleTestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_feature_flag_off_skips_everything(self):
        config = _minimal_config()
        # Default: flag not set → False
        result = run_diagnostic(config)
        self.assertEqual(result['status'], 'skipped')
        self.assertEqual(result['reason'], 'disabled')
        config.metrics_collector.assert_not_called()  # type: ignore[attr-defined]

    @override_settings(TEST_DIAGNOSTIC_ENABLED='true', TEST_DIAGNOSTIC_POSTING_ENABLED='false')
    def test_gate_clear_returns_clear_no_dispatch(self):
        config = _minimal_config(
            gate_evaluator=_build_gate_evaluator({'tripped': False, 'severity': None, 'reasons': []}),
        )
        with patch('core.services.scheduled_diagnostic_runner._resolve_import_path') as _resolve:
            result = run_diagnostic(config)
        self.assertEqual(result['status'], 'clear')
        _resolve.assert_not_called()

    @override_settings(TEST_DIAGNOSTIC_ENABLED='true', TEST_DIAGNOSTIC_POSTING_ENABLED='false')
    def test_metrics_collector_crash_returns_error(self):
        collector = MagicMock(side_effect=RuntimeError('boom'))
        config = _minimal_config(metrics_collector=collector)
        result = run_diagnostic(config)
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['stage'], 'collect_metrics')
        self.assertIn('boom', result['error'])

    @override_settings(TEST_DIAGNOSTIC_ENABLED='true', TEST_DIAGNOSTIC_POSTING_ENABLED='false')
    def test_posting_disabled_logs_without_enqueue(self):
        config = _minimal_config()
        with patch('core.tasks.execute_agent_task.apply_async') as apply_async_mock:
            apply_async_mock.return_value = MagicMock(id='fake-agent-id')
            result = run_diagnostic(config)
        self.assertEqual(result['status'], 'log_only')
        self.assertEqual(result['agent_async_task_id'], 'fake-agent-id')

    @override_settings(TEST_DIAGNOSTIC_ENABLED='true', TEST_DIAGNOSTIC_POSTING_ENABLED='true')
    def test_gated_by_cooldown_returns_gated_status(self):
        config = _minimal_config()
        # Pre-populate cooldown key (the hash depends on dedupe_payload_builder)
        now = timezone.now()
        gate = config.gate_evaluator(None)  # type: ignore[arg-type]
        dc = _dedupe_and_cooldown_check(config, now, gate, {})
        cache.set(dc['cooldown_key'], 'x', timeout=3600)
        with patch('core.tasks.execute_agent_task.apply_async') as apply_async_mock:
            result = run_diagnostic(config)
        self.assertEqual(result['status'], 'gated_by_dedupe_or_cooldown')
        apply_async_mock.assert_not_called()

    @override_settings(TEST_DIAGNOSTIC_ENABLED='true', TEST_DIAGNOSTIC_POSTING_ENABLED='true')
    def test_full_dispatch_path(self):
        config = _minimal_config(post_task_import_path='os.path:join')
        fake_agent_result = MagicMock(id='fake-agent-id')
        fake_post_result = MagicMock(id='fake-post-id')
        with patch('core.tasks.execute_agent_task.apply_async', return_value=fake_agent_result), \
             patch('core.services.scheduled_diagnostic_runner._resolve_import_path') as resolve_mock:
            resolve_mock.return_value = MagicMock()
            resolve_mock.return_value.apply_async.return_value = fake_post_result
            result = run_diagnostic(config)
        self.assertEqual(result['status'], 'dispatched')
        self.assertEqual(result['agent_async_task_id'], 'fake-agent-id')
        self.assertEqual(result['post_async_task_id'], 'fake-post-id')

    @override_settings(TEST_DIAGNOSTIC_ENABLED='true', TEST_DIAGNOSTIC_POSTING_ENABLED='true')
    def test_missing_post_task_import_path_returns_enqueue_failed(self):
        config = _minimal_config(post_task_import_path='')
        with patch('core.tasks.execute_agent_task.apply_async') as apply_async_mock:
            apply_async_mock.return_value = MagicMock(id='fake')
            result = run_diagnostic(config)
        self.assertEqual(result['status'], 'enqueue_failed')

    @override_settings(TEST_DIAGNOSTIC_ENABLED='true', TEST_DIAGNOSTIC_POSTING_ENABLED='false')
    def test_agent_dispatch_error_captured_but_continues(self):
        config = _minimal_config()
        with patch('core.tasks.execute_agent_task.apply_async',
                   side_effect=RuntimeError('agent down')):
            result = run_diagnostic(config)
        self.assertEqual(result['status'], 'log_only')
        self.assertIn('agent down', result['dispatch_error'])


# =============================================================================
# post_diagnostic — idempotence + narrative handling
# =============================================================================

class PostDiagnosticTests(SimpleTestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def _base_kwargs(self):
        return dict(
            agent_async_task_id=None,
            title='test title',
            severity='high',
            gate={'severity': 'high', 'reasons': [], 'reason_details': []},
            metrics={},
            structured_payload={'dedupe_hash': 'abc123def456'},
        )

    def test_idempotent_skips_on_posted_marker(self):
        config = _minimal_config()
        posted_key = f'{config.cache_key_prefix}:posted:abc123def456'
        cache.set(posted_key, '1', timeout=3600)
        with patch('core.services.human_attention_bridge.attention_bridge.create_diagnostic_alert') as bridge:
            result = post_diagnostic(config, **self._base_kwargs())
        self.assertEqual(result['status'], 'already_posted')
        bridge.assert_not_called()

    def test_posts_via_bridge_with_correct_diagnostic_type(self):
        config = _minimal_config()
        with patch('core.services.human_attention_bridge.attention_bridge.create_diagnostic_alert') as bridge:
            result = post_diagnostic(config, **self._base_kwargs())
        self.assertEqual(result['status'], 'posted')
        bridge.assert_called_once()
        kwargs = bridge.call_args.kwargs
        self.assertEqual(kwargs['diagnostic_type'], 'test_diagnostic')
        self.assertEqual(kwargs['source_agent'], 'FakeTestAgent')
        self.assertEqual(kwargs['urgency'], 'high')
        self.assertIn('## Headline', kwargs['summary'])

    def test_bridge_failure_returns_post_failed(self):
        config = _minimal_config()
        with patch('core.services.human_attention_bridge.attention_bridge.create_diagnostic_alert',
                   side_effect=RuntimeError('bridge down')):
            result = post_diagnostic(config, **self._base_kwargs())
        self.assertEqual(result['status'], 'post_failed')
        self.assertIn('bridge down', result['error'])

    def test_sets_posted_marker_on_success(self):
        config = _minimal_config()
        posted_key = f'{config.cache_key_prefix}:posted:abc123def456'
        self.assertIsNone(cache.get(posted_key))
        with patch('core.services.human_attention_bridge.attention_bridge.create_diagnostic_alert'):
            post_diagnostic(config, **self._base_kwargs())
        self.assertEqual(cache.get(posted_key), '1')
