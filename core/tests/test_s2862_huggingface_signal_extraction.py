"""Session 2862 slate #1 — huggingface signal extraction fix (Rigby Tool Gap Ledger #3).

Locks in the S2862 routing fix:
  - `huggingface` is no longer in `SPIDER_TARGET_URLS`, so `execute_spider_task`
    falls through to the `spider_class.fetch_data()` branch at
    core/tasks_spiders.py:158, invoking `HuggingFaceSpider.fetch_data()`.
    That produces items with `title`+`summary`+`description`, so
    `SignalAggregationService._extract_text_from_spider_data()` yields
    non-empty text and signals reach clustering.

Three test classes matching the Rigby-refined Q3 envelope:
  1. HuggingFaceSpiderOutputShapeTests — most items have title + description
  2. TextExtractionBeforeAndAfterFixTests — pre-fix URL-normalized items yield
     empty text (documenting the bug), post-fix HuggingFaceSpider items yield
     non-empty text + >=1 signal.
  3. RoutingRegressionTests — 'huggingface' is not in SPIDER_TARGET_URLS AND
     the registry still resolves it, so the else-branch has a class to run.
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from ai_core.spiders.real_data_collector import SPIDER_TARGET_URLS
from ai_core.spiders.spider_registry import SpiderRegistry
from ai_core.spiders.specialized.huggingface_spider import HuggingFaceSpider
from core.models_unified_system import LegacySpiderData
from core.services.signal_aggregation_service import SignalAggregationService


_HF_MODELS_API_SAMPLE = [
    {
        'id': 'meta-llama/Llama-3.3-70B-Instruct',
        'modelId': 'meta-llama/Llama-3.3-70B-Instruct',
        'pipeline_tag': 'text-generation',
        'tags': ['transformers', 'safetensors', 'llama', 'text-generation'],
        'downloads': 1_234_567,
        'likes': 4_321,
        'private': False,
        'createdAt': '2024-11-04T00:00:00.000Z',
        'library_name': 'transformers',
    },
    {
        'id': 'black-forest-labs/FLUX.1-schnell',
        'modelId': 'black-forest-labs/FLUX.1-schnell',
        'pipeline_tag': 'text-to-image',
        'tags': ['diffusers', 'safetensors', 'flux', 'text-to-image'],
        'downloads': 987_654,
        'likes': 2_109,
        'private': False,
        'createdAt': '2024-08-01T00:00:00.000Z',
        'library_name': 'diffusers',
    },
]

_HF_DATASETS_API_SAMPLE = [
    {
        'id': 'HuggingFaceH4/ultrachat_200k',
        'downloads': 543_210,
        'likes': 876,
    },
]

_HF_SPACES_API_SAMPLE = [
    {
        'id': 'stabilityai/stable-diffusion',
        'sdk': 'gradio',
        'likes': 12_345,
    },
]


def _make_hf_api_response(payload):
    """Build a stub for cached_get() that returns a Response-shaped mock."""
    resp = MagicMock()
    resp.json.return_value = payload
    resp.raise_for_status = MagicMock()
    return resp


class HuggingFaceSpiderOutputShapeTests(TestCase):
    """HuggingFaceSpider.fetch_data() emits items with title + description."""

    def test_output_items_have_title_and_description(self):
        def _fake_get(url, params=None, timeout=None):
            if '/models' in url:
                return _make_hf_api_response(_HF_MODELS_API_SAMPLE)
            if '/datasets' in url:
                return _make_hf_api_response(_HF_DATASETS_API_SAMPLE)
            if '/spaces' in url:
                return _make_hf_api_response(_HF_SPACES_API_SAMPLE)
            return _make_hf_api_response([])

        with patch(
            'ai_core.spiders.specialized.huggingface_spider.cached_get',
            side_effect=_fake_get,
        ):
            spider = HuggingFaceSpider()
            items = spider.fetch_data(max_results=8)

        self.assertGreater(len(items), 0, 'spider must return at least one item')

        with_title = [it for it in items if it.get('title')]
        with_description = [it for it in items if it.get('description')]
        with_summary = [it for it in items if it.get('summary')]

        # Rigby Q3 mod: at least N items have title; most have description.
        self.assertGreaterEqual(
            len(with_title), max(1, len(items) // 2),
            'at least half of items must expose a title',
        )
        self.assertGreaterEqual(
            len(with_description), max(1, len(items) // 2),
            'at least half of items must expose a description',
        )
        # Summary is always populated by the current spider implementation.
        self.assertEqual(len(with_summary), len(items))


class TextExtractionBeforeAndAfterFixTests(TestCase):
    """Signal extraction: pre-fix URL shape yields 0 text; post-fix shape yields text + signals."""

    def _fresh_row(self, items):
        return LegacySpiderData.objects.create(
            spider_name='huggingface',
            data_type='ai_ml',
            raw_data={'items': items, 'source': 'huggingface'},
            source_url='test://huggingface',
            relevance_score=70,
            is_processed=True,
        )

    def test_pre_fix_url_normalized_items_yield_empty_text(self):
        """Documents the bug: normalize_item() output has no title/summary/description
        for HF Hub API responses, so text extraction returns ''."""
        # Shape produced by the URL-path (real_data_collector.normalize_item).
        # See DB inspection at S2862 open: items have id/modelId/tags/likes/... but
        # NO title/summary/description because HF Hub payloads don't include
        # any of normalize_item's title/description field candidates.
        url_normalized_items = [
            {
                'id': 'meta-llama/Llama-3.3-70B-Instruct',
                'modelId': 'meta-llama/Llama-3.3-70B-Instruct',
                'pipeline_tag': 'text-generation',
                'tags': ['transformers', 'llama'],
                'downloads': 1_234_567,
                'likes': 4_321,
                'source': 'huggingface',
                'type': 'item',
            },
        ]
        row = self._fresh_row(url_normalized_items)
        svc = SignalAggregationService()

        text = svc._extract_text_from_spider_data(row)

        self.assertEqual(
            text, '',
            "URL-path normalized items have no readable text field, so extraction "
            "returns ''. Pre-fix bug repro.",
        )

    def test_post_fix_spider_items_yield_text_and_signal(self):
        """Post-fix: HuggingFaceSpider.fetch_data() items have title/summary/description,
        so extraction yields text AND at least one signal reaches clustering."""
        # Shape produced by HuggingFaceSpider._fetch_models() at
        # ai_core/spiders/specialized/huggingface_spider.py:111-127.
        spider_items = [
            {
                'title': 'meta-llama/Llama-3.3-70B-Instruct',
                'name': 'meta-llama/Llama-3.3-70B-Instruct',
                'url': 'https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct',
                'link': 'https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct',
                'summary': 'AI model for text-generation. Downloads: 1,234,567. Likes: 4,321.',
                'description': 'AI model for text-generation. Downloads: 1,234,567. Likes: 4,321.',
                'author': 'meta-llama',
                'pipeline_tag': 'text-generation',
                'downloads': 1_234_567,
                'likes': 4_321,
                'category': 'model',
                'source': 'HuggingFace',
                'data_type': 'ai_model',
                'tags': ['ai', 'ml', 'model', 'text-generation'],
            },
            {
                'title': 'black-forest-labs/FLUX.1-schnell',
                'name': 'black-forest-labs/FLUX.1-schnell',
                'url': 'https://huggingface.co/black-forest-labs/FLUX.1-schnell',
                'link': 'https://huggingface.co/black-forest-labs/FLUX.1-schnell',
                'summary': 'AI model for text-to-image. Downloads: 987,654. Likes: 2,109.',
                'description': 'AI model for text-to-image. Downloads: 987,654. Likes: 2,109.',
                'author': 'black-forest-labs',
                'pipeline_tag': 'text-to-image',
                'downloads': 987_654,
                'likes': 2_109,
                'category': 'model',
                'source': 'HuggingFace',
                'data_type': 'ai_model',
                'tags': ['ai', 'ml', 'model', 'text-to-image'],
            },
        ]
        row = self._fresh_row(spider_items)
        svc = SignalAggregationService()

        text = svc._extract_text_from_spider_data(row)
        self.assertGreater(
            len(text), 0,
            'HuggingFaceSpider-shaped items must yield non-empty extracted text',
        )

        signals = svc._extract_signals([row])
        self.assertGreaterEqual(
            len(signals), 1,
            'HuggingFaceSpider-shaped items must produce at least one signal '
            '(via keywords/topics/entity_tokens)',
        )


class RoutingRegressionTests(TestCase):
    """The routing fix itself: SPIDER_TARGET_URLS no longer includes huggingface,
    and the spider registry still resolves HuggingFaceSpider so the else-branch
    at core/tasks_spiders.py:158 has a class to run."""

    def test_huggingface_removed_from_spider_target_urls(self):
        self.assertNotIn(
            'huggingface', SPIDER_TARGET_URLS,
            "S2862 Option C: 'huggingface' must not live in SPIDER_TARGET_URLS. "
            "Its presence there routes execution through the generic URL path + "
            "normalize_item, which silently drops all signals.",
        )

    def test_huggingface_still_resolves_via_registry(self):
        registry = SpiderRegistry()
        cls = registry.get_spider_class('huggingface')
        self.assertIsNotNone(
            cls, 'HuggingFaceSpider must still be registered so the else-branch runs it'
        )
        self.assertIs(cls, HuggingFaceSpider)

    def test_huggingface_class_exposes_fetch_data(self):
        """`_run_spider_adapter` at core/tasks.py:1198 dispatches to fetch_data
        when the spider has no fetch/scrape/collect_data methods."""
        spider = HuggingFaceSpider()
        self.assertTrue(hasattr(spider, 'fetch_data'))
        self.assertFalse(hasattr(spider, 'fetch'))
        self.assertFalse(hasattr(spider, 'scrape'))
        self.assertFalse(hasattr(spider, 'collect_data'))
