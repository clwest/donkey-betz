"""
S2884 slate — cost_telemetry + newsletter structured error-envelope migration.

Seventh real handler migration wave in the S2876 backfill sunset arc
(Rigby Tool Gap Ledger #22). First file-completing slate after the
criticality-first cadence (S2879 → S2883): both
``td_handlers_agents.py`` (1 site) and ``td_handlers_newsletter.py``
(7 sites) EXIT the bare-``{'error': ...}``-return population in a
single PR. Post-S2884 file counts: agents.py = 0, newsletter.py = 0.

**8 sites across 2 handlers / 2 tool surfaces** — Rigby's Q1
pre-code routing-map (grounded via ``repo_tool.grep`` at HEAD)
established both files as single-surface, uniform-guard shape:

* ``_handle_cost_telemetry`` — ``cost_telemetry_tool``
  (``tool_dispatcher.py:416``). 1 site: L5026 ``unknown_action``
  (action not in {summary, top_agents, recent_calls}).
* ``_handle_newsletter`` + per-action helpers — ``newsletter_tool``
  (``tool_dispatcher.py:593``). 7 sites:

  - L44 ``_handle_newsletter`` unknown_action.
  - L85 ``_newsletter_prepare`` invalid_params (missing id).
  - L90 ``_newsletter_prepare`` not_found (Deliverable lookup miss).
  - L341 ``_newsletter_validate`` invalid_params.
  - L346 ``_newsletter_validate`` not_found.
  - L391 ``_newsletter_metrics`` invalid_params.
  - L396 ``_newsletter_metrics`` not_found.

**Helper-choice — all sites use ``_handler_error``:** taxonomy fit
per site was uniform-guard shape (unknown_action / invalid_params /
not_found), no broad-except paths in the population. No
``_tool_error('internal_error', ...)`` sites in this slate, unlike
S2883's Path 1 SPLIT.

**Ledger #13 adopter signal:** each file gets its own local
``_handler_error`` copy per Rigby's S2875 6-adopter gate on
``td_error.py`` extraction. Post-S2884 adopter count = 4
(``td_handlers_ops.py`` + ``td_handlers_governance.py`` +
``td_handlers_agents.py`` + ``td_handlers_newsletter.py``). Still
short of the 6-adopter extraction threshold — deferred to a
dedicated arc.

Sites tested (8 total):

* All 8 migrated to ``_handler_error`` — asserted via the shared
  ``_assert_migrated_envelope`` (imported from
  ``test_s2879_governance_ops_error_envelope``) to keep the
  contract single-source and force a compile-time break if the
  S2879 helper signature ever drifts.
* ``not_found`` cases pass a well-formed UUID that does not exist
  in the ``Deliverable`` table — exercises the real
  ``DoesNotExist`` catch without mocks.

Run::

    python manage.py test core.tests.test_s2884_agents_newsletter_error_envelope -v2
"""

import uuid

from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher
from core.tests.test_s2879_governance_ops_error_envelope import (
    _assert_migrated_envelope,
)


# ────────────────────────────────────────────────────────────────────────
# cost_telemetry_tool — 1 site
# ────────────────────────────────────────────────────────────────────────


class CostTelemetryToolMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for the S2884 ``_handle_cost_telemetry`` migration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync(
            'cost_telemetry_tool', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"cost_telemetry_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_unknown_action_returns_unknown_action(self):
        """L5026: action not in {summary, top_agents, recent_calls} → ``unknown_action``."""
        result = self._dispatch({'action': '__bogus_action_s2884__'})
        _assert_migrated_envelope(
            self, result,
            error_code='unknown_action',
            action='__bogus_action_s2884__',
        )


# ────────────────────────────────────────────────────────────────────────
# newsletter_tool — 7 sites
# ────────────────────────────────────────────────────────────────────────


class NewsletterToolMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for the S2884 ``_handle_newsletter`` + per-action migration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync(
            'newsletter_tool', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"newsletter_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    # ── top-level unknown_action (L44) ─────────────────────────────

    def test_unknown_action_returns_unknown_action(self):
        """L44: action not in the recognized set → ``unknown_action`` at dispatcher entrypoint."""
        result = self._dispatch({'action': '__bogus_action_s2884__'})
        _assert_migrated_envelope(
            self, result,
            error_code='unknown_action',
            action='__bogus_action_s2884__',
        )

    # ── prepare guards (L85 invalid_params, L90 not_found) ─────────

    def test_prepare_without_id_returns_invalid_params(self):
        """L85: ``prepare`` without ``id``/``deliverable_id`` → ``invalid_params``."""
        result = self._dispatch({'action': 'prepare'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='prepare',
        )

    def test_prepare_missing_deliverable_returns_not_found(self):
        """L90: ``prepare`` with a UUID that does not exist → ``not_found``."""
        missing_id = str(uuid.uuid4())
        result = self._dispatch({'action': 'prepare', 'id': missing_id})
        _assert_migrated_envelope(
            self, result,
            error_code='not_found',
            action='prepare',
        )

    # ── validate guards (L341 invalid_params, L346 not_found) ──────

    def test_validate_without_id_returns_invalid_params(self):
        """L341: ``validate`` without ``id``/``deliverable_id`` → ``invalid_params``."""
        result = self._dispatch({'action': 'validate'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='validate',
        )

    def test_validate_missing_deliverable_returns_not_found(self):
        """L346: ``validate`` with a UUID that does not exist → ``not_found``."""
        missing_id = str(uuid.uuid4())
        result = self._dispatch({'action': 'validate', 'id': missing_id})
        _assert_migrated_envelope(
            self, result,
            error_code='not_found',
            action='validate',
        )

    # ── metrics guards (L391 invalid_params, L396 not_found) ───────

    def test_metrics_without_id_returns_invalid_params(self):
        """L391: ``metrics`` without ``id``/``deliverable_id`` → ``invalid_params``."""
        result = self._dispatch({'action': 'metrics'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='metrics',
        )

    def test_metrics_missing_deliverable_returns_not_found(self):
        """L396: ``metrics`` with a UUID that does not exist → ``not_found``."""
        missing_id = str(uuid.uuid4())
        result = self._dispatch({'action': 'metrics', 'id': missing_id})
        _assert_migrated_envelope(
            self, result,
            error_code='not_found',
            action='metrics',
        )
