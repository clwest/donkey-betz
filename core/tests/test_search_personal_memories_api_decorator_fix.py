"""Session 1237 P2.a — search_personal_memories_api decorator-kwarg fix.

Verifies the latent decorator-kwarg bug Session 1235 PR #2639 caught
in two sibling functions (personal_memory_stats, delete_personal_memory)
is now also fixed in search_personal_memories_api.

Bug: `@require_personal_memory_access` decorator injects
`user_id=request.user.id` as a kwarg to the wrapped view. Pre-fix the
view signature was `def view(request):` → DRF dispatch raised
`TypeError: unexpected keyword argument 'user_id'`. Fix: `**kwargs`
absorption.

Per `feedback_test_real_db_for_queryset_semantics`: real DB; mocks
only at the `search_personal_memories` boundary (so we exercise the
DRF→decorator→view kwarg-passing path without setting up an
embedding pipeline).

Run::

    python manage.py test core.tests.test_search_personal_memories_api_decorator_fix -v 2 --keepdb
"""

import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

User = get_user_model()


class SearchPersonalMemoriesApiDecoratorFixTests(TestCase):
    """Endpoint dispatches cleanly through the
    `@require_personal_memory_access` decorator chain."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(
            username=f'test_spm_{uuid.uuid4().hex[:8]}',
            password='test',
        )

    def _call(self, body):
        from core.views_personal_memories import search_personal_memories_api
        request = self.factory.post(
            '/api/v1/personal-memories/search/',
            data=body,
            format='json',
        )
        force_authenticate(request, user=self.user)
        return search_personal_memories_api(request)

    def test_dispatch_does_not_raise_typeerror_on_decorator_kwarg(self):
        """Pre-fix this raised TypeError: unexpected keyword argument
        'user_id'. Post-fix the **kwargs absorbs the passthrough and
        the view executes."""
        with patch(
            'core.views_personal_memories.search_personal_memories',
            return_value=[],
        ):
            response = self._call({'query': 'test'})
        # If TypeError fires, response is never assigned. Any non-raise
        # outcome confirms the fix landed.
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

    def test_returns_empty_results_when_search_returns_empty(self):
        with patch(
            'core.views_personal_memories.search_personal_memories',
            return_value=[],
        ):
            response = self._call({'query': 'nothing'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], [])
        self.assertEqual(response.data['total_found'], 0)
        self.assertEqual(response.data['user_id'], self.user.id)

    def test_returns_400_when_query_missing(self):
        response = self._call({})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Query is required', response.data['error'])

    def test_user_id_in_response_matches_authenticated_user(self):
        """View reads request.user.id directly — confirm it's NOT
        using a stale or wrong user_id from the decorator passthrough."""
        with patch(
            'core.views_personal_memories.search_personal_memories',
            return_value=[],
        ):
            response = self._call({'query': 'test'})
        self.assertEqual(response.data['user_id'], self.user.id)


class AllPersonalMemoriesViewsAcceptDecoratorKwargTests(TestCase):
    """All three views in core/views_personal_memories.py must accept
    **kwargs to absorb the decorator's user_id passthrough — guard
    that none regress to bare `def view(request):` signatures."""

    def test_all_views_accept_kwargs(self):
        import inspect
        from core.views_personal_memories import (
            search_personal_memories_api,
            personal_memory_stats,
            delete_personal_memory,
        )

        # Unwrap DRF decorators to get to the underlying function
        for fn in (
            search_personal_memories_api,
            personal_memory_stats,
            delete_personal_memory,
        ):
            underlying = fn
            while hasattr(underlying, '__wrapped__'):
                underlying = underlying.__wrapped__

            sig = inspect.signature(underlying)
            has_var_keyword = any(
                p.kind == inspect.Parameter.VAR_KEYWORD
                for p in sig.parameters.values()
            )
            self.assertTrue(
                has_var_keyword,
                f"{underlying.__name__} signature {sig} must accept "
                f"**kwargs to absorb the "
                f"@require_personal_memory_access decorator's user_id "
                f"passthrough. Pre-fix raised "
                f"TypeError: unexpected keyword argument 'user_id'.",
            )
