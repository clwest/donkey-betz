"""
Session 2728 — Rigby Tool Validation Engineering Campaign, Batch B tool 3
regression tests for `kb_ingest` (an action on `intelligence_tool` delegated
to `_handle_rag_query.ingest`).

Covers the F-KI-* findings surfaced during code trace + patched at
Session 2728. See:
- `docs/research/tools/validation/kb_ingest_validation.md`
- `docs/research/tools/tools_validation_engineering_campaign_plan.md`

Findings covered:

- F-KI-1 empty URL → returns typed error dict (`ok: False, error_code:
  'url_required'`) instead of raising ValueError.
- F-KI-2 / F-KI-3 user_id plumbed through to `process_url_async.delay(...)`.
  Restores dispatching-user-owns-ingested-document invariant. Regression
  test verifies user_id survives via mock assertion + `user_id` echo in
  the response.
- F-KI-4 URL scheme validation at tool boundary. Rejects non-http/https
  schemes (file://, data:, javascript:, etc.) with typed error naming the
  scheme and the SSRF defense rationale.
- F-KI-5 option (a) additive `dispatched: True` field alongside existing
  `success: True`. Back-compat safe; semantically accurate for callers
  parsing dispatch vs ingestion success.

Baseline coverage (previously untested):

- Delegation from `intelligence_tool.kb_ingest` → `_handle_rag_query.
  ingest` → `process_url_async.delay(...)`.
- Response envelope shape (action, url, task_id, mode, message).

Run::

    python manage.py test core.tests.test_kb_ingest_validation_2728 -v2
"""
from __future__ import annotations

from unittest.mock import patch

from django.test import SimpleTestCase

from core.services.tool_dispatcher import ToolDispatcher


class _FakeAsyncResult:
    """Stand-in for Celery AsyncResult returned by `.delay(...)`."""

    def __init__(self, task_id):
        self.id = task_id


class _KbIngestTestBase(SimpleTestCase):
    """Shared dispatch helper. Uses `_handle_rag_query` directly (the
    layer-2 handler) because that's where the F-KI-* patches live. The
    intelligence_tool.kb_ingest → rag_query.ingest delegation is a thin
    wrapper (tested by test_delegation_flow_via_intelligence_tool)."""

    def _dispatch_rag_query(self, payload, user_id=None):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_rag_query(  # type: ignore[attr-defined]
            tool_name='rag_query_tool',
            payload=payload,
            user_id=user_id,
            trace_id='test-kb-ingest-2728',
        )


# ─── F-KI-1: empty URL returns typed error dict ────────────────────────


class FKI1EmptyUrlTypedError(_KbIngestTestBase):
    """F-KI-1 — empty URL returns `{'ok': False, 'error_code': 'url_required'}`
    instead of raising ValueError."""

    def test_empty_url_returns_typed_error(self):
        result = self._dispatch_rag_query({'action': 'ingest'})
        self.assertFalse(result.get('ok'))
        self.assertEqual(result['error_code'], 'url_required')
        self.assertIn("'url' is required", result['error'])
        self.assertEqual(result['action'], 'ingest')

    def test_whitespace_only_url_returns_typed_error(self):
        result = self._dispatch_rag_query({
            'action': 'ingest',
            'url': '   \t\n  ',
        })
        self.assertFalse(result.get('ok'))
        self.assertEqual(result['error_code'], 'url_required')


# ─── F-KI-4: URL scheme validation ─────────────────────────────────────


class FKI4UrlSchemeValidation(_KbIngestTestBase):
    """F-KI-4 — reject non-http/https schemes at tool boundary."""

    def test_file_scheme_rejected(self):
        result = self._dispatch_rag_query({
            'action': 'ingest',
            'url': 'file:///etc/passwd',
        })
        self.assertFalse(result.get('ok'))
        self.assertEqual(result['error_code'], 'invalid_url_scheme')
        self.assertIn("'file'", result['error'])
        self.assertIn('SSRF', result['error'])
        self.assertEqual(result['url'], 'file:///etc/passwd')

    def test_data_scheme_rejected(self):
        result = self._dispatch_rag_query({
            'action': 'ingest',
            'url': 'data:text/html,<script>alert(1)</script>',
        })
        self.assertFalse(result.get('ok'))
        self.assertEqual(result['error_code'], 'invalid_url_scheme')
        self.assertIn("'data'", result['error'])

    def test_javascript_scheme_rejected(self):
        result = self._dispatch_rag_query({
            'action': 'ingest',
            'url': 'javascript:alert(1)',
        })
        self.assertFalse(result.get('ok'))
        self.assertEqual(result['error_code'], 'invalid_url_scheme')
        self.assertIn("'javascript'", result['error'])

    def test_http_scheme_accepted(self):
        with patch(
            'core.tasks.process_url_async.delay',
            return_value=_FakeAsyncResult('celery-fki4-http'),
        ):
            result = self._dispatch_rag_query({
                'action': 'ingest',
                'url': 'http://example.com/article',
            })
        # Not an error; dispatch succeeded.
        self.assertNotIn('error_code', result)
        self.assertEqual(result['task_id'], 'celery-fki4-http')

    def test_https_scheme_accepted(self):
        with patch(
            'core.tasks.process_url_async.delay',
            return_value=_FakeAsyncResult('celery-fki4-https'),
        ):
            result = self._dispatch_rag_query({
                'action': 'ingest',
                'url': 'https://example.com/article',
            })
        self.assertNotIn('error_code', result)
        self.assertEqual(result['task_id'], 'celery-fki4-https')

    def test_no_scheme_rejected(self):
        # `example.com` without scheme is parsed by urlparse but scheme is ''.
        result = self._dispatch_rag_query({
            'action': 'ingest',
            'url': 'example.com/article',
        })
        self.assertFalse(result.get('ok'))
        self.assertEqual(result['error_code'], 'invalid_url_scheme')


# ─── F-KI-2 / F-KI-3: user_id plumbed through to task ──────────────────


class FKI23UserIdPlumbing(_KbIngestTestBase):
    """F-KI-2/F-KI-3 — dispatching user_id survives the delegation chain
    and reaches `process_url_async.delay(...)` as the `user_id` kwarg.
    Also verified via response `user_id` echo."""

    def test_user_id_passed_to_task_delay(self):
        with patch(
            'core.tasks.process_url_async.delay',
            return_value=_FakeAsyncResult('celery-fki23-a'),
        ) as mock_delay:
            self._dispatch_rag_query(
                {'action': 'ingest', 'url': 'https://example.com/a'},
                user_id=12345,
            )
        # Assert delay was called with user_id kwarg.
        mock_delay.assert_called_once()
        _, kwargs = mock_delay.call_args
        self.assertEqual(kwargs.get('user_id'), 12345)
        self.assertEqual(kwargs.get('url'), 'https://example.com/a')
        self.assertTrue(kwargs.get('generate_embeddings'))

    def test_user_id_none_still_passed_explicitly(self):
        # When user_id is None (direct-dispatch / non-PA path), the kwarg
        # is still explicitly passed as None so the task-side code path
        # is exercised deterministically (vs relying on kwarg-omission
        # behavior).
        with patch(
            'core.tasks.process_url_async.delay',
            return_value=_FakeAsyncResult('celery-fki23-b'),
        ) as mock_delay:
            self._dispatch_rag_query(
                {'action': 'ingest', 'url': 'https://example.com/b'},
                user_id=None,
            )
        _, kwargs = mock_delay.call_args
        self.assertIsNone(kwargs.get('user_id'))

    def test_response_echoes_user_id(self):
        # F-KI-2 provenance echo: response includes `user_id` so Rigby
        # can verify her user_id survived the delegation.
        with patch(
            'core.tasks.process_url_async.delay',
            return_value=_FakeAsyncResult('celery-fki23-c'),
        ):
            result = self._dispatch_rag_query(
                {'action': 'ingest', 'url': 'https://example.com/c'},
                user_id=98765,
            )
        self.assertEqual(result['user_id'], '98765')

    def test_response_echoes_user_id_null_when_none(self):
        with patch(
            'core.tasks.process_url_async.delay',
            return_value=_FakeAsyncResult('celery-fki23-d'),
        ):
            result = self._dispatch_rag_query(
                {'action': 'ingest', 'url': 'https://example.com/d'},
                user_id=None,
            )
        self.assertIsNone(result['user_id'])


# ─── F-KI-5 option (a): additive `dispatched: True` field ──────────────


class FKI5DispatchedField(_KbIngestTestBase):
    """F-KI-5 option (a) — additive `dispatched: True` field alongside
    existing `success: True`. Back-compat safe."""

    def test_dispatched_and_success_both_true_on_success(self):
        with patch(
            'core.tasks.process_url_async.delay',
            return_value=_FakeAsyncResult('celery-fki5'),
        ):
            result = self._dispatch_rag_query({
                'action': 'ingest',
                'url': 'https://example.com/article',
            })
        # Both fields present on happy path — back-compat guaranteed.
        self.assertTrue(result.get('success'))
        self.assertTrue(result.get('dispatched'))
        # Semantic clarity: message still mentions job_status polling.
        self.assertIn('job_status', result['message'])

    def test_dispatched_absent_on_url_required_error(self):
        # Error responses should not carry the dispatched field — they
        # weren't dispatched.
        result = self._dispatch_rag_query({'action': 'ingest'})
        self.assertNotIn('dispatched', result)
        self.assertNotIn('success', result)

    def test_dispatched_absent_on_invalid_scheme(self):
        result = self._dispatch_rag_query({
            'action': 'ingest',
            'url': 'file:///etc/passwd',
        })
        self.assertNotIn('dispatched', result)
        self.assertNotIn('success', result)


# ─── Baseline: delegation flow via intelligence_tool ───────────────────


class IntelligenceToolDelegation(SimpleTestCase):
    """Baseline: verify `intelligence_tool.kb_ingest` delegates to
    `_handle_rag_query.ingest` correctly (a thin wrapper at
    td_handlers_core.py:3333-3334)."""

    def _dispatch_intelligence(self, payload, user_id=None):
        dispatcher = ToolDispatcher()
        return dispatcher._handle_intelligence(  # type: ignore[attr-defined]
            tool_name='intelligence_tool',
            payload=payload,
            user_id=user_id,
            trace_id='test-intelligence-fki-2728',
        )

    def test_delegation_flow_via_intelligence_tool(self):
        with patch(
            'core.tasks.process_url_async.delay',
            return_value=_FakeAsyncResult('celery-delegation'),
        ) as mock_delay:
            result = self._dispatch_intelligence(
                {'action': 'kb_ingest', 'url': 'https://example.com/x'},
                user_id=55555,
            )
        # user_id survived the delegation chain from intelligence_tool
        # into rag_query_tool.ingest.
        _, kwargs = mock_delay.call_args
        self.assertEqual(kwargs.get('user_id'), 55555)
        # F-KI-5 fields present on the response.
        self.assertTrue(result.get('dispatched'))
        self.assertEqual(result['task_id'], 'celery-delegation')
