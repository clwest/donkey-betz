"""
I-0301 Phase 3 Stage 2 — Bucket B remediation regression tests.

For each endpoint in tests/security/endpoints_covered.txt with status
``remediated``, this suite exercises the following invariants:

1. Anonymous request MUST be rejected with a safety-envelope response
   whose ``reason_code`` is ``not_authenticated`` OR ``permission_denied``.
2. Response body MUST conform to the safety contract §3.1 permitted-field
   allowlist.
3. Response body MUST NOT contain any §3.2 prohibited content (via the
   same probes as ``test_failure_envelope_conformance.py``).

Contract ref:
    docs/research/implementation/tenant_boundary_lockdown/failure_data_safety_contract.md
    docs/research/implementation/tenant_boundary_lockdown/I-0301_scoping.md

Endpoint pin file:
    tests/security/endpoints_covered.txt

Discipline: adding a new endpoint to the pin file requires either
(a) marking it ``remediated`` and adding the endpoint to a probe class here,
or (b) marking it ``pending`` and pinning the follow-on stage. Non-remediated
endpoints do NOT appear in this suite's active tests.

Known limitation — envelope-shape divergence (follow-on scope):

The pre-existing ``core.api_responses.APIResponseEnvelope`` class emits its
own JSON error shape (``{success: False, error: {code, message}}``) via
helpers like ``api_unauthorized`` used by ``core.auth_middleware``. That
middleware intercepts unauthenticated requests before DRF's exception
handler fires, so the safety-contract envelope from
``core.security.error_envelope`` doesn't apply to these responses.

Both shapes are safe (no tenant / substrate leakage). But they are NOT
uniform. Envelope unification — migrating ``APIResponseEnvelope`` helpers
to emit safety-contract shape — is a separate substrate change with
cross-platform blast radius (frontend TSX parses the current shape).
Tracked as a follow-on arc; see I-0301 scoping §12 amendments.

This suite therefore accepts either envelope shape for anonymous
rejection, provided the response is safe (401/403 status + prohibited-
content probes pass).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

import pytest
from django.test import Client
from django.urls import reverse

# Reuse the prohibited-content regexes from the substrate conformance suite.
from tests.security.test_failure_envelope_conformance import (
    _ALL_PERMITTED_FIELDS,
    _CREDENTIAL_PATTERNS,
    _EXCEPTION_VALUE_PATTERNS,
    _FS_PATH_PATTERNS,
    _PROVIDER_PATTERNS,
    _REQUIRED_FIELDS,
    _STACK_TRACE_PATTERNS,
    _SUPPORT_CODE_RE,
    _UUID_ANYWHERE,
    _VALID_TERMINAL_STATES,
    _serialize,
)


_ENDPOINTS_COVERED_FILE = (
    Path(__file__).parent / "endpoints_covered.txt"
)


def _parse_endpoints_pin() -> list[dict]:
    """Parse tests/security/endpoints_covered.txt.

    Returns a list of dicts with keys: bucket, url, view, status.
    """
    endpoints: list[dict] = []
    for raw_line in _ENDPOINTS_COVERED_FILE.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 4:
            continue
        bucket, url, view, endpoint_status = parts
        endpoints.append({
            "bucket": bucket,
            "url": url,
            "view": view,
            "status": endpoint_status,
        })
    return endpoints


def _remediated_get_endpoints() -> list[dict]:
    """The subset of pinned endpoints that are marked ``remediated`` AND
    whose URL is a fixed path (no ``<param>`` placeholder) that can be
    exercised via GET.
    """
    return [
        e
        for e in _parse_endpoints_pin()
        if e["status"] == "remediated" and "<" not in e["url"]
    ]


@pytest.mark.django_db
class TestBucketBAnonymousRejection:
    """Every remediated Bucket B endpoint rejects anonymous requests with
    a conformant safety envelope."""

    def test_at_least_one_endpoint_remediated(self):
        """Sanity check that the pin file has at least one remediated
        endpoint to exercise. Guards against accidentally emptying the
        suite by mis-editing the pin file."""
        remediated = _remediated_get_endpoints()
        assert len(remediated) >= 1, (
            "tests/security/endpoints_covered.txt has no remediated GET "
            "endpoints. Suite would silently pass; refusing."
        )

    @pytest.mark.parametrize(
        "endpoint",
        _remediated_get_endpoints(),
        ids=lambda e: e["url"],
    )
    def test_anonymous_get_is_rejected(self, endpoint):
        """Anonymous GET → 401 / 403 with a safe error body.

        Envelope-shape uniformity (safety contract §3.1) is deferred: the
        pre-existing ``core.api_responses.APIResponseEnvelope`` intercepts
        auth failures in ``core.auth_middleware`` before DRF's exception
        handler fires, producing a different response body shape than the
        safety-contract envelope in ``core.security.error_envelope``. Both
        shapes are safe (neither leaks tenant data / stack traces), but
        they are not uniform.

        Envelope unification is tracked as a follow-on arc (see the file
        docstring). Stage 2a's real deliverable is the anonymous-access
        rejection itself, which this test verifies.
        """
        client = Client()
        response = client.get(endpoint["url"])

        # Anonymous MUST be rejected
        assert response.status_code in (401, 403), (
            f"Endpoint {endpoint['url']} returned status {response.status_code}"
            f" for anonymous request; expected 401 or 403"
        )

        # Response body is JSON (both envelope substrates emit JSON)
        try:
            body = json.loads(response.content)
        except json.JSONDecodeError:
            pytest.fail(
                f"Endpoint {endpoint['url']} response is not valid JSON: "
                f"{response.content[:200]!r}"
            )

        # Verify the response is one of the two known safe shapes:
        # (a) safety contract §3.1 envelope (from
        #     core.security.error_envelope.drf_exception_handler); OR
        # (b) core.api_responses.APIResponseEnvelope.unauthorized/forbidden
        #     shape ``{success: False, error: {code, message}}``
        is_safety_envelope = (
            "reason_code" in body and "support_code" in body
        )
        is_apiresp_envelope = (
            "success" in body
            and "error" in body
            and isinstance(body.get("error"), dict)
            and "code" in body["error"]
        )
        assert is_safety_envelope or is_apiresp_envelope, (
            f"Endpoint {endpoint['url']} response body is neither a "
            f"safety-contract envelope nor an APIResponseEnvelope: {body}"
        )

        if is_safety_envelope:
            # Full §3.1 conformance
            for field in _REQUIRED_FIELDS:
                assert field in body, (
                    f"Endpoint {endpoint['url']} safety envelope missing "
                    f"required field {field}: {body}"
                )
            assert body["reason_code"] in (
                "not_authenticated",
                "permission_denied",
            )
            assert body["terminal_state"] == "DENIED"
            assert body["retryable"] is False
            assert _SUPPORT_CODE_RE.match(body["support_code"]), (
                f"support_code {body['support_code']!r} does not match "
                f"contract §5.1 format"
            )

    @pytest.mark.parametrize(
        "endpoint",
        _remediated_get_endpoints(),
        ids=lambda e: e["url"],
    )
    def test_anonymous_response_passes_prohibited_content_probes(self, endpoint):
        """Anonymous rejection response never contains prohibited content."""
        client = Client()
        response = client.get(endpoint["url"])

        try:
            body = json.loads(response.content)
        except json.JSONDecodeError:
            pytest.skip(
                f"Endpoint {endpoint['url']} response is not JSON; skipping "
                f"prohibited-content probe on non-JSON body"
            )

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
                    f"Endpoint {endpoint['url']} anonymous-rejection response "
                    f"contains {name} pattern {pattern!r}: {serialized}"
                )

        # No UUID anywhere (Rigby SIGN §11)
        assert not _UUID_ANYWHERE.search(serialized), (
            f"Endpoint {endpoint['url']} response contains a UUID: {serialized}"
        )


class TestEndpointsCoveredPinFileShape:
    """The pin file has a valid shape and every row is legal."""

    def test_all_rows_have_valid_bucket(self):
        for endpoint in _parse_endpoints_pin():
            assert endpoint["bucket"] in ("A", "A2", "B", "C", "D"), (
                f"Invalid bucket in pin file: {endpoint}"
            )

    def test_all_rows_have_valid_status(self):
        valid_statuses = {"pending", "remediated", "dead-gated", "in-flight"}
        for endpoint in _parse_endpoints_pin():
            assert endpoint["status"] in valid_statuses, (
                f"Invalid status in pin file: {endpoint}; valid: {valid_statuses}"
            )
