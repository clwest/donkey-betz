"""Warn-only audit helper for PA-chat auth posture (Session 1132 B-scaffold).

Records one `FleetPAChatAuditRow` per `/api/pa/chat/` request so we
can measure how many fleet apps are still bearer-only before flipping
enforcement.

Rigby's lock (conversation pa-d19c1674b936, Session 1132):
    1) Use the EXISTING fleet HMAC signature path
       (FleetSignatureAuthentication, Session 1129 Move 1) as the
       canonical app_slug binding mechanism — no new bearer-token
       scheme.
    2) Add this audit layer to measure rollout progress.
    3) Do NOT enforce anything in this phase — every value is
       purely for visibility. Reject-mode waits for back-prop of
       HMAC signing to all 7 fleet apps + a future session.

The helper is intentionally cheap: one INSERT per PA chat call, no
upstream blocking. Wrap the call in try/except in the caller so an
audit-write failure can never prevent a chat from going through.
"""
from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def _client_ip_from_request(request) -> Optional[str]:
    """Best-effort client-IP extraction. Honors X-Forwarded-For first."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "") or ""
    if xff:
        # First entry is the original client per RFC 7239 conventions.
        # Strip + validate; if it looks invalid, fall through to REMOTE_ADDR.
        candidate = xff.split(",")[0].strip()
        if candidate:
            return candidate
    return request.META.get("REMOTE_ADDR") or None


def _classify_auth_mode(request, fleet_identity, user) -> str:
    """Categorize the auth path the request actually took.

    Order matches the @authentication_classes precedence in
    unified_pa_chat (fleet signature → session → token). When more
    than one applies, the strongest binding wins for classification
    purposes (fleet_signature beats session).

    Classification reads the Authorization header directly when
    present rather than relying on `successful_authenticator` —
    Django's session middleware can create an anonymous session for
    any request, which then satisfies SessionAuthentication's
    "successful" check even when the caller was using a token. The
    header is the ground truth of what the CLIENT actually sent.
    """
    from core.models.fleet import FleetPAChatAuditRow

    if fleet_identity is not None:
        return FleetPAChatAuditRow.AUTH_MODE_FLEET_SIGNATURE

    # Read the Authorization header before falling back to DRF's
    # post-auth classification. `Token ...` and `Bearer ...` both
    # signal a service/user-token request from a fleet app or API
    # consumer — this is the "bearer-only" bucket we want to measure.
    auth_header = (request.META.get("HTTP_AUTHORIZATION", "") or "").strip()
    if auth_header:
        if auth_header.lower().startswith(("token ", "bearer ")):
            # Distinguish fleet-service tokens from user tokens by
            # whether the auth produced an authenticated user. Fleet
            # apps use a shared service-user token which DRF still
            # resolves to a user; we put them in the same
            # bearer_only bucket so the metric reads "how many PA
            # chat calls came in with bearer auth but no fleet
            # signature."
            return FleetPAChatAuditRow.AUTH_MODE_BEARER_ONLY

    # No Authorization header — categorize by whatever auth got us here.
    if user is not None and getattr(user, "is_authenticated", False):
        authenticator = getattr(request, "successful_authenticator", None)
        if authenticator is not None:
            authenticator_name = authenticator.__class__.__name__
            if "Token" in authenticator_name:
                return FleetPAChatAuditRow.AUTH_MODE_API_USER_TOKEN
            if "Session" in authenticator_name:
                return FleetPAChatAuditRow.AUTH_MODE_SESSION_USER
        # Authenticated but we can't tell how — bucket as session_user
        # (the most common non-token path for the web UI).
        return FleetPAChatAuditRow.AUTH_MODE_SESSION_USER

    return FleetPAChatAuditRow.AUTH_MODE_ANONYMOUS


def _extract_claimed_app_slug(request) -> str:
    """Pull the body's claimed app_slug from either routing or context.

    Returns empty string if no claim was made. We check both common
    locations — `routing.app_slug` for explicit fleet routing requests
    and `context.app_slug` for the legacy brain_bridge shape.
    """
    data = getattr(request, "data", None) or {}
    if not isinstance(data, dict):
        return ""
    routing = data.get("routing") or {}
    if isinstance(routing, dict):
        claim = routing.get("app_slug")
        if claim:
            return str(claim)
    context = data.get("context") or {}
    if isinstance(context, dict):
        claim = context.get("app_slug")
        if claim:
            return str(claim)
    return ""


def write_pa_chat_audit(request) -> None:
    """Record one FleetPAChatAuditRow for the current PA chat request.

    Safe to call inside a view: failure is logged + swallowed so a
    DB hiccup can't break PA chat. The caller is expected to wrap in
    try/except as belt-and-suspenders.

    Idempotency note: each PA chat call writes exactly one audit row.
    This is intentional — we want a count of REQUESTS by auth mode,
    not a count of UNIQUE callers.
    """
    try:
        from core.models.fleet import FleetPAChatAuditRow

        fleet_identity = getattr(request, "fleet_identity", None)
        user = getattr(request, "user", None)

        auth_mode = _classify_auth_mode(request, fleet_identity, user)
        # FleetSignatureAuthentication stores `request.fleet_identity`
        # as a dict, NOT an ORM object — `{"app_slug": ..., "key_id":
        # ..., "service_identity_id": ...}` from core/services/
        # fleet_auth_drf.py:142. Use `.get()`, not `getattr`.
        if isinstance(fleet_identity, dict):
            verified_app_slug = str(fleet_identity.get("app_slug") or "")
        elif fleet_identity is not None:
            # Forward-compatible fallback if the contract changes to an
            # ORM-object some day.
            verified_app_slug = str(getattr(fleet_identity, "app_slug", "") or "")
        else:
            verified_app_slug = ""
        claimed_app_slug = _extract_claimed_app_slug(request)

        # NULL when either side is missing — we don't conflate "no
        # claim" with "mismatched claim".
        match: Optional[bool] = None
        if verified_app_slug and claimed_app_slug:
            match = (verified_app_slug == claimed_app_slug)

        FleetPAChatAuditRow.objects.create(
            auth_mode=auth_mode,
            has_fleet_identity=fleet_identity is not None,
            verified_app_slug=verified_app_slug or "",
            claimed_app_slug=claimed_app_slug or "",
            match=match,
            request_path=(request.path or "")[:200],
            remote_addr=_client_ip_from_request(request),
            user_agent=(request.META.get("HTTP_USER_AGENT", "") or "")[:500],
            request_id=(request.META.get("HTTP_X_REQUEST_ID", "") or "")[:64],
        )

        # Loud-log mismatches and bearer-only claims so they show up
        # in operational dashboards too, not just the DB. Quiet on the
        # happy path (signed + matching) so the log doesn't get noisy
        # once back-prop completes.
        if match is False:
            logger.warning(
                "[pa-chat-audit] app_slug claim MISMATCH "
                "verified=%s claimed=%s auth_mode=%s path=%s",
                verified_app_slug, claimed_app_slug, auth_mode, request.path,
            )
        elif auth_mode == FleetPAChatAuditRow.AUTH_MODE_BEARER_ONLY and claimed_app_slug:
            logger.info(
                "[pa-chat-audit] bearer-only with app_slug claim "
                "claimed=%s path=%s — fleet app should switch to "
                "HMAC signing",
                claimed_app_slug, request.path,
            )
    except Exception as e:  # pragma: no cover
        logger.warning(
            "[pa-chat-audit] write failed (request continues): %s", e,
        )


__all__ = [
    "write_pa_chat_audit",
]
