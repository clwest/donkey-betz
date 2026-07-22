"""
S2879 slate — ``governance_tool`` + ``ops_tool`` critical-slice structured
error-envelope migration.

Second real handler migration wave in the S2876 backfill sunset arc
(Rigby Tool Gap Ledger #22). Follows the S2878 ``_handle_bpaas`` pilot;
picked criticality-first (Rigby F5 forward-carry) rather than
breadcrumb-first because ops failures compound during incident/debug
loops and governance is a small-volume trivial ship in the same PR.

Migrated sites use a new local ``_handler_error(action, code, message,
**fields)`` helper in each file that emits the S2874 canonical 4-key
envelope ``{success: False, error_code, error, action, **fields}``.
Distinct from the existing S2875 ``_tool_error`` helper (3-key,
``{error, error_code, **fields}``; 12 existing ops-gateway adopters)
to avoid silent contract drift on those call sites — reconciliation
deferred until Rigby's 6-adopter helper-extraction gate.

Coverage: full ``ToolDispatcher.execute_sync`` path (matches S2877 +
S2878 patterns). Taxonomy locked to Rigby's 4-code minimum:

* ``invalid_params`` — missing or invalid input
* ``not_found`` — target resource missing (unused in this slice)
* ``unknown_action`` — action string not in valid set
* ``dependency_missing`` — optional model/service import failed

Assertions:

* ``error_code`` exact match (programmatic contract).
* ``error`` truthy (message present) — never full-message-text match,
  per S2877 zoom-out fold: message rewording must not fail this suite.
* ``success`` is False on every migrated envelope.
* ``action`` present on every migrated envelope (S2878 F3 guardrail).

Run::

    python manage.py test core.tests.test_s2879_governance_ops_error_envelope -v2
"""

import sys
from unittest.mock import patch

from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher


def _assert_migrated_envelope(tc, result, *, error_code, action):
    """Shared assertion for the S2879 canonical envelope shape.

    Module-level free function (not a mixin) so pyright resolves the
    ``TestCase.assert*`` methods on the passed ``tc`` argument.
    """
    tc.assertIsInstance(result, dict)
    tc.assertFalse(result.get('success'), f"expected success=False; got {result!r}")
    tc.assertEqual(result.get('error_code'), error_code)
    tc.assertTrue(result.get('error'), f"expected truthy error message; got {result!r}")
    tc.assertEqual(result.get('action'), action)


class GovernanceToolMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for the S2879 ``_handle_zoom_out`` migration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync('zoom_out_tool', payload, user_id=1)
        self.assertTrue(
            tool_result.ok,
            f"zoom_out_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_unknown_action_returns_unknown_action(self):
        """L63 (post-migration): action string not in the valid set."""
        result = self._dispatch({'action': '__bogus_action_s2879__'})
        _assert_migrated_envelope(
            self, result,
            error_code='unknown_action',
            action='__bogus_action_s2879__',
        )


class OpsToolMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for the S2879 ``_handle_ops`` critical slice."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync('ops_tool', payload, user_id=1)
        self.assertTrue(
            tool_result.ok,
            f"ops_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_unknown_action_returns_unknown_action(self):
        """Dispatcher default: action not in the valid set."""
        result = self._dispatch({'action': '__bogus_action_s2879__'})
        _assert_migrated_envelope(
            self, result,
            error_code='unknown_action',
            action='__bogus_action_s2879__',
        )

    def test_focus_mode_update_without_config_updates_returns_invalid_params(self):
        """``focus_mode_update`` requires a non-empty ``config_updates`` dict."""
        result = self._dispatch({'action': 'focus_mode_update'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='focus_mode_update',
        )

    def test_celery_task_history_missing_dependency_returns_dependency_missing(self):
        """``celery_task_history`` ImportError guard for ``CeleryTaskEvent``."""
        # sys.modules[name] = None makes subsequent `from name import X` raise
        # ImportError — the documented way to simulate a missing optional dep.
        with patch.dict(sys.modules, {'core.models_celery_telemetry': None}):
            result = self._dispatch({'action': 'celery_task_history'})
        _assert_migrated_envelope(
            self, result,
            error_code='dependency_missing',
            action='celery_task_history',
        )

    def test_tenant_boundary_violations_missing_dependency_returns_dependency_missing(self):
        """``tenant_boundary_violations`` ImportError guard for ``OpsRunEvent``."""
        with patch.dict(sys.modules, {'core.models_ops_runs': None}):
            result = self._dispatch({'action': 'tenant_boundary_violations'})
        _assert_migrated_envelope(
            self, result,
            error_code='dependency_missing',
            action='tenant_boundary_violations',
        )

    def test_tenant_boundary_violations_invalid_failure_kind_returns_invalid_params(self):
        """``tenant_boundary_violations`` rejects ``failure_kind`` not in the enum."""
        result = self._dispatch({
            'action': 'tenant_boundary_violations',
            'failure_kind': '__bogus_kind_s2879__',
        })
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='tenant_boundary_violations',
        )

    def test_staleness_warnings_missing_dependency_returns_dependency_missing(self):
        """``staleness_warnings`` ImportError guard for ``OpsRunEvent``."""
        with patch.dict(sys.modules, {'core.models_ops_runs': None}):
            result = self._dispatch({'action': 'staleness_warnings'})
        _assert_migrated_envelope(
            self, result,
            error_code='dependency_missing',
            action='staleness_warnings',
        )

    def test_staleness_warnings_invalid_verdict_returns_invalid_params(self):
        """``staleness_warnings`` rejects ``verdict`` not in the enum."""
        result = self._dispatch({
            'action': 'staleness_warnings',
            'verdict': '__bogus_verdict_s2879__',
        })
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='staleness_warnings',
        )
