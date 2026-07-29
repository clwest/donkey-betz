"""S3038 A3 — Tests for llm_error_classifier + LLMCallLog.save() hook.

Discharges S3037 Reliability Audit Step 4: 305 failed rows in 90d with empty
error_type blocked any error-type-based alerting. Classifier + hook auto-tag
error_type at write time; backfill command handles historical rows.
"""

from django.test import TestCase

from core.models_llm_routing import LLMCallLog
from core.services.llm_error_classifier import (
    KNOWN_ERROR_TYPES,
    classify_llm_error,
)


class LLMErrorClassifierTests(TestCase):
    """Pattern coverage — one case per tag + edge cases."""

    def test_empty_message_returns_empty(self):
        self.assertEqual(classify_llm_error(''), '')
        self.assertEqual(classify_llm_error(None), '')

    def test_connection_error_dominant_case(self):
        # Actual message dominating the S3037 audit-window data (305/305 rows).
        self.assertEqual(classify_llm_error('Connection error.'), 'connection_error')
        self.assertEqual(
            classify_llm_error('openai.APIConnectionError: connection reset'),
            'connection_error',
        )

    def test_rate_limit_variants(self):
        self.assertEqual(classify_llm_error('RateLimitError: too many'), 'rate_limit')
        self.assertEqual(classify_llm_error('HTTP 429 - rate limit exceeded'), 'rate_limit')
        self.assertEqual(classify_llm_error('rate_limit hit'), 'rate_limit')

    def test_auth_error_variants(self):
        self.assertEqual(
            classify_llm_error('openai.AuthenticationError: invalid API key'),
            'auth_error',
        )
        self.assertEqual(classify_llm_error('HTTP 401 unauthorized'), 'auth_error')

    def test_context_window_variants(self):
        self.assertEqual(
            classify_llm_error('ContextWindowExceededError: 200000 > 128000'),
            'context_window_exceeded',
        )
        self.assertEqual(
            classify_llm_error("This model's maximum context length is 8192 tokens"),
            'context_window_exceeded',
        )

    def test_timeout_variants(self):
        self.assertEqual(classify_llm_error('APITimeoutError'), 'timeout')
        self.assertEqual(classify_llm_error('Request timed out after 60s'), 'timeout')

    def test_server_error_5xx(self):
        # 500/502/504 go to server_error (503 is service_unavailable).
        self.assertEqual(classify_llm_error('HTTP 500 internal server error'), 'server_error')
        self.assertEqual(classify_llm_error('HTTP 502 bad gateway'), 'server_error')
        self.assertEqual(classify_llm_error('HTTP 503 service unavailable'), 'service_unavailable')

    def test_invalid_request_variants(self):
        self.assertEqual(classify_llm_error('BadRequestError: bad shape'), 'invalid_request')
        self.assertEqual(classify_llm_error('HTTP 400 invalid_request'), 'invalid_request')

    def test_unknown_message_returns_unknown_error(self):
        # Non-empty message that matches no pattern — the fallback tag is
        # itself a signal to widen the pattern table.
        self.assertEqual(
            classify_llm_error('Something totally weird happened'),
            'unknown_error',
        )

    def test_most_specific_wins(self):
        # A message containing both 'RateLimitError' and '500' should
        # classify as rate_limit (more specific) rather than server_error.
        self.assertEqual(
            classify_llm_error('RateLimitError: server returned 500'),
            'rate_limit',
        )

    def test_tag_fits_charfield_100(self):
        # LLMCallLog.error_type is max_length=100.
        for tag in KNOWN_ERROR_TYPES:
            self.assertLessEqual(len(tag), 100)


class LLMCallLogSaveHookTests(TestCase):
    """The save() hook auto-populates error_type when the write site skipped it."""

    def _build(self, **overrides):
        defaults = dict(
            agent_name='TestAgent',
            provider='openai',
            model_id='gpt-5.2',
            success=False,
        )
        defaults.update(overrides)
        return LLMCallLog(**defaults)

    def test_save_hook_populates_from_empty(self):
        row = self._build(error_message='Connection error.')
        self.assertEqual(row.error_type, '')
        row.save()
        row.refresh_from_db()
        self.assertEqual(row.error_type, 'connection_error')

    def test_save_hook_respects_caller_intent(self):
        # If the write site set error_type explicitly, don't clobber it —
        # this preserves any provider-specific tagging that the enforcer
        # or router may add in the future.
        row = self._build(
            error_message='RateLimitError: too many',
            error_type='provider_custom_tag',
        )
        row.save()
        row.refresh_from_db()
        self.assertEqual(row.error_type, 'provider_custom_tag')

    def test_save_hook_leaves_success_rows_alone(self):
        # error_message empty → hook is a no-op regardless of success.
        row = self._build(success=True)
        row.save()
        row.refresh_from_db()
        self.assertEqual(row.error_type, '')

    def test_save_hook_tags_unknown_when_no_match(self):
        row = self._build(error_message='completely unclassifiable weirdness')
        row.save()
        row.refresh_from_db()
        self.assertEqual(row.error_type, 'unknown_error')

    def test_save_hook_fails_open_on_classifier_exception(self):
        # If the classifier ever raises (regex import error, etc.) the
        # LLMCallLog write must still succeed — telemetry substrate must
        # never bounce writes on its own accessory logic.
        from unittest import mock
        with mock.patch(
            'core.services.llm_error_classifier.classify_llm_error',
            side_effect=RuntimeError('classifier boom'),
        ):
            row = self._build(error_message='Connection error.')
            row.save()  # must not raise
            row.refresh_from_db()
            self.assertEqual(row.error_type, '')
