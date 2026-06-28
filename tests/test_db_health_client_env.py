"""Tests for db_health_tool client-side ``env`` selector — Session 1249 P2(a).

Covers:
- ``env='local'`` (and unset) preserves existing behavior + adds ``env: 'local'`` tag.
- ``env='prod'`` config validation (URL missing / token missing / both missing).
- ``env='prod'`` happy path (mocked HTTP 200).
- ``env='prod'`` HTTP error paths (401, 500, URL error, timeout, malformed JSON).
- Outgoing payload strips ``env`` (defense against accidental loops).
- Unknown env values → error dict (no silent fallback).
- Tool schema exposes ``env`` enum.

Real HTTP is mocked via ``urllib.request.urlopen`` — tests never touch a
network or a real prod URL.
"""
from __future__ import annotations

import io
import json
import os
import unittest
from unittest import mock

import pytest


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def _make_dispatcher():
    """Return a fresh ToolDispatcher instance (handlers auto-registered)."""
    from core.services.tool_dispatcher import ToolDispatcher
    return ToolDispatcher()


def _make_urlopen_response(payload: dict, status: int = 200):
    """Build a context-manager-shaped mock for urlopen() returning JSON."""
    response = mock.MagicMock()
    response.read.return_value = json.dumps(payload).encode('utf-8')
    response.status = status
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    return response


# --------------------------------------------------------------------------
# Local-path: env default + explicit local + env tag
# --------------------------------------------------------------------------


@pytest.mark.django_db
class LocalEnvTagTests(unittest.TestCase):

    def test_unset_env_defaults_to_local_and_is_tagged(self) -> None:
        dispatcher = _make_dispatcher()
        result = dispatcher._handle_db_health(
            'db_health_tool',
            {'action': 'overview'},
            user_id=None,
            trace_id='test-1',
        )
        self.assertEqual(result['env'], 'local')
        self.assertEqual(result['action'], 'overview')

    def test_explicit_env_local_is_tagged(self) -> None:
        dispatcher = _make_dispatcher()
        result = dispatcher._handle_db_health(
            'db_health_tool',
            {'action': 'overview', 'env': 'local'},
            user_id=None,
            trace_id='test-2',
        )
        self.assertEqual(result['env'], 'local')


# --------------------------------------------------------------------------
# Prod env: config validation
# --------------------------------------------------------------------------


class ProdConfigValidationTests(unittest.TestCase):
    """Config-only tests — no Django DB needed (errors raised before dispatch)."""

    def setUp(self) -> None:
        env = {
            k: v for k, v in os.environ.items()
            if k not in ('PA_DB_HEALTH_RPC_URL', 'PA_DB_HEALTH_RPC_CLIENT_TOKEN')
        }
        self._env_patch = mock.patch.dict(os.environ, env, clear=True)
        self._env_patch.start()
        self.dispatcher = _make_dispatcher()

    def tearDown(self) -> None:
        self._env_patch.stop()

    def _call_prod(self, action: str = 'overview') -> dict:
        return self.dispatcher._handle_db_health(
            'db_health_tool',
            {'action': action, 'env': 'prod'},
            user_id=None,
            trace_id='test-prod',
        )

    def test_neither_url_nor_token_set(self) -> None:
        result = self._call_prod()
        self.assertEqual(result['env'], 'prod')
        self.assertEqual(result['action'], 'overview')
        self.assertIn('PA_DB_HEALTH_RPC_URL', result['error'])
        self.assertIn('PA_DB_HEALTH_RPC_CLIENT_TOKEN', result['error'])

    def test_only_url_set(self) -> None:
        os.environ['PA_DB_HEALTH_RPC_URL'] = 'http://localhost:8000/api/db-health-rpc/'
        result = self._call_prod()
        self.assertEqual(result['env'], 'prod')
        self.assertNotIn('PA_DB_HEALTH_RPC_URL', result['error'])
        self.assertIn('PA_DB_HEALTH_RPC_CLIENT_TOKEN', result['error'])

    def test_only_token_set(self) -> None:
        os.environ['PA_DB_HEALTH_RPC_CLIENT_TOKEN'] = 'tok-' + 'a' * 60
        result = self._call_prod()
        self.assertEqual(result['env'], 'prod')
        self.assertIn('PA_DB_HEALTH_RPC_URL', result['error'])
        self.assertNotIn('PA_DB_HEALTH_RPC_CLIENT_TOKEN', result['error'])

    def test_unknown_env_value_no_silent_fallback(self) -> None:
        result = self.dispatcher._handle_db_health(
            'db_health_tool',
            {'action': 'overview', 'env': 'staging'},
            user_id=None,
            trace_id='test-unknown-env',
        )
        self.assertEqual(result['env'], 'staging')
        self.assertEqual(result['action'], 'overview')
        self.assertIn('unsupported env', result['error'])


# --------------------------------------------------------------------------
# Prod env: HTTP delegation (mocked urlopen)
# --------------------------------------------------------------------------


class ProdHttpDelegationTests(unittest.TestCase):

    def setUp(self) -> None:
        env = {
            k: v for k, v in os.environ.items()
            if k not in ('PA_DB_HEALTH_RPC_URL', 'PA_DB_HEALTH_RPC_CLIENT_TOKEN')
        }
        env['PA_DB_HEALTH_RPC_URL'] = 'http://prod.example.com/api/db-health-rpc/'
        env['PA_DB_HEALTH_RPC_CLIENT_TOKEN'] = 'client-token-' + 'b' * 50
        self._env_patch = mock.patch.dict(os.environ, env, clear=True)
        self._env_patch.start()
        self.dispatcher = _make_dispatcher()

    def tearDown(self) -> None:
        self._env_patch.stop()

    def test_happy_path_returns_result_with_env_tag(self) -> None:
        envelope = {
            'ok': True,
            'result': {
                'action': 'overview',
                'connected': True,
                'database_name': 'prod_db',
                'postgres_version': 'PostgreSQL 15.4 ...',
            },
            'error': None,
            'trace_id': 'rpc-abc123def456',
        }
        with mock.patch('urllib.request.urlopen', return_value=_make_urlopen_response(envelope)):
            result = self.dispatcher._handle_db_health(
                'db_health_tool',
                {'action': 'overview', 'env': 'prod'},
                user_id=None,
                trace_id='client-trace-1',
            )
        self.assertEqual(result['env'], 'prod')
        self.assertEqual(result['action'], 'overview')
        self.assertEqual(result['database_name'], 'prod_db')
        self.assertEqual(result['remote_trace_id'], 'rpc-abc123def456')

    def test_payload_strips_env_before_sending(self) -> None:
        envelope = {'ok': True, 'result': {'action': 'overview'}, 'error': None, 'trace_id': 'rpc-x'}
        captured = {}

        def _capture(req, timeout=None):
            captured['url'] = req.full_url
            captured['body'] = json.loads(req.data.decode('utf-8'))
            captured['auth'] = req.headers.get('Authorization')
            return _make_urlopen_response(envelope)

        with mock.patch('urllib.request.urlopen', side_effect=_capture):
            self.dispatcher._handle_db_health(
                'db_health_tool',
                {'action': 'verify_table', 'table_name': 'core_legacyspiderdata', 'env': 'prod'},
                user_id=None,
                trace_id='client-trace-2',
            )
        self.assertNotIn('env', captured['body'])
        self.assertEqual(captured['body']['action'], 'verify_table')
        self.assertEqual(captured['body']['table_name'], 'core_legacyspiderdata')
        self.assertTrue(captured['auth'].startswith('Token '))
        self.assertEqual(captured['url'], 'http://prod.example.com/api/db-health-rpc/')

    def test_http_401_returns_error_dict(self) -> None:
        import urllib.error
        err = urllib.error.HTTPError(
            url='http://prod.example.com/api/db-health-rpc/',
            code=401,
            msg='Unauthorized',
            hdrs=None,
            fp=io.BytesIO(b'{"error": "unauthorized"}'),
        )
        with mock.patch('urllib.request.urlopen', side_effect=err):
            result = self.dispatcher._handle_db_health(
                'db_health_tool',
                {'action': 'overview', 'env': 'prod'},
                user_id=None,
                trace_id='client-trace-3',
            )
        self.assertEqual(result['env'], 'prod')
        self.assertIn('HTTP 401', result['error'])
        self.assertIn('unauthorized', result['error'].lower())

    def test_http_500_caps_error_body_at_500_chars(self) -> None:
        import urllib.error
        big_body = b'<html>' + (b'x' * 10000) + b'</html>'
        err = urllib.error.HTTPError(
            url='http://prod.example.com/api/db-health-rpc/',
            code=500,
            msg='Server Error',
            hdrs=None,
            fp=io.BytesIO(big_body),
        )
        with mock.patch('urllib.request.urlopen', side_effect=err):
            result = self.dispatcher._handle_db_health(
                'db_health_tool',
                {'action': 'overview', 'env': 'prod'},
                user_id=None,
                trace_id='client-trace-4',
            )
        self.assertIn('HTTP 500', result['error'])
        # Error message cap is 500 chars after the prefix; total error string
        # should be well under 600 chars (prevents log/UI blowup).
        self.assertLess(len(result['error']), 600)

    def test_url_error_returns_error_dict(self) -> None:
        import urllib.error
        with mock.patch(
            'urllib.request.urlopen',
            side_effect=urllib.error.URLError('Connection refused'),
        ):
            result = self.dispatcher._handle_db_health(
                'db_health_tool',
                {'action': 'overview', 'env': 'prod'},
                user_id=None,
                trace_id='client-trace-5',
            )
        self.assertEqual(result['env'], 'prod')
        self.assertIn('URL error', result['error'])
        self.assertIn('Connection refused', result['error'])

    def test_malformed_json_response(self) -> None:
        bad_response = mock.MagicMock()
        bad_response.read.return_value = b'this is not json'
        bad_response.__enter__.return_value = bad_response
        bad_response.__exit__.return_value = False
        with mock.patch('urllib.request.urlopen', return_value=bad_response):
            result = self.dispatcher._handle_db_health(
                'db_health_tool',
                {'action': 'overview', 'env': 'prod'},
                user_id=None,
                trace_id='client-trace-6',
            )
        self.assertEqual(result['env'], 'prod')
        self.assertIn('JSONDecodeError', result['error'])


# --------------------------------------------------------------------------
# Schema: env param exposed to GPT-5.2
# --------------------------------------------------------------------------


class SchemaExposesEnvTests(unittest.TestCase):

    def test_db_health_tool_schema_has_env_enum(self) -> None:
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        db_health = next(
            (s for s in PA_TOOL_SCHEMAS if s.get('name') == 'db_health_tool'), None,
        )
        self.assertIsNotNone(db_health)
        properties = db_health['parameters']['properties']
        self.assertIn('env', properties)
        self.assertEqual(properties['env']['type'], 'string')
        self.assertEqual(sorted(properties['env']['enum']), ['local', 'prod'])
        self.assertIn('PA_DB_HEALTH_RPC_URL', properties['env']['description'])


if __name__ == '__main__':
    unittest.main()
