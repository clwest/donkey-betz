"""Regression tests for ``_tool_to_agent_name`` at
``core/services/td_handlers_agents.py:83``.

The map translates PA tool names (e.g. ``workflow_orchestration_agent``)
into AgentRouter class names (e.g. ``WorkflowOrchestrationAgent``). A
misalignment here is silent: the wrong agent runs, receipt-verify still
passes, and the completion-verify signal reports success against the
unintended target.

Two guarantees enforced:

1. **Every RHS class exists in AGENT_MAP.** A rename or removal in
   ``core/agent_router.AGENT_MAP`` without a corresponding update here
   would otherwise ship silently.
2. **``workflow_orchestration_agent`` routes to
   ``WorkflowOrchestrationAgent``**, not to ``WorkflowAgent``. Guards
   the S2927 PR-A fix (pre-fix the map pointed at the delegate
   coordinator instead of the template-based orchestrator).

Run::

    python manage.py test core.tests.test_tool_to_agent_name_mapping -v2
"""

from django.test import SimpleTestCase

from core.agent_router import AgentRouter
from core.services.td_handlers_agents import AgentHandlersMixin


class ToolToAgentNameMappingTests(SimpleTestCase):

    def setUp(self):
        # _tool_to_agent_name is a pure method on the mixin; instantiate
        # via a bare shell with the mixin so we can call it directly.
        self.mixin = type('Shell', (AgentHandlersMixin,), {})()

    # ── S2927 PR-A guard ──

    def test_workflow_orchestration_agent_routes_to_orchestration_class(self):
        """Pre-S2927 the tool mapped to `WorkflowAgent` (delegate). Fixed
        to `WorkflowOrchestrationAgent` (template-based orchestrator)."""
        self.assertEqual(
            self.mixin._tool_to_agent_name('workflow_orchestration_agent'),
            'WorkflowOrchestrationAgent',
        )

    def test_workflow_agent_and_orchestration_agent_are_distinct_in_AGENT_MAP(self):
        """Guards the semantic distinction. If someone consolidates the
        two classes in AGENT_MAP, the mapping fix loses meaning."""
        self.assertIn('WorkflowAgent', AgentRouter.AGENT_MAP)
        self.assertIn('WorkflowOrchestrationAgent', AgentRouter.AGENT_MAP)
        self.assertIsNot(
            AgentRouter.AGENT_MAP['WorkflowAgent'],
            AgentRouter.AGENT_MAP['WorkflowOrchestrationAgent'],
        )

    # ── Structural map integrity ──

    def test_every_mapped_class_exists_in_AGENT_MAP(self):
        """Every explicit RHS class in the mapping table must be a
        registered AgentRouter class. Prevents silent breakage when an
        agent is renamed or removed."""
        # Introspect the mappings dict from the mixin method.
        import re
        import inspect
        src = inspect.getsource(self.mixin._tool_to_agent_name)
        mappings = dict(re.findall(r"'([a-z_]+)':\s*'([A-Za-z0-9]+)'", src))
        self.assertGreater(len(mappings), 30, 'Expected sizeable mapping table.')

        registered = set(AgentRouter.AGENT_MAP.keys())
        unregistered = {
            tool: cls for tool, cls in mappings.items()
            if cls not in registered
        }
        self.assertFalse(
            unregistered,
            f'These tool→class mappings reference classes missing from '
            f'AgentRouter.AGENT_MAP: {unregistered}',
        )
