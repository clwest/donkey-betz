"""
URC v0.1 shared envelope module — enrich_output_data() coverage.

Session 1209 follow-up: the original Phase A test_urc_v01_envelope.py
exercises the helpers via the AgentResult-stub shims kept on
tasks_agents.py for backcompat. This file tests the shared module
(core.services.urc_envelope) directly — specifically the new
enrich_output_data() function that gets called from BOTH writeback
paths (tasks_agents._impl_execute_agent_task AND
agent_router._complete_execution).

Run:
    python manage.py test core.tests.test_urc_envelope_module -v2
"""

from django.test import SimpleTestCase

from core.services.urc_envelope import (
    compute_run_status,
    enrich_output_data,
)


_REQUIRED_URC_KEYS = {
    'agent_name', 'run_status', 'latency_ms',
    'error_signature', 'error_message', 'artifacts',
    'warnings', 'completed_at',
}


class EnrichOutputDataEnvelopeShapeTests(SimpleTestCase):
    """Every call MUST land the 8 required top-level URC keys."""

    def test_success_clean_path_emits_all_required_keys(self):
        out = enrich_output_data(
            {'data': {'foo': 'bar'}, 'message': 'ok'},
            agent_name='TopicMinerAgent',
            success=True,
            error=None,
            message='ok',
            data={'foo': 'bar'},
            execution_time_ms=4034,
            input_context={},
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        self.assertTrue(_REQUIRED_URC_KEYS.issubset(out.keys()))
        self.assertEqual(out['agent_name'], 'TopicMinerAgent')
        self.assertEqual(out['run_status'], 'success')
        self.assertEqual(out['latency_ms'], 4034)
        self.assertIsNone(out['error_signature'])
        self.assertIsNone(out['error_message'])
        self.assertEqual(out['artifacts'], [])
        self.assertEqual(out['warnings'], [])
        self.assertEqual(out['completed_at'], '2026-06-23T05:00:00+00:00')

    def test_base_output_none_synthesizes_dict(self):
        """Failure paths pass output_data=None; helper must build envelope from scratch."""
        out = enrich_output_data(
            None,
            agent_name='SomeAgent',
            success=False,
            error='Crash boom',
            message='',
            data={},
            execution_time_ms=200,
            input_context=None,
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        self.assertTrue(_REQUIRED_URC_KEYS.issubset(out.keys()))
        self.assertEqual(out['run_status'], 'error')
        self.assertEqual(out['error_message'], 'Crash boom')
        self.assertEqual(out['error_signature'], 'Crash boom')

    def test_legacy_keys_preserved(self):
        """Caller's existing output_data shape is untouched (additive only)."""
        base = {
            'content': 'hello world',
            'metadata': {'k': 'v'},
            'message': 'hello world',
            'result_preview': 'hello world',
            'data': {'k': 'v'},
            'error': None,
            'tool_calls': [],
        }
        out = enrich_output_data(
            base,
            agent_name='X',
            success=True,
            error=None,
            message='hello world',
            data={'k': 'v'},
            execution_time_ms=10,
            input_context={},
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        # legacy keys
        for k in ('content', 'metadata', 'message', 'result_preview',
                  'data', 'error', 'tool_calls'):
            self.assertIn(k, out)
        self.assertEqual(out['content'], 'hello world')
        self.assertEqual(out['metadata'], {'k': 'v'})

    def test_warnings_list_initialized_when_absent(self):
        out = enrich_output_data(
            {},
            agent_name='X',
            success=True,
            error=None,
            message='',
            data={},
            execution_time_ms=10,
            input_context={},
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        self.assertIsInstance(out['warnings'], list)
        self.assertEqual(out['warnings'], [])

    def test_existing_warnings_preserved_and_extended(self):
        prior = [{'type': 'PRIOR_WARNING', 'message': 'something'}]
        base = {'warnings': prior, 'data': {'random': 'shape'}}
        out = enrich_output_data(
            base,
            agent_name='X',
            success=True,
            error=None,
            message='',
            data={'random': 'shape'},
            execution_time_ms=10,
            input_context={'mode': 'receipt_only'},
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        # prior warning preserved + contract violation appended
        self.assertEqual(out['warnings'][0]['type'], 'PRIOR_WARNING')
        self.assertEqual(out['warnings'][1]['type'], 'RECEIPT_CONTRACT_VIOLATION')

    def test_non_list_warnings_replaced_with_list(self):
        """Defensive: if caller passed warnings=None or junk, we reset to []."""
        out = enrich_output_data(
            {'warnings': None},
            agent_name='X',
            success=True,
            error=None,
            message='',
            data={},
            execution_time_ms=10,
            input_context={},
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        self.assertIsInstance(out['warnings'], list)


class EnrichOutputDataContractViolationTests(SimpleTestCase):
    """Phase C: receipt_only mode classifies non-receipt payloads."""

    def test_contract_violation_in_receipt_only_mode_adds_warning(self):
        out = enrich_output_data(
            {},
            agent_name='ContentWriterAgent',
            success=True,
            error=None,
            message='',
            data={'this': 'is not a receipt'},
            execution_time_ms=151320,
            input_context={'mode': 'receipt_only'},
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        self.assertEqual(out['run_status'], 'contract_violation')
        self.assertEqual(len(out['warnings']), 1)
        w = out['warnings'][0]
        self.assertEqual(w['type'], 'RECEIPT_CONTRACT_VIOLATION')
        self.assertEqual(w['message'], 'receipt_only mode: missing_status')
        self.assertEqual(w['meta']['predicate'], 'missing_status')
        self.assertEqual(out['error_signature'], 'RECEIPT_CONTRACT_VIOLATION: missing_status')
        self.assertEqual(out['error_message'], 'receipt_only mode: missing_status')

    def test_normal_mode_does_not_trigger_violation(self):
        out = enrich_output_data(
            {},
            agent_name='X',
            success=True,
            error=None,
            message='',
            data={'random': 'shape'},
            execution_time_ms=10,
            input_context={},
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        self.assertEqual(out['run_status'], 'success')
        self.assertEqual(out['warnings'], [])

    def test_valid_receipt_in_receipt_only_mode_stays_success(self):
        out = enrich_output_data(
            {},
            agent_name='X',
            success=True,
            error=None,
            message='',
            data={'status': 'ok'},
            execution_time_ms=10,
            input_context={'mode': 'receipt_only'},
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        self.assertEqual(out['run_status'], 'success')


class EnrichOutputDataArtifactsTests(SimpleTestCase):
    """artifacts field minimal-in-v0 behavior."""

    def test_deliverable_id_mirrored_into_artifacts(self):
        out = enrich_output_data(
            {},
            agent_name='X',
            success=True,
            error=None,
            message='',
            data={'deliverable_id': '6f09233c-c984-4303-87c4-e67b94390030'},
            execution_time_ms=10,
            input_context={},
            completed_at_iso='2026-06-23T05:00:00+00:00',
            deliverable_id='6f09233c-c984-4303-87c4-e67b94390030',
        )
        self.assertEqual(out['artifacts'], [
            {'type': 'deliverable', 'id': '6f09233c-c984-4303-87c4-e67b94390030'},
        ])
        # backcompat: top-level deliverable_id also set
        self.assertEqual(out['deliverable_id'], '6f09233c-c984-4303-87c4-e67b94390030')

    def test_no_deliverable_yields_empty_artifacts(self):
        out = enrich_output_data(
            {},
            agent_name='X',
            success=True,
            error=None,
            message='',
            data={},
            execution_time_ms=10,
            input_context={},
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        self.assertEqual(out['artifacts'], [])
        self.assertNotIn('deliverable_id', out)


class EnrichOutputDataOptionalFieldsTests(SimpleTestCase):
    """started_at + attempts_used are optional — emitted only when set."""

    def test_started_at_emitted_when_provided(self):
        out = enrich_output_data(
            {},
            agent_name='X', success=True, error=None, message='', data={},
            execution_time_ms=10, input_context={},
            started_at_iso='2026-06-23T05:00:00+00:00',
            completed_at_iso='2026-06-23T05:00:10+00:00',
        )
        self.assertEqual(out['started_at'], '2026-06-23T05:00:00+00:00')

    def test_started_at_absent_when_none(self):
        out = enrich_output_data(
            {},
            agent_name='X', success=True, error=None, message='', data={},
            execution_time_ms=10, input_context={},
            started_at_iso=None,
            completed_at_iso='2026-06-23T05:00:10+00:00',
        )
        self.assertNotIn('started_at', out)

    def test_attempts_used_mirrored_when_set(self):
        out = enrich_output_data(
            {},
            agent_name='X', success=True, error=None, message='', data={'attempts_used': 2},
            execution_time_ms=10, input_context={},
            completed_at_iso='2026-06-23T05:00:00+00:00',
            attempts_used=2,
        )
        self.assertEqual(out['attempts_used'], 2)

    def test_attempts_used_absent_when_none(self):
        out = enrich_output_data(
            {},
            agent_name='X', success=True, error=None, message='', data={},
            execution_time_ms=10, input_context={},
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        self.assertNotIn('attempts_used', out)


class EnrichOutputDataErrorPathTests(SimpleTestCase):
    """error/timeout paths set error_signature + error_message."""

    def test_error_with_message_normalized(self):
        out = enrich_output_data(
            {},
            agent_name='X', success=False,
            error='AttributeError: 6f09233c-c984-4303-87c4-e67b94390030 missing field',
            message='', data={},
            execution_time_ms=10, input_context={},
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        self.assertEqual(out['run_status'], 'error')
        self.assertIn('{id}', out['error_signature'])
        self.assertIn('AttributeError', out['error_signature'])

    def test_timeout_classified_separately_from_error(self):
        out = enrich_output_data(
            {},
            agent_name='X', success=False,
            error='Agent exceeded 600s wall-clock timeout',
            message='', data={},
            execution_time_ms=600000, input_context={},
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        self.assertEqual(out['run_status'], 'timeout')
        self.assertEqual(out['error_message'], 'Agent exceeded 600s wall-clock timeout')

    def test_q5_defensive_success_with_error_string_becomes_error(self):
        out = enrich_output_data(
            {},
            agent_name='X', success=True,
            error='Hmm something odd',
            message='', data={'status': 'ok'},
            execution_time_ms=10, input_context={'mode': 'receipt_only'},
            completed_at_iso='2026-06-23T05:00:00+00:00',
        )
        self.assertEqual(out['run_status'], 'error')


class ComputeRunStatusPrimitiveSignatureTests(SimpleTestCase):
    """The primitive-arg compute_run_status() entry point."""

    def test_returns_tuple_status_reason(self):
        status, reason = compute_run_status(
            success=True, error=None, data={}, input_context={},
        )
        self.assertEqual(status, 'success')
        self.assertIsNone(reason)

    def test_contract_violation_returns_reason(self):
        status, reason = compute_run_status(
            success=True, error=None, data={'random': 'shape'},
            input_context={'mode': 'receipt_only'},
        )
        self.assertEqual(status, 'contract_violation')
        self.assertEqual(reason, 'missing_status')
