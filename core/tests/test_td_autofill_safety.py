"""
Tests for core/services/td_autofill_safety.py — the canonical defenses
against the LLM-autofill class of bug Session 1227 root-caused.

GPT-5.2 in function-calling mode autofills declared optional booleans
with Python ``False`` and declared optional ints with ``0``, regardless
of whether the user asked to filter. PR-A's helper rejects those
autofills as "no signal" and only acts on explicit caller intent.

Memory rule: ``feedback_llm_autofills_boolean_params_with_false``.
"""

from django.test import SimpleTestCase

from core.services.td_autofill_safety import (
    coerce_optional_bool,
    is_truthy,
    require_write_authorization,
)


class CoerceOptionalBoolTests(SimpleTestCase):
    """coerce_optional_bool — tri-state filter coercion."""

    def test_explicit_true_forms_return_true(self):
        for v in (True, 'true', 'True', 1, '1'):
            self.assertIs(coerce_optional_bool(v), True, f'expected True for {v!r}')

    def test_explicit_false_string_returns_false(self):
        for v in ('false', 'False'):
            self.assertIs(coerce_optional_bool(v), False, f'expected False for {v!r}')

    def test_python_bool_false_returns_none(self):
        """Python bool False is the LLM autofill value — must NOT count as explicit-false."""
        self.assertIsNone(coerce_optional_bool(False))

    def test_missing_and_none_return_none(self):
        self.assertIsNone(coerce_optional_bool(None))

    def test_empty_string_returns_none(self):
        self.assertIsNone(coerce_optional_bool(''))

    def test_zero_int_returns_none(self):
        """Int 0 is the int-autofill value — must NOT count as explicit-false."""
        self.assertIsNone(coerce_optional_bool(0))

    def test_unknown_shapes_return_none(self):
        for v in ('maybe', 2, -1, [], {}, object()):
            self.assertIsNone(coerce_optional_bool(v), f'expected None for {v!r}')


class IsTruthyTests(SimpleTestCase):
    """is_truthy — one-direction switch coercion (show_all, include_*, etc)."""

    def test_explicit_truthy_forms(self):
        for v in (True, 'true', 'True', 1, '1'):
            self.assertTrue(is_truthy(v), f'expected truthy for {v!r}')

    def test_falsy_and_autofill_forms(self):
        for v in (False, 'false', 'False', None, '', 0, 'no', 'off'):
            self.assertFalse(is_truthy(v), f'expected falsy for {v!r}')


class RequireWriteAuthorizationTests(SimpleTestCase):
    """require_write_authorization — belt-and-suspenders mutation gate."""

    def test_empty_payload_stays_dry_run(self):
        dry, ok = require_write_authorization({})
        self.assertTrue(dry)
        self.assertFalse(ok)

    def test_dry_run_false_alone_stays_dry_run(self):
        """The Session 1227 autofill scenario: LLM passes dry_run=False;
        without confirm=true the gate must hold."""
        dry, ok = require_write_authorization({'dry_run': False})
        self.assertTrue(dry, 'autofilled dry_run=False alone must NOT authorize write')
        self.assertFalse(ok)

    def test_both_autofilled_false_stays_dry_run(self):
        """LLM autofills both dry_run AND confirm as False — both safety guards hold."""
        dry, ok = require_write_authorization({'dry_run': False, 'confirm': False})
        self.assertTrue(dry)
        self.assertFalse(ok)

    def test_explicit_python_bool_pair_authorizes_write(self):
        dry, ok = require_write_authorization({'dry_run': False, 'confirm': True})
        self.assertFalse(dry)
        self.assertTrue(ok)

    def test_string_sentinel_pair_authorizes_write(self):
        dry, ok = require_write_authorization({'dry_run': 'false', 'confirm': 'true'})
        self.assertFalse(dry)
        self.assertTrue(ok)

    def test_mixed_string_and_bool_authorizes_write(self):
        dry, ok = require_write_authorization({'dry_run': 'false', 'confirm': True})
        self.assertFalse(dry)
        self.assertTrue(ok)

    def test_dry_run_true_with_confirm_stays_dry_run(self):
        """Caller explicitly asked for preview — confirm=true does NOT override."""
        dry, ok = require_write_authorization({'dry_run': True, 'confirm': True})
        self.assertTrue(dry)
        self.assertFalse(ok)

    def test_confirm_alone_stays_dry_run(self):
        dry, ok = require_write_authorization({'confirm': True})
        self.assertTrue(dry)
        self.assertFalse(ok)

    def test_custom_keys_respected(self):
        dry, ok = require_write_authorization(
            {'preview_only': False, 'i_really_mean_it': True},
            dry_run_key='preview_only',
            confirm_key='i_really_mean_it',
        )
        self.assertFalse(dry)
        self.assertTrue(ok)

    def test_numeric_falsy_sentinels_for_dry_run(self):
        """Accept 0 / '0' as falsy dry_run alongside False / 'false' / 'False'."""
        for v in (0, '0'):
            dry, ok = require_write_authorization({'dry_run': v, 'confirm': True})
            self.assertFalse(dry, f'dry_run={v!r} + confirm=True must authorize')
            self.assertTrue(ok)

    def test_numeric_truthy_sentinels_for_confirm(self):
        for v in (1, '1'):
            dry, ok = require_write_authorization({'dry_run': False, 'confirm': v})
            self.assertFalse(dry, f'confirm={v!r} must satisfy gate')
            self.assertTrue(ok)
