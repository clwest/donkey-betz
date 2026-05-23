"""Pure-function tests for the PA-chat warn-only audit helper.

Session 1132 (B-scaffold). DB-write tests are exercised by live smoke
against the running stack (test DB lacks pgvector). What's covered
here:

- `_extract_claimed_app_slug`: pulls from routing or context, returns
  empty when neither is set
- `_client_ip_from_request`: honors X-Forwarded-For first, falls back
  to REMOTE_ADDR, None when neither is set
- `_classify_auth_mode`: reads Authorization header first, falls back
  to DRF authenticator, identifies fleet_signature when fleet_identity
  is present
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from core.services.fleet_pa_chat_audit import (
    _classify_auth_mode,
    _client_ip_from_request,
    _extract_claimed_app_slug,
)


def _fake_request(*, meta=None, data=None):
    return SimpleNamespace(
        META=meta or {},
        data=data if data is not None else {},
        path="/api/pa/chat/",
    )


# ─── _extract_claimed_app_slug ────────────────────────────────────────


class TestExtractClaimedAppSlug:
    def test_returns_empty_when_no_data(self):
        req = _fake_request(data={})
        assert _extract_claimed_app_slug(req) == ""

    def test_returns_empty_when_data_not_dict(self):
        req = _fake_request(data="not-a-dict")
        assert _extract_claimed_app_slug(req) == ""

    def test_routing_app_slug_wins_over_context(self):
        # When both are set, routing wins because that's the more
        # explicit fleet-routing claim path.
        req = _fake_request(data={
            "routing": {"app_slug": "from-routing"},
            "context": {"app_slug": "from-context"},
        })
        assert _extract_claimed_app_slug(req) == "from-routing"

    def test_falls_back_to_context_app_slug(self):
        req = _fake_request(data={"context": {"app_slug": "signal-studio"}})
        assert _extract_claimed_app_slug(req) == "signal-studio"

    def test_returns_empty_when_routing_app_slug_is_empty(self):
        req = _fake_request(data={
            "routing": {"app_slug": ""},
            "context": {"app_slug": "from-context"},
        })
        # Empty routing.app_slug → fall through to context.app_slug.
        assert _extract_claimed_app_slug(req) == "from-context"

    def test_non_dict_routing_or_context_skipped(self):
        req = _fake_request(data={
            "routing": "not-a-dict",
            "context": ["also-not-a-dict"],
        })
        assert _extract_claimed_app_slug(req) == ""

    def test_int_app_slug_stringified(self):
        # Defensive: someone could send a numeric "app slug" by mistake.
        req = _fake_request(data={"context": {"app_slug": 42}})
        assert _extract_claimed_app_slug(req) == "42"


# ─── _client_ip_from_request ──────────────────────────────────────────


class TestClientIpFromRequest:
    def test_returns_none_when_no_meta(self):
        req = _fake_request(meta={})
        assert _client_ip_from_request(req) is None

    def test_uses_remote_addr_when_no_xff(self):
        req = _fake_request(meta={"REMOTE_ADDR": "10.0.0.1"})
        assert _client_ip_from_request(req) == "10.0.0.1"

    def test_xff_first_entry_preferred(self):
        # Proxies append; first entry = original client per RFC 7239.
        req = _fake_request(meta={
            "HTTP_X_FORWARDED_FOR": "203.0.113.5, 10.0.0.1",
            "REMOTE_ADDR": "10.0.0.1",
        })
        assert _client_ip_from_request(req) == "203.0.113.5"

    def test_xff_strips_whitespace(self):
        req = _fake_request(meta={
            "HTTP_X_FORWARDED_FOR": "  192.0.2.99  ,  10.0.0.2  ",
        })
        assert _client_ip_from_request(req) == "192.0.2.99"

    def test_empty_xff_falls_back_to_remote_addr(self):
        req = _fake_request(meta={
            "HTTP_X_FORWARDED_FOR": "",
            "REMOTE_ADDR": "172.16.0.1",
        })
        assert _client_ip_from_request(req) == "172.16.0.1"


# ─── _classify_auth_mode ──────────────────────────────────────────────


def _fake_user(authenticated=True):
    u = MagicMock()
    u.is_authenticated = authenticated
    return u


def _request_with_auth(*, auth_header=None, authenticator_name=None):
    meta = {}
    if auth_header is not None:
        meta["HTTP_AUTHORIZATION"] = auth_header
    req = _fake_request(meta=meta)
    if authenticator_name is not None:
        # DRF stashes the auth class instance here; we set a stub.
        authenticator = MagicMock()
        authenticator.__class__.__name__ = authenticator_name
        req.successful_authenticator = authenticator
    return req


class TestClassifyAuthMode:
    def test_fleet_signature_wins_over_everything(self):
        from core.models.fleet import FleetPAChatAuditRow
        req = _request_with_auth(auth_header="Token abc123")
        result = _classify_auth_mode(
            req,
            fleet_identity={"app_slug": "signal-studio"},
            user=_fake_user(True),
        )
        assert result == FleetPAChatAuditRow.AUTH_MODE_FLEET_SIGNATURE

    def test_token_authorization_header_maps_to_bearer_only(self):
        from core.models.fleet import FleetPAChatAuditRow
        req = _request_with_auth(auth_header="Token abc123")
        result = _classify_auth_mode(req, fleet_identity=None, user=_fake_user(True))
        assert result == FleetPAChatAuditRow.AUTH_MODE_BEARER_ONLY

    def test_bearer_authorization_header_maps_to_bearer_only(self):
        from core.models.fleet import FleetPAChatAuditRow
        req = _request_with_auth(auth_header="Bearer xyz789")
        result = _classify_auth_mode(req, fleet_identity=None, user=_fake_user(True))
        assert result == FleetPAChatAuditRow.AUTH_MODE_BEARER_ONLY

    def test_lowercase_bearer_also_recognized(self):
        from core.models.fleet import FleetPAChatAuditRow
        req = _request_with_auth(auth_header="bearer xyz789")
        result = _classify_auth_mode(req, fleet_identity=None, user=_fake_user(True))
        assert result == FleetPAChatAuditRow.AUTH_MODE_BEARER_ONLY

    def test_session_user_when_no_auth_header_session_authenticator(self):
        from core.models.fleet import FleetPAChatAuditRow
        req = _request_with_auth(authenticator_name="SessionAuthentication")
        result = _classify_auth_mode(req, fleet_identity=None, user=_fake_user(True))
        assert result == FleetPAChatAuditRow.AUTH_MODE_SESSION_USER

    def test_api_user_token_when_no_auth_header_token_authenticator(self):
        from core.models.fleet import FleetPAChatAuditRow
        req = _request_with_auth(authenticator_name="TokenAuthentication")
        result = _classify_auth_mode(req, fleet_identity=None, user=_fake_user(True))
        assert result == FleetPAChatAuditRow.AUTH_MODE_API_USER_TOKEN

    def test_anonymous_when_no_user(self):
        from core.models.fleet import FleetPAChatAuditRow
        req = _request_with_auth()
        result = _classify_auth_mode(req, fleet_identity=None, user=None)
        assert result == FleetPAChatAuditRow.AUTH_MODE_ANONYMOUS

    def test_anonymous_when_user_not_authenticated(self):
        from core.models.fleet import FleetPAChatAuditRow
        req = _request_with_auth()
        result = _classify_auth_mode(
            req, fleet_identity=None, user=_fake_user(False),
        )
        assert result == FleetPAChatAuditRow.AUTH_MODE_ANONYMOUS

    def test_authenticated_with_unknown_authenticator_falls_to_session(self):
        # Defensive: if DRF added a new auth class we don't recognize,
        # bucket it as session_user (the web UI default) rather than
        # surprising operators with anonymous.
        from core.models.fleet import FleetPAChatAuditRow
        req = _request_with_auth(authenticator_name="MysteryAuthentication")
        result = _classify_auth_mode(req, fleet_identity=None, user=_fake_user(True))
        assert result == FleetPAChatAuditRow.AUTH_MODE_SESSION_USER

    def test_other_authorization_scheme_not_bearer(self):
        # Basic auth or some custom scheme shouldn't be misclassified
        # as bearer_only.
        from core.models.fleet import FleetPAChatAuditRow
        req = _request_with_auth(
            auth_header="Basic dXNlcjpwYXNz",
            authenticator_name="SessionAuthentication",
        )
        result = _classify_auth_mode(req, fleet_identity=None, user=_fake_user(True))
        assert result == FleetPAChatAuditRow.AUTH_MODE_SESSION_USER
