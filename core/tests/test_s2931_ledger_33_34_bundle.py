"""Session 2931 — Rigby Tool Gap Ledger #33 + #34 bundle.

Two fixes shipped in a single PR:

- **#34** — `on_agent_execution_completed` post_save receiver now short-circuits
  when `settings.TESTING` is True. Without this, every test that creates a
  completed/failed AgentExecution row fans out into
  `learning_orchestrator._generate_optimizations` → downstream services that
  can hit OpenAI. `test_agent_runs_list_endpoint.py` alone was measured at
  ~77 hidden calls per suite run.

- **#33** — `AgentExecution` added to `orm_inspect_tool`'s `_MODEL_POLICIES`
  allowlist alongside the pre-existing `Agent` entry. S2930 recon forced 3×
  Django shell fallback to trace agent runs; Rigby can now list/count/filter
  executions directly via the tool surface.
"""
from __future__ import annotations

from decimal import Decimal
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models_unified_system import Agent, AgentExecution
from core.services.tool_dispatcher import get_tool_dispatcher

User = get_user_model()


def _run(payload):
    dispatcher = get_tool_dispatcher()
    handler = dispatcher._tool_handlers['orm_inspect_tool']
    return handler(
        tool_name='orm_inspect_tool',
        payload=payload,
        user_id=None,
        trace_id='test-s2931-trace',
    )


# ─────────────────────────────────────────────────────────────────────────────
# #34 — TESTING gate on the learning-bridge post_save receiver
# ─────────────────────────────────────────────────────────────────────────────


class LearningBridgeTestingGateTests(TestCase):
    """Fix #34: post_save receiver must skip when settings.TESTING is True."""

    def setUp(self):
        self.agent = Agent.objects.create(name='TestAgentLedger34', agent_type='general')
        self.user = User.objects.create(username='s2931-user', email='s2931@example.com')

    def test_receiver_skips_when_testing_flag_true(self):
        # settings.TESTING defaults to True under manage.py test / pytest —
        # explicitly assert it here so the test is self-documenting.
        from django.conf import settings
        self.assertTrue(getattr(settings, 'TESTING', False),
                        'settings.TESTING must be True under the test runner')

        # If the receiver were still firing, process_execution would be
        # called during .save(). Patch it and assert it is NOT invoked.
        target = 'core.learning_bridges.agent_execution_bridge.agent_execution_learning.process_execution'
        with mock.patch(target) as mocked:
            AgentExecution.objects.create(
                agent=self.agent,
                user=self.user,
                task='ledger-34 gate check',
                status='completed',
                execution_time_ms=100,
                tokens_used=42,
                cost=Decimal('0.01'),
            )
            mocked.assert_not_called()

    def test_receiver_still_fires_when_testing_flag_false(self):
        """If TESTING is flipped off, the receiver should behave as before."""
        target = 'core.learning_bridges.agent_execution_bridge.agent_execution_learning.process_execution'
        with mock.patch(target) as mocked, self.settings(TESTING=False):
            AgentExecution.objects.create(
                agent=self.agent,
                user=self.user,
                task='ledger-34 gate check (non-test)',
                status='completed',
                execution_time_ms=100,
                tokens_used=42,
                cost=Decimal('0.01'),
            )
            mocked.assert_called_once()

    def test_receiver_stays_skipped_for_pending_status_even_when_testing_false(self):
        """The pre-existing status gate still applies when TESTING is False."""
        target = 'core.learning_bridges.agent_execution_bridge.agent_execution_learning.process_execution'
        with mock.patch(target) as mocked, self.settings(TESTING=False):
            AgentExecution.objects.create(
                agent=self.agent,
                user=self.user,
                task='status=pending should not fire',
                status='pending',
            )
            mocked.assert_not_called()


# ─────────────────────────────────────────────────────────────────────────────
# #33 — AgentExecution surfaced via orm_inspect_tool
# ─────────────────────────────────────────────────────────────────────────────


class OrmInspectAgentExecutionTests(TestCase):
    """Fix #33: AgentExecution reachable via orm_inspect_tool without shell."""

    def setUp(self):
        self.agent = Agent.objects.create(name='TestAgentLedger33', agent_type='general')
        self.user = User.objects.create(username='s2931-orm-user', email='s2931orm@example.com')
        for i in range(3):
            AgentExecution.objects.create(
                agent=self.agent,
                user=self.user,
                task=f'ledger-33 exec {i}',
                status='completed',
                execution_time_ms=100 + i,
                tokens_used=10 + i,
                cost=Decimal('0.0001'),
            )
        AgentExecution.objects.create(
            agent=self.agent,
            user=self.user,
            task='ledger-33 failed exec',
            status='failed',
            error_message='synthetic failure for group-by test',
        )

    def test_list_models_includes_agent_execution(self):
        result = _run({'action': 'list_models'})
        self.assertTrue(result['ok'])
        names = {m['name'] for m in result['models']}
        self.assertIn('AgentExecution', names)
        # Pre-existing sibling still present.
        self.assertIn('Agent', names)

    def test_describe_model_agent_execution(self):
        result = _run({'action': 'describe_model', 'model': 'AgentExecution'})
        self.assertTrue(result['ok'], msg=result)
        self.assertEqual(result['model'], 'AgentExecution')
        self.assertFalse(result['sensitive_model'])
        self.assertIn('task', result['expensive_text_fields'])
        self.assertIn('error_message', result['expensive_text_fields'])
        field_names = {f['name'] for f in result['fields']}
        # Sanity: canonical fields are surfaced.
        for expected in ('id', 'status', 'task', 'tokens_used', 'cost', 'agent'):
            self.assertIn(expected, field_names)

    def test_filter_agent_execution_by_status(self):
        result = _run({
            'action': 'filter',
            'model': 'AgentExecution',
            'filter_kwargs': {'status': 'completed'},
            'limit': 10,
        })
        self.assertTrue(result['ok'], msg=result)
        self.assertEqual(result['total_matching'], 3)
        self.assertEqual(result['returned'], 3)

    def test_count_by_agent_execution_status(self):
        result = _run({
            'action': 'count_by',
            'model': 'AgentExecution',
            'field': 'status',
        })
        self.assertTrue(result['ok'], msg=result)
        by_status = {g['value']: g['count'] for g in result['groups']}
        self.assertEqual(by_status.get('completed'), 3)
        self.assertEqual(by_status.get('failed'), 1)

    def test_contains_rejected_on_expensive_task_field(self):
        # Guardrail parity: `task` is registered as expensive_text; contains
        # lookups on it must be rejected the same way as on other allowlisted
        # models.
        result = _run({
            'action': 'filter',
            'model': 'AgentExecution',
            'filter_kwargs': {'task__contains': 'ledger-33'},
        })
        self.assertFalse(result['ok'])
        self.assertIn('expensive text field', result['error'])
