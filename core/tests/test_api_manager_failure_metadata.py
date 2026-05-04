from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from django.test import SimpleTestCase

from ai_core.spiders.api_manager import APIRequestManager


def asyncio_run(coro):
    import asyncio

    return asyncio.run(coro)


class DummyVault:
    def __init__(self, *, api_key=None, can_make_request=True, quota_exhausted=False):
        self.api_key = api_key
        self._can_make_request = can_make_request
        self.quotas = {}
        if quota_exhausted:
            self.quotas['coingecko'] = SimpleNamespace(is_exhausted=True)
        self.health = {
            'alpha_vantage': SimpleNamespace(is_healthy=True),
            'polygon': SimpleNamespace(is_healthy=True),
            'iex_cloud': SimpleNamespace(is_healthy=True),
            'finnhub': SimpleNamespace(is_healthy=True),
            'yahoo_finance': SimpleNamespace(is_healthy=True),
        }
        self.recorded_requests = []

    async def can_make_request(self, service):
        return self._can_make_request

    def get_key(self, service):
        return self.api_key

    def record_request(self, service, success=True, error=None):
        self.recorded_requests.append(
            {
                'service': service,
                'success': success,
                'error': error,
            }
        )


class APIManagerFailureMetadataTests(SimpleTestCase):
    def _make_manager(self, **vault_kwargs):
        return APIRequestManager(DummyVault(**vault_kwargs))

    def test_auth_failure_records_metadata(self):
        manager = self._make_manager(api_key=None)

        result = asyncio_run(
            manager.make_authenticated_request(
                service='newsapi',
                url='https://example.test/news',
            )
        )

        self.assertIsNone(result)
        self.assertEqual(manager.last_request_metadata['success'], False)
        self.assertEqual(manager.last_request_metadata['service'], 'newsapi')
        self.assertEqual(manager.last_request_metadata['failure_type'], 'missing_auth')
        self.assertEqual(manager.last_request_metadata['error_type'], 'MissingAuth')

    def test_http_failure_records_metadata(self):
        manager = self._make_manager(api_key=None)
        web_module = ModuleType('web_request_layer')

        async def fake_fetch(**kwargs):
            return {'status': 503, 'json': None}

        web_module.web_request_layer = SimpleNamespace(fetch=fake_fetch)

        with patch.dict('sys.modules', {'web_request_layer': web_module}):
            result = asyncio_run(
                manager.make_authenticated_request(
                    service='coingecko',
                    url='https://example.test/price',
                )
            )

        self.assertIsNone(result)
        self.assertEqual(manager.last_request_metadata['failure_type'], 'http_error')
        self.assertEqual(manager.last_request_metadata['http_status'], 503)
        self.assertEqual(manager.last_request_metadata['error_type'], 'HTTPError')

    def test_exception_records_metadata(self):
        manager = self._make_manager(api_key=None)
        web_module = ModuleType('web_request_layer')

        async def fake_fetch(**kwargs):
            raise RuntimeError('network exploded')

        web_module.web_request_layer = SimpleNamespace(fetch=fake_fetch)

        with patch.dict('sys.modules', {'web_request_layer': web_module}):
            result = asyncio_run(
                manager.make_authenticated_request(
                    service='coingecko',
                    url='https://example.test/price',
                )
            )

        self.assertIsNone(result)
        self.assertEqual(manager.last_request_metadata['failure_type'], 'exception')
        self.assertEqual(manager.last_request_metadata['error_type'], 'RuntimeError')
        self.assertEqual(manager.last_request_metadata['error'], 'network exploded')

    def test_fallback_exhaustion_records_metadata(self):
        manager = self._make_manager(api_key=None)
        manager.fallback_apis['test'] = ['service_a', 'service_b']

        async def fake_request(service, **kwargs):
            manager.last_request_metadata = {
                'success': False,
                'service': service,
                'failure_type': 'http_error',
                'error': f'{service} failed',
                'error_type': 'HTTPError',
                'http_status': 500,
                'quota_blocked': False,
                'rate_limited': False,
                'wait_seconds': 0.0,
            }
            return None

        result = asyncio_run(manager.request_with_fallback('test', fake_request))

        self.assertIsNone(result)
        self.assertEqual(manager.last_fallback_metadata['failure_type'], 'fallback_exhausted')
        self.assertTrue(manager.last_fallback_metadata['fallback_used'])
        self.assertEqual(
            manager.last_fallback_metadata['attempted_services'],
            ['service_a', 'service_b'],
        )
        self.assertEqual(len(manager.last_fallback_metadata['failed_services']), 2)
        self.assertEqual(manager.last_fallback_metadata['last_error'], 'service_b failed')

    def test_successful_request_returns_payload_and_metadata(self):
        manager = self._make_manager(api_key=None)
        web_module = ModuleType('web_request_layer')

        async def fake_fetch(**kwargs):
            return {'status': 200, 'json': {'ok': True}}

        web_module.web_request_layer = SimpleNamespace(fetch=fake_fetch)

        with patch.dict('sys.modules', {'web_request_layer': web_module}):
            result = asyncio_run(
                manager.make_authenticated_request(
                    service='coingecko',
                    url='https://example.test/price',
                )
            )

        self.assertEqual(result, {'status': 200, 'json': {'ok': True}})
        self.assertTrue(manager.last_request_metadata['success'])
        self.assertEqual(manager.last_request_metadata['http_status'], 200)

