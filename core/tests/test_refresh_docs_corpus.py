"""Session 1235 P5#2 — `core.tasks.refresh_docs_corpus` daily auto-cascade.

Two test classes:

1. ``RefreshDocsCorpusBehaviorTests`` — task behavior across the four
   gate paths: skip / hash-delta cascade / unembedded-secondary-trigger /
   force / cascade failure. Real DB for Document + DocumentEmbedding
   queries (per Session 1234 D16 memory rule
   ``feedback_test_real_db_for_queryset_semantics``); mocks only at the
   `call_command` and `.delay()` boundaries.

2. ``RefreshDocsCorpusBeatRegistrationTests`` — source-level guard that
   the beat schedule has the entry at 4:00 AM Denver and that the task
   is NOT in ``LOCAL_DENY_TASKS`` (delta cost is sub-penny; local Rigby
   benefits from fresh corpus).

Run::

    python manage.py test core.tests.test_refresh_docs_corpus -v 2 --keepdb
"""

import hashlib
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase

from content.models import Document, DocumentEmbedding, EmbeddingModel

User = get_user_model()


CACHE_KEY = 'docs_corpus:last_index_hash'


def _current_index_hash() -> str:
    """Read docs/_index.json from disk and return its sha256."""
    index_path = Path(settings.BASE_DIR) / 'docs' / '_index.json'
    if not index_path.exists():
        return ''
    with open(index_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


class RefreshDocsCorpusBehaviorTests(TestCase):
    """Session 1235 P5#2 — refresh_docs_corpus gate logic."""

    def setUp(self):
        cache.delete(CACHE_KEY)
        # TestCase wraps each test in a transaction, so any Document /
        # DocumentEmbedding rows created here are rolled back at test end.
        # Fresh test DB has 0 rows in both tables (verified pre-write).
        import uuid
        self.user = User.objects.create_user(
            username=f'test_refresh_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def tearDown(self):
        cache.delete(CACHE_KEY)

    def _make_unembedded_doc(self, title='Test Doc'):
        return Document.objects.create(
            title=title,
            document_type='markdown',
            raw_content='non-empty content for unembedded queryset',
            owner=self.user,
        )

    def _make_embedded_doc(self, title='Embedded Doc'):
        doc = Document.objects.create(
            title=title,
            document_type='markdown',
            raw_content='non-empty content',
            owner=self.user,
        )
        DocumentEmbedding.objects.create(
            document=doc,
            embedding_model=EmbeddingModel.OPENAI_SMALL,
            chunk_index=0,
            chunk_text='chunk text',
            chunk_size=10,
        )
        return doc

    def test_skip_when_hash_matches_and_no_unembedded(self):
        """Cache hash == current AND 0 unembedded docs → skip (no cascade,
        no fan-out). The fully-synced steady state."""
        from core.tasks import refresh_docs_corpus

        cache.set(CACHE_KEY, _current_index_hash(), timeout=None)
        # No Document rows created — 0 unembedded.

        with patch('django.core.management.call_command') as mock_cmd, \
             patch('core.tasks.generate_document_embeddings.delay') as mock_delay:
            result = refresh_docs_corpus()

        self.assertTrue(result['success'])
        self.assertFalse(result['index_changed'])
        self.assertEqual(result['unembedded_before'], 0)
        self.assertEqual(result['embedding_tasks_dispatched'], 0)
        self.assertIsNone(result['sync_summary'])
        mock_cmd.assert_not_called()
        mock_delay.assert_not_called()

    def test_hash_delta_triggers_cascade_and_fan_out(self):
        """Cache hash != current → cascade runs (steps 1-3) AND embedding
        fan-out fires for every unembedded doc."""
        from core.tasks import refresh_docs_corpus

        cache.set(CACHE_KEY, 'sentinel_wrong_hash', timeout=None)
        for i in range(3):
            self._make_unembedded_doc(title=f'Cascade Test Doc {i}')

        with patch('django.core.management.call_command') as mock_cmd, \
             patch('core.tasks.generate_document_embeddings.delay') as mock_delay:
            result = refresh_docs_corpus()

        self.assertTrue(result['success'])
        self.assertTrue(result['index_changed'])
        self.assertEqual(result['unembedded_before'], 3)
        self.assertEqual(result['sync_summary'], 'cascade_1_3_complete')
        self.assertEqual(result['embedding_tasks_dispatched'], 3)

        # Cascade ran 3 commands in order.
        self.assertEqual(mock_cmd.call_count, 3)
        cascade_names = [c.args[0] for c in mock_cmd.call_args_list]
        self.assertEqual(
            cascade_names,
            ['build_docs_index', 'build_rag_corpus',
             'sync_docs_index_to_documents'],
        )

        # Embedding fan-out dispatched per-doc.
        self.assertEqual(mock_delay.call_count, 3)

    def test_unembedded_count_secondary_trigger(self):
        """Hash unchanged BUT unembedded > 0 → skip cascade (steps 1-3),
        run embedding fan-out only. Self-healing path for partial step-4
        failures (rate-limit / network hiccup on prior fire)."""
        from core.tasks import refresh_docs_corpus

        cache.set(CACHE_KEY, _current_index_hash(), timeout=None)
        for i in range(2):
            self._make_unembedded_doc(title=f'Stuck Doc {i}')

        with patch('django.core.management.call_command') as mock_cmd, \
             patch('core.tasks.generate_document_embeddings.delay') as mock_delay:
            result = refresh_docs_corpus()

        self.assertTrue(result['success'])
        self.assertFalse(result['index_changed'])
        self.assertEqual(result['unembedded_before'], 2)
        # Cascade SKIPPED — hash matched — but embedding fired.
        self.assertIsNone(result['sync_summary'])
        self.assertEqual(result['embedding_tasks_dispatched'], 2)
        mock_cmd.assert_not_called()
        self.assertEqual(mock_delay.call_count, 2)

    def test_force_true_runs_cascade_regardless_of_hash(self):
        """force=True bypasses the hash gate. Useful for manual triggers
        (PA tool, post-deploy refresh)."""
        from core.tasks import refresh_docs_corpus

        cache.set(CACHE_KEY, _current_index_hash(), timeout=None)
        # 0 unembedded docs — would normally skip.

        with patch('django.core.management.call_command') as mock_cmd, \
             patch('core.tasks.generate_document_embeddings.delay') as mock_delay:
            result = refresh_docs_corpus(force=True)

        self.assertTrue(result['success'])
        # index_changed reflects file hash reality (False — file unchanged),
        # NOT whether the cascade ran. Force flips sync execution, not the
        # hash semantic. Cascade execution is captured by sync_summary.
        self.assertFalse(result['index_changed'])
        self.assertEqual(result['sync_summary'], 'cascade_1_3_complete')
        self.assertEqual(mock_cmd.call_count, 3)
        mock_delay.assert_not_called()  # still 0 unembedded → no fan-out

    def test_cascade_failure_returns_error_telemetry(self):
        """If any cascade step raises, the task captures error telemetry
        and returns success=False with stage='cascade_1_3'. Cache hash
        is NOT updated (so next fire retries)."""
        from core.tasks import refresh_docs_corpus

        cache.set(CACHE_KEY, 'sentinel_wrong_hash', timeout=None)
        self._make_unembedded_doc()

        def fake_call(*args, **kwargs):
            if args[0] == 'build_rag_corpus':
                raise RuntimeError('simulated rag failure')

        with patch('django.core.management.call_command', side_effect=fake_call), \
             patch('core.tasks.generate_document_embeddings.delay') as mock_delay:
            result = refresh_docs_corpus()

        self.assertFalse(result['success'])
        self.assertEqual(result['stage'], 'cascade_1_3')
        self.assertIn('RuntimeError', result['error'])
        self.assertIn('simulated rag failure', result['error'])
        # No fan-out on cascade failure.
        mock_delay.assert_not_called()
        # Cache hash NOT updated.
        self.assertEqual(cache.get(CACHE_KEY), 'sentinel_wrong_hash')

    def test_cache_updated_on_success(self):
        """After a successful cascade, cache holds the current real hash."""
        from core.tasks import refresh_docs_corpus

        cache.set(CACHE_KEY, 'sentinel_wrong_hash', timeout=None)

        with patch('django.core.management.call_command'), \
             patch('core.tasks.generate_document_embeddings.delay'):
            refresh_docs_corpus()

        cached = cache.get(CACHE_KEY)
        self.assertIsNotNone(cached)
        self.assertEqual(cached, _current_index_hash())
        self.assertNotEqual(cached, 'sentinel_wrong_hash')

    def test_empty_embedding_filter_excludes_blank_raw_content(self):
        """Documents with blank raw_content must NOT count as unembedded
        (would cause infinite re-dispatch loops — same shape as
        embed_documents --all-unembedded filter at line 34)."""
        from core.tasks import refresh_docs_corpus

        cache.set(CACHE_KEY, _current_index_hash(), timeout=None)
        # One blank-content doc — should NOT be counted as unembedded.
        Document.objects.create(
            title='Blank',
            document_type='markdown',
            raw_content='',
            owner=self.user,
        )

        with patch('django.core.management.call_command') as mock_cmd, \
             patch('core.tasks.generate_document_embeddings.delay') as mock_delay:
            result = refresh_docs_corpus()

        self.assertTrue(result['success'])
        self.assertEqual(result['unembedded_before'], 0)
        mock_cmd.assert_not_called()
        mock_delay.assert_not_called()


class RefreshDocsCorpusBeatRegistrationTests(TestCase):
    """Source-level guard: beat schedule has the refresh-docs-corpus entry
    at 4:00 AM Denver and the task is NOT in LOCAL_DENY_TASKS."""

    def test_refresh_docs_corpus_registered_in_beat_schedule(self):
        from celery.schedules import crontab
        from core.celery import app

        schedule = app.conf.beat_schedule
        self.assertIn('refresh-docs-corpus-daily', schedule)
        entry = schedule['refresh-docs-corpus-daily']
        self.assertEqual(entry['task'], 'core.tasks.refresh_docs_corpus')
        sched = entry['schedule']
        self.assertIsInstance(sched, crontab)
        # 4:00 AM Denver per Session 1235 P5#2 spec
        # (3h pre-morning_brief for cold-cascade headroom).
        self.assertEqual(sched.hour, {4})
        self.assertEqual(sched.minute, {0})

    def test_refresh_docs_corpus_NOT_in_local_deny_tasks(self):
        """Per Session 1235 P5#2 design (Rigby-approved): delta cost is
        sub-penny and local Rigby benefits from a fresh corpus during
        dev/test. Skipping local would lose dev/prod parity for the
        semantic_search → kb_tool path that Session 1234 D9-D16 built."""
        from core.management.commands.add_critical_celery_tasks import (
            LOCAL_DENY_TASKS,
        )
        self.assertNotIn('refresh-docs-corpus-daily', LOCAL_DENY_TASKS)
