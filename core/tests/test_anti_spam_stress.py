"""
Session 1096: end-to-end anti-spam stress test — Rigby's explicit verification.
================================================================================

Rigby's gating condition for enabling COO POSTING=true (Session 1096 check-in):

    "Do one deterministic simulation before enabling POSTING: fire 12
    synthetic alerts across severities in a single MT date_bucket. Assert:
    first post allowed, only up to cap posts publish, escalation posts
    only if under cap, all suppressed entries roll up, and rollup drains
    on next allowed post."

This test IS that simulation. If it passes, the anti-spam rails are
validated end-to-end and POSTING can be enabled.

## Scenario (12 alerts in one day)

  alert  1-6 : severity=high, different primary_gate each (lateral)
  alert  7-8 : severity=critical (escalation)
  alert  9-12: severity=high (lateral at already-reached critical)

## Expected behavior with daily_post_cap=3

  alert 1    → POST #1 (first post of day)                  -- allowed
  alert 2-6  → 5 suppressed (lateral — same-day rule)        -- rolled up
  alert 7    → POST #2 (critical escalation, under cap)      -- allowed, rollup drains
  alert 8    → suppressed (same-day critical already posted) -- rolled up
  alert 9-12 → 4 suppressed (lateral + cap)                  -- rolled up

  FINAL:  2 posts (not 12), 10 suppressions across 2 rollup drains

This is the cap-3 behavior: first + one escalation + (would allow one
more high escalation if any existed in scenario), with everything else
rolled into either the escalation post or a later low-volume trigger.

Run:
    python manage.py test core.tests.test_anti_spam_stress -v2
"""
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.utils import timezone

from core.services.scheduled_diagnostic_runner import (
    DiagnosticConfig,
    _date_bucket,
    run_diagnostic,
)


class TwelveAlertStressTests(SimpleTestCase):
    """Deterministic end-to-end simulation for the anti-spam rails."""

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def _build_config(self, severity: str, reason: str, cap: int = 3) -> DiagnosticConfig:
        """Fresh config for each simulated alert — same cache_key_prefix
        so cache state accumulates across calls the way it would in
        production when beat triggers multiple runs per day."""
        evaluator = MagicMock(return_value={
            'tripped': True,
            'severity': severity,
            'reasons': [reason],
            'reason_details': [f'simulated {reason}'],
        })
        return DiagnosticConfig(
            name='stress_diag',
            diagnostic_type='stress_diagnostic',
            agent_name='StressAgent',
            source_agent='StressAgent',
            log_prefix='STRESS',
            metrics_collector=MagicMock(return_value={'synthetic': True}),
            gate_evaluator=evaluator,
            prompt_builder=lambda m, g: 'stress prompt',
            dedupe_payload_builder=lambda m, g, d: {
                'severity': g.get('severity'),
                'date_bucket': d,
                'reasons': sorted(g.get('reasons', [])),
            },
            headline_builder=lambda m, g: f'stress {g["severity"]}',
            title_builder=lambda m, g, d: f'stress title {d}',
            enabled_env='STRESS_ENABLED',
            posting_enabled_env='STRESS_POSTING',
            cache_key_prefix='stress_anti_spam',
            post_task_import_path='os.path:join',
            daily_post_cap=cap,
        )

    def _run_scenario_alert(
        self,
        severity: str,
        reason: str,
        cap: int = 3,
        apply_mock=None,
        post_task_mock=None,
    ) -> dict:
        """Execute one simulated alert through run_diagnostic and return the result."""
        config = self._build_config(severity, reason, cap=cap)
        if apply_mock is None:
            apply_mock = MagicMock()
            apply_mock.return_value = MagicMock(id=f'fake-agent-{reason}')
        if post_task_mock is None:
            post_task_mock = MagicMock()
            post_task_mock.apply_async.return_value = MagicMock(id=f'fake-post-{reason}')
        with patch('core.tasks.execute_agent_task.apply_async', apply_mock), \
             patch('core.services.scheduled_diagnostic_runner._resolve_import_path',
                   return_value=post_task_mock):
            result = run_diagnostic(config)
        return {
            'result': result,
            'apply_mock': apply_mock,
            'post_task_mock': post_task_mock,
        }

    @override_settings(STRESS_ENABLED='true', STRESS_POSTING='true')
    def test_twelve_alert_day_with_cap_3(self):
        """Rigby's explicit scenario. End-to-end assertions on every stage."""
        prefix = 'stress_anti_spam'
        posts_fired = []
        rollup_drains = []

        def record_stage(alert_label: str, outcome: dict) -> None:
            """After each alert, read cache state for inspection."""
            date_bucket = _date_bucket(timezone.now(), 'America/Denver')
            suppressed_key = f'{prefix}:suppressed_today:{date_bucket}'
            sup_list = cache.get(suppressed_key) or []
            if outcome['result']['status'] == 'dispatched':
                # Capture the rollup that just drained (from post_task kwargs)
                call = outcome['post_task_mock'].apply_async.call_args
                if call:
                    sp = call.kwargs['kwargs']['structured_payload']
                    rollup_drains.append({
                        'alert': alert_label,
                        'rollup_count_drained': (sp.get('suppressed_rollup') or {}).get('count', 0),
                        'escalation': sp.get('escalation'),
                        'anti_spam_status': sp.get('anti_spam_status'),
                    })
                posts_fired.append(alert_label)

        # ── alerts 1-6: six highs with different reasons
        for i in range(1, 7):
            outcome = self._run_scenario_alert('high', f'GATE_R{i}')
            record_stage(f'alert_{i}_high_R{i}', outcome)

        # Alerts 2-6 should be suppressed
        suppressed_after_six = cache.get(f'{prefix}:suppressed_today:{_date_bucket(timezone.now(), "America/Denver")}') or []
        self.assertEqual(len(posts_fired), 1, 'only alert 1 should have fired')
        self.assertEqual(len(suppressed_after_six), 5, '5 laterals suppressed (alerts 2-6)')

        # ── alerts 7-8: two critical escalations
        for i in range(7, 9):
            outcome = self._run_scenario_alert('critical', f'CRIT_R{i}')
            record_stage(f'alert_{i}_critical', outcome)

        # Alert 7 should have fired (escalation from high to critical)
        # Alert 8 should be suppressed (critical already posted this day)
        self.assertEqual(len(posts_fired), 2,
                         'alert 7 escalation fires; alert 8 is same-day critical (suppressed)')

        # Verify rollup drained on alert 7 with 5 entries (from alerts 2-6)
        alert_7_drain = rollup_drains[-1]
        self.assertEqual(alert_7_drain['rollup_count_drained'], 5,
                         'alert 7 should drain the 5 lateral-suppressed entries from alerts 2-6')
        self.assertIsNotNone(alert_7_drain['escalation'])
        self.assertEqual(alert_7_drain['escalation']['from'], 'high')
        self.assertEqual(alert_7_drain['escalation']['to'], 'critical')

        # ── alerts 9-12: four more highs (below the cap of 3, but all are lateral)
        for i in range(9, 13):
            outcome = self._run_scenario_alert('high', f'LATE_R{i}')
            record_stage(f'alert_{i}_high_late', outcome)

        # Expected final state
        self.assertEqual(len(posts_fired), 2,
                         'alerts 9-12 are downgrades (critical→high) — all suppressed, no 3rd post')

        # Suppressed counter after all 12 alerts = 5 (from 7) drained to 0, plus
        # alert 8 + alerts 9-12 = 5 accumulated
        final_suppressed = cache.get(f'{prefix}:suppressed_today:{_date_bucket(timezone.now(), "America/Denver")}') or []
        self.assertEqual(len(final_suppressed), 5,
                         'alert 8 (critical lateral) + alerts 9-12 (high downgrades) = 5 accumulated since last drain')

        # Posts_today counter matches actual fires
        posts_counter = cache.get(f'{prefix}:posts_today:{_date_bucket(timezone.now(), "America/Denver")}')
        self.assertEqual(posts_counter, 2)

        # Max severity today = critical (from the escalation)
        max_sev = cache.get(f'{prefix}:max_sev_today:{_date_bucket(timezone.now(), "America/Denver")}')
        self.assertEqual(max_sev, 'critical')

        # ── Summary for visibility in test output
        print(f'\n=== STRESS TEST SUMMARY (cap=3, 12 alerts) ===')
        print(f'Posts fired: {len(posts_fired)} — {posts_fired}')
        print(f'Rollup drains: {[d["rollup_count_drained"] for d in rollup_drains]}')
        print(f'Final suppressed (pending next drain): {len(final_suppressed)}')
        print(f'Posts counter: {posts_counter}, Max severity: {max_sev}')

    @override_settings(STRESS_ENABLED='true', STRESS_POSTING='true')
    def test_cap_hit_blocks_escalation(self):
        """Rigby's secondary rule: even a critical escalation cannot
        override the daily cap. At cap=3, a new critical rolls up."""
        prefix = 'stress_anti_spam'

        # Pre-seed: 3 posts already today (cap=3 reached)
        date_bucket = _date_bucket(timezone.now(), 'America/Denver')
        cache.set(f'{prefix}:posts_today:{date_bucket}', 3, timeout=3600)
        cache.set(f'{prefix}:max_sev_today:{date_bucket}', 'high', timeout=3600)

        outcome = self._run_scenario_alert('critical', 'LATE_CRIT')
        result = outcome['result']
        self.assertEqual(result['status'], 'gated_by_dedupe_or_cooldown')
        self.assertIn('daily_cap_exceeded', result['skip_reason'])

        # The cap-blocked critical alert should be in the rollup for later
        suppressed = cache.get(f'{prefix}:suppressed_today:{date_bucket}') or []
        self.assertEqual(len(suppressed), 1)
        self.assertEqual(suppressed[0]['severity'], 'critical')
        self.assertEqual(suppressed[0]['primary_gate'], 'LATE_CRIT')

    @override_settings(STRESS_ENABLED='true', STRESS_POSTING='true')
    def test_rollup_drains_on_next_fire_not_double_ride(self):
        """After draining into post A, a second allowed post B must NOT
        re-include those already-consumed suppressions."""
        prefix = 'stress_anti_spam'
        date_bucket = _date_bucket(timezone.now(), 'America/Denver')

        # Alert 1: first post (no rollup yet)
        alert_1 = self._run_scenario_alert('medium', 'BASE')
        self.assertEqual(alert_1['result']['status'], 'dispatched')

        # Alert 2: lateral medium → suppressed, added to rollup
        alert_2 = self._run_scenario_alert('medium', 'DIFF')
        self.assertEqual(alert_2['result']['status'], 'gated_by_dedupe_or_cooldown')

        # Alert 3: escalation to high → fires, drains rollup (should get 1 entry)
        alert_3 = self._run_scenario_alert('high', 'ESCALATE')
        self.assertEqual(alert_3['result']['status'], 'dispatched')
        call_3 = alert_3['post_task_mock'].apply_async.call_args
        sp_3 = call_3.kwargs['kwargs']['structured_payload']
        self.assertEqual((sp_3.get('suppressed_rollup') or {}).get('count', 0), 1)

        # Alert 4: another escalation to critical → fires, should drain 0 (no new sups)
        alert_4 = self._run_scenario_alert('critical', 'ESCALATE_MORE')
        self.assertEqual(alert_4['result']['status'], 'dispatched')
        call_4 = alert_4['post_task_mock'].apply_async.call_args
        sp_4 = call_4.kwargs['kwargs']['structured_payload']
        # suppressed_rollup should be absent (nothing to drain) — 'count' = 0
        # means either the key isn't set or it's 0. Either way, no double-ride.
        self.assertEqual((sp_4.get('suppressed_rollup') or {}).get('count', 0), 0)
