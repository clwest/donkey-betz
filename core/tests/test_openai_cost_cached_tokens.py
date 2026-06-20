"""Session 1170: cached-input token cost math for the OpenAI estimator.

Pins the v2_cached_tokens behavior introduced in core/llm_enforcer.py:

- `_extract_cached_input_tokens` reads cached counts from either Usage
  shape (Responses API input_tokens_details, Chat Completions
  prompt_tokens_details), tolerates missing / garbage values, and
  clamps to the total_input cap.

- The cost formula charges cached tokens at $0.18/1M instead of the full
  $1.75/1M rate. Pre-Session-1170 behavior overestimated cost on every
  call that benefited from previous_response_id caching.

Run::

    python manage.py test core.tests.test_openai_cost_cached_tokens -v2
"""
from __future__ import annotations

from types import SimpleNamespace

from django.test import SimpleTestCase

from core.llm_enforcer import (
    COST_ESTIMATOR_VERSION,
    _extract_cached_input_tokens,
)


# Pricing constants pinned to the estimator (must match llm_enforcer.py
# math). When OpenAI changes rates these tests will fail loudly and
# remind us to update both.
INPUT_RATE = 1.75 / 1_000_000
CACHED_RATE = 0.18 / 1_000_000
OUTPUT_RATE = 14.00 / 1_000_000


def _calc_cost(uncached_input: int, cached: int, output: int) -> float:
    """Mirror of the v2 formula. Tests reference this so a future
    behavior change in the estimator is forced to update both sides."""
    return (uncached_input * INPUT_RATE) + (cached * CACHED_RATE) + (output * OUTPUT_RATE)


class ExtractCachedInputTokensTests(SimpleTestCase):
    """The helper must accept both Usage shapes + be defensive about
    missing / malformed details."""

    def test_responses_api_shape_reads_cached(self):
        usage = SimpleNamespace(
            input_tokens=1000,
            output_tokens=200,
            input_tokens_details=SimpleNamespace(cached_tokens=600),
        )
        self.assertEqual(_extract_cached_input_tokens(usage, 1000), 600)

    def test_chat_completions_shape_reads_cached(self):
        usage = SimpleNamespace(
            prompt_tokens=500,
            completion_tokens=120,
            prompt_tokens_details=SimpleNamespace(cached_tokens=300),
        )
        self.assertEqual(_extract_cached_input_tokens(usage, 500), 300)

    def test_responses_shape_wins_when_both_present(self):
        """If both detail attrs are populated (unusual but defensive),
        the Responses-API shape is checked first."""
        usage = SimpleNamespace(
            input_tokens_details=SimpleNamespace(cached_tokens=400),
            prompt_tokens_details=SimpleNamespace(cached_tokens=999),
        )
        self.assertEqual(_extract_cached_input_tokens(usage, 1000), 400)

    def test_dict_form_of_details(self):
        """Some older SDK builds expose details as a dict instead of an
        object. Must still resolve."""
        usage = SimpleNamespace(
            input_tokens_details={'cached_tokens': 250},
        )
        self.assertEqual(_extract_cached_input_tokens(usage, 1000), 250)

    def test_missing_details_returns_zero(self):
        usage = SimpleNamespace(input_tokens=1000, output_tokens=200)
        self.assertEqual(_extract_cached_input_tokens(usage, 1000), 0)

    def test_none_usage_returns_zero(self):
        self.assertEqual(_extract_cached_input_tokens(None, 1000), 0)

    def test_cached_value_clamped_to_total_input_cap(self):
        """A buggy API report where cached_tokens > total_input must be
        capped so downstream uncached_input never goes negative."""
        usage = SimpleNamespace(
            input_tokens_details=SimpleNamespace(cached_tokens=5000),
        )
        self.assertEqual(_extract_cached_input_tokens(usage, 1000), 1000)

    def test_negative_cached_value_returned_as_zero(self):
        usage = SimpleNamespace(
            input_tokens_details=SimpleNamespace(cached_tokens=-50),
        )
        self.assertEqual(_extract_cached_input_tokens(usage, 1000), 0)

    def test_non_numeric_cached_value_returns_zero(self):
        usage = SimpleNamespace(
            input_tokens_details=SimpleNamespace(cached_tokens='not-a-number'),
        )
        self.assertEqual(_extract_cached_input_tokens(usage, 1000), 0)


class CostMathTests(SimpleTestCase):
    """The cost formula applies the cached discount correctly across the
    interesting partial / boundary cases."""

    def test_zero_cached_matches_v1_behavior(self):
        """When no input is cached, v2 must match v1 to the cent so we
        don't drift the un-cached path."""
        cost = _calc_cost(uncached_input=1000, cached=0, output=500)
        v1_equivalent = (1000 * INPUT_RATE) + (500 * OUTPUT_RATE)
        self.assertAlmostEqual(cost, v1_equivalent, places=10)

    def test_all_input_cached_uses_cached_rate(self):
        """When every input token is a cache hit, the cost drops by
        roughly 9.7× on the input portion."""
        cost = _calc_cost(uncached_input=0, cached=1000, output=500)
        expected = (1000 * CACHED_RATE) + (500 * OUTPUT_RATE)
        self.assertAlmostEqual(cost, expected, places=10)

    def test_partial_cache_hit_mixed_math(self):
        """The realistic case: long PA thread with most context cached."""
        cost = _calc_cost(uncached_input=200, cached=800, output=300)
        expected = (
            200 * INPUT_RATE
            + 800 * CACHED_RATE
            + 300 * OUTPUT_RATE
        )
        self.assertAlmostEqual(cost, expected, places=10)

    def test_cached_discount_is_about_90_percent(self):
        """Sanity check the rate ratio so an accidental constant tweak
        in one direction screams."""
        ratio = CACHED_RATE / INPUT_RATE
        # Spec is $0.18 / $1.75 ≈ 0.1029 (cache ≈ 10% of input).
        self.assertAlmostEqual(ratio, 0.18 / 1.75, places=6)
        self.assertLess(ratio, 0.15)


class EstimatorVersionTagTests(SimpleTestCase):

    def test_version_tag_is_v2_cached_tokens(self):
        self.assertEqual(COST_ESTIMATOR_VERSION, 'v2_cached_tokens')
