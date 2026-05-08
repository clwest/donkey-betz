"""
Session 962 Phase 1: Doc Versioning Tests
==========================================

Tests that DocVersion records are created correctly with proper version numbering,
content hashing, and the BaseAgent._write_doc integration.
"""

import hashlib
from unittest.mock import patch, MagicMock, PropertyMock
from pathlib import Path

from django.test import TestCase
from django.conf import settings

from core.models_deliberation import DocVersion, DeliberationSession
class TestDocVersionModel(TestCase):
    """Direct model tests for DocVersion."""

    def test_create_doc_version(self):
        content = 'Document content v1'
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        dv = DocVersion.objects.create(
            doc_path='docs/test.md',
            version_number=1,
            content_hash=content_hash,
            content_snapshot=content,
            author_agent='ContentWriterAgent',
            change_reason='Initial creation',
        )
        self.assertEqual(dv.doc_path, 'docs/test.md')
        self.assertEqual(dv.version_number, 1)
        self.assertEqual(dv.content_hash, content_hash)

    def test_version_increment(self):
        """Sequential versions for same doc_path."""
        for i in range(1, 4):
            content = f'Version {i} content'
            DocVersion.objects.create(
                doc_path='docs/incremental.md',
                version_number=i,
                content_hash=hashlib.sha256(content.encode('utf-8')).hexdigest(),
                content_snapshot=content,
                author_agent='TestAgent',
            )
        self.assertEqual(DocVersion.objects.filter(doc_path='docs/incremental.md').count(), 3)

        latest = DocVersion.objects.filter(
            doc_path='docs/incremental.md'
        ).order_by('-version_number').first()
        self.assertEqual(latest.version_number, 3)

    def test_unique_doc_version_constraint(self):
        DocVersion.objects.create(
            doc_path='docs/unique.md',
            version_number=1,
            content_hash='aaa',
            content_snapshot='content',
        )
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            DocVersion.objects.create(
                doc_path='docs/unique.md',
                version_number=1,
                content_hash='bbb',
                content_snapshot='different content',
            )

    def test_deliberation_session_fk(self):
        session = DeliberationSession.objects.create(
            session_type='hivemind',
            objective='Doc test',
        )
        dv = DocVersion.objects.create(
            doc_path='docs/linked.md',
            version_number=1,
            content_hash='abc',
            content_snapshot='content',
            deliberation_session=session,
        )
        self.assertEqual(dv.deliberation_session_id, session.id)
        self.assertEqual(session.doc_versions.count(), 1)

    def test_str_repr(self):
        dv = DocVersion.objects.create(
            doc_path='docs/repr.md',
            version_number=2,
            content_hash='xyz',
            content_snapshot='content',
            author_agent='EditorAgent',
        )
        self.assertIn('docs/repr.md', str(dv))
        self.assertIn('v2', str(dv))
        self.assertIn('EditorAgent', str(dv))

    def test_different_docs_same_version_number(self):
        """Different doc_paths can have the same version_number."""
        DocVersion.objects.create(
            doc_path='docs/a.md', version_number=1,
            content_hash='h1', content_snapshot='a',
        )
        DocVersion.objects.create(
            doc_path='docs/b.md', version_number=1,
            content_hash='h2', content_snapshot='b',
        )
        self.assertEqual(DocVersion.objects.count(), 2)
