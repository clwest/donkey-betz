"""
Tests for claude_code_engineer per-dispatch budget caps.

Session 2967 Slice 7 PR-1 — verifies:
  1. Iteration cap terminates the LLM loop cleanly with envelope
     status='budget_exceeded' (not 'error') when hit.
  2. Cost cap terminates the LLM loop cleanly when accumulated Anthropic
     spend >= max_cost_usd, with correct partial-results envelope.
  3. Null caps from the caller resolve to the engine defaults
     (DEFAULT_MAX_ITERATIONS=150, DEFAULT_MAX_COST_USD=5.0) and echo
     back in the envelope.

Design pattern mirrors core/tests/test_engineer_openai_fallback.py +
core/tests/test_engineer_request_mode.py — mock the Anthropic client at
the get_anthropic_client factory, drive iteration count via the mock
side_effects list.

Rigby T1 SIGN answers guided:
  * envelope status='budget_exceeded' is a controlled stop, not an error
    (zoom-out answer #3)
  * iterations_used echoes for debugging without reading logs
  * caps are per-dispatch; null → engine defaults
"""
from unittest.mock import patch, MagicMock
from django.test import SimpleTestCase


def _make_mock_response(input_tokens=100, output_tokens=100, stop_reason="tool_use"):
    """Build a fake Anthropic response object with .usage + .content + .stop_reason."""
    response = MagicMock()
    response.stop_reason = stop_reason
    # Empty tool_use block that triggers another loop iteration
    response.content = []
    response.usage = MagicMock()
    response.usage.input_tokens = input_tokens
    response.usage.output_tokens = output_tokens
    response.usage.cache_read_input_tokens = 0
    response.usage.cache_creation_input_tokens = 0
    return response


def _make_end_turn_response(text="done."):
    """Build a fake end-of-turn Anthropic response with a text block."""
    response = MagicMock()
    response.stop_reason = "end_turn"
    text_block = MagicMock()
    text_block.text = text
    response.content = [text_block]
    response.usage = MagicMock()
    response.usage.input_tokens = 100
    response.usage.output_tokens = 100
    response.usage.cache_read_input_tokens = 0
    response.usage.cache_creation_input_tokens = 0
    return response


class TestIterationCap(SimpleTestCase):
    """max_iterations enforcement — loop terminates without end_turn hit."""

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'sk-test', 'CLAUDE_CODE_ENGINE_PROVIDER': 'anthropic'}, clear=False)
    @patch('core.services.claude_code_engineer._post_to_conversation')
    @patch('core.services.anthropic_client_factory.get_anthropic_client')
    def test_iteration_cap_terminates_loop(self, mock_get_client, mock_post):
        """max_iterations=3 stops the loop at iteration 3 with ITERATION_CAP marker."""
        from core.services.claude_code_engineer import execute_engineering_task

        # Always return tool_use (never end_turn) → loop runs to iteration cap
        client = MagicMock()
        client.messages.create.return_value = _make_mock_response(stop_reason="tool_use")
        mock_get_client.return_value = client

        result = execute_engineering_task(
            "test task",
            conversation_id=None,
            max_iterations=3,
            max_cost_usd=100.0,  # High so cost cap doesn't fire first
            request_mode='change',
        )

        # Engine consumed exactly max_iterations before else-branch fired
        self.assertEqual(client.messages.create.call_count, 3)
        # Envelope reports success (iteration cap hit ≠ error)
        self.assertEqual(result['status'], 'success')
        self.assertIn('ITERATION_CAP', result['summary'])
        self.assertEqual(result['iterations_used'], 3)
        self.assertEqual(result['effective_max_iterations'], 3)
        self.assertFalse(result['budget_exceeded'])


class TestCostCap(SimpleTestCase):
    """max_cost_usd enforcement — loop terminates with budget_exceeded envelope."""

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'sk-test', 'CLAUDE_CODE_ENGINE_PROVIDER': 'anthropic'}, clear=False)
    @patch('core.services.claude_code_engineer._post_to_conversation')
    @patch('core.services.anthropic_client_factory.get_anthropic_client')
    def test_cost_cap_terminates_loop_before_iterations(self, mock_get_client, mock_post):
        """Fat responses (1M output tokens each) trip $5 cap on iteration 1."""
        from core.services.claude_code_engineer import execute_engineering_task

        # 1M output tokens at $15/M = $15 → exceeds $5 cap on first iteration
        client = MagicMock()
        client.messages.create.return_value = _make_mock_response(
            input_tokens=0, output_tokens=1_000_000, stop_reason="tool_use",
        )
        mock_get_client.return_value = client

        result = execute_engineering_task(
            "test task",
            conversation_id=None,
            max_iterations=100,  # High so iteration cap doesn't fire first
            max_cost_usd=5.0,
            request_mode='change',
        )

        # Cost cap fired on iteration 1 (single message.create call)
        self.assertEqual(client.messages.create.call_count, 1)
        # Envelope reports budget_exceeded (controlled stop, not error)
        self.assertEqual(result['status'], 'budget_exceeded')
        self.assertTrue(result['budget_exceeded'])
        self.assertIn('BUDGET_EXCEEDED', result['summary'])
        self.assertGreaterEqual(result['cost_usd'], 5.0)
        self.assertEqual(result['effective_max_cost_usd'], 5.0)
        self.assertEqual(result['iterations_used'], 1)


class TestNullCapsResolveToDefaults(SimpleTestCase):
    """Null / omitted caps use DEFAULT_MAX_ITERATIONS (150) and DEFAULT_MAX_COST_USD ($5)."""

    @patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'sk-test', 'CLAUDE_CODE_ENGINE_PROVIDER': 'anthropic'}, clear=False)
    @patch('core.services.claude_code_engineer._post_to_conversation')
    @patch('core.services.anthropic_client_factory.get_anthropic_client')
    def test_null_caps_use_engine_defaults(self, mock_get_client, mock_post):
        """max_iterations=None + max_cost_usd=None → defaults echoed in envelope."""
        from core.services.claude_code_engineer import (
            execute_engineering_task,
            DEFAULT_MAX_ITERATIONS,
            DEFAULT_MAX_COST_USD,
        )

        # end_turn on iteration 1 so loop exits cheaply
        client = MagicMock()
        client.messages.create.return_value = _make_end_turn_response("finished.")
        mock_get_client.return_value = client

        result = execute_engineering_task(
            "test task",
            conversation_id=None,
            # NO caps passed — should resolve to defaults
            request_mode='change',
        )

        # Envelope echoes the engine defaults
        self.assertEqual(result['effective_max_iterations'], DEFAULT_MAX_ITERATIONS)
        self.assertEqual(result['effective_max_cost_usd'], DEFAULT_MAX_COST_USD)
        self.assertEqual(DEFAULT_MAX_ITERATIONS, 150)
        self.assertEqual(DEFAULT_MAX_COST_USD, 5.0)
        # Ran to completion (end_turn), not budget-exceeded
        self.assertEqual(result['status'], 'success')
        self.assertFalse(result['budget_exceeded'])
