import sys
import types
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase


class AutoResearchMetadataTest(SimpleTestCase):
    def test_auto_research_reports_partial_failures(self):
        from core.tasks import _auto_research_competitor

        mock_web_module = types.ModuleType('core.tools.web_search')
        mock_web = MagicMock()
        mock_web.execute.side_effect = [
            Exception('search failed'),
            {'results': [{'url': 'https://example.com/a', 'title': 'A'}]},
            {'results': []},
            {'results': []},
        ]
        mock_web_module.WebSearchTool = MagicMock(return_value=mock_web)

        mock_models_module = types.ModuleType('content.models')
        mock_document = MagicMock()
        mock_document.objects.filter.return_value.first.return_value = None
        mock_document.objects.create.return_value = MagicMock(id=99)
        mock_models_module.Document = mock_document
        mock_models_module.ContentStatus = types.SimpleNamespace(PROCESSED='processed')
        mock_models_module.ContentSource = types.SimpleNamespace(API='api')

        mock_embeddings_module = types.ModuleType('content.embeddings')
        mock_rag = MagicMock()
        mock_rag.process_document_for_rag_sync.side_effect = Exception('embed failed')
        mock_embeddings_module.rag_system = mock_rag
        mock_embeddings_module.DocumentEmbedding = MagicMock()
        mock_embeddings_module.DocumentEmbedding.objects.filter.return_value.exists.return_value = False

        mock_processors_module = types.ModuleType('content.processors')
        mock_pipeline = MagicMock()
        mock_pipeline.process_url.return_value = MagicMock(
            success=True,
            processed_content='content',
            raw_content='raw',
            word_count=123,
            language='en',
            key_phrases=[],
            entities=[],
            metadata={},
        )
        mock_processors_module.DocumentProcessingPipeline = MagicMock(return_value=mock_pipeline)

        mock_user_model = MagicMock()
        mock_user_model.objects.filter.return_value.first.return_value = None
        mock_user_model.objects.first.return_value = None

        fake_modules = {
            'core.tools.web_search': mock_web_module,
            'content.models': mock_models_module,
            'content.embeddings': mock_embeddings_module,
            'content.processors': mock_processors_module,
        }

        with patch.dict(sys.modules, fake_modules), \
             patch('django.contrib.auth.get_user_model', return_value=mock_user_model):
            stats = _auto_research_competitor('Acme', user_id=123, time_budget=120)

        self.assertEqual(stats['search_failures'], 1)
        self.assertEqual(stats['embedding_failures'], 1)
        self.assertTrue(stats['partial_failure'])
        self.assertGreaterEqual(stats['errors'], 2)
        self.assertEqual(stats['docs_ingested'], 1)
        self.assertEqual(stats['docs_embedded'], 0)

