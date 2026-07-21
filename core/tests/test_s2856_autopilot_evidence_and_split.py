"""Session 2856 slate #2 + #3 —
autopilot_tool.history include_evidence + enforcement_report auto/operator split.

Locks in the S2856 read-surface additions on td_handlers_ops.py:
  - `_handle_autopilot(action='history', include_evidence=True)` returns
    evidence + result JSONField values per row.
  - `_handle_workspace_budget(action='enforcement_report')` per-workspace
    rows carry auto_events_count + operator_events_count using
    evidence.actor_user_id presence as the decision rule.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone as tz

from core.models_diagnostic_pipeline import AutopilotAction
from core.models_skin_layer import ProjectWorkspace
from core.services.td_handlers_ops import OpsHandlersMixin


User = get_user_model()


class _OpsProxy(OpsHandlersMixin):
    """Same instantiation pattern as core/views_ops_console.py:133."""
    pass


class AutopilotHistoryIncludeEvidenceTests(TestCase):
    """The `history` action gains an opt-in `include_evidence` param."""

    def setUp(self):
        AutopilotAction.objects.create(
            action_type='workspace_budget_freeze',
            agent_name='BudgetController',
            policy='workspace_budget_controller',
            dry_run=False,
            evidence={
                'trigger': 'autopilot_cycle',
                'cap': 5.0,
                'daily_total': 5.25,
            },
            result={'workspace_id': 'abc', 'cap': 5.0, 'daily_spend': 5.25},
        )

    def test_default_omits_evidence_and_result(self):
        proxy = _OpsProxy()
        response = proxy._handle_autopilot(
            tool_name='autopilot_tool',
            payload={'action': 'history', 'limit': 5},
            user_id=None,
            trace_id='s2856-test',
        )
        self.assertEqual(response['action'], 'history')
        self.assertFalse(response['include_evidence'])
        self.assertGreaterEqual(response['count'], 1)
        for row in response['actions']:
            self.assertNotIn('evidence', row)
            self.assertNotIn('result', row)

    def test_include_evidence_true_surfaces_json_fields(self):
        proxy = _OpsProxy()
        response = proxy._handle_autopilot(
            tool_name='autopilot_tool',
            payload={
                'action': 'history',
                'limit': 5,
                'include_evidence': True,
            },
            user_id=None,
            trace_id='s2856-test',
        )
        self.assertTrue(response['include_evidence'])
        self.assertGreaterEqual(response['count'], 1)
        row = response['actions'][0]
        self.assertIn('evidence', row)
        self.assertIn('result', row)
        self.assertEqual(row['evidence']['trigger'], 'autopilot_cycle')
        self.assertEqual(row['result']['workspace_id'], 'abc')

    def test_limit_capped_at_100(self):
        # Seed 3 extra rows so we exceed the requested cap
        for i in range(3):
            AutopilotAction.objects.create(
                action_type='dry_run',
                policy='test',
                evidence={},
                result={},
            )
        proxy = _OpsProxy()
        response = proxy._handle_autopilot(
            tool_name='autopilot_tool',
            payload={'action': 'history', 'limit': 999},
            user_id=None,
            trace_id='s2856-test',
        )
        # Cap enforced upstream — even if we asked for 999 the ceiling is 100
        self.assertLessEqual(response['count'], 100)


class EnforcementReportAutoOperatorSplitTests(TestCase):
    """`enforcement_report` per-workspace rows carry auto vs operator counts,
    split by presence of evidence.actor_user_id."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s2856split',
            email='s2856split@test.com',
            password='pw',
            is_staff=True,
        )
        self.workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name='S2856 Split Workspace',
        )
        self.wid = str(self.workspace.id)

    def _seed_event(self, action_type, actor_user_id=None, extra_evidence=None):
        evidence = {'workspace_id': self.wid}
        if actor_user_id is not None:
            evidence['actor_user_id'] = str(actor_user_id)
        if extra_evidence:
            evidence.update(extra_evidence)
        return AutopilotAction.objects.create(
            action_type=action_type,
            agent_name='BudgetController',
            policy='workspace_budget_controller',
            dry_run=False,
            evidence=evidence,
            result={'workspace_id': self.wid},
        )

    def _run_report(self):
        proxy = _OpsProxy()
        return proxy._handle_workspace_budget(
            tool_name='workspace_budget_tool',
            payload={'action': 'enforcement_report', 'window': '24h'},
            user_id=self.user.id,
            trace_id='s2856-test',
        )

    def _row_for_workspace(self, response):
        for row in response['rows']:
            if row['workspace_id'] == self.wid:
                return row
        self.fail(f'workspace {self.wid} not found in rows: {response["rows"]}')

    def test_auto_only_row(self):
        # Autopilot cycle write — no actor_user_id
        self._seed_event(
            'workspace_budget_freeze',
            extra_evidence={'trigger': 'autopilot_cycle'},
        )
        row = self._row_for_workspace(self._run_report())
        self.assertEqual(row['enforcement_events_count'], 1)
        self.assertEqual(row['auto_events_count'], 1)
        self.assertEqual(row['operator_events_count'], 0)

    def test_operator_only_row(self):
        # Operator set_cap trigger
        self._seed_event(
            'workspace_downgrade_set',
            actor_user_id=self.user.id,
            extra_evidence={'trigger': 'operator_set_cap_immediate'},
        )
        row = self._row_for_workspace(self._run_report())
        self.assertEqual(row['enforcement_events_count'], 1)
        self.assertEqual(row['auto_events_count'], 0)
        self.assertEqual(row['operator_events_count'], 1)

    def test_mixed_rows_split_correctly(self):
        self._seed_event(
            'workspace_budget_freeze',
            extra_evidence={'trigger': 'autopilot_cycle'},
        )
        self._seed_event(
            'workspace_downgrade_set',
            extra_evidence={'trigger': 'autopilot_cycle'},
        )
        self._seed_event(
            'workspace_downgrade_cleared',
            actor_user_id=self.user.id,
        )
        row = self._row_for_workspace(self._run_report())
        self.assertEqual(row['enforcement_events_count'], 3)
        self.assertEqual(row['auto_events_count'], 2)
        self.assertEqual(row['operator_events_count'], 1)
        self.assertEqual(
            row['auto_events_count'] + row['operator_events_count'],
            row['enforcement_events_count'],
            msg='auto + operator must sum to enforcement_events_count',
        )

    def test_empty_window_zero_counts(self):
        # No events seeded — default row must show zeros, not missing keys
        row = self._row_for_workspace(self._run_report())
        self.assertEqual(row['enforcement_events_count'], 0)
        self.assertEqual(row['auto_events_count'], 0)
        self.assertEqual(row['operator_events_count'], 0)
        self.assertIsNone(row['last_enforcement_at'])

    def test_actor_user_id_empty_string_treated_as_auto(self):
        """Edge case: bool('') is False → row falls into auto bucket."""
        self._seed_event(
            'workspace_freeze_cleared',
            actor_user_id='',  # falsy — must not be counted as operator
        )
        row = self._row_for_workspace(self._run_report())
        self.assertEqual(row['enforcement_events_count'], 1)
        self.assertEqual(row['auto_events_count'], 1)
        self.assertEqual(row['operator_events_count'], 0)

    def test_out_of_window_row_ignored(self):
        # Event 48h ago must not show up in a 24h window
        old_row = self._seed_event(
            'workspace_budget_freeze',
            actor_user_id=self.user.id,
        )
        AutopilotAction.objects.filter(id=old_row.id).update(
            created_at=tz.now() - timedelta(hours=48),
        )
        row = self._row_for_workspace(self._run_report())
        self.assertEqual(row['enforcement_events_count'], 0)
        self.assertEqual(row['auto_events_count'], 0)
        self.assertEqual(row['operator_events_count'], 0)

    def test_response_note_mentions_split_rule(self):
        response = self._run_report()
        self.assertIn('actor_user_id', response['note'])
        self.assertIn('operator', response['note'])
        self.assertIn('auto', response['note'])
