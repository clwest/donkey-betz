"""Session 1199 — PA LLM iteration-cap silent-fallback regression tests.

Covers the two-part fix shipped to close deliverable ``c2bac9c0``:

A. ``max_iterations`` raised from 8 → 12 in ``_run_agentic_loop``
B. ``_detect_silent_tool_call_fallback`` scans the final text response
   for tool-call-shaped JSON; matches trigger a CRIT log + a clear
   user-visible error + ``silent_fallback=true`` in PA_TASK_SUMMARY

These tests are pure (no Django DB) so they bypass the pgbouncer test
DB blocker.

Run::

    python manage.py test core.tests.test_pa_silent_fallback_detector -v2
"""

import inspect
import unittest

from core.services.unified_pa_entrypoint import (
    UnifiedPAEntrypoint,
    _detect_silent_tool_call_fallback,
    _SILENT_FALLBACK_USER_MESSAGE,
)


class IterationCapRaisedTest(unittest.TestCase):
    """AC: max_iterations default is now 12 (was 8)."""

    def test_max_iterations_default_is_12(self):
        sig = inspect.signature(UnifiedPAEntrypoint._run_agentic_loop)
        self.assertEqual(sig.parameters['max_iterations'].default, 12)


class SilentFallbackDetectorTest(unittest.TestCase):
    """AC: detector flags tool-call JSON patterns in text."""

    def test_array_dump_detected(self):
        """Real Session 1193 symptom — array of unexecuted updates."""
        text = (
            'Here are the updates I planned:\n'
            '[{"action": "update", "id": "abc-123", "tags": ["x"]}, '
            '{"action": "update", "id": "def-456", "tags": ["y"]}]'
        )
        self.assertTrue(_detect_silent_tool_call_fallback(text))

    def test_single_object_dump_detected(self):
        text = '{"action": "create", "title": "X", "content": "Y"}'
        self.assertTrue(_detect_silent_tool_call_fallback(text))

    def test_dump_with_other_keys_detected(self):
        """LLM may put action first OR put other keys first; the regex
        matches on the brace+action pattern specifically."""
        text = '{"action": "link_initiative", "deliverable_id": "x", "initiative_id": "y"}'
        self.assertTrue(_detect_silent_tool_call_fallback(text))

    def test_multiline_dump_detected(self):
        text = '''Here's what I tried to do:

{
  "action": "update",
  "id": "abc"
}'''
        self.assertTrue(_detect_silent_tool_call_fallback(text))

    def test_legitimate_conversational_text_not_flagged(self):
        text = (
            'I will take the next action by reviewing the deliverables '
            'and updating them one at a time.'
        )
        self.assertFalse(_detect_silent_tool_call_fallback(text))

    def test_legitimate_text_with_action_field_phrase_not_flagged(self):
        """Mentioning "action" without the JSON brace pattern is fine."""
        text = 'The action field on the deliverable tool accepts: create, update, list.'
        self.assertFalse(_detect_silent_tool_call_fallback(text))

    def test_empty_text_not_flagged(self):
        self.assertFalse(_detect_silent_tool_call_fallback(''))
        self.assertFalse(_detect_silent_tool_call_fallback(None))

    def test_text_with_only_other_json_not_flagged(self):
        """JSON without "action" key is not flagged."""
        text = 'Here is some JSON: {"name": "X", "value": 42}'
        self.assertFalse(_detect_silent_tool_call_fallback(text))


class UserMessageContractTest(unittest.TestCase):
    """AC: the user-visible message clearly explains what happened."""

    def test_user_message_mentions_iteration_cap(self):
        self.assertIn('iteration', _SILENT_FALLBACK_USER_MESSAGE.lower())

    def test_user_message_mentions_nothing_saved(self):
        msg = _SILENT_FALLBACK_USER_MESSAGE.lower()
        self.assertTrue('nothing was saved' in msg or 'not saved' in msg)

    def test_user_message_actionable(self):
        """Tells user to ping again to continue."""
        self.assertIn('ping', _SILENT_FALLBACK_USER_MESSAGE.lower())
