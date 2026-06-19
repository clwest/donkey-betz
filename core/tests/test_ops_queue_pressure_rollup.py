"""
Session 1164 — ops_tool.overview queue_pressure rollup.

Phase 2 of the COO Operator Report queue-pressure work (Phase 1 was
cockpit_tool.queue_lengths in PR #2289). The rollup MUST reduce cockpit
output, never re-classify — single source of truth lives in cockpit.

Mocks cockpit_tool.queue_lengths so the test does not depend on Redis or
live Celery state.

Run: python manage.py test core.tests.test_ops_queue_pressure_rollup -v2
"""

from unittest.mock import patch

from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher


class TestOpsQueuePressureRollup(TestCase):

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _cockpit_return(self, queues, overall_state='GREEN', redis_error=None):
        out = {
            'action': 'queue_lengths',
            'queues': queues,
            'overall_state': overall_state,
            'overall_reasons': [],
        }
        if redis_error:
            out['redis_error'] = redis_error
        return out

    def _rollup(self, cockpit_payload):
        with patch.object(
            self.dispatcher, '_handle_cockpit', return_value=cockpit_payload,
        ):
            return self.dispatcher._ops_queue_pressure_rollup(
                user_id=1, trace_id='test-queue-pressure',
            )

    def test_no_reclassification_state_and_reasons_passthrough(self):
        cockpit = self._cockpit_return(
            queues={
                'long_running': {
                    'state': 'CRITICAL',
                    'depth': 1000,
                    'oldest_age_seconds': None,
                    'reasons': ['depth>=500', 'age_unknown'],
                },
            },
            overall_state='CRITICAL',
        )
        rollup = self._rollup(cockpit)
        self.assertEqual(rollup['overall_state'], 'CRITICAL')
        self.assertEqual(len(rollup['top_offenders']), 1)
        offender = rollup['top_offenders'][0]
        self.assertEqual(offender['state'], 'CRITICAL')
        self.assertEqual(offender['reasons'], ['depth>=500', 'age_unknown'])
        self.assertEqual(offender['depth'], 1000)

    def test_severity_counts_correct(self):
        cockpit = self._cockpit_return(
            queues={
                'q_crit_a': {'state': 'CRITICAL', 'depth': 600, 'oldest_age_seconds': None, 'reasons': []},
                'q_crit_b': {'state': 'CRITICAL', 'depth': 800, 'oldest_age_seconds': None, 'reasons': []},
                'q_red': {'state': 'RED', 'depth': 250, 'oldest_age_seconds': None, 'reasons': []},
                'q_yellow': {'state': 'YELLOW', 'depth': 60, 'oldest_age_seconds': None, 'reasons': []},
                'q_green': {'state': 'GREEN', 'depth': 0, 'oldest_age_seconds': None, 'reasons': []},
            },
            overall_state='CRITICAL',
        )
        rollup = self._rollup(cockpit)
        self.assertEqual(rollup['queues_critical_count'], 2)
        self.assertEqual(rollup['queues_red_count'], 1)

    def test_top_offenders_sorted_and_capped_at_3(self):
        cockpit = self._cockpit_return(
            queues={
                'q1': {'state': 'YELLOW', 'depth': 100, 'oldest_age_seconds': None, 'reasons': []},
                'q2': {'state': 'CRITICAL', 'depth': 500, 'oldest_age_seconds': None, 'reasons': []},
                'q3': {'state': 'RED', 'depth': 300, 'oldest_age_seconds': None, 'reasons': []},
                'q4': {'state': 'CRITICAL', 'depth': 900, 'oldest_age_seconds': None, 'reasons': []},
                'q5': {'state': 'YELLOW', 'depth': 70, 'oldest_age_seconds': None, 'reasons': []},
            },
            overall_state='CRITICAL',
        )
        rollup = self._rollup(cockpit)
        offenders = rollup['top_offenders']
        self.assertEqual(len(offenders), 3, 'top_offenders must cap at 3')
        # Severity-first ordering: CRITICAL before RED before YELLOW.
        self.assertEqual([o['state'] for o in offenders], ['CRITICAL', 'CRITICAL', 'RED'])
        # Within CRITICAL: higher depth first.
        self.assertEqual(offenders[0]['queue'], 'q4')
        self.assertEqual(offenders[1]['queue'], 'q2')

    def test_green_queues_excluded_from_offenders(self):
        cockpit = self._cockpit_return(
            queues={
                'q_green_a': {'state': 'GREEN', 'depth': 0, 'oldest_age_seconds': None, 'reasons': []},
                'q_green_b': {'state': 'GREEN', 'depth': 10, 'oldest_age_seconds': None, 'reasons': []},
                'q_yellow': {'state': 'YELLOW', 'depth': 60, 'oldest_age_seconds': None, 'reasons': ['depth>=50']},
            },
            overall_state='YELLOW',
        )
        rollup = self._rollup(cockpit)
        self.assertEqual(len(rollup['top_offenders']), 1)
        self.assertEqual(rollup['top_offenders'][0]['queue'], 'q_yellow')
        self.assertEqual(rollup['queues_critical_count'], 0)
        self.assertEqual(rollup['queues_red_count'], 0)

    def test_redis_error_passthrough(self):
        cockpit = self._cockpit_return(
            queues={
                'long_running': {'state': 'GREEN', 'depth': 0, 'oldest_age_seconds': None, 'reasons': []},
            },
            overall_state='GREEN',
            redis_error='ConnectionError: timeout',
        )
        rollup = self._rollup(cockpit)
        self.assertEqual(rollup['redis_error'], 'ConnectionError: timeout')
        self.assertEqual(rollup['overall_state'], 'GREEN')

    def test_cockpit_failure_returns_unknown_block(self):
        rollup = self._rollup({'error': 'cockpit unavailable'})
        self.assertEqual(rollup['overall_state'], 'UNKNOWN')
        self.assertIn('error', rollup)

    def test_cockpit_non_dict_returns_unknown_block(self):
        rollup = self._rollup('not a dict')
        self.assertEqual(rollup['overall_state'], 'UNKNOWN')

    def test_rollup_has_generated_at_timestamp(self):
        cockpit = self._cockpit_return(queues={}, overall_state='GREEN')
        rollup = self._rollup(cockpit)
        self.assertIn('generated_at', rollup)
        # ISO 8601 timestamp.
        self.assertRegex(rollup['generated_at'], r'^\d{4}-\d{2}-\d{2}T')
