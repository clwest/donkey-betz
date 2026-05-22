"""Tests for `core.services.fleet_auth` (Session 1129 Move 1).

Covers `verify_signed_request()` happy path + every canonical deny
code. Co-designed with Rigby (spec section 1.5).

These tests **mock the ORM lookup** rather than touching the test DB.
The Docker-resident u-d-b postgres doesn't have pgvector installed in
its container, so the test-DB-creation path fails on this machine.
Mocking the model `objects.select_related("service").get(...)` lets us
exercise the full verify logic (signature compute, timestamp window,
nonce replay, app_slug binding, signature mismatch, disabled status)
without any DB calls. The model layer itself was smoke-tested
manually against the main DB; see commit message.
"""
from __future__ import annotations

import base64
import time
import uuid
from unittest.mock import MagicMock, patch

import pytest

from core.services.fleet_auth import (
    HEADER_APP,
    HEADER_KEY_ID,
    HEADER_NONCE,
    HEADER_SIGNATURE,
    HEADER_TIMESTAMP,
    DenyCode,
    _consume_nonce,
    compute_signature,
    verify_signed_request,
)


# ─── Fakes ────────────────────────────────────────────────────────────


def _make_fake_identity(app_slug="contract-concierge", status="active"):
    identity = MagicMock()
    identity.app_slug = app_slug
    identity.status = status
    identity.STATUS_DISABLED = "disabled"
    identity.pk = uuid.uuid4()
    identity.capabilities = {
        "routing": {"can_request_hint": True, "can_request_force": True},
    }
    identity.allowed_routes = ["/api/pa/chat/"]
    return identity


def _make_fake_key(
    identity,
    key_id="fs_contractconcierge_k1",
    secret_hash="testhashdeadbeef",
    status="active",
    usable=True,
):
    key = MagicMock()
    key.key_id = key_id
    key.secret_hash = secret_hash
    key.status = status
    key.STATUS_DISABLED = "disabled"
    key.service = identity
    key.pk = uuid.uuid4()
    key.is_currently_usable = MagicMock(return_value=usable)
    return key


def _signed_headers(
    *,
    app_slug: str,
    key_id: str,
    secret: str,
    method: str = "POST",
    path: str = "/api/pa/chat/",
    query: str = "",
    body: bytes = b"",
    timestamp: int | None = None,
    nonce: str | None = None,
) -> dict[str, str]:
    ts = str(timestamp if timestamp is not None else int(time.time()))
    n = nonce or uuid.uuid4().hex
    sig = compute_signature(
        method=method,
        path=path,
        query=query,
        app_slug=app_slug,
        key_id=key_id,
        timestamp=ts,
        nonce=n,
        body=body,
        secret=secret,
    )
    return {
        HEADER_APP: app_slug,
        HEADER_KEY_ID: key_id,
        HEADER_TIMESTAMP: ts,
        HEADER_NONCE: n,
        HEADER_SIGNATURE: sig,
    }


@pytest.fixture
def patched_orm():
    """Patch `FleetServiceKey.objects.select_related().get()` chain.

    Yields a callable `register(key, ...)` that maps key_id → key object,
    plus `register_missing(key_id)` for unknown-key tests.
    """
    registry: dict[str, object] = {}
    missing: set[str] = set()

    def register(key):
        registry[key.key_id] = key

    def register_missing(key_id: str):
        missing.add(key_id)

    def fake_get(key_id):
        if key_id in missing or key_id not in registry:
            from core.models.fleet import FleetServiceKey
            raise FleetServiceKey.DoesNotExist()
        return registry[key_id]

    # Patch the chain: FleetServiceKey.objects.select_related(...).get(key_id=...)
    with patch("core.models.fleet.FleetServiceKey.objects") as mock_manager:
        mock_select = MagicMock()
        mock_manager.select_related.return_value = mock_select
        mock_select.get.side_effect = lambda key_id: fake_get(key_id)

        # Also patch the last_used_at .update() calls (lines 535-538 in fleet_auth)
        mock_manager.filter.return_value.update = MagicMock(return_value=1)
        with patch(
            "core.models.fleet.FleetServiceIdentity.objects"
        ) as mock_ident_manager:
            mock_ident_manager.filter.return_value.update = MagicMock(return_value=1)
            yield {"register": register, "register_missing": register_missing}


# ─── Happy path ───────────────────────────────────────────────────────


class TestHappyPath:
    def test_valid_signature_passes(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity, secret_hash="known_verify_key_hash")
        patched_orm["register"](key)

        body = b'{"message": "hi"}'
        headers = _signed_headers(
            app_slug=identity.app_slug,
            key_id=key.key_id,
            secret=key.secret_hash,
            body=body,
        )
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=body
        )
        assert out.ok is True, f"deny_code={out.deny_code} msg={out.message}"
        assert out.app_slug_resolved == identity.app_slug
        assert out.deny_code == ""

    def test_get_with_querystring(self, patched_orm):
        identity = _make_fake_identity(app_slug="signal-studio")
        key = _make_fake_key(
            identity, key_id="fs_signalstudio_k1", secret_hash="hash_ss"
        )
        patched_orm["register"](key)

        headers = _signed_headers(
            app_slug=identity.app_slug,
            key_id=key.key_id,
            secret=key.secret_hash,
            method="GET",
            path="/api/fleet/artifacts",
            query="limit=20&type=contract_draft",
            body=b"",
        )
        out = verify_signed_request(
            method="GET",
            path="/api/fleet/artifacts",
            query="limit=20&type=contract_draft",
            headers=headers,
            body=b"",
        )
        assert out.ok is True


# ─── Deny paths ───────────────────────────────────────────────────────


class TestDenyMissingHeaders:
    def test_no_headers_at_all(self, patched_orm):
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers={}, body=b""
        )
        assert out.deny_code == DenyCode.MISSING_HEADERS
        assert out.status_code == 401

    def test_partial_headers(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity)
        patched_orm["register"](key)

        headers = _signed_headers(
            app_slug=identity.app_slug,
            key_id=key.key_id,
            secret=key.secret_hash,
        )
        del headers[HEADER_SIGNATURE]
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=b""
        )
        assert out.deny_code == DenyCode.MISSING_HEADERS


class TestDenyMalformedHeaders:
    def test_timestamp_not_integer(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity)
        patched_orm["register"](key)

        headers = _signed_headers(
            app_slug=identity.app_slug, key_id=key.key_id, secret=key.secret_hash
        )
        headers[HEADER_TIMESTAMP] = "not-a-number"
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=b""
        )
        assert out.deny_code == DenyCode.MALFORMED_HEADERS

    def test_signature_not_base64(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity)
        patched_orm["register"](key)

        headers = _signed_headers(
            app_slug=identity.app_slug, key_id=key.key_id, secret=key.secret_hash
        )
        headers[HEADER_SIGNATURE] = "@@not-base64@@"
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=b""
        )
        assert out.deny_code == DenyCode.MALFORMED_HEADERS


class TestDenyTimestampSkew:
    def test_far_future_rejected(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity)
        patched_orm["register"](key)

        future = int(time.time()) + 9999
        headers = _signed_headers(
            app_slug=identity.app_slug,
            key_id=key.key_id,
            secret=key.secret_hash,
            timestamp=future,
        )
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=b""
        )
        assert out.deny_code == DenyCode.TIMESTAMP_SKEW
        assert out.timestamp_delta_seconds is not None
        assert out.timestamp_delta_seconds < -300

    def test_far_past_rejected(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity)
        patched_orm["register"](key)

        past = int(time.time()) - 9999
        headers = _signed_headers(
            app_slug=identity.app_slug,
            key_id=key.key_id,
            secret=key.secret_hash,
            timestamp=past,
        )
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=b""
        )
        assert out.deny_code == DenyCode.TIMESTAMP_SKEW


class TestDenyUnknownKey:
    def test_unknown_key_id(self, patched_orm):
        patched_orm["register_missing"]("fs_phantom_k1")
        headers = {
            HEADER_APP: "phantom-app",
            HEADER_KEY_ID: "fs_phantom_k1",
            HEADER_TIMESTAMP: str(int(time.time())),
            HEADER_NONCE: uuid.uuid4().hex,
            HEADER_SIGNATURE: "AAAA",
        }
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=b""
        )
        assert out.deny_code == DenyCode.UNKNOWN_KEY_ID


class TestDenyServiceDisabled:
    def test_identity_disabled(self, patched_orm):
        identity = _make_fake_identity(status="disabled")
        key = _make_fake_key(identity)
        patched_orm["register"](key)

        headers = _signed_headers(
            app_slug=identity.app_slug, key_id=key.key_id, secret=key.secret_hash
        )
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=b""
        )
        assert out.deny_code == DenyCode.SERVICE_DISABLED

    def test_key_disabled(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity, status="disabled")
        patched_orm["register"](key)

        headers = _signed_headers(
            app_slug=identity.app_slug, key_id=key.key_id, secret=key.secret_hash
        )
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=b""
        )
        assert out.deny_code == DenyCode.SERVICE_DISABLED

    def test_key_not_usable(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity, usable=False)
        patched_orm["register"](key)

        headers = _signed_headers(
            app_slug=identity.app_slug, key_id=key.key_id, secret=key.secret_hash
        )
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=b""
        )
        assert out.deny_code == DenyCode.SERVICE_DISABLED


class TestDenyAppSlugMismatch:
    def test_x_fleet_app_lies(self, patched_orm):
        identity = _make_fake_identity(app_slug="real-app")
        key = _make_fake_key(identity)
        patched_orm["register"](key)

        # Sign with a wrong app_slug so the binding check fires
        headers = _signed_headers(
            app_slug="wrong-app",
            key_id=key.key_id,
            secret=key.secret_hash,
        )
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=b""
        )
        assert out.deny_code == DenyCode.APP_SLUG_MISMATCH
        assert out.status_code == 403


class TestDenySignatureMismatch:
    def test_tampered_signature(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity, secret_hash="real_verify_key")
        patched_orm["register"](key)

        headers = _signed_headers(
            app_slug=identity.app_slug,
            key_id=key.key_id,
            secret=key.secret_hash,
        )
        # Corrupt the signature by flipping a byte
        raw = base64.b64decode(headers[HEADER_SIGNATURE])
        tampered = bytes([raw[0] ^ 0xFF]) + raw[1:]
        headers[HEADER_SIGNATURE] = base64.b64encode(tampered).decode()
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=b""
        )
        assert out.deny_code == DenyCode.SIGNATURE_MISMATCH

    def test_body_tampering_caught(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity, secret_hash="real_verify_key")
        patched_orm["register"](key)

        body = b'{"message": "original"}'
        headers = _signed_headers(
            app_slug=identity.app_slug,
            key_id=key.key_id,
            secret=key.secret_hash,
            body=body,
        )
        tampered_body = b'{"message": "tampered"}'
        out = verify_signed_request(
            method="POST",
            path="/api/pa/chat/",
            query="",
            headers=headers,
            body=tampered_body,
        )
        assert out.deny_code == DenyCode.SIGNATURE_MISMATCH

    def test_wrong_secret_signed(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity, secret_hash="server_key")
        patched_orm["register"](key)

        # Client signs with the wrong secret
        headers = _signed_headers(
            app_slug=identity.app_slug,
            key_id=key.key_id,
            secret="different_secret",
        )
        out = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=b""
        )
        assert out.deny_code == DenyCode.SIGNATURE_MISMATCH


class TestDenyReplay:
    def test_nonce_replay_rejected(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity, secret_hash="replay_key")
        patched_orm["register"](key)

        nonce = uuid.uuid4().hex
        body = b""
        headers = _signed_headers(
            app_slug=identity.app_slug,
            key_id=key.key_id,
            secret=key.secret_hash,
            nonce=nonce,
            body=body,
        )
        out1 = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=body
        )
        assert out1.ok is True, f"first call should pass: {out1.deny_code}"

        # Replay with same nonce
        out2 = verify_signed_request(
            method="POST", path="/api/pa/chat/", query="", headers=headers, body=body
        )
        assert out2.deny_code == DenyCode.REPLAY_NONCE
        assert out2.replay_detected is True


# ─── Querystring canonicalization ─────────────────────────────────────


class TestQuerystringCanonicalization:
    def test_order_doesnt_matter_for_get(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity, secret_hash="qs_key")
        patched_orm["register"](key)

        path = "/api/fleet/artifacts"
        body = b""
        client_query = "type=contract_draft&limit=20"
        headers = _signed_headers(
            app_slug=identity.app_slug,
            key_id=key.key_id,
            secret=key.secret_hash,
            method="GET",
            path=path,
            query=client_query,
            body=body,
        )
        # Server receives the OTHER ordering
        server_query = "limit=20&type=contract_draft"
        out = verify_signed_request(
            method="GET", path=path, query=server_query, headers=headers, body=body
        )
        assert out.ok is True, f"deny_code={out.deny_code}"

    def test_post_querystring_not_signed(self, patched_orm):
        identity = _make_fake_identity()
        key = _make_fake_key(identity, secret_hash="post_key")
        patched_orm["register"](key)

        body = b'{"x": 1}'
        headers = _signed_headers(
            app_slug=identity.app_slug,
            key_id=key.key_id,
            secret=key.secret_hash,
            method="POST",
            path="/api/pa/chat/",
            query="",
            body=body,
        )
        # Different querystring on the actual request — POST query is
        # NOT signed, so this must still pass.
        out = verify_signed_request(
            method="POST",
            path="/api/pa/chat/",
            query="extra=ignored",
            headers=headers,
            body=body,
        )
        assert out.ok is True


@pytest.fixture(autouse=True)
def _isolate_nonce_store():
    """Each test gets a clean in-process nonce store."""
    from core.services.fleet_auth import _DEV_NONCE_STORE
    _DEV_NONCE_STORE.clear()
    yield
    _DEV_NONCE_STORE.clear()
