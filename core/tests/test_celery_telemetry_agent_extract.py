"""Tests for the Session 1169 agent_name extraction helper.

Closes Session 1168 carryover F. Verifies that ``_extract_agent_name``
walks the 4-key fallback order Rigby ratified (agent_name → agent_class
→ agent → agent_type), accepts only strings, and returns ``''`` on
every degraded path so the signal handler can never crash on bad input.

Run::

    python manage.py test core.tests.test_celery_telemetry_agent_extract -v2
"""
from __future__ import annotations

from django.test import SimpleTestCase

from core.celery_telemetry import _extract_agent_name


class ExtractAgentNameTests(SimpleTestCase):

    # ── Happy path: each key in priority order ────────────────────────

    def test_agent_name_key_wins_when_present(self):
        self.assertEqual(
            _extract_agent_name({'agent_name': 'WinnerAgent'}),
            'WinnerAgent',
        )

    def test_agent_class_key_used_when_agent_name_absent(self):
        self.assertEqual(
            _extract_agent_name({'agent_class': 'ClassyAgent'}),
            'ClassyAgent',
        )

    def test_agent_key_used_when_first_two_absent(self):
        self.assertEqual(
            _extract_agent_name({'agent': 'BareAgent'}),
            'BareAgent',
        )

    def test_agent_type_used_as_last_fallback(self):
        self.assertEqual(
            _extract_agent_name({'agent_type': 'TypeAgent'}),
            'TypeAgent',
        )

    def test_priority_order_enforced(self):
        """When multiple keys are present, the earliest in the priority
        list wins."""
        self.assertEqual(
            _extract_agent_name({
                'agent_type': 'fourth',
                'agent': 'third',
                'agent_class': 'second',
                'agent_name': 'first',  # wins
            }),
            'first',
        )

    # ── Sad paths: must return '' rather than crash ────────────────────

    def test_none_input_returns_empty(self):
        self.assertEqual(_extract_agent_name(None), '')

    def test_non_dict_input_returns_empty(self):
        self.assertEqual(_extract_agent_name('not-a-dict'), '')
        self.assertEqual(_extract_agent_name(42), '')
        self.assertEqual(_extract_agent_name(['list', 'of', 'stuff']), '')

    def test_empty_dict_returns_empty(self):
        self.assertEqual(_extract_agent_name({}), '')

    def test_no_known_keys_returns_empty(self):
        self.assertEqual(
            _extract_agent_name({'unrelated': 'value', 'task_kwargs': 'other'}),
            '',
        )

    # ── Type / value filtering: only non-empty strings accepted ───────

    def test_non_string_agent_value_is_skipped(self):
        """The 'agent' key is intentionally tolerant: callers sometimes
        pass an instance object. We must not coerce it to repr() — fall
        through to the next key instead."""
        self.assertEqual(
            _extract_agent_name({
                'agent': object(),  # not a string → skip
                'agent_type': 'fallback',
            }),
            'fallback',
        )

    def test_non_string_agent_name_falls_through(self):
        """Same rule applies to all keys, not just `agent`."""
        self.assertEqual(
            _extract_agent_name({
                'agent_name': 42,  # int — not a string
                'agent_class': 'fallback-cls',
            }),
            'fallback-cls',
        )

    def test_empty_string_falls_through(self):
        self.assertEqual(
            _extract_agent_name({
                'agent_name': '',
                'agent_class': 'BackupAgent',
            }),
            'BackupAgent',
        )

    def test_whitespace_only_falls_through(self):
        self.assertEqual(
            _extract_agent_name({
                'agent_name': '   ',
                'agent_class': 'BackupAgent',
            }),
            'BackupAgent',
        )

    # ── Length cap ────────────────────────────────────────────────────

    def test_long_agent_name_truncated_to_255(self):
        long_name = 'A' * 500
        result = _extract_agent_name({'agent_name': long_name})
        self.assertEqual(len(result), 255)
        self.assertEqual(result, 'A' * 255)
