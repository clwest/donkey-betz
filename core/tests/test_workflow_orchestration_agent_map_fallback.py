"""Session 1231 F4 — WorkflowOrchestrationAgent AGENT_MAP fallback.

Pre-fix: ``_execute_step()`` was an ``if/elif`` chain handling 9
internal step names (web_search, coleadership_agent,
image_generation_agent, create_project_from_research,
video_generation_agent, audio_generation_agent, image_selection,
image_variation_agent, content_writer_agent). The built-in workflow
templates also reference 4 names that lacked handlers:
``research_agent``, ``competitor_analysis_agent``,
``customer_research_agent``, ``strategic_synthesis``. The first three
have PascalCase equivalents in ``AGENT_MAP`` (``ResearchAgent``,
``CompetitorAnalysisAgent``, ``CustomerResearchAgent``); the fourth
does not.

Pre-fix every workflow step using those names silently failed with
``"Unknown agent in workflow: <snake_name>"``, aborting the workflow.
Surfaced by Session 1231 full-AGENT_MAP fleet smoke
(``smoke_id=9321b9a13397``).

Post-fix the ``else`` branch converts snake_case → PascalCase and
attempts an ``AgentRouter`` dispatch. Returns explicit error if the
PascalCase name isn't in AGENT_MAP (instead of the prior generic
"Unknown agent" message).

Run::

    python manage.py test core.tests.test_workflow_orchestration_agent_map_fallback -v2
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from core.services.workflow_orchestration_agent import WorkflowOrchestrationAgent


class WorkflowAgentMapFallbackTests(SimpleTestCase):

    def setUp(self):
        # WorkflowOrchestrationAgent subclasses BaseContentAgent which
        # requires `user`. _execute_step only reads `self.user` via
        # getattr() for the AGENT_MAP fallback router instantiation —
        # a Mock is sufficient (we patch AgentRouter itself).
        self.agent = WorkflowOrchestrationAgent(user=MagicMock(name='user'))

    def _step(self, agent_name, description="probe step", name="test_step"):
        return {'step': 1, 'name': name, 'agent': agent_name, 'description': description}

    # ── known AGENT_MAP fallback (research_agent → ResearchAgent) ──

    def test_research_agent_routes_to_ResearchAgent_via_AGENT_MAP(self):
        fake_router = MagicMock()
        fake_router.AGENT_MAP = {'ResearchAgent': object}
        fake_router.route.return_value = SimpleNamespace(
            success=True, message="researched market trends", data={'k': 'v'}
        )

        with patch('core.agent_router.AgentRouter', return_value=fake_router):
            result = self.agent._execute_step(
                self._step('research_agent', description="Research market trends"),
                context={},
            )

        self.assertTrue(result['success'])
        self.assertEqual(result['output'], "researched market trends")
        self.assertEqual(result['data'], {'k': 'v'})
        # AgentRouter was asked for the PascalCase form
        fake_router.route.assert_called_once()
        args, _ = fake_router.route.call_args
        self.assertEqual(args[0], 'ResearchAgent')

    def test_competitor_analysis_agent_routes_to_CompetitorAnalysisAgent(self):
        fake_router = MagicMock()
        fake_router.AGENT_MAP = {'CompetitorAnalysisAgent': object}
        fake_router.route.return_value = SimpleNamespace(
            success=True, message="analyzed competitors", data={}
        )
        with patch('core.agent_router.AgentRouter', return_value=fake_router):
            result = self.agent._execute_step(
                self._step('competitor_analysis_agent'), context={}
            )
        self.assertTrue(result['success'])
        args, _ = fake_router.route.call_args
        self.assertEqual(args[0], 'CompetitorAnalysisAgent')

    def test_customer_research_agent_routes_to_CustomerResearchAgent(self):
        fake_router = MagicMock()
        fake_router.AGENT_MAP = {'CustomerResearchAgent': object}
        fake_router.route.return_value = SimpleNamespace(
            success=True, message="built personas", data={}
        )
        with patch('core.agent_router.AgentRouter', return_value=fake_router):
            result = self.agent._execute_step(
                self._step('customer_research_agent'), context={}
            )
        self.assertTrue(result['success'])
        args, _ = fake_router.route.call_args
        self.assertEqual(args[0], 'CustomerResearchAgent')

    # ── name not in AGENT_MAP — explicit error ──

    def test_unknown_snake_name_returns_explicit_no_handler_error(self):
        """An arbitrary snake_case name with no internal handler AND
        no PascalCase entry in AGENT_MAP returns an explicit error
        naming both forms. Pre-F4 the error was the generic 'Unknown
        agent in workflow: <name>' which made the gap invisible.

        (Session 1231 F7 added a dedicated internal handler for
        ``strategic_synthesis``, so this test now uses a freshly-
        invented name that no future-friendly elif could match.)"""
        fake_router = MagicMock()
        fake_router.AGENT_MAP = {'ResearchAgent': object}

        with patch('core.agent_router.AgentRouter', return_value=fake_router):
            result = self.agent._execute_step(
                self._step('totally_made_up_agent_xyz123'), context={}
            )

        self.assertFalse(result['success'])
        self.assertIn("totally_made_up_agent_xyz123", result['error'])
        self.assertIn("TotallyMadeUpAgentXyz123", result['error'])
        self.assertIn("not in AGENT_MAP", result['error'])
        fake_router.route.assert_not_called()

    # ── dispatch exception is surfaced ──

    def test_dispatch_exception_surfaces_in_error(self):
        fake_router = MagicMock()
        fake_router.AGENT_MAP = {'ResearchAgent': object}
        fake_router.route.side_effect = RuntimeError("simulated dispatch failure")

        with patch('core.agent_router.AgentRouter', return_value=fake_router):
            result = self.agent._execute_step(
                self._step('research_agent'), context={}
            )

        self.assertFalse(result['success'])
        self.assertIn("AGENT_MAP fallback dispatch failed", result['error'])
        self.assertIn("research_agent", result['error'])
        self.assertIn("ResearchAgent", result['error'])
        self.assertIn("RuntimeError", result['error'])

    # ── internal handlers still take precedence over the fallback ──

    def test_existing_internal_handlers_still_take_precedence(self):
        """coleadership_agent / image_generation_agent / etc. must
        keep using their specialized handlers, NOT fall through to
        AGENT_MAP. Otherwise the fallback would silently change the
        execution shape for years of working workflows."""
        fake_router = MagicMock()
        fake_router.AGENT_MAP = {'ColeadershipAgent': object}  # would match

        # Patch a sentinel-return on each of the 9 internal handlers
        sentinel_returns = {}
        for handler in (
            '_execute_web_search_step',
            '_execute_coleadership_step',
            '_execute_image_generation_step',
            '_execute_create_project_step',
            '_execute_video_generation_step',
            '_execute_audio_generation_step',
            '_execute_image_selection_step',
            '_execute_image_variation_step',
            '_execute_content_writer_step',
        ):
            sentinel = {'success': True, 'output': f'<{handler}>'}
            sentinel_returns[handler] = sentinel

        # Spy on each handler
        names_to_test = [
            ('web_search', '_execute_web_search_step'),
            ('coleadership_agent', '_execute_coleadership_step'),
            ('image_generation_agent', '_execute_image_generation_step'),
            ('create_project_from_research', '_execute_create_project_step'),
            ('video_generation_agent', '_execute_video_generation_step'),
            ('audio_generation_agent', '_execute_audio_generation_step'),
            ('image_selection', '_execute_image_selection_step'),
            ('image_variation_agent', '_execute_image_variation_step'),
            ('content_writer_agent', '_execute_content_writer_step'),
        ]

        with patch('core.agent_router.AgentRouter', return_value=fake_router):
            for agent_name, handler_name in names_to_test:
                with patch.object(
                    self.agent, handler_name,
                    return_value=sentinel_returns[handler_name],
                ) as spy:
                    result = self.agent._execute_step(
                        self._step(agent_name), context={'k': 'v'},
                    )
                    spy.assert_called_once()
                    self.assertEqual(result, sentinel_returns[handler_name],
                                     msg=f"{agent_name} should use internal "
                                         f"handler, not AGENT_MAP fallback")

        # The fallback's router.route MUST NOT have been called for any of
        # the 9 names that have internal handlers.
        fake_router.route.assert_not_called()
