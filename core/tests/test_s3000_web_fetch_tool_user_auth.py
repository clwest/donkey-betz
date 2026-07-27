"""Session 3000 — web_fetch_tool user auth injection (v2 item #5, corrected shape).

Previously called "web_fetch_tool session cookies" — actual gap surfaced by
S3000 investigation is simpler: handler had `user_id` in dispatch context
but never used it to inject the user's DRF Token. `Authorization: Token
<key>` is what our own `MobileTokenAuthentication` accepts, so injecting
that header makes Rigby's `web_fetch_tool` calls to `/api/repo/...`
return 200 instead of 401.

Contract:
- `use_user_auth=True` in payload + `user_id` in dispatch context → look
  up user's DRF Token via `rest_framework.authtoken.models.Token`; inject
  `Authorization: Token <key>` header
- Only injects when caller hasn't already supplied an Authorization
  header (explicit override wins)
- Fail-open: no Token row for the user → proceed unauthenticated,
  endpoint's 401 is returned as-is
- Default `use_user_auth=False` — no change to existing external callsites
"""
from __future__ import annotations

from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.authtoken.models import Token

from core.services.tool_dispatcher import get_tool_dispatcher


class WebFetchToolUserAuthTests(TestCase):
    """web_fetch_tool injects DRF token when use_user_auth=True."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="s3000_tester",
            password="pw",
            email="s3000@test.local",
        )
        self.token = Token.objects.create(user=self.user)
        self.dispatcher = get_tool_dispatcher()
        self.handler = self.dispatcher._tool_handlers["web_fetch_tool"]

    def _call(self, payload, user_id=None):
        return self.handler(
            tool_name="web_fetch_tool",
            payload=payload,
            user_id=user_id,
            trace_id="test-s3000-trace",
        )

    def _mock_httpx(self, status_code=200, body=b'{"ok": true}'):
        """Return a context-manager mock that captures the actual httpx call."""
        captured = {}

        def _make_resp():
            resp = MagicMock()
            resp.status_code = status_code
            resp.headers = {"content-type": "application/json"}
            resp.content = body
            resp.text = body.decode("utf-8", "replace")
            return resp

        class FakeClient:
            def __init__(self, *args, **kwargs):
                pass
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False
            def get(self, url, headers=None, params=None):
                captured["headers"] = dict(headers or {})
                captured["method"] = "GET"
                captured["url"] = url
                return _make_resp()
            def post(self, url, headers=None, params=None, json=None):
                captured["headers"] = dict(headers or {})
                captured["method"] = "POST"
                captured["url"] = url
                return _make_resp()

        return FakeClient, captured

    # ---- default behavior unchanged ----

    def test_default_no_flag_no_injection(self):
        FakeClient, captured = self._mock_httpx()
        with patch("httpx.Client", FakeClient):
            result = self._call(
                {"url": "http://localhost:8000/api/repo/x/"},
                user_id=self.user.id,
            )
        self.assertTrue(result["ok"])
        # No Authorization header injected — caller didn't ask for it.
        self.assertNotIn("Authorization", captured["headers"])

    def test_use_user_auth_false_no_injection(self):
        FakeClient, captured = self._mock_httpx()
        with patch("httpx.Client", FakeClient):
            self._call(
                {"url": "http://localhost:8000/api/repo/x/", "use_user_auth": False},
                user_id=self.user.id,
            )
        self.assertNotIn("Authorization", captured["headers"])

    # ---- injection path ----

    def test_use_user_auth_true_injects_token(self):
        FakeClient, captured = self._mock_httpx()
        with patch("httpx.Client", FakeClient):
            self._call(
                {"url": "http://localhost:8000/api/repo/x/", "use_user_auth": True},
                user_id=self.user.id,
            )
        self.assertEqual(
            captured["headers"].get("Authorization"),
            f"Token {self.token.key}",
        )

    def test_use_user_auth_true_no_user_id_no_injection(self):
        # If dispatch context has no user_id, we can't look up a token.
        FakeClient, captured = self._mock_httpx()
        with patch("httpx.Client", FakeClient):
            self._call(
                {"url": "http://localhost:8000/api/repo/x/", "use_user_auth": True},
                user_id=None,
            )
        self.assertNotIn("Authorization", captured["headers"])

    def test_use_user_auth_true_no_token_row_fail_open(self):
        # User has no Token — proceed unauthenticated (fail-open).
        User = get_user_model()
        tokenless = User.objects.create_user(
            username="s3000_tokenless", password="pw",
        )
        FakeClient, captured = self._mock_httpx(status_code=401)
        with patch("httpx.Client", FakeClient):
            result = self._call(
                {"url": "http://localhost:8000/api/repo/x/", "use_user_auth": True},
                user_id=tokenless.id,
            )
        # Request still went through, endpoint returned its own 401
        self.assertEqual(result["status_code"], 401)
        self.assertNotIn("Authorization", captured["headers"])

    # ---- explicit override wins ----

    def test_explicit_auth_header_wins_case_insensitive(self):
        # Caller-supplied Authorization header should NOT be overwritten,
        # even when use_user_auth=True. Check case-insensitive match.
        FakeClient, captured = self._mock_httpx()
        with patch("httpx.Client", FakeClient):
            self._call(
                {
                    "url": "http://localhost:8000/api/repo/x/",
                    "use_user_auth": True,
                    "headers": {"authorization": "Bearer explicit-override"},
                },
                user_id=self.user.id,
            )
        # Explicit lowercase header preserved; no `Authorization` (title
        # case) added — the case-insensitive check prevented dup.
        self.assertEqual(
            captured["headers"].get("authorization"),
            "Bearer explicit-override",
        )
        self.assertNotIn("Authorization", captured["headers"])

    def test_explicit_uppercase_auth_header_wins(self):
        FakeClient, captured = self._mock_httpx()
        with patch("httpx.Client", FakeClient):
            self._call(
                {
                    "url": "http://localhost:8000/api/repo/x/",
                    "use_user_auth": True,
                    "headers": {"Authorization": "Bearer explicit"},
                },
                user_id=self.user.id,
            )
        self.assertEqual(
            captured["headers"].get("Authorization"),
            "Bearer explicit",
        )
        # Injected token key must NOT overwrite explicit value
        self.assertNotIn(
            self.token.key,
            captured["headers"].get("Authorization", ""),
        )

    # ---- no mutation of caller's headers dict ----

    def test_injection_does_not_mutate_caller_headers(self):
        caller_headers = {"X-Custom": "foo"}
        FakeClient, _captured = self._mock_httpx()
        with patch("httpx.Client", FakeClient):
            self._call(
                {
                    "url": "http://localhost:8000/api/repo/x/",
                    "use_user_auth": True,
                    "headers": caller_headers,
                },
                user_id=self.user.id,
            )
        # Original dict should still only have X-Custom — no Authorization.
        self.assertEqual(caller_headers, {"X-Custom": "foo"})
