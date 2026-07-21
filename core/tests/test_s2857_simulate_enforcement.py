"""Session 2857 A1 W2 #4 — workspace_budget_tool.simulate_enforcement.

Locks in the new PA-tool action that fires the workspace freeze +
downgrade enforcer against a synthetic daily-spend value so operators /
customer demos don't need to drop to Django shell (Rigby's calling
agent is 'PersonalAssistant' which bypasses freeze at
core/llm_enforcer.py:271).

Also locks the S2857 enforcement_report `include_simulated` filter that
keeps evidence.simulated=True rows out of the fleet report by default.
"""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone as tz

from core.models.system import SystemConfiguration
from core.models_diagnostic_pipeline import AutopilotAction
from core.models_skin_layer import ProjectWorkspace
from core.services.ops_autopilot.budget import BudgetController
from core.services.td_handlers_ops import OpsHandlersMixin


User = get_user_model()


class _OpsProxy(OpsHandlersMixin):
    """Same instantiation pattern as core/views_ops_console.py:133."""
    pass


class _BaseSimEnforceCase(TestCase):
    """Shared setup — workspace owned by test user + $10 explicit cap.

    Cap of $10 gives clean thresholds: freeze at $10, downgrade set at
    $7.00 (70%), downgrade clear at $6.00 (60%).
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='s2857sim',
            email='s2857sim@test.com',
            password='pw',
        )
        self.workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name='S2857 Sim Workspace',
        )
        self.wid = str(self.workspace.id)
        self.controller = BudgetController()
        self.controller.set_workspace_daily_cap(
            self.workspace.id, daily_cap_usd=10.0, actor_user_id=self.user.id,
        )
        # set_workspace_daily_cap writes an AutopilotAction — clear so
        # each test's assertion counts start clean.
        AutopilotAction.objects.all().delete()

    def _call(self, payload):
        proxy = _OpsProxy()
        return proxy._handle_workspace_budget(
            tool_name='workspace_budget_tool',
            payload={'action': 'simulate_enforcement', **payload},
            user_id=self.user.id,
            trace_id='s2857-test',
        )


class SimulateEnforcementDryRunTests(_BaseSimEnforceCase):
    """dry_run=True — decisions computed, no state written."""

    def test_below_soft_limit_no_op(self):
        # $5 < $7 → downgrade no_op, freeze no_op
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': 5.0,
        })
        self.assertTrue(r['dry_run'])
        self.assertEqual(r['freeze_decision'], 'no_op_below_cap')
        self.assertEqual(r['downgrade_decision'], 'no_op_below_soft_limit')
        self.assertIsNone(r['freeze_action'])
        self.assertIsNone(r['downgrade_action'])
        # No state written
        self.assertFalse(self.controller.is_workspace_frozen(self.workspace.id))
        self.assertFalse(
            self.controller.is_workspace_downgraded(self.workspace.id),
        )
        # No audit rows written for dry-run
        self.assertEqual(AutopilotAction.objects.count(), 0)

    def test_at_soft_limit_would_downgrade(self):
        # $7.50 >= $7 → downgrade would set, freeze still no_op
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': 7.5,
        })
        self.assertEqual(r['freeze_decision'], 'no_op_below_cap')
        self.assertEqual(r['downgrade_decision'], 'would_set_downgrade')

    def test_at_cap_would_freeze(self):
        # $10 >= $10 → freeze would fire; downgrade also would set
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': 10.0,
        })
        self.assertEqual(r['freeze_decision'], 'would_freeze')
        self.assertEqual(r['downgrade_decision'], 'would_set_downgrade')

    def test_thresholds_math_reported(self):
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': 3.0,
        })
        t = r['thresholds']
        self.assertEqual(t['cap_usd'], 10.0)
        self.assertAlmostEqual(t['downgrade_set_threshold_usd'], 7.0)
        self.assertAlmostEqual(t['downgrade_clear_threshold_usd'], 6.0)
        self.assertFalse(t['currently_frozen'])
        self.assertFalse(t['currently_downgraded'])

    def test_note_warns_about_live_side_effect(self):
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': 3.0,
        })
        self.assertIn('dry_run=true', r['note'])
        self.assertIn('dry_run=false', r['note'])
        self.assertIn('WARNING', r['note'])

    def test_currently_downgraded_would_clear(self):
        # Prime the downgrade flag; sim spend below clear threshold
        # should report would_clear_downgrade.
        SystemConfiguration.objects.create(
            key=f'workspace_downgrade_active:{self.workspace.id}',
            value=True,
            description='prime',
            category='performance',
        )
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': 4.0,  # < $6
        })
        self.assertEqual(r['downgrade_decision'], 'would_clear_downgrade')
        self.assertTrue(r['thresholds']['currently_downgraded'])

    def test_currently_frozen_already_at_cap(self):
        SystemConfiguration.objects.create(
            key=f'workspace_freeze_active:{self.workspace.id}',
            value=True,
            description='prime',
            category='performance',
        )
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': 12.0,
        })
        self.assertEqual(r['freeze_decision'], 'no_op_already_frozen')
        self.assertTrue(r['thresholds']['currently_frozen'])


class SimulateEnforcementLiveTests(_BaseSimEnforceCase):
    """dry_run=False — real enforcer methods invoked, real flags written."""

    def test_freeze_actually_fires_and_writes_flag(self):
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': 10.0,
            'dry_run': False,
        })
        self.assertFalse(r['dry_run'])
        self.assertIsNotNone(r['freeze_action'])
        self.assertEqual(
            r['freeze_action']['type'], 'workspace_budget_freeze',
        )
        # Real flag now written
        self.assertTrue(self.controller.is_workspace_frozen(self.workspace.id))

    def test_downgrade_actually_fires_and_writes_flag(self):
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': 7.5,
            'dry_run': False,
        })
        self.assertIsNotNone(r['downgrade_action'])
        self.assertEqual(
            r['downgrade_action']['type'], 'workspace_downgrade_set',
        )
        self.assertTrue(
            self.controller.is_workspace_downgraded(self.workspace.id),
        )

    def test_evidence_carries_simulated_flag(self):
        self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': 10.0,
            'dry_run': False,
        })
        row = AutopilotAction.objects.get(
            action_type='workspace_budget_freeze',
        )
        self.assertTrue(row.evidence.get('simulated'))
        self.assertEqual(row.evidence.get('trigger'), 'simulate_enforcement')
        self.assertEqual(
            row.evidence.get('actor_user_id'), str(self.user.id),
        )
        # Attribution — operator, not autopilot
        self.assertEqual(row.agent_name, 'workspace_budget_tool')
        self.assertEqual(row.policy, 'workspace_budget_tool')

    def test_downgrade_set_evidence_carries_simulated(self):
        self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': 7.5,
            'dry_run': False,
        })
        row = AutopilotAction.objects.get(
            action_type='workspace_downgrade_set',
        )
        self.assertTrue(row.evidence.get('simulated'))

    def test_note_warns_flags_are_live(self):
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': 10.0,
            'dry_run': False,
        })
        self.assertIn('LIVE', r['note'])
        self.assertIn('clear_freeze', r['note'])
        self.assertIn('simulated=True', r['note'])


class SimulateEnforcementAuthTests(TestCase):
    """Non-owner / unauth callers are refused; staff bypass ownership."""

    def setUp(self):
        self.owner = User.objects.create_user(
            username='s2857owner', email='o@test.com', password='pw',
        )
        self.other = User.objects.create_user(
            username='s2857other', email='x@test.com', password='pw',
        )
        self.staff = User.objects.create_user(
            username='s2857staff', email='s@test.com', password='pw',
            is_staff=True,
        )
        self.workspace = ProjectWorkspace.objects.create(
            user=self.owner, name='S2857 Auth Workspace',
        )
        self.wid = str(self.workspace.id)
        BudgetController().set_workspace_daily_cap(
            self.workspace.id, daily_cap_usd=10.0,
            actor_user_id=self.owner.id,
        )
        AutopilotAction.objects.all().delete()

    def _call(self, user_id):
        proxy = _OpsProxy()
        return proxy._handle_workspace_budget(
            tool_name='workspace_budget_tool',
            payload={
                'action': 'simulate_enforcement',
                'workspace_id': self.wid,
                'simulated_daily_spend_usd': 3.0,
            },
            user_id=user_id,
            trace_id='s2857-test',
        )

    def test_owner_allowed(self):
        r = self._call(self.owner.id)
        self.assertNotIn('error', r)
        self.assertEqual(r['freeze_decision'], 'no_op_below_cap')

    def test_staff_allowed(self):
        r = self._call(self.staff.id)
        self.assertNotIn('error', r)

    def test_non_owner_denied(self):
        r = self._call(self.other.id)
        self.assertIn('error', r)
        self.assertIn('not owner', r['error'])

    def test_unauth_denied(self):
        r = self._call(None)
        self.assertIn('error', r)
        self.assertIn('authentication required', r['error'])


class SimulateEnforcementValidationTests(_BaseSimEnforceCase):

    def test_missing_workspace_id(self):
        r = self._call({'simulated_daily_spend_usd': 5.0})
        self.assertIn('error', r)
        self.assertIn('workspace_id is required', r['error'])

    def test_missing_simulated_spend(self):
        r = self._call({'workspace_id': self.wid})
        self.assertIn('error', r)
        self.assertIn('simulated_daily_spend_usd is required', r['error'])

    def test_negative_spend_rejected(self):
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': -1.0,
        })
        self.assertIn('error', r)
        self.assertIn('≥ 0', r['error'])

    def test_non_numeric_spend_rejected(self):
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': 'lots',
        })
        self.assertIn('error', r)
        self.assertIn('numeric', r['error'])

    def test_nan_spend_rejected(self):
        # Rigby SIGN Q3 — NaN passes the `< 0` guard silently and
        # would pollute SystemConfig descriptions on dry_run=false.
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': float('nan'),
        })
        self.assertIn('error', r)
        self.assertIn('finite', r['error'])

    def test_inf_spend_rejected(self):
        r = self._call({
            'workspace_id': self.wid,
            'simulated_daily_spend_usd': float('inf'),
        })
        self.assertIn('error', r)
        self.assertIn('finite', r['error'])

    def test_workspace_without_cap_rejected(self):
        ws2 = ProjectWorkspace.objects.create(
            user=self.user, name='Uncapped',
        )
        r = self._call({
            'workspace_id': str(ws2.id),
            'simulated_daily_spend_usd': 5.0,
        })
        self.assertIn('error', r)
        self.assertIn('no explicit', r['error'])


class EnforcementReportSimulatedFilterTests(TestCase):
    """S2857 addition: enforcement_report excludes evidence.simulated=True
    rows by default; include_simulated=true opts them back in."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s2857filter', email='f@test.com', password='pw',
            is_staff=True,
        )
        self.workspace = ProjectWorkspace.objects.create(
            user=self.user, name='S2857 Filter Workspace',
        )
        self.wid = str(self.workspace.id)
        # Seed: 1 real operator freeze, 1 real auto freeze, 2 simulated
        # rows (one operator-attributed, one auto-attributed).
        AutopilotAction.objects.create(
            action_type='workspace_budget_freeze',
            agent_name='workspace_budget_tool',
            policy='workspace_budget_tool',
            dry_run=False,
            evidence={
                'workspace_id': self.wid,
                'actor_user_id': str(self.user.id),
                'trigger': 'operator_set_cap_immediate',
            },
            result={},
        )
        AutopilotAction.objects.create(
            action_type='workspace_budget_freeze',
            agent_name='BudgetController',
            policy='workspace_budget_controller',
            dry_run=False,
            evidence={
                'workspace_id': self.wid,
                'trigger': 'autopilot_cycle',
            },
            result={},
        )
        AutopilotAction.objects.create(
            action_type='workspace_downgrade_set',
            agent_name='workspace_budget_tool',
            policy='workspace_budget_tool',
            dry_run=False,
            evidence={
                'workspace_id': self.wid,
                'actor_user_id': str(self.user.id),
                'trigger': 'simulate_enforcement',
                'simulated': True,
            },
            result={},
        )
        AutopilotAction.objects.create(
            action_type='workspace_downgrade_cleared',
            agent_name='BudgetController',
            policy='workspace_budget_controller',
            dry_run=False,
            evidence={
                'workspace_id': self.wid,
                'trigger': 'simulate_enforcement',
                'simulated': True,
            },
            result={},
        )

    def _row(self, response):
        for row in response['rows']:
            if row['workspace_id'] == self.wid:
                return row
        self.fail('workspace not in rows')

    def _call(self, include_simulated=None):
        payload = {'action': 'enforcement_report', 'window': '24h'}
        if include_simulated is not None:
            payload['include_simulated'] = include_simulated
        proxy = _OpsProxy()
        return proxy._handle_workspace_budget(
            tool_name='workspace_budget_tool',
            payload=payload,
            user_id=self.user.id,
            trace_id='s2857-test',
        )

    def test_default_excludes_simulated(self):
        row = self._row(self._call())
        self.assertEqual(row['enforcement_events_count'], 2)
        self.assertEqual(row['auto_events_count'], 1)
        self.assertEqual(row['operator_events_count'], 1)

    def test_include_simulated_true_shows_all(self):
        row = self._row(self._call(include_simulated=True))
        self.assertEqual(row['enforcement_events_count'], 4)
        self.assertEqual(row['auto_events_count'], 2)
        self.assertEqual(row['operator_events_count'], 2)

    def test_note_records_which_mode(self):
        default = self._call()
        self.assertIn('excluded by default', default['note'])
        included = self._call(include_simulated=True)
        self.assertIn('INCLUDED', included['note'])
