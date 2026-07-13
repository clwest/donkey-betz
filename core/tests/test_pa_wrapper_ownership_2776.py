"""S2776 N21 — PA wrapper ownership verification tests.

Locks three contracts introduced this session:

  1. ``GET /api/pa/whoami/`` returns the authenticated user's identity
     as a bounded 3-field payload (username, user_id, is_staff).
     Rejects unauthenticated requests.

  2. ``verify_pa_wrapper_ownership`` management command distinguishes:
       * exit 0 — verified · cache file written with lean payload
       * exit 2 — mismatch · token owner != pin owner
       * exit 3 — token invalid · missing env / whoami rejection /
         Django unreachable / malformed response
       * exit 4 — pin belongs to no user · orphan pin

  3. Cache file at ``<cache-dir>/<pin>.json`` contains
     ``{pin, verified_user_id, verified_username, verified_at}`` on success.

Ratified: S2776 Rigby joint SIGN (Q1 DISAGREED with Claude — dedicated
command not session_lifecycle extension; Q2 AGREED on dedicated
``/api/pa/whoami/`` + sharp 5-point test; Q3 MOSTLY AGREED with content
fold for verified_user_id in cache; 4 zoom-out concerns folded as 2
same-PR-actionable + 2 same-PR-mitigatable + 1 future-trigger) + Chris
D-verdict yes.

The bash prelude in ``tools/pa_local.sh`` is exercised manually + via
live E2E; the Python surface (view + command) is what gets locked here.
"""
from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from core.models import ChatConversation


class PaWhoamiViewTests(TestCase):
    """/api/pa/whoami/ contract — bounded 3-field payload, auth-required."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(
            username="test_wrapper_owner",
            is_staff=True,
        )

    def test_returns_username_user_id_is_staff(self):
        client = Client()
        client.force_login(self.user)
        response = client.get(reverse("pa-whoami"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["username"], "test_wrapper_owner")
        self.assertEqual(payload["user_id"], str(self.user.id))
        self.assertTrue(payload["is_staff"])
        # Bounded output — no bonus fields (sharp 5-point test point 4).
        self.assertEqual(
            set(payload.keys()),
            {"username", "user_id", "is_staff"},
        )

    def test_rejects_unauthenticated_request(self):
        client = Client()
        response = client.get(reverse("pa-whoami"))
        # @login_required redirects (302) or returns 401/403 depending
        # on settings; anything non-2xx satisfies the contract.
        self.assertNotEqual(response.status_code, 200)
        # Accept 302/401/403 as valid rejection responses.
        self.assertIn(response.status_code, {302, 401, 403})

    def test_get_only(self):
        client = Client()
        client.force_login(self.user)
        response = client.post(reverse("pa-whoami"))
        self.assertEqual(response.status_code, 405)


class VerifyPaWrapperOwnershipCommandTests(TestCase):
    """verify_pa_wrapper_ownership exit-code + cache contract."""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_user(
            username="wrapper_owner",
        )
        cls.other = User.objects.create_user(
            username="wrapper_other",
        )
        cls.pin = "pa-0000000000000001"
        cls.other_pin = "pa-0000000000000002"
        cls.orphan_pin = "pa-ffffffffffffffff"
        ChatConversation.objects.create(
            conversation_id=cls.pin,
            user_id=cls.owner.id,
            session_title="test",
            user_message="hi",
            assistant_response="hi",
        )
        ChatConversation.objects.create(
            conversation_id=cls.other_pin,
            user_id=cls.other.id,
            session_title="test",
            user_message="hi",
            assistant_response="hi",
        )

    def _run(self, pin: str, cache_dir: Path, token: str = "fake-token",
             whoami_response=None, whoami_http_status: int = 200):
        """Run the command with a mocked whoami HTTP call. Returns exit code + cache path."""
        cache_path = cache_dir / f"{pin}.json"

        # Craft a mock urllib response for the whoami call.
        class _FakeResp:
            def __init__(self, payload):
                self._payload = json.dumps(payload).encode("utf-8")
            def read(self):
                return self._payload
            def __enter__(self):
                return self
            def __exit__(self, *_):
                return False

        from urllib.error import HTTPError

        def mock_urlopen(req, timeout=10):
            if whoami_http_status != 200:
                raise HTTPError(
                    url=req.full_url, code=whoami_http_status,
                    msg="rejected", hdrs=None, fp=None,
                )
            return _FakeResp(whoami_response or {})

        exit_code = 0
        with patch.dict("os.environ", {"PA_API_TOKEN": token} if token else {}, clear=False):
            if not token:
                # Simulate empty PA_API_TOKEN.
                import os as _os
                _os.environ.pop("PA_API_TOKEN", None)
            with patch("urllib.request.urlopen", side_effect=mock_urlopen):
                try:
                    call_command(
                        "verify_pa_wrapper_ownership",
                        "--pin", pin,
                        "--cache-dir", str(cache_dir),
                        "--api-url", "http://localhost:8000",
                    )
                except SystemExit as e:
                    exit_code = int(e.code) if e.code is not None else 0
        return exit_code, cache_path

    def test_success_writes_cache(self):
        with TemporaryDirectory() as td:
            cache_dir = Path(td)
            code, cache_path = self._run(
                pin=self.pin,
                cache_dir=cache_dir,
                whoami_response={
                    "username": self.owner.username,
                    "user_id": str(self.owner.id),
                    "is_staff": False,
                },
            )
            self.assertEqual(code, 0)
            self.assertTrue(cache_path.exists())
            payload = json.loads(cache_path.read_text())
            self.assertEqual(payload["pin"], self.pin)
            self.assertEqual(payload["verified_user_id"], str(self.owner.id))
            self.assertEqual(payload["verified_username"], self.owner.username)
            self.assertIn("verified_at", payload)

    def test_mismatch_returns_exit_2(self):
        """Token belongs to owner; pin belongs to other → mismatch."""
        with TemporaryDirectory() as td:
            cache_dir = Path(td)
            code, cache_path = self._run(
                pin=self.other_pin,  # pin owner = self.other
                cache_dir=cache_dir,
                whoami_response={
                    "username": self.owner.username,
                    "user_id": str(self.owner.id),  # token owner = self.owner
                    "is_staff": False,
                },
            )
            self.assertEqual(code, 2)
            self.assertFalse(cache_path.exists())

    def test_missing_token_returns_exit_3(self):
        with TemporaryDirectory() as td:
            cache_dir = Path(td)
            code, cache_path = self._run(
                pin=self.pin,
                cache_dir=cache_dir,
                token="",  # forces PA_API_TOKEN unset
            )
            self.assertEqual(code, 3)
            self.assertFalse(cache_path.exists())

    def test_whoami_rejection_returns_exit_3(self):
        with TemporaryDirectory() as td:
            cache_dir = Path(td)
            code, cache_path = self._run(
                pin=self.pin,
                cache_dir=cache_dir,
                whoami_http_status=403,
            )
            self.assertEqual(code, 3)
            self.assertFalse(cache_path.exists())

    def test_orphan_pin_returns_exit_4(self):
        """Pin resolves to no ChatConversation row → orphan."""
        with TemporaryDirectory() as td:
            cache_dir = Path(td)
            code, cache_path = self._run(
                pin=self.orphan_pin,
                cache_dir=cache_dir,
                whoami_response={
                    "username": self.owner.username,
                    "user_id": str(self.owner.id),
                    "is_staff": False,
                },
            )
            self.assertEqual(code, 4)
            self.assertFalse(cache_path.exists())

    def test_json_flag_emits_success_json(self):
        with TemporaryDirectory() as td:
            cache_dir = Path(td)
            from io import StringIO
            out = StringIO()
            owner_username = self.owner.username
            owner_id = str(self.owner.id)
            with patch.dict("os.environ", {"PA_API_TOKEN": "fake"}, clear=False):
                class _FakeResp:
                    def __init__(self):
                        self._payload = json.dumps({
                            "username": owner_username,
                            "user_id": owner_id,
                            "is_staff": False,
                        }).encode("utf-8")
                    def read(self):
                        return self._payload
                    def __enter__(self):
                        return self
                    def __exit__(self, *_):
                        return False
                with patch("urllib.request.urlopen", return_value=_FakeResp()):
                    try:
                        call_command(
                            "verify_pa_wrapper_ownership",
                            "--pin", self.pin,
                            "--cache-dir", str(cache_dir),
                            "--api-url", "http://localhost:8000",
                            "--json",
                            stdout=out,
                        )
                    except SystemExit as e:
                        self.assertEqual(e.code, 0)
            payload = json.loads(out.getvalue().strip())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["pin"], self.pin)
            self.assertEqual(payload["verified_user_id"], str(self.owner.id))
