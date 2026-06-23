"""Tests for the reasoning-contract guard in core/services/openai_client_factory.

Session 1216 Phase E (PR #1). Covers:

- Pure function ``apply_reasoning_guard`` across all 3 modes
- Model-substring gating (only triggers for gpt-5.x)
- Boundary cases (None/empty model, no forbidden kwargs present)
- Unknown env var value falls back to ``warn``
- Wrapped factory client raises in error mode before any network call
"""

import os
from unittest import TestCase
from unittest.mock import patch

from core.services.openai_client_factory import (
    ReasoningGuardViolation,
    apply_reasoning_guard,
    get_openai_client,
    _CLIENT_CACHE,
)


class ApplyReasoningGuardTests(TestCase):
    """Unit tests for the pure-function guard."""

    def test_non_reasoning_model_passes_through(self):
        kwargs = {"max_tokens": 100, "temperature": 0.5}
        result = apply_reasoning_guard(kwargs, "gpt-4o", "test")
        self.assertIs(result, kwargs)

    def test_none_model_passes_through(self):
        kwargs = {"max_tokens": 100}
        self.assertIs(apply_reasoning_guard(kwargs, None, "test"), kwargs)

    def test_empty_model_passes_through(self):
        kwargs = {"max_tokens": 100}
        self.assertIs(apply_reasoning_guard(kwargs, "", "test"), kwargs)

    def test_gpt5_with_no_forbidden_passes_through(self):
        kwargs = {"max_completion_tokens": 200, "reasoning_effort": "medium"}
        self.assertIs(apply_reasoning_guard(kwargs, "gpt-5-mini", "test"), kwargs)

    @patch.dict(os.environ, {"OPENAI_REASONING_GUARD": "warn"}, clear=False)
    def test_warn_mode_preserves_kwargs(self):
        kwargs = {"max_tokens": 100, "temperature": 0.5, "messages": []}
        result = apply_reasoning_guard(kwargs, "gpt-5-mini", "warn_test")
        self.assertIs(result, kwargs)
        self.assertIn("max_tokens", result)
        self.assertIn("temperature", result)

    @patch.dict(os.environ, {"OPENAI_REASONING_GUARD": "strip"}, clear=False)
    def test_strip_mode_removes_forbidden_preserves_allowed(self):
        kwargs = {
            "max_tokens": 100,
            "temperature": 0.5,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
            "max_completion_tokens": 200,
            "messages": [{"role": "user", "content": "hi"}],
        }
        result = apply_reasoning_guard(kwargs, "gpt-5-mini", "strip_test")
        for forbidden in ("max_tokens", "temperature", "top_p",
                          "frequency_penalty", "presence_penalty"):
            self.assertNotIn(forbidden, result)
        self.assertIn("max_completion_tokens", result)
        self.assertIn("messages", result)
        # Original dict unchanged
        self.assertIn("max_tokens", kwargs)

    @patch.dict(os.environ, {"OPENAI_REASONING_GUARD": "error"}, clear=False)
    def test_error_mode_raises_violation(self):
        with self.assertRaises(ReasoningGuardViolation) as ctx:
            apply_reasoning_guard(
                {"max_tokens": 100}, "gpt-5-mini", "error_test",
            )
        self.assertIn("gpt-5-mini", str(ctx.exception))
        self.assertIn("max_tokens", str(ctx.exception))
        self.assertIn("max_completion_tokens", str(ctx.exception))

    @patch.dict(os.environ, {"OPENAI_REASONING_GUARD": "destroy"}, clear=False)
    def test_unknown_mode_falls_back_to_warn(self):
        kwargs = {"max_tokens": 100}
        result = apply_reasoning_guard(kwargs, "gpt-5-mini", "unknown_mode")
        self.assertIs(result, kwargs)

    @patch.dict(os.environ, {"OPENAI_REASONING_GUARD": ""}, clear=False)
    def test_empty_env_defaults_to_warn(self):
        kwargs = {"max_tokens": 100}
        result = apply_reasoning_guard(kwargs, "gpt-5-mini", "empty_env")
        self.assertIs(result, kwargs)

    def test_gpt5_substring_match_covers_variants(self):
        for model in ("gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-5-2026-04-01"):
            with patch.dict(os.environ, {"OPENAI_REASONING_GUARD": "error"}, clear=False):
                with self.assertRaises(ReasoningGuardViolation,
                                       msg=f"model={model}"):
                    apply_reasoning_guard({"max_tokens": 100}, model, "")

    def test_non_gpt5_models_not_gated(self):
        for model in ("gpt-4o", "gpt-4.1", "o3-mini", "qwen2.5:14b"):
            with patch.dict(os.environ, {"OPENAI_REASONING_GUARD": "error"}, clear=False):
                # Should NOT raise — these aren't gpt-5.x
                result = apply_reasoning_guard(
                    {"max_tokens": 100, "temperature": 0.5}, model, "",
                )
                self.assertIn("max_tokens", result, f"model={model}")


class FactoryClientGuardTests(TestCase):
    """Verify that factory-returned clients have the guard installed
    on chat.completions.create."""

    def setUp(self):
        _CLIENT_CACHE.clear()

    @patch.dict(os.environ, {"OPENAI_REASONING_GUARD": "error"}, clear=False)
    def test_wrapped_create_raises_before_network_call(self):
        client = get_openai_client()
        with self.assertRaises(ReasoningGuardViolation):
            client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=100,
            )

    @patch.dict(os.environ, {"OPENAI_REASONING_GUARD": "error"}, clear=False)
    def test_wrapped_create_allows_non_gpt5(self):
        """For non-gpt-5 models, guard should not interfere even in error mode.
        This test confirms the guard short-circuits before making a network
        call by checking that ReasoningGuardViolation is NOT raised — any
        downstream HTTP failure is acceptable here."""
        client = get_openai_client()
        try:
            client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "hi"}],
                max_tokens=100,
            )
        except ReasoningGuardViolation:
            self.fail("guard fired on non-gpt-5 model")
        except Exception:
            # Any other exception (auth, network, model not available) is fine —
            # we only care that the guard did not preemptively raise.
            pass
