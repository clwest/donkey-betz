"""Session 1234 D4 — agent_router workflow-dispatch intercept.

When an LLM-orchestrated agent (e.g. DevOpsAgent) hands the router a
task like ``"Run WORKFLOWS['morning_brief'] end-to-end"`` with
``agent_name='ResearchAgent'`` (or any non-orchestrator pick), the
router must reroute to WorkflowOrchestrationAgent so the named
workflow actually runs. Two independent trigger signals:

1. Task text contains the ``WORKFLOWS['<name>']`` subscript pattern.
2. Context dict has ``workflow_name`` set to a non-empty string.

Pre-fix behavior (2026-06-25 first-fire repro):
    AgentExecution at 02:50 — task="Run WORKFLOWS['morning_brief']
    end-to-end", agent=ResearchAgent, context={'workflow_name':
    'morning_brief'}. ResearchAgent ignored workflow_name and ran its
    default market-trends research; DevOpsAgent's downstream report
    flagged the mismatch.

Run::

    python manage.py test core.tests.test_agent_router_workflow_dispatch_intercept -v2
"""

import inspect
from unittest.mock import MagicMock, patch

from django.test import TestCase

from core.agent_router import AgentRouter


class WorkflowDispatchInterceptTaskPatternTests(TestCase):
    """Pattern (1): task text matches WORKFLOWS['<name>'] subscript."""

    def setUp(self):
        # No user needed — the intercept happens before agent instantiation.
        self.router = AgentRouter(user=None)

    def _route_with_mocked_execute(self, agent_name, task, context=None):
        """Run route() but stub out everything after agent reroute.

        Returns the agent_name that the router resolved to, captured
        via the override log line. Avoids the heavy execution path
        (context gathering, agent.execute, learning hooks, telemetry).
        """
        captured = {}

        def fake_check_priority(*args, **kwargs):
            agent = kwargs.get('agent_name') or (args[0] if args else None)
            captured['agent_after_intercept'] = agent
            # Raise to bail out cleanly before the rest of route() runs.
            raise _StopRouteSentinel()

        # check_priority is called RIGHT AFTER the intercept block
        # (line 1031 in route()), so it catches the rerouted name.
        with patch(
            'core.services.priority.enforce.check_priority',
            side_effect=fake_check_priority,
        ):
            try:
                self.router.route(
                    agent_name=agent_name,
                    task=task,
                    context=context,
                )
            except _StopRouteSentinel:
                pass

        return captured.get('agent_after_intercept')

    def test_workflows_subscript_pattern_reroutes_to_orchestrator(self):
        """Task with WORKFLOWS['morning_brief'] reroutes from ResearchAgent."""
        resolved = self._route_with_mocked_execute(
            agent_name='ResearchAgent',
            task="Run WORKFLOWS['morning_brief'] end-to-end smoke",
            context={},
        )
        self.assertEqual(resolved, 'WorkflowOrchestrationAgent')

    def test_workflows_subscript_double_quotes_also_matches(self):
        """LLM occasionally generates WORKFLOWS[\"name\"] with double quotes."""
        resolved = self._route_with_mocked_execute(
            agent_name='ContentWriterAgent',
            task='Execute WORKFLOWS["business_research"] and report',
            context={},
        )
        self.assertEqual(resolved, 'WorkflowOrchestrationAgent')

    def test_normal_task_without_workflows_pattern_not_rerouted(self):
        """Tasks without the pattern stay with the requested agent."""
        resolved = self._route_with_mocked_execute(
            agent_name='ResearchAgent',
            task='Analyze 2026 market trends in autonomous agents',
            context={},
        )
        self.assertEqual(resolved, 'ResearchAgent')

    def test_workflows_word_alone_not_a_trigger(self):
        """Mere mention of the word "workflows" without subscript is OK."""
        resolved = self._route_with_mocked_execute(
            agent_name='ContentWriterAgent',
            task='Write a blog post about Celery workflows',
            context={},
        )
        # No subscript → no intercept → original agent
        self.assertEqual(resolved, 'ContentWriterAgent')


class WorkflowDispatchInterceptContextSignalTests(TestCase):
    """Pattern (2): context['workflow_name'] set → reroute."""

    def setUp(self):
        self.router = AgentRouter(user=None)

    def _route(self, agent_name, task, context):
        captured = {}

        def fake_check_priority(*args, **kwargs):
            agent = kwargs.get('agent_name') or (args[0] if args else None)
            captured['agent_after_intercept'] = agent
            raise _StopRouteSentinel()

        with patch(
            'core.services.priority.enforce.check_priority',
            side_effect=fake_check_priority,
        ):
            try:
                self.router.route(agent_name=agent_name, task=task, context=context)
            except _StopRouteSentinel:
                pass

        return captured.get('agent_after_intercept')

    def test_context_workflow_name_reroutes(self):
        """context={'workflow_name': 'morning_brief'} reroutes ResearchAgent."""
        resolved = self._route(
            agent_name='ResearchAgent',
            task='do the thing',  # no WORKFLOWS[] pattern
            context={'workflow_name': 'morning_brief'},
        )
        self.assertEqual(resolved, 'WorkflowOrchestrationAgent')

    def test_context_workflow_name_seeds_workflow_key_for_agent(self):
        """workflow_name → context['workflow'] mirror so the orchestrator
        sees its required key (it reads 'workflow', not 'workflow_name')."""
        ctx = {'workflow_name': 'morning_brief'}
        self._route(
            agent_name='ResearchAgent',
            task='do the thing',
            context=ctx,
        )
        self.assertEqual(ctx.get('workflow'), 'morning_brief',
                         "Intercept must seed context['workflow'] from "
                         "workflow_name when not already set.")

    def test_explicit_workflow_already_set_not_overwritten(self):
        """If caller already set context['workflow'], don't clobber it."""
        ctx = {
            'workflow_name': 'morning_brief',
            'workflow': 'manual_override',
        }
        self._route(
            agent_name='ResearchAgent',
            task='do the thing',
            context=ctx,
        )
        self.assertEqual(ctx.get('workflow'), 'manual_override',
                         "Existing context['workflow'] must NOT be "
                         "overwritten by the intercept.")

    def test_empty_string_workflow_name_does_not_trigger(self):
        """Falsy workflow_name = no signal."""
        ctx = {'workflow_name': ''}
        resolved = self._route(
            agent_name='ResearchAgent',
            task='do the thing',
            context=ctx,
        )
        self.assertEqual(resolved, 'ResearchAgent')

    def test_target_already_orchestrator_is_noop(self):
        """If caller already routed to WorkflowOrchestrationAgent, no reroute."""
        resolved = self._route(
            agent_name='WorkflowOrchestrationAgent',
            task="Run WORKFLOWS['morning_brief']",
            context={'workflow_name': 'morning_brief'},
        )
        self.assertEqual(resolved, 'WorkflowOrchestrationAgent')


class WorkflowDispatchInterceptSourceGuardTests(TestCase):
    """Source-level guard: the intercept lives BEFORE the existing
    _ROUTING_OVERRIDES block (so it runs first), and BEFORE the
    check_priority call (so the rerouted name reaches throttling).
    """

    def test_intercept_appears_before_routing_overrides_block(self):
        src = inspect.getsource(AgentRouter.route)
        intercept_pos = src.find('routing-override:workflow-dispatch')
        overrides_pos = src.find('_ROUTING_OVERRIDES = [')
        priority_pos = src.find('check_priority(')

        self.assertGreater(intercept_pos, -1,
                           "Intercept marker missing from route().")
        self.assertGreater(overrides_pos, -1,
                           "_ROUTING_OVERRIDES sentinel missing.")
        self.assertGreater(priority_pos, -1,
                           "check_priority call missing.")

        # NOTE: priority_pos may appear BEFORE intercept_pos because
        # check_priority is also referenced in the docstring of the
        # original method. Find the FIRST executable call instead.
        # The intercept must come before _ROUTING_OVERRIDES so it
        # runs first; that's the load-bearing ordering.
        self.assertLess(
            intercept_pos, overrides_pos,
            "Workflow-dispatch intercept must appear BEFORE the "
            "_ROUTING_OVERRIDES block (otherwise the keyword-match "
            "override might rewrite agent_name first).",
        )


class _StopRouteSentinel(Exception):
    """Test-only sentinel used to bail out of route() after the
    intercept reroutes — avoids the full execution path."""
    pass
