"""
S2885 slate — content_tool structured error-envelope migration.

Eighth real handler migration wave in the S2876 backfill sunset arc
(Rigby Tool Gap Ledger #22). Second file-completing slate after S2884
opened the file-completing cadence: ``td_handlers_content.py``
(13 sites) EXITS the bare-``{'error': ...}``-return population in a
single PR. Post-S2885 file counts: content.py = 0.

**13 sites across 5 handlers / 3 tool surfaces** — pre-code routing
map SIGN-verified by Rigby (tool-grounded ``repo_tool.grep`` +
``repo_tool.read_file``, all 5 dimensions AGREE):

* ``_handle_deliverable_initiative_link`` — ``deliverable_tool`` via
  ``_handle_deliverable_direct``. 4 sites:

  - L178 missing ``deliverable_id`` → ``invalid_params``.
  - L182 Deliverable.DoesNotExist → ``not_found``.
  - L186 missing ``initiative_id`` for ``link_initiative`` → ``invalid_params``.
  - L190 Initiative.DoesNotExist → ``not_found``.

* ``_handle_feedback`` — ``feedback_tool``. 1 site:

  - L3654 ``submit`` without ``comment`` → ``invalid_params``.

* ``_handle_content`` — ``content_tool`` (top-level dispatch). 1 site:

  - L4788 action not in known set → ``unknown_action``.

* ``_handle_bulk_archive`` — ``content_tool`` action=``bulk_archive``. 1 site:

  - L4821 all requested statuses reject published/archived → ``invalid_params``.

* ``_handle_bulk_archive_published`` — ``content_tool`` action=
  ``bulk_archive_published`` (staff-gated write path). 6 sites:

  - L4966 non-staff user → ``permission_denied`` (S2882 5th-code taxonomy
    reuse; legacy ``'status': 403`` field dropped per Rigby SIGN T1c).
  - L4971 ``types`` includes ``blog`` → ``invalid_params``.
  - L4976 missing ``categories`` → ``invalid_params``.
  - L4980 missing ``created_before`` → ``invalid_params``.
  - L4984 malformed ``created_before`` → ``invalid_params``.
  - L5046 execute without ``confirm=true`` → ``invalid_params`` (dry-run
    ``result`` preview preserved via ``**{k: v for k, v in result.items()
    if k != 'action'}`` spread — action key filtered to avoid TypeError
    collision with helper's positional ``action``).

**Helper-choice — all 13 sites use ``_handler_error``:** uniform-guard
shape (invalid_params / not_found / unknown_action / permission_denied)
across all sites; no ``internal_error``, no broad-except paths, no new
taxonomy codes needed. Contrast with S2883's Path 1 SPLIT.

**Ledger #13 adopter signal:** file gets its own local
``_handler_error`` copy per Rigby's S2875 6-adopter gate on
``td_error.py`` extraction. Post-S2885 adopter count = 5
(``td_handlers_ops.py`` + ``td_handlers_governance.py`` +
``td_handlers_agents.py`` + ``td_handlers_newsletter.py`` +
``td_handlers_content.py``). Now **1 short of** the 6-adopter
extraction threshold — Slate B is a candidate trigger.

**S2884 zoom-out fold carry:** Rigby's S2885 zoom-out (b) confirms
her S2884 concern that file-completing can leave the highest-volume /
riskiest files (core.py 73, gateway.py 57) for last. Chris-ratified
Slate B pivot: after S2885, revert to criticality-first grep across
remaining 4 files (core.py + gateway.py first), NOT continue
file-completing on codejobs.py (15).

Sites tested (13 total):

* All 13 migrated to ``_handler_error`` — asserted via the shared
  ``_assert_migrated_envelope`` (imported from
  ``test_s2879_governance_ops_error_envelope``) to keep the
  contract single-source and force a compile-time break if the
  S2879 helper signature ever drifts.
* ``not_found`` cases pass a well-formed UUID that does not exist
  in the target table — exercises the real ``DoesNotExist`` catch
  without mocks.
* ``permission_denied`` uses a real non-staff ``User`` row (no
  ``SimpleNamespace`` mock) — the real ORM path is what
  ``_handle_bulk_archive_published`` walks.

Run::

    python manage.py test core.tests.test_s2885_content_error_envelope -v2
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

# Note: DeliverableInitiativeLinkMigratedEnvelopeTests and
# ContentToolMigratedEnvelopeTests use ``TransactionTestCase`` because
# ``ToolDispatcher.execute_sync`` spins up a fresh asyncio event loop
# (``asyncio.new_event_loop().run_until_complete(...)``) — the handler's
# ORM queries land on a Django connection that doesn't see the test's
# wrapping transaction, so ``setUp``-created fixtures (real Deliverable,
# real staff/non-staff User) are invisible. ``TransactionTestCase``
# commits between setUp and the dispatched request so fixtures are
# visible to any connection. ``FeedbackToolMigratedEnvelopeTests`` and
# ``_assert_migrated_envelope`` don't need fixtures — plain ``TestCase``.


# ────────────────────────────────────────────────────────────────────────
# deliverable_tool — link_initiative / unlink_initiative — 4 sites
# ────────────────────────────────────────────────────────────────────────


class DeliverableInitiativeLinkMigratedEnvelopeTests(TransactionTestCase):
    """Full dispatcher-path smoke for S2885 ``_handle_deliverable_initiative_link``."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def setUp(self):
        # L186 + L190 tests need a real Deliverable to reach the initiative
        # check. Create per-test (TestCase wraps in a transaction that
        # rolls back, so no cross-test pollution).
        from core.models_deliverables import Deliverable
        self.real_deliverable = Deliverable.objects.create(
            title='s2885 link_initiative fixture',
            content='fixture body',
            deliverable_type='doc',
            category='test',
            status='draft',
        )

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync(
            'deliverable_tool', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"deliverable_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_link_initiative_missing_deliverable_id_returns_invalid_params(self):
        """L178: ``link_initiative`` without ``deliverable_id`` → ``invalid_params``."""
        result = self._dispatch({'action': 'link_initiative'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='link_initiative',
        )

    def test_link_initiative_missing_deliverable_returns_not_found(self):
        """L182: ``link_initiative`` with a UUID that does not exist → ``not_found``."""
        missing_id = str(uuid.uuid4())
        result = self._dispatch({'action': 'link_initiative', 'deliverable_id': missing_id})
        _assert_migrated_envelope(
            self, result,
            error_code='not_found',
            action='link_initiative',
        )

    def test_link_initiative_missing_initiative_id_returns_invalid_params(self):
        """L186: ``link_initiative`` with valid deliverable but no ``initiative_id`` → ``invalid_params``."""
        result = self._dispatch({
            'action': 'link_initiative',
            'deliverable_id': str(self.real_deliverable.id),
        })
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='link_initiative',
        )

    def test_link_initiative_missing_initiative_returns_not_found(self):
        """L190: ``link_initiative`` with valid deliverable, missing initiative → ``not_found``.

        Fortified: also asserts the error message mentions the missing
        ``initiative_id`` (not ``Deliverable``) to prevent a silent false
        pass if fixture visibility regresses and L182 is reached instead.
        """
        missing_initiative_id = str(uuid.uuid4())
        result = self._dispatch({
            'action': 'link_initiative',
            'deliverable_id': str(self.real_deliverable.id),
            'initiative_id': missing_initiative_id,
        })
        _assert_migrated_envelope(
            self, result,
            error_code='not_found',
            action='link_initiative',
        )
        self.assertIn(
            'Initiative', result.get('error', ''),
            "S2885 L190 must reach the Initiative.DoesNotExist branch; "
            "'Deliverable not found' would indicate the fixture didn't persist "
            "(TransactionTestCase visibility regression)",
        )


# ────────────────────────────────────────────────────────────────────────
# feedback_tool — submit guard — 1 site
# ────────────────────────────────────────────────────────────────────────


class FeedbackToolMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for S2885 ``_handle_feedback`` submit-guard migration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync(
            'feedback_tool', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"feedback_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_submit_without_comment_returns_invalid_params(self):
        """L3654: ``submit`` without ``comment`` → ``invalid_params``."""
        result = self._dispatch({'action': 'submit'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='submit',
        )


# ────────────────────────────────────────────────────────────────────────
# content_tool — top-level unknown + bulk_archive + bulk_archive_published — 8 sites
# ────────────────────────────────────────────────────────────────────────


class ContentToolMigratedEnvelopeTests(TransactionTestCase):
    """Full dispatcher-path smoke for S2885 ``content_tool`` migrations (unknown_action + bulk_archive + bulk_archive_published)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def setUp(self):
        # Non-staff user for L4966 permission_denied test.
        # Staff user for L4971+ tests that need to pass the admin gate.
        User = get_user_model()
        self.non_staff_user = User.objects.create_user(
            username=f's2885_non_staff_{uuid.uuid4().hex[:8]}',
            password=_TEST_USER_PW,
            is_staff=False,
        )
        self.staff_user = User.objects.create_user(
            username=f's2885_staff_{uuid.uuid4().hex[:8]}',
            password=_TEST_USER_PW,
            is_staff=True,
        )

    def _dispatch(self, payload, user_id):
        tool_result = self.dispatcher.execute_sync(
            'content_tool', payload, user_id=user_id,
        )
        self.assertTrue(
            tool_result.ok,
            f"content_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    # ── top-level unknown_action (L4788) ────────────────────────────

    def test_unknown_action_returns_unknown_action(self):
        """L4788: content_tool action not in the known set → ``unknown_action``."""
        result = self._dispatch(
            {'action': '__bogus_action_s2885__'},
            user_id=self.staff_user.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='unknown_action',
            action='__bogus_action_s2885__',
        )

    # ── bulk_archive constraint (L4821) ─────────────────────────────

    def test_bulk_archive_only_forbidden_statuses_returns_invalid_params(self):
        """L4821: bulk_archive with only published/archived statuses → ``invalid_params``."""
        result = self._dispatch(
            {'action': 'bulk_archive', 'statuses': ['published', 'archived']},
            user_id=self.staff_user.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='bulk_archive',
        )

    # ── bulk_archive_published guards (L4966-L5046) ─────────────────

    def test_bulk_archive_published_non_staff_returns_permission_denied(self):
        """L4966: non-staff user → ``permission_denied`` (legacy ``status: 403`` dropped)."""
        result = self._dispatch(
            {'action': 'bulk_archive_published'},
            user_id=self.non_staff_user.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='permission_denied',
            action='bulk_archive_published',
        )
        # SIGN T1c: legacy 'status' key MUST be dropped.
        self.assertNotIn(
            'status', result,
            "S2885 SIGN T1c: legacy 'status: 403' hint must be dropped from permission_denied envelope",
        )

    def test_bulk_archive_published_blog_type_returns_invalid_params(self):
        """L4971: ``types`` includes ``blog`` → ``invalid_params``."""
        result = self._dispatch(
            {'action': 'bulk_archive_published', 'types': ['blog']},
            user_id=self.staff_user.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='bulk_archive_published',
        )

    def test_bulk_archive_published_missing_categories_returns_invalid_params(self):
        """L4976: missing ``categories`` → ``invalid_params``."""
        result = self._dispatch(
            {'action': 'bulk_archive_published'},
            user_id=self.staff_user.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='bulk_archive_published',
        )

    def test_bulk_archive_published_missing_created_before_returns_invalid_params(self):
        """L4980: missing ``created_before`` → ``invalid_params``."""
        result = self._dispatch(
            {'action': 'bulk_archive_published', 'categories': ['initiative_completion']},
            user_id=self.staff_user.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='bulk_archive_published',
        )

    def test_bulk_archive_published_invalid_created_before_returns_invalid_params(self):
        """L4984: malformed ``created_before`` → ``invalid_params``."""
        result = self._dispatch(
            {
                'action': 'bulk_archive_published',
                'categories': ['initiative_completion'],
                'created_before': 'not-a-real-datetime',
            },
            user_id=self.staff_user.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='bulk_archive_published',
        )

    def test_bulk_archive_published_execute_without_confirm_returns_invalid_params(self):
        """L5046: execute (dry_run=false) without confirm → ``invalid_params`` + dry-run preview preserved."""
        result = self._dispatch(
            {
                'action': 'bulk_archive_published',
                'categories': ['initiative_completion'],
                'created_before': '2026-01-01T00:00:00Z',
                'dry_run': False,
                # confirm intentionally omitted
            },
            user_id=self.staff_user.id,
        )
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='bulk_archive_published',
        )
        # SIGN T1d: the dry-run ``result`` preview must be preserved
        # via **-spread (with 'action' key filtered to avoid TypeError).
        # The preview payload includes total_matching + cap + filters +
        # breakdown + sample_items — assert one representative key.
        self.assertIn(
            'total_matching', result,
            "S2885 SIGN T1d: **result spread must preserve dry-run preview keys "
            "(total_matching) alongside the error envelope",
        )
