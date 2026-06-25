"""Session 1234 D12 — rag_integration.search_embeddings pivot tests.

Pre-D12 search_embeddings queried a dead `unified_embeddings` table
that doesn't exist (the real Django table is
`persistence_unifiedembedding`, also empty locally). Callers silently
degraded — get_rag_context returned has_context=False every call.

D12 pivots to pgvector cosine similarity over the populated
`DocumentEmbedding` table with D9/D10 filter pushdown.

These tests verify:
- Mocked embedding service produces a query vector
- Mocked cosine_similarity_search returns chunks
- Filters (category / document_class / is_pinned / min_session /
  include_superseded) push through to the queryset
- Response shape matches the legacy contract (id / content /
  content_type / metadata / importance_score / similarity_score)
- LLM-autofill guard for is_pinned=False

Run::

    python manage.py test core.tests.test_rag_integration_search_embeddings -v2
"""

import uuid
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from core.rag_integration import search_embeddings

User = get_user_model()


class SearchEmbeddingsPivotTests(TestCase):
    """`search_embeddings(query)` now queries DocumentEmbedding via pgvector."""

    def _mock_chunk(
        self,
        chunk_text='sample text',
        chunk_index=0,
        distance=0.2,
        doc_kwargs=None,
    ):
        """Build a MagicMock chunk that quacks like a DocumentEmbedding row."""
        doc_kwargs = doc_kwargs or {}
        doc = MagicMock()
        doc.file_path = doc_kwargs.get('file_path', 'docs/specs/SAMPLE.md')
        doc.title = doc_kwargs.get('title', 'Sample Spec')
        doc.category = doc_kwargs.get('category', 'specs')
        doc.document_class = doc_kwargs.get('document_class', 'spec')
        doc.is_pinned = doc_kwargs.get('is_pinned', True)
        doc.tags = doc_kwargs.get('tags', ['workflow', 'session-1234'])
        doc.retrieval_boost = doc_kwargs.get('retrieval_boost', 1.5)
        doc.status = doc_kwargs.get('status', 'processed')

        chunk = MagicMock()
        chunk.id = uuid.uuid4()
        chunk.chunk_text = chunk_text
        chunk.chunk_index = chunk_index
        chunk.distance = distance
        chunk.document = doc
        chunk.document_id = uuid.uuid4()
        return chunk

    def _patch_pipeline(self, chunks, query_vec=None):
        """Patch create_embedding + the cosine_similarity_search path."""
        if query_vec is None:
            query_vec = [0.1] * 1536

        # The function does qs = cosine_similarity_search(...).filter(...)[:limit].
        # We patch the QS to be a MagicMock that supports chained filter/exclude
        # and yields our chunks on iteration.
        qs_mock = MagicMock()
        qs_mock.filter.return_value = qs_mock
        qs_mock.exclude.return_value = qs_mock
        qs_mock.__getitem__.return_value = chunks  # [:limit] slice
        qs_mock.__iter__.return_value = iter(chunks)
        qs_mock.values_list.return_value.distinct.return_value = []

        mock_embed = patch(
            'core.rag_integration.create_embedding',
            return_value=query_vec,
        )
        mock_search = patch(
            'content.models.DocumentEmbedding.cosine_similarity_search',
            return_value=qs_mock,
        )
        # Patch Document.objects too in case min_session pathway runs
        mock_doc_mgr = patch(
            'core.rag_integration.Document', new=MagicMock(),
        )
        return mock_embed, mock_search, mock_doc_mgr, qs_mock

    def test_no_results_when_embedding_fails(self):
        with patch(
            'core.rag_integration.create_embedding',
            return_value=None,
        ):
            self.assertEqual(search_embeddings('hello'), [])

    def test_response_shape_matches_legacy_contract(self):
        chunk = self._mock_chunk(
            chunk_text='Lane 4 rotating slot pseudocode',
            chunk_index=3,
            distance=0.1,
            doc_kwargs={
                'file_path': 'docs/specs/MORNING_BRIEF.md',
                'title': 'Morning Brief Spec',
                'category': 'specs',
                'document_class': 'spec',
                'is_pinned': True,
                'tags': ['workflow', 'morning_brief'],
                'retrieval_boost': 1.5,
            },
        )
        embed_p, search_p, _doc_p, _qs = self._patch_pipeline([chunk])

        with embed_p, search_p:
            out = search_embeddings('Lane 4 rotating slot', limit=5)

        self.assertEqual(len(out), 1)
        item = out[0]
        # Legacy keys
        for k in ('id', 'content', 'content_type', 'metadata',
                  'importance_score', 'similarity_score'):
            self.assertIn(k, item)

        # New D9/D10 metadata exposed
        self.assertEqual(item['metadata']['category'], 'specs')
        self.assertEqual(item['metadata']['document_class'], 'spec')
        self.assertTrue(item['metadata']['is_pinned'])
        self.assertIn('workflow', item['metadata']['tags'])
        self.assertEqual(item['metadata']['chunk_index'], 3)
        self.assertEqual(
            item['metadata']['citation'],
            '[docs/specs/MORNING_BRIEF.md#3]',
        )

        # Similarity = 1 - distance
        self.assertAlmostEqual(item['similarity_score'], 0.9, places=2)
        # importance_score mirrors retrieval_boost
        self.assertEqual(item['importance_score'], 1.5)
        # content_type derives from document_class
        self.assertEqual(item['content_type'], 'spec')

    def test_filter_pushdown_category(self):
        chunk = self._mock_chunk(doc_kwargs={'category': 'handoffs'})
        embed_p, search_p, _doc_p, qs = self._patch_pipeline([chunk])

        with embed_p, search_p:
            search_embeddings('test', category='handoffs')

        # Verify .filter(document__category='handoffs') was called
        found = any(
            call.kwargs.get('document__category') == 'handoffs'
            for call in qs.filter.call_args_list
        )
        self.assertTrue(found, f"category filter not pushed. Calls: {qs.filter.call_args_list}")

    def test_filter_pushdown_document_class(self):
        chunk = self._mock_chunk()
        embed_p, search_p, _doc_p, qs = self._patch_pipeline([chunk])

        with embed_p, search_p:
            search_embeddings('test', document_class='handoff')

        found = any(
            call.kwargs.get('document__document_class') == 'handoff'
            for call in qs.filter.call_args_list
        )
        self.assertTrue(found)

    def test_is_pinned_true_pushes_filter(self):
        chunk = self._mock_chunk()
        embed_p, search_p, _doc_p, qs = self._patch_pipeline([chunk])

        with embed_p, search_p:
            search_embeddings('test', is_pinned=True)

        found = any(
            call.kwargs.get('document__is_pinned') is True
            for call in qs.filter.call_args_list
        )
        self.assertTrue(found)

    def test_is_pinned_false_does_NOT_push_filter(self):
        """LLM-autofill guard: is_pinned=False must be ignored."""
        chunk = self._mock_chunk()
        embed_p, search_p, _doc_p, qs = self._patch_pipeline([chunk])

        with embed_p, search_p:
            search_embeddings('test', is_pinned=False)

        # No filter call with document__is_pinned=False
        for call in qs.filter.call_args_list:
            self.assertNotIn('document__is_pinned', call.kwargs,
                             "is_pinned=False MUST NOT push a filter (LLM-autofill guard).")

    def test_default_excludes_archived(self):
        chunk = self._mock_chunk()
        embed_p, search_p, _doc_p, qs = self._patch_pipeline([chunk])

        with embed_p, search_p:
            search_embeddings('test')

        # Verify .exclude(document__status=ARCHIVED) called
        from content.models import ContentStatus
        found_exclude = any(
            call.kwargs.get('document__status') == ContentStatus.ARCHIVED
            for call in qs.exclude.call_args_list
        )
        self.assertTrue(
            found_exclude,
            f"Default should exclude archived. Calls: {qs.exclude.call_args_list}",
        )

    def test_include_superseded_skips_archive_exclusion(self):
        chunk = self._mock_chunk()
        embed_p, search_p, _doc_p, qs = self._patch_pipeline([chunk])

        with embed_p, search_p:
            search_embeddings('test', include_superseded=True)

        from content.models import ContentStatus
        found_exclude = any(
            call.kwargs.get('document__status') == ContentStatus.ARCHIVED
            for call in qs.exclude.call_args_list
        )
        self.assertFalse(
            found_exclude,
            "include_superseded=True should NOT add archived exclusion.",
        )

    def test_content_types_legacy_maps_to_document_class(self):
        """Back-compat: callers passing content_types=['spec'] (legacy)
        should have it interpreted as document_class='spec' if the new
        kwarg isn't given."""
        chunk = self._mock_chunk()
        embed_p, search_p, _doc_p, qs = self._patch_pipeline([chunk])

        with embed_p, search_p:
            search_embeddings('test', content_types=['handoff'])

        found = any(
            call.kwargs.get('document__document_class') == 'handoff'
            for call in qs.filter.call_args_list
        )
        self.assertTrue(found, "Legacy content_types should map to document_class.")

    def test_explicit_document_class_wins_over_legacy_content_types(self):
        chunk = self._mock_chunk()
        embed_p, search_p, _doc_p, qs = self._patch_pipeline([chunk])

        with embed_p, search_p:
            search_embeddings(
                'test',
                content_types=['handoff'],   # legacy
                document_class='spec',       # new, should win
            )

        spec_called = any(
            call.kwargs.get('document__document_class') == 'spec'
            for call in qs.filter.call_args_list
        )
        handoff_called = any(
            call.kwargs.get('document__document_class') == 'handoff'
            for call in qs.filter.call_args_list
        )
        self.assertTrue(spec_called, "Explicit document_class should fire.")
        self.assertFalse(handoff_called, "Legacy content_types should NOT fire when document_class explicit.")
