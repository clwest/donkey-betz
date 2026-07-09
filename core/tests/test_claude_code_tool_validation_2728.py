"""
Session 2728 — Rigby Tool Validation Engineering Campaign, Batch A tool 4
regression tests for `claude_code_tool`.

Covers the F-CC-* findings surfaced during code trace + patched at
Session 2728. See:
- `docs/research/tools/validation/claude_code_tool_validation.md` (findings)
- `docs/research/tools/tools_validation_engineering_campaign_plan.md` (campaign)

Findings covered:

- F-CC-3: Dispatch response now echoes `conversation_id` and surfaces a
  `follow_up_will_fire: bool` field so Rigby can detect whether the S1174
  PR-2 auto-completion banner will arm. Prior response said
  `status: 'dispatched'` regardless of conversation_id resolution — Rigby
  had no way to detect the silent-no-banner consequence from the response.
  Chris ratified option (a) at Batch A tool 4 close: additive fields;
  back-compat safe.

Existing coverage NOT duplicated:
- Task-side receipt reliability (S1262) — covered in
  test_claude_code_task_receipts_s1262.py.
- request_mode heuristic — covered in test_engineer_request_mode.py.
- Agent-dimension resolution — covered in test_claude_code_agent_dim_dispatch.py.

Run::

    python manage.py test core.tests.test_claude_code_tool_validation_2728 -v2
"""
from __future__ import annotations

from unittest.mock import patch

from django.test import SimpleTestCase

from core.services.tool_dispatcher import ToolDispatcher


class _FakeAsyncResult:
    """Stand-in for the Celery AsyncResult returned by `.delay(...)` — the
    only attribute the handler reads is `.id` (used for `str(task.id)`)."""

    def __init__(self, task_id):
        self.id = task_id


class FCC3ConversationIdSurface(SimpleTestCase):
    """F-CC-3 — claude_code_tool dispatch response echoes `conversation_id`
    and surfaces `follow_up_will_fire` so Rigby knows whether to expect a
    completion banner."""

    def _dispatch_claude_code(self, payload):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_claude_code(  # type: ignore[attr-defined]
            tool_name='claude_code_tool',
            payload=payload,
            user_id=None,
            trace_id='test-claude-code-2728',
        )

    def test_dispatch_with_conversation_id_signals_follow_up_will_fire(self):
        with patch(
            'core.tasks.claude_code_engineer_task.delay',
            return_value=_FakeAsyncResult('celery-task-fcc3-a'),
        ):
            result = self._dispatch_claude_code({
                'task': 'add a docstring to core/services/tool_dispatcher.py',
                'conversation_id': 'pa-fcc3-conv-1234567890abcdef',
            })
        self.assertEqual(result['status'], 'dispatched')
        self.assertEqual(result['task_id'], 'celery-task-fcc3-a')
        self.assertEqual(result['conversation_id'], 'pa-fcc3-conv-1234567890abcdef')
        self.assertTrue(result['follow_up_will_fire'])
        # Message should NOT contain the no-banner warning.
        self.assertNotIn('no completion banner will fire', result['message'])
        self.assertIn('Results will be posted', result['message'])

    def test_dispatch_without_conversation_id_signals_no_follow_up(self):
        with patch(
            'core.tasks.claude_code_engineer_task.delay',
            return_value=_FakeAsyncResult('celery-task-fcc3-b'),
        ):
            result = self._dispatch_claude_code({
                'task': 'add a docstring to core/services/tool_dispatcher.py',
                # NO conversation_id
            })
        self.assertEqual(result['status'], 'dispatched')
        self.assertEqual(result['task_id'], 'celery-task-fcc3-b')
        # conversation_id echoed as None when unset (typed absence).
        self.assertIsNone(result['conversation_id'])
        self.assertFalse(result['follow_up_will_fire'])
        # Message must include the poll-alternative guidance.
        self.assertIn('no completion banner will fire', result['message'])
        self.assertIn('execution_history_tool', result['message'])
        self.assertIn('schedule_followup', result['message'])

    def test_dispatch_with_empty_conversation_id_treated_as_missing(self):
        """Regression guard: empty-string conversation_id must be treated
        the same as missing (`follow_up_will_fire=False`)."""
        with patch(
            'core.tasks.claude_code_engineer_task.delay',
            return_value=_FakeAsyncResult('celery-task-fcc3-c'),
        ):
            result = self._dispatch_claude_code({
                'task': 'anything',
                'conversation_id': '',
            })
        self.assertFalse(result['follow_up_will_fire'])
        self.assertIsNone(result['conversation_id'])

    def test_missing_task_still_returns_error_shape(self):
        """Regression guard: empty task still returns the error dict; the
        F-CC-3 patch must NOT change the fail-loud behavior for missing
        task_description."""
        result = self._dispatch_claude_code({'conversation_id': 'pa-fcc3'})
        self.assertIn('error', result)
        self.assertIn('task description is required', result['error'])
        # New F-CC-3 fields must NOT appear on the error response.
        self.assertNotIn('follow_up_will_fire', result)
        self.assertNotIn('status', result)

    def test_request_mode_still_echoed_and_defaults_to_auto(self):
        """Regression guard: F-CC-3 additive fields must not disturb
        existing `request_mode` echo (Session 1230 P4)."""
        with patch(
            'core.tasks.claude_code_engineer_task.delay',
            return_value=_FakeAsyncResult('celery-task-fcc3-e'),
        ):
            result_no_mode = self._dispatch_claude_code({
                'task': 'anything',
                'conversation_id': 'pa-fcc3',
            })
        self.assertEqual(result_no_mode['request_mode'], 'auto')

        with patch(
            'core.tasks.claude_code_engineer_task.delay',
            return_value=_FakeAsyncResult('celery-task-fcc3-f'),
        ):
            result_change = self._dispatch_claude_code({
                'task': 'refactor the dispatcher',
                'conversation_id': 'pa-fcc3',
                'request_mode': 'change',
            })
        self.assertEqual(result_change['request_mode'], 'change')

    def test_task_alias_still_works_with_fcc3_fields(self):
        """Regression guard: F-CC-3 additive fields must not disturb the
        multi-alias `task` extraction path (F-CC-1 defensive behavior)."""
        with patch(
            'core.tasks.claude_code_engineer_task.delay',
            return_value=_FakeAsyncResult('celery-task-fcc3-g'),
        ):
            result = self._dispatch_claude_code({
                # `task_description` alias, not the schema-declared `task`.
                'task_description': 'reachable via the alias fallback',
                'conversation_id': 'pa-fcc3',
            })
        self.assertEqual(result['status'], 'dispatched')
        self.assertTrue(result['follow_up_will_fire'])
        self.assertEqual(result['conversation_id'], 'pa-fcc3')
