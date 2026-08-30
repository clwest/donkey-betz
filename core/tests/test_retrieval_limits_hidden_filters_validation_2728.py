"""
Session 2730 — Rigby Tool Validation Engineering Campaign, Batch C tool 3
regression tests for retrieval limits + hidden filters.

Covers the F-RL-* findings surfaced during code trace + patched at
Session 2730. See:
- `docs/research/tools/validation/retrieval_limits_hidden_filters_validation.md`
- `docs/research/tools/tools_validation_engineering_campaign_plan.md`

Findings covered:

- F-RL-1 `td_limit_envelope.compute_limit` helper — envelope shape,
  under-cap fast path, cap-fired envelope, zero/negative/non-int
  autofill defenses, custom `key` param.
- F-RL-2 3-site migration to the shared helper — source-level guards
  that inline `_requested_limit_int` / `_limit_capped` patterns are
  gone from the three migrated handler methods.
- F-RL-5 `td_autofill_safety` verified in production use at HEAD.

Existing coverage NOT duplicated:
- `coerce_optional_bool` / `is_truthy` / `require_write_authorization`
  helpers — covered in test_td_autofill_safety.py.
- F-D-5 envelope response shape — covered in
  test_deliverable_tool_validation_2728.py.
- F-KB-1 envelope response shape — covered in
  test_search_docs_kb_tool_validation_2728.py.

Run::

    python manage.py test core.tests.test_retrieval_limits_hidden_filters_validation_2728 -v2
"""
from __future__ import annotations

import inspect

from django.test import SimpleTestCase

from core.services.td_limit_envelope import compute_limit


# ─── F-RL-1: compute_limit helper — happy paths + autofill defenses ─────


class FRL1UnderCapReturnsEmptyEnvelope(SimpleTestCase):
    """F-RL-1 — when the caller stays under hard_max, envelope is empty."""

    def test_missing_limit_uses_default_no_envelope(self):
        limit, envelope = compute_limit({}, default=10, hard_max=50)
        self.assertEqual(limit, 10)
        self.assertEqual(envelope, {})

    def test_explicit_below_cap_no_envelope(self):
        limit, envelope = compute_limit({'limit': 30}, default=10, hard_max=50)
        self.assertEqual(limit, 30)
        self.assertEqual(envelope, {})

    def test_explicit_equal_to_cap_no_envelope(self):
        """Requesting exactly the cap should NOT fire the envelope —
        the caller got what they asked for."""
        limit, envelope = compute_limit({'limit': 50}, default=10, hard_max=50)
        self.assertEqual(limit, 50)
        self.assertEqual(envelope, {})


class FRL1OverCapReturnsFDR5Envelope(SimpleTestCase):
    """F-RL-1 — when the caller exceeds hard_max, envelope carries F-D-5 shape."""

    def test_envelope_shape_matches_F_D_5(self):
        limit, envelope = compute_limit({'limit': 200}, default=10, hard_max=50)
        self.assertEqual(limit, 50)
        self.assertEqual(envelope, {
            'limit_capped': True,
            'requested_limit': 200,
            'effective_limit': 50,
            'hard_max': 50,
        })

    def test_envelope_spread_into_response_dict(self):
        """Verify the intended use pattern: `**envelope` spread."""
        _limit, envelope = compute_limit({'limit': 200}, default=10, hard_max=50)
        resp = {'action': 'list', 'items': [1, 2, 3], **envelope}
        self.assertTrue(resp['limit_capped'])
        self.assertEqual(resp['requested_limit'], 200)


class FRL1AutofillDefenses(SimpleTestCase):
    """F-RL-1 — LLM-autofill defenses beyond the inline copies."""

    def test_zero_limit_falls_back_to_default(self):
        """Session 1227 PR2 int-autofill class: GPT-5.2 fills declared
        optional ints with 0. Zero limit is never a real intent."""
        limit, envelope = compute_limit({'limit': 0}, default=10, hard_max=50)
        self.assertEqual(limit, 10)
        self.assertEqual(envelope, {})

    def test_negative_limit_falls_back_to_default(self):
        limit, envelope = compute_limit({'limit': -5}, default=10, hard_max=50)
        self.assertEqual(limit, 10)
        self.assertEqual(envelope, {})

    def test_string_non_int_falls_back_to_default(self):
        limit, envelope = compute_limit({'limit': 'foo'}, default=10, hard_max=50)
        self.assertEqual(limit, 10)
        self.assertEqual(envelope, {})

    def test_list_value_falls_back_to_default(self):
        """Unhashable / unexpected payload types must not raise."""
        limit, envelope = compute_limit({'limit': [1, 2]}, default=10, hard_max=50)
        self.assertEqual(limit, 10)
        self.assertEqual(envelope, {})

    def test_none_value_falls_back_to_default(self):
        limit, envelope = compute_limit({'limit': None}, default=10, hard_max=50)
        self.assertEqual(limit, 10)
        self.assertEqual(envelope, {})

    def test_numeric_string_is_coerced(self):
        """Rigby's LLM sometimes emits `"limit": "20"` (numeric string)."""
        limit, envelope = compute_limit({'limit': '20'}, default=10, hard_max=50)
        self.assertEqual(limit, 20)
        self.assertEqual(envelope, {})

    def test_numeric_string_over_cap_capped(self):
        limit, envelope = compute_limit({'limit': '500'}, default=10, hard_max=50)
        self.assertEqual(limit, 50)
        self.assertEqual(envelope['requested_limit'], 500)


class FRL1CustomKey(SimpleTestCase):
    """F-RL-1 — the `key` parameter enables reuse for tools that use
    non-`limit` names (e.g., `max`, `count`, `top_k`)."""

    def test_custom_key_reads_correct_field(self):
        limit, envelope = compute_limit(
            {'top_k': 100}, default=10, hard_max=50, key='top_k',
        )
        self.assertEqual(limit, 50)
        self.assertEqual(envelope['requested_limit'], 100)

    def test_custom_key_ignores_limit_field(self):
        """When `key='top_k'`, a `limit` field in the payload is ignored."""
        limit, envelope = compute_limit(
            {'top_k': 20, 'limit': 500},
            default=10, hard_max=50, key='top_k',
        )
        self.assertEqual(limit, 20)  # from top_k, not limit
        self.assertEqual(envelope, {})


# ─── F-RL-2: source-level migration guards ──────────────────────────────


class FRL2InlinePatternRemovedTests(SimpleTestCase):
    """F-RL-2 — source-level guards that the inline `_requested_limit_int` /
    `_limit_capped` patterns are gone from the migrated handler methods."""

    def test_deliverable_tool_list_uses_compute_limit(self):
        """`_handle_deliverables` at td_handlers_agents.py:~1621
        now imports and calls `compute_limit` instead of inline
        parsing/clamping."""
        from core.services.td_handlers_agents import AgentHandlersMixin
        src = inspect.getsource(AgentHandlersMixin._handle_deliverables)
        self.assertIn('from core.services.td_limit_envelope import compute_limit', src)
        self.assertIn('compute_limit(', src)
        # The inline pattern is gone.
        self.assertNotIn('_requested_limit_int = int(_requested_limit)', src)
        self.assertNotIn('_limit_capped = _requested_limit_int > _LIST_HARD_MAX', src)

    def test_content_tool_list_recent_uses_compute_limit(self):
        """`_handle_conversation` / `_handle_content` at
        td_handlers_core.py:~4013 (list_recent action)."""
        # `list_recent` lives inside a bigger method — read raw file
        # rather than a specific method's source.
        src_path = '/Users/donkeyking/Donkey_Betz/unified-donkey-betz/core/services/td_handlers_core.py'
        with open(src_path) as f:
            src = f.read()
        # `list_recent` block references compute_limit now.
        self.assertIn('compute_limit(payload, default=10, hard_max=25)', src)
        # The inline pattern for THIS site is gone.
        self.assertNotIn('_LIST_RECENT_HARD_MAX = 25', src)

    def test_ops_kb_browse_uses_compute_limit(self):
        """`_handle_kb_browse` at td_handlers_ops.py:5267 uses the helper;
        the closure wrapper is preserved for shape compatibility."""
        from core.services.td_handlers_ops import OpsHandlersMixin
        src = inspect.getsource(OpsHandlersMixin._handle_kb_browse)
        self.assertIn('from core.services.td_limit_envelope import compute_limit', src)
        self.assertIn('compute_limit(payload, default=20, hard_max=50)', src)
        # Inline pattern gone.
        self.assertNotIn('_KB_HARD_MAX = 50', src)
        self.assertNotIn('_limit_capped = _requested_limit_int > _KB_HARD_MAX', src)


# ─── F-RL-5: td_autofill_safety verified at HEAD ────────────────────────


class FRL5AutofillSafetyModuleIntactTests(SimpleTestCase):
    """F-RL-5 — the S1228 PR-A canonical defenses remain in place at HEAD."""

    def test_module_exports_three_canonical_helpers(self):
        from core.services import td_autofill_safety
        self.assertTrue(hasattr(td_autofill_safety, 'coerce_optional_bool'))
        self.assertTrue(hasattr(td_autofill_safety, 'is_truthy'))
        self.assertTrue(hasattr(td_autofill_safety, 'require_write_authorization'))

    def test_python_bool_false_treated_as_no_signal(self):
        """MEMORY rule feedback_llm_autofills_boolean_params_with_false —
        Python False must not fire the reverse filter."""
        from core.services.td_autofill_safety import coerce_optional_bool
        self.assertIsNone(coerce_optional_bool(False))

    def test_explicit_string_false_fires_reverse_filter(self):
        from core.services.td_autofill_safety import coerce_optional_bool
        self.assertIs(coerce_optional_bool('false'), False)
        self.assertIs(coerce_optional_bool('False'), False)

    def test_truthy_forms_fire_forward_filter(self):
        from core.services.td_autofill_safety import coerce_optional_bool
        for v in (True, 'true', 'True', 1, '1'):
            self.assertIs(coerce_optional_bool(v), True, f'expected True for {v!r}')
