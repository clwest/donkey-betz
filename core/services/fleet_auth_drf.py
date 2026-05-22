"""DRF authentication + permission classes for fleet signed requests.

Thin shims over `core.services.fleet_auth.verify_signed_request()` so
DRF views can opt into fleet auth via standard `authentication_classes`
and `permission_classes` lists. Designed for two patterns:

1. **Fleet-only endpoints** (artifact push/pull, eventually):
   ```python
   @api_view(["POST"])
   @authentication_classes([SessionAuthentication, FleetSignatureAuthentication])
   @permission_classes([FleetSignatureRequired])
   def push_artifact(request):
       ...
   ```
   The auth class populates `request.fleet_identity`. The permission
   class enforces `request.fleet_identity is not None`.

2. **Hybrid endpoints** (`/api/pa/chat/` — works with user auth alone,
   gates routing-block enforcement on fleet auth):
   ```python
   @api_view(["POST"])
   @authentication_classes([
       SessionAuthentication, TokenAuthentication,
       FleetSignatureAuthentication,
   ])
   @permission_classes([IsAuthenticated])
   def unified_pa_chat(request):
       if request.fleet_identity:
           # routing block is honored
       else:
           # any routing block in the body is stripped
   ```

The auth class is designed to NEVER raise — it logs the deny and
returns `None` (treating absence-of-fleet-auth as "no fleet identity"
rather than "auth failure"). That lets unsigned user-auth requests
keep working. For fleet-only endpoints, the **permission class** is
what enforces fleet auth.

Read the body via `request._request.body` (raw bytes) so signature
verification happens before any `request.data` parsing. The first
call to `request.data` would consume the stream; we want to avoid
that.
"""
from __future__ import annotations

import logging
import time
import uuid
from typing import Optional

from django.utils import timezone
from rest_framework import authentication, exceptions, permissions

from core.services.fleet_auth import (
    HEADER_REQUEST_ID,
    DenyCode,
    persist_audit_row,
    verify_signed_request,
)

logger = logging.getLogger(__name__)


class FleetSignatureAuthentication(authentication.BaseAuthentication):
    """DRF authentication class for fleet-signed requests.

    Behavior:
    - If NO fleet headers are present: return None (let other auth
      classes handle the request).
    - If fleet headers are present but invalid: persist audit row,
      return None (request will fail at the permission layer if fleet
      auth is required; otherwise it falls back to user auth).
    - If valid: persist audit row (allow), populate
      `request.fleet_identity` with the verify outcome dict, return
      a 2-tuple per DRF contract.

    Critical: we DO NOT raise on signature failure. Raising would
    block hybrid endpoints (`/api/pa/chat/`) from accepting user-auth
    requests that don't carry fleet headers. Fleet-only endpoints
    enforce auth via `FleetSignatureRequired` permission instead.
    """

    def authenticate(self, request):
        # If no fleet headers at all → bail silently (None).
        meta = request.META
        has_any_fleet_header = any(
            meta.get("HTTP_" + h.upper().replace("-", "_"))
            for h in ("X-Fleet-App", "X-Fleet-Key-Id", "X-Fleet-Signature")
        )
        if not has_any_fleet_header:
            return None

        start_ms = time.monotonic()
        # Read RAW body bytes before anything else touches `request.data`.
        raw_body = request._request.body
        path = request._request.path
        query = request._request.META.get("QUERY_STRING", "") or ""
        method = request._request.method
        request_id = (
            meta.get("HTTP_" + HEADER_REQUEST_ID.upper().replace("-", "_"))
            or uuid.uuid4().hex
        )

        outcome = verify_signed_request(
            method=method,
            path=path,
            query=query,
            headers=meta,
            body=raw_body,
        )

        # Persist audit row regardless of outcome.
        try:
            persist_audit_row(
                outcome,
                method=method,
                path=path,
                query=query,
                request_id=request_id,
                ip=_client_ip(request),
                user_agent=meta.get("HTTP_USER_AGENT", ""),
                latency_ms=int((time.monotonic() - start_ms) * 1000),
            )
        except Exception as e:  # pragma: no cover - audit must never block
            logger.exception(f"[fleet-auth] audit row persist failed: {e}")

        if not outcome.ok:
            # Stash the outcome so view code (or permission class) can
            # inspect why fleet auth was rejected.
            request.fleet_identity = None
            request._fleet_auth_outcome = outcome
            return None

        # Success: build the per-request identity payload.
        request.fleet_identity = {
            "app_slug": outcome.app_slug_resolved,
            "key_id": outcome.key_id,
            "service_identity_id": outcome.service_identity_id,
            "request_id": request_id,
            "verified_at": timezone.now().isoformat(),
        }
        request._fleet_auth_outcome = outcome

        # DRF wants (user, auth) — we don't author a Django user; just
        # mark the request as authenticated by fleet by returning a
        # truthy sentinel. The actual permission gating happens via
        # FleetSignatureRequired or hybrid view code.
        return (FleetServicePrincipal(outcome.app_slug_resolved), outcome.key_id)


class FleetServicePrincipal:
    """Lightweight stand-in for `request.user` when only fleet auth ran.

    We deliberately don't return a Django User model — fleet identities
    are services, not humans. Anything that needs `request.user` should
    use `request.fleet_identity` instead, OR a Django user that came
    from a separate auth class. Implements the bare DRF contract so
    `request.user.is_authenticated` reads as True.
    """

    is_authenticated = True
    is_anonymous = False

    def __init__(self, app_slug: str):
        self.app_slug = app_slug
        self.username = f"fleet:{app_slug}"
        self.pk = None
        self.id = None

    def __str__(self) -> str:
        return self.username


class FleetSignatureRequired(permissions.BasePermission):
    """Reject requests that lack a verified fleet identity.

    Use this on fleet-only endpoints (artifact push/pull). For hybrid
    endpoints, check `request.fleet_identity` inline instead — that
    pattern keeps user-auth requests working while gating routing
    enforcement.
    """

    message = "Valid fleet service signature required"

    def has_permission(self, request, view) -> bool:
        identity = getattr(request, "fleet_identity", None)
        if identity:
            return True

        # Build a structured 403 message using the verify outcome (if
        # the request even attempted fleet auth).
        outcome = getattr(request, "_fleet_auth_outcome", None)
        if outcome is not None and outcome.deny_code:
            self.message = {
                "error": {
                    "code": outcome.deny_code,
                    "message": outcome.message,
                    "request_id": "",
                    "app_slug_claimed": outcome.app_slug_claimed,
                    "key_id": outcome.key_id,
                }
            }
        else:
            self.message = {
                "error": {
                    "code": DenyCode.MISSING_HEADERS,
                    "message": "Fleet service signature required",
                }
            }
        return False


class FleetCapabilityRequired(permissions.BasePermission):
    """Require a specific capability on the calling fleet identity.

    Usage:
        class MyView(APIView):
            authentication_classes = [FleetSignatureAuthentication]
            permission_classes = [
                FleetSignatureRequired,
                FleetCapabilityRequired.for_capability("artifacts", "can_push"),
            ]
    """

    capability_path: tuple = ()

    @classmethod
    def for_capability(cls, *path: str):
        """Build a subclass keyed to a specific capability path."""

        class _Bound(cls):
            capability_path = tuple(path)
            message = {
                "error": {
                    "code": DenyCode.CAPABILITY_DENIED,
                    "message": f"capability required: {'.'.join(path)}",
                }
            }

        _Bound.__name__ = f"FleetCapability_{'_'.join(path)}"
        return _Bound

    def has_permission(self, request, view) -> bool:
        identity = getattr(request, "fleet_identity", None)
        if not identity:
            return False

        # Pull the live service identity to check capability.
        from core.models.fleet import FleetServiceIdentity

        try:
            row = FleetServiceIdentity.objects.get(
                pk=identity["service_identity_id"]
            )
        except FleetServiceIdentity.DoesNotExist:
            return False

        if not self.capability_path:
            return True
        return bool(row.capability(*self.capability_path, default=False))


def _client_ip(request) -> Optional[str]:
    """Best-effort client IP extraction from DRF request."""
    meta = request.META
    xff = meta.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        # First IP in the chain is the original client
        return xff.split(",")[0].strip() or None
    return meta.get("REMOTE_ADDR") or None


__all__ = [
    "FleetSignatureAuthentication",
    "FleetSignatureRequired",
    "FleetCapabilityRequired",
    "FleetServicePrincipal",
]
