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
# POST /api/fleet/artifacts/ — push
# ──────────────────────────────────────────────────────────────────────


@csrf_exempt
@api_view(["POST"])
@authentication_classes([FleetSignatureExclusiveAuthentication])
@permission_classes([FleetSignatureRequired])
def fleet_artifacts_push(request):
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

    artifact = FleetArtifact.objects.create(
        artifact_type=artifact_type,
        payload=payload,
        caller_metadata=caller_metadata if isinstance(caller_metadata, dict) else {},
        sha256=sha256,
        size_bytes=size_bytes,
        created_by_identity=identity,
        created_by_key_id=identity_payload["key_id"],
        request_id=identity_payload.get("request_id", "") or "",
    )

    logger.info(
        "[fleet-artifacts] created app=%s type=%s id=%s size=%d sha=%s",
        identity.app_slug, artifact_type, artifact.id, size_bytes, sha256[:16],
    )

    return Response(
        {
            "id": str(artifact.id),
            "sha256": sha256,
            "size_bytes": size_bytes,
            "created_at": artifact.created_at.isoformat(),
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

    if caller_app_slug != creator_app_slug:
        logger.warning(
            "[fleet-artifacts] cross_identity_pull_denied caller=%s creator=%s artifact=%s",
            caller_app_slug, creator_app_slug, artifact.id,
        )
        # Treat as not-found to avoid leaking artifact existence to a
        # different identity. (Could return 403; 404 is the more
        # defensive choice.)
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


__all__ = ["fleet_artifacts_push", "fleet_artifacts_pull"]
