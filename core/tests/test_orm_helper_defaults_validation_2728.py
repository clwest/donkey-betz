"""
Session 2730 — Rigby Tool Validation Engineering Campaign, Batch C tool 4
regression tests for ORM helper defaults.

Covers the F-OH-* findings surfaced during code trace + patched at
Session 2730. See:
- `docs/research/tools/validation/orm_helper_defaults_validation.md`
- `docs/research/tools/tools_validation_engineering_campaign_plan.md`

Findings covered:

- F-OH-1 `content_tool.content_review.list` `applied_filters` echo +
  `status='all'` escape hatch + `status_defaulted` marker.
- F-OH-2 `_handle_initiative.list` `applied_filters` echo +
  `status_defaulted` marker.
- F-OH-3 `deliverable_tool._apply_common_filters` gold standard
  verified at HEAD (source-level guard).
- F-OH-4 `td_autofill_safety` module still exports canonical helpers
  (reinforces Batch C tool 3 F-RL-5).

Existing coverage NOT duplicated:
- `td_autofill_safety` helper semantics — covered in
  test_td_autofill_safety.py + test_retrieval_limits_hidden_filters_validation_2728.py.
- `deliverable_tool.list` `applied_filters` shape — covered in
  test_deliverable_tool_validation_2728.py F-D-* tests.

Run::

    python manage.py test core.tests.test_orm_helper_defaults_validation_2728 -v2
"""
from __future__ import annotations

import inspect
import uuid

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase


User = get_user_model()


# ─── F-OH-1: content_tool.content_review.list ─────────────────────────


class FOH1SourceGuardTests(SimpleTestCase):
    """F-OH-1 — source-level guards on `_handle_content_review.list`."""

    def _src(self) -> str:
        from core.services.td_handlers_content import ContentHandlersMixin
        return inspect.getsource(ContentHandlersMixin._handle_content_review)

    def test_applied_filters_field_in_response(self):
        src = self._src()
        # New canonical echo present.
        self.assertIn("'applied_filters': dict(_applied),", src)

    def test_status_defaulted_marker_present(self):
        src = self._src()
        self.assertIn("'status_defaulted': _status_defaulted,", src)
        # And the bool is computed from raw payload (not from the
        # effective default value).
        self.assertIn("_status_defaulted = _status_raw is None", src)

    def test_status_all_escape_hatch_present(self):
        src = self._src()
        self.assertIn("str(status_filter).lower() != 'all'", src)

    def test_legacy_filters_applied_preserved_for_backward_compat(self):
        src = self._src()
        # Old key still emitted (matches _handle_initiative for consistency).
        self.assertIn("'filters_applied': {", src)


class FOH1BehaviorTests(TestCase):
    """F-OH-1 — behavioral tests via direct handler invocation."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f'oh1-{uuid.uuid4().hex[:8]}',
            email='oh1@example.com',
            password='x',
        )

    def _dispatch(self, payload: dict) -> dict:
        """Direct handler invocation (bypasses the tool_dispatcher gateway
        translation from `content_review_tool` → `content_tool.content_list`).
        Calling the handler directly exercises exactly the branch F-OH-1
        patched."""
        from core.services.tool_dispatcher import ToolDispatcher
        dispatcher = ToolDispatcher()
        return dispatcher._handle_content_review(
            tool_name='content_review_tool',
            payload=payload,
            user_id=self.user.id,
            trace_id='test-trace',
        )

    def test_default_call_marks_status_defaulted_true(self):
        """No `status` in payload → `status_defaulted: True`,
        applied_filters records the ready default."""
        result = self._dispatch({'action': 'list'})
        self.assertIn('applied_filters', result)
        self.assertIn('status_defaulted', result)
        self.assertTrue(result['status_defaulted'])
        # Applied filter reflects the default value.
        self.assertEqual(result['applied_filters'].get('status'), 'ready')

    def test_explicit_ready_marks_status_defaulted_false(self):
        result = self._dispatch({'action': 'list', 'status': 'ready'})
        self.assertFalse(result['status_defaulted'])
        self.assertEqual(result['applied_filters'].get('status'), 'ready')

    def test_all_escape_hatch_omits_status_filter(self):
        """`status='all'` bypasses the status filter — applied_filters
        does NOT include a status key."""
        result = self._dispatch({'action': 'list', 'status': 'all'})
        # Escape hatch fired.
        self.assertNotIn('status', result['applied_filters'])
        # Explicit intent → not defaulted.
        self.assertFalse(result['status_defaulted'])


# ─── F-OH-2: _handle_initiative.list ────────────────────────────────


class FOH2SourceGuardTests(SimpleTestCase):
    """F-OH-2 — source-level guards on `_handle_initiative.list`."""

    def _src(self) -> str:
        from core.services.td_handlers_content import ContentHandlersMixin
        return inspect.getsource(ContentHandlersMixin._handle_initiative)

    def test_applied_filters_field_in_response(self):
        src = self._src()
        self.assertIn("'applied_filters': dict(_applied),", src)

    def test_status_defaulted_marker_present(self):
        src = self._src()
        self.assertIn("'status_defaulted': _status_defaulted,", src)
        self.assertIn("_status_defaulted = _status_raw is None", src)

    def test_status_all_escape_hatch_preserved(self):
        """The existing `'all'` escape hatch is intact (unchanged behavior)."""
        src = self._src()
        self.assertIn("status_filter != 'all'", src)

    def test_status_filter_records_uppercased_value_when_fired(self):
        """When status filter fires, _applied records the .upper() form
        that matches what the ORM actually saw."""
        src = self._src()
        self.assertIn("_applied['status'] = status_filter.upper()", src)


# ─── F-OH-3: deliverable_tool gold standard verified ────────────────


class FOH3DeliverableToolGoldStandardTests(SimpleTestCase):
    """F-OH-3 — source-level guard that the gold-standard pattern
    hasn't regressed at HEAD."""

    def _src(self) -> str:
        from core.services.td_handlers_agents import AgentHandlersMixin
        return inspect.getsource(AgentHandlersMixin._handle_deliverables)

    def test_apply_common_filters_helper_present(self):
        src = self._src()
        self.assertIn('def _apply_common_filters(qs):', src)

    def test_show_all_bypass_uses_truthy_only(self):
        """S1227 defense: `show_all` accepts only truthy explicit signals."""
        src = self._src()
        self.assertIn(
            "_show_all = payload.get('show_all') in (True, 'true', 'True', 1, '1')",
            src,
        )

    def test_has_initiative_uses_truthy_only_plus_string_false(self):
        """S1227 defense: `has_initiative` truthy-only + string-'false' sentinel."""
        src = self._src()
        self.assertIn("has_init in (True, 'true', 'True', 1, '1')", src)
        self.assertIn("elif has_init in ('false', 'False'):", src)

    def test_applied_filters_echo_in_list_response(self):
        src = self._src()
        # List branch echoes applied_filters.
        self.assertIn("'applied_filters': dict(_applied),", src)

    def test_applied_filters_echo_in_search_response(self):
        """Search action shares the same echo."""
        src = self._src()
        # `_apply_common_filters` is called for both list and search.
        # The echo appears at both return sites — grep for both.
        matches = src.count("'applied_filters': dict(_applied),")
        self.assertGreaterEqual(matches, 2)


# ─── F-OH-4: td_autofill_safety module intact ───────────────────────


class FOH4AutofillSafetyIntactTests(SimpleTestCase):
    """F-OH-4 — reinforce Batch C tool 3 F-RL-5. The canonical
    defenses remain in place."""

    def test_module_exists_and_exports_three_helpers(self):
        from core.services import td_autofill_safety
        self.assertTrue(hasattr(td_autofill_safety, 'coerce_optional_bool'))
        self.assertTrue(hasattr(td_autofill_safety, 'is_truthy'))
        self.assertTrue(hasattr(td_autofill_safety, 'require_write_authorization'))

    def test_module_lives_at_expected_import_path(self):
        """Stability contract: the module path is public API to handler code."""
        from core.services.td_autofill_safety import coerce_optional_bool
        # If this import succeeds, the path is stable.
        self.assertTrue(callable(coerce_optional_bool))
