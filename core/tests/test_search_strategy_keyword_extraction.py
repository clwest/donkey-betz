"""Session 1092: Regression tests for keyword extraction in search_strategy_service.

Bug history (canary v2): ResearchAgent appended `[User Context: ...]` to the
task before query generation. The keyword extractor included that prose,
and downstream callers used `sorted(...)[:N]` to pick top keywords —
producing alphabetically-first noise like "alex anal balanced based" while
burying actual subject words like "stock" and "signals". The agent then
searched garbage queries and got marine biology / labor docs instead of
market data.

These tests assert:
  1. _extract_keywords strips ResearchAgent's user-context tail
  2. _extract_keywords returns an ordered list (not a set), so callers
     preserve natural reading order rather than sorting alphabetically
  3. The literal canary task produces stock-relevant top keywords
"""

from django.test import SimpleTestCase

from core.services.search_strategy_service import (
    _extract_keywords,
    _generate_narrow_queries,
)


class TestExtractKeywords(SimpleTestCase):
    def test_strips_user_context_tail(self):
        text = (
            "Stock market signals from the last 24 hours\n\n"
            "[User Context: Researching for: Alex Chen; "
            "User profile: Entrepreneur, balanced, analytical mindset]"
        )
        kw = _extract_keywords(text)
        self.assertNotIn('alex', kw, 'user name leaked into keywords')
        self.assertNotIn('chen', kw, 'user surname leaked into keywords')
        self.assertNotIn('analytical', kw, 'profile attribute leaked')
        self.assertNotIn('entrepreneur', kw, 'profile attribute leaked')
        self.assertIn('stock', kw)
        self.assertIn('market', kw)
        self.assertIn('signals', kw)

    def test_strips_past_research_patterns_tail(self):
        text = (
            "Quarterly revenue analysis for SaaS startups\n\n"
            "[Past research patterns: Profile: Role: Entrepreneur]"
        )
        kw = _extract_keywords(text)
        self.assertNotIn('entrepreneur', kw)
        self.assertNotIn('profile', kw)
        self.assertIn('quarterly', kw)
        self.assertIn('revenue', kw)
        self.assertIn('saas', kw)

    def test_returns_ordered_list_not_alphabetical_set(self):
        """Subject words should appear ahead of meta words after stopword
        filtering, even when meta words sort earlier alphabetically."""
        text = "Produce a concise summary of stock market signals"
        kw = _extract_keywords(text)
        # Pre-fix bug: alphabetical sort put 'concise' (c), 'market' (m),
        # 'produce' (p), 'signals' (s), 'stock' (s), 'summary' (s) first,
        # burying subject words. After Session 1092: 'produce', 'concise',
        # and 'summary' are stopwords (instruction-meta), and 'stock'
        # leads in original order.
        self.assertIsInstance(kw, list)
        self.assertEqual(kw[0], 'stock')  # first surviving subject word
        self.assertEqual(kw[:3], ['stock', 'market', 'signals'])

    def test_canary_v2_task_extracts_subject_words(self):
        """The exact canary v2 task should produce stock-relevant top-6 keywords."""
        task = (
            "Produce a concise one-paragraph summary of the most important "
            "stock market signals from the last 24 hours (no citations needed). "
            "Title the deliverable: CANARY v2: Stock Signals Summary."
        )
        kw = _extract_keywords(task)
        top6 = kw[:6]
        # The pre-fix bug produced "canary citations concise deliverable hours
        # important" — subject words missing.  The fix should put "stock" and
        # "signals" inside the first 6.
        self.assertIn('stock', top6, f'stock missing from top-6: {top6}')
        self.assertIn('signals', top6, f'signals missing from top-6: {top6}')

    def test_handles_empty_input(self):
        self.assertEqual(_extract_keywords(''), [])
        self.assertEqual(_extract_keywords(None), [])  # type: ignore[arg-type]


class TestGenerateNarrowQueries(SimpleTestCase):
    def test_uses_natural_order_not_alphabetical(self):
        # Repro: pre-fix produced '"alex anal balanced based"' from
        # contaminated seed.  With ordered list input, narrow queries
        # should reflect the literal task wording.
        keywords = ['stock', 'market', 'signals', 'last', 'hours']
        queries = _generate_narrow_queries(
            'stock market signals from the last 24 hours', keywords
        )
        self.assertEqual(len(queries), 2)
        # Exact-phrase query uses first 4 keywords in original order
        self.assertEqual(
            queries[0]['query'],
            '"stock market signals last"',
        )
