"""
S2854 pricing canonicalization arc — Phase 1 (C+).

Locks in the canonical per-1M-token rates for every model the billing paths
(``core/llm_enforcer.py`` + ``core/services/llm_provider_registry.py`` +
``core/services/ops_autopilot/pricing.py``) delegate to.

Guards against silent rate drift in ``core/services/pricing_catalog.py``.
"""

from decimal import Decimal

from django.test import SimpleTestCase

from core.services.pricing_catalog import (
    MODEL_PRICES,
    calculate_cost,
    estimate_uncached_cost,
    get_model_pricing,
)


class ModelPricesTableTests(SimpleTestCase):
    """Rate assertions per model — canonical values as of S2854."""

    def test_gpt_5_2_matches_enforcer_billing_lineage(self):
        p = MODEL_PRICES['gpt-5.2']
        self.assertEqual(p['input'], Decimal('1.75'))
        self.assertEqual(p['output'], Decimal('14.00'))
        self.assertEqual(p['cached_input'], Decimal('0.18'))

    def test_gpt_5_mini_matches_enforcer_billing_lineage(self):
        p = MODEL_PRICES['gpt-5-mini']
        self.assertEqual(p['input'], Decimal('0.50'))
        self.assertEqual(p['output'], Decimal('1.50'))
        self.assertNotIn('cached_input', p)

    def test_haiku_split_input_output_rates(self):
        p = MODEL_PRICES['claude-3-haiku-20240307']
        self.assertEqual(p['input'], Decimal('0.25'))
        self.assertEqual(p['output'], Decimal('1.25'))


class CalculateCostTests(SimpleTestCase):
    """Math correctness across cached / uncached / unknown / Haiku paths."""

    def test_gpt_5_2_uncached_math(self):
        # 100 * 1.75/1M + 50 * 14/1M = 0.000175 + 0.0007 = 0.000875
        self.assertEqual(
            calculate_cost('gpt-5.2', 100, 50),
            Decimal('0.000875'),
        )

    def test_gpt_5_2_with_cached_input(self):
        # 100 uncached + 50 out + 200 cached
        # = 100*1.75/1M + 50*14/1M + 200*0.18/1M = 0.000911
        self.assertEqual(
            calculate_cost('gpt-5.2', 100, 50, cached_input_tokens=200),
            Decimal('0.000911'),
        )

    def test_gpt_5_mini_pins_real_llmcalllog_row(self):
        """Matches the single real LLMCallLog row seen at S2853 close ($0.000399)."""
        # 35 * 0.5/1M + 254 * 1.5/1M = 0.0000175 + 0.000381 = 0.0003985
        self.assertEqual(
            calculate_cost('gpt-5-mini', 35, 254),
            Decimal('0.0003985'),
        )

    def test_haiku_split_math_fixes_blended_undercharge(self):
        """
        Pre-S2854 the enforcer's ``_call_claude`` applied a single blended
        $0.25/1M to (input + output) tokens, silently under-charging every
        Claude call because output is 5x input rate.
        """
        # 100 * 0.25/1M + 200 * 1.25/1M = 0.000025 + 0.00025 = 0.000275
        canonical = calculate_cost('claude-3-haiku-20240307', 100, 200)
        self.assertEqual(canonical, Decimal('0.000275'))
        # Pre-S2854 buggy blend would have priced this as:
        # (100 + 200) * 0.25 / 1M = 0.000075 — undercharge of 3.67x
        old_blended = Decimal('300') * Decimal('0.25') / Decimal('1000000')
        self.assertLess(old_blended, canonical)

    def test_unknown_model_falls_back_to_conservative_rate(self):
        # 1000 * 1.00/1M + 500 * 3.00/1M = 0.001 + 0.0015 = 0.0025
        self.assertEqual(
            calculate_cost('unknown-model-42', 1000, 500),
            Decimal('0.0025'),
        )

    def test_zero_tokens_bills_zero(self):
        self.assertEqual(
            calculate_cost('gpt-5.2', 0, 0),
            Decimal('0'),
        )

    def test_cached_tokens_on_model_without_cached_rate_uses_input_rate(self):
        # gpt-5-mini has no 'cached_input' key; cached tokens billed at input rate.
        # 100 in + 50 out + 200 cached at 0.50/1M input
        # = 100*0.5/1M + 50*1.5/1M + 200*0.5/1M = 0.00005 + 0.000075 + 0.0001 = 0.000225
        self.assertEqual(
            calculate_cost('gpt-5-mini', 100, 50, cached_input_tokens=200),
            Decimal('0.000225'),
        )


class EstimateUncachedCostTests(SimpleTestCase):
    """Backward-compat shim used by workspace_budget_tool.enforcement_report."""

    def test_returns_none_for_unknown_model(self):
        """Preserves the ops_autopilot 'skip unknown, don't guess' contract."""
        self.assertIsNone(estimate_uncached_cost('unknown-model-42', 100, 50))

    def test_returns_decimal_for_known_model(self):
        result = estimate_uncached_cost('gpt-5-mini', 35, 254)
        self.assertEqual(result, Decimal('0.0003985'))


class GetModelPricingTests(SimpleTestCase):

    def test_returns_none_for_unknown(self):
        self.assertIsNone(get_model_pricing('unknown-model-42'))

    def test_returns_full_dict_for_gpt_5_2_including_cached_key(self):
        p = get_model_pricing('gpt-5.2')
        self.assertIsNotNone(p)
        assert p is not None  # narrow for pyright
        self.assertIn('cached_input', p)


class OpsAutopilotShimTests(SimpleTestCase):
    """Verify the S2853 ops_autopilot/pricing.py shim still re-exports canonical."""

    def test_shim_reexports_are_the_same_objects(self):
        from core.services.ops_autopilot.pricing import (
            MODEL_PRICES as shim_prices,
            calculate_cost as shim_calculate_cost,
            estimate_uncached_cost as shim_estimate_uncached_cost,
        )
        self.assertIs(shim_prices, MODEL_PRICES)
        self.assertIs(shim_calculate_cost, calculate_cost)
        self.assertIs(shim_estimate_uncached_cost, estimate_uncached_cost)
