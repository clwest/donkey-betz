"""Session 1235 P5#3 audit Tranche 1 PR #1 — dashboard dead-substrate pivot.

Verifies that the three dashboard views pivoted away from the dead
`unified_embeddings` / `ai_unified_platform` substrate to live
`DocumentEmbedding` ORM queries. Per Session 1234 D16 memory rule
`feedback_test_real_db_for_queryset_semantics`: real DB throughout;
mocks only at the request-construction boundary.

Three test classes:

1. ``DashboardStatsORMTests`` — `dashboard_stats` view reads real
   DocumentEmbedding count, not the hardcoded 67922 fallback.
2. ``EmbeddingsStatsORMTests`` — `embeddings_stats` view reports real
   counts, not the hardcoded 265174 demo data.
3. ``RealTimeMonitorORMTests`` — `RealTimeMonitor.get_real_time_stats`
   pulls embedding metrics via ORM, not psycopg2 to dead DB.

Plus a source-level guard (`NoDeadSubstrateReferencesTests`) that the
three changed files contain zero `psycopg2.connect` calls or
`unified_embeddings`/`ai_unified_platform` outside of explanatory
comments.

Run::

    python manage.py test dashboard.tests.test_dead_substrate_pivot -v 2 --keepdb
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate

from content.models import Document, DocumentEmbedding, EmbeddingModel

User = get_user_model()


def _make_doc_with_embedding(owner, title='Test', doc_type='markdown'):
    """Create a real Document + DocumentEmbedding pair for ORM count tests."""
    doc = Document.objects.create(
        title=title,
        document_type=doc_type,
        raw_content='content',
        owner=owner,
    )
    DocumentEmbedding.objects.create(
        document=doc,
        embedding_model=EmbeddingModel.OPENAI_SMALL,
        chunk_index=0,
        chunk_text='chunk',
        chunk_size=5,
        embedding_dimension=1536,
    )
    return doc


class DashboardStatsORMTests(TestCase):
    """`dashboard_stats` reads from DocumentEmbedding, not the 67922 fallback."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username=f'test_dash_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def test_returns_real_documentembedding_count(self):
        from dashboard.views import dashboard_stats

        # 5 real DocumentEmbedding rows
        for i in range(5):
            _make_doc_with_embedding(self.user, title=f'Doc {i}')

        request = self.factory.get('/api/dashboard/stats/')
        force_authenticate(request, user=self.user)
        response = dashboard_stats(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_embeddings'], 5)
        self.assertEqual(response.data['total_content'], 5)
        # Pre-pivot would have returned 67922 fallback or 0 from exception
        self.assertNotEqual(response.data['total_embeddings'], 67922)

    def test_returns_zero_when_no_embeddings(self):
        from dashboard.views import dashboard_stats

        request = self.factory.get('/api/dashboard/stats/')
        force_authenticate(request, user=self.user)
        response = dashboard_stats(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_embeddings'], 0)

    def test_today_count_reflects_freshly_created_embeddings(self):
        from dashboard.views import dashboard_stats

        _make_doc_with_embedding(self.user, title='Today doc')

        request = self.factory.get('/api/dashboard/stats/')
        force_authenticate(request, user=self.user)
        response = dashboard_stats(request)

        # learning_today field should reflect today's creation
        self.assertEqual(response.data['learning_today'], 1)
        self.assertEqual(response.data['total_content_trend'], '+1')


class EmbeddingsStatsORMTests(TestCase):
    """`embeddings_stats` reports real ORM counts, no hardcoded 265174."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username=f'test_emb_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def test_total_embeddings_from_orm(self):
        from dashboard.views import embeddings_stats

        for i in range(3):
            _make_doc_with_embedding(self.user, title=f'Doc {i}')

        request = self.factory.get('/api/dashboard/embeddings/stats/')
        force_authenticate(request, user=self.user)
        response = embeddings_stats(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['total_embeddings'], 3)
        # Pre-pivot: hardcoded 265174 demo data
        self.assertNotEqual(response.data['total_embeddings'], 265174)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('DocumentEmbedding', response.data.get('message', ''))

    def test_by_type_breakdown_matches_document_types(self):
        from dashboard.views import embeddings_stats

        _make_doc_with_embedding(self.user, title='MD doc', doc_type='markdown')
        _make_doc_with_embedding(self.user, title='Text doc', doc_type='text')
        _make_doc_with_embedding(self.user, title='MD doc 2', doc_type='markdown')

        request = self.factory.get('/api/dashboard/embeddings/stats/')
        force_authenticate(request, user=self.user)
        response = embeddings_stats(request)

        by_type = response.data['by_type']
        self.assertEqual(by_type.get('markdown'), 2)
        self.assertEqual(by_type.get('text'), 1)

    def test_zero_embeddings_returns_clean_zero_not_demo_data(self):
        from dashboard.views import embeddings_stats

        request = self.factory.get('/api/dashboard/embeddings/stats/')
        force_authenticate(request, user=self.user)
        response = embeddings_stats(request)

        # Critical: pre-pivot, empty result + dead table → status='demo_mode'
        # with 265174 fake number. Post-pivot must report 0 honestly.
        self.assertEqual(response.data['total_embeddings'], 0)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertNotEqual(response.data['total_embeddings'], 265174)


class RealTimeMonitorORMTests(TestCase):
    """`RealTimeMonitor.get_real_time_stats` uses DocumentEmbedding ORM."""

    def setUp(self):
        self.user = User.objects.create_user(
            username=f'test_rtm_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def test_embeddings_today_and_total_from_orm(self):
        from dashboard.real_time_monitor import RealTimeMonitor

        for i in range(2):
            _make_doc_with_embedding(self.user, title=f'Doc {i}')

        monitor = RealTimeMonitor()
        stats = monitor.get_real_time_stats()

        self.assertEqual(stats['embeddings_today'], 2)
        self.assertEqual(stats['total_knowledge_base'], 2)
        # Pre-pivot, dead DB connection failed silently → `error` key set
        # and embedding fields missing from stats.
        self.assertNotIn('error', stats)
        self.assertTrue(stats['monitoring_active'])

    def test_zero_when_no_embeddings(self):
        from dashboard.real_time_monitor import RealTimeMonitor

        monitor = RealTimeMonitor()
        stats = monitor.get_real_time_stats()

        self.assertEqual(stats['embeddings_today'], 0)
        self.assertEqual(stats['total_knowledge_base'], 0)
        self.assertNotIn('error', stats)


class NoDeadSubstrateReferencesTests(TestCase):
    """Source-level guard: changed files contain zero live psycopg2.connect
    calls or unified_embeddings/ai_unified_platform queries (comments OK)."""

    CHANGED_FILES = [
        'dashboard/views.py',
        'dashboard/real_time_monitor.py',
    ]

    def _read_non_comment_lines(self, path):
        """Read file, strip comment lines + docstring blocks, return remainder."""
        from pathlib import Path
        text = Path(path).read_text()
        out_lines = []
        in_docstring = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                # Crude docstring toggle. Multi-line docstrings dominate
                # this codebase; single-line """foo""" toggles twice on
                # one line and stays out.
                if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                    continue  # single-line docstring, skip whole line
                in_docstring = not in_docstring
                continue
            if in_docstring:
                continue
            if stripped.startswith('#'):
                continue
            out_lines.append(line)
        return '\n'.join(out_lines)

    def test_no_psycopg2_connect_in_changed_files(self):
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent.parent
        for rel_path in self.CHANGED_FILES:
            code = self._read_non_comment_lines(base / rel_path)
            self.assertNotIn(
                'psycopg2.connect',
                code,
                f"{rel_path} still has a psycopg2.connect call outside "
                f"comments — dead-substrate pivot incomplete.",
            )

    def test_no_unified_embeddings_query_in_changed_files(self):
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent.parent
        for rel_path in self.CHANGED_FILES:
            code = self._read_non_comment_lines(base / rel_path)
            # Match SQL-style references: FROM unified_embeddings,
            # INTO unified_embeddings, etc. Avoid catching the model
            # name 'DocumentEmbedding' (different identifier).
            for marker in ('FROM unified_embeddings', 'INTO unified_embeddings',
                           'DELETE FROM unified_embeddings'):
                self.assertNotIn(
                    marker,
                    code,
                    f"{rel_path} still queries dead table: {marker!r}",
                )

    def test_no_ai_unified_platform_connect_in_changed_files(self):
        from pathlib import Path
        base = Path(__file__).resolve().parent.parent.parent
        for rel_path in self.CHANGED_FILES:
            code = self._read_non_comment_lines(base / rel_path)
            self.assertNotIn(
                "database='ai_unified_platform'",
                code,
                f"{rel_path} still connects to dead DB ai_unified_platform.",
            )
