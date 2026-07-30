"""
S3048 — AgentExecution lineage threading through delegation call sites.
=======================================================================

Baseline pre-S3048 (2026-07-30): 0/2917 AgentExecution rows had
``parent_execution_id`` set. Router already threaded lineage correctly
in ``_create_execution_record`` (line 2872-2900), but the four
production child-dispatch call sites in ``core/agents/**/*.py`` built
fresh context dicts and dropped the parent's ``execution_id``.

Fixed sites (verified by Rigby T1 SIGN 2026-07-30):

- ``core/agents/base_agent.py:_delegate_to_specialist`` (line 948)
- ``core/agents/workflow_agent.py:delegate_to_agent`` (line 461)
- ``core/agents/ai_series_workflow_agent.py:_route_with_timeout`` (line 421)
- ``core/agents/executive/meeting_coordinator_agent.py:_get_agent_perspective`` (line 471)

Each site now reads ``self._execution_context.get('execution_id')`` and
threads it via ``context.setdefault('execution_id', ...)`` (or explicit
assignment in the MeetingCoordinator case where a fresh context dict
is constructed inline). ``setdefault`` preserves caller-provided
overrides. The router then reads ``context.get('execution_id')`` in
``_create_execution_record`` (agent_router.py line 2874) as the parent
lineage signal.

Coverage strategy:

- **Source-guard tests** for BaseAgent, WorkflowAgent, and
  MeetingCoordinator sites: BaseAgent is abstract (can't be
  instantiated cleanly) and MeetingCoordinator instantiates a fresh
  ``AgentRouter`` inside a closure. Source inspection is the cheapest,
  most stable coverage — a refactor that removes the fix triggers a
  loud, targeted test failure.
- **Behavior test** for AISeriesWorkflowAgent (concrete class, easy to
  instantiate, ``_route_with_timeout`` is a clean helper): mocks the
  router and asserts the child-dispatch context carries the parent's
  ``execution_id``.

Run::

    python manage.py test core.tests.test_agent_lineage_threading -v2
"""

import uuid
from pathlib import Path
from unittest import mock

from django.test import TestCase


class BaseAgentSourceGuardTests(TestCase):
    """Guard the threading block at ``base_agent.py:936-960`` against
    accidental removal by a future refactor."""

    def test_base_agent_threads_execution_id_in_delegation(self):
        src = Path('core/agents/base_agent.py').read_text()
        self.assertIn(
            "delegation_ctx.setdefault('execution_id'",
            src,
            'S3048 threading block removed from base_agent.py',
        )
        # Also verify the _execution_context read that feeds the setdefault.
        self.assertIn(
            "getattr(self, '_execution_context', None) or {}",
            src,
            'S3048 _execution_context read removed from base_agent.py',
        )


class WorkflowAgentSourceGuardTests(TestCase):
    """Guard the threading block at ``workflow_agent.py:451-455``."""

    def test_workflow_agent_threads_execution_id_in_subtask(self):
        src = Path('core/agents/workflow_agent.py').read_text()
        self.assertIn(
            "subtask_context.setdefault('execution_id'",
            src,
            'S3048 threading block removed from workflow_agent.py',
        )


class MeetingCoordinatorSourceGuardTests(TestCase):
    """Guard the threading block at
    ``meeting_coordinator_agent.py:469-478``. Uses source inspection
    because the coordinator constructs a fresh ``AgentRouter`` inside a
    closure — hard to mock cleanly at the module boundary."""

    def test_meeting_coordinator_threads_execution_id(self):
        src = Path(
            'core/agents/executive/meeting_coordinator_agent.py'
        ).read_text()
        self.assertIn(
            "_child_context['execution_id'] = _parent_exec_id",
            src,
            'S3048 threading block removed from meeting_coordinator_agent.py',
        )


class RouterEndToEndLineageTests(TestCase):
    """S3048 addendum coverage: verifies the router's
    ``_create_execution_record`` actually READS ``execution_id`` from
    the raw caller context (not the ``context_summary`` blob).

    Pre-addendum, ``agent_router.py:2849`` rebound
    ``context = context_summary or {}`` before the lineage read at
    line 2872-2882, silently dropping every ``execution_id`` threaded
    by the delegation-site fix. D1 empirical verify (2026-07-30):
    child row created with ``parent=cba6595c root=cba6595c`` matching
    the expected parent id — end-to-end wire confirmed."""

    def setUp(self):
        from django.contrib.auth import get_user_model
        from core.models_unified_system import Agent, AgentExecution

        User = get_user_model()
        self.user = User.objects.create_user(
            username='router-lineage-e2e',
            email='router-e2e@example.com',
            password='x',
        )
        # Parent execution (simulates the caller's own AgentExecution row)
        self.parent_agent, _ = Agent.objects.get_or_create(
            name='S3048RouterE2EParent', defaults={'agent_type': 'routable'},
        )
        self.parent_row = AgentExecution.objects.create(
            agent=self.parent_agent,
            user=self.user,
            task='S3048 router e2e verify',
            status='in_progress',
        )
        # Stub child agent for fast dispatch
        Agent.objects.get_or_create(
            name='S3048RouterE2EChild', defaults={'agent_type': 'routable'},
        )

    def test_router_threads_execution_id_from_raw_context(self):
        from core.agent_router import AgentRouter
        from core.agents.base_agent import BaseAgent, AgentResult
        from core.models_unified_system import AgentExecution

        class _StubChild(BaseAgent):
            def execute(self, task, context=None, **kw):
                return AgentResult(
                    success=True,
                    message='stub',
                    data={},
                    agent_name='S3048RouterE2EChild',
                )

        router = AgentRouter(user=self.user)
        router.AGENT_MAP['S3048RouterE2EChild'] = _StubChild

        result = router.route(
            'S3048RouterE2EChild',
            'S3048 router-side threading e2e verify',
            context={'execution_id': str(self.parent_row.id)},
        )
        self.assertTrue(result.success)

        # The child row must have parent_execution_id = parent.id and
        # root_execution_id resolved (falls back to parent_id when
        # parent has no recorded root yet).
        children = AgentExecution.objects.filter(
            parent_execution_id=self.parent_row.id,
        )
        self.assertEqual(
            children.count(), 1,
            'router must create exactly one child with parent_execution_id set',
        )
        child = children.first()
        self.assertEqual(str(child.parent_execution_id), str(self.parent_row.id))
        self.assertEqual(str(child.root_execution_id), str(self.parent_row.id))

    def test_router_uses_parent_execution_id_kwarg_when_provided(self):
        """Router's ``parent_execution_id`` kwarg still wins over
        context inheritance — back-compat safeguard."""
        from core.agent_router import AgentRouter
        from core.agents.base_agent import BaseAgent, AgentResult
        from core.models_unified_system import AgentExecution

        class _StubChild(BaseAgent):
            def execute(self, task, context=None, **kw):
                return AgentResult(
                    success=True, message='stub', data={},
                    agent_name='S3048RouterE2EChild',
                )

        router = AgentRouter(user=self.user)
        router.AGENT_MAP['S3048RouterE2EChild'] = _StubChild
        # Direct-invoke the private method with parent_execution_id kwarg
        rec = router._create_execution_record(
            agent_name='S3048RouterE2EChild',
            task='direct kwarg verify',
            parent_execution_id=str(self.parent_row.id),
            context={},
        )
        self.assertIsNotNone(rec)
        rec.refresh_from_db()
        self.assertEqual(str(rec.parent_execution_id), str(self.parent_row.id))

    def test_router_addendum_none_context_guard_in_source(self):
        """Post-addendum: raw context can be None (kwarg default);
        lineage resolution must not crash. Source-guard the None-safe
        rebind that protects lineage lookup from crashing."""
        src = Path('core/agent_router.py').read_text()
        self.assertIn(
            "_raw_ctx = context if isinstance(context, dict) else {}",
            src,
            'S3048 addendum None-context guard removed from agent_router.py',
        )


class AISeriesWorkflowAgentRoutingLineageTests(TestCase):
    """Behavior test — AISeriesWorkflowAgent._route_with_timeout threads
    execution_id from ``self._execution_context`` into the context dict
    passed to the router. Confirms the D5 refinement Rigby requested."""

    def setUp(self):
        self.parent_exec_id = str(uuid.uuid4())

    def _make_agent(self, execution_context=None):
        """Instantiate AISeriesWorkflowAgent with a mocked router."""
        from core.agents.ai_series_workflow_agent import AISeriesWorkflowAgent

        agent = AISeriesWorkflowAgent()
        if execution_context is not None:
            agent._execution_context = execution_context

        fake_router = mock.MagicMock()
        agent._router = fake_router
        return agent, fake_router

    def test_route_with_timeout_threads_execution_id_when_present(self):
        agent, fake_router = self._make_agent(
            execution_context={'execution_id': self.parent_exec_id}
        )

        captured = {}

        def _capture(agent_name, task, context):
            captured['context'] = context
            r = mock.MagicMock()
            r.success = True
            return r

        fake_router.route.side_effect = _capture

        agent._route_with_timeout(
            agent_name='ChildAgent',
            task='child work',
            context={'existing': 'value'},
        )

        self.assertEqual(
            captured['context'].get('execution_id'),
            self.parent_exec_id,
            'execution_id must be threaded into the child dispatch context',
        )
        self.assertEqual(
            captured['context'].get('existing'),
            'value',
            'threading must not clobber caller-provided context keys',
        )

    def test_route_with_timeout_no_thread_when_execution_context_missing(self):
        agent, fake_router = self._make_agent(execution_context=None)

        captured = {}

        def _capture(agent_name, task, context):
            captured['context'] = context
            r = mock.MagicMock()
            r.success = True
            return r

        fake_router.route.side_effect = _capture

        agent._route_with_timeout(
            agent_name='ChildAgent',
            task='root work',
            context={},
        )

        self.assertNotIn(
            'execution_id',
            captured['context'],
            'root dispatch (no _execution_context) must not add execution_id',
        )

    def test_route_with_timeout_setdefault_preserves_override(self):
        """If caller pre-set execution_id in context, threading must not
        clobber it — ``setdefault`` semantics."""
        agent, fake_router = self._make_agent(
            execution_context={'execution_id': self.parent_exec_id}
        )
        caller_override = str(uuid.uuid4())

        captured = {}

        def _capture(agent_name, task, context):
            captured['context'] = context
            r = mock.MagicMock()
            r.success = True
            return r

        fake_router.route.side_effect = _capture

        agent._route_with_timeout(
            agent_name='ChildAgent',
            task='override test',
            context={'execution_id': caller_override},
        )

        self.assertEqual(
            captured['context'].get('execution_id'),
            caller_override,
            'caller-provided execution_id must survive setdefault threading',
        )
