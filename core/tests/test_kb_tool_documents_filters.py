"""Session 1234 D11 — kb_tool action=documents filter params.

D9 + D10 populated the type-aware enrichment fields on the Document
table (`category`, `tags`, `document_class`, `is_pinned`,
`retrieval_boost`). D11 wires those into kb_tool's `documents` action
so Rigby can scope browsing to "only current architecture docs",
"only Session 1200+ handoffs", "exclude superseded", etc.

These tests verify the handler's filter behavior, ordering, and the
default-exclude-superseded contract.

Run::

    python manage.py test core.tests.test_kb_tool_documents_filters -v2
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase

from content.models import (
    ContentSource,
    ContentStatus,
    Document,
    DocumentType,
)
from core.services.tool_dispatcher import ToolDispatcher

User = get_user_model()


class KbToolDocumentsFilterTests(TestCase):
    """`kb_tool action=documents` filter & ordering contract."""

    def setUp(self):
        self.owner, _ = User.objects.get_or_create(
            username=f'test_d11_{uuid.uuid4().hex[:8]}',
            defaults={'email': 't@x.com', 'is_active': False},
        )
        self.dispatcher = ToolDispatcher()

        # Seed a varied corpus that exercises every filter axis.
        self.pinned_spec = self._mk(
            title='Morning Brief Spec',
            file_path='docs/specs/MORNING_BRIEF.md',
            category='specs',
            tags=['workflow', 'morning_brief'],
            document_class='spec',
            is_pinned=True,
            retrieval_boost=1.5,
            status=ContentStatus.PROCESSED,
        )
        self.pinned_arch = self._mk(
            title='System Map',
            file_path='docs/architecture/COMPLETE_SYSTEM_MAP.md',
            category='architecture',
            tags=['platform'],
            document_class='architecture',
            is_pinned=True,
            retrieval_boost=1.5,
            status=ContentStatus.PROCESSED,
        )
        self.handoff_recent = self._mk(
            title='Session 1234 Handoff',
            file_path='docs/handoffs/SESSION_1234_FIRST_FIRE.md',
            category='handoffs',
            tags=['workflow', 'session-1234'],
            document_class='handoff',
            is_pinned=False,
            retrieval_boost=1.5,
            status=ContentStatus.PROCESSED,
        )
        self.handoff_old = self._mk(
            title='Session 649 Handoff',
            file_path='docs/handoffs/SESSION_649_X.md',
            category='handoffs',
            tags=['session-649'],
            document_class='handoff',
            is_pinned=False,
            retrieval_boost=0.3,
            status=ContentStatus.ARCHIVED,
        )
        self.audit = self._mk(
            title='Celery Audit',
            file_path='docs/audits/CELERY.md',
            category='audits',
            tags=[],
            document_class='audit',
            is_pinned=False,
            retrieval_boost=1.0,
            status=ContentStatus.PROCESSED,
        )

    def _mk(self, **kwargs):
        defaults = dict(
            document_type=DocumentType.MARKDOWN,
            source=ContentSource.IMPORTED,
            owner=self.owner,
            raw_content='x',
            processed_content='x',
            content_hash=uuid.uuid4().hex,
            mime_type='text/markdown',
        )
        defaults.update(kwargs)
        return Document.objects.create(**defaults)

    def _call(self, **payload):
        payload.setdefault('action', 'documents')
        return self.dispatcher._handle_kb_browse(
            tool_name='kb_tool',
            payload=payload,
            user_id=None,
            trace_id=None,
        )

    def test_default_excludes_archived_superseded(self):
        """Default behavior: archived docs are excluded."""
        out = self._call(limit=50)
        titles = {d['title'] for d in out['documents']}
        self.assertNotIn('Session 649 Handoff', titles,
                         "Archived handoff must be excluded by default.")
        self.assertIn('Morning Brief Spec', titles)
        self.assertIn('System Map', titles)
        self.assertEqual(out['applied_filters']['include_superseded'], False)

    def test_include_superseded_brings_them_back(self):
        out = self._call(include_superseded=True, limit=50)
        titles = {d['title'] for d in out['documents']}
        self.assertIn('Session 649 Handoff', titles)
        self.assertEqual(out['applied_filters']['include_superseded'], True)

    def test_filter_by_category(self):
        out = self._call(category='specs', limit=50)
        titles = {d['title'] for d in out['documents']}
        self.assertEqual(titles, {'Morning Brief Spec'})
        self.assertEqual(out['applied_filters']['category'], 'specs')

    def test_filter_by_document_class(self):
        out = self._call(document_class='handoff', limit=50)
        titles = {d['title'] for d in out['documents']}
        # Only the recent handoff (old one excluded by default)
        self.assertEqual(titles, {'Session 1234 Handoff'})

    def test_filter_is_pinned_true(self):
        out = self._call(is_pinned=True, limit=50)
        titles = {d['title'] for d in out['documents']}
        self.assertEqual(titles, {'Morning Brief Spec', 'System Map'})
        self.assertEqual(out['applied_filters']['is_pinned'], True)

    def test_is_pinned_false_does_not_filter(self):
        """LLM-autofill guard per feedback_llm_autofills_boolean_params_with_false:
        is_pinned=False must NOT narrow the result set (would surface only
        unpinned docs). Truthy-only check."""
        out = self._call(is_pinned=False, limit=50)
        titles = {d['title'] for d in out['documents']}
        # Should include all NON-archived docs (defaults applied)
        self.assertIn('Morning Brief Spec', titles, "Pinned docs should NOT be excluded by is_pinned=False")
        self.assertIn('System Map', titles)
        self.assertIn('Session 1234 Handoff', titles)
        # applied_filters reports None to signal the value was ignored
        self.assertIsNone(out['applied_filters']['is_pinned'])

    def test_min_session_filter(self):
        out = self._call(
            min_session=1000,
            include_superseded=True,  # let old handoff into pool
            limit=50,
        )
        titles = {d['title'] for d in out['documents']}
        # Only handoffs (session-tagged) above threshold; recent (1234)
        # passes, old (649) doesn't
        self.assertIn('Session 1234 Handoff', titles)
        self.assertNotIn('Session 649 Handoff', titles)

    def test_min_session_excludes_lower_handoffs(self):
        out = self._call(
            min_session=1500,
            limit=50,
        )
        titles = {d['title'] for d in out['documents']}
        # Session 1234 < 1500; neither handoff passes
        self.assertNotIn('Session 1234 Handoff', titles)
        self.assertNotIn('Session 649 Handoff', titles)

    def test_ordering_pinned_first_then_boost_then_recency(self):
        """Pinned docs surface first regardless of created_at."""
        out = self._call(limit=50)
        # First two should be the two pinned docs
        first_two = [d['title'] for d in out['documents'][:2]]
        self.assertIn('Morning Brief Spec', first_two)
        self.assertIn('System Map', first_two)

    def test_response_includes_enrichment_fields(self):
        out = self._call(category='specs', limit=10)
        d = out['documents'][0]
        # All D9/D10 enrichment keys present
        for k in ('category', 'document_class', 'is_pinned', 'tags',
                  'retrieval_boost'):
            self.assertIn(k, d, f'Response missing enrichment key: {k}')
        self.assertEqual(d['document_class'], 'spec')
        self.assertEqual(d['is_pinned'], True)
        self.assertGreaterEqual(d['retrieval_boost'], 1.5)
        self.assertIn('morning_brief', d['tags'])

    def test_query_substring_still_works(self):
        out = self._call(query='audit', limit=10)
        titles = {d['title'] for d in out['documents']}
        self.assertEqual(titles, {'Celery Audit'})

    def test_combined_filters(self):
        out = self._call(category='handoffs', min_session=1000, limit=50)
        titles = {d['title'] for d in out['documents']}
        self.assertEqual(titles, {'Session 1234 Handoff'})
