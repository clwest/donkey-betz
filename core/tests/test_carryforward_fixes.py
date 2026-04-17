"""
Carryforward fix tests — Session 1094 task #4.
================================================

Three small fixes from the Session 1092/1093 carryforward backlog:

1. `run_agent` PA tool schema now exposes a top-level `content` parameter
   for agents that score/critique/edit a content blob (VoiceCriticAgent,
   EditorAgent). Mirrors the #1974 `workspace_id` pattern.

2. `BaseAgent._save_to_deliverable` now guards against `create_deliverable`
   returning None (the Session 1088 quality gate rejects some content).
   Before: AttributeError on `deliverable.id`. After: returns None gracefully
   with an info log.

3. `.env.example` DATABASE_URL line no longer uses `username:password`
   placeholder pattern that false-triggers pre-commit secret-scanning hooks.
   Uppercase tokens (DB_USER / DB_PASSWORD / DB_HOST) are unambiguously stubs.

Run:
    python manage.py test core.tests.test_carryforward_fixes -v2
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase


# =============================================================================
# Fix 1: run_agent schema + handler promote content/workspace_id
# =============================================================================

class RunAgentSchemaContentParamTests(SimpleTestCase):
    """The `run_agent` tool schema must expose `content` as a top-level param."""

    def _run_agent_schema(self) -> dict:
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        for schema in PA_TOOL_SCHEMAS:
            # Handle both flat {name, parameters} and nested {function: {name, parameters}}
            name = schema.get('name') or (schema.get('function') or {}).get('name')
            if name == 'run_agent':
                return schema if 'parameters' in schema else schema['function']
        self.fail('run_agent schema not found in PA_TOOL_SCHEMAS')

    def test_content_param_present(self):
        schema = self._run_agent_schema()
        props = schema['parameters']['properties']
        self.assertIn('content', props,
                      "run_agent must expose top-level `content` param for critique/edit agents")

    def test_content_param_is_string(self):
        schema = self._run_agent_schema()
        self.assertEqual(schema['parameters']['properties']['content']['type'], 'string')

    def test_content_param_documented(self):
        schema = self._run_agent_schema()
        desc = schema['parameters']['properties']['content']['description']
        # Description must mention the intent (critique/edit) so GPT knows when to use it
        self.assertIn('score', desc.lower() + ' ')

    def test_content_not_required(self):
        """Most agents don't take content; only required fields stay required."""
        schema = self._run_agent_schema()
        required = schema['parameters'].get('required', [])
        self.assertNotIn('content', required)


class RunAgentHandlerContentPromotionTests(SimpleTestCase):
    """`_handle_universal_agent` must promote top-level content/workspace_id into context."""

    def _invoke(self, payload):
        """Run the handler with mocked Celery dispatch, return (agent_name, context)."""
        from core.services.tool_dispatcher import ToolDispatcher
        dispatcher = ToolDispatcher()
        with patch('core.tasks.execute_agent_task.apply_async') as mock_dispatch:
            mock_dispatch.return_value = MagicMock(id='fake-task-id')
            dispatcher._handle_universal_agent('run_agent', payload, user_id=None, trace_id='t')
            args = mock_dispatch.call_args.kwargs.get('args') or mock_dispatch.call_args.args[0]
        return args[0], args[2]  # agent_name, context

    def test_top_level_content_promoted(self):
        agent_name, context = self._invoke({
            'agent_name': 'voice_critic_agent',
            'task': 'Score this blog',
            'content': 'The blog body text here...',
        })
        self.assertEqual(agent_name, 'VoiceCriticAgent')
        self.assertEqual(context.get('content'), 'The blog body text here...')

    def test_top_level_workspace_id_promoted(self):
        _, context = self._invoke({
            'agent_name': 'research_agent',
            'task': 'Research X',
            'workspace_id': 'af61c625-2cf1-4e70-82b2-d44e301f897e',
        })
        self.assertEqual(context['workspace_id'], 'af61c625-2cf1-4e70-82b2-d44e301f897e')

    def test_context_wins_if_both_provided(self):
        """If context.content already set, top-level doesn't overwrite it.

        Rationale: LLM may have deliberately structured the content (e.g.,
        wrapped in metadata) in context. Don't second-guess the dispatcher
        when they've already made a choice.
        """
        _, context = self._invoke({
            'agent_name': 'voice_critic_agent',
            'task': 'Score this',
            'content': 'SHOULD NOT APPEAR',
            'context': {'content': 'already here'},
        })
        self.assertEqual(context['content'], 'already here')

    def test_no_content_at_all_fine(self):
        """Omitting content is fine for agents that don't need it."""
        _, context = self._invoke({
            'agent_name': 'research_agent',
            'task': 'Research X',
        })
        self.assertNotIn('content', context)


# =============================================================================
# Fix 2: BaseAgent._save_to_deliverable None guard
# =============================================================================

class DeliverableNoneGuardTests(SimpleTestCase):
    """When create_deliverable returns None (quality gate reject),
    _save_to_deliverable must return None gracefully instead of crashing."""

    def _make_concrete_agent(self):
        """BaseAgent is abstract — subclass with a no-op execute for testing."""
        from core.agents.base_agent import BaseAgent, AgentResult

        class _TestAgent(BaseAgent):
            name = 'TestAgent'

            def execute(self, task, context, scifi_context, spider_context):
                return AgentResult(success=True, agent_name=self.name)

        agent = _TestAgent.__new__(_TestAgent)
        agent.name = 'TestAgent'
        agent._current_execution_id = None
        agent._current_task = 'test task'
        return agent

    def test_create_deliverable_returning_none_does_not_crash(self):
        """Previously: AttributeError on deliverable.id."""
        agent = self._make_concrete_agent()

        with patch('core.services.deliverable_factory.create_deliverable',
                   return_value=None) as mock_create:
            result = agent._save_to_deliverable(
                title='Test Title',
                content='Some content',
            )

        mock_create.assert_called_once()
        self.assertIsNone(result,
                          'Should return None when create_deliverable returns None')

    def test_successful_create_still_works(self):
        """The happy path unchanged — returns the Deliverable object."""
        agent = self._make_concrete_agent()

        fake_deliverable = MagicMock()
        fake_deliverable.id = 'fake-id'
        fake_deliverable.quality_score = 0.7

        with patch('core.services.deliverable_factory.create_deliverable',
                   return_value=fake_deliverable), \
             patch.object(agent, '_trigger_deliverable_learning'):
            result = agent._save_to_deliverable(
                title='Test Title',
                content='Some content',
            )

        self.assertIs(result, fake_deliverable)


# =============================================================================
# Fix 3: .env.example stub tokens
# =============================================================================

class EnvExampleStubTests(SimpleTestCase):
    """The .env.example must not contain username:password patterns that
    pre-commit secret-scanning flags as potential credentials."""

    @property
    def env_example_text(self) -> str:
        path = Path(__file__).resolve().parent.parent.parent / '.env.example'
        self.assertTrue(path.exists(), f'.env.example not found at {path}')
        return path.read_text()

    def test_no_secure_password_placeholder(self):
        """The original offending placeholder was `unified_user:secure_password`."""
        text = self.env_example_text
        self.assertNotIn('unified_user:secure_password', text)
        self.assertNotIn('unified_user:staging_password', text)

    def test_uppercase_stub_tokens_used(self):
        """Replacement uses clearly-stub uppercase tokens."""
        text = self.env_example_text
        self.assertIn('DB_USER', text)
        self.assertIn('DB_PASSWORD', text)

    def test_database_url_uses_example_com_host(self):
        """The hook whitelists example.com — using it sidesteps the
        username:password regex entirely even with uppercase stubs."""
        text = self.env_example_text
        # Every DATABASE_URL line (including commented overrides) uses example.com
        import re
        database_url_lines = re.findall(r'.*DATABASE_URL.*', text)
        database_url_lines = [
            line for line in database_url_lines
            if 'postgresql://' in line and 'localhost' in line or 'postgresql://' in line
        ]
        # At least the top-level active one must use example.com
        active_urls = [line for line in database_url_lines if not line.lstrip().startswith('#')]
        self.assertTrue(active_urls, 'Should have at least one active DATABASE_URL line')
        for url in active_urls:
            self.assertIn('example.com', url,
                          f'Active DATABASE_URL must use example.com host: {url}')

    def test_diagnostic_env_flags_documented(self):
        """Session 1093/1094 diagnostic flags must appear as commented-out
        defaults so future contributors can discover + enable them."""
        text = self.env_example_text
        for flag in (
            'CTO_DIAGNOSTIC_ENABLED',
            'CTO_DIAGNOSTIC_POSTING_ENABLED',
            'COO_DIAGNOSTIC_ENABLED',
            'COO_DIAGNOSTIC_POSTING_ENABLED',
            'TREND_DIAGNOSTIC_ENABLED',
            'TREND_DIAGNOSTIC_POSTING_ENABLED',
        ):
            self.assertIn(flag, text, f'{flag} missing from .env.example')
