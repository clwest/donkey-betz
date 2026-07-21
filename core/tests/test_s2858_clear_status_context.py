"""Session 2858 PR#1 — clear_freeze / clear_downgrade status_context.

Locks the inline post-clear spend + threshold + re_flag_likely context
that clear_freeze and clear_downgrade now return so operators don't
have to re-call get_status.

Semantic contract validated:
- re_flag_likely computed against the EXPLICIT cap only (enforcer
  ignores default fallback).
- When cap_source != 'explicit', re_flag_likely is False + reason
  explains that enforcement won't re-fire until an explicit cap is set.
- freeze re-fires at daily_total >= explicit_cap.
- downgrade re-fires at daily_total >= 0.7 * explicit_cap.
"""

from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models.system import SystemConfiguration
from core.models_diagnostic_pipeline import AutopilotAction
from core.models_skin_layer import ProjectWorkspace
from core.services.ops_autopilot.budget import BudgetController
from core.services.td_handlers_ops import OpsHandlersMixin


User = get_user_model()


class _OpsProxy(OpsHandlersMixin):
    pass


class _BaseClearStatusCase(TestCase):
    """Workspace with $10 explicit cap. Thresholds: freeze $10, downgrade $7."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s2858clear',
            email='s2858clear@test.com',
            password='pw',
        )
        self.workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name='S2858 Clear Workspace',
        )
        self.wid = str(self.workspace.id)
        self.controller = BudgetController()
        self.controller.set_workspace_daily_cap(
            self.workspace.id, daily_cap_usd=10.0, actor_user_id=self.user.id,
        )
        AutopilotAction.objects.all().delete()

    def _call(self, action, spend_amount):
        proxy = _OpsProxy()
        # Patch compute_workspace_spend so we don't need to seed LLMCallLog
        # rows — the status_context read path is what we're locking.
        with patch.object(
            BudgetController,
            'compute_workspace_spend',
            return_value={
                'daily_total': spend_amount,
                'daily_calls': 1,
                'hourly_total': spend_amount,
                'hourly_calls': 1,
            },
        ):
            return proxy._handle_workspace_budget(
                tool_name='workspace_budget_tool',
                payload={'action': action, 'workspace_id': self.wid},
                user_id=self.user.id,
                trace_id='s2858-test',
            )


class ClearFreezeStatusContextTests(_BaseClearStatusCase):
    """clear_freeze now returns status_context tied to freeze threshold."""

    def test_shape_when_below_cap(self):
        # $5 < $10 → freeze would NOT re-fire
        r = self._call('clear_freeze', 5.0)
        self.assertIn('status_context', r)
        ctx = r['status_context']
        self.assertEqual(ctx['daily_total'], 5.0)
        self.assertEqual(ctx['effective_cap'], 10.0)
        self.assertEqual(ctx['cap_source'], 'explicit')
        self.assertEqual(ctx['spend_pct_of_cap'], 50)
        self.assertFalse(ctx['re_flag_likely'])
        self.assertIn('will not re-fire', ctx['re_flag_reason'])
        self.assertEqual(ctx['refire_threshold'], 10.0)
        self.assertEqual(ctx['refire_threshold_pct_of_cap'], 100)
        self.assertIn('daily spend >= explicit cap', ctx['enforcement_note'])

    def test_re_flag_likely_when_at_cap(self):
        # $10 >= $10 → freeze WILL re-fire immediately
        r = self._call('clear_freeze', 10.0)
        ctx = r['status_context']
        self.assertTrue(ctx['re_flag_likely'])
        self.assertEqual(ctx['spend_pct_of_cap'], 100)
        self.assertIn('will re-fire', ctx['re_flag_reason'])

    def test_re_flag_likely_when_above_cap(self):
        # $12 > $10 → freeze WILL re-fire
        r = self._call('clear_freeze', 12.0)
        ctx = r['status_context']
        self.assertTrue(ctx['re_flag_likely'])
        self.assertEqual(ctx['spend_pct_of_cap'], 120)

    def test_note_mentions_state_flip_semantic(self):
        # Guardrail per Rigby SIGN Q5 #4 — response can't imply that
        # clearing "fixed" anything; must be flagged as state flip.
        # Freeze the workspace first so cleared=True (the note only
        # applies to the real-clear branch, not the no-op branch).
        SystemConfiguration.objects.create(
            key=f'workspace_freeze_active:{self.workspace.id}',
            value=True,
            category='performance',
        )
        r = self._call('clear_freeze', 5.0)
        self.assertTrue(r['cleared'])
        self.assertIn('state flip only', r['note'])


class ClearDowngradeStatusContextTests(_BaseClearStatusCase):
    """clear_downgrade returns status_context tied to 70% soft threshold."""

    def test_shape_when_below_soft_limit(self):
        # $5 < $7 → downgrade would NOT re-fire
        r = self._call('clear_downgrade', 5.0)
        ctx = r['status_context']
        self.assertEqual(ctx['refire_threshold'], 7.0)
        self.assertEqual(ctx['refire_threshold_pct_of_cap'], 70)
        self.assertFalse(ctx['re_flag_likely'])
        self.assertIn('will not re-fire', ctx['re_flag_reason'])
        self.assertIn('70% of explicit cap', ctx['enforcement_note'])

    def test_re_flag_likely_at_soft_limit(self):
        # $7 >= $7 → downgrade WILL re-fire
        r = self._call('clear_downgrade', 7.0)
        ctx = r['status_context']
        self.assertTrue(ctx['re_flag_likely'])
        self.assertIn('will re-fire', ctx['re_flag_reason'])

    def test_re_flag_likely_above_soft_limit(self):
        # $8 > $7 but < $10 → downgrade re-fires, freeze wouldn't
        r = self._call('clear_downgrade', 8.0)
        ctx = r['status_context']
        self.assertTrue(ctx['re_flag_likely'])
        self.assertEqual(ctx['spend_pct_of_cap'], 80)


class DefaultCapSemanticsTests(TestCase):
    """When workspace has only a default cap (cap_source != 'explicit'),
    enforcement will NOT re-fire — re_flag_likely must be False regardless
    of spend, and reason must explain the enforcement gap.

    This locks Rigby SIGN Q5 concern (1): operator-facing effective_cap
    vs enforcer-only explicit_cap.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='s2858dflt',
            email='s2858dflt@test.com',
            password='pw',
        )
        # Workspace with NO explicit cap
        self.workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name='S2858 Default-only Workspace',
        )
        self.wid = str(self.workspace.id)
        # Set a global default cap so effective_cap resolves
        controller = BudgetController()
        # Staff needed for set_default_cap — flip is_staff
        self.user.is_staff = True
        self.user.save()
        controller.set_workspace_default_cap(
            cap=10.0, actor_user_id=self.user.id,
        )
        AutopilotAction.objects.all().delete()

    def _call(self, action, spend_amount):
        proxy = _OpsProxy()
        with patch.object(
            BudgetController,
            'compute_workspace_spend',
            return_value={
                'daily_total': spend_amount,
                'daily_calls': 1,
                'hourly_total': spend_amount,
                'hourly_calls': 1,
            },
        ):
            return proxy._handle_workspace_budget(
                tool_name='workspace_budget_tool',
                payload={'action': action, 'workspace_id': self.wid},
                user_id=self.user.id,
                trace_id='s2858-test',
            )

    def test_default_cap_re_flag_false_when_above_effective(self):
        # $12 > effective_cap ($10 default) but no EXPLICIT cap → enforcer
        # won't re-fire. re_flag_likely MUST be False.
        r = self._call('clear_freeze', 12.0)
        ctx = r['status_context']
        self.assertEqual(ctx['cap_source'], 'default')
        self.assertFalse(ctx['re_flag_likely'])
        self.assertIn('no explicit cap', ctx['re_flag_reason'])
        self.assertIn('backfill_defaults', ctx['re_flag_reason'])
        # Threshold is None because there IS no enforcement threshold
        self.assertIsNone(ctx['refire_threshold'])

    def test_default_cap_downgrade_also_gated(self):
        # Same story for downgrade — no explicit cap = no enforcement
        r = self._call('clear_downgrade', 8.0)
        ctx = r['status_context']
        self.assertEqual(ctx['cap_source'], 'default')
        self.assertFalse(ctx['re_flag_likely'])
        self.assertIsNone(ctx['refire_threshold'])


class UnsetCapSemanticsTests(TestCase):
    """When workspace has no cap at all (cap_source == 'unset'), same
    story — effective_cap is None, re_flag_likely False.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='s2858unset',
            email='s2858unset@test.com',
            password='pw',
        )
        self.workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name='S2858 Unset Workspace',
        )
        self.wid = str(self.workspace.id)

    def _call(self, action, spend_amount):
        proxy = _OpsProxy()
        with patch.object(
            BudgetController,
            'compute_workspace_spend',
            return_value={
                'daily_total': spend_amount,
                'daily_calls': 0,
                'hourly_total': 0.0,
                'hourly_calls': 0,
            },
        ):
            return proxy._handle_workspace_budget(
                tool_name='workspace_budget_tool',
                payload={'action': action, 'workspace_id': self.wid},
                user_id=self.user.id,
                trace_id='s2858-test',
            )

    def test_unset_cap_spend_pct_none(self):
        r = self._call('clear_freeze', 5.0)
        ctx = r['status_context']
        self.assertEqual(ctx['cap_source'], 'unset')
        self.assertIsNone(ctx['effective_cap'])
        self.assertIsNone(ctx['spend_pct_of_cap'])
        self.assertFalse(ctx['re_flag_likely'])


class NoopStatusContextTests(_BaseClearStatusCase):
    """status_context is present even when cleared=False (no-op case)
    so operators get the same visibility either way.
    """

    def test_clear_freeze_noop_still_has_status_context(self):
        # Nothing frozen → cleared=False, but context still returned
        r = self._call('clear_freeze', 5.0)
        self.assertFalse(r['cleared'])
        self.assertIn('status_context', r)
        self.assertEqual(r['status_context']['effective_cap'], 10.0)

    def test_clear_downgrade_noop_still_has_status_context(self):
        r = self._call('clear_downgrade', 5.0)
        self.assertFalse(r['cleared'])
        self.assertIn('status_context', r)
        self.assertEqual(r['status_context']['refire_threshold_pct_of_cap'], 70)
