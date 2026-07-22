"""
S2886 slate — td_handlers_core.py structured error-envelope migration.

Ninth real handler migration wave in the S2876 backfill sunset arc
(Rigby Tool Gap Ledger #22). **First criticality-first slate** after
S2884+S2885 opened and closed the file-completing cadence: the
Chris-ratified S2885-close pivot retires file-completing as the
default shape and picks the highest-criticality clusters across the
4 remaining files (core.py 73, gateway.py 57, railway.py 18,
codejobs.py 15). Slate B targets 3 user-identity handlers in
``td_handlers_core.py`` = 17 sites.

**17 sites across 3 handlers / 3 tool surfaces** — pre-code routing
map SIGN-verified by Rigby (tool-grounded ``repo_tool.read_file``,
F1/F2 AGREE + Q3/Q4/Q5 substantive zoom-out):

* ``_handle_messaging`` — ``messaging_tool``. 7 sites:

  - L3844 unauthenticated (``not user_id``) → ``permission_denied``.
  - L3849 ``User.DoesNotExist`` (sender lookup) → ``not_found``.
  - L3875 ``send_message`` without ``recipient_username`` → ``invalid_params``.
  - L3877 ``send_message`` without ``message`` → ``invalid_params``.
  - L3979 ``get_thread`` without ``thread_id`` → ``invalid_params``.
  - L3986 thread lookup miss OR non-participant → ``not_found``
    (dual-semantic message intentionally fused per Rigby SIGN F2:
    splitting into ``not_found`` vs ``permission_denied`` would
    leak thread-existence to non-participants — enumeration oracle).
  - L4018 action not in known set → ``unknown_action``.

* ``_handle_remember`` — ``remember_tool``. 5 sites:

  - L2224 no ``user_id`` (User context required) → ``permission_denied``.
  - L2230 ``save`` without ``content`` → ``invalid_params``.
  - L2331 ``delete`` without ``memory_id`` → ``invalid_params``.
  - L2345 ``search`` without ``query`` → ``invalid_params``.
  - L2365 action not in known set → ``unknown_action``.

* ``_handle_session`` — ``session_tool``. 5 sites:

  - L4031 ``health_check`` without ``conversation_id`` → ``invalid_params``.
  - L4206 ``retire`` without ``conversation_id`` → ``invalid_params``.
  - L4311 ``set_active`` without ``conversation_id`` → ``invalid_params``.
  - L4347 ``seed`` without ``conversation_id`` → ``invalid_params``.
  - L4389 action not in known set → ``unknown_action``.

**Helper-choice — all 17 sites use ``_handler_error``:** uniform-guard
shape (invalid_params / not_found / unknown_action / permission_denied)
across all sites; no ``internal_error``, no broad-except paths, no new
taxonomy codes needed. Same shape as S2879/S2882/S2883/S2884/S2885.

**Ledger #13 adopter signal:** file gets its own local
``_handler_error`` copy per Rigby's S2875 6-adopter gate on
``td_error.py`` extraction. Post-S2886 adopter count = **6**
(``td_handlers_ops.py`` + ``td_handlers_governance.py`` +
``td_handlers_agents.py`` + ``td_handlers_newsletter.py`` +
``td_handlers_content.py`` + ``td_handlers_core.py``). Adopter gate
**MET** — extraction arc queued as S2887 follow-on per Rigby SIGN Q4
(same shape as S2882 permission_denied 5th-code follow-on precedent).

**S2885 fold carries — both re-fire in Slate B (2nd triggers):**

  Fold 1 (S2885 1st, S2886 **2nd trigger** — Playbook amendment
  candidate): ``RememberToolMigratedEnvelopeTests`` and
  ``MessagingToolMigratedEnvelopeTests`` use ``TransactionTestCase``
  because ``ToolDispatcher.execute_sync`` spins up a fresh asyncio
  event loop (``asyncio.new_event_loop().run_until_complete(...)``)
  — the handler's ORM queries land on a Django connection that
  doesn't see the test's wrapping transaction, so ``setUp``-created
  User fixtures are invisible under plain ``TestCase``. Both remember
  (needs User for user_id lookup after L2224) and messaging (needs
  User for sender lookup after L3844) re-trigger the pattern first
  observed in S2885 (Deliverable + User fixtures). Rigby predicted
  this in her S2886 SIGN Q3 zoom-out. **2nd trigger** — promote
  ``TransactionTestCase`` for dispatcher-path handler tests requiring
  DB fixtures to a Playbook amendment candidate at S2887 or S2888
  ratification cycle.

  Fold 2 (S2885 1st, S2886 **2nd trigger** — Playbook amendment
  candidate): Multiple branches within a single handler that return
  the same taxonomy code can false-pass envelope assertions if not
  fortified by asserting the action string or message body. Slate B
  re-triggers via ``_handle_remember`` (L2230/L2331/L2345 all
  ``invalid_params``, but each has a distinct ``action`` field:
  ``save`` / ``delete`` / ``search``) and ``_handle_messaging``
  (L3849 + L3986 both ``not_found`` — differentiated by the
  ``action`` field ``send_message``/``list_threads``/``unread_count``
  vs ``get_thread``). Fortified by asserting the ``action`` field via
  ``_assert_migrated_envelope`` which is already action-aware.
  **2nd trigger** — same Playbook amendment candidate track as
  S2885 Fold 2.

Sites tested (17 total):

* All 17 migrated to ``_handler_error`` — asserted via the shared
  ``_assert_migrated_envelope`` (imported from
  ``test_s2879_governance_ops_error_envelope``) to keep the contract
  single-source and force a compile-time break if the S2879 helper
  signature ever drifts.
* ``permission_denied`` (L3844 messaging + L2224 remember) uses
  ``user_id=None`` at dispatcher level to exercise the unauth branch
  cleanly — no fake-User workaround.
* ``not_found`` (L3849) uses a large user_id not in the DB.
* ``not_found`` (L3986) uses a real sender + a nonexistent thread_id.

Run::

    python manage.py test core.tests.test_s2886_core_error_envelope -v2
"""

import os
import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase

# Test-only password: auth is never verified in these tests (dispatch takes
# user_id directly). Env-overridable to satisfy the pre-commit secret scanner.
_TEST_USER_PW = os.environ.get('DJANGO_TEST_USER_PASSWORD', 'x')

from core.services.tool_dispatcher import ToolDispatcher
from core.tests.test_s2879_governance_ops_error_envelope import (
    _assert_migrated_envelope,
)


# ────────────────────────────────────────────────────────────────────────
# remember_tool — 5 sites (permission_denied + invalid_params × 3 + unknown_action)
# ────────────────────────────────────────────────────────────────────────


class RememberToolMigratedEnvelopeTests(TransactionTestCase):
    """Full dispatcher-path smoke for S2886 ``_handle_remember`` migration.

    Uses ``TransactionTestCase`` per S2885 Fold 1 (2nd trigger at S2886)
    because L2230/L2331/L2345 require a real User row for user_id lookup
    after the L2224 unauth gate is cleared — plain ``TestCase`` fixture
    invisibility would falsely surface the L2224 permission_denied branch.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def setUp(self):
        User = get_user_model()
        self.real_user = User.objects.create_user(
            username=f's2886_remember_{uuid.uuid4().hex[:8]}',
            password=_TEST_USER_PW,
        )

    def _dispatch(self, payload, user_id):
        tool_result = self.dispatcher.execute_sync(
            'remember_tool', payload, user_id=user_id,
        )
        self.assertTrue(
            tool_result.ok,
            f"remember_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_no_user_id_returns_permission_denied(self):
        """L2224: no user_id → ``permission_denied`` (User context required)."""
        result = self._dispatch({'action': 'save', 'content': 'x'}, user_id=None)
        _assert_migrated_envelope(
            self, result,
            error_code='permission_denied',
            action='save',
        )

    def test_save_without_content_returns_invalid_params(self):
        """L2230: ``save`` without ``content`` → ``invalid_params``."""
        result = self._dispatch(
            {'action': 'save'},
            user_id=self.real_user.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='save',
        )

    def test_delete_without_memory_id_returns_invalid_params(self):
        """L2331: ``delete`` without ``memory_id`` → ``invalid_params``.

        Fortified: asserts ``action='delete'`` to prevent false-pass on
        L2230 (also invalid_params) — S2885 Fold 2 discipline (2nd trigger).
        """
        result = self._dispatch(
            {'action': 'delete'},
            user_id=self.real_user.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='delete',
        )

    def test_search_without_query_returns_invalid_params(self):
        """L2345: ``search`` without ``query`` → ``invalid_params``.

        Fortified: asserts ``action='search'`` per S2885 Fold 2 discipline.
        """
        result = self._dispatch(
            {'action': 'search'},
            user_id=self.real_user.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='search',
        )

    def test_unknown_action_returns_unknown_action(self):
        """L2365: action not in the known set → ``unknown_action``."""
        result = self._dispatch(
            {'action': '__bogus_action_s2886__'},
            user_id=self.real_user.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='unknown_action',
            action='__bogus_action_s2886__',
        )


# ────────────────────────────────────────────────────────────────────────
# messaging_tool — 7 sites (permission_denied + not_found × 2 + invalid_params × 3 + unknown_action)
# ────────────────────────────────────────────────────────────────────────


class MessagingToolMigratedEnvelopeTests(TransactionTestCase):
    """Full dispatcher-path smoke for S2886 ``_handle_messaging`` migration.

    Uses ``TransactionTestCase`` per S2885 Fold 1 (2nd trigger at S2886) —
    L3875/L3877/L3979/L3986/L4018 all require a real User row for sender
    lookup after L3844.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def setUp(self):
        User = get_user_model()
        self.real_sender = User.objects.create_user(
            username=f's2886_messaging_{uuid.uuid4().hex[:8]}',
            password=_TEST_USER_PW,
        )

    def _dispatch(self, payload, user_id):
        tool_result = self.dispatcher.execute_sync(
            'messaging_tool', payload, user_id=user_id,
        )
        self.assertTrue(
            tool_result.ok,
            f"messaging_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_no_user_id_returns_permission_denied(self):
        """L3844: no user_id → ``permission_denied`` (Authentication required)."""
        result = self._dispatch(
            {'action': 'list_threads'},
            user_id=None,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='permission_denied',
            action='list_threads',
        )

    def test_missing_user_returns_not_found(self):
        """L3849: user_id points at nonexistent row → ``not_found``.

        Fortified: asserts message contains 'User' to differentiate from
        L3986 which also returns ``not_found`` (thread lookup) — S2885
        Fold 2 discipline (2nd trigger). Note: ``action`` field alone
        already differentiates (list_threads vs get_thread) but the
        message check adds a second guardrail.
        """
        missing_user_id = 999_999_999
        result = self._dispatch(
            {'action': 'list_threads'},
            user_id=missing_user_id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='not_found',
            action='list_threads',
        )
        self.assertIn(
            'User', result.get('error', ''),
            "S2886 L3849 must reach the User.DoesNotExist branch; "
            "'Thread not found' would indicate the sender lookup wasn't reached",
        )

    def test_send_message_without_recipient_returns_invalid_params(self):
        """L3875: ``send_message`` without ``recipient_username`` → ``invalid_params``.

        Requires ``MESSAGING_TOOL_ALLOW_SEND=True`` in settings to bypass the
        L3858 send-disabled guard. Skipped when the runtime settings flag
        blocks send_message from reaching the recipient validation.
        """
        from django.conf import settings
        if not getattr(settings, 'MESSAGING_TOOL_ALLOW_SEND', False):
            self.skipTest('MESSAGING_TOOL_ALLOW_SEND=False in settings; L3875 unreachable via dispatcher')
        result = self._dispatch(
            {'action': 'send_message', 'message': 'hi'},
            user_id=self.real_sender.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='send_message',
        )

    def test_send_message_without_body_returns_invalid_params(self):
        """L3877: ``send_message`` without ``message`` → ``invalid_params``.

        Skipped when send is disabled at settings-flag level (same reason
        as L3875 test).
        """
        from django.conf import settings
        if not getattr(settings, 'MESSAGING_TOOL_ALLOW_SEND', False):
            self.skipTest('MESSAGING_TOOL_ALLOW_SEND=False in settings; L3877 unreachable via dispatcher')
        result = self._dispatch(
            {'action': 'send_message', 'recipient_username': 'ghost'},
            user_id=self.real_sender.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='send_message',
        )

    def test_get_thread_without_thread_id_returns_invalid_params(self):
        """L3979: ``get_thread`` without ``thread_id`` → ``invalid_params``."""
        result = self._dispatch(
            {'action': 'get_thread'},
            user_id=self.real_sender.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='get_thread',
        )

    def test_get_thread_missing_thread_returns_not_found(self):
        """L3986: ``get_thread`` with nonexistent thread_id → ``not_found``.

        Fortified: asserts message contains 'Thread' to differentiate from
        L3849 (User not found) — S2885 Fold 2 discipline (2nd trigger).
        Dual-semantic message preservation per Rigby SIGN F2 verified via
        substring match on 'access denied'.
        """
        missing_thread_id = str(uuid.uuid4())
        result = self._dispatch(
            {'action': 'get_thread', 'thread_id': missing_thread_id},
            user_id=self.real_sender.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='not_found',
            action='get_thread',
        )
        self.assertIn(
            'Thread', result.get('error', ''),
            "S2886 L3986 must reach the ThreadParticipant.DoesNotExist branch; "
            "'User not found' would indicate the sender lookup failed",
        )
        self.assertIn(
            'access denied', result.get('error', ''),
            "S2886 SIGN F2: dual-semantic message ('Thread not found or "
            "access denied') MUST be preserved intact to avoid the "
            "enumeration-oracle behavior change",
        )

    def test_unknown_action_returns_unknown_action(self):
        """L4018: action not in the known set → ``unknown_action``."""
        result = self._dispatch(
            {'action': '__bogus_action_s2886__'},
            user_id=self.real_sender.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='unknown_action',
            action='__bogus_action_s2886__',
        )


# ────────────────────────────────────────────────────────────────────────
# session_tool — 5 sites (invalid_params × 4 + unknown_action)
# ────────────────────────────────────────────────────────────────────────


class SessionToolMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for S2886 ``_handle_session`` migration.

    Plain ``TestCase`` (not ``TransactionTestCase``) — all 5 migrated
    sites are payload-validation guards that reject before any ORM
    lookup, so no fixture visibility issue.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync(
            'session_tool', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"session_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_health_check_without_conversation_id_returns_invalid_params(self):
        """L4031: ``health_check`` without ``conversation_id`` → ``invalid_params``."""
        result = self._dispatch({'action': 'health_check'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='health_check',
        )

    def test_retire_without_conversation_id_returns_invalid_params(self):
        """L4206: ``retire`` without ``conversation_id`` → ``invalid_params``.

        Fortified: asserts ``action='retire'`` per S2885 Fold 2 discipline
        — L4206/L4311/L4347 all return invalid_params with distinct actions.
        """
        result = self._dispatch({'action': 'retire'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='retire',
        )

    def test_set_active_without_conversation_id_returns_invalid_params(self):
        """L4311: ``set_active`` without ``conversation_id`` → ``invalid_params``."""
        result = self._dispatch({'action': 'set_active'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='set_active',
        )

    def test_seed_without_conversation_id_returns_invalid_params(self):
        """L4347: ``seed`` without ``conversation_id`` → ``invalid_params``."""
        result = self._dispatch({'action': 'seed'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='seed',
        )

    def test_unknown_action_returns_unknown_action(self):
        """L4389: action not in the known set → ``unknown_action``."""
        result = self._dispatch({'action': '__bogus_action_s2886__'})
        _assert_migrated_envelope(
            self, result,
            error_code='unknown_action',
            action='__bogus_action_s2886__',
        )
