"""Fleet paid-interest submission endpoint (Session 1138).

Implements `docs/specs/SIGNAL_STUDIO_PAID_INTEREST_SIGNAL_SPEC.md`
with the URL + table rename to fleet-generic naming (so future
Decision-13-style demand-gates on SellerPilot / ComplianceSentinel
etc reuse the same surface).

- `POST /api/fleet/paid-interest/` — record a paid-interest signal

Auth: fleet HMAC signature required (FleetSignatureRequired). The
caller's `app_slug` is taken from the verified identity, NOT from
the request body. Any body field claiming an app_slug is ignored.

Server-side dedup: (app_slug, email lowercased, use_case casefolded)
within the last 7 days returns the existing row's id with a `deduped`
flag. This is a safety net — the calling fleet app already does
per-IP rate-limit + email dedup before sending; u-d-b enforces dedup
again so spam-via-many-IPs can't blow up the table.

No capability gate in v1 — any fleet identity with a valid signature
can submit. If we need to lock this down later (e.g. only signal-studio
can submit), add an allowlist on the view side or an
`paid_interest.can_submit` capability on the identity.
"""
from __future__ import annotations

import logging
import re
import time
from datetime import timedelta
from typing import Optional

from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response

from core.models.fleet import FleetPaidInterest, FleetServiceIdentity
from core.services.fleet_auth import persist_audit_row
from core.services.fleet_auth_drf import (
    FleetSignatureExclusiveAuthentication,
    FleetSignatureRequired,
)

logger = logging.getLogger(__name__)


# Dedup window — Decision 13 spec calls for 7 days. Configurable via
# settings later if we need to tune.
DEDUP_WINDOW_DAYS = 7

# Loose email regex — full RFC 5322 is overkill for a notify-me form.
# Calling fleet app should do real validation before reaching here.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Accept the spec's workspace-size strings exactly.
_VALID_WORKSPACE_SIZES = {"solo", "2-5", "6-20", "20+"}

# RFC 2606 reserved domains + IANA test TLDs. Submissions targeting
# these are guaranteed-not-production by spec and get auto-flagged
# is_test_data=True so they don't contaminate the Decision 13 gate.
#
# RFC 2606 reserves the example.{com,org,net} domains and ALL their
# subdomains for documentation/testing — so user@mail.example.com also
# counts. The bare `@example` form covers the bare reserved TLD.
_TEST_EMAIL_DIRECT_SUFFIXES = (
    "@example.com",
    "@example.org",
    "@example.net",
    "@example",
    ".test",
    ".invalid",
    ".localhost",
)
_TEST_EMAIL_SUBDOMAIN_SUFFIXES = (
    ".example.com",
    ".example.org",
    ".example.net",
)
# Public constant kept stable for callers that need to introspect the
# direct-match list (e.g. test assertions). Subdomain rules are part of
# the function contract, not the constant.
_TEST_EMAIL_SUFFIXES = _TEST_EMAIL_DIRECT_SUFFIXES


def _looks_like_test_email(email_lc: str) -> bool:
    """Return True when ``email_lc`` is in an RFC 2606 reserved test domain.

    Matches:
        - Direct: ``@example.com``, ``@example.org``, ``@example.net``,
          ``@example``, and any address ending in ``.test`` / ``.invalid`` /
          ``.localhost`` TLDs.
        - Subdomain: any address ending in ``.example.com``, ``.example.org``,
          ``.example.net`` (RFC 2606 reserves all subdomains too).

    Caller must lowercase first (storage email is already lowercased).
    """
    if any(email_lc.endswith(suffix) for suffix in _TEST_EMAIL_DIRECT_SUFFIXES):
        return True
    return any(email_lc.endswith(suffix) for suffix in _TEST_EMAIL_SUBDOMAIN_SUFFIXES)


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────


def _client_ip(request) -> Optional[str]:
    return (
        request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
        or request.META.get("REMOTE_ADDR")
        or None
    )


def _normalize_use_case(s: str) -> str:
    """Casefold + collapse whitespace for dedup comparison."""
    return " ".join(s.casefold().split())


# ──────────────────────────────────────────────────────────────────────
# POST /api/fleet/paid-interest/ — submit
# ──────────────────────────────────────────────────────────────────────


@csrf_exempt
@api_view(["POST"])
@authentication_classes([FleetSignatureExclusiveAuthentication])
@permission_classes([FleetSignatureRequired])
def fleet_paid_interest_submit(request):
    """POST /api/fleet/paid-interest/ — record a paid-interest signal.

    Request JSON:
        {
            "email":          "user@example.com",   # required
            "use_case":       "short text",         # required, ≤140 chars
            "willing_pay":    49,                   # optional, positive int
            "workspace_size": "solo",               # optional choice
            "user_id_claim":  "..."                 # optional fleet-app user id
        }

    Response 201 (new row):
        {
            "id": "<uuid>",
            "deduped": false,
            "message": "captured"
        }

    Response 200 (deduped):
        {
            "id": "<existing-uuid>",
            "deduped": true,
            "message": "already_captured"
        }

    Response 400: validation error
    Response 401: missing / invalid fleet signature
    """
    start_ms = time.monotonic()

    # Resolve the verified identity. FleetSignatureRequired already
    # ensured request.fleet_identity is populated.
    identity_payload = getattr(request, "fleet_identity", None) or {}
    try:
        identity = FleetServiceIdentity.objects.get(
            pk=identity_payload["service_identity_id"]
        )
    except (FleetServiceIdentity.DoesNotExist, KeyError):
        return Response(
            {
                "error": {
                    "code": "unknown_identity",
                    "message": "verified identity row no longer exists",
                }
            },
            status=401,
        )

    app_slug = identity.app_slug
    body = request.data or {}

    # ── Validation ────────────────────────────────────────────────────
    email_raw = (body.get("email") or "").strip()
    use_case_raw = (body.get("use_case") or "").strip()
    willing_pay_raw = body.get("willing_pay")
    workspace_size_raw = (body.get("workspace_size") or "").strip()
    user_id_claim_raw = (body.get("user_id_claim") or "").strip()

    if not email_raw:
        return Response(
            {"error": {"code": "missing_email", "message": "email is required"}},
            status=400,
        )
    if not _EMAIL_RE.match(email_raw):
        return Response(
            {"error": {"code": "invalid_email", "message": "email is not well-formed"}},
            status=400,
        )
    if not use_case_raw:
        return Response(
            {"error": {"code": "missing_use_case", "message": "use_case is required"}},
            status=400,
        )
    if len(use_case_raw) > 140:
        return Response(
            {
                "error": {
                    "code": "use_case_too_long",
                    "message": "use_case must be ≤140 characters",
                    "length": len(use_case_raw),
                }
            },
            status=400,
        )

    willing_pay_clean: Optional[int] = None
    if willing_pay_raw not in (None, ""):
        try:
            willing_pay_clean = int(willing_pay_raw)
        except (TypeError, ValueError):
            return Response(
                {
                    "error": {
                        "code": "invalid_willing_pay",
                        "message": "willing_pay must be an integer",
                    }
                },
                status=400,
            )
        if willing_pay_clean < 0:
            return Response(
                {
                    "error": {
                        "code": "invalid_willing_pay",
                        "message": "willing_pay must be >= 0",
                    }
                },
                status=400,
            )

    if workspace_size_raw and workspace_size_raw not in _VALID_WORKSPACE_SIZES:
        return Response(
            {
                "error": {
                    "code": "invalid_workspace_size",
                    "message": (
                        f"workspace_size must be one of "
                        f"{sorted(_VALID_WORKSPACE_SIZES)}"
                    ),
                }
            },
            status=400,
        )

    email_lc = email_raw.lower()

    # ── Dedup ─────────────────────────────────────────────────────────
    # Same (app_slug, email_lc) within the last DEDUP_WINDOW_DAYS, and
    # the *normalized* use_case matches → no-op, return existing.
    cutoff = timezone.now() - timedelta(days=DEDUP_WINDOW_DAYS)
    use_case_norm = _normalize_use_case(use_case_raw)
    recent = (
        FleetPaidInterest.objects
        .filter(app_slug=app_slug, email=email_lc, created_at__gte=cutoff)
        .only("id", "use_case")
        .order_by("-created_at")
    )
    for row in recent[:25]:
        if _normalize_use_case(row.use_case) == use_case_norm:
            logger.info(
                "[paid-interest] deduped app=%s email=%s row=%s",
                app_slug, email_lc, row.id,
            )
            return Response(
                {
                    "id": str(row.id),
                    "deduped": True,
                    "message": "already_captured",
                },
                status=200,
            )

    # ── Persist ───────────────────────────────────────────────────────
    is_test_data = _looks_like_test_email(email_lc)
    row = FleetPaidInterest.objects.create(
        app_slug=app_slug,
        email=email_lc,
        use_case=use_case_raw,
        willing_pay=willing_pay_clean,
        workspace_size=workspace_size_raw or "",
        user_id_claim=user_id_claim_raw or "",
        submitted_by_identity=identity,
        submitted_by_key_id=identity_payload.get("key_id", "") or "",
        request_id=request.META.get("HTTP_X_REQUEST_ID", "") or "",
        is_test_data=is_test_data,
    )

    logger.info(
        "[paid-interest] captured app=%s email=%s pay=%s row=%s test=%s",
        app_slug, email_lc, willing_pay_clean, row.id, is_test_data,
    )

    # Audit row — fleet_auth already wrote one on the auth path; we don't
    # double-write here. The latency_ms on the auth-side row covers the
    # full request because persist_audit_row is called pre-view by DRF
    # auth class. Nothing else to do.
    _ = start_ms  # kept for symmetry / future timing

    return Response(
        {
            "id": str(row.id),
            "deduped": False,
            "message": "captured",
        },
        status=201,
    )


__all__ = ["fleet_paid_interest_submit"]
