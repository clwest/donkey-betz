"""S3039 S9: LLMCallLog fallback + auto-select telemetry regression tests.

Prior state (S2856 shipped `was_downgraded` at the enforcer write site
via PR #3328). The S3037 Reliability Audit surfaced that in a 30d /
39,971-call sample, all three telemetry flags — `was_downgraded`,
`was_fallback`, `was_auto_selected` — were 0/0/0 populated. The
enforcer path (100% of prod openai traffic) never wired
`was_fallback` or `was_auto_selected`; the router path hardcoded
`was_auto_selected=False`.

S3039 S9 wires the plumbing (kwargs threaded end-to-end through both
write sites) so producers can populate the flags. This test locks in:

- **Enforcer write site** (`_save_cost_tracking`): both defaults and
  explicit-True land on `LLMCallLog` for all three flags.
- **Router write site** (`_log_call`): both defaults and explicit-True
  land for all three flags, including the previously hardcoded
  `was_auto_selected`.
- Rigby SIGN ask #4: the "checkbox telemetry" risk is mitigated by
  asserting the explicit-True path actually persists, not just the
  default path.

Producer threading (agent_model_router.auto_route call sites →
was_auto_selected=True at the enforcer call site) is explicitly
deferred to a follow-up — see Rigby's zoom-out fold in the PR body.
"""
from __future__ import annotations

from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase

from core.llm_enforcer import LLMEnforcer
from core.models_llm_routing import LLMCallLog


class EnforcerWriteSiteFlagsTests(TestCase):
    """`_save_cost_tracking` accepts all 3 flags and persists them to LLMCallLog."""

    def _seed(self, **overrides):
        enforcer = LLMEnforcer()
        defaults = dict(
            provider='openai',
            model='gpt-5.2',
            agent_name='S9EnforcerAgent',
            task_type='general',
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
            cost=0.001,
        )
        defaults.update(overrides)
        enforcer._save_cost_tracking(**defaults)
        return LLMCallLog.objects.filter(
            agent_name=defaults['agent_name'],
        ).latest('created_at')

    def test_defaults_all_three_flags_false(self):
        row = self._seed()
        self.assertFalse(row.was_downgraded)
        self.assertFalse(row.was_fallback)
        self.assertFalse(row.was_auto_selected)
        self.assertEqual(row.pre_downgrade_model_id, '')

    def test_explicit_was_fallback_persists_true(self):
        row = self._seed(was_fallback=True)
        self.assertTrue(row.was_fallback)
        self.assertFalse(row.was_downgraded)
        self.assertFalse(row.was_auto_selected)

    def test_explicit_was_auto_selected_persists_true(self):
        row = self._seed(was_auto_selected=True)
        self.assertTrue(row.was_auto_selected)
        self.assertFalse(row.was_downgraded)
        self.assertFalse(row.was_fallback)

    def test_all_three_flags_true_together(self):
        row = self._seed(
            was_downgraded=True,
            pre_downgrade_model_id='gpt-5.2',
            was_fallback=True,
            was_auto_selected=True,
            model='gpt-5-mini',
        )
        self.assertTrue(row.was_downgraded)
        self.assertEqual(row.pre_downgrade_model_id, 'gpt-5.2')
        self.assertTrue(row.was_fallback)
        self.assertTrue(row.was_auto_selected)


class EnforceRealAIThreadsFlagsToWriteSiteTests(TestCase):
    """The top-level `enforce_real_ai` entrypoint accepts the new kwargs
    and threads them into `_save_cost_tracking`. Producers only need to
    touch this one call site to record the events."""

    def test_enforce_real_ai_threads_was_fallback_and_auto_selected(self):
        enforcer = LLMEnforcer()

        fake_openai_result = {
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

        with patch.object(enforcer, '_call_openai', return_value=fake_openai_result):
            enforcer.enforce_real_ai(
                prompt='hi',
                agent_name='S9EnforceRealAgent',
                was_fallback=True,
                was_auto_selected=True,
            )

        row = LLMCallLog.objects.filter(
            agent_name='S9EnforceRealAgent',
        ).latest('created_at')
        self.assertTrue(row.was_fallback)
        self.assertTrue(row.was_auto_selected)

    def test_enforce_real_ai_defaults_leave_flags_false(self):
        """No-kwarg callers must not break — defaults preserve prior behavior."""
        enforcer = LLMEnforcer()

        fake_openai_result = {
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

        with patch.object(enforcer, '_call_openai', return_value=fake_openai_result):
            enforcer.enforce_real_ai(
                prompt='hi',
                agent_name='S9DefaultsAgent',
            )

        row = LLMCallLog.objects.filter(
            agent_name='S9DefaultsAgent',
        ).latest('created_at')
        self.assertFalse(row.was_fallback)
        self.assertFalse(row.was_auto_selected)


class RouterWriteSiteFlagsTests(TestCase):
    """`agent_llm_router._log_call` accepts all 3 flags. Pre-fix,
    `was_auto_selected` was hardcoded False and `was_downgraded` +
    `pre_downgrade_model_id` were not accepted at all — a router-path
    call that got budget-downgraded lost the signal."""

    def _make_router(self):
        from core.services.agent_llm_router import AgentLLMRouter
        return AgentLLMRouter.__new__(AgentLLMRouter)

    def _make_response(self, success=True):
        from core.services.llm_provider_registry import LLMResponse
        return LLMResponse(
            success=success,
            content='ok',
            provider='anthropic',
            model='claude-3-haiku',
            tokens_input=10,
            tokens_output=5,
            tokens_total=15,
            latency_ms=100,
            cost=0.001,
            error=None,
        )

    def test_router_defaults_all_three_flags_false(self):
        router = self._make_router()
        router._log_call(
            agent_name='S9RouterDefaults',
            provider='anthropic',
            model_id='claude-3-haiku',
            response=self._make_response(),
            task_type='general',
            user=None,
            was_fallback=False,
        )
        row = LLMCallLog.objects.filter(agent_name='S9RouterDefaults').latest('created_at')
        self.assertFalse(row.was_downgraded)
        self.assertFalse(row.was_fallback)
        self.assertFalse(row.was_auto_selected)
        self.assertEqual(row.pre_downgrade_model_id, '')

    def test_router_explicit_was_auto_selected_persists_true(self):
        """Pre-S9, was_auto_selected was hardcoded False in _log_call
        regardless of caller intent. Post-S9, the param persists."""
        router = self._make_router()
        router._log_call(
            agent_name='S9RouterAutoSelect',
            provider='anthropic',
            model_id='claude-3-haiku',
            response=self._make_response(),
            task_type='general',
            user=None,
            was_fallback=False,
            was_auto_selected=True,
        )
        row = LLMCallLog.objects.filter(agent_name='S9RouterAutoSelect').latest('created_at')
        self.assertTrue(row.was_auto_selected)

    def test_router_explicit_was_downgraded_persists_true(self):
        """Pre-S9, _log_call didn't accept was_downgraded at all — router
        callers had no way to record a budget-downgrade event."""
        router = self._make_router()
        router._log_call(
            agent_name='S9RouterDowngrade',
            provider='openai',
            model_id='gpt-5-mini',
            response=self._make_response(),
            task_type='general',
            user=None,
            was_fallback=True,
            was_downgraded=True,
            pre_downgrade_model_id='gpt-5.2',
            was_auto_selected=False,
        )
        row = LLMCallLog.objects.filter(agent_name='S9RouterDowngrade').latest('created_at')
        self.assertTrue(row.was_fallback)
        self.assertTrue(row.was_downgraded)
        self.assertEqual(row.pre_downgrade_model_id, 'gpt-5.2')
        self.assertFalse(row.was_auto_selected)
