"""Session 1234 D13 — kb_tool action=semantic_search.

D9-D11 made the Document table type-aware and gave Rigby filter axes
in `kb_tool action=documents`. But that surface is browsing only —
title icontains, no semantic search.

D12 pivoted `core.rag_integration.search_embeddings` to native
pgvector over the populated DocumentEmbedding table with D9/D10
filter pushdown. D13 exposes that as a first-class PA tool action
so Rigby can call:

    kb_tool action=semantic_search query="morning brief workflow"
    kb_tool action=semantic_search query="how does retry work" document_class=spec
    kb_tool action=semantic_search query="lane 4" min_session=1230

and get back ranked chunks with [docs/path#chunk] citations.

These tests verify:
- query is required
- response shape (chunks list with citation, similarity, importance,
  D9/D10 metadata)
- filter params pass through to search_embeddings
- LLM-autofill guard on is_pinned
- similarity_threshold knob clamping

Run::

    python manage.py test core.tests.test_kb_tool_semantic_search -v2
"""

from unittest.mock import patch

from django.test import TestCase

from core.services.tool_dispatcher import ToolDispatcher


class KbToolSemanticSearchTests(TestCase):
    """`kb_tool action=semantic_search` end-to-end contract."""

    def setUp(self):
        self.dispatcher = ToolDispatcher()

    def _call(self, **payload):
        payload.setdefault('action', 'semantic_search')
        return self.dispatcher._handle_kb_browse(
            tool_name='kb_tool',
            payload=payload,
            user_id=None,
            trace_id=None,
        )

    def _stub_chunks(self):
        return [
            {
                'id': 'chunk-1',
                'content': 'Lane 4 rotating slot pseudocode for morning brief',
                'content_type': 'spec',
                'metadata': {
                    'file_path': 'docs/specs/MORNING_BRIEF.md',
                    'title': 'Morning Brief Spec',
                    'category': 'specs',
                    'document_class': 'spec',
                    'is_pinned': True,
                    'tags': ['workflow', 'morning_brief'],
                    'chunk_index': 3,
                    'citation': '[docs/specs/MORNING_BRIEF.md#3]',
                },
                'importance_score': 1.5,
                'similarity_score': 0.87,
            },
            {
                'id': 'chunk-2',
                'content': 'Second chunk, also relevant',
                'content_type': 'handoff',
                'metadata': {
                    'file_path': 'docs/handoffs/SESSION_1232.md',
                    'title': 'Session 1232 Handoff',
                    'category': 'handoffs',
                    'document_class': 'handoff',
                    'is_pinned': False,
                    'tags': ['session-1232'],
                    'chunk_index': 7,
                    'citation': '[docs/handoffs/SESSION_1232.md#7]',
                },
                'importance_score': 1.5,
                'similarity_score': 0.71,
            },
        ]

    def test_query_required(self):
        out = self._call(query='')
        self.assertIn('error', out)
        self.assertIn('query is required', out['error'])

    def test_basic_search_returns_chunks(self):
        with patch(
            'core.rag_integration.search_embeddings',
            return_value=self._stub_chunks(),
        ):
            out = self._call(query='morning brief')

        self.assertEqual(out['action'], 'semantic_search')
        self.assertEqual(out['count'], 2)
        self.assertEqual(len(out['chunks']), 2)

        c = out['chunks'][0]
        # Required keys per the action contract
        for k in ('id', 'similarity', 'importance', 'content_preview',
                  'file_path', 'title', 'category', 'document_class',
                  'is_pinned', 'tags', 'chunk_index', 'citation'):
            self.assertIn(k, c, f'Missing key: {k}')

        # Citation has the expected shape
        self.assertEqual(c['citation'], '[docs/specs/MORNING_BRIEF.md#3]')

    def test_applied_filters_echoed(self):
        with patch(
            'core.rag_integration.search_embeddings',
            return_value=self._stub_chunks(),
        ):
            out = self._call(
                query='morning brief',
                category='specs',
                document_class='spec',
                is_pinned=True,
                min_session=1230,
                include_superseded=False,
                similarity_threshold=0.7,
            )

        f = out['applied_filters']
        self.assertEqual(f['query'], 'morning brief')
        self.assertEqual(f['category'], 'specs')
        self.assertEqual(f['document_class'], 'spec')
        self.assertEqual(f['is_pinned'], True)
        self.assertEqual(f['min_session'], 1230)
        self.assertEqual(f['include_superseded'], False)
        self.assertEqual(f['similarity_threshold'], 0.7)

    def test_is_pinned_false_does_not_pass_through(self):
        """LLM-autofill guard: is_pinned=False at the PA surface must
        NOT become is_pinned=False at search_embeddings (which would
        be ignored anyway, but we don't want noise in applied_filters
        either)."""
        captured = {}

        def fake_search(**kwargs):
            captured.update(kwargs)
            return []

        with patch(
            'core.rag_integration.search_embeddings',
            side_effect=fake_search,
        ):
            self._call(query='x', is_pinned=False)

        # The handler must convert is_pinned=False → None for search_embeddings
        self.assertIsNone(captured.get('is_pinned'),
                          'is_pinned=False should NOT pass through to search_embeddings.')

    def test_is_pinned_true_passes_through(self):
        captured = {}

        def fake_search(**kwargs):
            captured.update(kwargs)
            return []

        with patch(
            'core.rag_integration.search_embeddings',
            side_effect=fake_search,
        ):
            self._call(query='x', is_pinned=True)

        self.assertTrue(captured.get('is_pinned'))

    def test_similarity_threshold_default(self):
        captured = {}

        def fake_search(**kwargs):
            captured.update(kwargs)
            return []

        with patch(
            'core.rag_integration.search_embeddings',
            side_effect=fake_search,
        ):
            self._call(query='x')

        # Session 1234 D15 lowered the default from 0.6 to 0.4 — Chris's first
        # verification run against "morning_brief workflow" at 0.6 returned 0
        # chunks because text-embedding-3-small produces similarities in the
        # 0.4-0.7 band for related-but-not-identical content. This assertion
        # tracked the pre-D15 default and was stale ever since; refreshed
        # opportunistically during Batch A tool 3 validation (S2728).
        self.assertEqual(captured.get('similarity_threshold'), 0.4)

    def test_similarity_threshold_clamped_above_1(self):
        captured = {}

        def fake_search(**kwargs):
            captured.update(kwargs)
            return []

        with patch(
            'core.rag_integration.search_embeddings',
            side_effect=fake_search,
        ):
            self._call(query='x', similarity_threshold=1.5)

        self.assertEqual(captured.get('similarity_threshold'), 1.0)

    def test_similarity_threshold_clamped_below_0(self):
        captured = {}

        def fake_search(**kwargs):
            captured.update(kwargs)
            return []

        with patch(
            'core.rag_integration.search_embeddings',
            side_effect=fake_search,
        ):
            self._call(query='x', similarity_threshold=-0.3)

        self.assertEqual(captured.get('similarity_threshold'), 0.0)

    def test_min_session_int_string_accepted(self):
        captured = {}

        def fake_search(**kwargs):
            captured.update(kwargs)
            return []

        with patch(
            'core.rag_integration.search_embeddings',
            side_effect=fake_search,
        ):
            # String '1234' should be parsed as int
            self._call(query='x', min_session='1234')

        self.assertEqual(captured.get('min_session'), 1234)

    def test_unknown_action_message_lists_semantic_search(self):
        """Source-level guard: when an unknown action is sent, the
        error message must list 'semantic_search' in the valid set."""
        out = self._call(action='nonsense', query='x')
        self.assertIn('semantic_search', out['error'])
