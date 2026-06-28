"""Tests for /api/db-health-rpc/ — Session 1249 P2(a) server-side PR.

Covers: token gate (404/401), action allowlist (403), payload validation
(400), and live dispatch (200) against the existing ``_handle_db_health``
handler.

Live-verify path (no prod deploy required): tests hit the endpoint via
Django's test client against the local test database, which exercises
routing + auth + dispatcher plumbing end-to-end.
"""
from __future__ import annotations

import json
import os
import unittest
from unittest import mock

import pytest
from django.test import Client


RPC_PATH = '/api/db-health-rpc/'
TEST_TOKEN = 'rpc-test-token-' + 'a' * 32


@pytest.mark.django_db
class TokenGateTests(unittest.TestCase):
    """The 404 / 401 paths — token-driven endpoint visibility + auth."""

    def setUp(self) -> None:
        self.client = Client()

    def test_endpoint_returns_404_when_token_unset(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != 'PA_DB_HEALTH_RPC_TOKEN'}
        with mock.patch.dict(os.environ, env, clear=True):
            resp = self.client.post(
                RPC_PATH,
                data=json.dumps({'action': 'overview'}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Token {TEST_TOKEN}',
            )
        self.assertEqual(resp.status_code, 404)

    def test_endpoint_returns_404_when_token_blank(self) -> None:
        with mock.patch.dict(os.environ, {'PA_DB_HEALTH_RPC_TOKEN': '   '}):
            resp = self.client.post(
                RPC_PATH,
                data=json.dumps({'action': 'overview'}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Token {TEST_TOKEN}',
            )
        self.assertEqual(resp.status_code, 404)

    def test_endpoint_returns_401_with_no_authorization_header(self) -> None:
        with mock.patch.dict(os.environ, {'PA_DB_HEALTH_RPC_TOKEN': TEST_TOKEN}):
            resp = self.client.post(
                RPC_PATH,
                data=json.dumps({'action': 'overview'}),
                content_type='application/json',
            )
        self.assertEqual(resp.status_code, 401)

    def test_endpoint_returns_401_with_wrong_token(self) -> None:
        with mock.patch.dict(os.environ, {'PA_DB_HEALTH_RPC_TOKEN': TEST_TOKEN}):
            resp = self.client.post(
                RPC_PATH,
                data=json.dumps({'action': 'overview'}),
                content_type='application/json',
                HTTP_AUTHORIZATION='Token not-the-real-token',
            )
        self.assertEqual(resp.status_code, 401)

    def test_endpoint_returns_401_with_wrong_scheme(self) -> None:
        """Bearer / Basic / etc. must not be accepted — only 'Token <hex>'."""
        with mock.patch.dict(os.environ, {'PA_DB_HEALTH_RPC_TOKEN': TEST_TOKEN}):
            resp = self.client.post(
                RPC_PATH,
                data=json.dumps({'action': 'overview'}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {TEST_TOKEN}',
            )
        self.assertEqual(resp.status_code, 401)


@pytest.mark.django_db
class PayloadValidationTests(unittest.TestCase):
    """The 400 / 403 paths — action allowlist + JSON payload sanity."""

    def setUp(self) -> None:
        self.client = Client()
        self._env_patch = mock.patch.dict(
            os.environ, {'PA_DB_HEALTH_RPC_TOKEN': TEST_TOKEN}
        )
        self._env_patch.start()
        self.auth = f'Token {TEST_TOKEN}'

    def tearDown(self) -> None:
        self._env_patch.stop()

    def test_returns_400_with_malformed_json(self) -> None:
        resp = self.client.post(
            RPC_PATH,
            data=b'{not valid json',
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth,
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn('malformed', resp.json()['error'].lower())

    def test_returns_400_when_payload_not_object(self) -> None:
        resp = self.client.post(
            RPC_PATH,
            data=json.dumps(['array', 'not', 'object']),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth,
        )
        self.assertEqual(resp.status_code, 400)

    def test_returns_400_when_action_missing(self) -> None:
        resp = self.client.post(
            RPC_PATH,
            data=json.dumps({'something_else': 'oops'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth,
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("'action'", resp.json()['error'])

    def test_returns_403_with_disallowed_action(self) -> None:
        resp = self.client.post(
            RPC_PATH,
            data=json.dumps({'action': 'drop_database'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth,
        )
        self.assertEqual(resp.status_code, 403)
        body = resp.json()
        self.assertIn('not in allowlist', body['error'])
        self.assertIn('overview', body['allowed_actions'])
        self.assertNotIn('drop_database', body['allowed_actions'])


@pytest.mark.django_db
class DispatchSuccessTests(unittest.TestCase):
    """The 200 path — real dispatch against the existing handler."""

    def setUp(self) -> None:
        self.client = Client()
        self._env_patch = mock.patch.dict(
            os.environ, {'PA_DB_HEALTH_RPC_TOKEN': TEST_TOKEN}
        )
        self._env_patch.start()
        self.auth = f'Token {TEST_TOKEN}'

    def tearDown(self) -> None:
        self._env_patch.stop()

    def test_overview_returns_200_with_dispatcher_result(self) -> None:
        resp = self.client.post(
            RPC_PATH,
            data=json.dumps({'action': 'overview'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth,
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body['ok'])
        self.assertIsNone(body['error'])
        self.assertTrue(body['trace_id'].startswith('rpc-'))
        # Existing handler always populates 'action' in its result
        self.assertEqual(body['result']['action'], 'overview')
        # 'connected' is the first key the overview handler sets
        self.assertIn('connected', body['result'])

    def test_verify_table_returns_200_for_existing_table(self) -> None:
        # django_content_type is always created by Django's contenttypes app.
        resp = self.client.post(
            RPC_PATH,
            data=json.dumps({'action': 'verify_table', 'table_name': 'django_content_type'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth,
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body['ok'])
        self.assertEqual(body['result']['action'], 'verify_table')
        self.assertEqual(body['result']['table_name'], 'django_content_type')
        self.assertTrue(body['result']['exists'])
        self.assertIn('columns', body['result'])

    def test_search_tables_returns_200(self) -> None:
        # 'django_' prefix matches built-in tables (content_type, migrations, etc.)
        resp = self.client.post(
            RPC_PATH,
            data=json.dumps({'action': 'search_tables', 'prefix': 'django_'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=self.auth,
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertTrue(body['ok'])
        self.assertEqual(body['result']['prefix'], 'django_')
        table_names = {t['name'] for t in body['result']['tables']}
        self.assertIn('django_content_type', table_names)
        self.assertIn('django_migrations', table_names)


@pytest.mark.django_db
class MethodGuardTests(unittest.TestCase):
    """GET / other methods must be rejected by require_POST."""

    def setUp(self) -> None:
        self.client = Client()

    def test_get_returns_405(self) -> None:
        with mock.patch.dict(os.environ, {'PA_DB_HEALTH_RPC_TOKEN': TEST_TOKEN}):
            resp = self.client.get(
                RPC_PATH,
                HTTP_AUTHORIZATION=f'Token {TEST_TOKEN}',
            )
        self.assertEqual(resp.status_code, 405)


if __name__ == '__main__':
    unittest.main()
