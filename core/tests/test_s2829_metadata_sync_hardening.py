"""S2829 metadata-sync hardening — stop-writer guard + sync skip-branch closure.

At S2829 open (2026-07-19) the sanity checks re-surfaced 870 rows in the
same drift class the S2826 backfill was supposed to close permanently.
Joint Claude + Rigby SIGN traced two independent defects:

1. **Backfill invocation is unguarded** — running the S2826 backfill
   command as a bare `python manage.py backfill_document_status_from_docs_index`
   writes without asking, and if `_index.json` is mid-regeneration (e.g.
   `build_docs_index` still running), the command flips rows to the
   *old* mapping. That's the exact writer signature behind the 866-row
   bulk `.update()` at 2026-07-19T03:17:40 UTC.

2. **sync_docs_index_to_documents skip-branch does not touch status.**
   S2826 shipped the fix in the *update* branch (content_hash mismatch)
   but returned `'skipped'` early when content_hash matched. Every
   sync that ran after backfill-with-mid-flight-index preserved the
   incorrect archived state on the canonical anchors, because their
   file content didn't change from one sync to the next.

Two test classes:

* ``BackfillApplyGuardTests`` — bare / --dry-run / --apply / both-flags.
* ``SyncSkipBranchStatusRefreshTests`` — status is corrected in the
  content-unchanged branch when it drifts from docs_index_status.

Both classes hit a real DB (per ``feedback_test_real_db_for_queryset_semantics``).

Run::

    python manage.py test core.tests.test_s2829_metadata_sync_hardening -v 2 --keepdb
"""

from __future__ import annotations

import json
import tempfile
import uuid
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from content.models import ContentStatus, Document

User = get_user_model()


class _IsolatedIndexMixin:
    """Point `docs/_index.json` at a temp file so each test controls truth."""

    def _write_index(self, tmp_dir: Path, documents: list[dict]) -> Path:
        docs_dir = tmp_dir / 'docs'
        docs_dir.mkdir(exist_ok=True)
        idx_path = docs_dir / '_index.json'
        idx_path.write_text(json.dumps({'documents': documents}))
        return idx_path


class BackfillApplyGuardTests(_IsolatedIndexMixin, TestCase):
    """S2829 stop-writer guard on backfill_document_status_from_docs_index."""

    def _run_backfill(self, tmp_dir: Path, **flags):
        """Run the command with BASE_DIR pointed at the temp dir."""
        out, err = StringIO(), StringIO()
        with override_settings(BASE_DIR=str(tmp_dir)):
            call_command(
                'backfill_document_status_from_docs_index',
                stdout=out, stderr=err, **flags,
            )
        return out.getvalue(), err.getvalue()

    def _seed_drifted_doc(self, tmp_dir: Path) -> Document:
        """Create a Document that _index.json says is 'active' but DB
        has archived — the S2826 drift shape."""
        owner = User.objects.create_user(
            username=f'guard_{uuid.uuid4().hex[:8]}',
            password='test',
        )
        doc = Document.objects.create(
            title='Anchor',
            document_type='markdown',
            file_path='docs/ANCHOR.md',
            raw_content='body',
            owner=owner,
            source='imported',
            status=ContentStatus.ARCHIVED,  # drifted state
            canonical_authority='repo_canonical',
        )
        self._write_index(tmp_dir, [{
            'path': 'docs/ANCHOR.md',
            'status': 'active',
        }])
        return doc

    def test_bare_invocation_raises_command_error(self):
        """Neither --dry-run nor --apply → refuse. Prevents unattended
        bulk sweeps at mid-flight _index.json moments."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            self._seed_drifted_doc(tmp_dir)
            with self.assertRaises(CommandError) as cm:
                self._run_backfill(tmp_dir)
            self.assertIn('Explicit mode required', str(cm.exception))

    def test_both_flags_raises_command_error(self):
        """--dry-run + --apply are mutually exclusive."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            self._seed_drifted_doc(tmp_dir)
            with self.assertRaises(CommandError) as cm:
                self._run_backfill(tmp_dir, dry_run=True, apply=True)
            self.assertIn('mutually exclusive', str(cm.exception))

    def test_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            doc = self._seed_drifted_doc(tmp_dir)
            out, _ = self._run_backfill(tmp_dir, dry_run=True)
            doc.refresh_from_db()
            self.assertEqual(doc.status, ContentStatus.ARCHIVED)  # unchanged
            self.assertIn('DRY RUN', out)

    def test_apply_writes_and_restores(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            doc = self._seed_drifted_doc(tmp_dir)
            out, _ = self._run_backfill(tmp_dir, apply=True)
            doc.refresh_from_db()
            self.assertEqual(doc.status, ContentStatus.PROCESSED)
            self.assertIn('RESTORATION COMPLETE', out)

    def test_snapshot_hash_is_logged(self):
        """S2829 snapshot: index file is hashed at command start so a
        post-hoc audit can see which _index.json state the command
        actually operated on."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            self._seed_drifted_doc(tmp_dir)
            out, _ = self._run_backfill(tmp_dir, dry_run=True)
            self.assertIn('sha256=', out)


class SyncSkipBranchStatusRefreshTests(_IsolatedIndexMixin, TestCase):
    """S2829 sync skip-branch closure — even when content_hash matches,
    status is refreshed to docs_index_status ground truth."""

    def _run_sync(self, tmp_dir: Path, **flags):
        out, err = StringIO(), StringIO()
        with override_settings(BASE_DIR=str(tmp_dir)):
            call_command(
                'sync_docs_index_to_documents',
                stdout=out, stderr=err, **flags,
            )
        return out.getvalue(), err.getvalue()

    def _seed_content_unchanged_drift(
        self,
        tmp_dir: Path,
        *,
        db_status: str,
        index_status: str,
        content: str = 'stable body',
    ) -> Document:
        """Create a Document whose on-disk content matches its stored
        content_hash — so sync will hit the skip-branch — but DB status
        drifts from docs_index_status."""
        import hashlib
        owner = User.objects.create_user(
            username=f'sync_{uuid.uuid4().hex[:8]}',
            password='test',
        )
        # Write file on disk so sync's file-existence check + read succeeds.
        docs_dir = tmp_dir / 'docs'
        docs_dir.mkdir(exist_ok=True)
        file_path = docs_dir / 'ANCHOR.md'
        file_path.write_text(content)
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        doc = Document.objects.create(
            title='Anchor',
            document_type='markdown',
            file_path='docs/ANCHOR.md',
            raw_content=content,
            content_hash=content_hash,
            owner=owner,
            source='imported',
            status=db_status,
            canonical_authority='repo_canonical',
        )
        self._write_index(tmp_dir, [{
            'path': 'docs/ANCHOR.md',
            'status': index_status,
            'title': 'Anchor',
            'type': 'reference',
            'folder': 'docs',
            'subsystems': [],
        }])
        return doc

    def test_skip_branch_refreshes_archived_to_processed(self):
        """The S2829 exact failure mode: content unchanged, DB=archived,
        index=active → sync must refresh to processed."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            doc = self._seed_content_unchanged_drift(
                tmp_dir,
                db_status=ContentStatus.ARCHIVED,
                index_status='active',
            )
            out, _ = self._run_sync(tmp_dir)
            doc.refresh_from_db()
            self.assertEqual(doc.status, ContentStatus.PROCESSED)
            self.assertIn('Status refreshed:', out)

    def test_skip_branch_leaves_matching_status_alone(self):
        """When status already matches index truth, skip-branch is a
        no-op — no write, no updated_at bump."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            doc = self._seed_content_unchanged_drift(
                tmp_dir,
                db_status=ContentStatus.PROCESSED,
                index_status='active',
            )
            original_updated = doc.updated_at
            self._run_sync(tmp_dir)
            doc.refresh_from_db()
            self.assertEqual(doc.status, ContentStatus.PROCESSED)
            self.assertEqual(doc.updated_at, original_updated)

    def test_skip_branch_dry_run_does_not_write(self):
        """Dry-run in the skip-branch reports the drift without writing."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            doc = self._seed_content_unchanged_drift(
                tmp_dir,
                db_status=ContentStatus.ARCHIVED,
                index_status='active',
            )
            self._run_sync(tmp_dir, dry_run=True)
            doc.refresh_from_db()
            self.assertEqual(doc.status, ContentStatus.ARCHIVED)  # unchanged

    def test_skip_branch_refreshes_processed_to_archived_on_supersede(self):
        """Symmetric: if index flips a doc to superseded, sync
        skip-branch archives the DB row on next run even with unchanged
        content."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            doc = self._seed_content_unchanged_drift(
                tmp_dir,
                db_status=ContentStatus.PROCESSED,
                index_status='superseded',
            )
            self._run_sync(tmp_dir)
            doc.refresh_from_db()
            self.assertEqual(doc.status, ContentStatus.ARCHIVED)
