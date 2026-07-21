"""Session 2856 — LLMCallLog.was_downgraded + enforcer stale-flag reset.

Locks in the S2856 correctness leg for `enforcement_report
--include_downgrade_savings`:
  - LLMCallLog.was_downgraded + pre_downgrade_model_id default to False/''
  - `enforce_real_ai` resets `_budget_downgrade_model` to None at the top
    of every call (fixes singleton stale-flag leak)
  - `_call_openai` result dict carries was_downgraded + pre_downgrade_model_id
  - `_save_cost_tracking` writes both fields into LLMCallLog
  - `enforcement_report` filters on was_downgraded=True (not model_id), so
    natively-mini agents (PersonalAssistant, orchestration coordinators)
    do not inflate the savings estimate
"""

from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone as tz

from core.llm_enforcer import LLMEnforcer
from core.models_llm_routing import LLMCallLog
from core.models_skin_layer import ProjectWorkspace
from core.services.td_handlers_ops import OpsHandlersMixin


User = get_user_model()


class LLMCallLogFieldTests(TestCase):
    """Field defaults + explicit-value round-trip on the new columns."""

    def test_defaults_are_false_and_empty(self):
        row = LLMCallLog.objects.create(
            agent_name='SomeAgent',
            provider='openai',
            model_id='gpt-5.2',
        )
        self.assertFalse(row.was_downgraded)
        self.assertEqual(row.pre_downgrade_model_id, '')

    def test_explicit_values_persist(self):
        row = LLMCallLog.objects.create(
            agent_name='SomeAgent',
            provider='openai',
            model_id='gpt-5-mini',
            was_downgraded=True,
            pre_downgrade_model_id='gpt-5.2',
        )
        row.refresh_from_db()
        self.assertTrue(row.was_downgraded)
        self.assertEqual(row.pre_downgrade_model_id, 'gpt-5.2')


class EnforcerStaleFlagResetTests(TestCase):
    """The singleton's `_budget_downgrade_model` must be re-derived per call.

    Pre-S2856: once any call set the flag, every subsequent openai call in
    the process silently routed to the downgrade model until Django
    restarted, because `enforce_real_ai` only SET the attr and never
    reset it. Test asserts the reset now happens at the top of the method.
    """

    def test_reset_at_top_of_enforce_real_ai_when_no_flag_active(self):
        enforcer = LLMEnforcer()
        enforcer._budget_downgrade_model = 'gpt-5-mini'

        with patch.object(enforcer, '_call_openai') as mock_call, \
                patch.object(enforcer, '_save_cost_tracking'):
            mock_call.return_value = {
                'content': 'ok',
                'tokens': 10,
                'cost': 0.0,
                'effective_model': 'gpt-5.2',
                'truncated': False,
                'input_tokens': 5,
                'output_tokens': 5,
                'reasoning_tokens': 0,
                'cached_input_tokens': 0,
                'cost_estimator_version': 'test',
                'was_downgraded': False,
                'pre_downgrade_model_id': '',
            }
            enforcer.enforce_real_ai(prompt='hi', agent_name='Test')

        self.assertIsNone(
            enforcer._budget_downgrade_model,
            msg='enforce_real_ai must reset _budget_downgrade_model per call',
        )


class SaveCostTrackingWritesDowngradeFieldsTests(TestCase):
    """`_save_cost_tracking` threads was_downgraded + pre_downgrade_model_id
    into LLMCallLog.objects.create."""

    def test_forced_downgrade_row(self):
        enforcer = LLMEnforcer()
        enforcer._save_cost_tracking(
            provider='openai',
            model='gpt-5-mini',
            agent_name='SomeAgent',
            task_type='content',
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            cost=0.001,
            was_downgraded=True,
            pre_downgrade_model_id='gpt-5.2',
        )
        row = LLMCallLog.objects.filter(agent_name='SomeAgent').latest('created_at')
        self.assertEqual(row.model_id, 'gpt-5-mini')
        self.assertTrue(row.was_downgraded)
        self.assertEqual(row.pre_downgrade_model_id, 'gpt-5.2')

    def test_natively_mini_row_stays_false(self):
        enforcer = LLMEnforcer()
        enforcer._save_cost_tracking(
            provider='openai',
            model='gpt-5-mini',
            agent_name='PersonalAssistantAgent',
            task_type='pa_chat',
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            cost=0.0005,
            # was_downgraded + pre_downgrade_model_id omitted — defaults apply
        )
        row = LLMCallLog.objects.filter(
            agent_name='PersonalAssistantAgent',
        ).latest('created_at')
        self.assertEqual(row.model_id, 'gpt-5-mini')
        self.assertFalse(row.was_downgraded)
        self.assertEqual(row.pre_downgrade_model_id, '')

    def test_claude_path_row_stays_false(self):
        """Claude has no downgrade cascade — the row must land with the
        default False/'' values even when written from the Claude code path."""
        enforcer = LLMEnforcer()
        enforcer._save_cost_tracking(
            provider='anthropic',
            model='claude-3-haiku',
            agent_name='ClaudeCaller',
            task_type='content',
            input_tokens=50,
            output_tokens=20,
            total_tokens=70,
            cost=0.0001,
            # No was_downgraded/pre_downgrade_model_id kwargs — enforcer
            # caller thread defaults them for Claude path.
        )
        row = LLMCallLog.objects.filter(agent_name='ClaudeCaller').latest('created_at')
        self.assertEqual(row.provider, 'anthropic')
        self.assertFalse(row.was_downgraded)
        self.assertEqual(row.pre_downgrade_model_id, '')

    def test_failure_path_row_still_persists_fields(self):
        """success=False must not skip the write nor corrupt the new fields."""
        enforcer = LLMEnforcer()
        enforcer._save_cost_tracking(
            provider='openai',
            model='gpt-5-mini',
            agent_name='FailingAgent',
            task_type='content',
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            cost=0.0,
            success=False,
            error_message='429 rate_limit',
            was_downgraded=True,
            pre_downgrade_model_id='gpt-5.2',
        )
        row = LLMCallLog.objects.filter(agent_name='FailingAgent').latest('created_at')
        self.assertFalse(row.success)
        self.assertTrue(row.was_downgraded)
        self.assertEqual(row.pre_downgrade_model_id, 'gpt-5.2')


class _OpsProxy(OpsHandlersMixin):
    """Same instantiation pattern as core/views_ops_console.py:133."""
    pass


class EnforcementReportFilterTests(TestCase):
    """`enforcement_report --include_downgrade_savings` must count only
    was_downgraded=True rows, not model_id='gpt-5-mini' rows."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='s2856test',
            email='s2856@test.com',
            password='pw',
            is_staff=True,
        )
        self.workspace = ProjectWorkspace.objects.create(
            user=self.user,
            name='S2856 Test Workspace',
        )

    def _seed_call(self, model_id, was_downgraded, pre_model='', cost='0.001'):
        return LLMCallLog.objects.create(
            agent_name='TestAgent',
            provider='openai',
            model_id=model_id,
            was_downgraded=was_downgraded,
            pre_downgrade_model_id=pre_model,
            cost=Decimal(cost),
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            user=self.user,
            workspace=self.workspace,
        )

    def test_only_forced_downgrades_counted(self):
        # Row A: natively-mini agent (PersonalAssistantAgent shape) — must NOT count
        self._seed_call('gpt-5-mini', was_downgraded=False, cost='0.001')
        # Row B: forced downgrade — must count
        self._seed_call(
            'gpt-5-mini', was_downgraded=True, pre_model='gpt-5.2', cost='0.002',
        )
        # Row C: non-downgraded gpt-5.2 — must NOT count
        self._seed_call('gpt-5.2', was_downgraded=False, cost='0.05')

        proxy = _OpsProxy()
        result = proxy._handle_workspace_budget(
            tool_name='workspace_budget_tool',
            payload={
                'action': 'enforcement_report',
                'window': '24h',
                'include_downgrade_savings': True,
            },
            user_id=self.user.id,
            trace_id='s2856-test',
        )

        totals = result['downgrade_model_totals']
        self.assertEqual(
            totals['calls'], 1,
            msg=(
                'Only the was_downgraded=True row should be counted. '
                f'Got totals={totals}'
            ),
        )
        self.assertAlmostEqual(totals['actual_cost_usd'], 0.002, places=6)
