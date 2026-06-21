"""
Session 1189 PR-3A: CATEGORY_ALIASES + _normalize_categories tests.

Background: Session 1188 supply recon found that `creative`, `crypto`,
`sports` are dead `AGENT_SPIDER_MAPPINGS` values (zero `is_actionable`
supply in 30d) because they're not real `SpiderData.data_type` keys.
The real buckets are `design`/`visual_trends`/`video`, `blockchain`,
and `sports_odds`/`sports_news` respectively. PR-3A introduces
`CATEGORY_ALIASES` + `_normalize_categories` so the dead keys auto-expand
at query time without breaking external callers (soft transition per
Rigby's spec — deliverable `a48e1164-edc6-49d8-bc70-135bedb614a9`).

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_spider_context_aliases -v2 --keepdb
"""

from django.test import SimpleTestCase

from core.services.spider_context_builder import (
    CATEGORY_ALIASES,
    KNOWN_DATA_TYPES,
    SpiderContextBuilder,
)


class CategoryAliasesTests(SimpleTestCase):
    """The module-level CATEGORY_ALIASES dict must keep the three dead
    keys with the right real-data_type expansions."""

    def test_creative_aliases_to_design_visual_trends_video(self):
        self.assertEqual(CATEGORY_ALIASES['creative'], ['design', 'visual_trends', 'video'])

    def test_crypto_aliases_to_blockchain(self):
        self.assertEqual(CATEGORY_ALIASES['crypto'], ['blockchain'])

    def test_sports_aliases_to_sports_odds_sports_news(self):
        self.assertEqual(CATEGORY_ALIASES['sports'], ['sports_odds', 'sports_news'])

    def test_security_aliases_to_cybersecurity(self):
        """PR-3B: `security` was used by cto/code_generator/code_review/
        devops/autonomous_content_studio but isn't a real data_type
        (real bucket is `cybersecurity` with 15 actionable / 30d). The
        alias keeps the semantic mapping while resolving to the real
        bucket at query time."""
        self.assertEqual(CATEGORY_ALIASES['security'], ['cybersecurity'])

    def test_every_alias_expansion_is_a_known_data_type(self):
        """If an alias resolves to something not in KNOWN_DATA_TYPES the
        normalization will WARN downstream — guard the snapshot at the
        test layer too so we catch drift early."""
        for source, expansion in CATEGORY_ALIASES.items():
            for real in expansion:
                self.assertIn(
                    real, KNOWN_DATA_TYPES,
                    f"alias '{source}' expands to '{real}' which isn't "
                    f"in KNOWN_DATA_TYPES — either add it or drop the alias",
                )


class NormalizeCategoriesTests(SimpleTestCase):
    def setUp(self):
        self.builder = SpiderContextBuilder()
        # Process-wide warned-set: clear so warn-once assertions are
        # deterministic regardless of test order.
        SpiderContextBuilder._warned_unknown_categories = set()

    def test_dead_keys_expand_to_real_buckets(self):
        self.assertEqual(
            self.builder._normalize_categories(['creative']),
            ['design', 'visual_trends', 'video'],
        )
        self.assertEqual(self.builder._normalize_categories(['crypto']), ['blockchain'])
        self.assertEqual(
            self.builder._normalize_categories(['sports']),
            ['sports_odds', 'sports_news'],
        )

    def test_real_data_types_pass_through_unchanged(self):
        self.assertEqual(
            self.builder._normalize_categories(['tech', 'news', 'ai_ml']),
            ['tech', 'news', 'ai_ml'],
        )

    def test_security_expands_to_cybersecurity(self):
        """PR-3B: security agents (cto, code_review, devops...) keep
        `security` in their per-agent lists; the normalizer expands at
        query time so they actually hit cybersecurity (the real bucket)."""
        self.assertEqual(self.builder._normalize_categories(['security']), ['cybersecurity'])

    def test_mixed_aliases_and_real_dedupe_and_preserve_order(self):
        # creative → design+visual_trends+video; tech passes through;
        # sports → sports_odds+sports_news; order preserved across the
        # iteration; no duplicates.
        result = self.builder._normalize_categories(['creative', 'tech', 'sports', 'design'])
        self.assertEqual(
            result,
            ['design', 'visual_trends', 'video', 'tech', 'sports_odds', 'sports_news'],
        )

    def test_unknown_category_passes_through_with_one_time_warn(self):
        with self.assertLogs('core.services.spider_context_builder', level='WARNING') as cm:
            result1 = self.builder._normalize_categories(['totally_invented'])
        self.assertEqual(result1, ['totally_invented'])
        warn_count_first = sum(1 for m in cm.output if 'totally_invented' in m)
        self.assertEqual(warn_count_first, 1)

        # Second call with the SAME unknown should NOT re-emit a warning.
        try:
            with self.assertLogs('core.services.spider_context_builder', level='WARNING') as cm2:
                self.builder._normalize_categories(['totally_invented'])
        except AssertionError:
            pass  # expected — no logs at WARNING level
        else:
            for msg in cm2.output:
                self.assertNotIn('totally_invented', msg)

    def test_empty_or_invalid_input_returns_empty(self):
        self.assertEqual(self.builder._normalize_categories([]), [])
        self.assertEqual(self.builder._normalize_categories([None, 42]), [])


class BuildContextRequestedVsResolvedTests(SimpleTestCase):
    """Integration: build_context_for_agent must populate both
    categories_requested (pre-alias) and categories_queried (post-alias)
    so the AC instrumentation can record the divergence."""

    def setUp(self):
        self.builder = SpiderContextBuilder()
        # Use a fake intelligence service so we don't hit the real DB.
        fake_service = type('FakeIntel', (), {
            'get_trending_topics': staticmethod(lambda **kw: []),
            'get_tech_trends': staticmethod(lambda **kw: None),
            'get_creative_trends': staticmethod(lambda **kw: None),
            'get_market_insights': staticmethod(lambda **kw: None),
            'get_job_market_summary': staticmethod(lambda **kw: None),
            'search_spider_data': staticmethod(lambda **kw: None),
        })()
        self.builder._intelligence_service = fake_service

    def test_image_substring_match_still_includes_dead_creative_in_requested(self):
        """`ImageEditingAgent` matches the legacy `image` substring key
        whose mapping still contains `'creative'`. After PR-3A,
        categories_requested should preserve `creative` while
        categories_queried should resolve to the real buckets."""
        ctx = self.builder.build_context_for_agent(
            agent_name='ImageEditingAgent', task='retouch a photo',
        )
        self.assertIn('creative', ctx['categories_requested'])
        # creative dropped; design/visual_trends/video added
        self.assertNotIn('creative', ctx['categories_queried'])
        for real in ('design', 'visual_trends', 'video'):
            self.assertIn(real, ctx['categories_queried'])

    def test_imageagent_categories_queried_never_contains_dead_creative(self):
        """ImageAgent's explicit `imageagent` key uses real data_type
        values (Session 1188 PR-2). Even when a task triggers the
        TASK_KEYWORD_BOOSTS entry for `logo` → `['creative']` —
        adding `creative` to categories_requested — the alias layer
        ensures categories_queried (post-alias) NEVER contains the
        dead key. Real data_type buckets are always what's queried."""
        ctx = self.builder.build_context_for_agent(
            agent_name='ImageAgent', task='generate a logo',
        )
        # task boost adds 'creative' to requested
        self.assertIn('creative', ctx['categories_requested'])
        # alias layer expanded it before query
        self.assertNotIn('creative', ctx['categories_queried'])
        for real in ('design', 'visual_trends', 'video'):
            self.assertIn(real, ctx['categories_queried'])
