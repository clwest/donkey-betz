"""
Session 1096: anti-spam safety rails — escalation + daily cap + rollup tests.
==============================================================================

Rigby's queued priority from Session 1095 wrap:
    "That's the gating layer that turns all this great detection work
    into something you can actually live with."

Under test:

1. `_is_escalation` severity ordering helper
2. `_dedupe_and_cooldown_check` with the new rules:
   - Same-day already-posted blocks lateral reposts (severity not higher)
   - Severity escalation (upward) bypasses the one-per-day guard
   - Daily post cap (default 3) blocks even escalations once reached
3. Suppressed-event rollup counter accumulates on block, drains on fire
4. Rendered body includes escalation badge + rollup block when active

Run:
    python manage.py test core.tests.test_anti_spam_rails -v2
"""
from datetime import datetime, timedelta, timezone as dt_tz
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from core.services.scheduled_diagnostic_runner import (
    DiagnosticConfig,
    _compose_body,
    _consume_suppressed_rollup,
    _dedupe_and_cooldown_check,
    _is_escalation,
    _record_suppressed_event,
    run_diagnostic,
)


# =============================================================================
# _is_escalation — severity ordering
# =============================================================================

class IsEscalationTests(SimpleTestCase):

    def test_high_to_critical_is_escalation(self):
        self.assertTrue(_is_escalation('critical', 'high'))

    def test_medium_to_high_is_escalation(self):
        self.assertTrue(_is_escalation('high', 'medium'))

    def test_low_to_critical_is_escalation(self):
        self.assertTrue(_is_escalation('critical', 'low'))

    def test_same_severity_not_escalation(self):
        self.assertFalse(_is_escalation('high', 'high'))
        self.assertFalse(_is_escalation('critical', 'critical'))

    def test_critical_to_high_is_not_escalation(self):
        """Downgrade is not escalation — lateral rule handles it."""
        self.assertFalse(_is_escalation('high', 'critical'))

    def test_none_prior_treated_as_no_prior(self):
        """First post of the day has no prior — any severity escalates."""
        self.assertTrue(_is_escalation('medium', None))
        self.assertTrue(_is_escalation('critical', None))

    def test_unknown_values_default_safely(self):
        self.assertFalse(_is_escalation(None, 'high'))
        self.assertFalse(_is_escalation('', 'high'))


# =============================================================================
# Fixtures: minimal synthetic config for dedupe tests
# =============================================================================

def _minimal_config(**overrides) -> DiagnosticConfig:
    collector = MagicMock(return_value={'x': 1})
    evaluator = MagicMock(return_value={
        'tripped': True, 'severity': 'high',
        'reasons': ['R'], 'reason_details': ['d'],
    })
    defaults = dict(
        name='test_diag',
        diagnostic_type='test_diagnostic',
        agent_name='TestAgent',
        source_agent='TestAgent',
        log_prefix='TEST',
        metrics_collector=collector,
        gate_evaluator=evaluator,
        prompt_builder=lambda m, g: 'p',
        dedupe_payload_builder=lambda m, g, d: {'severity': g.get('severity'), 'd': d, 'r': sorted(g.get('reasons', []))},
        headline_builder=lambda m, g: 'headline',
        title_builder=lambda m, g, d: f'title {d}',
        enabled_env='TEST_DIAG_ENABLED',
        posting_enabled_env='TEST_DIAG_POSTING_ENABLED',
        cache_key_prefix='test_anti_spam',
        post_task_import_path='os.path:join',
    )
    defaults.update(overrides)
    return DiagnosticConfig(**defaults)


def _gate(severity='high', reasons=None):
    return {
        'tripped': True,
        'severity': severity,
        'reasons': reasons or ['DEFAULT_REASON'],
        'reason_details': ['detail'],
    }


# =============================================================================
# Dedupe check — severity escalation rule
# =============================================================================

class EscalationBypassTests(SimpleTestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_first_post_of_day_allowed(self):
        config = _minimal_config()
        result = _dedupe_and_cooldown_check(config, timezone.now(), _gate('high'), {})
        self.assertTrue(result['should_post'])

    def test_same_severity_same_day_blocked(self):
        """Second post at same severity → same_day_already_posted."""
        config = _minimal_config()
        now = timezone.now()
        # Simulate first post by setting max_sev key directly
        first = _dedupe_and_cooldown_check(config, now, _gate('high'), {})
        cache.set(first['max_sev_key'], 'high', timeout=3600)
        second = _dedupe_and_cooldown_check(config, now, _gate('high', ['DIFF_REASON']), {})
        self.assertFalse(second['should_post'])
        self.assertIn('same_day_already_posted', second['reason'])

    def test_escalation_upward_allowed(self):
        """high → critical inside same day should fire."""
        config = _minimal_config()
        now = timezone.now()
        first = _dedupe_and_cooldown_check(config, now, _gate('high'), {})
        cache.set(first['max_sev_key'], 'high', timeout=3600)
        escalated = _dedupe_and_cooldown_check(config, now, _gate('critical'), {})
        self.assertTrue(escalated['should_post'])
        self.assertTrue(escalated.get('is_escalation'))
        self.assertEqual(escalated.get('prior_max_severity'), 'high')

    def test_lateral_high_to_high_different_reasons_blocked(self):
        """Rigby's explicit case: high with different reasons is lateral,
        NOT escalation. Goes to rollup, doesn't post."""
        config = _minimal_config()
        now = timezone.now()
        first = _dedupe_and_cooldown_check(config, now, _gate('high', ['R1']), {})
        cache.set(first['max_sev_key'], 'high', timeout=3600)
        lateral = _dedupe_and_cooldown_check(config, now, _gate('high', ['R2']), {})
        self.assertFalse(lateral['should_post'])
        self.assertIn('same_day_already_posted', lateral['reason'])

    def test_downgrade_also_blocked_not_escalation(self):
        """critical → high is not escalation — gets rolled up."""
        config = _minimal_config()
        now = timezone.now()
        first = _dedupe_and_cooldown_check(config, now, _gate('critical'), {})
        cache.set(first['max_sev_key'], 'critical', timeout=3600)
        downgrade = _dedupe_and_cooldown_check(config, now, _gate('high'), {})
        self.assertFalse(downgrade['should_post'])
        self.assertIn('same_day_already_posted', downgrade['reason'])


# =============================================================================
# Dedupe check — daily post cap
# =============================================================================

class DailyPostCapTests(SimpleTestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_cap_reached_blocks_even_escalation(self):
        """At cap, even a new critical can't bypass — it rolls up."""
        config = _minimal_config(daily_post_cap=3)
        now = timezone.now()
        first = _dedupe_and_cooldown_check(config, now, _gate('high'), {})
        # Simulate 3 posts already today
        cache.set(first['posts_today_key'], 3, timeout=3600)
        cache.set(first['max_sev_key'], 'high', timeout=3600)
        # Even a critical escalation should be blocked
        escalated = _dedupe_and_cooldown_check(config, now, _gate('critical'), {})
        self.assertFalse(escalated['should_post'])
        self.assertIn('daily_cap_exceeded', escalated['reason'])

    def test_below_cap_allows(self):
        config = _minimal_config(daily_post_cap=3)
        now = timezone.now()
        first = _dedupe_and_cooldown_check(config, now, _gate('high'), {})
        cache.set(first['posts_today_key'], 2, timeout=3600)
        cache.set(first['max_sev_key'], 'high', timeout=3600)
        escalated = _dedupe_and_cooldown_check(config, now, _gate('critical'), {})
        self.assertTrue(escalated['should_post'])

    def test_config_default_is_three(self):
        """Sanity: the design default matches Rigby's sizing."""
        config = _minimal_config()
        self.assertEqual(config.daily_post_cap, 3)

    def test_configurable_lower_cap(self):
        """Ops can start conservative per Rigby's recommendation."""
        config = _minimal_config(daily_post_cap=2)
        now = timezone.now()
        first = _dedupe_and_cooldown_check(config, now, _gate('high'), {})
        cache.set(first['posts_today_key'], 2, timeout=3600)
        escalated = _dedupe_and_cooldown_check(config, now, _gate('critical'), {})
        self.assertFalse(escalated['should_post'])


# =============================================================================
# Suppressed-event rollup counter
# =============================================================================

class SuppressedRollupTests(SimpleTestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def _suppressed_key(self):
        return 'test_prefix:suppressed_today:2026-04-18'

    def test_record_and_consume_round_trip(self):
        key = self._suppressed_key()
        _record_suppressed_event(
            _minimal_config(cache_key_prefix='test_prefix'),
            suppressed_key=key,
            entry={'ts': 'now', 'severity': 'high', 'skip_reason': 'x'},
        )
        drained = _consume_suppressed_rollup(key)
        self.assertEqual(len(drained), 1)
        self.assertEqual(drained[0]['severity'], 'high')

    def test_consume_clears_cache(self):
        """After reading, the list must be empty so next post doesn't
        double-ride the rollup."""
        key = self._suppressed_key()
        _record_suppressed_event(
            _minimal_config(cache_key_prefix='test_prefix'),
            suppressed_key=key,
            entry={'ts': 'now', 'severity': 'medium'},
        )
        _consume_suppressed_rollup(key)
        # Second read returns empty
        self.assertEqual(_consume_suppressed_rollup(key), [])

    def test_accumulates_multiple_entries(self):
        key = self._suppressed_key()
        config = _minimal_config(cache_key_prefix='test_prefix')
        for i in range(5):
            _record_suppressed_event(
                config, suppressed_key=key,
                entry={'ts': f't{i}', 'severity': 'medium'},
            )
        drained = _consume_suppressed_rollup(key)
        self.assertEqual(len(drained), 5)

    def test_caps_at_50_entries(self):
        """Defensive: don't let the rollup balloon unboundedly."""
        key = self._suppressed_key()
        config = _minimal_config(cache_key_prefix='test_prefix')
        for i in range(100):
            _record_suppressed_event(
                config, suppressed_key=key,
                entry={'ts': f't{i}', 'severity': 'low'},
            )
        drained = _consume_suppressed_rollup(key)
        self.assertEqual(len(drained), 50)


# =============================================================================
# Body composition renders escalation + rollup blocks when present
# =============================================================================

class ComposeBodyEscalationTests(SimpleTestCase):

    def test_escalation_badge_rendered_when_upgrade(self):
        config = _minimal_config()
        body, _ = _compose_body(
            config, {}, _gate('critical'), narrative='agent text',
            narrative_error=None,
            structured_payload={
                'escalation': {'from': 'high', 'to': 'critical'},
            },
        )
        self.assertIn('⚠ Escalation', body)
        self.assertIn('`high` → `critical`', body)

    def test_no_badge_when_no_escalation_data(self):
        config = _minimal_config()
        body, _ = _compose_body(
            config, {}, _gate('high'), narrative='x',
            narrative_error=None, structured_payload={},
        )
        self.assertNotIn('⚠ Escalation', body)

    def test_rollup_block_rendered_when_suppressed_present(self):
        config = _minimal_config()
        body, _ = _compose_body(
            config, {}, _gate('critical'), narrative='x', narrative_error=None,
            structured_payload={
                'suppressed_rollup': {
                    'count': 3,
                    'note': 'Earlier alerts suppressed today',
                    'entries': [
                        {'ts': '2026-04-18T10:00:00', 'severity': 'high', 'reasons': ['R1'], 'skip_reason': 'same_day_already_posted'},
                        {'ts': '2026-04-18T12:00:00', 'severity': 'high', 'reasons': ['R2'], 'skip_reason': 'same_day_already_posted'},
                    ],
                },
            },
        )
        self.assertIn('Anti-Spam Rollup', body)
        self.assertIn('3 suppressed alert(s)', body)
        self.assertIn('same_day_already_posted', body)

    def test_no_rollup_block_when_empty(self):
        config = _minimal_config()
        body, _ = _compose_body(
            config, {}, _gate('high'), narrative='x', narrative_error=None,
            structured_payload={'suppressed_rollup': {'count': 0}},
        )
        self.assertNotIn('Anti-Spam Rollup', body)

    def test_backward_compat_no_structured_payload(self):
        """Old callers don't pass structured_payload — still works."""
        config = _minimal_config()
        body, _ = _compose_body(
            config, {}, _gate('high'), narrative='x', narrative_error=None,
        )
        self.assertIn('## Headline', body)
        self.assertNotIn('⚠ Escalation', body)
        self.assertNotIn('Anti-Spam Rollup', body)


# =============================================================================
# End-to-end: run_diagnostic records suppressed events + consumes on next fire
# =============================================================================

class EndToEndSuppressedRollupTests(SimpleTestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @override_settings(TEST_DIAG_ENABLED='true', TEST_DIAG_POSTING_ENABLED='true')
    def test_lateral_alert_increments_rollup_counter(self):
        """After first high post, a second high with different reasons
        is blocked AND recorded in the rollup counter."""
        config = _minimal_config()
        now = timezone.now()
        # Seed: first post already happened
        from core.services.scheduled_diagnostic_runner import _date_bucket
        date_bucket = _date_bucket(now, 'America/Denver')
        prefix = config.cache_key_prefix
        cache.set(f'{prefix}:max_sev_today:{date_bucket}', 'high', timeout=3600)
        cache.set(f'{prefix}:posts_today:{date_bucket}', 1, timeout=3600)

        # Now dispatch a second run with LATERAL alert (same severity, diff reasons)
        config.gate_evaluator = MagicMock(return_value={
            'tripped': True, 'severity': 'high',
            'reasons': ['DIFFERENT_REASON'], 'reason_details': ['d'],
        })
        with patch('core.tasks.execute_agent_task.apply_async') as apply_async_mock:
            apply_async_mock.return_value = MagicMock(id='fake-id')
            result = run_diagnostic(config)

        self.assertEqual(result['status'], 'gated_by_dedupe_or_cooldown')
        self.assertIn('same_day_already_posted', result['skip_reason'])

        # Rollup counter should now have an entry
        suppressed = cache.get(f'{prefix}:suppressed_today:{date_bucket}') or []
        self.assertEqual(len(suppressed), 1)
        self.assertEqual(suppressed[0]['severity'], 'high')

    @override_settings(TEST_DIAG_ENABLED='true', TEST_DIAG_POSTING_ENABLED='true')
    def test_escalation_post_drains_rollup_into_payload(self):
        """After suppressing 2 laterals, a critical escalation fires AND
        carries the suppressed_rollup into the structured_payload."""
        config = _minimal_config()
        now = timezone.now()
        from core.services.scheduled_diagnostic_runner import _date_bucket
        date_bucket = _date_bucket(now, 'America/Denver')
        prefix = config.cache_key_prefix

        # Seed: one post fired earlier at high, two suppressed laterals
        cache.set(f'{prefix}:max_sev_today:{date_bucket}', 'high', timeout=3600)
        cache.set(f'{prefix}:posts_today:{date_bucket}', 1, timeout=3600)
        cache.set(
            f'{prefix}:suppressed_today:{date_bucket}',
            [
                {'ts': 't1', 'severity': 'high', 'reasons': ['R2'], 'skip_reason': 'same_day_already_posted'},
                {'ts': 't2', 'severity': 'high', 'reasons': ['R3'], 'skip_reason': 'same_day_already_posted'},
            ],
            timeout=3600,
        )

        # Now a critical escalation comes in
        config.gate_evaluator = MagicMock(return_value={
            'tripped': True, 'severity': 'critical',
            'reasons': ['CRITICAL_REASON'], 'reason_details': ['d'],
        })

        with patch('core.tasks.execute_agent_task.apply_async') as apply_mock, \
             patch('core.services.scheduled_diagnostic_runner._resolve_import_path') as resolve_mock:
            apply_mock.return_value = MagicMock(id='fake-id')
            post_task_mock = MagicMock()
            post_task_mock.apply_async.return_value = MagicMock(id='fake-post-id')
            resolve_mock.return_value = post_task_mock
            result = run_diagnostic(config)

        self.assertEqual(result['status'], 'dispatched')

        # The enqueued post task should have received the rollup
        call_kwargs = post_task_mock.apply_async.call_args.kwargs['kwargs']
        sp = call_kwargs['structured_payload']
        self.assertIn('suppressed_rollup', sp)
        self.assertEqual(sp['suppressed_rollup']['count'], 2)
        # And escalation metadata is attached
        self.assertEqual(sp['escalation']['from'], 'high')
        self.assertEqual(sp['escalation']['to'], 'critical')

        # Rollup counter is drained (cleared)
        after = cache.get(f'{prefix}:suppressed_today:{date_bucket}') or []
        self.assertEqual(len(after), 0)

    @override_settings(TEST_DIAG_ENABLED='true', TEST_DIAG_POSTING_ENABLED='true')
    def test_first_post_increments_posts_counter(self):
        """On successful post, posts_today counter ticks up."""
        config = _minimal_config()
        now = timezone.now()
        from core.services.scheduled_diagnostic_runner import _date_bucket
        date_bucket = _date_bucket(now, 'America/Denver')
        prefix = config.cache_key_prefix

        with patch('core.tasks.execute_agent_task.apply_async') as apply_mock, \
             patch('core.services.scheduled_diagnostic_runner._resolve_import_path') as resolve_mock:
            apply_mock.return_value = MagicMock(id='fake-id')
            post_task_mock = MagicMock()
            post_task_mock.apply_async.return_value = MagicMock(id='fake-post-id')
            resolve_mock.return_value = post_task_mock
            result = run_diagnostic(config)

        self.assertEqual(result['status'], 'dispatched')
        self.assertEqual(cache.get(f'{prefix}:posts_today:{date_bucket}'), 1)
        self.assertEqual(cache.get(f'{prefix}:max_sev_today:{date_bucket}'), 'high')
