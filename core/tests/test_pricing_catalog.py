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


# =============================================================================
# S2855 Phase 2A — analytics-plane migration
# =============================================================================


class PricingCatalogSeparationTests(SimpleTestCase):
    """Embedding rates live in embedding_service.EMBEDDING_COSTS — NOT here.

    Rigby zoom-out fold: adding embeddings to MODEL_PRICES would create dual
    sources of truth for embedding pricing. Enforce the separation.
    """

    def test_embedding_models_not_in_chat_pricing_catalog(self):
        for model_id in (
            'text-embedding-3-small',
            'text-embedding-3-large',
            'text-embedding-ada-002',
        ):
            self.assertNotIn(model_id, MODEL_PRICES)

    def test_embedding_service_owns_embedding_rates(self):
        from core.services.embedding_service import EMBEDDING_COSTS
        # Assert the canonical embedding rates present (guards against silent
        # rate drift that would diverge from OpenAI pricing).
        from decimal import Decimal as D
        self.assertEqual(EMBEDDING_COSTS['text-embedding-3-small'], D('0.02'))
        self.assertEqual(EMBEDDING_COSTS['text-embedding-3-large'], D('0.13'))
        self.assertEqual(EMBEDDING_COSTS['text-embedding-ada-002'], D('0.10'))


class TrackLLMAnalyticsModelAttributionTests(SimpleTestCase):
    """base_agent._track_llm_analytics respects the _last_llm_model instance attr.

    Pre-S2855 the method hardcoded ``service='gpt-5-mini'`` on every
    ``AdvancedAnalyticsService.track_cost`` call irrespective of the actual
    model used — silently mis-attributing every gpt-5.2 call to gpt-5-mini in
    CostTracking, and mispricing at $3/$12 per 1M (matched neither model).
    """

    def _fake_response(self, prompt_tokens=100, completion_tokens=50, model=None):
        from types import SimpleNamespace
        usage = SimpleNamespace(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        r = SimpleNamespace(usage=usage)
        if model is not None:
            r.model = model
        return r

    def _make_fake_agent(self, last_model=None):
        """Build the minimum viable BaseAgent needed by _track_llm_analytics."""
        from core.agents.base_agent import BaseAgent

        class _FakeAgent(BaseAgent):
            system_prompt = 'fake'

            def execute(self, task, context=None, **kwargs):  # noqa: ARG002
                return {'success': True}

        # Bypass __init__ (touches LLM/spider plumbing); set only what
        # _track_llm_analytics reads.
        agent = _FakeAgent.__new__(_FakeAgent)
        agent.name = 'test-agent'
        agent.user = None  # user=None → skips track_cost + track_usage
        if last_model is not None:
            agent._last_llm_model = last_model
        return agent

    def test_uses_last_llm_model_when_set(self):
        """gpt-5.2 attributed correctly; not silently rewritten to gpt-5-mini."""
        from unittest.mock import patch
        agent = self._make_fake_agent(last_model='gpt-5.2')
        agent.user = object()  # non-None so track_cost fires
        response = self._fake_response(100, 50)

        with patch('core.views_analytics.AdvancedAnalyticsService.track_cost') as tc, \
             patch('core.views_analytics.AdvancedAnalyticsService.track_usage'), \
             patch('core.models_unified_system.PerformanceLog.objects.create'):
            agent._track_llm_analytics(response, start_time=0.0)

        tc.assert_called_once()
        kwargs = tc.call_args.kwargs
        self.assertEqual(kwargs['service'], 'gpt-5.2')
        # gpt-5.2 canonical: 100*1.75/1M + 50*14/1M = 0.000175 + 0.0007 = 0.000875
        self.assertAlmostEqual(kwargs['estimated_cost_usd'], 0.000875, places=8)

    def test_falls_back_to_response_model_when_no_last_llm_model(self):
        from unittest.mock import patch
        agent = self._make_fake_agent(last_model=None)
        agent.user = object()
        response = self._fake_response(100, 50, model='gpt-5.2')

        with patch('core.views_analytics.AdvancedAnalyticsService.track_cost') as tc, \
             patch('core.views_analytics.AdvancedAnalyticsService.track_usage'), \
             patch('core.models_unified_system.PerformanceLog.objects.create'):
            agent._track_llm_analytics(response, start_time=0.0)

        self.assertEqual(tc.call_args.kwargs['service'], 'gpt-5.2')

    def test_final_fallback_to_gpt_5_mini(self):
        from unittest.mock import patch
        agent = self._make_fake_agent(last_model=None)
        agent.user = object()
        response = self._fake_response(100, 50)  # no .model attr

        with patch('core.views_analytics.AdvancedAnalyticsService.track_cost') as tc, \
             patch('core.views_analytics.AdvancedAnalyticsService.track_usage'), \
             patch('core.models_unified_system.PerformanceLog.objects.create'):
            agent._track_llm_analytics(response, start_time=0.0)

        self.assertEqual(tc.call_args.kwargs['service'], 'gpt-5-mini')
        # gpt-5-mini canonical: 100*0.5/1M + 50*1.5/1M = 0.00005 + 0.000075 = 0.000125
        self.assertAlmostEqual(
            tc.call_args.kwargs['estimated_cost_usd'], 0.000125, places=8
        )

    def test_pre_phase_2a_wrong_rates_would_have_differed(self):
        """Regression witness: the pre-S2855 formula priced 100/50 at $0.000900.

        (100 * 0.003/1000) + (50 * 0.012/1000) = 0.0003 + 0.0006 = 0.0009.
        gpt-5.2 canonical is 0.000875; gpt-5-mini canonical is 0.000125.
        Neither matches — proving the pre-fix formula was rate-broken.
        """
        pre_fix = (100 * 0.003 / 1000) + (50 * 0.012 / 1000)
        self.assertAlmostEqual(pre_fix, 0.0009, places=8)
        canonical_5_2 = float(calculate_cost('gpt-5.2', 100, 50))
        canonical_mini = float(calculate_cost('gpt-5-mini', 100, 50))
        self.assertNotAlmostEqual(pre_fix, canonical_5_2, places=6)
        self.assertNotAlmostEqual(pre_fix, canonical_mini, places=6)


class DisplayFallbackEstimatorTests(SimpleTestCase):
    """views_agent_dashboard + views_analytics fallback rates are canonical.

    Pre-S2855 these hardcoded blended per-1M rates ($0.375 dashboard,
    $10 analytics) with unclear provenance. Now they price through
    ``calculate_cost('gpt-5-mini', tokens, 0)`` with an ``estimated=True``
    flag telling the frontend to label the number.
    """

    def test_dashboard_default_display_model_is_canonical_gpt_5_mini_rate(self):
        # 750 tokens (dashboard solution baseline) priced as gpt-5-mini input:
        # 750 * 0.5/1M = 0.000375
        self.assertEqual(
            calculate_cost('gpt-5-mini', 750, 0, 0),
            (750 * MODEL_PRICES['gpt-5-mini']['input']) / 1_000_000,
        )

    def test_analytics_default_display_model_is_canonical_gpt_5_mini_rate(self):
        # 10_000 tokens (analytics rollup baseline):
        # 10000 * 0.5/1M = 0.005
        from decimal import Decimal as D
        self.assertEqual(
            calculate_cost('gpt-5-mini', 10_000, 0, 0),
            D('0.005'),
        )


class TriageSpiderEmbeddingsCostSourceTests(SimpleTestCase):
    """triage_spider_embeddings sources embedding rate from EMBEDDING_COSTS.

    Pre-S2855 the management command inlined ``* 0.02`` (correct rate for
    text-embedding-3-small at the time it was written but decoupled from
    the canonical embedding-rate table). Post-S2855 it imports from
    ``core.services.embedding_service.EMBEDDING_COSTS`` so any future rate
    update lands in one place.
    """

    def test_management_command_imports_embedding_costs_from_canonical_table(self):
        import ast
        from pathlib import Path
        source = Path(
            'core/management/commands/triage_spider_embeddings.py'
        ).read_text()
        tree = ast.parse(source)
        imports = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module == 'core.services.embedding_service'
        ]
        self.assertTrue(
            imports,
            'triage_spider_embeddings must import from embedding_service; '
            'inlining embedding rates duplicates the canonical table.',
        )
        imported_names = {
            alias.name for imp in imports for alias in imp.names
        }
        self.assertIn('EMBEDDING_COSTS', imported_names)

    def test_management_command_no_longer_inlines_0_02_rate(self):
        from pathlib import Path
        source = Path(
            'core/management/commands/triage_spider_embeddings.py'
        ).read_text()
        # Substring guard — old formula would contain `* 0.02` literal.
        self.assertNotIn('/ 1_000_000 * 0.02', source)
