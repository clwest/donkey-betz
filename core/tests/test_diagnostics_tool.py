"""Session 1202 §A.2 PR-1 — diagnostics_tool regression tests.

Covers the four simple actions shipped in the §A.2 PR-1 split:

- ``advisor_invocations`` — per-advisor N-day invocation count
- ``provider_calls`` — per-LLM-provider call rollup
- ``beat_schedule_health`` — PeriodicTask sorted by last_run_at
- ``workspace_metrics`` — per-ProjectWorkspace activity + counts

The 3 medium-complex actions (``schema_handler_diff``,
``learning_bridge_writes``, ``discord_health``) ship in PR-2 and have
placeholder error responses; ``test_pr2_actions_return_placeholder``
locks the placeholder contract.

TransactionTestCase rather than TestCase because ToolDispatcher routes
sync handlers through a thread-pool executor (memory rule from
PR #2442). Test-transaction-wrapped fixtures aren't visible across
connections.

Run::

    USE_PGBOUNCER=0 .venv/bin/python manage.py test \\
        core.tests.test_diagnostics_tool -v2 --noinput
"""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.utils import timezone

from core.models_skin_layer import ProjectWorkspace
from core.models_unified_system import Advisor, Agent, AgentExecution
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


class DiagnosticsToolTestBase(TransactionTestCase):
    """Shared fixtures: one user + small advisor/agent/workspace setup."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()
        cls.trace_id = 'session-1202-a2-pr1'

    def setUp(self):
        suffix = uuid.uuid4().hex[:8]
        self.user = User.objects.create_user(
            username=f'diag-{suffix}',
            email=f'diag-{suffix}@example.com',
            password='x',
        )
        self.user_id = self.user.id

        # Two advisors — one we'll invoke, one stays dead
        self.advisor_busy = Advisor.objects.create(
            name=f'BusyAdvisor-{suffix}',
            title='Test Busy Advisor',
            expertise='Coverage',
            category='test',
            is_active=True,
        )
        self.advisor_dead = Advisor.objects.create(
            name=f'DeadAdvisor-{suffix}',
            title='Test Dead Advisor',
            expertise='Silence',
            category='test',
            is_active=True,
        )

        # Two workspaces — one active, one inactive
        self.ws_active = ProjectWorkspace.objects.create(
            user=self.user,
            name=f'Active WS {suffix}',
            root_path=f'/tmp/diag-active-{suffix}',
            is_active=True,
            allow_autonomous_writes=True,
        )
        self.ws_inactive = ProjectWorkspace.objects.create(
            user=self.user,
            name=f'Inactive WS {suffix}',
            root_path=f'/tmp/diag-inactive-{suffix}',
            is_active=False,
            allow_autonomous_writes=False,
        )

    def _call(self, payload: dict) -> dict:
        tool_result = self.dispatcher.execute_sync('diagnostics_tool', payload, self.user_id)
        self.assertTrue(
            tool_result.ok,
            f"diagnostics_tool failed: {tool_result.error_message}",
        )
        result = tool_result.result
        self.assertIsInstance(result, dict)
        return result


class TestAdvisorInvocations(DiagnosticsToolTestBase):

    def setUp(self):
        super().setUp()
        # Build an Agent row that matches the busy advisor's name, then
        # log 3 executions for it in the window.
        suffix = self.advisor_busy.name
        self.busy_agent = Agent.objects.create(
            name=suffix, agent_type='test', description='diagnostics test fixture',
            specialization='diagnostics',
        )
        for _ in range(3):
            AgentExecution.objects.create(
                agent=self.busy_agent,
                status='completed',
                input_data={'test': True},
            )

    def test_busy_advisor_counted_dead_advisor_zero(self):
        result = self._call({'action': 'advisor_invocations', 'window': '7d'})

        self.assertEqual(result['action'], 'advisor_invocations')
        self.assertEqual(result.get('gateway'), 'diagnostics_tool')
        self.assertEqual(result.get('window_days'), 7)

        # Find our two advisors in the response
        by_name = {row['name']: row for row in result['advisors']}
        self.assertIn(self.advisor_busy.name, by_name)
        self.assertIn(self.advisor_dead.name, by_name)
        self.assertEqual(by_name[self.advisor_busy.name]['invocations_in_window'], 3)
        self.assertEqual(by_name[self.advisor_dead.name]['invocations_in_window'], 0)

        # Sorted busy-first
        busy_idx = next(i for i, r in enumerate(result['advisors']) if r['name'] == self.advisor_busy.name)
        dead_idx = next(i for i, r in enumerate(result['advisors']) if r['name'] == self.advisor_dead.name)
        self.assertLess(busy_idx, dead_idx)

    def test_window_filters_old_invocations(self):
        # Move all executions 14 days into the past — outside the 7d
        # window but inside the 30d window. Avoids the boundary case
        # where data set at "now - 90d" can drift past a "now - 90d"
        # threshold computed microseconds later.
        AgentExecution.objects.filter(agent=self.busy_agent).update(
            created_at=timezone.now() - timedelta(days=14),
        )
        result_7 = self._call({'action': 'advisor_invocations', 'window': '7d'})
        by_name_7 = {row['name']: row for row in result_7['advisors']}
        self.assertEqual(by_name_7[self.advisor_busy.name]['invocations_in_window'], 0)

        result_30 = self._call({'action': 'advisor_invocations', 'window': '30d'})
        by_name_30 = {row['name']: row for row in result_30['advisors']}
        self.assertEqual(by_name_30[self.advisor_busy.name]['invocations_in_window'], 3)

    def test_unknown_window_falls_back_to_default(self):
        result = self._call({'action': 'advisor_invocations', 'window': 'nope'})
        self.assertEqual(result.get('window_days'), 7)


class TestProviderCalls(DiagnosticsToolTestBase):

    def setUp(self):
        super().setUp()
        from core.models_llm_routing import LLMCallLog

        # 5 anthropic, 3 openai, 2 anthropic failures
        for _ in range(5):
            LLMCallLog.objects.create(
                agent_name='TestAgent', provider='anthropic', model_id='claude-opus-4-7',
                total_tokens=100, cost=0.001, success=True,
            )
        for _ in range(3):
            LLMCallLog.objects.create(
                agent_name='TestAgent', provider='openai', model_id='gpt-5-mini',
                total_tokens=80, cost=0.0005, success=True,
            )
        for _ in range(2):
            LLMCallLog.objects.create(
                agent_name='TestAgent', provider='anthropic', model_id='claude-opus-4-7',
                total_tokens=10, cost=0.0, success=False,
            )

    def test_per_provider_rollup(self):
        result = self._call({'action': 'provider_calls', 'window': '7d'})

        self.assertEqual(result['action'], 'provider_calls')
        by_provider = {row['provider']: row for row in result['providers']}

        anth = by_provider.get('anthropic')
        self.assertIsNotNone(anth, 'anthropic should be in providers')
        self.assertEqual(anth['total_calls'], 7)
        self.assertEqual(anth['successful_calls'], 5)
        self.assertEqual(anth['failure_calls'], 2)
        self.assertAlmostEqual(anth['success_rate_pct'], round(100 * 5 / 7, 1))

        oai = by_provider.get('openai')
        self.assertIsNotNone(oai, 'openai should be in providers')
        self.assertEqual(oai['total_calls'], 3)
        self.assertEqual(oai['successful_calls'], 3)
        self.assertEqual(oai['success_rate_pct'], 100.0)

    def test_zero_providers_returns_empty(self):
        # Older-than-window data → no rows
        from core.models_llm_routing import LLMCallLog
        LLMCallLog.objects.all().update(created_at=timezone.now() - timedelta(days=400))

        result = self._call({'action': 'provider_calls', 'window': '7d'})
        self.assertEqual(result.get('total_providers_called'), 0)
        self.assertEqual(result.get('providers'), [])


class TestBeatScheduleHealth(DiagnosticsToolTestBase):

    def test_returns_periodic_task_rollup(self):
        result = self._call({'action': 'beat_schedule_health', 'limit': 5})

        self.assertEqual(result['action'], 'beat_schedule_health')
        self.assertIn('total_count', result)
        self.assertIn('enabled_count', result)
        self.assertIn('disabled_count', result)
        self.assertIn('zero_run_count', result)
        self.assertIn('zero_run_enabled_count', result)
        self.assertEqual(result.get('limit'), 5)
        self.assertIsInstance(result.get('tasks'), list)
        self.assertLessEqual(len(result['tasks']), 5)
        # Counts are self-consistent
        self.assertEqual(
            result['total_count'],
            result['enabled_count'] + result['disabled_count'],
        )

    def test_pagination_offset(self):
        result_page1 = self._call({'action': 'beat_schedule_health', 'limit': 3, 'offset': 0})
        result_page2 = self._call({'action': 'beat_schedule_health', 'limit': 3, 'offset': 3})

        if result_page1['total_count'] > 3:
            ids_page1 = {t['id'] for t in result_page1['tasks']}
            ids_page2 = {t['id'] for t in result_page2['tasks']}
            self.assertFalse(ids_page1 & ids_page2, 'pages should not overlap')

    def test_include_disabled_false_filters(self):
        all_result = self._call({'action': 'beat_schedule_health', 'include_disabled': True, 'limit': 1})
        enabled_only = self._call({'action': 'beat_schedule_health', 'include_disabled': False, 'limit': 1})
        self.assertEqual(enabled_only['disabled_count'], 0)
        self.assertGreaterEqual(all_result['total_count'], enabled_only['total_count'])


class TestWorkspaceMetrics(DiagnosticsToolTestBase):

    def test_fixture_workspaces_show_up(self):
        result = self._call({'action': 'workspace_metrics', 'limit': 200})

        self.assertEqual(result['action'], 'workspace_metrics')
        ids = {ws['id'] for ws in result['workspaces']}
        self.assertIn(str(self.ws_active.id), ids)
        self.assertIn(str(self.ws_inactive.id), ids)

        by_id = {ws['id']: ws for ws in result['workspaces']}
        self.assertTrue(by_id[str(self.ws_active.id)]['is_active'])
        self.assertTrue(by_id[str(self.ws_active.id)]['allow_autonomous_writes'])
        self.assertFalse(by_id[str(self.ws_inactive.id)]['is_active'])
        self.assertFalse(by_id[str(self.ws_inactive.id)]['allow_autonomous_writes'])

    def test_include_inactive_false_filters(self):
        result_all = self._call({'action': 'workspace_metrics', 'include_inactive': True, 'limit': 200})
        result_active = self._call({'action': 'workspace_metrics', 'include_inactive': False, 'limit': 200})

        active_ids = {ws['id'] for ws in result_active['workspaces']}
        self.assertIn(str(self.ws_active.id), active_ids)
        self.assertNotIn(str(self.ws_inactive.id), active_ids)
        self.assertGreaterEqual(result_all['total_count'], result_active['total_count'])

    def test_rollup_counts_are_consistent(self):
        result = self._call({'action': 'workspace_metrics', 'limit': 200})
        # active_count <= total_count
        self.assertLessEqual(result['active_count'], result['total_count'])
        # autonomous_count <= total_count
        self.assertLessEqual(result['autonomous_count'], result['total_count'])


class TestActionRouting(DiagnosticsToolTestBase):

    def test_unknown_action_lists_valid_options(self):
        tool_result = self.dispatcher.execute_sync(
            'diagnostics_tool',
            {'action': 'fictional_action'},
            self.user_id,
        )
        # Unknown action returns a structured error inside the result
        # (not a dispatcher-level failure).
        self.assertTrue(tool_result.ok)
        result = tool_result.result
        self.assertIn('error', result)
        self.assertIn('advisor_invocations', result['error'])

    def test_pr2_actions_return_placeholder(self):
        for action in ('schema_handler_diff', 'learning_bridge_writes', 'discord_health'):
            result = self._call({'action': action})
            self.assertEqual(result['action'], action)
            self.assertIn('error', result)
            self.assertEqual(result.get('pending_pr'), 'session-1202-diagnostics-tool-pr2')
