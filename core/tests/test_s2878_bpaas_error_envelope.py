"""
S2878 slate — ``bpaas_tool`` structured error-envelope migration.

Migrated ``_handle_bpaas`` (``core/services/td_handlers_agents.py:6227``)
from bare ``{'success': False, 'error': msg}`` returns to the S2874
canonical shape ``{'success': False, 'error_code': <snake>, 'error':
msg, 'action': action}``. Picked because ``bpaas_tool.generate_close_pack``
was the only real (non-test-fixture) hit in ``django_debug.log`` grep of
the S2876 ``legacy_handler_error_envelope_missing_error_code`` breadcrumb.

Prior state: dispatched through S2876 backfill → ``error_code='legacy_error'``.
Post-S2878: emits concrete ``error_code`` values, backfill wrapper's
idempotent guard short-circuits before assigning ``legacy_error``.

Coverage: full ``ToolDispatcher.execute_sync`` path (matches the S2877
PA-surface smoke pattern). 5 rows — one per error-return site in
``_handle_bpaas``:

* L6237 → ``missing_required_params`` (action missing)
* L6249 → ``missing_required_params`` (create_project without workspace_id/packet)
* L6261 → ``missing_required_params`` (generate_close_pack without packet)
* L6273 → ``unknown_action``
* L6277 → ``handler_exception`` (uncaught exception in try block)

Pre-code SIGN via Rigby (2026-07-21, ``pa-e869c051b9fd4c0d``, 3 grounded
``repo_tool.read_file`` runs, not rubber-stamp) folded four refinements:

* F3: consolidated 5 proposed codes to 3 canonical codes — collapse the
  three "required param(s) absent" sites to a single
  ``missing_required_params`` value; human-readable specificity
  preserved in the ``error`` string.
* F4: this file replaces the ``bpaas_tool`` row previously living in
  ``LegacyBackfillPASurfaceTests`` (S2877). The re-home keeps the
  legacy suite as a truthful "still-legacy" scoreboard.
* F5 zoom-out (Rigby): breadcrumb-driven picks optimize frequency over
  blast radius; forward-carried to S2879 as criticality-first slate
  selector — not altering S2878 scope.

Assertions:

* ``error_code`` exact match (programmatic contract).
* ``error`` truthy (message present) — never full-message-text match,
  per S2877 zoom-out fold: message rewording should not fail this suite.

Run::

    python manage.py test core.tests.test_s2878_bpaas_error_envelope -v2
"""

from unittest.mock import patch

from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher


class BpaasToolMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke tests for the S2878 ``_handle_bpaas`` migration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        """Dispatch bpaas_tool via ``execute_sync``, return inner result dict."""
        tool_result = self.dispatcher.execute_sync('bpaas_tool', payload, user_id=1)
        self.assertTrue(
            tool_result.ok,
            f"bpaas_tool dispatcher-level failure: {tool_result.error_message}",
        )
        self.assertIsInstance(tool_result.result, dict)
        return tool_result.result

    def test_missing_action_returns_missing_required_params(self):
        """L6237: no ``action`` in payload."""
        result = self._dispatch({})
        self.assertEqual(result.get('error_code'), 'missing_required_params')
        self.assertTrue(result.get('error'))
        self.assertFalse(result.get('success'))

    def test_create_project_missing_workspace_and_packet_returns_missing_required_params(self):
        """L6249: ``create_project`` without ``workspace_id`` or ``packet``."""
        result = self._dispatch({'action': 'create_project'})
        self.assertEqual(result.get('error_code'), 'missing_required_params')
        self.assertTrue(result.get('error'))
        self.assertEqual(result.get('action'), 'create_project')

    def test_generate_close_pack_missing_packet_returns_missing_required_params(self):
        """L6261: ``generate_close_pack`` without ``packet``.

        This is the original S2876 F-VERIFIED probe (from
        ``LegacyBackfillPASurfaceTests`` in S2877, pre-migration it
        surfaced ``error_code='legacy_error'`` via backfill). Post-S2878
        it must surface the concrete ``missing_required_params``.
        """
        result = self._dispatch({'action': 'generate_close_pack', 'packet': {}})
        self.assertEqual(result.get('error_code'), 'missing_required_params')
        self.assertTrue(result.get('error'))
        self.assertEqual(result.get('action'), 'generate_close_pack')

    def test_unknown_action_returns_unknown_action(self):
        """L6273: ``action`` string not in the valid set."""
        result = self._dispatch({'action': '__bogus_action_s2878__'})
        self.assertEqual(result.get('error_code'), 'unknown_action')
        self.assertTrue(result.get('error'))
        self.assertEqual(result.get('action'), '__bogus_action_s2878__')

    def test_handler_exception_returns_handler_exception(self):
        """L6277: uncaught exception inside try block surfaces via fallback.

        Patch ``generate_close_pack`` at its import site inside the handler
        (function-scoped import at L6257) to raise a synthetic error, then
        dispatch a valid payload — the exception is caught by the outer
        try/except and re-emitted as the structured ``handler_exception``
        envelope.
        """
        with patch(
            'core.services.bpaas.packet_service.generate_close_pack',
            side_effect=RuntimeError('synthetic S2878 test failure'),
        ):
            result = self._dispatch(
                {'action': 'generate_close_pack', 'packet': {'nonempty': True}},
            )
        self.assertEqual(result.get('error_code'), 'handler_exception')
        self.assertTrue(result.get('error'))
        self.assertEqual(result.get('action'), 'generate_close_pack')
