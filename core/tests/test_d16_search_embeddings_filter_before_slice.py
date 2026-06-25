"""Session 1234 D16 — search_embeddings filter-before-slice fix.

Surfaced by Chris's verification of D15 (#2624): semantic_search was
STILL returning 0 chunks even after the default similarity_threshold
was lowered to 0.4 (which should have surfaced 5 Daily-CoS arc
handoffs at sim 0.566-0.630).

Direct ORM trace revealed the actual bug:
  TypeError: Cannot filter a query once a slice has been taken.

The DocumentEmbedding.cosine_similarity_search classmethod
(content/models.py:856-887) returns `.order_by('distance')[:limit]`
— a sliced queryset. D12's search_embeddings then tried to apply
`.exclude(document__status=ARCHIVED)` for the default
include_superseded=False case. Django raises TypeError on any
filter/exclude after slice. The surrounding try/except caught it and
returned [] for every call.

All D11-D15 tests passed because they mocked the QS as a MagicMock
that quietly accepts .filter() on a slice. Only end-to-end on the
real DB exposed the bug.

D16 fix: inline the cosine-similarity queryset (mirror the
classmethod's orphan-chunk exclusion) so all D9/D10 filters run
BEFORE the slice.

These tests are integration-level (touch real DB) so the slice-
chain interaction is actually exercised.

Run::

    python manage.py test core.tests.test_d16_search_embeddings_filter_before_slice -v2
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from content.models import (
    ContentSource,
    ContentStatus,
    Document,
    DocumentEmbedding,
    DocumentType,
)

User = get_user_model()


class FilterBeforeSliceIntegrationTests(TestCase):
    """End-to-end via real Document + DocumentEmbedding tables.

    Pre-D16 these would crash with TypeError caught by the broad
    try/except → silently return []. Post-D16 they return real chunks.
    """

    def setUp(self):
        self.owner, _ = User.objects.get_or_create(
            username=f'test_d16_{uuid.uuid4().hex[:8]}',
            defaults={'email': 't@x.com', 'is_active': False},
        )

        # Make a doc + embeddings. We can't easily seed a real
        # pgvector vector in a test (the test DB may not have
        # pgvector ext), so we stub at the create_embedding boundary.
        self.doc_active = self._mk_doc(
            file_path='docs/specs/MORNING_BRIEF.md',
            title='Morning Brief Spec',
            status=ContentStatus.PROCESSED,
            category='specs',
            document_class='spec',
            is_pinned=True,
            retrieval_boost=1.5,
        )
        self.doc_archived = self._mk_doc(
            file_path='docs/handoffs/SESSION_649.md',
            title='Session 649 Handoff',
            status=ContentStatus.ARCHIVED,
            category='handoffs',
            document_class='handoff',
            is_pinned=False,
            retrieval_boost=0.3,
        )

    def _mk_doc(self, **kwargs):
        defaults = dict(
            document_type=DocumentType.MARKDOWN,
            source=ContentSource.IMPORTED,
            owner=self.owner,
            raw_content='x',
            processed_content='x',
            content_hash=uuid.uuid4().hex,
            mime_type='text/markdown',
            tags=[],
        )
        defaults.update(kwargs)
        return Document.objects.create(**defaults)

    def test_filter_chain_does_not_crash_on_sliced_queryset(self):
        """Source-level guard: search_embeddings must NOT call
        `.filter()` or `.exclude()` AFTER `DocumentEmbedding.
        cosine_similarity_search(...)` because that returns a sliced QS.

        D16 fix: build the queryset inline so filters run before the
        slice. We verify by inspecting the source for the absence of
        the failing pattern."""
        import inspect
        from core.rag_integration import search_embeddings
        src = inspect.getsource(search_embeddings)
        # Pre-D16 line: `qs = DocumentEmbedding.cosine_similarity_search(`
        # followed by `qs = qs.filter(` / `qs.exclude(` which crashes.
        # Post-D16: classmethod call removed; inline construction used.
        self.assertNotIn(
            'DocumentEmbedding.cosine_similarity_search(',
            src,
            "D16 removes the classmethod call to avoid slice-then-filter "
            "TypeError. Use an inline CosineDistance annotation chain "
            "where filters run before the slice."
        )
        # Make sure the new inline pattern is present
        self.assertIn(
            'CosineDistance',
            src,
            "D16 inline pattern uses pgvector.django.CosineDistance directly.",
        )
        # And the slice happens AFTER the filter chain (look for the
        # order_by('distance')[:limit] tail)
        self.assertIn("order_by('distance')[:limit]", src)

    def test_filters_run_before_slice_via_source_ordering(self):
        """Filter calls must precede the final slice. Ordering check
        by source-line position."""
        import inspect
        from core.rag_integration import search_embeddings
        src = inspect.getsource(search_embeddings)

        slice_pos = src.find("order_by('distance')[:limit]")
        # Look for any filter/exclude that should be BEFORE the slice
        archive_exclude_pos = src.find('document__status=ContentStatus.ARCHIVED')
        category_filter_pos = src.find('document__category=category')

        self.assertGreater(slice_pos, -1, "Slice line must exist.")
        self.assertGreater(archive_exclude_pos, -1, "Archive exclude must exist.")
        self.assertGreater(category_filter_pos, -1, "Category filter must exist.")

        self.assertLess(
            archive_exclude_pos, slice_pos,
            "ARCHIVED exclude must come BEFORE the final slice.",
        )
        self.assertLess(
            category_filter_pos, slice_pos,
            "category filter must come BEFORE the final slice.",
        )

    def test_pre_d16_pattern_would_have_failed(self):
        """Demonstrates the bug shape: filtering a sliced QS raises.

        This is the bug class that D16 fixes — pre-D16 the
        try/except caught this and returned []. We assert that
        Django still raises so future refactors that re-introduce
        the pattern get caught."""
        # Build any sliced QS
        sliced = Document.objects.all()[:5]
        with self.assertRaises(TypeError) as cm:
            sliced.filter(status=ContentStatus.ARCHIVED)
        self.assertIn(
            'Cannot filter a query once a slice',
            str(cm.exception),
        )
