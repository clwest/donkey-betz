"""
S2876 slate — Rigby Tool Gap Ledger #22 promote (1st trigger at S2875 close,
Rigby zoom-out fold).

Dispatcher-layer ``error_code`` backfill wrapper for legacy handlers that
return ``{'error': msg}`` without an ``error_code``. Solves the mixed-mode
migration friction observed in S2875 (17 sites migrated; N legacy handlers
remain) without forcing every legacy tool to migrate first.

Pre-code SIGN via Rigby (2026-07-21) folded two design refinements + three
mitigations:

* F1: backfill value is ``'legacy_error'`` (not ``'unknown_error'``) — clean
  signal to consumers that this dispatch came from a pre-migration handler,
  distinct from any future "truly unknown in migrated taxonomy" semantic.
* F2: truthy-error guard (``result.get('error')``) rather than presence-of-
  key alone — avoids backfilling on success dicts that reserve ``error`` as
  a nullable field.
* Mitigation #1+#2: rate-limited (60s per-tool) ``logger.warning`` with
  structured fields — visibility into remaining pre-migration surface area
  without log spam.
* Mitigation #3: inline sunset criteria comment + Ledger #22 backreference
  so a 6-month reviewer can grep the code and know when to remove the
  compat bridge.

Run::

    python manage.py test core.tests.test_s2876_dispatcher_error_code_backfill -v2
"""

import asyncio
import logging

from django.test import TestCase

from core.services import tool_dispatcher as td_module
from core.services.tool_dispatcher import ToolDispatcher


class _BackfillTestBase(TestCase):
    """Common fixture: dispatch a fake tool whose handler returns a canned
    dict, and inspect the resulting ToolResult.result."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()
        # S2876: clear per-tool rate-limit state between tests so the
        # WARNING breadcrumb assertions are deterministic regardless of
        # test-execution order.
        td_module._last_legacy_backfill_warning.clear()

    def _dispatch_with_handler_return(self, handler_return, tool_name='_s2876_fake_tool'):
        """Register a fake handler that returns handler_return, dispatch,
        and return the ToolResult."""
        self.dispatcher.register(tool_name, lambda name, payload, uid, tid: handler_return)
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                self.dispatcher.execute(
                    tool_name=tool_name,
                    payload={'action': 'test'},
                    user_id=None,
                    record_telemetry=False,
                )
            )
        finally:
            loop.close()
        return result


class LegacyBackfillCoreCases(_BackfillTestBase):
    """The five core backfill decision points."""

    def test_legacy_error_dict_gets_backfilled(self):
        """A handler returning {'error': 'boom'} without error_code gets
        backfilled with error_code='legacy_error'."""
        r = self._dispatch_with_handler_return({'error': 'boom'})
        self.assertTrue(r.ok)  # dispatch itself was successful
        self.assertEqual(r.result, {'error': 'boom', 'error_code': 'legacy_error'})

    def test_migrated_handler_error_code_preserved(self):
        """A migrated handler ({'error', 'error_code', ...}) passes through
        unchanged — backfill is idempotent."""
        r = self._dispatch_with_handler_return(
            {'error': 'nope', 'error_code': 'not_a_directory', 'path': '/x'}
        )
        self.assertEqual(
            r.result,
            {'error': 'nope', 'error_code': 'not_a_directory', 'path': '/x'},
        )

    def test_success_dict_no_error_key_untouched(self):
        """Success dicts (no 'error' key) do not gain an error_code field."""
        r = self._dispatch_with_handler_return({'ok': True, 'value': 42})
        assert r.result is not None
        self.assertNotIn('error_code', r.result)
        self.assertEqual(r.result, {'ok': True, 'value': 42})

    def test_falsy_error_none_skips_backfill(self):
        """F2 guard: handler reserving `error: None` as sentinel should
        NOT gain an error_code (truthy guard, not presence-of-key)."""
        r = self._dispatch_with_handler_return({'error': None, 'data': 'ok'})
        assert r.result is not None
        self.assertNotIn('error_code', r.result)

    def test_falsy_error_empty_string_skips_backfill(self):
        """F2 guard: `error: ''` also treated as sentinel — no backfill."""
        r = self._dispatch_with_handler_return({'error': '', 'data': 'ok'})
        assert r.result is not None
        self.assertNotIn('error_code', r.result)


class LegacyBackfillScopeCases(_BackfillTestBase):
    """F3 (non-dict) + F4 (nested error) scope guards."""

    def test_non_dict_return_untouched(self):
        """Handlers returning raw strings/lists/ints are not touched (the
        isinstance(result, dict) guard skips them cleanly)."""
        r_str = self._dispatch_with_handler_return('plain string result')
        self.assertEqual(r_str.result, 'plain string result')

        r_list = self._dispatch_with_handler_return([1, 2, 3])
        self.assertEqual(r_list.result, [1, 2, 3])

        r_int = self._dispatch_with_handler_return(42)
        self.assertEqual(r_int.result, 42)

    def test_nested_error_key_untouched(self):
        """F4: nested {result: {error: ...}} is a handler-domain shape.
        Backfill only touches top-level; nested payloads stay pristine."""
        r = self._dispatch_with_handler_return(
            {'status': 'ok', 'result': {'error': 'nested-only'}}
        )
        assert r.result is not None
        # No top-level error → no top-level error_code
        self.assertNotIn('error_code', r.result)
        # Nested error preserved verbatim, unmutated
        self.assertEqual(r.result['result'], {'error': 'nested-only'})


class OuterEnvelopeIsolationCases(_BackfillTestBase):
    """F5: dispatcher-level (outer) error_code vs handler-level (inner)
    error_code live on different planes — no collision."""

    def test_outer_error_code_is_none_on_handler_error_envelope(self):
        """Handler returning an error envelope still produces ok=True at
        the dispatcher level (dispatch succeeded), so ToolResult.error_code
        stays None. The backfilled 'legacy_error' lives inside result."""
        r = self._dispatch_with_handler_return({'error': 'legacy-boom'})
        self.assertTrue(r.ok)
        self.assertIsNone(r.error_code)  # outer envelope untouched
        self.assertEqual(r.result['error_code'], 'legacy_error')  # inner backfilled


class BreadcrumbLoggingCases(_BackfillTestBase):
    """Mitigation #1+#2 — rate-limited WARNING breadcrumb per-tool."""

    def test_warning_emitted_on_first_backfill(self):
        with self.assertLogs('core.services.tool_dispatcher', level='WARNING') as cm:
            self._dispatch_with_handler_return({'error': 'boom'}, tool_name='_s2876_a')
        matched = [m for m in cm.output if 'legacy_handler_error_envelope_missing_error_code' in m]
        self.assertEqual(len(matched), 1, f"expected 1 breadcrumb, got: {cm.output}")
        self.assertIn('tool=_s2876_a', matched[0])
        self.assertIn('action=test', matched[0])
        self.assertIn("error_code='legacy_error'", matched[0])

    def test_warning_rate_limited_per_tool(self):
        """Second dispatch of the same tool within the window does NOT
        re-emit the WARNING (per-tool rate limit)."""
        # First dispatch — emits
        with self.assertLogs('core.services.tool_dispatcher', level='WARNING') as cm1:
            self._dispatch_with_handler_return({'error': 'first'}, tool_name='_s2876_b')
        self.assertEqual(
            sum(1 for m in cm1.output if 'legacy_handler_error_envelope_missing_error_code' in m),
            1,
        )
        # Second dispatch — silenced by rate limit. Use a logger that
        # WILL fire at WARNING (root sentinel) so assertLogs has something
        # to capture, then assert the breadcrumb specifically is absent.
        logging.getLogger('core.services.tool_dispatcher').warning('sentinel to satisfy assertLogs')
        with self.assertLogs('core.services.tool_dispatcher', level='WARNING') as cm2:
            logging.getLogger('core.services.tool_dispatcher').warning('sentinel-pre')
            self._dispatch_with_handler_return({'error': 'second'}, tool_name='_s2876_b')
        matched2 = [m for m in cm2.output if 'legacy_handler_error_envelope_missing_error_code' in m]
        self.assertEqual(len(matched2), 0, f"expected 0 breadcrumbs (rate-limited), got: {cm2.output}")

    def test_warning_per_tool_independent(self):
        """Two different tools each get their own initial WARNING (rate
        limit is per-tool, not global)."""
        with self.assertLogs('core.services.tool_dispatcher', level='WARNING') as cm:
            self._dispatch_with_handler_return({'error': 'x'}, tool_name='_s2876_c')
            self._dispatch_with_handler_return({'error': 'y'}, tool_name='_s2876_d')
        matched = [m for m in cm.output if 'legacy_handler_error_envelope_missing_error_code' in m]
        self.assertEqual(len(matched), 2)
        self.assertTrue(any('tool=_s2876_c' in m for m in matched))
        self.assertTrue(any('tool=_s2876_d' in m for m in matched))

    def test_no_warning_on_migrated_handler(self):
        """Migrated envelopes ({'error', 'error_code'}) do NOT trigger the
        breadcrumb — backfill guard short-circuits before the log."""
        # Emit a sentinel WARNING so assertLogs has at least one record to
        # capture (assertLogs raises if nothing is logged at the level).
        with self.assertLogs('core.services.tool_dispatcher', level='WARNING') as cm:
            logging.getLogger('core.services.tool_dispatcher').warning('sentinel')
            self._dispatch_with_handler_return(
                {'error': 'boom', 'error_code': 'not_a_directory'},
                tool_name='_s2876_e',
            )
        matched = [m for m in cm.output if 'legacy_handler_error_envelope_missing_error_code' in m]
        self.assertEqual(len(matched), 0)

    def test_no_warning_on_success_dict(self):
        """Success dicts with no 'error' key don't trigger the breadcrumb."""
        with self.assertLogs('core.services.tool_dispatcher', level='WARNING') as cm:
            logging.getLogger('core.services.tool_dispatcher').warning('sentinel')
            self._dispatch_with_handler_return({'ok': True}, tool_name='_s2876_f')
        matched = [m for m in cm.output if 'legacy_handler_error_envelope_missing_error_code' in m]
        self.assertEqual(len(matched), 0)
