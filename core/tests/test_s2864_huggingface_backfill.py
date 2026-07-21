"""Session 2864 slate #1 — enrich pre-S2862 HuggingFace items (Rigby Tool Gap Ledger #14).

Locks in the backfill migration + view-layer workaround removal.

Two test classes:
  1. ItemEnrichmentTests — enrich_item() correctness across item shapes
  2. CommandIntegrationTests — management command end-to-end with fixture rows
"""

from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from core.management.commands.backfill_huggingface_items import enrich_item
from core.models_unified_system import LegacySpiderData


_PRE_S2862_MODEL_ITEM = {
    'id': 'sentence-transformers/all-MiniLM-L6-v2',
    'modelId': 'sentence-transformers/all-MiniLM-L6-v2',
    'type': 'item',
    'source': 'huggingface',
    'fetched_at': '2026-07-20T10:00:00+00:00',
    'pipeline_tag': 'sentence-similarity',
    'library_name': 'sentence-transformers',
    'tags': ['transformers', 'bert', 'feature-extraction', 'dataset:s2orc', 'arxiv:1904.06472'],
    'downloads': 241_315_604,
    'likes': 5104,
    'private': False,
    'createdAt': '2022-03-02T23:29:05.000Z',
}


_POST_S2862_RICH_ITEM = {
    'title': 'meta-llama/Llama-3.3-70B-Instruct',
    'name': 'meta-llama/Llama-3.3-70B-Instruct',
    'url': 'https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct',
    'link': 'https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct',
    'description': 'AI model for text-generation. Downloads: 1,234,567. Likes: 4,321.',
    'summary': 'AI model for text-generation. Downloads: 1,234,567. Likes: 4,321.',
    'pipeline_tag': 'text-generation',
    'tags': ['transformers', 'safetensors'],
    'downloads': 1_234_567,
    'likes': 4_321,
}


class ItemEnrichmentTests(TestCase):
    """enrich_item() unit tests — pure function, no DB."""

    def test_enriches_pre_s2862_model_item(self):
        item = dict(_PRE_S2862_MODEL_ITEM)
        changed = enrich_item(item)
        self.assertTrue(changed)
        self.assertEqual(item['title'], 'sentence-transformers/all-MiniLM-L6-v2')
        self.assertEqual(item['url'], 'https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2')
        self.assertEqual(item['link'], item['url'])
        # Description format mirrors views_spider_intelligence.py:1217-1233 exactly
        self.assertIn('Task: sentence-similarity', item['description'])
        self.assertIn('Library: sentence-transformers', item['description'])
        self.assertIn('Tags: transformers, bert, feature-extraction', item['description'])
        self.assertIn('241,315,604 downloads', item['description'])
        self.assertIn('5,104 likes', item['description'])
        self.assertEqual(item['summary'], item['description'])
        # Skip-prefix tags filtered
        self.assertNotIn('dataset:', item['description'])
        self.assertNotIn('arxiv:', item['description'])

    def test_skips_post_s2862_rich_item(self):
        item = dict(_POST_S2862_RICH_ITEM)
        original_title = item['title']
        original_desc = item['description']
        changed = enrich_item(item)
        self.assertFalse(changed)
        self.assertEqual(item['title'], original_title)
        self.assertEqual(item['description'], original_desc)

    def test_idempotent_second_call_is_noop(self):
        item = dict(_PRE_S2862_MODEL_ITEM)
        self.assertTrue(enrich_item(item))
        # Second call: title now set, so guard skips
        self.assertFalse(enrich_item(item))

    def test_skips_item_without_id(self):
        item = {'type': 'item', 'source': 'huggingface', 'tags': ['foo']}
        changed = enrich_item(item)
        self.assertFalse(changed)
        self.assertNotIn('title', item)
        self.assertNotIn('url', item)

    def test_falls_back_to_id_when_modelId_missing(self):
        item = dict(_PRE_S2862_MODEL_ITEM)
        del item['modelId']
        changed = enrich_item(item)
        self.assertTrue(changed)
        self.assertEqual(item['title'], 'sentence-transformers/all-MiniLM-L6-v2')

    def test_space_item_gets_spaces_url(self):
        item = {
            'id': 'stabilityai/stable-diffusion',
            'modelId': 'stabilityai/stable-diffusion',
            'sdk': 'gradio',
            'likes': 100,
        }
        changed = enrich_item(item)
        self.assertTrue(changed)
        self.assertEqual(item['url'], 'https://huggingface.co/spaces/stabilityai/stable-diffusion')

    def test_empty_description_when_no_metadata(self):
        item = {'modelId': 'foo/bar'}
        changed = enrich_item(item)
        self.assertTrue(changed)
        self.assertEqual(item['title'], 'foo/bar')
        self.assertEqual(item['url'], 'https://huggingface.co/foo/bar')
        # No description keys set because desc_parts is empty
        self.assertNotIn('description', item)


class CommandIntegrationTests(TestCase):
    """Management command end-to-end with fixture rows."""

    def _make_row(self, items):
        return LegacySpiderData.objects.create(
            spider_name='huggingface',
            data_type='ai_ml',
            raw_data={'items': items, 'source': 'huggingface'},
            source_url='https://huggingface.co/api/models?sort=downloads&direction=-1&limit=20',
            relevance_score=70,
        )

    def test_backfill_enriches_and_persists(self):
        self._make_row([dict(_PRE_S2862_MODEL_ITEM), dict(_PRE_S2862_MODEL_ITEM)])
        out = StringIO()
        call_command('backfill_huggingface_items', stdout=out)
        row = LegacySpiderData.objects.get(spider_name='huggingface')
        for item in row.raw_data['items']:
            self.assertEqual(item['title'], 'sentence-transformers/all-MiniLM-L6-v2')
            self.assertIn('Task: sentence-similarity', item['description'])
        output = out.getvalue()
        self.assertIn('rows_updated:            1', output)
        self.assertIn('items_enriched:          2', output)

    def test_backfill_dry_run_does_not_persist(self):
        self._make_row([dict(_PRE_S2862_MODEL_ITEM)])
        out = StringIO()
        call_command('backfill_huggingface_items', '--dry-run', stdout=out)
        row = LegacySpiderData.objects.get(spider_name='huggingface')
        self.assertNotIn('title', row.raw_data['items'][0])
        self.assertIn('DRY RUN', out.getvalue())

    def test_backfill_idempotent_second_run_updates_zero(self):
        self._make_row([dict(_PRE_S2862_MODEL_ITEM)])
        call_command('backfill_huggingface_items', stdout=StringIO())
        out = StringIO()
        call_command('backfill_huggingface_items', stdout=out)
        self.assertIn('rows_updated:            0', out.getvalue())
        self.assertIn('items_enriched:          0', out.getvalue())

    def test_backfill_mixed_rows_only_enriches_pre_s2862(self):
        self._make_row([dict(_PRE_S2862_MODEL_ITEM)])
        self._make_row([dict(_POST_S2862_RICH_ITEM)])
        out = StringIO()
        call_command('backfill_huggingface_items', stdout=out)
        self.assertIn('rows_updated:            1', out.getvalue())
        self.assertIn('items_enriched:          1', out.getvalue())
        self.assertIn('items_skipped_has_title: 1', out.getvalue())
