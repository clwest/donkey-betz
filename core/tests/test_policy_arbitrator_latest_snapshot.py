"""
Tests for PolicyArbitrator.get_latest_snapshot() and the
`latest_overrides_snapshot` PA tool action.

Honest exposure of the single-row overwrite storage mechanism — the
patent Disclosure L §5 Component 4 `FinalAppliedOverrides.objects.create(...)`
pattern is aspirational, not as-built. See Disclosure L §14 addendum
and `docs/narratives/SELF_TUNING_AND_EXPERIMENTATION.md` §6.4 for the
drift record. The B-style correct fix (append-only per-cycle model)
is queued as a follow-on; this test pins the C-style honest behavior
in the interim.
"""
import json

from django.test import TestCase

from core.models.system import SystemConfiguration
from core.services.ops_autopilot.governance import PolicyArbitrator


class GetLatestSnapshotTests(TestCase):
    """Direct unit tests for PolicyArbitrator.get_latest_snapshot()."""

    def test_returns_friendly_null_when_no_snapshot_exists(self):
        """No SystemConfiguration row → found=False with explainer note."""
        SystemConfiguration.objects.filter(
            key='policy_arbitrator_snapshot'
        ).delete()

        result = PolicyArbitrator().get_latest_snapshot()

        self.assertFalse(result['found'])
        self.assertIsNone(result['cycle_id'])
        self.assertIsNone(result['ts'])
        self.assertIsNone(result['row_updated_at'])
        self.assertEqual(result['knob_count'], 0)
        self.assertEqual(result['knobs'], {})
        self.assertEqual(result['storage']['key'], 'policy_arbitrator_snapshot')
        self.assertIn('single-row overwrite', result['storage']['mechanism'])
        self.assertIn('No arbitrator snapshot has been written', result['note'])

    def test_returns_parsed_payload_when_row_exists(self):
        """Existing row → fields parsed from JSON payload + storage context."""
        payload = {
            'cycle_id': 'test-cycle-uuid-1234',
            'ts': '2026-05-26T20:00:00+00:00',
            'knobs': {
                'budget_hard_limit_pct': {
                    'value': '0.90',
                    'owner': 'budget_controller',
                    'priority': 10,
                },
                'agent_timeout_seconds': {
                    'value': '120',
                    'owner': 'timeout_remediation_playbook',
                    'priority': 20,
                },
            },
            'knob_count': 2,
        }
        SystemConfiguration.objects.update_or_create(
            key='policy_arbitrator_snapshot',
            defaults={'value': json.dumps(payload)},
        )

        result = PolicyArbitrator().get_latest_snapshot()

        self.assertTrue(result['found'])
        self.assertEqual(result['cycle_id'], 'test-cycle-uuid-1234')
        self.assertEqual(result['ts'], '2026-05-26T20:00:00+00:00')
        self.assertIsNotNone(result['row_updated_at'])
        # row_updated_at is the DB row's updated_at, surfaced for
        # operator-side freshness checks ("is this snapshot stale?")
        # without needing to infer from cycle cadence.
        self.assertEqual(result['knob_count'], 2)
        self.assertEqual(
            result['knobs']['budget_hard_limit_pct']['owner'],
            'budget_controller',
        )
        self.assertEqual(result['storage']['model'], 'SystemConfiguration')
        self.assertIn(
            'Per-cycle history is not stored',
            result['note'],
        )

    def test_handles_corrupt_json_payload_without_crashing(self):
        """Row exists but value is not valid JSON → degraded but not 500."""
        SystemConfiguration.objects.update_or_create(
            key='policy_arbitrator_snapshot',
            defaults={'value': 'not-valid-json{{'},
        )

        result = PolicyArbitrator().get_latest_snapshot()

        self.assertTrue(result['found'])
        self.assertIsNone(result['cycle_id'])
        self.assertEqual(result['knob_count'], 0)
        self.assertEqual(result['knobs'], {})
        self.assertEqual(result['storage']['model'], 'SystemConfiguration')

    def test_storage_context_documents_no_time_travel(self):
        """The storage block always names the as-built mechanism honestly."""
        result = PolicyArbitrator().get_latest_snapshot()

        self.assertEqual(
            result['storage']['mechanism'],
            'single-row overwrite per cycle (no per-cycle history)',
        )


class LatestOverridesSnapshotHandlerTests(TestCase):
    """Smoke test for the `latest_overrides_snapshot` ops_tool action."""

    def test_handler_returns_action_label_and_snapshot_fields(self):
        """The dispatcher handler echoes the action label + snapshot dict."""
        # Late import: the handler lives on a Mixin assembled by
        # ToolDispatcher; we exercise the action by calling the mixin
        # method directly with the same payload contract.
        from core.services.td_handlers_ops import OpsHandlersMixin

        SystemConfiguration.objects.update_or_create(
            key='policy_arbitrator_snapshot',
            defaults={'value': json.dumps({
                'cycle_id': 'handler-test-cycle',
                'ts': '2026-05-26T21:00:00+00:00',
                'knobs': {},
                'knob_count': 0,
            })},
        )

        handler = OpsHandlersMixin()
        result = handler._handle_autopilot(
            tool_name='ops_tool',
            payload={'action': 'latest_overrides_snapshot'},
            user_id=None,
            trace_id='test-trace',
        )

        self.assertEqual(result['action'], 'latest_overrides_snapshot')
        self.assertTrue(result['found'])
        self.assertEqual(result['cycle_id'], 'handler-test-cycle')
        self.assertEqual(result['storage']['key'], 'policy_arbitrator_snapshot')
