"""Session 1235 P5#3 audit Tranche 1 PR #4 — personal_memory_stats +
delete_personal_memory ORM pivot.

Verifies the two functions in `core/views_personal_memories.py` no
longer hit the dead `unified_embeddings` substrate. Both pivoted to
the live `UserEmbedding` ORM (same model D21 PR #2631 validated for
the read-path `search_personal_memories`).

Sibling endpoint `search_personal_memories_api` is untouched — it was
already clean (delegates to `core.rag_integration.search_personal_memories`
which D21 fixed).

Per Session 1234 D16 memory rule
``feedback_test_real_db_for_queryset_semantics``: real DB throughout;
mocks only at the DRF request-construction boundary.

Run::

    python manage.py test core.tests.test_personal_memory_stats_delete_pivot -v 2 --keepdb
"""

import uuid
from unittest.mock import patch

from django.apps import apps
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

User = get_user_model()
UserEmbedding = apps.get_model('core', 'UserEmbedding')


def _make_user_embedding(owner, content='test memory', content_type='success_pattern'):
    """Create a real UserEmbedding row for the user-scoped queries."""
    return UserEmbedding.objects.create(
        user=owner,
        embedding_vector=[0.1] * 1536,
        content=content,
        content_type=content_type,
        confidence_score=0.8,
    )


class PersonalMemoryStatsORMTests(TestCase):
    """personal_memory_stats counts via UserEmbedding ORM."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username=f'test_stats_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def _call(self):
        from core.views_personal_memories import personal_memory_stats
        request = self.factory.get('/api/v1/personal-memories/stats/')
        force_authenticate(request, user=self.user)
        return personal_memory_stats(request)

    def test_returns_real_user_embedding_count(self):
        for i in range(3):
            _make_user_embedding(self.user, content=f'memory {i}')

        response = self._call()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['personal_memories_count'], 3)
        self.assertEqual(response.data['user_id'], self.user.id)

    def test_returns_zero_for_user_with_no_memories(self):
        response = self._call()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['personal_memories_count'], 0)
        # Pre-pivot returned 500 with `error: 'relation does not exist'`
        self.assertNotIn('error', response.data)

    def test_isolates_users(self):
        other = User.objects.create_user(
            username=f'other_{uuid.uuid4().hex[:8]}', password='test',
        )
        _make_user_embedding(self.user, content='mine')
        _make_user_embedding(other, content='theirs')

        response = self._call()
        # Should only count self.user's row
        self.assertEqual(response.data['personal_memories_count'], 1)

    def test_excludes_inactive_rows(self):
        active = _make_user_embedding(self.user, content='active')
        inactive = _make_user_embedding(self.user, content='inactive')
        UserEmbedding.objects.filter(id=inactive.id).update(is_active=False)

        response = self._call()
        # Pre-pivot had no is_active filter (dead table didn't have that
        # column shape); post-pivot mirrors D21's `is_active=True` filter.
        self.assertEqual(response.data['personal_memories_count'], 1)


class DeletePersonalMemoryORMTests(TestCase):
    """delete_personal_memory uses ORM with user-scoped access control."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username=f'test_del_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def _call(self, body):
        # Patch the require_personal_memory_access decorator wrapper to no-op
        # since the access controller pre-check isn't the unit under test.
        from core.views_personal_memories import delete_personal_memory
        request = self.factory.post(
            '/api/v1/personal-memories/delete/',
            data=body,
            format='json',
        )
        force_authenticate(request, user=self.user)
        return delete_personal_memory(request)

    def test_deletes_own_memory(self):
        memory = _make_user_embedding(self.user, content='will be deleted')
        memory_id = str(memory.id)

        response = self._call({'memory_id': memory_id})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['memory_id'], memory_id)
        self.assertFalse(
            UserEmbedding.objects.filter(id=memory.id).exists(),
            "Memory should be hard-deleted from DB.",
        )

    def test_rejects_missing_memory_id(self):
        response = self._call({})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Memory ID', response.data['error'])

    def test_returns_404_for_other_users_memory(self):
        """Memory exists but belongs to a different user → 404 (does
        not leak existence)."""
        other = User.objects.create_user(
            username=f'other_{uuid.uuid4().hex[:8]}', password='test',
        )
        other_memory = _make_user_embedding(other, content='not mine')

        response = self._call({'memory_id': str(other_memory.id)})

        self.assertEqual(response.status_code, 404)
        # Other user's memory must NOT be deleted.
        self.assertTrue(
            UserEmbedding.objects.filter(id=other_memory.id).exists(),
            "Cross-user delete must be blocked at queryset filter.",
        )

    def test_returns_404_for_nonexistent_memory(self):
        fake_id = str(uuid.uuid4())
        response = self._call({'memory_id': fake_id})
        self.assertEqual(response.status_code, 404)


class NoDeadSubstrateLeftInPersonalMemoriesTests(TestCase):
    """Source-level guard: views_personal_memories.py contains zero
    live cursor.execute / raw-SQL / dead-table references outside
    docstrings."""

    FILE_PATH = 'core/views_personal_memories.py'

    def _extract_function_bodies(self):
        """Extract bodies of personal_memory_stats + delete_personal_memory
        as separate strings (skips docstrings)."""
        from pathlib import Path
        import ast
        text = Path(__file__).resolve().parent.parent.parent.joinpath(
            self.FILE_PATH,
        ).read_text()
        tree = ast.parse(text)
        target_names = {'personal_memory_stats', 'delete_personal_memory'}
        bodies = {}
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.FunctionDef)
                and node.name in target_names
            ):
                body = node.body
                if (
                    body
                    and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)
                ):
                    body = body[1:]
                bodies[node.name] = '\n'.join(ast.unparse(stmt) for stmt in body)
        return bodies

    def test_no_cursor_execute_in_pivoted_function_bodies(self):
        bodies = self._extract_function_bodies()
        for name, body in bodies.items():
            self.assertNotIn(
                'cursor.execute',
                body,
                f'{name}: raw cursor.execute call remained after pivot',
            )

    def test_no_unified_embeddings_query_in_pivoted_function_bodies(self):
        bodies = self._extract_function_bodies()
        for name, body in bodies.items():
            for marker in (
                'FROM unified_embeddings',
                'DELETE FROM unified_embeddings',
                'INTO unified_embeddings',
            ):
                self.assertNotIn(
                    marker, body, f'{name} still references {marker!r}',
                )

    def test_no_connection_cursor_context_manager(self):
        """The `with connection.cursor() as cursor:` pattern was the
        dead-substrate vehicle in both pivoted functions. Verify gone."""
        bodies = self._extract_function_bodies()
        for name, body in bodies.items():
            self.assertNotIn(
                'connection.cursor()',
                body,
                f'{name} still opens a raw connection.cursor context',
            )
