"""
PA Context Endpoint + Rebuild Task — Regression Tests
======================================================

Session 1078: Validates the stale-first async rebuild pattern.

Endpoint contract:
  - Fresh hit → return cached context
  - Fresh miss + stale exists → return stale, enqueue Celery rebuild
  - Both miss (cold start) → return skeleton, enqueue rebuild
  - force_rebuild=1 bypasses fresh cache (staff only)

Celery task contract:
  - Writes both fresh + stale cache keys
  - Stampede lock prevents concurrent rebuilds
  - Exceptions don't wipe stale cache

Run: python manage.py test core.tests.test_pa_context -v2
"""

from unittest.mock import patch, MagicMock
from django.test import TransactionTestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()


class PAContextEndpointTests(TransactionTestCase):
    """Tests for get_assistant_context view."""

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='pa_ctx_test',
            password='testpass',
            is_staff=True,
        )

        # Clear all pa_ctx keys before each test
        import hashlib
        self.user_hash = hashlib.md5(str(self.user.id).encode()).hexdigest()
        self.fresh_key = f"pa_ctx:fresh:{self.user_hash}"
        self.stale_key = f"pa_ctx:stale:{self.user_hash}"
        cache.delete(self.fresh_key)
        cache.delete(self.stale_key)

    def _get(self, query_params=None):
        """Helper to call the endpoint."""
        from core.views_personal_assistant import get_assistant_context
        url = '/api/assistant/context/'
        if query_params:
            url += '?' + '&'.join(f'{k}={v}' for k, v in query_params.items())
        request = self.factory.get(url, query_params or {})
        request.user = self.user
        return get_assistant_context(request)

    @patch('core.tasks.rebuild_pa_context_task.delay')
    def test_cold_start_returns_skeleton(self, mock_delay):
        """Both caches empty → returns skeleton immediately, enqueues rebuild."""
        response = self._get()
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertTrue(data['success'])
        ctx = data['context']
        self.assertTrue(ctx.get('_skeleton'), "Cold start should return skeleton context")
        self.assertEqual(ctx['username'], self.user.username)
        mock_delay.assert_called_once()
        # Reason should be cold_start
        args, kwargs = mock_delay.call_args
        self.assertEqual(args[1] if len(args) > 1 else kwargs.get('reason'), 'cold_start')

    @patch('core.tasks.rebuild_pa_context_task.delay')
    def test_stale_served_on_fresh_miss(self, mock_delay):
        """Fresh miss + stale exists → returns stale, enqueues rebuild."""
        stale_ctx = {'user_id': str(self.user.id), 'stale': True, 'test': 'stale_data'}
        cache.set(self.stale_key, stale_ctx, 60)

        response = self._get()
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertTrue(data['success'])
        self.assertEqual(data['context']['test'], 'stale_data')
        mock_delay.assert_called_once()
        args, kwargs = mock_delay.call_args
        self.assertEqual(args[1] if len(args) > 1 else kwargs.get('reason'), 'fresh_miss')

    @patch('core.tasks.rebuild_pa_context_task.delay')
    def test_fresh_hit_no_rebuild(self, mock_delay):
        """Fresh cache hit → returns immediately, no rebuild enqueued."""
        fresh_ctx = {'user_id': str(self.user.id), 'fresh': True}
        cache.set(self.fresh_key, fresh_ctx, 60)

        response = self._get()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['context']['fresh'], True)
        mock_delay.assert_not_called()

    @patch('core.tasks.rebuild_pa_context_task.delay')
    def test_force_rebuild_bypasses_fresh(self, mock_delay):
        """Staff force_rebuild=1 skips fresh cache, serves stale, enqueues rebuild."""
        fresh_ctx = {'user_id': str(self.user.id), 'fresh': True}
        stale_ctx = {'user_id': str(self.user.id), 'stale': True}
        cache.set(self.fresh_key, fresh_ctx, 60)
        cache.set(self.stale_key, stale_ctx, 60)

        response = self._get({'force_rebuild': '1'})
        self.assertEqual(response.status_code, 200)
        # Should serve stale (bypassed fresh)
        self.assertTrue(response.data['context'].get('stale'))
        mock_delay.assert_called_once()

    @patch('core.tasks.rebuild_pa_context_task.delay')
    def test_force_rebuild_non_staff_ignored(self, mock_delay):
        """Non-staff force_rebuild=1 is ignored — fresh cache returned."""
        self.user.is_staff = False
        self.user.save()
        try:
            fresh_ctx = {'user_id': str(self.user.id), 'fresh': True}
            cache.set(self.fresh_key, fresh_ctx, 60)

            response = self._get({'force_rebuild': '1'})
            self.assertEqual(response.status_code, 200)
            # Fresh cache should be returned (force_rebuild ignored for non-staff)
            self.assertTrue(response.data['context'].get('fresh'))
            mock_delay.assert_not_called()
        finally:
            self.user.is_staff = True
            self.user.save()

    @patch('core.tasks.rebuild_pa_context_task.delay')
    def test_debug_includes_timing(self, mock_delay):
        """Staff debug=1 includes _debug field in response."""
        response = self._get({'debug': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('_debug', response.data)
        debug = response.data['_debug']
        self.assertIn('cache', debug)
        self.assertIn('total_ms', debug)


class PAContextRebuildTaskTests(TransactionTestCase):
    """Tests for rebuild_pa_context_task Celery task."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='pa_rebuild_test',
            password='testpass',
        )
        import hashlib
        self.user_hash = hashlib.md5(str(self.user.id).encode()).hexdigest()
        self.fresh_key = f"pa_ctx:fresh:{self.user_hash}"
        self.stale_key = f"pa_ctx:stale:{self.user_hash}"
        self.lock_key = f"pa_ctx:rebuild_lock:{self.user_hash}"
        cache.delete(self.fresh_key)
        cache.delete(self.stale_key)
        cache.delete(self.lock_key)

    @patch('core.agent_context_middleware.AgentContextMiddleware')
    def test_writes_both_cache_keys(self, MockMiddleware):
        """Task writes both fresh and stale cache keys on success."""
        mock_instance = MagicMock()
        mock_instance.get_user_context.return_value = {'test': 'context', 'user_id': str(self.user.id)}
        MockMiddleware.return_value = mock_instance

        from core.tasks import rebuild_pa_context_task
        result = rebuild_pa_context_task(self.user.id, reason='test')

        self.assertTrue(result['success'])
        self.assertIsNotNone(cache.get(self.fresh_key))
        self.assertIsNotNone(cache.get(self.stale_key))
        self.assertEqual(cache.get(self.fresh_key)['test'], 'context')
        self.assertTrue(result.get('cache_write_ok'))

    @patch('core.agent_context_middleware.AgentContextMiddleware')
    def test_lock_prevents_stampede(self, MockMiddleware):
        """Second rebuild is suppressed while lock is held."""
        mock_instance = MagicMock()
        mock_instance.get_user_context.return_value = {'test': 'context'}
        MockMiddleware.return_value = mock_instance

        # Simulate an existing lock
        cache.set(self.lock_key, '1', timeout=90)

        from core.tasks import rebuild_pa_context_task
        result = rebuild_pa_context_task(self.user.id, reason='test_stampede')

        self.assertTrue(result.get('skipped'))
        self.assertEqual(result.get('reason'), 'lock_held')
        # Middleware should never have been instantiated
        MockMiddleware.assert_not_called()

    @patch('core.agent_context_middleware.AgentContextMiddleware')
    def test_exception_preserves_stale(self, MockMiddleware):
        """On exception, stale cache is not wiped."""
        stale_ctx = {'preserved': True}
        cache.set(self.stale_key, stale_ctx, 600)

        mock_instance = MagicMock()
        mock_instance.get_user_context.side_effect = RuntimeError("boom")
        MockMiddleware.return_value = mock_instance

        from core.tasks import rebuild_pa_context_task
        result = rebuild_pa_context_task(self.user.id, reason='test_error')

        self.assertFalse(result.get('success'))
        # Stale should still be there
        self.assertEqual(cache.get(self.stale_key), stale_ctx)

    @patch('core.agent_context_middleware.AgentContextMiddleware')
    def test_lock_released_after_exception(self, MockMiddleware):
        """Lock is released even on failure (finally block)."""
        mock_instance = MagicMock()
        mock_instance.get_user_context.side_effect = RuntimeError("boom")
        MockMiddleware.return_value = mock_instance

        from core.tasks import rebuild_pa_context_task
        rebuild_pa_context_task(self.user.id, reason='test_cleanup')

        # Lock should be cleared
        self.assertIsNone(cache.get(self.lock_key))

    @patch('core.agent_context_middleware.AgentContextMiddleware')
    def test_returns_metrics(self, MockMiddleware):
        """Successful rebuild returns build_ms and rss_delta_mb."""
        mock_instance = MagicMock()
        mock_instance.get_user_context.return_value = {'test': True}
        MockMiddleware.return_value = mock_instance

        from core.tasks import rebuild_pa_context_task
        result = rebuild_pa_context_task(self.user.id, reason='test_metrics')

        self.assertTrue(result['success'])
        self.assertIn('build_ms', result)
        self.assertIsInstance(result['build_ms'], int)
