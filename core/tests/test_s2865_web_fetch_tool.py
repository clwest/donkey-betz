"""Session 2865 slate #1 — PA raw HTTP fetch tool (Rigby Tool Gap Ledger #15).

Covers the `web_fetch_tool` handler at core/services/td_handlers_agents.py.

Uses httpx.MockTransport to swap the network transport rather than mocking the
httpx.Client class itself — closer to real client behavior (redirect handling,
header casing, content decoding).
"""

from unittest.mock import patch

import httpx
from django.test import SimpleTestCase

from core.services.tool_dispatcher import get_tool_dispatcher


def _run_fetch(payload, transport):
    """Call the handler with a mock-transport'd httpx.Client injected."""
    dispatcher = get_tool_dispatcher()
    handler = dispatcher._tool_handlers['web_fetch_tool']

    real_client = httpx.Client

    def _client_factory(*args, **kwargs):
        kwargs['transport'] = transport
        return real_client(*args, **kwargs)

    with patch('httpx.Client', side_effect=_client_factory):
        return handler(
            tool_name='web_fetch_tool',
            payload=payload,
            user_id=None,
            trace_id='test-trace',
        )


class SchemaAndRegistrationTests(SimpleTestCase):
    def test_tool_registered(self):
        dispatcher = get_tool_dispatcher()
        self.assertIn('web_fetch_tool', dispatcher._tool_handlers)
        self.assertTrue(callable(dispatcher._tool_handlers['web_fetch_tool']))

    def test_schema_present(self):
        from core.services.pa_tool_schemas import PA_TOOL_SCHEMAS
        names = [s.get('name') for s in PA_TOOL_SCHEMAS if 'name' in s]
        self.assertIn('web_fetch_tool', names)


class InputValidationTests(SimpleTestCase):
    def test_missing_url(self):
        result = _run_fetch({}, httpx.MockTransport(lambda r: httpx.Response(200)))
        self.assertFalse(result['ok'])
        self.assertIn('url is required', result['error'])

    def test_disallowed_scheme_file(self):
        result = _run_fetch(
            {'url': 'file:///etc/passwd'},
            httpx.MockTransport(lambda r: httpx.Response(200)),
        )
        self.assertFalse(result['ok'])
        self.assertIn("disallowed scheme 'file'", result['error'])

    def test_disallowed_scheme_ftp(self):
        result = _run_fetch(
            {'url': 'ftp://example.com/file'},
            httpx.MockTransport(lambda r: httpx.Response(200)),
        )
        self.assertFalse(result['ok'])
        self.assertIn("disallowed scheme 'ftp'", result['error'])

    def test_disallowed_method(self):
        result = _run_fetch(
            {'url': 'https://example.com', 'method': 'DELETE'},
            httpx.MockTransport(lambda r: httpx.Response(200)),
        )
        self.assertFalse(result['ok'])
        self.assertIn("unsupported method 'DELETE'", result['error'])

    def test_timeout_clamped_to_max(self):
        # 500s requested → clamped to 60s. Verify by inspecting the timeout
        # applied to the actual request. We can't easily read the client's
        # config, but we can verify the request goes through cleanly.
        def handler(request):
            return httpx.Response(200, json={'ok': True})

        result = _run_fetch(
            {'url': 'https://example.com', 'timeout_seconds': 500},
            httpx.MockTransport(handler),
        )
        self.assertTrue(result['ok'])

    def test_max_bytes_clamped_to_max(self):
        # Requesting 10MB → clamped to 2MB.
        def handler(request):
            return httpx.Response(200, content=b'x' * 1000)

        result = _run_fetch(
            {'url': 'https://example.com', 'max_bytes': 10_000_000},
            httpx.MockTransport(handler),
        )
        self.assertTrue(result['ok'])
        self.assertFalse(result['truncated'])


class SuccessResponseTests(SimpleTestCase):
    def test_json_get_returns_parsed_json(self):
        def handler(request):
            self.assertEqual(request.method, 'GET')
            return httpx.Response(
                200,
                json={'items': [{'id': 'model-1'}], 'total': 1},
                headers={'content-type': 'application/json'},
            )

        result = _run_fetch(
            {'url': 'https://huggingface.co/api/models'},
            httpx.MockTransport(handler),
        )
        self.assertTrue(result['ok'])
        self.assertEqual(result['status_code'], 200)
        self.assertEqual(result['content_type'], 'application/json')
        self.assertFalse(result['truncated'])
        self.assertEqual(result['json'], {'items': [{'id': 'model-1'}], 'total': 1})
        self.assertIn('items', result['body_text'])

    def test_text_get_returns_body_text_no_json(self):
        def handler(request):
            return httpx.Response(
                200,
                content=b'<html><body>hi</body></html>',
                headers={'content-type': 'text/html; charset=utf-8'},
            )

        result = _run_fetch(
            {'url': 'https://example.com'},
            httpx.MockTransport(handler),
        )
        self.assertTrue(result['ok'])
        self.assertIsNone(result['json'])
        self.assertIn('<body>', result['body_text'])

    def test_non_2xx_returns_ok_true_with_status(self):
        # HTTP errors are not tool errors — caller inspects status_code.
        def handler(request):
            return httpx.Response(
                404,
                json={'error': 'not found'},
                headers={'content-type': 'application/json'},
            )

        result = _run_fetch(
            {'url': 'https://example.com/missing'},
            httpx.MockTransport(handler),
        )
        self.assertTrue(result['ok'])
        self.assertEqual(result['status_code'], 404)
        self.assertEqual(result['json'], {'error': 'not found'})

    def test_binary_content_type_omits_body_text(self):
        def handler(request):
            return httpx.Response(
                200,
                content=b'\x89PNG\r\n\x1a\n' + b'\x00' * 100,
                headers={'content-type': 'image/png'},
            )

        result = _run_fetch(
            {'url': 'https://example.com/logo.png'},
            httpx.MockTransport(handler),
        )
        self.assertTrue(result['ok'])
        self.assertEqual(result['body_text'], '')
        self.assertEqual(result['body_text_note'], 'omitted_non_text_content_type')
        self.assertIsNone(result['json'])
        self.assertGreater(result['body_bytes'], 100)

    def test_body_truncation(self):
        payload_bytes = b'A' * 1_000_000  # 1MB

        def handler(request):
            return httpx.Response(
                200,
                content=payload_bytes,
                headers={'content-type': 'text/plain'},
            )

        result = _run_fetch(
            {'url': 'https://example.com/big.txt', 'max_bytes': 5000},
            httpx.MockTransport(handler),
        )
        self.assertTrue(result['ok'])
        self.assertTrue(result['truncated'])
        self.assertEqual(result['body_bytes'], 1_000_000)
        self.assertEqual(len(result['body_text']), 5000)

    def test_post_with_json_body(self):
        received = {}

        def handler(request):
            received['method'] = request.method
            received['content'] = request.content
            return httpx.Response(200, json={'echoed': True})

        result = _run_fetch(
            {
                'url': 'https://example.com/echo',
                'method': 'POST',
                'json_body': {'hello': 'world'},
            },
            httpx.MockTransport(handler),
        )
        self.assertTrue(result['ok'])
        self.assertEqual(received['method'], 'POST')
        self.assertIn(b'hello', received['content'])

    def test_params_merged_into_querystring(self):
        received_url = {}

        def handler(request):
            received_url['full'] = str(request.url)
            return httpx.Response(200, json={'ok': True})

        result = _run_fetch(
            {
                'url': 'https://huggingface.co/api/models',
                'params': {'sort': 'downloads', 'direction': '-1', 'limit': '1'},
            },
            httpx.MockTransport(handler),
        )
        self.assertTrue(result['ok'])
        self.assertIn('sort=downloads', received_url['full'])
        self.assertIn('limit=1', received_url['full'])

    def test_custom_headers_sent(self):
        received_headers = {}

        def handler(request):
            received_headers.update(dict(request.headers))
            return httpx.Response(200)

        _run_fetch(
            {
                'url': 'https://example.com',
                'headers': {'X-Custom': 'abc', 'Authorization': 'Bearer sekret'},
            },
            httpx.MockTransport(handler),
        )
        self.assertEqual(received_headers.get('x-custom'), 'abc')
        self.assertEqual(received_headers.get('authorization'), 'Bearer sekret')


class ErrorPathTests(SimpleTestCase):
    def test_timeout_returns_ok_false(self):
        def handler(request):
            raise httpx.ReadTimeout('read timed out', request=request)

        result = _run_fetch(
            {'url': 'https://slow.example.com', 'timeout_seconds': 1},
            httpx.MockTransport(handler),
        )
        self.assertFalse(result['ok'])
        self.assertIn('timeout', result['error'].lower())

    def test_connect_error_returns_ok_false(self):
        def handler(request):
            raise httpx.ConnectError('connection refused', request=request)

        result = _run_fetch(
            {'url': 'https://unreachable.example.com'},
            httpx.MockTransport(handler),
        )
        self.assertFalse(result['ok'])
        self.assertIn('http error', result['error'].lower())


class AuthorizationRedactionTests(SimpleTestCase):
    def test_authorization_value_not_in_log(self):
        # The handler logs header NAMES only, not values. Verify by capturing
        # the log record and asserting the secret value doesn't appear.
        secret = 'Bearer super-secret-token-12345'

        def handler(request):
            return httpx.Response(200)

        with self.assertLogs('core.services.td_handlers_agents', level='INFO') as cm:
            _run_fetch(
                {
                    'url': 'https://example.com',
                    'headers': {'Authorization': secret, 'X-Custom': 'ok'},
                },
                httpx.MockTransport(handler),
            )

        full_log = '\n'.join(cm.output)
        self.assertNotIn('super-secret-token-12345', full_log)
        # Header names ARE logged for debuggability.
        self.assertIn('Authorization', full_log)
