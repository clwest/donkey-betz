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


__all__ = ["fleet_identities", "fleet_identity_keys"]
