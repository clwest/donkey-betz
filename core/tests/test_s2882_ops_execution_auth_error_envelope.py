"""
S2882 slate — ``ops_tool`` EXECUTION + AUTH structured error-envelope migration.

Fifth real handler migration wave in the S2876 backfill sunset arc
(Rigby Tool Gap Ledger #22). Continues the S2879/S2880/S2881
criticality-first cadence into the low-Fold-D-risk cluster: 4 sites
across two clusters, all dispatched via ``ops_tool`` → ``_handle_ops``
(native surface, single tool, no per-method routing verification
required — contrasts with the deferred Slate 3 which spans 4 dedicated
tools).

**Fold D routing (verified — mid-slate correction after 4th-trigger event):**

* ``_ops_execution_detail`` — reached via ``ops_tool`` action
  ``execution_detail`` (dispatched at ``_handle_ops`` L358-360). Verified
  via ``tool_dispatcher.py:519`` registration.
* ``_authorize_staff`` — inner helper inside ``_handle_workspace_budget``
  (NOT ``_handle_ops``), called from ``set_default_cap`` and
  ``backfill_defaults`` action branches. Dispatched via
  ``workspace_budget_tool`` at ``tool_dispatcher.py:542``.

**Fold D 4th trigger:** Pre-code SIGN framed both clusters as ``ops_tool``
surface; test dispatcher initially routed AUTH through ``ops_tool`` and
got ``unknown_action``. Same routing-boundary drift Rigby caught in
S2880 (governance → governance_tool) and S2881 (write-path →
autopilot_tool). PLAYBOOK-6.10.10 amendment candidate re-triggered.

Sites migrated (4 total):

* **EXECUTION cluster** — ``_ops_execution_detail`` param-guard +
  not-found (2 sites, ``invalid_params`` + ``not_found``).
* **AUTH cluster** — ``_authorize_staff`` missing-auth +
  actor-not-found (2 sites, ``invalid_params`` + ``not_found``).

Not migrated in Slate 2 (deferred, taxonomy gap): ``_authorize_staff``
not-staff branch. The 4-code taxonomy (``invalid_params`` /
``not_found`` / ``unknown_action`` / ``dependency_missing``) has no
``permission_denied`` code; mapping question is a Rigby SIGN candidate.

Reuses the S2879 ``_handler_error(action, code, message, **fields)``
helper (no new helper introduced). Assertions follow the S2879/S2880/S2881
pattern via the shared ``_assert_migrated_envelope`` helper (imported to
keep the contract single-source and force a compile-time break if the
S2879 helper signature ever drifts).

Run::

    python manage.py test core.tests.test_s2882_ops_execution_auth_error_envelope -v2
"""

from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher
from core.tests.test_s2879_governance_ops_error_envelope import (
    _assert_migrated_envelope,
)


class ExecutionAuthMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for the S2882 ops_tool EXECUTION+AUTH slice."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch_ops(self, payload):
        """Dispatch via ``ops_tool`` (registered at ``tool_dispatcher.py:519``)."""
        tool_result = self.dispatcher.execute_sync(
            'ops_tool', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"ops_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    # -- _ops_execution_detail (action=execution_detail) ---------------

    def test_execution_detail_without_execution_id_returns_invalid_params(self):
        """``execution_detail`` requires a non-empty ``execution_id``."""
        result = self._dispatch_ops({'action': 'execution_detail'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='execution_detail',
        )

    def test_execution_detail_unknown_id_returns_not_found(self):
        """``execution_detail`` returns ``not_found`` for missing ``AgentExecution``."""
        # A UUID that will not exist. AgentExecution.id is a UUID PK; the
        # helper's DoesNotExist path is the site under test.
        result = self._dispatch_ops({
            'action': 'execution_detail',
            'execution_id': '00000000-0000-0000-0000-000000000000',
        })
        _assert_migrated_envelope(
            self, result,
            error_code='not_found',
            action='execution_detail',
        )
        self.assertEqual(
            result.get('execution_id'),
            '00000000-0000-0000-0000-000000000000',
            "not_found envelope must echo the requested execution_id",
        )

    # -- _authorize_staff (via workspace_budget_tool set_default_cap) --

    def _dispatch_budget(self, payload, user_id):
        """Dispatch via ``workspace_budget_tool`` (registered at ``tool_dispatcher.py:542``).

        The AUTH cluster's ``_authorize_staff`` helper lives inside
        ``_handle_workspace_budget``, not ``_handle_ops``. Corrected
        mid-slate after Fold D 4th-trigger event.
        """
        tool_result = self.dispatcher.execute_sync(
            'workspace_budget_tool', payload, user_id=user_id,
        )
        self.assertTrue(
            tool_result.ok,
            f"workspace_budget_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_set_default_cap_without_user_returns_invalid_params(self):
        """``_authorize_staff`` returns ``invalid_params`` when user_id is None."""
        result = self._dispatch_budget(
            {'action': 'set_default_cap', 'daily_cap_usd': 5.0},
            user_id=None,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='set_default_cap',
        )

    def test_set_default_cap_unknown_actor_returns_not_found(self):
        """``_authorize_staff`` returns ``not_found`` when actor user_id does not exist."""
        User = get_user_model()
        existing_max = User.objects.order_by('-id').values_list('id', flat=True).first()
        missing_id = (existing_max or 0) + 999_999

        result = self._dispatch_budget(
            {'action': 'set_default_cap', 'daily_cap_usd': 5.0},
            user_id=missing_id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='not_found',
            action='set_default_cap',
        )
        self.assertEqual(
            result.get('user_id'),
            missing_id,
            "not_found envelope must echo the requested user_id",
        )

    def test_set_default_cap_non_staff_returns_permission_denied(self):
        """``_authorize_staff`` returns ``permission_denied`` for non-staff actor.

        S2882 close follow-on: 5th taxonomy code added so the not-staff
        deny branch gets a structured envelope. Chris D-verdict per
        Rigby SIGN zoom-out (a).

        Mocks ``User.objects.get`` because ``TestCase`` transactions
        are not visible to the dispatcher's async ORM connection —
        a real created actor would return DoesNotExist and short-
        circuit to the ``not_found`` branch instead of exercising
        the ``is_staff`` check.
        """
        User = get_user_model()
        non_staff_actor = SimpleNamespace(id=99_991, is_staff=False)

        with patch.object(User.objects, 'get', return_value=non_staff_actor):
            result = self._dispatch_budget(
                {'action': 'set_default_cap', 'daily_cap_usd': 5.0},
                user_id=99_991,
            )
        _assert_migrated_envelope(
            self, result,
            error_code='permission_denied',
            action='set_default_cap',
        )
        self.assertEqual(
            result.get('user_id'),
            99_991,
            "permission_denied envelope must echo the requested user_id",
        )
