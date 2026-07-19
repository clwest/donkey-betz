"""Session 1235 P5#1 — extracted_metadata clobber fix.

Three test classes:

1. ``ExtractedMetadataMergeBehaviorTests`` — direct dict-merge semantics
   (``{**existing, **result}``) preserve rich keys + add processor keys.
2. ``SyncUpdatePathRefreshesMetadataTests`` — the sync update branch
   (``sync_docs_index_to_documents``) refreshes extracted_metadata on
   content-change updates so manual re-syncs self-heal divergence.
3. ``BackfillMigrationLogicTests`` — the migration backfill function
   restores ``scope='docs_index'`` on clobbered rows + preserves the
   TextProcessor processor/encoding/file_size keys.

Per Session 1234 D16 memory rule ``feedback_test_real_db_for_queryset_semantics``:
real DB throughout (no MagicMock'd Document.objects); mocks only at the
DocumentProcessingPipeline boundary where applicable.

Run::

    python manage.py test core.tests.test_extracted_metadata_clobber_fix -v 2 --keepdb
"""

import uuid
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from content.models import Document

User = get_user_model()


class ExtractedMetadataMergeBehaviorTests(TestCase):
    """Direct merge semantics — the fix pattern at all 4 clobber sites."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f'test_meta_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def _make_doc(self, **metadata_kwargs):
        return Document.objects.create(
            title='Test',
            document_type='markdown',
            raw_content='content',
            owner=self.user,
            source='imported',
            extracted_metadata=metadata_kwargs or {},
        )

    def test_merge_preserves_scope_and_subsystems(self):
        """Pre-existing rich keys (scope, subsystems) survive when
        processor metadata is merged in."""
        doc = self._make_doc(
            scope='docs_index',
            subsystems=['agents', 'spiders'],
            outbound_links=['ARCHITECTURE.md'],
        )
        # Simulate the fixed merge from views.py:319 / tasks_misc.py:1678
        processor_meta = {
            'processor': 'TextProcessor',
            'encoding': 'utf-8',
            'file_size': 1024,
        }
        doc.extracted_metadata = {
            **(doc.extracted_metadata or {}),
            **processor_meta,
        }
        doc.save()
        doc.refresh_from_db()

        meta = doc.extracted_metadata
        # Curated keys preserved
        self.assertEqual(meta['scope'], 'docs_index')
        self.assertEqual(meta['subsystems'], ['agents', 'spiders'])
        self.assertEqual(meta['outbound_links'], ['ARCHITECTURE.md'])
        # Processor keys added
        self.assertEqual(meta['processor'], 'TextProcessor')
        self.assertEqual(meta['encoding'], 'utf-8')
        self.assertEqual(meta['file_size'], 1024)

    def test_merge_handles_none_existing_in_memory(self):
        """Defensive ``or {}`` guard handles the None case in memory.
        The DB constraint prevents persisting None, but a code path could
        still produce a None reference (e.g., stale model instance, mock).
        Verify the merge expression doesn't crash on None existing."""
        existing = None
        processor_meta = {'processor': 'TextProcessor', 'encoding': 'utf-8'}
        # The exact fix expression from views.py:319 / tasks_misc.py:1678
        merged = {**(existing or {}), **processor_meta}
        self.assertEqual(merged, processor_meta)

    def test_merge_handles_empty_dict_existing(self):
        """Empty pre-existing dict merges to just the processor keys —
        the realistic upload-from-scratch case."""
        doc = self._make_doc()  # creates with extracted_metadata={}
        processor_meta = {'processor': 'TextProcessor', 'encoding': 'utf-8'}
        doc.extracted_metadata = {
            **(doc.extracted_metadata or {}),
            **processor_meta,
        }
        doc.save()
        doc.refresh_from_db()

        self.assertEqual(doc.extracted_metadata, processor_meta)

    def test_merge_processor_wins_on_key_collision(self):
        """If a key exists in both dicts (unlikely with current writers),
        the processor's value wins — last-write semantics. Documents the
        invariant per Rigby's design note for future divergence."""
        doc = self._make_doc(
            scope='docs_index',
            file_size=99999,  # stale value from sync
        )
        processor_meta = {'file_size': 1024}  # accurate value from processor
        doc.extracted_metadata = {
            **(doc.extracted_metadata or {}),
            **processor_meta,
        }
        doc.save()
        doc.refresh_from_db()

        # Both keys present
        self.assertEqual(doc.extracted_metadata['scope'], 'docs_index')
        # Processor wins on collision
        self.assertEqual(doc.extracted_metadata['file_size'], 1024)


class SyncUpdatePathRefreshesMetadataTests(TestCase):
    """sync_docs_index_to_documents update branch refreshes
    extracted_metadata when content changes — the Session 1235 P5#1
    self-healing path."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f'test_sync_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def test_update_path_refreshes_extracted_metadata_on_content_change(self):
        """Existing Document with stale/clobbered metadata gets refreshed
        scope='docs_index' + other sync keys after content change passes
        through the update branch."""
        from core.management.commands.sync_docs_index_to_documents import Command

        # Pre-state: clobbered Document (processor keys only, no scope)
        doc = Document.objects.create(
            title='Stale Doc',
            document_type='markdown',
            raw_content='OLD CONTENT',
            processed_content='OLD CONTENT',
            content_hash='old_hash_sentinel',
            file_path='docs/specs/STALE.md',
            owner=self.user,
            source='imported',
            extracted_metadata={
                'processor': 'TextProcessor',
                'encoding': 'utf-8',
                'file_size': 100,
            },
        )

        # Build a doc_data shape matching what _index.json provides
        doc_data = {
            'path': 'docs/specs/STALE.md',
            'title': 'Stale Doc',
            'type': 'spec',
            'status': 'active',
            'subsystems': ['agents', 'frontend'],
            'folder': 'docs/specs',
            'inbound_links_count': 5,
            'outbound_links': ['SESSION_1234.md'],
            'has_frontmatter': True,
            'size_bytes': 200,
        }

        # Stub the file read to return NEW content (forces update branch)
        cmd = Command()
        with patch.object(
            __import__('pathlib').Path, 'exists', return_value=True,
        ), patch.object(
            __import__('pathlib').Path, 'read_text', return_value='NEW CONTENT',
        ):
            result = cmd.sync_document(
                doc_data=doc_data,
                base_path=__import__('pathlib').Path('/fake/base'),
                dry_run=False,
                owner=self.user,
            )

        self.assertEqual(result, 'updated')

        doc.refresh_from_db()
        meta = doc.extracted_metadata
        # Refreshed sync keys present
        self.assertEqual(meta['scope'], 'docs_index')
        self.assertEqual(meta['docs_index_type'], 'spec')
        self.assertEqual(meta['subsystems'], ['agents', 'frontend'])
        self.assertEqual(meta['outbound_links'], ['SESSION_1234.md'])
        self.assertEqual(meta['inbound_links_count'], 5)
        # Pre-existing processor keys preserved by the merge
        self.assertEqual(meta['processor'], 'TextProcessor')
        self.assertEqual(meta['encoding'], 'utf-8')

    def test_update_path_skip_when_content_unchanged(self):
        """If content_hash matches AND status already matches
        docs_index_status, the skip-branch returns 'skipped' and does
        NOT touch extracted_metadata. Test doc is seeded with the
        already-correct status so the S2829 skip-branch status-refresh
        path stays dormant — this is the pure no-op case."""
        from core.management.commands.sync_docs_index_to_documents import Command
        from content.models import ContentStatus
        import hashlib

        content = 'IDENTICAL CONTENT'
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        original_meta = {
            'processor': 'TextProcessor',
            'encoding': 'utf-8',
        }
        doc = Document.objects.create(
            title='Stable',
            document_type='markdown',
            raw_content=content,
            processed_content=content,
            content_hash=content_hash,
            file_path='docs/specs/STABLE.md',
            owner=self.user,
            source='imported',
            status=ContentStatus.PROCESSED,  # matches doc_data['status']='active' → PROCESSED
            extracted_metadata=original_meta,
        )

        doc_data = {
            'path': 'docs/specs/STABLE.md',
            'title': 'Stable',
            'type': 'spec',
            'status': 'active',
            'folder': 'docs/specs',
            'size_bytes': len(content),
        }

        cmd = Command()
        with patch.object(
            __import__('pathlib').Path, 'exists', return_value=True,
        ), patch.object(
            __import__('pathlib').Path, 'read_text', return_value=content,
        ):
            result = cmd.sync_document(
                doc_data=doc_data,
                base_path=__import__('pathlib').Path('/fake/base'),
                dry_run=False,
                owner=self.user,
            )

        self.assertEqual(result, 'skipped')
        doc.refresh_from_db()
        # Untouched.
        self.assertEqual(doc.extracted_metadata, original_meta)


class BackfillMigrationLogicTests(TestCase):
    """Session 1235 migration 0047 — backfill logic restores scope on
    clobbered docs corpus rows + preserves processor keys."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f'test_backfill_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def test_backfill_adds_scope_to_clobbered_row(self):
        """A source=imported doc with processor=TextProcessor key + no
        scope key gets scope='docs_index' added; processor keys preserved."""
        from content._backfill_helpers import run_backfill
        clobbered = Document.objects.create(
            title='Clobber Victim',
            document_type='markdown',
            raw_content='content',
            owner=self.user,
            source='imported',
            extracted_metadata={
                'processor': 'TextProcessor',
                'encoding': 'utf-8',
                'file_size': 500,
            },
        )

        count = run_backfill(Document)

        self.assertEqual(count, 1)
        clobbered.refresh_from_db()
        meta = clobbered.extracted_metadata
        self.assertEqual(meta['scope'], 'docs_index')
        # Processor keys preserved
        self.assertEqual(meta['processor'], 'TextProcessor')
        self.assertEqual(meta['encoding'], 'utf-8')
        self.assertEqual(meta['file_size'], 500)

    def test_backfill_skips_already_scoped_rows(self):
        """A source=imported doc that already has scope is not touched."""
        from content._backfill_helpers import run_backfill
        intact = Document.objects.create(
            title='Intact',
            document_type='markdown',
            raw_content='content',
            owner=self.user,
            source='imported',
            extracted_metadata={
                'scope': 'docs_index',
                'subsystems': ['agents'],
                'processor': 'TextProcessor',
            },
        )

        count = run_backfill(Document)

        self.assertEqual(count, 0)
        intact.refresh_from_db()
        self.assertEqual(intact.extracted_metadata['subsystems'], ['agents'])

    def test_backfill_skips_non_imported_docs(self):
        """An upload (source='upload') with TextProcessor metadata and
        no scope is NOT touched — those aren't docs corpus rows."""
        from content._backfill_helpers import run_backfill
        Document.objects.create(
            title='User Upload',
            document_type='markdown',
            raw_content='content',
            owner=self.user,
            source='upload',
            extracted_metadata={'processor': 'TextProcessor'},
        )

        count = run_backfill(Document)

        self.assertEqual(count, 0)
