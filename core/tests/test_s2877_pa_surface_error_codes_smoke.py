"""
S2877 slate — PA-surface `error_code` smoke suite (S2874 1st-trigger promoted).

Prior-session tests exercise migrated handlers *directly* via
``dispatcher._handle_<x>()`` — they bypass the full ``_execute_inner`` path
and therefore never touch the S2876 dispatcher-layer backfill wrapper. This
suite dispatches through ``ToolDispatcher.execute_sync``, exercising the
whole PA-tool surface as PA callers see it:

* migrated handlers (S2874 read-file paging + S2875 read-path envelope
  migration) must pass their concrete ``error_code`` through unchanged;
* legacy handlers (still returning bare ``{'error': msg}``) must have
  ``error_code='legacy_error'`` backfilled by the S2876 wrapper;
* dispatcher-level failures (e.g. unknown tool name) must surface at the
  *outer* ``ToolResult.error_code`` field, distinct from inner handler
  error fields.

Pre-code SIGN via Rigby (2026-07-21, 4 grounded ``repo_tool`` runs, not
rubber-stamp) folded five refinements into the design:

* F1: ``execute_sync`` returns ``ToolResult(ok=True, result={error,
  error_code, ...})`` on handler-level errors — verified against
  ``tool_dispatcher.py`` L820–887 (backfill) + L920–929 (wrap).
* F2: two-class split (migrated / backfill) plus a small third class for
  the dispatcher-level branch — cleaner "which contract are we proving?"
  attribution than one-class-per-tool.
* F3: 1-row backfill sample is a weak claim against the 39-file
  bare-``{'error':msg}`` population Rigby enumerated; adding
  ``newsletter_tool`` + ``ops_tool`` bogus-action rows proves the
  wrapper fires across multiple legacy handler modules.
* F4: no ``assertLogs`` on the S2876 breadcrumb — the WARNING is
  gated by ``_last_legacy_backfill_warning`` (module-global map), which
  would make the suite order-dependent and flaky under parallel test
  runs. Deterministic-only.
* Zoom-out folds: (row 8) use ``00000000-0000-0000-0000-000000000000``
  for the bogus-UUID fixture — stable across environments; (all rows)
  assert only ``error_code`` value + ``error`` truthiness, never full
  error-message text — a message rewording should not fail this suite.

**S2876 sunset guardrail:** when S2876 backfill wrapper is removed
(all handlers migrated OR breadcrumb <1% for 14d, per sunset criteria
near ``_last_legacy_backfill_warning`` in ``tool_dispatcher.py``),
delete the entire ``LegacyBackfillPASurfaceTests`` class in the same
PR — the migrated handlers in question will start emitting their own
concrete ``error_code`` values, so the tests as-written will start
failing on strict equality.

Run::

    python manage.py test core.tests.test_s2877_pa_surface_error_codes_smoke -v2
"""

from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher, ToolErrorCode


# ────────────────────────────────────────────────────────────────────────
# Migrated handlers (S2874 + S2875) — concrete error_code passes through
# ────────────────────────────────────────────────────────────────────────


class MigratedHandlerPASurfaceTests(TestCase):
    """Full dispatcher-path smoke tests for S2874 + S2875 migrated handlers.

    All 14 rows dispatch through ``execute_sync``, unwrap the inner result
    dict, and assert the exact ``error_code`` set by the handler. The
    S2876 backfill wrapper *must not* touch these — idempotent guard on
    ``error_code`` presence should short-circuit before the backfill
    assigns ``legacy_error``.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, tool_name, payload):
        """Dispatch via full ``execute_sync`` path, return inner result dict."""
        tool_result = self.dispatcher.execute_sync(tool_name, payload, user_id=1)
        self.assertTrue(
            tool_result.ok,
            f"{tool_name} dispatcher-level failure: {tool_result.error_message}",
        )
        self.assertIsInstance(tool_result.result, dict)
        return tool_result.result

    # ── S2874 — repo_tool.read_file paging (1 row) ─────────────────────

    def test_repo_read_file_oversize_returns_file_too_large(self):
        """S2874 opt-in: >500KB without allow_large → 'file_too_large'."""
        result = self._dispatch(
            'repo_tool',
            {'action': 'read_file', 'path': 'core/models_unified_system.py'},
        )
        self.assertEqual(result.get('error_code'), 'file_too_large')
        self.assertTrue(result.get('error'))

    # ── S2875 — repo_tool (4 rows) ────────────────────────────────────

    def test_repo_tree_on_file_returns_not_a_directory(self):
        result = self._dispatch(
            'repo_tool', {'action': 'tree', 'path': 'manage.py'},
        )
        self.assertEqual(result.get('error_code'), 'not_a_directory')
        self.assertTrue(result.get('error'))

    def test_repo_search_missing_query_returns_query_required(self):
        result = self._dispatch(
            'repo_tool', {'action': 'search', 'path': 'core/'},
        )
        self.assertEqual(result.get('error_code'), 'query_required')
        self.assertTrue(result.get('error'))

    def test_repo_unknown_action_returns_unknown_action(self):
        result = self._dispatch(
            'repo_tool', {'action': '__bogus_action_s2877__'},
        )
        self.assertEqual(result.get('error_code'), 'unknown_action')
        self.assertTrue(result.get('error'))

    def test_repo_read_file_path_traversal_returns_value_error(self):
        """`..` escape past project root triggers _safe_path ValueError."""
        result = self._dispatch(
            'repo_tool',
            {'action': 'read_file', 'path': '../../../../etc/passwd'},
        )
        self.assertEqual(result.get('error_code'), 'value_error')
        self.assertTrue(result.get('error'))

    # ── S2875 — spider_status_tool (5 rows) ───────────────────────────

    def test_spider_status_history_missing_name_returns_spider_name_required(self):
        result = self._dispatch(
            'spider_status_tool', {'action': 'history'},
        )
        self.assertEqual(result.get('error_code'), 'spider_name_required')
        self.assertTrue(result.get('error'))

    def test_spider_status_detail_missing_id_returns_item_id_required(self):
        result = self._dispatch(
            'spider_status_tool', {'action': 'detail'},
        )
        self.assertEqual(result.get('error_code'), 'item_id_required')
        self.assertTrue(result.get('error'))

    def test_spider_status_detail_bogus_uuid_returns_item_not_found(self):
        """Bogus UUID is deterministic across environments — not env-dependent."""
        result = self._dispatch(
            'spider_status_tool',
            {
                'action': 'detail',
                'item_id': '00000000-0000-0000-0000-000000000000',
            },
        )
        self.assertEqual(result.get('error_code'), 'item_not_found')
        self.assertTrue(result.get('error'))

    def test_spider_status_search_no_filters_returns_filters_required(self):
        result = self._dispatch(
            'spider_status_tool', {'action': 'search'},
        )
        self.assertEqual(result.get('error_code'), 'filters_required')
        self.assertTrue(result.get('error'))

    def test_spider_status_unknown_action_returns_unknown_action(self):
        result = self._dispatch(
            'spider_status_tool', {'action': '__bogus_action_s2877__'},
        )
        self.assertEqual(result.get('error_code'), 'unknown_action')
        self.assertTrue(result.get('error'))

    # ── S2875 — kb_tool (4 rows) ──────────────────────────────────────

    def test_kb_chunks_missing_id_returns_document_id_required(self):
        result = self._dispatch(
            'kb_tool', {'action': 'chunks'},
        )
        self.assertEqual(result.get('error_code'), 'document_id_required')
        self.assertTrue(result.get('error'))

    def test_kb_search_embeddings_no_filters_returns_filters_required(self):
        result = self._dispatch(
            'kb_tool', {'action': 'search_embeddings'},
        )
        self.assertEqual(result.get('error_code'), 'filters_required')
        self.assertTrue(result.get('error'))

    def test_kb_semantic_search_missing_query_returns_query_required(self):
        result = self._dispatch(
            'kb_tool', {'action': 'semantic_search'},
        )
        self.assertEqual(result.get('error_code'), 'query_required')
        self.assertTrue(result.get('error'))

    def test_kb_unknown_action_returns_unknown_action(self):
        result = self._dispatch(
            'kb_tool', {'action': '__bogus_action_s2877__'},
        )
        self.assertEqual(result.get('error_code'), 'unknown_action')
        self.assertTrue(result.get('error'))


# ────────────────────────────────────────────────────────────────────────
# Legacy backfill (S2876) — DELETE THIS CLASS AFTER S2876 SUNSET
# ────────────────────────────────────────────────────────────────────────


class LegacyBackfillPASurfaceTests(TestCase):
    """Full dispatcher-path smoke tests for the S2876 backfill wrapper.

    ⚠️  **DELETE THIS ENTIRE CLASS AFTER S2876 SUNSET.**

    Sunset criteria (see comment near ``_last_legacy_backfill_warning``
    in ``core/services/tool_dispatcher.py``): all handlers emit their
    own ``error_code`` on error envelopes, OR the backfill breadcrumb
    fires < 1% of total dispatches for 14 consecutive days.

    When those criteria are met, ``ops_tool`` / ``newsletter_tool`` /
    ``bpaas_tool`` will emit concrete codes and these ``legacy_error``
    equality assertions will fail — delete the class as part of the
    sunset PR rather than migrating the assertions.

    Rigby enumerated the current legacy population (S2877 pre-code
    SIGN, ``repo_tool.search query="return {'error':"``): 39 files
    across ``core/services/`` still return bare ``{'error': msg}``.
    Handlers picked for the smoke matrix:

    * ``newsletter_tool.<bogus>`` — proves backfill fires across
      handler module boundaries (``td_handlers_newsletter.py:44``)

    Prior rows retired as their handlers were migrated:

    * ``bpaas_tool.generate_close_pack`` — S2876 F-VERIFIED fixture;
      re-homed to ``test_s2878_bpaas_error_envelope.py`` when
      ``_handle_bpaas`` migrated to the S2874 shape in S2878.
    * ``ops_tool.<bogus>`` — S2877 dispatcher-default row; re-homed to
      ``test_s2879_governance_ops_error_envelope.py`` when the ops
      unknown-action default at ``td_handlers_ops.py:397`` migrated to
      the S2874 shape in S2879 (governance + ops critical slice).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, tool_name, payload):
        tool_result = self.dispatcher.execute_sync(tool_name, payload, user_id=1)
        self.assertTrue(
            tool_result.ok,
            f"{tool_name} dispatcher-level failure: {tool_result.error_message}",
        )
        self.assertIsInstance(tool_result.result, dict)
        return tool_result.result

    def test_newsletter_unknown_action_backfilled(self):
        """Proves backfill fires from td_handlers_newsletter.py:44 site."""
        result = self._dispatch(
            'newsletter_tool', {'action': '__bogus_action_s2877__'},
        )
        self.assertEqual(result.get('error_code'), 'legacy_error')
        self.assertTrue(result.get('error'))


# ────────────────────────────────────────────────────────────────────────
# Dispatcher-level envelope (unknown tool) — the OTHER envelope plane
# ────────────────────────────────────────────────────────────────────────


class DispatcherEnvelopeTests(TestCase):
    """Proves the *outer* ``ToolResult`` envelope surfaces dispatcher-level
    failures via ``ok=False`` + ``error_code`` set to a
    :class:`ToolErrorCode` enum value.

    Distinct from the handler-error inner envelope: consumers keying only
    on ``result.result.get('error_code')`` (as taught by the migrated /
    backfill paths above) would miss dispatcher errors entirely. This
    single row makes the split explicit as part of the contract this
    suite documents.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def test_unknown_tool_returns_tool_not_found_outer_envelope(self):
        tool_result = self.dispatcher.execute_sync(
            '__nonexistent_tool_s2877__', {}, user_id=1,
        )
        self.assertFalse(tool_result.ok)
        self.assertEqual(tool_result.error_code, ToolErrorCode.TOOL_NOT_FOUND)
        self.assertTrue(tool_result.error_message)
        self.assertIsNone(tool_result.result)
