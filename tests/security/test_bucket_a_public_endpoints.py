"""
I-0301 Phase 3 Stage 3 — Bucket A public-endpoint conformance tests.

Every Bucket A endpoint in tests/security/endpoints_covered.txt with
status ``remediated`` must:

1. Return the SAME response body regardless of session cookie / auth
   header (constant-shape invariant per Rigby S2742 Stage 3 SIGN Q3).
2. Never emit UUIDs, provider names, credentials, filesystem paths,
   stack traces, or exception values (contract §3.2 probes).
3. Only include the frozen field set for its specific endpoint (see
   per-view class docstring).

Contract ref:
    docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md

This suite complements ``test_bucket_b_remediation.py`` which verifies
anonymous REJECTION for Bucket B endpoints. Bucket A endpoints instead
verify anonymous ACCEPT under strict field-freeze.
"""
from __future__ import annotations

import json
import re

import pytest
from django.test import Client

from tests.security.test_failure_envelope_conformance import (
    _CREDENTIAL_PATTERNS,
    _EXCEPTION_VALUE_PATTERNS,
    _FS_PATH_PATTERNS,
    _PROVIDER_PATTERNS,
    _STACK_TRACE_PATTERNS,
    _UUID_ANYWHERE,
    _serialize,
)


@pytest.mark.django_db
class TestNervousIsResponsivePublicHealthCheck:
    """Frozen response contract for the sole Bucket A endpoint at Phase 3
    close: ``GET /api/nervous/is-responsive/``.

    Guardrails per Rigby S2742 Stage 3 SIGN Q3:
    - Constant shape (no cookie / auth-header variance)
    - Only two fields: ``is_responsive`` (bool) + ``timestamp`` (ISO)
    - No UUIDs, no providers, no internal fields
    """

    _URL = "/api/nervous/is-responsive/"
    _FROZEN_FIELDS = frozenset({"is_responsive", "timestamp"})

    def _get(self, client: Client) -> dict:
        response = client.get(self._URL)
        # 200 or 500 both permitted (see class docstring); 500 keeps
        # constant shape per view implementation.
        assert response.status_code in (200, 500), (
            f"Unexpected status {response.status_code} from {self._URL}"
        )
        return json.loads(response.content)

    def test_anonymous_get_returns_only_frozen_fields(self):
        body = self._get(Client())
        assert set(body.keys()) == self._FROZEN_FIELDS, (
            f"NervousIsResponsiveView returned {set(body.keys())}; "
            f"contract froze to {self._FROZEN_FIELDS}. Adding fields "
            f"requires re-audit against safety contract §3.2."
        )
        assert isinstance(body["is_responsive"], bool)
        assert isinstance(body["timestamp"], str)
        # ISO 8601 with timezone
        from datetime import datetime

        parsed = datetime.fromisoformat(body["timestamp"])
        assert parsed.tzinfo is not None

    def test_response_does_not_contain_uuid(self):
        body = self._get(Client())
        serialized = _serialize(body)
        assert not _UUID_ANYWHERE.search(serialized), (
            f"NervousIsResponsiveView response contains a UUID: {serialized}"
        )

    def test_response_passes_prohibited_content_probes(self):
        body = self._get(Client())
        serialized = _serialize(body)
        for pattern_set, name in (
            (_FS_PATH_PATTERNS, "filesystem-path"),
            (_STACK_TRACE_PATTERNS, "stack-trace"),
            (_EXCEPTION_VALUE_PATTERNS, "exception-value"),
            (_PROVIDER_PATTERNS, "provider-name"),
            (_CREDENTIAL_PATTERNS, "credential"),
        ):
            for pattern in pattern_set:
                assert not re.search(pattern, serialized, re.IGNORECASE), (
                    f"NervousIsResponsiveView contains {name} pattern "
                    f"{pattern!r}: {serialized}"
                )

    def test_response_shape_is_constant_across_variants(self):
        """Response body keys MUST NOT vary based on cookies / headers /
        query params (Rigby SIGN Q3 constant-shape invariant)."""
        anon_body = self._get(Client())

        # With a session cookie
        cookie_client = Client()
        cookie_client.cookies["sessionid"] = "fake-session-value"
        cookie_body = self._get(cookie_client)

        # With arbitrary auth header
        auth_client = Client()
        auth_header_body = json.loads(
            auth_client.get(
                self._URL, HTTP_AUTHORIZATION="Bearer fake-token"
            ).content
        )

        # All three must have the same key set
        assert set(anon_body.keys()) == set(cookie_body.keys()) == set(
            auth_header_body.keys()
        ), (
            "NervousIsResponsiveView response shape varies by cookie / "
            "auth header; violates constant-shape invariant"
        )

    def test_response_does_not_include_version_or_dependency_health(self):
        """Rigby SIGN Q3 explicit prohibition: no version, no queue depth,
        no dependency health beyond the boolean is_responsive."""
        body = self._get(Client())
        forbidden_field_hints = (
            "version",
            "queue_depth",
            "queue",
            "redis",
            "postgres",
            "database",
            "dependency",
            "worker",
            "celery",
        )
        for field_hint in forbidden_field_hints:
            for key in body:
                assert field_hint not in key.lower(), (
                    f"NervousIsResponsiveView response field {key!r} "
                    f"hints at {field_hint!r}; Rigby SIGN Q3 forbids "
                    f"version/queue-depth/dependency-health exposure"
                )
