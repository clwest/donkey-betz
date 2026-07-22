"""
S2881 slate — ``autopilot_tool`` write-path structured error-envelope migration.

Fourth real handler migration wave in the S2876 backfill sunset arc
(Rigby Tool Gap Ledger #22). Continues the S2879/S2880 criticality-first
cadence into the contiguous write-path block inside ``_handle_autopilot``
at ``td_handlers_ops.py`` L3305-3533: 11 sites across four bounded
action-families dispatched via ``autopilot_tool``.

**Fold D 3rd-trigger event** (from S2880 close): the write-path actions
live inside ``_handle_autopilot`` (registered ``autopilot_tool`` at
``tool_dispatcher.py:538``), NOT ``_handle_ops``. Same routing-boundary
drift Rigby caught with the S2880 governance kill-switch cluster.
Pre-code framing at S2881 open labeled the slate as ``ops_tool``
handler-surface; corrected during test authoring after the dispatcher
returned ``unknown_action`` for all 11 rows.

* **outreach_* draft mutations** — ``outreach_approve`` /
  ``outreach_reject`` (2 sites, ``draft_id`` param-guard).
* **close_pack_* deal mutations** — ``close_pack_generate`` /
  ``close_pack_approve`` (2 sites, ``price`` / ``pack_id`` param-guard).
* **engagement_* event mutations** — ``engagement_classify`` /
  ``engagement_draft_reply`` / ``engagement_approve_reply`` /
  ``engagement_disqualify`` (4 sites, ``event_id`` / composite
  param-guard).
* **meeting_* pipeline mutations** — ``meeting_create`` /
  ``meeting_brief`` / ``meeting_recap`` (3 sites,
  ``scheduled_at`` / ``meeting_id`` param-guard).

Slate labeled per Fold D (from S2880 close): pure **(b) autopilot
engine-internal** — all 11 sites live inside ``_handle_autopilot`` and
dispatch via ``autopilot_tool``. Verified via
``tool_dispatcher.py:538`` registration.

Reuses the S2879 ``_handler_error(action, code, message, **fields)``
helper (no new helper introduced). All 11 sites are ``invalid_params``
per Rigby's 4-code taxonomy (missing-required-field guards).

Assertions follow the S2879/S2880 pattern via the shared
``_assert_migrated_envelope`` helper (imported to keep the contract
single-source and force a compile-time break if the S2879 helper
signature ever drifts).

Run::

    python manage.py test core.tests.test_s2881_ops_write_path_error_envelope -v2
"""

from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher
from core.tests.test_s2879_governance_ops_error_envelope import (
    _assert_migrated_envelope,
)


class WritePathMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for the S2881 autopilot_tool write-path slice."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        # All 11 write-path actions live inside ``_handle_autopilot`` and
        # dispatch via ``autopilot_tool``. Corrected from ``ops_tool``
        # at S2881 open (Fold D 3rd trigger — same routing-boundary
        # drift Rigby caught in the S2880 governance cluster). Verified
        # via ``tool_dispatcher.py:538`` registration.
        tool_result = self.dispatcher.execute_sync(
            'autopilot_tool', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"autopilot_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    # -- outreach_* ---------------------------------------------------

    def test_outreach_approve_without_draft_id_returns_invalid_params(self):
        """``outreach_approve`` requires a non-empty ``draft_id``."""
        result = self._dispatch({'action': 'outreach_approve'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='outreach_approve',
        )

    def test_outreach_reject_without_draft_id_returns_invalid_params(self):
        """``outreach_reject`` requires a non-empty ``draft_id``."""
        result = self._dispatch({'action': 'outreach_reject'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='outreach_reject',
        )

    # -- close_pack_* -------------------------------------------------

    def test_close_pack_generate_without_price_returns_invalid_params(self):
        """``close_pack_generate`` requires a non-empty ``price``."""
        result = self._dispatch({'action': 'close_pack_generate'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='close_pack_generate',
        )

    def test_close_pack_approve_without_pack_id_returns_invalid_params(self):
        """``close_pack_approve`` requires a non-empty ``pack_id``."""
        result = self._dispatch({'action': 'close_pack_approve'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='close_pack_approve',
        )

    # -- engagement_* -------------------------------------------------

    def test_engagement_classify_without_event_id_returns_invalid_params(self):
        """``engagement_classify`` requires both ``event_id`` and ``intent``."""
        result = self._dispatch({'action': 'engagement_classify'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='engagement_classify',
        )

    def test_engagement_draft_reply_without_event_id_returns_invalid_params(self):
        """``engagement_draft_reply`` requires both ``event_id`` and ``reply_text``."""
        result = self._dispatch({'action': 'engagement_draft_reply'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='engagement_draft_reply',
        )

    def test_engagement_approve_reply_without_event_id_returns_invalid_params(self):
        """``engagement_approve_reply`` requires a non-empty ``event_id``."""
        result = self._dispatch({'action': 'engagement_approve_reply'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='engagement_approve_reply',
        )

    def test_engagement_disqualify_without_event_id_returns_invalid_params(self):
        """``engagement_disqualify`` requires a non-empty ``event_id``."""
        result = self._dispatch({'action': 'engagement_disqualify'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='engagement_disqualify',
        )

    # -- meeting_* ----------------------------------------------------

    def test_meeting_create_without_scheduled_at_returns_invalid_params(self):
        """``meeting_create`` requires a non-empty ``scheduled_at``."""
        result = self._dispatch({'action': 'meeting_create'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='meeting_create',
        )

    def test_meeting_brief_without_meeting_id_returns_invalid_params(self):
        """``meeting_brief`` requires a non-empty ``meeting_id``."""
        result = self._dispatch({'action': 'meeting_brief'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='meeting_brief',
        )

    def test_meeting_recap_without_meeting_id_returns_invalid_params(self):
        """``meeting_recap`` requires a non-empty ``meeting_id``."""
        result = self._dispatch({'action': 'meeting_recap'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='meeting_recap',
        )
