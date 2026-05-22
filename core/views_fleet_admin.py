"""Fleet identity admin endpoints (Move 1 Round 2).

Admin-only HTTP surface for provisioning + key management. Calls into
`core.services.fleet_provisioning` for the actual work; this module
just handles auth, request shape, and the "secret returned exactly
once" response contract.

Endpoints:
- `POST /api/admin/fleet/identities` — provision new identity + first key
- `POST /api/admin/fleet/identities/<app_slug>/keys` — add additional key
  (dual-active support per Rigby's Round-2 heads-up)
- `GET /api/admin/fleet/identities` — list identities (no secrets)
- `GET /api/admin/fleet/identities/<app_slug>` — single identity (no secret)

Auth: `IsAdminUser` + extra `is_superuser` check (toggleable via
`FLEET_PROVISIONING_REQUIRE_SUPERUSER`, default True). Blast radius
stays small without inventing a new permission system.

Logging: raw secrets NEVER touch the logger. The response is the ONLY
place they exist after the helper returns; the helper itself never
logs.
"""
from __future__ import annotations

import logging

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from core.services.fleet_provisioning import (
    ProvisioningError,
    add_key_for_identity,
    provision_identity,
)

logger = logging.getLogger(__name__)


def _superuser_gate(request) -> Response | None:
    """Optional second-gate beyond IsAdminUser. Returns 403 Response if blocked."""
    require_superuser = getattr(
        settings, "FLEET_PROVISIONING_REQUIRE_SUPERUSER", True
    )
    if require_superuser and not request.user.is_superuser:
        return Response(
            {"error": {"code": "superuser_required", "message": "superuser required"}},
            status=403,
        )
    return None


@csrf_exempt
@api_view(["POST", "GET"])
@permission_classes([IsAdminUser])
def fleet_identities(request):
    """List identities (GET) or provision a new one (POST).

    GET response (no secrets exposed):
        {"identities": [{"app_slug": "...", "status": "...", "key_count": N, ...}, ...]}

    POST body:
        {
          "app_slug": "contract-concierge",
          "name": "Contract Concierge",
          "capabilities": {...},        // optional, falls back to per-app defaults
          "allowed_routes": [...],      // optional, falls back to defaults
          "use_defaults": true          // optional, default true
        }

    POST 201 response:
        {
          "service": {...},
          "key": {"key_id": "...", "secret": "...", "created_at": "..."},
          "next_steps": {
            "set_env": ["FLEET_APP_SLUG=...", "FLEET_KEY_ID=...", "FLEET_SERVICE_SECRET=..."],
            "verify": "POST a signed /api/pa/chat/ ..."
          }
        }
    """
    gate = _superuser_gate(request)
    if gate is not None:
        return gate

    if request.method == "GET":
        from core.models.fleet import FleetServiceIdentity
        rows = []
        for identity in FleetServiceIdentity.objects.all().prefetch_related("keys"):
            rows.append(
                {
                    "app_slug": identity.app_slug,
                    "name": identity.name,
                    "status": identity.status,
                    "capabilities": identity.capabilities,
                    "allowed_routes": identity.allowed_routes,
                    "key_count": identity.keys.count(),
                    "last_used_at": (
                        identity.last_used_at.isoformat()
                        if identity.last_used_at
                        else None
                    ),
                    "created_at": identity.created_at.isoformat(),
                }
            )
        return Response({"identities": rows})

    # POST — provision new identity
    payload = request.data or {}
    app_slug = (payload.get("app_slug") or "").strip()
    name = (payload.get("name") or "").strip()
    capabilities = payload.get("capabilities")
    allowed_routes = payload.get("allowed_routes")
    use_defaults = bool(payload.get("use_defaults", True))

    if not app_slug:
        return Response(
            {"error": {"code": "missing_app_slug", "message": "app_slug is required"}},
            status=400,
        )
    if not name:
        return Response(
            {"error": {"code": "missing_name", "message": "name is required"}},
            status=400,
        )

    try:
        result = provision_identity(
            app_slug=app_slug,
            name=name,
            capabilities=capabilities,
            allowed_routes=allowed_routes,
            use_defaults=use_defaults,
        )
    except ProvisioningError as e:
        # Log the failure with the slug but NOT any secret material
        # (provision_identity raises before secret generation).
        logger.warning(
            f"[fleet-provision] reject app_slug={app_slug!r}: {e}"
        )
        return Response(
            {"error": {"code": "provisioning_failed", "message": str(e)}},
            status=409,
        )

    logger.info(
        "[fleet-provision] minted identity app=%s key_id=%s by user=%s",
        result.app_slug, result.key_id, request.user.username,
    )

    return Response(
        {
            "service": {
                "app_slug": result.app_slug,
                "name": result.name,
                "status": result.status,
                "capabilities": result.capabilities,
                "allowed_routes": result.allowed_routes,
            },
            "key": {
                "key_id": result.key_id,
                "secret": result.secret,
                "created_at": result.created_at,
            },
            "next_steps": {
                "set_env": [
                    f"FLEET_APP_SLUG={result.app_slug}",
                    f"FLEET_KEY_ID={result.key_id}",
                    "FLEET_SERVICE_SECRET=<see secret above>",
                ],
                "verify": (
                    "Call POST /api/pa/chat/ with signed X-Fleet-* headers; "
                    "confirm response routing.phase2_dispatched fires when "
                    "you pass {mode: 'force', agent: '<allowlisted>'}."
                ),
                "warning": (
                    "The secret is shown EXACTLY ONCE. Save it to your "
                    "deployment secrets immediately; u-d-b stores only the "
                    "SHA256 hash and cannot recover the raw secret. If "
                    "lost, mint a new key via /api/admin/fleet/identities/"
                    f"{result.app_slug}/keys."
                ),
            },
        },
        status=201,
    )


@csrf_exempt
@api_view(["POST", "GET"])
@permission_classes([IsAdminUser])
def fleet_identity_keys(request, app_slug: str):
    """List keys for an identity (GET) or add a new key (POST).

    Dual-active key support per Rigby's Round-2 heads-up — operators
    can mint a second key alongside the existing one without forcing
    immediate rotation. The new key starts in ``active`` state; old
    key stays ``active``.

    GET response (no secrets):
        {"keys": [{"key_id": "...", "status": "...", "created_at": "...", "last_used_at": "..."}]}

    POST 201 response: same shape as provision_identity (raw secret
    returned once).
    """
    gate = _superuser_gate(request)
    if gate is not None:
        return gate

    if request.method == "GET":
        from core.models.fleet import FleetServiceIdentity
        try:
            identity = FleetServiceIdentity.objects.get(app_slug=app_slug)
        except FleetServiceIdentity.DoesNotExist:
            return Response(
                {"error": {"code": "unknown_app_slug", "message": "no such identity"}},
                status=404,
            )
        keys = [
            {
                "key_id": k.key_id,
                "status": k.status,
                "created_at": k.created_at.isoformat(),
                "last_used_at": (
                    k.last_used_at.isoformat() if k.last_used_at else None
                ),
                "not_before": (
                    k.not_before.isoformat() if k.not_before else None
                ),
                "not_after": (
                    k.not_after.isoformat() if k.not_after else None
                ),
            }
            for k in identity.keys.all().order_by("created_at")
        ]
        return Response({"app_slug": app_slug, "keys": keys})

    # POST — add additional active key
    try:
        result = add_key_for_identity(app_slug=app_slug)
    except ProvisioningError as e:
        logger.warning(f"[fleet-provision] add-key reject app_slug={app_slug!r}: {e}")
        return Response(
            {"error": {"code": "provisioning_failed", "message": str(e)}},
            status=404 if "no identity" in str(e) else 409,
        )

    logger.info(
        "[fleet-provision] minted additional key app=%s key_id=%s by user=%s",
        result.app_slug, result.key_id, request.user.username,
    )

    return Response(
        {
            "service": {
                "app_slug": result.app_slug,
                "name": result.name,
                "status": result.status,
            },
            "key": {
                "key_id": result.key_id,
                "secret": result.secret,
                "created_at": result.created_at,
                "is_additional_key": True,
            },
            "next_steps": {
                "set_env": [
                    f"FLEET_KEY_ID={result.key_id}",
                    "FLEET_SERVICE_SECRET=<see secret above>",
                ],
                "rollout": (
                    "Old key remains active; flip the fleet app to the "
                    "new key_id/secret in its env, then disable the old "
                    "key via the rotation endpoints (Round 3)."
                ),
                "warning": (
                    "The secret is shown EXACTLY ONCE. Save it now; "
                    "u-d-b stores only the SHA256 hash."
                ),
            },
        },
        status=201,
    )


@csrf_exempt
@api_view(["POST", "GET"])
@permission_classes([IsAdminUser])
def fleet_rotations(request, app_slug: str | None = None):
    """List rotations (GET, optionally filtered by app_slug) or plan a new one (POST).

    POST body:
        {"app_slug": "contract-concierge", "ends_in_hours": 72}

    POST 201 returns the raw new_key_secret EXACTLY ONCE.
    """
    gate = _superuser_gate(request)
    if gate is not None:
        return gate

    if request.method == "GET":
        from core.models.fleet import FleetServiceRotation
        qs = FleetServiceRotation.objects.select_related(
            "service", "old_key", "new_key"
        )
        if app_slug:
            qs = qs.filter(service__app_slug=app_slug)
        rows = [
            {
                "rotation_id": str(r.pk),
                "app_slug": r.service.app_slug,
                "status": r.status,
                "old_key_id": r.old_key.key_id,
                "new_key_id": r.new_key.key_id,
                "starts_at": r.starts_at.isoformat() if r.starts_at else None,
                "ends_at": r.ends_at.isoformat() if r.ends_at else None,
                "created_at": r.created_at.isoformat(),
            }
            for r in qs.order_by("-created_at")[:50]
        ]
        return Response({"rotations": rows})

    # POST — plan a new rotation
    from core.services.fleet_rotation import plan_rotation, RotationError
    payload = request.data or {}
    target_slug = app_slug or (payload.get("app_slug") or "").strip()
    if not target_slug:
        return Response(
            {"error": {"code": "missing_app_slug", "message": "app_slug required"}},
            status=400,
        )
    ends_in_hours = int(payload.get("ends_in_hours", 72))

    try:
        result = plan_rotation(app_slug=target_slug, ends_in_hours=ends_in_hours)
    except RotationError as e:
        logger.warning(f"[fleet-rotation] plan reject app_slug={target_slug!r}: {e}")
        return Response(
            {"error": {"code": "rotation_plan_failed", "message": str(e)}},
            status=409,
        )

    logger.info(
        "[fleet-rotation] planned app=%s rotation_id=%s by user=%s",
        target_slug, result.rotation_id, request.user.username,
    )

    return Response(
        {
            "rotation": {
                "rotation_id": result.rotation_id,
                "status": result.status,
                "old_key_id": result.old_key_id,
                "new_key_id": result.new_key_id,
                "ends_at": result.ends_at,
            },
            "key": {
                "key_id": result.new_key_id,
                "secret": result.new_key_secret,
            },
            "next_steps": {
                "1_set_env": [
                    f"FLEET_KEY_ID={result.new_key_id}",
                    "FLEET_SERVICE_SECRET=<see secret above>",
                ],
                "2_activate": (
                    f"POST /api/admin/fleet/rotations/{result.rotation_id}/activate/ — "
                    f"flips old key to draining, marks rotation as in-rollout."
                ),
                "3_complete": (
                    f"POST /api/admin/fleet/rotations/{result.rotation_id}/complete/ — "
                    f"after the fleet app starts using the new key, this disables the old."
                ),
                "abort_anytime": (
                    f"POST /api/admin/fleet/rotations/{result.rotation_id}/abort/ — "
                    f"only allowed before complete."
                ),
                "warning": (
                    "The secret is shown EXACTLY ONCE. Save now; u-d-b stores only the SHA256 hash."
                ),
            },
        },
        status=201,
    )


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAdminUser])
def fleet_rotation_transition(request, rotation_id: str, action: str):
    """Drive a rotation through its state machine.

    action ∈ {"activate", "complete", "abort"}. Idempotent for
    activate + complete; abort rejected after complete.
    """
    gate = _superuser_gate(request)
    if gate is not None:
        return gate

    from core.services.fleet_rotation import (
        RotationError,
        abort_rotation,
        activate_rotation,
        complete_rotation,
    )

    payload = request.data or {}

    try:
        if action == "activate":
            result = activate_rotation(rotation_id=rotation_id)
        elif action == "complete":
            force = bool(payload.get("force", False))
            result = complete_rotation(rotation_id=rotation_id, force=force)
        elif action == "abort":
            result = abort_rotation(rotation_id=rotation_id)
        else:
            return Response(
                {
                    "error": {
                        "code": "unknown_action",
                        "message": f"action must be activate/complete/abort, got {action!r}",
                    }
                },
                status=400,
            )
    except RotationError as e:
        logger.warning(
            f"[fleet-rotation] {action} reject rotation_id={rotation_id!r}: {e}"
        )
        return Response(
            {"error": {"code": "rotation_transition_failed", "message": str(e)}},
            status=409,
        )

    logger.info(
        "[fleet-rotation] %s rotation_id=%s by user=%s",
        action, rotation_id, request.user.username,
    )

    return Response(
        {
            "rotation": {
                "rotation_id": result.rotation_id,
                "status": result.status,
                "old_key_id": result.old_key_id,
                "new_key_id": result.new_key_id,
                "old_key_status": result.old_key_status,
                "new_key_status": result.new_key_status,
                "starts_at": result.starts_at,
                "ends_at": result.ends_at,
            }
        }
    )


__all__ = [
    "fleet_identities",
    "fleet_identity_keys",
    "fleet_rotations",
    "fleet_rotation_transition",
]
