"""
S2869 slate — Rigby Tool Gap Ledger #2 + #4 grouped.

#2: `spider_status_tool.search` preview fallback — when `embedding_text` is
empty, extract a best-effort title from `raw_data['items'][0].{title|name|id}`
(inline fallback, not a shared helper — do not codify raw_data structure as
a contract).

#4: `intelligence_tool.signal_clusters` multi-source filter — `source_spider`
now accepts a list-of-spider-names and applies `source_breakdown__has_any_keys`
union filter, so callers can fetch clusters across multiple spiders in one
call instead of looping.

Run::

    python manage.py test core.tests.test_s2869_search_preview_and_multisource -v2
"""

import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models_unified_system import LegacySpiderData
from core.models import SignalCluster
from core.services.tool_dispatcher import ToolDispatcher


User = get_user_model()


class SpiderStatusSearchPreviewFallbackTests(TestCase):
    """Ledger #2: preview should fall back to raw_data extraction when
    embedding_text is empty. Each fixture uses a distinct raw_data shape
    to exercise all fallback branches."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f's2869-preview-{uuid.uuid4().hex[:8]}',
            email='s2869-preview@example.com',
            password='x',
        )
        now = timezone.now()

        # Fixture 1: embedding_text populated → uses embedding_text as before.
        cls.row_embed = LegacySpiderData.objects.create(
            spider_name='s2869_test_embed',
            data_type='test',
            source_url='https://test.example.com/embed',
            raw_data={'items': [{'title': 'ignored because embed_text wins'}]},
            processed_data={},
            embedding_text='embedding preview content',
            created_at=now,
        )
        # Fixture 2: embedding_text empty, raw_data['items'][0]['title'] present
        # (devto / techcrunch shape).
        cls.row_items_title = LegacySpiderData.objects.create(
            spider_name='s2869_test_items_title',
            data_type='test',
            source_url='https://test.example.com/items-title',
            raw_data={'items': [{'title': 'Article headline from items[0]'}]},
            processed_data={},
            embedding_text='',
            created_at=now - timedelta(seconds=1),
        )
        # Fixture 3: embedding_text empty, items[0] has no title but has id
        # (huggingface model-registry shape).
        cls.row_items_id = LegacySpiderData.objects.create(
            spider_name='s2869_test_items_id',
            data_type='test',
            source_url='https://test.example.com/items-id',
            raw_data={'items': [{'id': 'sentence-transformers/all-MiniLM-L6-v2'}]},
            processed_data={},
            embedding_text='',
            created_at=now - timedelta(seconds=2),
        )
        # Fixture 4: empty embed + raw_data top-level title (no items key).
        cls.row_top_title = LegacySpiderData.objects.create(
            spider_name='s2869_test_top_title',
            data_type='test',
            source_url='https://test.example.com/top-title',
            raw_data={'title': 'Top-level title fallback'},
            processed_data={},
            embedding_text='',
            created_at=now - timedelta(seconds=3),
        )
        # Fixture 5: empty embed + no usable text anywhere (returns '').
        cls.row_empty = LegacySpiderData.objects.create(
            spider_name='s2869_test_empty',
            data_type='test',
            source_url='https://test.example.com/empty',
            raw_data={'items': []},
            processed_data={},
            embedding_text='',
            created_at=now - timedelta(seconds=4),
        )
        # Fixture 6: raw_data is a list, not a dict — must not crash.
        cls.row_list_raw = LegacySpiderData.objects.create(
            spider_name='s2869_test_list_raw',
            data_type='test',
            source_url='https://test.example.com/list-raw',
            raw_data=[{'title': 'buried in top-level list — not extracted'}],
            processed_data={},
            embedding_text='',
            created_at=now - timedelta(seconds=5),
        )

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _search(self, **extras):
        payload = {'action': 'search', **extras}
        return self.dispatcher._handle_spider_status(
            'spider_status_tool', payload, self.user.id, 'test-trace-s2869',
        )

    def _preview_for(self, spider_name):
        result = self._search(spider_name=spider_name, limit=5)
        self.assertEqual(result.get('action'), 'search',
                         f'unexpected result for {spider_name}: {result}')
        items = result.get('items', [])
        self.assertEqual(len(items), 1,
                         f'expected 1 fixture row for {spider_name}, got {len(items)}')
        return items[0].get('preview', '')

    def test_p1_embedding_text_still_wins_when_populated(self):
        preview = self._preview_for('s2869_test_embed')
        self.assertEqual(preview, 'embedding preview content')

    def test_p2_items_title_fallback_when_embed_empty(self):
        preview = self._preview_for('s2869_test_items_title')
        self.assertEqual(preview, 'Article headline from items[0]')

    def test_p3_items_id_fallback_when_no_title(self):
        preview = self._preview_for('s2869_test_items_id')
        self.assertEqual(preview, 'sentence-transformers/all-MiniLM-L6-v2')

    def test_p4_top_level_title_fallback_when_no_items(self):
        preview = self._preview_for('s2869_test_top_title')
        self.assertEqual(preview, 'Top-level title fallback')

    def test_p5_empty_when_no_extractable_text(self):
        preview = self._preview_for('s2869_test_empty')
        self.assertEqual(preview, '')

    def test_p6_list_raw_data_does_not_crash_returns_empty(self):
        # raw_data is a list (not a dict) → skip extraction path safely.
        preview = self._preview_for('s2869_test_list_raw')
        self.assertEqual(preview, '')

    def test_p7_preview_truncated_to_200_chars(self):
        long_title = 'X' * 500
        row = LegacySpiderData.objects.create(
            spider_name='s2869_test_long_title',
            data_type='test',
            source_url='https://test.example.com/long',
            raw_data={'items': [{'title': long_title}]},
            processed_data={},
            embedding_text='',
            created_at=timezone.now(),
        )
        preview = self._preview_for('s2869_test_long_title')
        self.assertEqual(len(preview), 200)
        self.assertEqual(preview, 'X' * 200)


class SignalClustersMultiSourceFilterTests(TestCase):
    """Ledger #4: source_spider accepts string OR list; list triggers
    has_any_keys union filter."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username=f's2869-multi-{uuid.uuid4().hex[:8]}',
            email='s2869-multi@example.com',
            password='x',
        )
        now = timezone.now()
        # 3 clusters each keyed on a distinct spider in source_breakdown.
        cls.c_hn = SignalCluster.objects.create(
            name='s2869_hn_cluster',
            pattern_type='trend_emergence',
            spider_data_ids=[],
            keywords=['ai', 'agents'],
            source_breakdown={'hackernews': 5},
            detected_at=now,
        )
        cls.c_hf = SignalCluster.objects.create(
            name='s2869_hf_cluster',
            pattern_type='trend_emergence',
            spider_data_ids=[],
            keywords=['ai', 'models'],
            source_breakdown={'huggingface': 3},
            detected_at=now - timedelta(hours=1),
        )
        cls.c_devto = SignalCluster.objects.create(
            name='s2869_devto_cluster',
            pattern_type='trend_emergence',
            spider_data_ids=[],
            keywords=['ai', 'tutorials'],
            source_breakdown={'devto': 2},
            detected_at=now - timedelta(hours=2),
        )
        # Multi-source cluster: keyed on both hackernews AND huggingface.
        cls.c_multi = SignalCluster.objects.create(
            name='s2869_multi_source_cluster',
            pattern_type='trend_emergence',
            spider_data_ids=[],
            keywords=['ai'],
            source_breakdown={'hackernews': 2, 'huggingface': 4},
            detected_at=now - timedelta(hours=3),
        )

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _signal_clusters(self, **extras):
        payload = {'action': 'signal_clusters', 'limit': 30, **extras}
        return self.dispatcher._handle_intelligence(
            'intelligence_tool', payload, self.user.id, 'test-trace-s2869',
        )

    def _names_in(self, result):
        return {c['name'] for c in result.get('clusters', [])}

    def test_m1_string_source_spider_preserves_has_key_behavior(self):
        result = self._signal_clusters(source_spider='hackernews', query='s2869')
        names = self._names_in(result)
        self.assertIn('s2869_hn_cluster', names)
        self.assertIn('s2869_multi_source_cluster', names)
        self.assertNotIn('s2869_hf_cluster', names)
        self.assertNotIn('s2869_devto_cluster', names)
        self.assertEqual(result['filters_applied']['source_spider'], 'hackernews')

    def test_m2_list_source_spider_unions_via_has_any_keys(self):
        result = self._signal_clusters(
            source_spider=['hackernews', 'huggingface'], query='s2869',
        )
        names = self._names_in(result)
        self.assertIn('s2869_hn_cluster', names)
        self.assertIn('s2869_hf_cluster', names)
        self.assertIn('s2869_multi_source_cluster', names)
        self.assertNotIn('s2869_devto_cluster', names)
        self.assertEqual(
            result['filters_applied']['source_spider'],
            ['hackernews', 'huggingface'],
        )

    def test_m3_list_source_spider_dedupes_via_orm(self):
        # multi-source cluster keyed on both hn+hf; must appear ONCE in the union.
        result = self._signal_clusters(
            source_spider=['hackernews', 'huggingface'], query='s2869',
        )
        names_list = [c['name'] for c in result.get('clusters', [])]
        self.assertEqual(
            names_list.count('s2869_multi_source_cluster'), 1,
            f'multi-source cluster must not duplicate; got {names_list}',
        )

    def test_m4_json_stringified_list_from_middleware_coerced(self):
        # Defensive: if middleware stringifies the list, handler must
        # still route to has_any_keys.
        result = self._signal_clusters(
            source_spider='["hackernews", "huggingface"]', query='s2869',
        )
        names = self._names_in(result)
        self.assertIn('s2869_hn_cluster', names)
        self.assertIn('s2869_hf_cluster', names)
        self.assertNotIn('s2869_devto_cluster', names)

    def test_m5_empty_list_falls_through_to_no_filter(self):
        result = self._signal_clusters(source_spider=[], query='s2869')
        # With no filter applied, all 4 s2869 clusters should surface.
        names = self._names_in(result)
        self.assertIn('s2869_hn_cluster', names)
        self.assertIn('s2869_hf_cluster', names)
        self.assertIn('s2869_devto_cluster', names)
        self.assertIn('s2869_multi_source_cluster', names)
        self.assertIsNone(result['filters_applied']['source_spider'])

    def test_m6_list_with_non_string_items_filtered_out(self):
        # Defensive: mixed list with None/int gets filtered to just strings.
        result = self._signal_clusters(
            source_spider=['hackernews', None, 42, ''], query='s2869',
        )
        names = self._names_in(result)
        self.assertIn('s2869_hn_cluster', names)
        self.assertNotIn('s2869_hf_cluster', names)
        self.assertEqual(result['filters_applied']['source_spider'], ['hackernews'])

    def test_m7_list_with_only_invalid_items_falls_through(self):
        # If after filtering the list is empty, no source filter applied.
        result = self._signal_clusters(source_spider=[None, 42, ''], query='s2869')
        # No source filter applied → all 4 s2869 clusters surface.
        names = self._names_in(result)
        self.assertEqual(len(names), 4)
        self.assertIsNone(result['filters_applied']['source_spider'])
