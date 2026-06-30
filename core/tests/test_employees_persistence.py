"""Session 1267 PR 4.0 — shared persistence helper tests.

Proves that the lifted ``_persist_to_summary`` helper preserves the
exact merge + save semantics of the two prior inline implementations
in ``core/jobs/morning_brief.py`` and ``core/jobs/platform_audit.py``.

Scope discipline (per PR 4.0):
- Helper-level tests only; no employee/job behavior changes here.
- Existing morning_brief + platform_audit test suites cover the
  end-to-end summary-write paths and are expected to keep passing
  unchanged.

Run::

    .venv/bin/python manage.py test core.tests.test_employees_persistence -v2
"""

from __future__ import annotations

from unittest.mock import MagicMock

from django.test import SimpleTestCase

from core.employees._persistence import _persist_to_summary


class PersistToSummaryBehaviorTests(SimpleTestCase):
    """Verifies the merge + save semantics on a mocked mission."""

    def _mission(self, summary):
        mission = MagicMock()
        mission.summary = summary
        return mission

    def test_writes_into_none_summary(self):
        mission = self._mission(None)

        _persist_to_summary(mission, audit_type="comprehensive", step_count=5)

        self.assertEqual(
            mission.summary,
            {"audit_type": "comprehensive", "step_count": 5},
        )
        mission.save.assert_called_once_with(update_fields=["summary"])

    def test_writes_into_empty_dict_summary(self):
        mission = self._mission({})

        _persist_to_summary(mission, ok=True)

        self.assertEqual(mission.summary, {"ok": True})
        mission.save.assert_called_once_with(update_fields=["summary"])

    def test_merges_into_existing_summary_preserving_other_keys(self):
        mission = self._mission({"existing_key": "keep me", "other": 42})

        _persist_to_summary(mission, new_key="added")

        self.assertEqual(
            mission.summary,
            {"existing_key": "keep me", "other": 42, "new_key": "added"},
        )
        mission.save.assert_called_once_with(update_fields=["summary"])

    def test_overwrites_existing_keys_with_same_name(self):
        mission = self._mission({"shared_key": "old", "untouched": 1})

        _persist_to_summary(mission, shared_key="new")

        self.assertEqual(
            mission.summary,
            {"shared_key": "new", "untouched": 1},
        )
        mission.save.assert_called_once_with(update_fields=["summary"])

    def test_supports_no_fields_noop_write(self):
        mission = self._mission({"left_alone": 1})

        _persist_to_summary(mission)

        self.assertEqual(mission.summary, {"left_alone": 1})
        mission.save.assert_called_once_with(update_fields=["summary"])

    def test_save_uses_update_fields_summary_only(self):
        """Regression guard — never let this drift to ``mission.save()``.

        A bare ``save()`` would trigger ``auto_now`` columns +
        ``post_save`` signals on unrelated fields. The original
        inline implementations both used the focused
        ``update_fields=['summary']`` and the lift must preserve that.
        """
        mission = self._mission(None)

        _persist_to_summary(mission, x=1)

        # Single call, single kwarg, exact list.
        self.assertEqual(mission.save.call_count, 1)
        _, kwargs = mission.save.call_args
        self.assertEqual(list(kwargs.keys()), ["update_fields"])
        self.assertEqual(kwargs["update_fields"], ["summary"])


class PersistToSummaryCallersImportFromSharedHelperTests(SimpleTestCase):
    """AST-level contract: PA + CoS job modules import the lifted helper.

    Locks in the LIFT so a future edit can't accidentally re-introduce
    an inline duplicate definition. Mirrors the AST-contract pattern
    used in ``test_employees_platform_auditor.py``.
    """

    def test_morning_brief_imports_shared_helper(self):
        import core.jobs.morning_brief as morning_brief
        from core.employees._persistence import _persist_to_summary as canonical

        self.assertIs(morning_brief._persist_to_summary, canonical)

    def test_platform_audit_imports_shared_helper(self):
        import core.jobs.platform_audit as platform_audit
        from core.employees._persistence import _persist_to_summary as canonical

        self.assertIs(platform_audit._persist_to_summary, canonical)
