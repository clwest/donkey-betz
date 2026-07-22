"""
S2874 slate — Rigby Tool Gap Ledger #2 promote (2nd trigger at S2873).

Extends ``repo_tool.read_file`` with an ``allow_large=True`` opt-in that lifts
the 500KB soft cap for large-file paged reads. The prior hard cap
short-circuited before the existing ``start_line``/``max_lines`` paging params
fired, leaving files like ``core/models_unified_system.py`` (~760KB)
unreachable via ``read_file`` at all.

Pre-code SIGN via Rigby (2026-07-21) folded four refinements into the design:

* Q1: default remains ``allow_large=False`` + structured ``file_too_large``
  envelope; error carries ``path``, ``file_size_bytes``, ``narrowing_hint``.
* Q2: skip the ``total_lines`` second-pass unconditionally when
  ``size > 500_000`` — no operator should pay double I/O for metadata even
  in opt-in mode. Surface as ``total_lines_known=False``.
* Q3: ``start_line`` past EOF (or empty file) → soft ``warning_code``
  field, not a hard error; script-friendly empty result.
* Q4: local ``_read_file_error`` helper for envelope-shape consistency; do
  NOT retrofit ``tree`` yet (different failure modes).

Run::

    python manage.py test core.tests.test_s2874_repo_tool_read_file_paging -v2
"""

from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher


class RepoReadFileLargeFileDefaultTests(TestCase):
    """Default path (allow_large=False) on a >500KB file — structured error."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _dispatch(self, **payload):
        return self.dispatcher._handle_repo(
            'repo_tool', payload, None, 'test-trace-s2874-large-default',
        )

    def test_large_file_default_returns_structured_error(self):
        result = self._dispatch(
            action='read_file', path='core/models_unified_system.py',
        )
        self.assertEqual(result.get('error_code'), 'file_too_large', result)
        self.assertIn('error', result)
        self.assertIn('allow_large', result['error'])

    def test_large_file_error_envelope_has_size_and_path(self):
        result = self._dispatch(
            action='read_file', path='core/models_unified_system.py',
        )
        self.assertEqual(result['path'], 'core/models_unified_system.py')
        self.assertGreater(result['file_size_bytes'], 500_000)
        self.assertEqual(result['size_hard_max'], 500_000)

    def test_large_file_error_envelope_has_narrowing_hint(self):
        result = self._dispatch(
            action='read_file', path='core/models_unified_system.py',
        )
        hint = result.get('narrowing_hint')
        self.assertIsInstance(hint, dict)
        self.assertTrue(hint['set_allow_large'])
        self.assertEqual(hint['suggested_max_lines'], 200)


class RepoReadFileLargeFilePagingTests(TestCase):
    """allow_large=True path on a >500KB file — paged read works."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _dispatch(self, **payload):
        return self.dispatcher._handle_repo(
            'repo_tool', payload, None, 'test-trace-s2874-large-paged',
        )

    def test_allow_large_returns_first_page(self):
        result = self._dispatch(
            action='read_file',
            path='core/models_unified_system.py',
            allow_large=True,
        )
        self.assertNotIn('error', result)
        self.assertEqual(result['action'], 'read_file')
        self.assertEqual(result['start_line'], 0)
        self.assertEqual(result['end_line'], 200)
        self.assertEqual(result['lines'], 200)
        self.assertFalse(result['total_lines_known'])
        self.assertTrue(result['truncated'])
        self.assertNotIn('total_lines', result)
        self.assertGreater(len(result['content']), 0)

    def test_allow_large_with_start_line_and_max_lines(self):
        result = self._dispatch(
            action='read_file',
            path='core/models_unified_system.py',
            start_line=500,
            max_lines=50,
            allow_large=True,
        )
        self.assertEqual(result['start_line'], 500)
        self.assertEqual(result['end_line'], 550)
        self.assertEqual(result['lines'], 50)
        self.assertFalse(result['total_lines_known'])
        self.assertTrue(result['truncated'])
        self.assertIn('501:', result['content'])

    def test_allow_large_max_lines_hard_cap_still_enforced(self):
        result = self._dispatch(
            action='read_file',
            path='core/models_unified_system.py',
            max_lines=9999,
            allow_large=True,
        )
        self.assertEqual(result['lines'], 500)
        self.assertEqual(result['end_line'], 500)

    def test_allow_large_start_line_past_eof_returns_warning(self):
        result = self._dispatch(
            action='read_file',
            path='core/models_unified_system.py',
            start_line=999_999,
            max_lines=10,
            allow_large=True,
        )
        self.assertEqual(result['lines'], 0)
        self.assertEqual(result['end_line'], 999_999)
        self.assertEqual(
            result.get('warning_code'),
            'start_line_past_eof_or_empty_file',
        )
        self.assertNotIn('error', result)


class RepoReadFileSmallFileTests(TestCase):
    """Small file (<500KB) — prior behavior preserved + shape parity."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _dispatch(self, **payload):
        return self.dispatcher._handle_repo(
            'repo_tool', payload, None, 'test-trace-s2874-small',
        )

    def test_small_file_default_returns_content_and_total_lines(self):
        result = self._dispatch(
            action='read_file', path='core/services/td_handlers_gateway.py',
        )
        self.assertNotIn('error', result)
        self.assertTrue(result['total_lines_known'])
        self.assertIn('total_lines', result)
        self.assertGreater(result['total_lines'], 2000)
        self.assertEqual(result['lines'], 200)
        self.assertTrue(result['truncated'])

    def test_small_file_file_size_bytes_present(self):
        result = self._dispatch(
            action='read_file', path='core/services/td_handlers_gateway.py',
        )
        self.assertLess(result['file_size_bytes'], 500_000)
        self.assertGreater(result['file_size_bytes'], 10_000)

    def test_small_file_allow_large_true_is_a_noop(self):
        result_default = self._dispatch(
            action='read_file', path='core/services/td_handlers_gateway.py',
        )
        result_opt_in = self._dispatch(
            action='read_file',
            path='core/services/td_handlers_gateway.py',
            allow_large=True,
        )
        self.assertEqual(
            result_default['total_lines'], result_opt_in['total_lines'],
        )
        self.assertEqual(result_default['lines'], result_opt_in['lines'])
        self.assertTrue(result_default['total_lines_known'])
        self.assertTrue(result_opt_in['total_lines_known'])


class RepoReadFileEnvelopeShapeTests(TestCase):
    """Structured error envelope shape consistency (Rigby Q4 fold)."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _dispatch(self, **payload):
        return self.dispatcher._handle_repo(
            'repo_tool', payload, None, 'test-trace-s2874-envelope',
        )

    def test_missing_path_returns_structured_error(self):
        result = self._dispatch(action='read_file')
        self.assertEqual(result.get('error_code'), 'path_required')
        self.assertIn('error', result)

    def test_file_not_found_returns_structured_error(self):
        result = self._dispatch(
            action='read_file', path='does/not/exist.py',
        )
        self.assertEqual(result.get('error_code'), 'file_not_found')
        self.assertEqual(result['path'], 'does/not/exist.py')

    def test_file_too_large_error_has_error_and_error_code_both(self):
        """Ensure the envelope keeps human `error` alongside machine `error_code`."""
        result = self._dispatch(
            action='read_file', path='core/models_unified_system.py',
        )
        self.assertIn('error', result)
        self.assertIn('error_code', result)
        self.assertEqual(result['error_code'], 'file_too_large')
