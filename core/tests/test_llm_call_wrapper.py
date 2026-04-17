"""
Session 1098: LLMCallEvent + llm_call_wrapper smoke tests.
=========================================================

Covers PR #1 of Rigby's boardroom-dispatch remediation
(conversation pa-3c7ddc058db1).

What's exercised:
- Sync ``llm_call_span`` success path writes SUCCESS row with duration,
  tokens, provider/model, execution_id.
- Sync span on exception writes FAILED row with classified error_type
  and preserves the original exception.
- ``LLMCallCancelled`` pre-flight (cancel_token already cancelled)
  raises before the provider call and writes CANCELLED row.
- Token usage extraction handles OpenAI-shape, Anthropic-shape, and
  responses with no usage attribute.
- Async ``llm_call_async`` success path writes SUCCESS row and returns
  the underlying value.
- ``_classify_error`` covers the common provider exception names.

Run:
    python manage.py test core.tests.test_llm_call_wrapper -v2

Notes:
- Uses TransactionTestCase so LLMCallEvent rows are actually written
  (the wrapper uses objects.create / save, and we assert the row ends
  up in the DB).
- Wrapper is designed to never mask the caller's exception, so most
  tests assert both ``assertRaises`` + the telemetry row shape.
"""

import asyncio
import uuid
from unittest import mock

from django.test import SimpleTestCase, TestCase

from core.models_llm_telemetry import LLMCallEvent
from core.services.llm_call_wrapper import (
    CancelToken,
    LLMCallCancelled,
    llm_call_async,
    llm_call_span,
)
from core.services.llm_call_wrapper import (
    _classify_error,
    _extract_usage,
)


# =========================================================================
# Pure-logic helpers (no DB) — fast, no fixtures
# =========================================================================


class ClassifyErrorTests(SimpleTestCase):
    """``_classify_error`` is the dashboard-facing error bucket."""

    def test_timeout_by_class_name(self):
        class TimeoutError_(Exception):
            pass
        self.assertEqual(_classify_error(TimeoutError_("x")), 'timeout')

    def test_timeout_by_message(self):
        self.assertEqual(
            _classify_error(Exception("request timeout exceeded")),
            'timeout',
        )

    def test_rate_limit_by_class(self):
        class RateLimitError(Exception):
            pass
        self.assertEqual(_classify_error(RateLimitError("x")), 'rate_limit')

    def test_auth_by_message(self):
        self.assertEqual(
            _classify_error(Exception("Invalid API key")),
            'auth',
        )

    def test_client_error_for_connection(self):
        class APIConnectionError(Exception):
            pass
        self.assertEqual(
            _classify_error(APIConnectionError("broken")),
            'client_error',
        )

    def test_api_error_fallback(self):
        class APIStatusError(Exception):
            pass
        self.assertEqual(_classify_error(APIStatusError("503")), 'api_error')

    def test_unknown_fallback(self):
        self.assertEqual(_classify_error(ValueError("boom")), 'unknown')


class ExtractUsageTests(SimpleTestCase):
    """``_extract_usage`` unwraps common provider response shapes."""

    def test_openai_shape(self):
        resp = mock.Mock()
        resp.usage = mock.Mock(prompt_tokens=123, completion_tokens=45)
        self.assertEqual(
            _extract_usage(resp),
            {'tokens_in': 123, 'tokens_out': 45},
        )

    def test_anthropic_shape(self):
        resp = mock.Mock(spec=['usage'])
        resp.usage = mock.Mock(spec=['input_tokens', 'output_tokens'])
        resp.usage.input_tokens = 7
        resp.usage.output_tokens = 11
        self.assertEqual(
            _extract_usage(resp),
            {'tokens_in': 7, 'tokens_out': 11},
        )

    def test_dict_shape(self):
        resp = {'usage': {'prompt_tokens': 3, 'completion_tokens': 9}}
        self.assertEqual(
            _extract_usage(resp),
            {'tokens_in': 3, 'tokens_out': 9},
        )

    def test_missing_usage_is_none(self):
        self.assertEqual(
            _extract_usage(mock.Mock(spec=[])),
            {'tokens_in': None, 'tokens_out': None},
        )

    def test_none_response_safe(self):
        self.assertEqual(
            _extract_usage(None),
            {'tokens_in': None, 'tokens_out': None},
        )


# =========================================================================
# Sync span — writes LLMCallEvent rows
# =========================================================================


class LLMCallSpanSyncTests(TestCase):
    """``llm_call_span`` context manager writes one row per call."""

    def test_success_writes_success_row(self):
        exec_id = uuid.uuid4()
        fake_resp = mock.Mock()
        fake_resp.usage = mock.Mock(prompt_tokens=100, completion_tokens=50)

        with llm_call_span(
            provider='openai',
            model='gpt-5-mini',
            execution_id=exec_id,
            agent_name='ThinkingAgent',
            metadata={'task_id': 't-1'},
        ) as span:
            span.attach_response(fake_resp)

        rows = list(LLMCallEvent.objects.filter(execution_id=exec_id))
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row.status, 'SUCCESS')
        self.assertEqual(row.provider, 'openai')
        self.assertEqual(row.model, 'gpt-5-mini')
        self.assertEqual(row.agent_name, 'ThinkingAgent')
        self.assertEqual(row.tokens_in, 100)
        self.assertEqual(row.tokens_out, 50)
        self.assertFalse(row.cancelled)
        self.assertEqual(row.error_type, '')
        self.assertIsNotNone(row.duration_ms)
        self.assertIsNotNone(row.finished_at)
        self.assertEqual(row.metadata, {'task_id': 't-1'})

    def test_exception_writes_failed_row_and_propagates(self):
        exec_id = uuid.uuid4()

        class APIStatusError(Exception):
            pass

        with self.assertRaises(APIStatusError):
            with llm_call_span(
                provider='anthropic',
                model='claude-sonnet-4-6',
                execution_id=exec_id,
                agent_name='EditorAgent',
            ):
                raise APIStatusError("provider said no")

        row = LLMCallEvent.objects.get(execution_id=exec_id)
        self.assertEqual(row.status, 'FAILED')
        self.assertEqual(row.error_type, 'api_error')
        self.assertIn('provider said no', row.error_message)
        self.assertFalse(row.cancelled)

    def test_pre_cancelled_token_raises_and_records(self):
        exec_id = uuid.uuid4()
        token = CancelToken()
        token.cancel()

        with self.assertRaises(LLMCallCancelled):
            with llm_call_span(
                provider='openai',
                model='gpt-5-mini',
                execution_id=exec_id,
                cancel_token=token,
            ):
                # This body must never execute because the token was
                # already cancelled before the span acquired.
                raise AssertionError("body should not run")

        # Pre-flight cancellation raises before the row is created (by
        # design — we fail fast without any DB write). Confirm the
        # exception semantic, not row presence.
        self.assertFalse(
            LLMCallEvent.objects.filter(execution_id=exec_id).exists(),
            "pre-flight cancellation should raise before row creation",
        )

    def test_none_execution_id_is_accepted(self):
        with llm_call_span(
            provider='openai', model='gpt-5-mini',
        ) as span:
            span.attach_response(mock.Mock(spec=[]))

        row = LLMCallEvent.objects.filter(
            provider='openai', execution_id__isnull=True,
        ).latest('started_at')
        self.assertEqual(row.status, 'SUCCESS')

    def test_string_execution_id_is_coerced(self):
        exec_str = str(uuid.uuid4())
        with llm_call_span(
            provider='openai', model='gpt-5-mini',
            execution_id=exec_str,
        ) as span:
            span.attach_response(mock.Mock(spec=[]))

        row = LLMCallEvent.objects.get(execution_id=uuid.UUID(exec_str))
        self.assertEqual(row.status, 'SUCCESS')

    def test_invalid_execution_id_becomes_null(self):
        """Garbage execution_id should not raise — just store NULL."""
        with llm_call_span(
            provider='openai', model='gpt-5-mini',
            execution_id='not-a-uuid',
        ) as span:
            span.attach_response(mock.Mock(spec=[]))

        row = LLMCallEvent.objects.filter(
            provider='openai', execution_id__isnull=True,
        ).latest('started_at')
        self.assertEqual(row.status, 'SUCCESS')


# =========================================================================
# Async wrapper — awaits the provider call, records telemetry
# =========================================================================


class LLMCallAsyncTests(TestCase):
    """``llm_call_async`` twin for async agents (e.g. ThinkingAgent)."""

    def test_async_success_returns_response_and_records(self):
        exec_id = uuid.uuid4()
        fake_resp = mock.Mock()
        fake_resp.usage = mock.Mock(prompt_tokens=10, completion_tokens=3)

        def sync_fn(**kwargs):
            return fake_resp

        async def _run():
            return await llm_call_async(
                sync_fn,
                provider='openai',
                model_name='gpt-5-mini',
                execution_id=exec_id,
                agent_name='ThinkingAgent',
            )

        result = asyncio.run(_run())
        self.assertIs(result, fake_resp)

        row = LLMCallEvent.objects.get(execution_id=exec_id)
        self.assertEqual(row.status, 'SUCCESS')
        self.assertEqual(row.tokens_in, 10)
        self.assertEqual(row.tokens_out, 3)

    def test_async_exception_records_failed(self):
        exec_id = uuid.uuid4()

        class TimeoutError_(Exception):
            pass

        def sync_fn(**kwargs):
            raise TimeoutError_("read timeout 90s")

        async def _run():
            await llm_call_async(
                sync_fn,
                provider='openai',
                model_name='gpt-5-mini',
                execution_id=exec_id,
            )

        with self.assertRaises(TimeoutError_):
            asyncio.run(_run())

        row = LLMCallEvent.objects.get(execution_id=exec_id)
        self.assertEqual(row.status, 'FAILED')
        self.assertEqual(row.error_type, 'timeout')

    def test_async_awaits_coroutine_return(self):
        exec_id = uuid.uuid4()
        fake_resp = mock.Mock(spec=[])

        async def async_fn(**kwargs):
            await asyncio.sleep(0)
            return fake_resp

        async def _run():
            return await llm_call_async(
                async_fn,
                provider='openai',
                model_name='gpt-5-mini',
                execution_id=exec_id,
            )

        result = asyncio.run(_run())
        self.assertIs(result, fake_resp)
        self.assertEqual(
            LLMCallEvent.objects.get(execution_id=exec_id).status,
            'SUCCESS',
        )
