"""
URC v0.1 envelope helpers — Universal Receipt Contract.

Session 1209: Phase A + Phase C runner-level enforcement of the URC v0.1
envelope at the `core/tasks_agents.py` writeback block. Q1–Q5 locked
on conversation pa-61c7b47d201d4591; spec deliverable
6f09233c-c984-4303-87c4-e67b94390030.

Covers the four pure helper functions and the precedence rule. The
writeback-block integration is exercised indirectly through agent
dispatch in production; live smoke confirmation runs after merge.

Run:
    python manage.py test core.tests.test_urc_v01_envelope -v2
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from django.test import SimpleTestCase

from core.tasks_agents import (
    _urc_compute_run_status,
    _urc_is_skipped,
    _urc_is_timeout,
    _urc_normalize_error_signature,
    _urc_receipt_violation_reason,
)


@dataclass
class _StubResult:
    """Minimal stand-in for AgentResult — covers fields the URC helpers read."""

    success: bool
    error: Optional[str] = None
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


class UrcSkippedDetectorTests(SimpleTestCase):
    """Q1: result.success is True AND result.data['skipped'] is True."""

    def test_skipped_marker_with_success_returns_true(self):
        r = _StubResult(success=True, data={'skipped': True})
        self.assertTrue(_urc_is_skipped(r))

    def test_skipped_marker_without_success_returns_false(self):
        r = _StubResult(success=False, data={'skipped': True})
        self.assertFalse(_urc_is_skipped(r))

    def test_no_skipped_marker_returns_false(self):
        r = _StubResult(success=True, data={'other': 'value'})
        self.assertFalse(_urc_is_skipped(r))

    def test_non_dict_data_returns_false(self):
        r = _StubResult(success=True, data=None)  # type: ignore[arg-type]
        self.assertFalse(_urc_is_skipped(r))

    def test_skipped_falsy_value_returns_false(self):
        r = _StubResult(success=True, data={'skipped': False})
        self.assertFalse(_urc_is_skipped(r))


class UrcTimeoutDetectorTests(SimpleTestCase):
    """Q2: success=False AND 'wall-clock timeout' in result.error."""

    def test_canonical_timeout_string_matches(self):
        r = _StubResult(
            success=False,
            error='ContentWriterAgent exceeded 600s wall-clock timeout',
        )
        self.assertTrue(_urc_is_timeout(r))

    def test_success_true_returns_false_even_with_timeout_string(self):
        r = _StubResult(success=True, error='wall-clock timeout')
        self.assertFalse(_urc_is_timeout(r))

    def test_unrelated_error_returns_false(self):
        r = _StubResult(success=False, error='AttributeError: NoneType has no attribute "id"')
        self.assertFalse(_urc_is_timeout(r))

    def test_empty_error_returns_false(self):
        r = _StubResult(success=False, error=None)
        self.assertFalse(_urc_is_timeout(r))


class UrcReceiptSchemaTests(SimpleTestCase):
    """Q3: v0 minimal receipt schema = dict + status∈{ok,skipped,error} + conditional message."""

    def test_valid_ok_receipt_returns_none(self):
        self.assertIsNone(_urc_receipt_violation_reason({'status': 'ok'}))

    def test_valid_skipped_receipt_returns_none(self):
        self.assertIsNone(_urc_receipt_violation_reason({'status': 'skipped', 'reason': 'gated'}))

    def test_valid_error_receipt_with_message_returns_none(self):
        self.assertIsNone(_urc_receipt_violation_reason({'status': 'error', 'message': 'boom'}))

    def test_non_dict_returns_not_dict(self):
        self.assertEqual(_urc_receipt_violation_reason('a string'), 'not_dict')
        self.assertEqual(_urc_receipt_violation_reason(None), 'not_dict')
        self.assertEqual(_urc_receipt_violation_reason(['list']), 'not_dict')

    def test_missing_status_returns_missing_status(self):
        self.assertEqual(_urc_receipt_violation_reason({'foo': 'bar'}), 'missing_status')

    def test_invalid_status_returns_invalid_status(self):
        self.assertEqual(
            _urc_receipt_violation_reason({'status': 'whoops'}),
            'invalid_status',
        )

    def test_error_without_message_returns_error_missing_message(self):
        self.assertEqual(
            _urc_receipt_violation_reason({'status': 'error'}),
            'error_missing_message',
        )

    def test_error_with_blank_message_returns_error_missing_message(self):
        self.assertEqual(
            _urc_receipt_violation_reason({'status': 'error', 'message': '   '}),
            'error_missing_message',
        )

    def test_v0_does_not_require_timestamp(self):
        """Q3 lock: timestamp is explicitly NOT required for v0."""
        self.assertIsNone(_urc_receipt_violation_reason({'status': 'ok'}))


class UrcErrorSignatureNormalizationTests(SimpleTestCase):
    """Q4: string-only normalize — first line, strip UUIDs/long hex, ≤80 chars."""

    def test_none_returns_none(self):
        self.assertIsNone(_urc_normalize_error_signature(None))

    def test_empty_string_returns_none(self):
        self.assertIsNone(_urc_normalize_error_signature(''))

    def test_uuid_stripped(self):
        out = _urc_normalize_error_signature(
            'Initiative 29154d73-06a5-4630-abb4-3412cbdca5c5 not found'
        )
        self.assertEqual(out, 'Initiative {id} not found')

    def test_long_hex_stripped(self):
        out = _urc_normalize_error_signature(
            'Hash mismatch deadbeefdeadbeefcafe1234abcd5678 expected match'
        )
        assert out is not None
        self.assertIn('{hex}', out)
        self.assertNotIn('deadbeefdeadbeefcafe1234abcd5678', out)

    def test_only_first_line_retained(self):
        out = _urc_normalize_error_signature(
            'Top level error\nTraceback (most recent call last):\nFile "x.py"'
        )
        self.assertEqual(out, 'Top level error')

    def test_truncated_to_80_chars(self):
        long_input = 'A' * 200
        out = _urc_normalize_error_signature(long_input)
        assert out is not None
        self.assertEqual(len(out), 80)

    def test_whitespace_only_returns_none(self):
        self.assertIsNone(_urc_normalize_error_signature('   \n\t '))


class UrcComputeRunStatusPrecedenceTests(SimpleTestCase):
    """Precedence: skipped > timeout > error > contract_violation > success."""

    def test_success_clean_path(self):
        r = _StubResult(success=True, data={'foo': 'bar'})
        status, reason = _urc_compute_run_status(r, {})
        self.assertEqual(status, 'success')
        self.assertIsNone(reason)

    def test_skipped_beats_everything_else_when_marker_set(self):
        r = _StubResult(success=True, data={'skipped': True})
        status, _ = _urc_compute_run_status(r, {'mode': 'receipt_only'})
        self.assertEqual(status, 'skipped')

    def test_timeout_classified_when_pattern_in_error(self):
        r = _StubResult(success=False, error='Agent exceeded 600s wall-clock timeout')
        status, _ = _urc_compute_run_status(r, {})
        self.assertEqual(status, 'timeout')

    def test_error_classified_when_success_false(self):
        r = _StubResult(success=False, error='Something broke')
        status, _ = _urc_compute_run_status(r, {})
        self.assertEqual(status, 'error')

    def test_defensive_q5_lock_success_true_but_error_non_empty(self):
        """Q5: non-empty error string forces 'error' regardless of success bool."""
        r = _StubResult(success=True, error='Hmm something weird', data={'status': 'ok'})
        status, reason = _urc_compute_run_status(r, {'mode': 'receipt_only'})
        self.assertEqual(status, 'error')
        self.assertIsNone(reason)

    def test_contract_violation_only_in_receipt_only_mode(self):
        """A non-receipt-shaped payload outside receipt_only mode stays success."""
        r = _StubResult(success=True, data={'random': 'shape'})
        status, _ = _urc_compute_run_status(r, {})
        self.assertEqual(status, 'success')

    def test_contract_violation_fires_in_receipt_only_when_schema_fails(self):
        r = _StubResult(success=True, data={'random': 'shape'})
        status, reason = _urc_compute_run_status(r, {'mode': 'receipt_only'})
        self.assertEqual(status, 'contract_violation')
        self.assertEqual(reason, 'missing_status')

    def test_receipt_only_with_valid_receipt_stays_success(self):
        r = _StubResult(success=True, data={'status': 'ok', 'extra': 'fine'})
        status, _ = _urc_compute_run_status(r, {'mode': 'receipt_only'})
        self.assertEqual(status, 'success')

    def test_receipt_only_with_invalid_status_classifies_violation(self):
        r = _StubResult(success=True, data={'status': 'whoops'})
        status, reason = _urc_compute_run_status(r, {'mode': 'receipt_only'})
        self.assertEqual(status, 'contract_violation')
        self.assertEqual(reason, 'invalid_status')

    def test_receipt_only_with_error_status_missing_message_classifies_violation(self):
        r = _StubResult(success=True, data={'status': 'error'})
        status, reason = _urc_compute_run_status(r, {'mode': 'receipt_only'})
        self.assertEqual(status, 'contract_violation')
        self.assertEqual(reason, 'error_missing_message')

    def test_error_precedence_beats_contract_violation(self):
        """Real crashes (error) cannot be masked by contract failures."""
        r = _StubResult(success=False, error='boom', data={'random': 'shape'})
        status, _ = _urc_compute_run_status(r, {'mode': 'receipt_only'})
        self.assertEqual(status, 'error')

    def test_timeout_precedence_beats_contract_violation(self):
        r = _StubResult(
            success=False,
            error='exceeded 600s wall-clock timeout',
            data={'random': 'shape'},
        )
        status, _ = _urc_compute_run_status(r, {'mode': 'receipt_only'})
        self.assertEqual(status, 'timeout')

    def test_non_receipt_mode_with_random_payload_stays_success(self):
        r = _StubResult(success=True, data={'message': 'hello world'})
        status, _ = _urc_compute_run_status(r, {'mode': 'normal'})
        self.assertEqual(status, 'success')

    def test_input_context_not_dict_skips_contract_check(self):
        r = _StubResult(success=True, data={'random': 'shape'})
        status, _ = _urc_compute_run_status(r, None)
        self.assertEqual(status, 'success')
