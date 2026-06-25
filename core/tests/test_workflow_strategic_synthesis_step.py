"""Session 1231 F7 — strategic_synthesis workflow step handler.

Pre-fix: Built-in templates `business_research` and `startup_validation`
end with a synthesis step that references the snake_case agent name
`strategic_synthesis`. There's no `StrategicSynthesis` class in
AGENT_MAP, so the F4 fallback (PR #2590) correctly returned an
explicit error — but that still aborted the workflow at step 4.

Post-fix: `_execute_step()` routes `strategic_synthesis` to an
internal `_execute_strategic_synthesis_step()` handler that:
- Reads any prior step outputs from the workflow context
  (research_summary, competitor_insights, customer_insights, etc.)
- Builds a synthesis prompt from whatever's available
- Calls gpt-5-mini via the OpenAI factory
- Stores the synthesis in context for downstream steps

Graceful empty-context behavior: when no prior outputs and no topic
are present (smoke / capability-ping case), returns success with an
explicit "No synthesis input available" note rather than aborting.

Run::

    python manage.py test core.tests.test_workflow_strategic_synthesis_step -v2
"""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase

from core.services.workflow_orchestration_agent import WorkflowOrchestrationAgent


class StrategicSynthesisStepTests(SimpleTestCase):

    def setUp(self):
        self.agent = WorkflowOrchestrationAgent(user=MagicMock(name='user'))

    # ── empty context — graceful no-op ──────────────────────────────

    def test_empty_context_returns_graceful_no_op(self):
        """Smoke / capability-ping path: no topic, no prior step
        outputs. Pre-F7 the workflow aborted with "Unknown agent in
        workflow"; post-F7 returns success with an explicit note."""
        result = self.agent._execute_step(
            {'step': 4, 'name': 'synthesize_findings',
             'agent': 'strategic_synthesis', 'description': 'Synthesize'},
            context={},
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['inputs_used'], [])
        self.assertEqual(result['summary'], 'No synthesis input available')
        self.assertIn('nothing to synthesize', result['synthesis'])

    # ── populated context — dispatches LLM call ─────────────────────

    def test_populated_context_calls_LLM_with_synthesis_prompt(self):
        fake_response = SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(content="- Insight 1\n- Insight 2\n- Insight 3"),
                finish_reason='stop',
            )],
        )
        fake_client = MagicMock()
        fake_client.chat.completions.create.return_value = fake_response

        with patch('core.services.openai_client_factory.get_openai_client',
                   return_value=fake_client):
            result = self.agent._execute_step(
                {'step': 4, 'name': 'synthesize_findings',
                 'agent': 'strategic_synthesis', 'description': 'Synthesize'},
                context={
                    'topic': 'AI agent platforms',
                    'research_summary': 'Market growing 40% YoY',
                    'competitor_insights': 'Three major players',
                    'customer_pain_points': ['cost', 'reliability'],
                },
            )

        self.assertTrue(result['success'])
        self.assertIn('Insight 1', result['synthesis'])
        self.assertEqual(
            sorted(result['inputs_used']),
            sorted(['research_summary', 'competitor_insights', 'customer_pain_points']),
        )

        # LLM call shape — gpt-5-mini + 4000-token floor
        fake_client.chat.completions.create.assert_called_once()
        kwargs = fake_client.chat.completions.create.call_args.kwargs
        self.assertEqual(kwargs['model'], 'gpt-5-mini')
        self.assertGreaterEqual(kwargs['max_completion_tokens'], 4000)

        # The prompt should include the topic + all 3 populated context keys
        prompt = kwargs['messages'][0]['content']
        self.assertIn('AI agent platforms', prompt)
        self.assertIn('research_summary', prompt)
        self.assertIn('Market growing 40% YoY', prompt)
        self.assertIn('competitor_insights', prompt)
        self.assertIn('customer_pain_points', prompt)

    # ── dict/list context values get serialized for the prompt ──────

    def test_dict_and_list_context_values_get_serialized(self):
        fake_response = SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(content="- A\n- B"),
                finish_reason='stop',
            )],
        )
        fake_client = MagicMock()
        fake_client.chat.completions.create.return_value = fake_response

        with patch('core.services.openai_client_factory.get_openai_client',
                   return_value=fake_client):
            result = self.agent._execute_step(
                {'step': 4, 'name': 'syn', 'agent': 'strategic_synthesis',
                 'description': ''},
                context={
                    'topic': 'X',
                    'customer_personas': [{'name': 'Alice'}, {'name': 'Bob'}],
                    'research_results': {'count': 5, 'summary': 'foo'},
                },
            )

        self.assertTrue(result['success'])
        prompt = fake_client.chat.completions.create.call_args.kwargs['messages'][0]['content']
        # Dict + list serialized to JSON in the prompt
        self.assertIn('Alice', prompt)
        self.assertIn('Bob', prompt)
        self.assertIn('"count": 5', prompt)

    # ── LLM exception surfaces in error envelope ────────────────────

    def test_LLM_exception_surfaces_in_error(self):
        fake_client = MagicMock()
        fake_client.chat.completions.create.side_effect = RuntimeError(
            "simulated openai outage"
        )
        with patch('core.services.openai_client_factory.get_openai_client',
                   return_value=fake_client):
            result = self.agent._execute_step(
                {'step': 4, 'name': 'syn', 'agent': 'strategic_synthesis',
                 'description': ''},
                context={'topic': 'X', 'research_summary': 'data'},
            )

        self.assertFalse(result['success'])
        self.assertIn('strategic_synthesis LLM call failed', result['error'])
        self.assertIn('RuntimeError', result['error'])
        self.assertIn('simulated openai outage', result['error'])

    # ── empty LLM response surfaces explicit error ──────────────────

    def test_empty_LLM_response_surfaces_explicit_error(self):
        """gpt-5* with insufficient max_completion_tokens can silently
        return empty content (finish_reason='length'). Handler must
        surface that as an explicit error, not return success with
        empty synthesis."""
        fake_response = SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(content=''),
                finish_reason='length',
            )],
        )
        fake_client = MagicMock()
        fake_client.chat.completions.create.return_value = fake_response

        with patch('core.services.openai_client_factory.get_openai_client',
                   return_value=fake_client):
            result = self.agent._execute_step(
                {'step': 4, 'name': 'syn', 'agent': 'strategic_synthesis',
                 'description': ''},
                context={'topic': 'X', 'research_summary': 'data'},
            )

        self.assertFalse(result['success'])
        self.assertIn('returned empty content', result['error'])
        self.assertIn('finish_reason=length', result['error'])

    # ── synthesis is persisted into context for downstream steps ────

    def test_synthesis_is_persisted_into_context(self):
        fake_response = SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(content="- Synthesized insight"),
                finish_reason='stop',
            )],
        )
        fake_client = MagicMock()
        fake_client.chat.completions.create.return_value = fake_response

        ctx = {'topic': 'X', 'research_summary': 'data'}
        with patch('core.services.openai_client_factory.get_openai_client',
                   return_value=fake_client):
            self.agent._execute_step(
                {'step': 4, 'name': 'syn', 'agent': 'strategic_synthesis',
                 'description': ''},
                context=ctx,
            )
        self.assertIn('strategic_synthesis', ctx)
        self.assertIn('Synthesized insight', ctx['strategic_synthesis'])

    # ── source-level guard: regression sentinel ─────────────────────

    def test_source_level_guard_handler_is_wired(self):
        """Lock the wiring so a future revert is caught at test-time
        rather than via downstream workflow failures."""
        import re
        from pathlib import Path
        src = Path('core/services/workflow_orchestration_agent.py').read_text()

        # The elif branch must exist for 'strategic_synthesis' BEFORE
        # the F4 AGENT_MAP fallback else.
        self.assertIsNotNone(
            re.search(
                r"elif agent_name == 'strategic_synthesis':\s*\n\s*return self\._execute_strategic_synthesis_step\(context\)",
                src,
            ),
            msg="_execute_step must route 'strategic_synthesis' to the "
                "internal handler. Reverting reintroduces the F4 AGENT_MAP "
                "fallback's explicit 'not in AGENT_MAP' abort.",
        )
        # And the handler itself must exist.
        self.assertIn(
            'def _execute_strategic_synthesis_step',
            src,
            msg="_execute_strategic_synthesis_step handler removed.",
        )
