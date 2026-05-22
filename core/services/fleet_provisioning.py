"""Fleet service identity provisioning (Move 1 Round 2).

Implements `docs/specs/FLEET_MOVE_1_AND_2_SPEC.md` section 1.6 — the
admin-only path that mints the first key for a fleet identity, plus
the rotation-friendly add-key path that creates a SECOND active key on
an existing identity (per Rigby's heads-up: dual-active keys make
emergency recovery much easier than forced rotation).

Two public entry points called by both the HTTP admin endpoint and
the management commands:

- `provision_identity(...)` — creates a brand-new
  `FleetServiceIdentity` + first `FleetServiceKey`. Raises if
  app_slug already exists.
- `add_key_for_identity(...)` — adds another `FleetServiceKey` to
  an existing identity. Used for rotation + emergency
  multi-active-key scenarios.

Both return a `ProvisioningResult` dataclass carrying the raw secret
exactly once — callers MUST surface it to the operator immediately
and never persist or log it.

Co-designed with Rigby (conversation pa-d19c1674b936). Decisions:
- Capability defaults are per-app hardcoded in `DEFAULT_CAPABILITIES`
  but always overridable via the `capabilities=` / `allowed_routes=`
  parameters.
- Key naming: `fs_{slug_with_no_dashes}_k{N}` where N auto-increments
  per identity (starts at 1).
- Raw secret never persisted (only `SHA256(secret)` lives in the DB).
- Caller decides log policy; this module never logs the secret.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.db import transaction

from core.models.fleet import (
    FleetServiceIdentity,
    FleetServiceKey,
    generate_service_secret,
    hash_service_secret,
)


# ──────────────────────────────────────────────────────────────────────
# Per-app capability defaults
# ──────────────────────────────────────────────────────────────────────


# Defaults for the seven known fleet apps. These match the
# `force_allowed` flags in `config/fleet_agent_routing.json` —
# contract-concierge and signal-studio are the two apps cleared for
# force-mode routing today. The others get hint-only.
DEFAULT_CAPABILITIES: dict[str, dict] = {
    "mentorforge": {
        "routing": {"can_request_hint": True, "can_request_force": False},
        "artifacts": {"can_pull": True, "can_push": True, "max_payload_kb": 512},
    },
    "pitchdeckforge": {
        "routing": {"can_request_hint": True, "can_request_force": False},
        "artifacts": {"can_pull": True, "can_push": True, "max_payload_kb": 512},
    },
    "contract-concierge": {
        "routing": {"can_request_hint": True, "can_request_force": True},
        "artifacts": {"can_pull": True, "can_push": True, "max_payload_kb": 512},
    },
    "sellerpilot": {
        "routing": {"can_request_hint": True, "can_request_force": False},
        "artifacts": {"can_pull": True, "can_push": True, "max_payload_kb": 512},
    },
    "dealflowtracker": {
        "routing": {"can_request_hint": True, "can_request_force": False},
        "artifacts": {"can_pull": True, "can_push": True, "max_payload_kb": 512},
    },
    "compliancesentinel": {
        "routing": {"can_request_hint": True, "can_request_force": False},
        "artifacts": {"can_pull": True, "can_push": True, "max_payload_kb": 512},
    },
    "signal-studio": {
        "routing": {"can_request_hint": True, "can_request_force": True},
        "artifacts": {"can_pull": True, "can_push": True, "max_payload_kb": 512},
    },
}

# Default allowed routes for the known apps. All apps get /api/pa/chat/
# by default; artifact endpoints are enabled per Move 2 capability.
DEFAULT_ALLOWED_ROUTES = [
    "/api/pa/chat/",
    "/api/fleet/artifacts/push",
    "/api/fleet/artifacts/pull",
]


# ──────────────────────────────────────────────────────────────────────
# Result + errors
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ProvisioningResult:
    """Returned by provision_identity / add_key_for_identity.

    Carries the raw secret exactly ONCE. Surface to the operator
    immediately and never persist or log.
    """

    app_slug: str
    name: str
    status: str
    capabilities: dict
    allowed_routes: list
    key_id: str
    secret: str  # raw secret — ONLY exposed here
    created_at: str
    is_additional_key: bool  # True when add_key_for_identity created this


class ProvisioningError(Exception):
    """Raised when provisioning preconditions fail (duplicate slug, etc)."""


# ──────────────────────────────────────────────────────────────────────
# Key id allocation
# ──────────────────────────────────────────────────────────────────────


def _slug_for_key_id(app_slug: str) -> str:
    """Convert e.g. ``contract-concierge`` → ``contractconcierge``."""
    return app_slug.replace("-", "").replace("_", "").lower()


def _next_key_index(identity: FleetServiceIdentity) -> int:
    """Find the next available key index N for ``fs_{slug}_k{N}``."""
    used: set[int] = set()
    for key in identity.keys.all():
        # Parse trailing _k<N>
        if "_k" in key.key_id:
            tail = key.key_id.rsplit("_k", 1)[-1]
            try:
                used.add(int(tail))
            except ValueError:
                continue
    if not used:
        return 1
    return max(used) + 1


def _build_key_id(app_slug: str, index: int) -> str:
    return f"fs_{_slug_for_key_id(app_slug)}_k{index}"


# ──────────────────────────────────────────────────────────────────────
# Public — provision_identity
# ──────────────────────────────────────────────────────────────────────


@transaction.atomic
def provision_identity(
    *,
    app_slug: str,
    name: str,
    capabilities: Optional[dict] = None,
    allowed_routes: Optional[list] = None,
    use_defaults: bool = True,
) -> ProvisioningResult:
    """Create a brand-new FleetServiceIdentity + its first key.

    Args:
        app_slug: Fleet app identifier (e.g. "contract-concierge").
            Must not collide with an existing identity.
        name: Human-readable label.
        capabilities: Explicit capabilities dict. When None and
            ``use_defaults=True``, falls back to per-app defaults
            (or to a minimal hint-only default for unknown apps).
        allowed_routes: Explicit route allowlist. When None and
            ``use_defaults=True``, uses `DEFAULT_ALLOWED_ROUTES`.
        use_defaults: When False, requires capabilities + allowed_routes
            be provided explicitly. Useful for fully-custom identities.

    Returns:
        ProvisioningResult — raw secret exposed exactly once.

    Raises:
        ProvisioningError when app_slug already exists or required
        params are missing with ``use_defaults=False``.
    """
    if FleetServiceIdentity.objects.filter(app_slug=app_slug).exists():
        raise ProvisioningError(
            f"app_slug={app_slug!r} already exists; use add_key_for_identity to "
            f"add another key or rotate"
        )

    # Resolve capabilities + allowed_routes
    if capabilities is None:
        if use_defaults:
            capabilities = dict(DEFAULT_CAPABILITIES.get(app_slug, {})) or {
                "routing": {"can_request_hint": True, "can_request_force": False},
                "artifacts": {"can_pull": False, "can_push": False},
            }
        else:
            raise ProvisioningError("capabilities required when use_defaults=False")
    if allowed_routes is None:
        if use_defaults:
            allowed_routes = list(DEFAULT_ALLOWED_ROUTES)
        else:
            raise ProvisioningError("allowed_routes required when use_defaults=False")

    identity = FleetServiceIdentity.objects.create(
        app_slug=app_slug,
        name=name,
        capabilities=capabilities,
        allowed_routes=allowed_routes,
    )

    secret = generate_service_secret()
    key = FleetServiceKey.objects.create(
        service=identity,
        key_id=_build_key_id(app_slug, 1),
        secret_hash=hash_service_secret(secret),
    )

    return ProvisioningResult(
        app_slug=identity.app_slug,
        name=identity.name,
        status=identity.status,
        capabilities=dict(identity.capabilities),
        allowed_routes=list(identity.allowed_routes),
        key_id=key.key_id,
        secret=secret,
        created_at=key.created_at.isoformat(),
        is_additional_key=False,
    )


# ──────────────────────────────────────────────────────────────────────
# Public — add_key_for_identity (dual-active support)
# ──────────────────────────────────────────────────────────────────────


@transaction.atomic
def add_key_for_identity(*, app_slug: str) -> ProvisioningResult:
    """Mint an additional active key for an existing fleet identity.

    Used for dual-active key rollouts and emergency recovery. The new
    key starts in ``active`` status alongside the existing key(s) —
    callers can disable old keys explicitly via the rotation lifecycle
    (Round 3) or leave them dual-active indefinitely.

    Raises:
        ProvisioningError when the identity doesn't exist or is disabled.
    """
    try:
        identity = FleetServiceIdentity.objects.get(app_slug=app_slug)
    except FleetServiceIdentity.DoesNotExist as e:
        raise ProvisioningError(
            f"no identity for app_slug={app_slug!r}; use provision_identity first"
        ) from e

    if identity.status == FleetServiceIdentity.STATUS_DISABLED:
        raise ProvisioningError(
            f"identity {app_slug!r} is disabled; re-enable before adding keys"
        )

    index = _next_key_index(identity)
    secret = generate_service_secret()
    key = FleetServiceKey.objects.create(
        service=identity,
        key_id=_build_key_id(app_slug, index),
        secret_hash=hash_service_secret(secret),
    )

    return ProvisioningResult(
        app_slug=identity.app_slug,
        name=identity.name,
        status=identity.status,
        capabilities=dict(identity.capabilities),
        allowed_routes=list(identity.allowed_routes),
        key_id=key.key_id,
        secret=secret,
        created_at=key.created_at.isoformat(),
        is_additional_key=True,
    )


__all__ = [
    "DEFAULT_CAPABILITIES",
    "DEFAULT_ALLOWED_ROUTES",
    "ProvisioningResult",
    "ProvisioningError",
    "provision_identity",
    "add_key_for_identity",
]
