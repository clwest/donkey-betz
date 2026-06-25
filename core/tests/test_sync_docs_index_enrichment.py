"""Session 1234 D9 — sync_docs_index_to_documents enrichment fields.

The Session 1234 close audit found that the Document table was flat:
`document_class='reference'` for ALL 2,732 docs, `category=''` for all,
`tags=[]` for all, `is_pinned=False` for all, `retrieval_boost` default.
Rigby's retrieval (kb_tool / core.rag_integration) had no per-row
differentiator beyond title-icontains, so a superseded 2025 handoff
competed equally with a current 2026 spec in semantic search.

D9 makes `sync_docs_index_to_documents` populate the live Document
fields (`category` / `tags` / `document_class` / `is_pinned` /
`retrieval_boost`) from `_index.json` frontmatter, so downstream
retrieval can filter and rank by real semantic axes without re-
embedding.

This test file covers the helper `_enrichment_fields()` directly —
the helper is the load-bearing logic; the sync wiring around it is
straightforward field assignment.

Run::

    python manage.py test core.tests.test_sync_docs_index_enrichment -v2
"""

from django.test import TestCase

from core.management.commands.sync_docs_index_to_documents import Command


class EnrichmentFieldsTests(TestCase):
    """``_enrichment_fields(doc_data)`` returns category / tags /
    document_class / is_pinned / retrieval_boost from index frontmatter.
    """

    def setUp(self):
        self.cmd = Command()

    def _doc(self, **kwargs):
        defaults = {
            'path': 'docs/specs/INITIATIVES.md',
            'folder': 'docs/specs',
            'type': 'spec',
            'status': 'active',
            'subsystems': [],
        }
        defaults.update(kwargs)
        return defaults

    def test_category_strips_docs_prefix(self):
        out = self.cmd._enrichment_fields(self._doc(folder='docs/specs'))
        self.assertEqual(out['category'], 'specs')

    def test_category_strips_handoffs(self):
        out = self.cmd._enrichment_fields(self._doc(folder='docs/handoffs'))
        self.assertEqual(out['category'], 'handoffs')

    def test_category_root_for_repo_root_docs(self):
        """CLAUDE.md / README.md have folder='' or 'docs' — both → 'root'."""
        self.assertEqual(
            self.cmd._enrichment_fields(self._doc(folder=''))['category'],
            'root',
        )
        self.assertEqual(
            self.cmd._enrichment_fields(self._doc(folder='docs'))['category'],
            'root',
        )

    def test_category_nested_folder_uses_first_segment(self):
        """docs/handoffs/sub-area → handoffs (top-level category)."""
        out = self.cmd._enrichment_fields(self._doc(folder='docs/handoffs/sub-area'))
        self.assertEqual(out['category'], 'handoffs')

    def test_tags_from_subsystems(self):
        out = self.cmd._enrichment_fields(self._doc(
            subsystems=['initiatives', 'workflow'],
        ))
        self.assertEqual(set(out['tags']), {'initiatives', 'workflow'})

    def test_tags_adds_session_tag_for_handoffs(self):
        out = self.cmd._enrichment_fields(self._doc(
            path='docs/handoffs/SESSION_1234_FIRST_FIRE_FIXES.md',
            folder='docs/handoffs',
            type='handoff',
            subsystems=['workflow'],
        ))
        self.assertIn('session-1234', out['tags'])
        self.assertIn('workflow', out['tags'])

    def test_tags_no_session_tag_for_non_handoffs(self):
        out = self.cmd._enrichment_fields(self._doc(
            path='docs/specs/INITIATIVES.md',
            folder='docs/specs',
            type='spec',
        ))
        self.assertTrue(all(not t.startswith('session-') for t in out['tags']))

    def test_document_class_from_type(self):
        out = self.cmd._enrichment_fields(self._doc(type='narrative'))
        self.assertEqual(out['document_class'], 'narrative')

    def test_document_class_defaults_to_reference_when_type_missing(self):
        out = self.cmd._enrichment_fields(self._doc(type=''))
        self.assertEqual(out['document_class'], 'reference')

    def test_is_pinned_for_active_narrative(self):
        out = self.cmd._enrichment_fields(self._doc(type='narrative', status='active'))
        self.assertTrue(out['is_pinned'])

    def test_is_pinned_for_active_spec(self):
        out = self.cmd._enrichment_fields(self._doc(type='spec', status='active'))
        self.assertTrue(out['is_pinned'])

    def test_is_pinned_for_active_index(self):
        out = self.cmd._enrichment_fields(self._doc(type='index', status='active'))
        self.assertTrue(out['is_pinned'])

    def test_not_pinned_for_handoff_even_when_active(self):
        """Handoffs are session-specific history — never pinned, even active."""
        out = self.cmd._enrichment_fields(self._doc(type='handoff', status='active'))
        self.assertFalse(out['is_pinned'])

    def test_not_pinned_for_superseded_narrative(self):
        out = self.cmd._enrichment_fields(self._doc(type='narrative', status='superseded'))
        self.assertFalse(out['is_pinned'])

    def test_not_pinned_for_archived_spec(self):
        out = self.cmd._enrichment_fields(self._doc(type='spec', status='archived'))
        self.assertFalse(out['is_pinned'])

    def test_retrieval_boost_active_pinned(self):
        out = self.cmd._enrichment_fields(self._doc(type='narrative', status='active'))
        self.assertGreaterEqual(out['retrieval_boost'], 1.5)

    def test_retrieval_boost_superseded(self):
        out = self.cmd._enrichment_fields(self._doc(type='handoff', status='superseded'))
        self.assertLess(out['retrieval_boost'], 1.0)
        self.assertEqual(out['retrieval_boost'], 0.4)

    def test_retrieval_boost_archived(self):
        out = self.cmd._enrichment_fields(self._doc(type='handoff', status='archived'))
        self.assertEqual(out['retrieval_boost'], 0.3)

    def test_retrieval_boost_active_handoff(self):
        """Active handoff (not pinned, but recent) gets the 'active'
        boost — not the pinned multiplier."""
        out = self.cmd._enrichment_fields(self._doc(type='handoff', status='active'))
        # active boost = 1.5; pinned wouldn't change it here since not pinned
        self.assertEqual(out['retrieval_boost'], 1.5)
        self.assertFalse(out['is_pinned'])

    def test_unknown_status_defaults_to_active_boost(self):
        out = self.cmd._enrichment_fields(self._doc(type='spec', status='weird'))
        # 'weird' not in _STATUS_BOOST → falls to default 1.0
        # spec/active wouldn't trigger pinned since status != 'active'
        self.assertFalse(out['is_pinned'])
        self.assertEqual(out['retrieval_boost'], 1.0)
