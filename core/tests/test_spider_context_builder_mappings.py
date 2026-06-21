"""
Session 1188 PR-1 (C-trace remediation #3): explicit Hot-agent keys in
SpiderContextBuilder.AGENT_SPIDER_MAPPINGS.

Background (Session 1187 Utilization Recon, deliverable
1f548d38-8971-4780-a798-03e79399f322): 56/83 agents had zero dispatches in
30d; the in-code `AGENT_SPIDER_MAPPINGS` dict was the actual wiring (the
parallel `AgentSpiderConnection` DB table is dead read-side). Rigby's
PR-prep recon (deliverable 51062b8c-0fdf-4ca9-855a-264962e2506c) found:

- ImageAgent already covered by `'image' in 'imageagent'` substring match.
- ResearchAgent already covered by `'research' in 'researchagent'` substring.
- ThinkingAgent had no substring match → fell back to `'default'`.

PR-1 (this) adds explicit `imageagent` / `researchagent` / `thinkingagent`
keys. Image/Research are functionally unchanged (mirror their substring
outcomes for trace clarity); Thinking moves off `default` to a curated
reasoning-oriented set.

Run:
    USE_PGBOUNCER=0 python manage.py test core.tests.test_spider_context_builder_mappings -v2 --keepdb
"""

from django.test import SimpleTestCase

from core.services.spider_context_builder import SpiderContextBuilder


class ExplicitAgentMappingTests(SimpleTestCase):
    def setUp(self):
        self.builder = SpiderContextBuilder()

    def test_thinking_agent_no_longer_falls_to_default(self):
        cats = self.builder._get_agent_categories('ThinkingAgent')
        self.assertEqual(cats, ['tech', 'news', 'science', 'financial'])
        self.assertNotEqual(cats, SpiderContextBuilder.AGENT_SPIDER_MAPPINGS['default'])

    def test_image_agent_uses_real_data_type_categories(self):
        """PR-2: ImageAgent retuned off the dead 'creative' key to the real
        creative-domain SpiderData.data_type values (design / visual_trends /
        video) per Rigby's supply recon."""
        cats = self.builder._get_agent_categories('ImageAgent')
        self.assertEqual(cats, ['design', 'visual_trends', 'video', 'tech', 'entertainment'])
        self.assertNotIn('creative', cats)

    def test_research_agent_picks_up_high_supply_buckets(self):
        """PR-2: ResearchAgent additionally picks up `ai_ml` (364 actionable
        in 30d) and `business` (92) — the largest research-relevant supply
        buckets it was previously missing."""
        cats = self.builder._get_agent_categories('ResearchAgent')
        self.assertEqual(
            cats,
            ['tech', 'news', 'social', 'community', 'financial', 'legal',
             'science', 'health', 'ai_ml', 'business'],
        )

    def test_explicit_keys_precede_substring_keys_in_dict(self):
        """Order matters — explicit keys must come before substring matches
        so `_get_agent_categories` returns on the explicit key first."""
        keys = list(SpiderContextBuilder.AGENT_SPIDER_MAPPINGS.keys())
        self.assertLess(keys.index('imageagent'), keys.index('image'))
        self.assertLess(keys.index('researchagent'), keys.index('research'))
        self.assertIn('thinkingagent', keys)

    def test_image_editing_agent_still_matches_image_not_imageagent(self):
        """Regression: adding `imageagent` must not steal matches from agents
        that contain `image` but not `imageagent` as a substring."""
        cats = self.builder._get_agent_categories('ImageEditingAgent')
        self.assertEqual(cats, ['creative', 'tech', 'entertainment'])
