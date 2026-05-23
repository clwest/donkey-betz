"""Fleet artifact push + pull endpoints (Move 2 Round 1 MLC).

Implements the minimum lovable contract from
`docs/specs/FLEET_MOVE_1_AND_2_SPEC.md` section 2 + Rigby's Round 1
MLC carve-out:

- `POST /api/fleet/artifacts/` — create a new artifact
- `GET /api/fleet/artifacts/<id>/` — fetch one (creator's app_slug only)

Both endpoints REQUIRE a valid fleet signature. Unlike `/api/pa/chat/`
(which is hybrid — works with user auth alone, gates only the routing
block), these are fleet-only. Missing / invalid / replayed signatures
get hard 401/403 per the spec.

Capability gates:
- POST requires `artifacts.can_push=true` on the identity
- GET requires `artifacts.can_pull=true`
- POST enforces `max_payload_kb` from capabilities (default 512 KB)

Ownership rule (Move 2 Round 1):
- Only the **creator's app_slug** can pull. Same app_slug + different
  key (via rotation) → still allowed. Different app_slug → 403.

Future rounds add: list+filter, versioning, provenance, cross-app
visibility (gated by separate `artifacts.can_cross_app` capability).
"""
from __future__ import annotations

import json
import logging
import uuid

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from core.models.fleet import (
    FleetArtifact,
    FleetServiceIdentity,
    compute_payload_sha256,
)
from core.services.fleet_auth import DenyCode
from core.services.fleet_auth_drf import (
    FleetSignatureExclusiveAuthentication,
    FleetSignatureRequired,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────
# Capability permission classes (inline — only used by these two views)
# ──────────────────────────────────────────────────────────────────────


def _capability_check(request, *path: str) -> Response | None:
    """Inline capability gate.

    Returns a 403 Response when the request's verified fleet identity
    lacks the capability at `path`. Returns None on pass.
    """
    identity_payload = getattr(request, "fleet_identity", None)
    if not identity_payload:
        # FleetSignatureRequired should have caught this, but defensive:
        return Response(
            {
                "error": {
                    "code": DenyCode.MISSING_HEADERS,
                    "message": "fleet signature required",
                }
            },
            status=401,
        )
    try:
        identity = FleetServiceIdentity.objects.get(
            pk=identity_payload["service_identity_id"]
        )
    except FleetServiceIdentity.DoesNotExist:
        return Response(
            {
                "error": {
                    "code": DenyCode.UNKNOWN_KEY_ID,
                    "message": "identity row no longer exists",
                }
            },
            status=401,
        )
    if not identity.capability(*path, default=False):
        cap_str = ".".join(path)
        logger.warning(
            "[fleet-artifacts] capability_denied app=%s capability=%s",
            identity.app_slug, cap_str,
        )
        return Response(
            {
                "error": {
                    "code": DenyCode.CAPABILITY_DENIED,
                    "message": f"capability required: {cap_str}",
                    "app_slug": identity.app_slug,
                }
            },
            status=403,
        )
    return None


# ──────────────────────────────────────────────────────────────────────
# POST /api/fleet/artifacts/ — push (impl; called from collection view)
# ──────────────────────────────────────────────────────────────────────


def _do_push(request):
    """Create a new fleet artifact.

    Request JSON:
        {
            "artifact_type": "contract_draft",
            "payload": { ... },        # required, JSON-serializable
            "metadata": { ... }        # optional, caller-supplied tags
        }

    Response 201:
        {
            "id": "<uuid>",
            "sha256": "<hex>",
            "size_bytes": 1234,
            "created_at": "<iso>",
            "artifact_type": "contract_draft"
        }

    Caller's `app_slug` is taken from the verified fleet identity, NOT
    from the request body. Any body field claiming an app_slug is
    ignored.
    """
    cap_check = _capability_check(request, "artifacts", "can_push")
    if cap_check is not None:
        return cap_check

    identity_payload = request.fleet_identity
    identity = FleetServiceIdentity.objects.get(
        pk=identity_payload["service_identity_id"]
    )

    body = request.data or {}
    artifact_type = (body.get("artifact_type") or "").strip()
    payload = body.get("payload")
    caller_metadata = body.get("metadata") or {}

    if not artifact_type:
        return Response(
            {
                "error": {
                    "code": "missing_artifact_type",
                    "message": "artifact_type is required",
                }
            },
            status=400,
        )
    if payload is None:
        return Response(
            {
                "error": {
                    "code": "missing_payload",
                    "message": "payload is required",
                }
            },
            status=400,
        )

    try:
        sha256, size_bytes = compute_payload_sha256(payload)
    except (TypeError, ValueError) as e:
        return Response(
            {
                "error": {
                    "code": "payload_not_serializable",
                    "message": f"payload must be JSON-serializable: {e}",
                }
            },
            status=400,
        )

    # Enforce capability-defined size limit (default 512 KB).
    max_payload_kb = identity.capability(
        "artifacts", "max_payload_kb", default=512
    )
    if size_bytes > max_payload_kb * 1024:
        logger.warning(
            "[fleet-artifacts] payload_too_large app=%s size_bytes=%d limit_kb=%d",
            identity.app_slug, size_bytes, max_payload_kb,
        )
        return Response(
            {
                "error": {
                    "code": DenyCode.PAYLOAD_TOO_LARGE,
                    "message": (
                        f"payload {size_bytes} bytes exceeds limit "
                        f"{max_payload_kb} KB"
                    ),
                    "size_bytes": size_bytes,
                    "max_payload_kb": max_payload_kb,
                }
            },
            status=413,
        )

    # Round 2 — compute expires_at server-side at create time.
    # Per the spec: TTL is NOT user-overridable in R2's MLC. Always
    # `created_at + DEFAULT_TTL_DAYS`. Created_at is auto_now_add, so
    # we approximate via timezone.now() and let Django set the
    # canonical timestamp via the auto-add. The 1-2ms drift is
    # acceptable for TTL semantics.
    from datetime import timedelta as _td
    from django.conf import settings as _settings
    from django.utils import timezone as _tz
    ttl_days = int(getattr(_settings, "FLEET_ARTIFACT_DEFAULT_TTL_DAYS", 30))
    expires_at = _tz.now() + _td(days=ttl_days)

    artifact = FleetArtifact.objects.create(
        artifact_type=artifact_type,
        payload=payload,
        caller_metadata=caller_metadata if isinstance(caller_metadata, dict) else {},
        sha256=sha256,
        size_bytes=size_bytes,
        created_by_identity=identity,
        created_by_key_id=identity_payload["key_id"],
        request_id=identity_payload.get("request_id", "") or "",
        expires_at=expires_at,
    )

    logger.info(
        "[fleet-artifacts] created app=%s type=%s id=%s size=%d sha=%s",
        identity.app_slug, artifact_type, artifact.id, size_bytes, sha256[:16],
    )

    # Session 1129 Move 3 — emit lifecycle event AFTER successful create.
    # Include rich payload so subscribers can act without a follow-up fetch.
    try:
        from core.services.fleet_events import emit_event
        emit_event(
            event_type="artifact.created",
            app_slug=identity.app_slug,
            payload={
                "artifact_id": str(artifact.id),
                "artifact_type": artifact_type,
                "sha256": sha256,
                "size_bytes": size_bytes,
                "created_at": artifact.created_at.isoformat(),
                "expires_at": (
                    artifact.expires_at.isoformat() if artifact.expires_at else None
                ),
                # Forward caller metadata so the consuming app (CC for
                # the flagship) has enough to filter per-user without
                # an extra DB hit. Includes generated_by_user_id when
                # present.
                "metadata": caller_metadata if isinstance(caller_metadata, dict) else {},
                "request_id": identity_payload.get("request_id", "") or "",
            },
            source_artifact=artifact,
        )
    except Exception as e:
        # Event emit must never block the create — log and move on.
        logger.warning(
            "[fleet-events] emit failed for artifact.created %s: %s",
            artifact.id, e,
        )

    return Response(
        {
            "id": str(artifact.id),
            "sha256": sha256,
            "size_bytes": size_bytes,
            "created_at": artifact.created_at.isoformat(),
            "expires_at": artifact.expires_at.isoformat() if artifact.expires_at else None,
            "artifact_type": artifact_type,
        },
        status=201,
    )


# ──────────────────────────────────────────────────────────────────────
# GET /api/fleet/artifacts/<id>/ — pull
# ──────────────────────────────────────────────────────────────────────


@csrf_exempt
@api_view(["GET"])
@authentication_classes([FleetSignatureExclusiveAuthentication])
@permission_classes([FleetSignatureRequired])
def fleet_artifacts_pull(request, artifact_id: str):
    """Fetch a fleet artifact by id.

    Ownership rule: caller's `app_slug` (from verified signature) must
    match the creator's `app_slug`. Different identity → 403.

    Response 200:
        {
            "id": "<uuid>",
            "artifact_type": "...",
            "payload": { ... },
            "metadata": { ... },
            "sha256": "<hex>",
            "size_bytes": 1234,
            "created_at": "<iso>",
            "created_by": {
                "app_slug": "...",
                "key_id": "...",
                "request_id": "..."
            }
        }
    """
    cap_check = _capability_check(request, "artifacts", "can_pull")
    if cap_check is not None:
        return cap_check

    try:
        uuid_obj = uuid.UUID(artifact_id)
    except (ValueError, TypeError):
        return Response(
            {"error": {"code": "invalid_artifact_id", "message": "not a uuid"}},
            status=400,
        )

    try:
        artifact = FleetArtifact.objects.select_related(
            "created_by_identity"
        ).get(pk=uuid_obj)
    except FleetArtifact.DoesNotExist:
        return Response(
            {"error": {"code": "artifact_not_found", "message": "no such artifact"}},
            status=404,
        )

    caller_app_slug = request.fleet_identity["app_slug"]
    creator_app_slug = artifact.created_by_identity.app_slug

    # Round 1 — cross-identity → 404 (no existence leak)
    # Round 2 — expired or soft-deleted → also 404 (same posture).
    # The three cases collapse to a single response so a client
    # holding an artifact id can't distinguish "owned by someone
    # else" from "expired" from "deleted by cleanup".
    is_unreadable = (
        caller_app_slug != creator_app_slug
        or artifact.is_deleted
        or artifact.is_expired
    )
    if is_unreadable:
        # Log the reason at server side so operators can debug; client
        # always sees the same response.
        reason = (
            "cross_identity" if caller_app_slug != creator_app_slug
            else ("deleted" if artifact.is_deleted else "expired")
        )
        logger.warning(
            "[fleet-artifacts] pull_denied reason=%s caller=%s creator=%s artifact=%s",
            reason, caller_app_slug, creator_app_slug, artifact.id,
        )
        return Response(
            {
                "error": {
                    "code": "artifact_not_found",
                    "message": "no such artifact",
                }
            },
            status=404,
        )

    logger.info(
        "[fleet-artifacts] served app=%s id=%s size=%d",
        caller_app_slug, artifact.id, artifact.size_bytes,
    )

    return Response(
        {
            "id": str(artifact.id),
            "artifact_type": artifact.artifact_type,
            "payload": artifact.payload,
            "metadata": artifact.caller_metadata,
            "sha256": artifact.sha256,
            "size_bytes": artifact.size_bytes,
            "created_at": artifact.created_at.isoformat(),
            "created_by": {
                "app_slug": creator_app_slug,
                "key_id": artifact.created_by_key_id,
                "request_id": artifact.request_id,
            },
        }
    )


# ──────────────────────────────────────────────────────────────────────
# GET /api/fleet/artifacts/ — list (Move 2 Round 2)
# ──────────────────────────────────────────────────────────────────────


LIST_MAX_LIMIT = 100
LIST_DEFAULT_LIMIT = 25


def _parse_iso_datetime(value):
    """Accept ISO-8601 with optional 'Z' or +HH:MM offset. Return aware datetime."""
    from datetime import datetime, timezone as _tz_local
    if value is None:
        return None
    s = value.strip()
    if not s:
        return None
    # Normalize trailing Z → +00:00 for fromisoformat compatibility
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError as e:
        raise ValueError(f"invalid ISO-8601 datetime: {value!r}") from e
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=_tz_local.utc)
    return dt


def _parse_bool(value, default: bool = False) -> bool:
    """Parse the standard 'true'/'false'/'1'/'0' bool flavors. Default on unknown."""
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _do_list(request):
    """List the caller's own fleet artifacts.

    Auto-scoped to the verified fleet identity's `app_slug` — there is
    NO `created_by=` query param (it would be a leak vector). Per spec
    section 1: caller identity is the only valid scope.

    Query params (all optional):
      - limit (int, default 25, max 100 — clamped, not 400'd)
      - offset (int, default 0)
      - artifact_type (string; exact match)
      - created_after (ISO-8601 datetime; inclusive lower bound on created_at)
      - created_before (ISO-8601 datetime; exclusive upper bound on created_at)
      - include_expired (bool, default false — exclude rows where now > expires_at)
      - include_deleted (bool, default false — exclude rows where deleted_at IS NOT NULL)

    Response 200:
      {
        "count": int,             # post-filter count
        "limit": int,             # echoed (post-clamp)
        "offset": int,            # echoed
        "next_offset": int | null,
        "results": [ {summary fields}, ... ]
      }

    Stable ordering: (-created_at, -id) — the tiebreaker prevents
    duplicates/missing rows across offset pages when multiple
    artifacts share a timestamp.
    """
    cap_check = _capability_check(request, "artifacts", "can_pull")
    if cap_check is not None:
        return cap_check

    caller_app_slug = request.fleet_identity["app_slug"]

    # ─── Parse + validate query params ───────────────────────────────
    try:
        limit_raw = request.GET.get("limit")
        limit = LIST_DEFAULT_LIMIT if limit_raw is None else int(limit_raw)
        if limit < 0:
            raise ValueError("limit must be non-negative")
        limit = min(limit, LIST_MAX_LIMIT)  # clamp per spec

        offset_raw = request.GET.get("offset")
        offset = 0 if offset_raw is None else int(offset_raw)
        if offset < 0:
            raise ValueError("offset must be non-negative")
    except ValueError as e:
        return Response(
            {"error": {"code": "invalid_pagination", "message": str(e)}},
            status=400,
        )

    artifact_type = (request.GET.get("artifact_type") or "").strip() or None

    try:
        created_after = _parse_iso_datetime(request.GET.get("created_after"))
        created_before = _parse_iso_datetime(request.GET.get("created_before"))
    except ValueError as e:
        return Response(
            {"error": {"code": "invalid_datetime", "message": str(e)}},
            status=400,
        )

    include_expired = _parse_bool(request.GET.get("include_expired"), default=False)
    include_deleted = _parse_bool(request.GET.get("include_deleted"), default=False)

    # ─── Build queryset ──────────────────────────────────────────────
    from django.utils import timezone as _tz
    qs = FleetArtifact.objects.filter(
        created_by_identity__app_slug=caller_app_slug,
    ).select_related("created_by_identity")

    if not include_deleted:
        qs = qs.filter(deleted_at__isnull=True)
    if not include_expired:
        qs = qs.filter(expires_at__gt=_tz.now())

    if artifact_type:
        qs = qs.filter(artifact_type=artifact_type)
    if created_after is not None:
        qs = qs.filter(created_at__gte=created_after)
    if created_before is not None:
        qs = qs.filter(created_at__lt=created_before)

    # Stable ordering with (-created_at, -id) tiebreaker per spec.
    qs = qs.order_by("-created_at", "-id")

    total = qs.count()
    page = list(qs[offset:offset + limit])
    returned = len(page)
    next_offset = offset + returned if (offset + returned) < total else None

    now = _tz.now()
    results = [
        {
            "id": str(a.id),
            "artifact_type": a.artifact_type,
            "sha256": a.sha256,
            "size_bytes": a.size_bytes,
            "created_at": a.created_at.isoformat(),
            "expires_at": a.expires_at.isoformat() if a.expires_at else None,
            "is_expired": (a.expires_at is not None and a.expires_at <= now),
            "deleted_at": a.deleted_at.isoformat() if a.deleted_at else None,
            "metadata": a.caller_metadata or {},
        }
        for a in page
    ]

    logger.info(
        "[fleet-artifacts] list app=%s limit=%d offset=%d returned=%d total=%d",
        caller_app_slug, limit, offset, returned, total,
    )

    return Response(
        {
            "count": total,
            "limit": limit,
            "offset": offset,
            "next_offset": next_offset,
            "results": results,
        }
    )


@csrf_exempt
@api_view(["POST", "GET"])
@authentication_classes([FleetSignatureExclusiveAuthentication])
@permission_classes([FleetSignatureRequired])
def fleet_artifacts_collection(request):
    """Single endpoint for the artifact collection: POST = push, GET = list.

    Implementation lives in the `_do_push` and `_do_list` helpers (which
    take DRF Request objects directly). This view is the only @api_view
    wrapped entry point; the helpers exist so the same shared
    auth/permission setup applies to both methods without trying to
    nest @api_view decorators (which fails because the inner decorator
    expects a Django HttpRequest, not the DRF Request from the outer).
    """
    if request.method == "POST":
        return _do_push(request)
    return _do_list(request)


__all__ = [
    "fleet_artifacts_pull",
    "fleet_artifacts_collection",
]
