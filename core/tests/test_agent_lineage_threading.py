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
