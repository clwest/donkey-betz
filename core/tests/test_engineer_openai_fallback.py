"""Session 1226 P4 — claude_code_engineer OpenAI fallback path tests.

Confirms the workaround that routes the autonomous engineer through gpt-5-mini
when Anthropic credits are exhausted (CLAUDE_CODE_ENGINE_PROVIDER=openai).

Covers:
- Tool format translation (Anthropic → OpenAI function-call schema)
- Provider routing dispatches to the OpenAI path when env is set
- Provider routing falls back to Anthropic path when env is unset/absent
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.test import TestCase

from core.services.claude_code_engineer import (
    TOOLS,
    _OPENAI_TOOLS,
    _translate_tools_to_openai,
    execute_engineering_task,
)


class ToolTranslationTests(TestCase):
    """Anthropic tool format → OpenAI function-call format."""

    def test_translation_preserves_all_tools(self):
        self.assertEqual(len(_OPENAI_TOOLS), len(TOOLS))

    def test_translated_shape_matches_openai_schema(self):
        translated = _translate_tools_to_openai([
            {
                'name': 'echo',
                'description': 'echo the input',
                'input_schema': {
                    'type': 'object',
                    'properties': {'msg': {'type': 'string'}},
                    'required': ['msg'],
                },
            }
        ])
        self.assertEqual(translated, [{
            'type': 'function',
            'function': {
                'name': 'echo',
                'description': 'echo the input',
                'parameters': {
                    'type': 'object',
                    'properties': {'msg': {'type': 'string'}},
                    'required': ['msg'],
                },
            },
        }])

    def test_all_anthropic_tools_have_input_schema(self):
        """Smoke check — any future-added tool MUST have input_schema or translation breaks."""
        for tool in TOOLS:
            self.assertIn('input_schema', tool, f"tool {tool.get('name')} missing input_schema")


class ProviderRoutingTests(TestCase):
    """CLAUDE_CODE_ENGINE_PROVIDER env routes to OpenAI vs Anthropic."""

    def _stub_openai_response_done(self, content='All set.'):
        """Return an OpenAI client whose first call returns finish_reason='stop'."""
        client = MagicMock()
        msg = MagicMock()
        msg.content = content
        msg.tool_calls = None
        choice = MagicMock()
        choice.message = msg
        choice.finish_reason = 'stop'
        response = MagicMock()
        response.choices = [choice]
        client.chat.completions.create.return_value = response
        return client

    @patch('core.services.claude_code_engineer._ensure_git_repo', lambda: None)
    @patch('core.services.claude_code_engineer._post_to_conversation', lambda *a, **k: None)
    @patch.dict('os.environ', {'CLAUDE_CODE_ENGINE_PROVIDER': 'openai'}, clear=False)
    def test_provider_openai_dispatches_to_openai_path(self):
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=self._stub_openai_response_done('hello from gpt-5-mini'),
        ):
            result = execute_engineering_task(
                task_description='Say hello.',
                conversation_id=None,
                max_iterations=5,
            )
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result.get('provider'), 'openai')
        self.assertEqual(result['summary'], 'hello from gpt-5-mini')

    @patch('core.services.claude_code_engineer._ensure_git_repo', lambda: None)
    @patch.dict('os.environ', {}, clear=False)
    def test_provider_unset_uses_anthropic_path(self):
        """When the env var is missing AND ANTHROPIC_API_KEY is missing, fall through
        to the Anthropic path's early-return error envelope. Confirms we didn't
        accidentally route to OpenAI by default.
        """
        # Make sure the OpenAI env var is removed even if the runner set it
        import os
        os.environ.pop('CLAUDE_CODE_ENGINE_PROVIDER', None)
        os.environ.pop('ANTHROPIC_API_KEY', None)

        result = execute_engineering_task(
            task_description='no-op',
            conversation_id=None,
            max_iterations=1,
        )
        self.assertEqual(result['status'], 'error')
        self.assertEqual(result['error'], 'ANTHROPIC_API_KEY not set')
        self.assertNotIn('provider', result)  # anthropic path doesn't tag

    @patch('core.services.claude_code_engineer._ensure_git_repo', lambda: None)
    @patch('core.services.claude_code_engineer._post_to_conversation', lambda *a, **k: None)
    @patch.dict('os.environ', {'CLAUDE_CODE_ENGINE_PROVIDER': 'OpenAI'}, clear=False)
    def test_provider_value_is_case_insensitive(self):
        """'OpenAI' / 'OPENAI' / 'openai' all route the same way."""
        with patch(
            'core.services.openai_client_factory.get_openai_client',
            return_value=self._stub_openai_response_done(),
        ):
            result = execute_engineering_task(
                task_description='Say hello.',
                conversation_id=None,
                max_iterations=5,
            )
        self.assertEqual(result.get('provider'), 'openai')
