"""
S2875 slate — Rigby Tool Gap Ledger #2 promote (2nd trigger at S2874 close).

Extends the S2874 structured-error envelope shape
(``{error, error_code, ...optional_fields}``) from ``repo_tool.read_file``
to 3 sibling read-path handlers:

* ``repo_tool`` (tree / search / shared catchers)
* ``kb_tool`` (chunks / search_embeddings / semantic_search / shared)
* ``spider_status_tool`` (history / detail / search / shared)

Pre-code SIGN via Rigby (2026-07-21) folded four refinements:

* Q1: full-coverage sweep across all 3 handlers surfaced 5 within-handler
  sites Rigby's initial pass missed (kb.chunks/search_embeddings/semantic,
  spider_status.history). Migrated all 17 for internal consistency.
* Q2: envelope shape matches S2874 exactly — ``{error, error_code, ...}``,
  NO ``success: false`` key (proposal corrected in-flight).
* Q3=A: keep ``_tool_error`` helper local per file (2 module-level helpers
  in ``td_handlers_gateway.py`` + ``td_handlers_ops.py``). Do NOT extract
  ``td_error.py`` gateway helper until 6+ adopters stable.
* Q4 folds: preserve exact error message text (no rephrasing → no substring
  regressions); ``error_code`` is optional during mixed-mode migration;
  partial-success ``warnings:[]``/``errors:[]`` convention deferred until
  first real trigger.

Run::

    python manage.py test core.tests.test_s2875_cross_tool_error_envelope -v2
"""

from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher


# ────────────────────────────────────────────────────────────────────────
# repo_tool — 5 sites
# ────────────────────────────────────────────────────────────────────────


class RepoToolErrorEnvelopeTests(TestCase):
    """Envelope-shape tests for the 5 migrated repo_tool error paths."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _dispatch(self, **payload):
        return self.dispatcher._handle_repo(
            'repo_tool', payload, None, 'test-trace-s2875-repo',
        )

    def test_tree_not_a_directory_returns_structured_envelope(self):
        # Point at a file that exists but isn't a directory.
        result = self._dispatch(action='tree', path='manage.py')
        self.assertEqual(result.get('error_code'), 'not_a_directory')
        self.assertIn('Not a directory', result.get('error', ''))
        self.assertEqual(result.get('path'), 'manage.py')

    def test_search_missing_query_returns_structured_envelope(self):
        result = self._dispatch(action='search', path='core/')
        self.assertEqual(result.get('error_code'), 'query_required')
        self.assertEqual(result.get('error'), 'query is required for search')

    def test_unknown_action_returns_structured_envelope(self):
        result = self._dispatch(action='does_not_exist')
        self.assertEqual(result.get('error_code'), 'unknown_action')
        self.assertIn('Unknown repo_tool action', result.get('error', ''))
        self.assertEqual(result.get('action'), 'does_not_exist')
        self.assertIn('tree', result.get('valid_actions', []))
        self.assertIn('read_file', result.get('valid_actions', []))

    def test_value_error_catcher_returns_structured_envelope(self):
        # `..` outside project root triggers _safe_path → ValueError.
        result = self._dispatch(action='read_file', path='../../../../etc/passwd')
        self.assertEqual(result.get('error_code'), 'value_error')
        # exact ValueError message preserved (no rephrasing per Q4 fold)
        self.assertTrue(result.get('error'))

    def test_error_message_text_preserved_verbatim(self):
        """Q4 fold #1: no rephrasing — downstream substring matchers must not regress."""
        result = self._dispatch(action='search', path='core/')
        self.assertEqual(result.get('error'), 'query is required for search')


# ────────────────────────────────────────────────────────────────────────
# spider_status_tool — 6 sites
# ────────────────────────────────────────────────────────────────────────


class SpiderStatusToolErrorEnvelopeTests(TestCase):
    """Envelope-shape tests for the 6 migrated spider_status_tool paths."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _dispatch(self, **payload):
        return self.dispatcher._handle_spider_status(
            'spider_status_tool', payload, None,
            'test-trace-s2875-spider-status',
        )

    def test_history_missing_spider_name_returns_structured_envelope(self):
        result = self._dispatch(action='history')
        self.assertEqual(result.get('error_code'), 'spider_name_required')
        self.assertEqual(
            result.get('error'),
            'spider_name required for history action',
        )

    def test_detail_missing_item_id_returns_structured_envelope(self):
        result = self._dispatch(action='detail')
        self.assertEqual(result.get('error_code'), 'item_id_required')
        self.assertEqual(
            result.get('error'),
            'item_id required for detail action',
        )

    def test_detail_item_not_found_returns_structured_envelope(self):
        # Well-formed UUID that won't exist. LegacySpiderData uses UUID PK;
        # bogus UUID → DoesNotExist branch.
        bogus_id = '00000000-0000-0000-0000-000000000000'
        result = self._dispatch(action='detail', item_id=bogus_id)
        self.assertEqual(result.get('error_code'), 'item_not_found')
        self.assertIn(bogus_id, result.get('error', ''))
        self.assertEqual(result.get('item_id'), bogus_id)

    def test_search_missing_all_filters_returns_structured_envelope(self):
        result = self._dispatch(action='search')
        self.assertEqual(result.get('error_code'), 'filters_required')
        self.assertEqual(
            result.get('error'),
            'At least one of query, data_type, or spider_name required',
        )

    def test_unknown_action_returns_structured_envelope(self):
        result = self._dispatch(action='not_a_real_action')
        self.assertEqual(result.get('error_code'), 'unknown_action')
        self.assertIn('Unknown spider_status action', result.get('error', ''))
        self.assertEqual(result.get('action'), 'not_a_real_action')
        self.assertEqual(
            result.get('valid_actions'),
            ['list', 'history', 'detail', 'search'],
        )

    def test_internal_error_catcher_returns_structured_envelope(self):
        # Force the generic exception path by passing a non-UUID item_id
        # (fails inside .get(id=item_id) with ValueError).
        result = self._dispatch(action='detail', item_id='not-a-uuid')
        self.assertEqual(result.get('error_code'), 'internal_error')
        self.assertEqual(result.get('action'), 'detail')
        self.assertIn('exception_type', result)


# ────────────────────────────────────────────────────────────────────────
# kb_tool — 5 sites
# ────────────────────────────────────────────────────────────────────────


class KbToolErrorEnvelopeTests(TestCase):
    """Envelope-shape tests for the 5 migrated kb_tool (kb_browse) paths."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _dispatch(self, **payload):
        return self.dispatcher._handle_kb_browse(
            'kb_tool', payload, None, 'test-trace-s2875-kb',
        )

    def test_chunks_missing_document_id_returns_structured_envelope(self):
        result = self._dispatch(action='chunks')
        self.assertEqual(result.get('error_code'), 'document_id_required')
        self.assertEqual(
            result.get('error'),
            'document_id required for chunks action',
        )

    def test_search_embeddings_missing_filters_returns_structured_envelope(self):
        result = self._dispatch(action='search_embeddings')
        self.assertEqual(result.get('error_code'), 'filters_required')
        self.assertEqual(
            result.get('error'),
            'query or content_type required for search_embeddings',
        )

    def test_semantic_search_missing_query_returns_structured_envelope(self):
        result = self._dispatch(action='semantic_search')
        self.assertEqual(result.get('error_code'), 'query_required')
        self.assertEqual(
            result.get('error'),
            'query is required for semantic_search',
        )

    def test_unknown_action_returns_structured_envelope(self):
        result = self._dispatch(action='not_a_valid_kb_action')
        self.assertEqual(result.get('error_code'), 'unknown_action')
        self.assertIn('Unknown kb_tool action', result.get('error', ''))
        self.assertEqual(result.get('action'), 'not_a_valid_kb_action')
        self.assertIn('semantic_search', result.get('valid_actions', []))


# ────────────────────────────────────────────────────────────────────────
# Cross-tool envelope-shape parity
# ────────────────────────────────────────────────────────────────────────


class CrossToolEnvelopeShapeParityTests(TestCase):
    """Every migrated site returns the S2874 envelope shape:

    * ``error`` present (human-readable string)
    * ``error_code`` present (machine-readable snake_case string)
    * NO ``success`` key (proposal was corrected during pre-code SIGN;
      S2874 does NOT include ``success: false``)
    """

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _all_error_responses(self):
        """Dispatch each of the 12 non-internal_error sites once."""
        return [
            # repo_tool (4 non-internal_error sites)
            self.dispatcher._handle_repo(
                'repo_tool', {'action': 'tree', 'path': 'manage.py'},
                None, 't1',
            ),
            self.dispatcher._handle_repo(
                'repo_tool', {'action': 'search', 'path': 'core/'},
                None, 't2',
            ),
            self.dispatcher._handle_repo(
                'repo_tool', {'action': 'nope'}, None, 't3',
            ),
            self.dispatcher._handle_repo(
                'repo_tool',
                {'action': 'read_file', 'path': '../../etc/passwd'},
                None, 't4',
            ),
            # spider_status_tool (5 non-internal_error sites)
            self.dispatcher._handle_spider_status(
                'spider_status_tool', {'action': 'history'}, None, 't5',
            ),
            self.dispatcher._handle_spider_status(
                'spider_status_tool', {'action': 'detail'}, None, 't6',
            ),
            self.dispatcher._handle_spider_status(
                'spider_status_tool',
                {'action': 'detail',
                 'item_id': '00000000-0000-0000-0000-000000000000'},
                None, 't7',
            ),
            self.dispatcher._handle_spider_status(
                'spider_status_tool', {'action': 'search'}, None, 't8',
            ),
            self.dispatcher._handle_spider_status(
                'spider_status_tool', {'action': 'nope'}, None, 't9',
            ),
            # kb_tool (4 non-internal_error sites)
            self.dispatcher._handle_kb_browse(
                'kb_tool', {'action': 'chunks'}, None, 't10',
            ),
            self.dispatcher._handle_kb_browse(
                'kb_tool', {'action': 'search_embeddings'}, None, 't11',
            ),
            self.dispatcher._handle_kb_browse(
                'kb_tool', {'action': 'semantic_search'}, None, 't12',
            ),
            self.dispatcher._handle_kb_browse(
                'kb_tool', {'action': 'nope'}, None, 't13',
            ),
        ]

    def test_every_migrated_site_has_error_key(self):
        for resp in self._all_error_responses():
            self.assertIn('error', resp, resp)
            self.assertIsInstance(resp['error'], str)
            self.assertTrue(resp['error'])

    def test_every_migrated_site_has_error_code_key(self):
        for resp in self._all_error_responses():
            self.assertIn('error_code', resp, resp)
            self.assertIsInstance(resp['error_code'], str)
            # snake_case check (no spaces, no uppercase)
            self.assertEqual(resp['error_code'], resp['error_code'].lower())
            self.assertNotIn(' ', resp['error_code'])

    def test_no_migrated_site_returns_success_key(self):
        """Q2 fold: S2874 envelope does NOT include ``success: false``."""
        for resp in self._all_error_responses():
            self.assertNotIn('success', resp, resp)
