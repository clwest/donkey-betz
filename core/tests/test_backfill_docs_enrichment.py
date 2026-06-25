"""Session 1234 D10 — backfill_docs_enrichment mgmt command.

The D9 sync_docs_index_to_documents change populates enrichment fields
only for newly created/updated docs. D10 backfills the pre-existing
2,732 rows by replaying docs/_index.json against the same helper.

Tests verify:
1. Backfill correctly populates the 5 enrichment fields
2. Idempotency — running twice doesn't double-write or churn
3. --dry-run reports counts without mutating
4. --limit short-circuits as expected
5. Missing-in-DB rows are counted but skipped (no crash)
6. Tag order normalization (set-equal not list-equal)

Run::

    python manage.py test core.tests.test_backfill_docs_enrichment -v2
"""

import json
import os
import tempfile
import uuid
from io import StringIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from content.models import Document, ContentStatus, DocumentType, ContentSource

User = get_user_model()


class BackfillDocsEnrichmentTests(TestCase):
    """End-to-end behavior of `backfill_docs_enrichment`."""

    def setUp(self):
        # System user for Document.owner FK
        self.owner, _ = User.objects.get_or_create(
            username=f'test_d10_{uuid.uuid4().hex[:8]}',
            defaults={'email': 't@x.com', 'is_active': False},
        )

        # Seed 4 Documents that match what we'll put in _index.json
        self.docs = []
        self.docs.append(self._mk_doc(
            file_path='docs/handoffs/SESSION_1100_X.md',
            title='SESSION 1100 X',
        ))
        self.docs.append(self._mk_doc(
            file_path='docs/specs/MORNING_BRIEF.md',
            title='Morning Brief Spec',
        ))
        self.docs.append(self._mk_doc(
            file_path='docs/narratives/CONTENT_PIPELINE.md',
            title='Content Pipeline Narrative',
        ))
        self.docs.append(self._mk_doc(
            file_path='docs/audits/CELERY.md',
            title='Celery Audit',
        ))

        # Build a synthetic _index.json on disk
        self._index_payload = {
            'documents': [
                {
                    'path': 'docs/handoffs/SESSION_1100_X.md',
                    'folder': 'docs/handoffs',
                    'type': 'handoff',
                    'status': 'archived',
                    'subsystems': ['workflow'],
                },
                {
                    'path': 'docs/specs/MORNING_BRIEF.md',
                    'folder': 'docs/specs',
                    'type': 'spec',
                    'status': 'active',
                    'subsystems': ['workflow', 'morning_brief'],
                },
                {
                    'path': 'docs/narratives/CONTENT_PIPELINE.md',
                    'folder': 'docs/narratives',
                    'type': 'narrative',
                    'status': 'active',
                    'subsystems': ['content'],
                },
                {
                    'path': 'docs/audits/CELERY.md',
                    'folder': 'docs/audits',
                    'type': 'audit',
                    'status': 'active',
                    'subsystems': [],
                },
            ],
        }

        # Write to a temp index file the command will read
        self.tmpdir = tempfile.mkdtemp()
        self.index_path = Path(self.tmpdir) / '_index.json'
        with open(self.index_path, 'w') as f:
            json.dump(self._index_payload, f)

    def tearDown(self):
        try:
            os.remove(self.index_path)
            os.rmdir(self.tmpdir)
        except OSError:
            pass

    def _mk_doc(self, *, file_path, title):
        """Pre-D9 baseline: no enrichment fields set."""
        return Document.objects.create(
            title=title,
            file_path=file_path,
            document_type=DocumentType.MARKDOWN,
            status=ContentStatus.PROCESSED,
            source=ContentSource.IMPORTED,
            owner=self.owner,
            raw_content='x',
            processed_content='x',
            content_hash=uuid.uuid4().hex,
            mime_type='text/markdown',
            # Explicitly flat defaults:
            category='',
            tags=[],
            document_class='reference',
            is_pinned=False,
            retrieval_boost=1.0,
        )

    def _refresh(self, doc):
        doc.refresh_from_db()
        return doc

    def _run_cmd(self, **kwargs):
        out = StringIO()
        call_command(
            'backfill_docs_enrichment',
            index=str(self.index_path),
            stdout=out,
            **kwargs,
        )
        return out.getvalue()

    def test_dry_run_does_not_mutate(self):
        out = self._run_cmd(dry_run=True)
        self.assertIn('DRY RUN COMPLETE', out)

        # All 4 still flat
        for d in self.docs:
            d = self._refresh(d)
            self.assertEqual(d.category, '')
            self.assertEqual(d.tags, [])
            self.assertEqual(d.document_class, 'reference')
            self.assertFalse(d.is_pinned)
            self.assertEqual(d.retrieval_boost, 1.0)

    def test_real_run_populates_enrichment(self):
        out = self._run_cmd()
        self.assertIn('BACKFILL COMPLETE', out)

        handoff = self._refresh(self.docs[0])
        self.assertEqual(handoff.category, 'handoffs')
        self.assertIn('workflow', handoff.tags)
        self.assertIn('session-1100', handoff.tags)
        self.assertEqual(handoff.document_class, 'handoff')
        self.assertFalse(handoff.is_pinned,
                         "Handoff must never be pinned, even archived.")
        # archived → boost 0.3
        self.assertEqual(handoff.retrieval_boost, 0.3)

        spec = self._refresh(self.docs[1])
        self.assertEqual(spec.category, 'specs')
        self.assertEqual(spec.document_class, 'spec')
        self.assertTrue(spec.is_pinned, "Active spec must be pinned.")
        self.assertGreaterEqual(spec.retrieval_boost, 1.5)

        narrative = self._refresh(self.docs[2])
        self.assertEqual(narrative.category, 'narratives')
        self.assertEqual(narrative.document_class, 'narrative')
        self.assertTrue(narrative.is_pinned)

        audit = self._refresh(self.docs[3])
        self.assertEqual(audit.category, 'audits')
        self.assertEqual(audit.document_class, 'audit')
        self.assertFalse(audit.is_pinned,
                         "Audit must not be pinned (ages out).")

    def test_idempotent_second_run_reports_unchanged(self):
        self._run_cmd()  # first
        out = self._run_cmd()  # second — should be all unchanged
        self.assertIn('Unchanged:        4', out)
        self.assertIn('Updated:           0', out)

    def test_limit_short_circuits(self):
        out = self._run_cmd(limit=2)
        self.assertIn('Hit --limit=2', out)
        self.assertIn('Updated:           2', out)

        # Two docs got enriched, two didn't (whichever came first in the
        # index payload order)
        updated_count = sum(
            1 for d in self.docs
            if self._refresh(d).document_class != 'reference'
        )
        self.assertEqual(updated_count, 2)

    def test_missing_in_db_counted_not_crashed(self):
        # Add a 5th entry to the index that doesn't exist in the DB
        self._index_payload['documents'].append({
            'path': 'docs/handoffs/SESSION_9999_GHOST.md',
            'folder': 'docs/handoffs',
            'type': 'handoff',
            'status': 'archived',
            'subsystems': [],
        })
        with open(self.index_path, 'w') as f:
            json.dump(self._index_payload, f)

        out = self._run_cmd()
        self.assertIn('Missing in DB:    1', out)
        self.assertIn('Updated:           4', out)

    def test_tags_order_does_not_trigger_unnecessary_update(self):
        # Pre-seed handoff with the EXPECTED tags but in different order
        self.docs[0].tags = ['session-1100', 'workflow']  # reversed vs default
        self.docs[0].category = 'handoffs'
        self.docs[0].document_class = 'handoff'
        self.docs[0].is_pinned = False
        self.docs[0].retrieval_boost = 0.3
        self.docs[0].save()

        out = self._run_cmd()
        # The handoff should be Unchanged (tags compare set-equal, not
        # list-equal). The other 3 should be Updated.
        self.assertIn('Updated:           3', out)
        self.assertIn('Unchanged:        1', out)
