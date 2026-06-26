"""Session 1235 P5#3 audit Tranche 1 PR #3 — personal_knowledge_list pivot.

Verifies that `core.views.personal_knowledge_list` no longer hits the
dead `unified_embeddings` substrate. The endpoint now returns honest
empty data while the personal-knowledge feature awaits its real
backing model (coupled with the deferred `core/views_knowledge.py`
write endpoints).

Run::

    python manage.py test core.tests.test_personal_knowledge_list_pivot -v 2 --keepdb
"""

import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

User = get_user_model()


class PersonalKnowledgeListDeprecationShapeTests(TestCase):
    """Endpoint returns the expected empty shape — no DB hit, no error key."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username=f'test_pkl_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def _call(self, query_params=None):
        from core.views import personal_knowledge_list
        request = self.factory.get(
            '/api/v1/personal-knowledge/list/',
            data=query_params or {},
        )
        force_authenticate(request, user=self.user)
        return personal_knowledge_list(request)

    def test_returns_200_empty_shape(self):
        response = self._call()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['knowledge'], [])
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(response.data['total_pages'], 0)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_stats_zeroed_no_categories(self):
        response = self._call()
        stats = response.data['stats']
        self.assertEqual(stats['total_entries'], 0)
        self.assertEqual(stats['total_words'], 0)
        self.assertEqual(stats['categories'], [])
        self.assertEqual(stats['total_embeddings'], 0)

    def test_no_error_key_in_response(self):
        """Pre-pivot returned `error: '<psycopg2 message>'` on dead-table
        query failure. Post-pivot has no DB hit and no error key — clean
        empty response."""
        response = self._call()
        self.assertNotIn('error', response.data)

    def test_page_param_echoed_in_response(self):
        response = self._call({'page': 5})
        self.assertEqual(response.data['page'], 5)

    def test_search_and_category_params_no_op_silently(self):
        """Query params accepted but produce no DB hit / no error."""
        response = self._call({
            'search': 'anything',
            'category': 'note',
            'per_page': 50,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['knowledge'], [])


class NoDeadSubstrateLeftInPersonalKnowledgeListTests(TestCase):
    """Source-level guard: the personal_knowledge_list function body
    contains zero psycopg2 calls / dead-table queries / dead-DB connect
    strings outside of explanatory docstrings.

    Checks BOTH the live source (`core/views/main.py` — what
    core/urls.py actually imports via `from core.views import ...`) AND
    the shadowed dead source (`core/views.py`) so a regression in either
    place is caught.
    """

    SOURCES = [
        'core/views/main.py',  # LIVE — package shadows the .py module
        'core/views.py',       # SHADOWED dead code, kept in sync as Session 1236 cleanup pending
    ]

    def _extract_function_body(self, rel_path):
        """Extract the personal_knowledge_list function body from the
        named source file as a single string. Skips the docstring."""
        from pathlib import Path
        import ast
        text = Path(__file__).resolve().parent.parent.parent.joinpath(
            rel_path,
        ).read_text()
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.FunctionDef)
                and node.name == 'personal_knowledge_list'
            ):
                body = node.body
                if (
                    body
                    and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)
                ):
                    body = body[1:]
                return '\n'.join(ast.unparse(stmt) for stmt in body)
        raise AssertionError(
            f'personal_knowledge_list function not found in {rel_path}'
        )

    def test_no_psycopg2_in_function_body(self):
        for rel_path in self.SOURCES:
            body = self._extract_function_body(rel_path)
            self.assertNotIn('psycopg2', body, msg=f'in {rel_path}')

    def test_no_unified_embeddings_query_in_function_body(self):
        for rel_path in self.SOURCES:
            body = self._extract_function_body(rel_path)
            for marker in ('unified_embeddings', 'FROM unified_embeddings'):
                self.assertNotIn(marker, body, msg=f'{marker!r} in {rel_path}')

    def test_no_ai_unified_platform_in_function_body(self):
        for rel_path in self.SOURCES:
            body = self._extract_function_body(rel_path)
            self.assertNotIn('ai_unified_platform', body, msg=f'in {rel_path}')

    def test_no_raw_db_connect_in_function_body(self):
        """Function body should not contain any raw `.connect(` calls or
        `.cursor()` calls — those would indicate dead-substrate code
        slipped back in."""
        for rel_path in self.SOURCES:
            body = self._extract_function_body(rel_path)
            self.assertNotIn('.connect(', body, msg=f'in {rel_path}')
            self.assertNotIn('.cursor()', body, msg=f'in {rel_path}')
