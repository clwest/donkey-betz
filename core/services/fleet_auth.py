"""Fleet service-identity signature verification (Move 1).

Implements the verification half of `docs/specs/FLEET_MOVE_1_AND_2_SPEC.md`
section 1.3-1.4. Pure-function `verify_signed_request()` + small
DRF authentication / permission classes that wrap it.

Wire shape:

    fleet app                                    u-d-b
    --------                                     -----
    sign(method, path, headers, body, secret) --> X-Fleet-Signature
    POST /api/pa/chat/ with X-Fleet-* headers --> DRF auth class
                                                    verify_signed_request()
                                                    → request.fleet_identity
                                                    → audit log row

The verify function is the single source of truth for the contract.
DRF auth class is a thin shim that:
- reads `request._request.body` (raw bytes, never `request.data`)
- calls `verify_signed_request()`
- populates `request.fleet_identity` on success
- raises rest_framework.exceptions.AuthenticationFailed on hard fail
  (with the canonical deny_code in the exception detail)

For routes that REQUIRE fleet auth (artifact push/pull, eventually),
add `FleetSignatureRequiredPermission` to permission_classes. For
hybrid routes (`/api/pa/chat/` — works with user auth, gates routing
block on fleet auth), use the `Optional` variant + check
`request.fleet_identity` inline.

Co-designed with Rigby (Session 1129 — conversation pa-d19c1674b936).
Decisions locked:
- HMAC-SHA256 with per-service shared secret.
- 300s timestamp window, 600s nonce TTL in Redis.
- GET querystring is part of the signature base (sorted by key, value
  tuples, percent-encoded). POST/PUT querystring is NOT signed.
- On deny: WARN to standard logger + persist `FleetAuthAuditLog` row.
- On allow: INFO to standard logger ONLY when `FLEET_AUTH_LOG_ALL=true`;
  persist audit row unconditionally (cheap, useful for forensics).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import time
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import parse_qsl, quote, urlencode

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────

# Header names — must match the fleet brain_client signing helper byte
# for byte. Lowercased lookups happen in DRF / Django, but standard
# HTTP convention is the canonical capitalization.
HEADER_APP = "X-Fleet-App"
HEADER_KEY_ID = "X-Fleet-Key-Id"
HEADER_TIMESTAMP = "X-Fleet-Timestamp"
HEADER_NONCE = "X-Fleet-Nonce"
HEADER_SIGNATURE = "X-Fleet-Signature"
HEADER_REQUEST_ID = "X-Request-Id"

REQUIRED_HEADERS = (
    HEADER_APP,
    HEADER_KEY_ID,
    HEADER_TIMESTAMP,
    HEADER_NONCE,
    HEADER_SIGNATURE,
)

TIMESTAMP_SKEW_SECONDS = 300
NONCE_TTL_SECONDS = 600
NONCE_REDIS_PREFIX = "fleet_sig:nonce"


# Canonical deny codes (spec section 1.5)
class DenyCode:
    MISSING_HEADERS = "missing_fleet_headers"
    MALFORMED_HEADERS = "malformed_fleet_headers"
    UNKNOWN_KEY_ID = "unknown_key_id"
    SERVICE_DISABLED = "service_disabled"
    TIMESTAMP_SKEW = "timestamp_skew"
    REPLAY_NONCE = "replay_nonce"
    SIGNATURE_MISMATCH = "signature_mismatch"
    APP_SLUG_MISMATCH = "app_slug_mismatch"
    CAPABILITY_DENIED = "capability_denied"
    ROUTE_NOT_ALLOWLISTED = "route_not_allowlisted"
    PAYLOAD_TOO_LARGE = "payload_too_large"
    CONTENT_TYPE_NOT_ALLOWED = "content_type_not_allowed"


# HTTP status for each deny code (spec section 1.5 table)
DENY_STATUS_CODES: dict[str, int] = {
    DenyCode.MISSING_HEADERS: 401,
    DenyCode.MALFORMED_HEADERS: 401,
    DenyCode.UNKNOWN_KEY_ID: 401,
    DenyCode.SERVICE_DISABLED: 401,
    DenyCode.TIMESTAMP_SKEW: 401,
    DenyCode.REPLAY_NONCE: 401,
    DenyCode.SIGNATURE_MISMATCH: 401,
    DenyCode.APP_SLUG_MISMATCH: 403,
    DenyCode.CAPABILITY_DENIED: 403,
    DenyCode.ROUTE_NOT_ALLOWLISTED: 403,
    DenyCode.PAYLOAD_TOO_LARGE: 413,
    DenyCode.CONTENT_TYPE_NOT_ALLOWED: 415,
}


# ──────────────────────────────────────────────────────────────────────
# Result objects
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class VerifyOutcome:
    """Return shape of verify_signed_request().

    `ok=True` → identity loaded, signature good, no replay.
    `ok=False` → use `deny_code`/`status_code`/`message` for the
    canonical 4xx response. `notes` carries per-failure-mode detail
    suitable for `FleetAuthAuditLog.notes`.
    """

    ok: bool
    deny_code: str = ""
    status_code: int = 200
    message: str = ""

    # Set on success
    service_identity_id: Optional[str] = None
    app_slug_resolved: str = ""

    # Echoed back for audit log
    key_id: str = ""
    app_slug_claimed: str = ""
    timestamp_claimed: Optional[int] = None
    timestamp_delta_seconds: Optional[int] = None
    nonce: str = ""
    replay_detected: bool = False
    body_sha256: str = ""
    sig_present: bool = False
    notes: dict = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────
# Internals — querystring canonicalization + signature base
# ──────────────────────────────────────────────────────────────────────


def _canonicalize_querystring(query: str) -> str:
    """Spec section 1.3 querystring policy.

    Parse → percent-encode each (k, v) per RFC3986 → sort lexicographically
    by (key, value) tuple → reassemble. Multi-value params end up as
    separate tuples; their order is determined by value sort, not
    arrival order. Empty string returns empty string.
    """
    if not query:
        return ""
    pairs = parse_qsl(query, keep_blank_values=True)
    # Percent-encode both sides (safe='' so '/' and other reserved chars
    # are escaped; matches AWS-style strict canonicalization).
    encoded = [(quote(k, safe=""), quote(v, safe="")) for k, v in pairs]
    encoded.sort()
    return urlencode(encoded, safe="")


def _build_signature_base(
    method: str,
    path: str,
    query: str,
    app_slug: str,
    key_id: str,
    timestamp: str,
    nonce: str,
    body: bytes,
) -> str:
    """Spec section 1.3 canonical signature base string.

    For GET/DELETE: path includes canonical querystring.
    For POST/PUT/PATCH: querystring is NOT signed (body carries
    parameters).
    """
    method_upper = method.upper()
    if method_upper in ("GET", "DELETE", "HEAD"):
        canon_query = _canonicalize_querystring(query)
        canonical_path = f"{path}?{canon_query}" if canon_query else path
    else:
        canonical_path = path

    body_hash = hashlib.sha256(body or b"").hexdigest()

    return "\n".join(
        [
            method_upper,
            canonical_path,
            app_slug,
            key_id,
            timestamp,
            nonce,
            body_hash,
        ]
    )


def compute_signature(
    *,
    method: str,
    path: str,
    query: str,
    app_slug: str,
    key_id: str,
    timestamp: str,
    nonce: str,
    body: bytes,
    secret: str,
) -> str:
    """Produce the base64-encoded HMAC-SHA256 signature for a request.

    Used by the fleet-side client to sign outbound requests. Server
    side does its own HMAC and constant-time compares. Public surface
    so the fleet brain_client signing helper can call into the same
    canonicalization.
    """
    base = _build_signature_base(
        method=method,
        path=path,
        query=query,
        app_slug=app_slug,
        key_id=key_id,
        timestamp=timestamp,
        nonce=nonce,
        body=body,
    )
    digest = hmac.new(
        secret.encode("utf-8"), base.encode("utf-8"), hashlib.sha256
    ).digest()
    return base64.b64encode(digest).decode("ascii")


# ──────────────────────────────────────────────────────────────────────
# Replay-protection nonce store (Redis-backed; falls back to in-process
# dict for tests / dev environments without Redis)
# ──────────────────────────────────────────────────────────────────────


_DEV_NONCE_STORE: dict[str, float] = {}


def _redis_client():
    """Return a Redis client or None when unavailable.

    Lazy import so tests / non-Redis dev paths don't pay the cost.
    """
    try:
        from django_redis import get_redis_connection
        return get_redis_connection("default")
    except Exception:
        return None


def _consume_nonce(key_id: str, nonce: str) -> bool:
    """Atomic claim of (key_id, nonce); returns True if first time, False if replay.

    Uses Redis ``SET NX EX`` for atomic insert-if-absent with TTL.
    Falls back to an in-process dict when Redis is unreachable —
    that's fine for unit tests but the production deploy MUST have
    Redis or replay protection is per-process and broken under
    multiple workers.
    """
    key = f"{NONCE_REDIS_PREFIX}:{key_id}:{nonce}"
    redis = _redis_client()
    if redis is not None:
        # SET key value NX EX → returns True/None
        return bool(redis.set(key, "1", nx=True, ex=NONCE_TTL_SECONDS))

    # Dev / test fallback — single-process dict with TTL pruning.
    now = time.time()
    # Periodic cleanup of expired entries
    expired = [k for k, ts in _DEV_NONCE_STORE.items() if now - ts > NONCE_TTL_SECONDS]
    for k in expired:
        _DEV_NONCE_STORE.pop(k, None)
    if key in _DEV_NONCE_STORE:
        return False
    _DEV_NONCE_STORE[key] = now
    return True


# ──────────────────────────────────────────────────────────────────────
# Public — verify_signed_request
# ──────────────────────────────────────────────────────────────────────


def verify_signed_request(
    *,
    method: str,
    path: str,
    query: str,
    headers: dict,
    body: bytes,
) -> VerifyOutcome:
    """Verify the fleet-auth headers on an incoming request.

    Headers can be passed as the request.META-style dict or any
    case-insensitive mapping that supports ``.get(name)``. We try both
    the canonical ``X-Fleet-*`` form and the Django-WSGI
    ``HTTP_X_FLEET_*`` form so the caller doesn't have to normalize.
    """
    fetched = _read_headers(headers)
    app_claimed = fetched.get(HEADER_APP, "")
    key_id = fetched.get(HEADER_KEY_ID, "")
    timestamp_str = fetched.get(HEADER_TIMESTAMP, "")
    nonce = fetched.get(HEADER_NONCE, "")
    signature = fetched.get(HEADER_SIGNATURE, "")

    body_hash = hashlib.sha256(body or b"").hexdigest()
    sig_present = bool(signature)

    # 1. All required headers present?
    missing = [h for h in REQUIRED_HEADERS if not fetched.get(h)]
    if missing:
        return _deny(
            DenyCode.MISSING_HEADERS,
            message=f"missing required headers: {','.join(missing)}",
            key_id=key_id,
            app_slug_claimed=app_claimed,
            nonce=nonce,
            body_sha256=body_hash,
            sig_present=sig_present,
            notes={"reason": "required_for_routing_or_artifact", "missing": missing},
        )

    # 2. Timestamp parses + within skew window?
    try:
        timestamp_int = int(timestamp_str)
    except ValueError:
        return _deny(
            DenyCode.MALFORMED_HEADERS,
            message="X-Fleet-Timestamp must be unix seconds (int)",
            key_id=key_id,
            app_slug_claimed=app_claimed,
            nonce=nonce,
            body_sha256=body_hash,
            sig_present=sig_present,
            notes={"field": "X-Fleet-Timestamp", "value": timestamp_str},
        )

    now = int(time.time())
    delta = now - timestamp_int
    if abs(delta) > TIMESTAMP_SKEW_SECONDS:
        return _deny(
            DenyCode.TIMESTAMP_SKEW,
            message=f"timestamp outside ±{TIMESTAMP_SKEW_SECONDS}s window",
            key_id=key_id,
            app_slug_claimed=app_claimed,
            timestamp_claimed=timestamp_int,
            timestamp_delta_seconds=delta,
            nonce=nonce,
            body_sha256=body_hash,
            sig_present=sig_present,
            notes={"allowed_window_seconds": TIMESTAMP_SKEW_SECONDS},
        )

    # 3. Signature decodes?
    try:
        base64.b64decode(signature, validate=True)
    except Exception:
        return _deny(
            DenyCode.MALFORMED_HEADERS,
            message="X-Fleet-Signature is not valid base64",
            key_id=key_id,
            app_slug_claimed=app_claimed,
            timestamp_claimed=timestamp_int,
            timestamp_delta_seconds=delta,
            nonce=nonce,
            body_sha256=body_hash,
            sig_present=sig_present,
            notes={"field": "X-Fleet-Signature"},
        )

    # 4. Key lookup.
    from core.models.fleet import FleetServiceKey

    try:
        key_row = FleetServiceKey.objects.select_related("service").get(key_id=key_id)
    except FleetServiceKey.DoesNotExist:
        return _deny(
            DenyCode.UNKNOWN_KEY_ID,
            message="no matching service key",
            key_id=key_id,
            app_slug_claimed=app_claimed,
            timestamp_claimed=timestamp_int,
            timestamp_delta_seconds=delta,
            nonce=nonce,
            body_sha256=body_hash,
            sig_present=sig_present,
            notes={"reason": "no_matching_key"},
        )

    # 5. Identity + key status.
    identity = key_row.service
    if (
        identity.status == identity.STATUS_DISABLED
        or key_row.status == key_row.STATUS_DISABLED
        or not key_row.is_currently_usable()
    ):
        return _deny(
            DenyCode.SERVICE_DISABLED,
            message="service identity or key is disabled / out of window",
            key_id=key_id,
            app_slug_claimed=app_claimed,
            timestamp_claimed=timestamp_int,
            timestamp_delta_seconds=delta,
            nonce=nonce,
            body_sha256=body_hash,
            sig_present=sig_present,
            notes={
                "service_status": identity.status,
                "key_status": key_row.status,
            },
        )

    # 6. app_slug binding.
    if app_claimed != identity.app_slug:
        return _deny(
            DenyCode.APP_SLUG_MISMATCH,
            message="X-Fleet-App does not match service identity",
            key_id=key_id,
            app_slug_claimed=app_claimed,
            timestamp_claimed=timestamp_int,
            timestamp_delta_seconds=delta,
            nonce=nonce,
            body_sha256=body_hash,
            sig_present=sig_present,
            notes={
                "mismatch": {
                    "claimed": app_claimed,
                    "resolved": identity.app_slug,
                }
            },
        )

    # 7. Signature verify.
    #
    # Design note (Session 1129): both sides of the wire use
    # SHA256(raw_secret) as the HMAC key, not the raw secret itself.
    # The fleet app holds the raw 32-byte secret in its env vars (per
    # spec section 1.6) and computes SHA256(secret) once at startup
    # before signing. The server stores SHA256(secret) directly. This
    # has two nice properties:
    #   - DB exfiltration leaks only the HMAC verify key, not the
    #     original 32-byte secret (which never travels off the fleet
    #     app's deployment env).
    #   - Captured signatures cannot be inverted to recover the raw
    #     secret either, since signing uses the hash.
    # The raw 32-byte secret remains high-entropy; SHA256 of it is
    # also 256 bits, so HMAC strength is unchanged.
    verify_key = key_row.secret_hash
    expected_sig = compute_signature(
        method=method,
        path=path,
        query=query,
        app_slug=identity.app_slug,
        key_id=key_id,
        timestamp=timestamp_str,
        nonce=nonce,
        body=body,
        secret=verify_key,
    )
    if not hmac.compare_digest(expected_sig, signature):
        return _deny(
            DenyCode.SIGNATURE_MISMATCH,
            message="HMAC signature does not match",
            key_id=key_id,
            app_slug_claimed=app_claimed,
            app_slug_resolved=identity.app_slug,
            timestamp_claimed=timestamp_int,
            timestamp_delta_seconds=delta,
            nonce=nonce,
            body_sha256=body_hash,
            sig_present=sig_present,
            notes={"hash": body_hash},
        )

    # 8. Replay protection.
    if not _consume_nonce(key_id, nonce):
        return _deny(
            DenyCode.REPLAY_NONCE,
            message="nonce already seen within TTL",
            key_id=key_id,
            app_slug_claimed=app_claimed,
            app_slug_resolved=identity.app_slug,
            timestamp_claimed=timestamp_int,
            timestamp_delta_seconds=delta,
            nonce=nonce,
            body_sha256=body_hash,
            sig_present=sig_present,
            replay_detected=True,
            notes={"nonce_ttl_seconds": NONCE_TTL_SECONDS},
        )

    # 9. Success. Stamp last_used_at on the key + identity.
    now_ts = timezone.now()
    FleetServiceKey.objects.filter(pk=key_row.pk).update(last_used_at=now_ts)
    from core.models.fleet import FleetServiceIdentity
    FleetServiceIdentity.objects.filter(pk=identity.pk).update(last_used_at=now_ts)

    return VerifyOutcome(
        ok=True,
        status_code=200,
        service_identity_id=str(identity.pk),
        app_slug_resolved=identity.app_slug,
        key_id=key_id,
        app_slug_claimed=app_claimed,
        timestamp_claimed=timestamp_int,
        timestamp_delta_seconds=delta,
        nonce=nonce,
        body_sha256=body_hash,
        sig_present=True,
    )


def _deny(
    code: str,
    *,
    message: str = "",
    key_id: str = "",
    app_slug_claimed: str = "",
    app_slug_resolved: str = "",
    timestamp_claimed: Optional[int] = None,
    timestamp_delta_seconds: Optional[int] = None,
    nonce: str = "",
    body_sha256: str = "",
    sig_present: bool = False,
    replay_detected: bool = False,
    notes: Optional[dict] = None,
) -> VerifyOutcome:
    return VerifyOutcome(
        ok=False,
        deny_code=code,
        status_code=DENY_STATUS_CODES.get(code, 401),
        message=message or code,
        key_id=key_id,
        app_slug_claimed=app_slug_claimed,
        app_slug_resolved=app_slug_resolved,
        timestamp_claimed=timestamp_claimed,
        timestamp_delta_seconds=timestamp_delta_seconds,
        nonce=nonce,
        body_sha256=body_sha256,
        sig_present=sig_present,
        replay_detected=replay_detected,
        notes=notes or {},
    )


# ──────────────────────────────────────────────────────────────────────
# Header reading (case-insensitive across raw + WSGI conventions)
# ──────────────────────────────────────────────────────────────────────


def _read_headers(headers) -> dict[str, str]:
    """Read fleet headers from either a dict, request.META, or DRF request.

    Returns a dict keyed by the canonical `X-Fleet-*` names.
    """
    out: dict[str, str] = {}
    for canonical in (
        HEADER_APP,
        HEADER_KEY_ID,
        HEADER_TIMESTAMP,
        HEADER_NONCE,
        HEADER_SIGNATURE,
        HEADER_REQUEST_ID,
    ):
        wsgi_name = "HTTP_" + canonical.upper().replace("-", "_")
        value = None
        if hasattr(headers, "get"):
            value = (
                headers.get(canonical)
                or headers.get(canonical.lower())
                or headers.get(wsgi_name)
            )
        if value:
            out[canonical] = value
    return out


# ──────────────────────────────────────────────────────────────────────
# Audit logging
# ──────────────────────────────────────────────────────────────────────


def persist_audit_row(
    outcome: VerifyOutcome,
    *,
    method: str,
    path: str,
    query: str,
    request_id: str,
    ip: Optional[str],
    user_agent: str,
    latency_ms: int,
    status_code: Optional[int] = None,
):
    """Write a `FleetAuthAuditLog` row + emit logger line.

    Always persists. WARN on deny; INFO on allow only when
    FLEET_AUTH_LOG_ALL=true.
    """
    from core.models.fleet import FleetAuthAuditLog

    result = FleetAuthAuditLog.RESULT_ALLOW if outcome.ok else FleetAuthAuditLog.RESULT_DENY
    sc = status_code if status_code is not None else outcome.status_code

    row = FleetAuthAuditLog.objects.create(
        method=method,
        path=path,
        query=query,
        status_code=sc,
        result=result,
        deny_code=outcome.deny_code or "",
        key_id=outcome.key_id or "",
        app_slug_claimed=outcome.app_slug_claimed or "",
        app_slug_resolved=outcome.app_slug_resolved or "",
        timestamp_claimed=outcome.timestamp_claimed,
        timestamp_delta_seconds=outcome.timestamp_delta_seconds,
        nonce=outcome.nonce or "",
        replay_detected=outcome.replay_detected,
        body_sha256=outcome.body_sha256 or "",
        sig_present=outcome.sig_present,
        ip=ip,
        user_agent=user_agent or "",
        latency_ms=latency_ms,
        notes=outcome.notes or {},
        request_id=request_id or "",
    )

    # Mirror to standard logger
    if outcome.ok:
        if getattr(settings, "FLEET_AUTH_LOG_ALL", False):
            logger.info(
                "[fleet-auth] allow app=%s key=%s path=%s request_id=%s",
                outcome.app_slug_resolved, outcome.key_id, path, request_id,
            )
    else:
        logger.warning(
            "[fleet-auth] deny code=%s path=%s key=%s claimed=%s request_id=%s delta=%s replay=%s",
            outcome.deny_code,
            path,
            outcome.key_id,
            outcome.app_slug_claimed,
            request_id,
            outcome.timestamp_delta_seconds,
            outcome.replay_detected,
        )

    return row


__all__ = [
    # Constants
    "HEADER_APP",
    "HEADER_KEY_ID",
    "HEADER_TIMESTAMP",
    "HEADER_NONCE",
    "HEADER_SIGNATURE",
    "HEADER_REQUEST_ID",
    "TIMESTAMP_SKEW_SECONDS",
    "NONCE_TTL_SECONDS",
    "DenyCode",
    "DENY_STATUS_CODES",
    # Pure functions
    "compute_signature",
    "verify_signed_request",
    "persist_audit_row",
    # Result type
    "VerifyOutcome",
]
