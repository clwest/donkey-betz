"""
S2880 slate — ``ops_tool`` remainder critical-slice structured
error-envelope migration.

Third real handler migration wave in the S2876 backfill sunset arc
(Rigby Tool Gap Ledger #22). Continues the S2879 criticality-first
cadence into three additional bounded slices of ``td_handlers_ops.py``:

* **Kill-switch / mode-change actions** (``governance_set_mode`` /
  ``governance_kill_switch`` / ``governance_deactivate_switch``) —
  worst incident-loop blast radius; 3 sites.
* **Scheduled-task enable/disable** — 2 sites (missing task id +
  target not found).
* **Ops-digest post + local unknown-action fallback** — 2 sites.

Reuses the S2879 ``_handler_error(action, code, message, **fields)``
helper (no new helper introduced). Taxonomy locked to Rigby's 4-code
minimum:

* ``invalid_params`` — missing or invalid input
* ``not_found`` — target resource missing
* ``unknown_action`` — action string not in valid set
* ``dependency_missing`` — optional model/service import failed
  (unused in this slice)

Assertions follow the S2879 pattern via the shared
``_assert_migrated_envelope`` helper (imported to keep the contract
single-source and force a compile-time break if the S2879 helper
signature ever drifts).

Run::

    python manage.py test core.tests.test_s2880_ops_remainder_error_envelope -v2
"""

from django.test import TestCase
from django_celery_beat.models import PeriodicTask

from core.services.tool_dispatcher import ToolDispatcher
from core.tests.test_s2879_governance_ops_error_envelope import (
    _assert_migrated_envelope,
)


class KillSwitchMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for the S2880 governance kill-switch slice."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        # governance_* actions live inside ``_handle_autopilot`` (dispatched
        # via ``autopilot_tool``), not ``_handle_ops``. Verified S2880 open.
        tool_result = self.dispatcher.execute_sync(
            'autopilot_tool', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"autopilot_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_governance_set_mode_without_mode_returns_invalid_params(self):
        """``governance_set_mode`` requires a non-empty ``mode`` string."""
        result = self._dispatch({'action': 'governance_set_mode'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='governance_set_mode',
        )

    def test_governance_kill_switch_without_target_returns_invalid_params(self):
        """``governance_kill_switch`` requires a non-empty ``target`` string."""
        result = self._dispatch({'action': 'governance_kill_switch'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='governance_kill_switch',
        )

    def test_governance_deactivate_switch_without_switch_id_returns_invalid_params(self):
        """``governance_deactivate_switch`` requires a non-empty ``switch_id``."""
        result = self._dispatch({'action': 'governance_deactivate_switch'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='governance_deactivate_switch',
        )


class ScheduledTasksMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for the S2880 scheduled_tasks_tool slice."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync(
            'scheduled_tasks_tool', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"scheduled_tasks_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_enable_without_task_id_returns_invalid_params(self):
        """``enable`` requires either ``task_id`` or ``name``."""
        result = self._dispatch({'action': 'enable'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='enable',
        )

    def test_disable_missing_task_returns_not_found(self):
        """``disable`` against a non-existent task returns ``not_found``.

        Uses a name that cannot exist as either a beat-entry name or a
        numeric primary key.
        """
        bogus = '__nonexistent_task_s2880__'
        # Guard: ensure it really doesn't exist so the test is meaningful.
        self.assertFalse(
            PeriodicTask.objects.filter(name=bogus).exists(),
            f"test fixture leak: task {bogus!r} unexpectedly exists",
        )
        result = self._dispatch({'action': 'disable', 'task_id': bogus})
        _assert_migrated_envelope(
            self, result,
            error_code='not_found',
            action='disable',
        )


class OpsDigestMigratedEnvelopeTests(TestCase):
    """Full dispatcher-path smoke for the S2880 ops_digest_tool slice."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dispatcher = ToolDispatcher()

    def _dispatch(self, payload):
        tool_result = self.dispatcher.execute_sync(
            'ops_digest_tool', payload, user_id=1,
        )
        self.assertTrue(
            tool_result.ok,
            f"ops_digest_tool dispatcher-level failure: {tool_result.error_message}",
        )
        return tool_result.result

    def test_post_without_conversation_id_returns_invalid_params(self):
        """``post`` requires a ``conversation_id``."""
        result = self._dispatch({'action': 'post'})
        _assert_migrated_envelope(
            self, result,
            error_code='invalid_params',
            action='post',
        )

    def test_unknown_action_returns_unknown_action(self):
        """Local fallback: action string not in the ops_digest valid set."""
        result = self._dispatch({'action': '__bogus_action_s2880__'})
        _assert_migrated_envelope(
            self, result,
            error_code='unknown_action',
            action='__bogus_action_s2880__',
        )
