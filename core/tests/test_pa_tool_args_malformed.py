"""
PA tool-call args JSON malformed detection — Session 1177 F1 regression test.

Background: in Session 1176 we discovered that `deliverable_tool update`
silently fell back to `action=list` for content payloads above ~6-7kB.
Session 1177 root-cause: at `unified_pa_entrypoint.py:1521` the LLM's
tool-call `arguments` field was being parsed via `json.loads` with a
silent `except: arguments = {}` fallback. When the LLM truncated its
args output (long content payload hits output token budget), the JSON
parse raised and the empty-dict fallback flowed into the handler. The
handler defaulted `action` to `'list'`, so Rigby's intended update
silently became a list-deliverables call and the write was lost.

This test pins the fix: malformed args produce a typed
`TOOL_ARGS_JSON_MALFORMED` envelope and the tool handler is never
invoked.

Run:
    python manage.py test core.tests.test_pa_tool_args_malformed -v2
"""
import json

from django.test import SimpleTestCase

from core.services.unified_pa_entrypoint import (
    TOOL_ARGS_MALFORMED_ERROR_CODE,
    _build_tool_args_malformed_envelope,
)


class ToolArgsMalformedEnvelopeTests(SimpleTestCase):
    """`_build_tool_args_malformed_envelope` shape ratified by Rigby in Session 1177."""

    def _build(self, *, tool_name: str, raw_args: str):
        try:
            json.loads(raw_args)
        except (json.JSONDecodeError, TypeError) as parse_err:
            return _build_tool_args_malformed_envelope(
                tool_name=tool_name,
                raw_args=raw_args,
                parse_err=parse_err,
            )
        raise AssertionError(
            f"Expected raw_args to fail json.loads but it parsed: {raw_args!r}"
        )

    def test_truncated_json_produces_typed_envelope(self):
        # Simulates the Session 1176 repro: LLM started emitting a large
        # content update but truncated mid-string before the closing brace.
        truncated = '{"id": "abc-123", "action": "update", "content": "this is a long content that gets cut off mid'
        env = self._build(tool_name='deliverable_tool', raw_args=truncated)

        self.assertFalse(env['ok'])
        self.assertEqual(env['error_code'], TOOL_ARGS_MALFORMED_ERROR_CODE)
        self.assertEqual(env['tool_name'], 'deliverable_tool')
        self.assertIn('truncated', env['message'].lower())
        self.assertIn('append', env['message'].lower())

    def test_envelope_meta_includes_args_len_and_tail(self):
        raw = '{"action": "update", "content": "' + ('x' * 500) + 'unterminated'
        env = self._build(tool_name='deliverable_tool', raw_args=raw)

        self.assertEqual(env['meta']['arguments_len'], len(raw))
        self.assertTrue(env['meta']['parse_error'].startswith('JSONDecodeError'))
        # Tail must be at most 200 chars and come from the *end* of the input —
        # that's what tells the operator where the truncation occurred.
        self.assertLessEqual(len(env['meta']['arguments_excerpt_tail']), 200)
        self.assertTrue(raw.endswith(env['meta']['arguments_excerpt_tail']))

    def test_retry_hint_points_at_append_for_tool_names(self):
        env = self._build(tool_name='deliverable_tool', raw_args='{not valid')
        self.assertEqual(env['retry_hint']['recommended_action'], 'deliverable_tool.append')
        self.assertEqual(env['retry_hint']['max_chunk_chars_suggestion'], 2000)

    def test_retry_hint_none_for_non_tool_suffix_names(self):
        # Some PA entries (e.g. agent dispatches like `research_agent`) don't
        # follow the `_tool` suffix convention and don't have an append variant.
        env = self._build(tool_name='research_agent', raw_args='{not valid')
        self.assertIsNone(env['retry_hint']['recommended_action'])

    def test_short_raw_args_full_in_tail(self):
        # When args are shorter than 200 chars, the entire string appears in tail
        # (so operators see the whole thing in logs).
        raw = '{"action": "upd'
        env = self._build(tool_name='deliverable_tool', raw_args=raw)
        self.assertEqual(env['meta']['arguments_excerpt_tail'], raw)

    def test_empty_args_string_is_handled(self):
        # If the LLM somehow emits an empty string instead of '{}', json.loads
        # raises JSONDecodeError on the first char — we still produce a clean
        # envelope rather than a generic stack trace.
        env = self._build(tool_name='deliverable_tool', raw_args='')
        self.assertFalse(env['ok'])
        self.assertEqual(env['meta']['arguments_len'], 0)
        self.assertEqual(env['meta']['arguments_excerpt_tail'], '')
