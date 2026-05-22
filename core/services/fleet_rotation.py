"""Fleet service key rotation lifecycle (Move 1 Round 3).

Implements `docs/specs/FLEET_MOVE_1_AND_2_SPEC.md` section 1.6
"Rotation lifecycle". State machine:

    planned ─ activate() ─→ active ─ complete() ─→ completed
                  │                       │
                  ↓                       └─ abort() ─→ aborted (rejected after complete)
              aborted

Invariants (locked with Rigby, conversation pa-d19c1674b936):
- At most ONE rotation in `planned` or `active` state per identity at
  a time. plan() refuses if one is already in flight.
- Only keys in `active` or `draining` state verify signatures
  (enforced by `FleetServiceKey.is_currently_usable()`).
- Operations are idempotent where the spec allows:
    - activate() on an already-`active` rotation → no-op + return current state
    - complete() on an already-`completed` rotation → no-op
    - abort() after complete → REJECTED (raises). Once a rotation has
      retired the old key, you can't "un-complete" it; mint a new
      rotation if you need to roll back.

Each operation persists its admin action via `core.models.audit_log`
when available; if no such logger is wired up we fall back to the
stdlib logger. The minted state changes are always reflected in the
DB rows so the audit trail can be reconstructed from
`FleetServiceRotation` history alone.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from django.db import transaction
from django.utils import timezone

from core.models.fleet import (
    FleetServiceIdentity,
    FleetServiceKey,
    FleetServiceRotation,
    generate_service_secret,
    hash_service_secret,
)
from core.services.fleet_provisioning import _build_key_id, _next_key_index

logger = logging.getLogger(__name__)


class RotationError(Exception):
    """Raised when a rotation operation violates an invariant."""


@dataclass(frozen=True)
class PlanResult:
    """Result of plan() — carries the raw secret for the new key exactly once."""

    rotation_id: str
    status: str
    old_key_id: str
    new_key_id: str
    new_key_secret: str  # raw secret — exposed ONLY here
    ends_at: str


@dataclass(frozen=True)
class StateResult:
    """Result of activate / complete / abort. No secrets ever."""

    rotation_id: str
    status: str
    old_key_id: str
    new_key_id: str
    old_key_status: str
    new_key_status: str
    starts_at: Optional[str]
    ends_at: Optional[str]


# ──────────────────────────────────────────────────────────────────────
# plan
# ──────────────────────────────────────────────────────────────────────


@transaction.atomic
def plan_rotation(
    *,
    app_slug: str,
    ends_in_hours: int = 72,
) -> PlanResult:
    """Start a rotation: mint a new key, store the rotation row in `planned`.

    Invariants:
    - identity must exist + not be disabled
    - no existing rotation in {planned, active} for this identity
    - identity must have at least one key in `active` status to be the
      old_key for the rotation

    Raises RotationError on violation.
    """
    try:
        identity = FleetServiceIdentity.objects.select_for_update().get(
            app_slug=app_slug
        )
    except FleetServiceIdentity.DoesNotExist as e:
        raise RotationError(f"no identity for app_slug={app_slug!r}") from e

    if identity.status == FleetServiceIdentity.STATUS_DISABLED:
        raise RotationError(
            f"identity {app_slug!r} is disabled; re-enable before rotating"
        )

    # Invariant: only one rotation in flight per identity
    in_flight = FleetServiceRotation.objects.filter(
        service=identity,
        status__in=(
            FleetServiceRotation.STATUS_PLANNED,
            FleetServiceRotation.STATUS_ACTIVE,
        ),
    ).first()
    if in_flight:
        raise RotationError(
            f"rotation {in_flight.pk} already in flight for {app_slug!r} "
            f"(status={in_flight.status}); complete or abort it first"
        )

    # Pick the old_key: any active key on the identity. Prefer the
    # oldest active key so callers don't accidentally rotate keys
    # that were just minted via add_fleet_key.
    old_key = (
        FleetServiceKey.objects.filter(
            service=identity, status=FleetServiceKey.STATUS_ACTIVE
        )
        .order_by("created_at")
        .first()
    )
    if old_key is None:
        raise RotationError(
            f"no active key on identity {app_slug!r}; provision a key first"
        )

    # Mint the new key in active state. It runs alongside old_key
    # until activate() — at which point old_key flips to draining.
    new_secret = generate_service_secret()
    new_index = _next_key_index(identity)
    new_key = FleetServiceKey.objects.create(
        service=identity,
        key_id=_build_key_id(app_slug, new_index),
        secret_hash=hash_service_secret(new_secret),
        status=FleetServiceKey.STATUS_ACTIVE,
    )

    rotation = FleetServiceRotation.objects.create(
        service=identity,
        old_key=old_key,
        new_key=new_key,
        status=FleetServiceRotation.STATUS_PLANNED,
        ends_at=timezone.now() + timedelta(hours=ends_in_hours),
    )

    # Mark identity as rotating so operators can see in-flight rotations.
    identity.status = FleetServiceIdentity.STATUS_ROTATING
    identity.save(update_fields=["status", "updated_at"])

    logger.info(
        "[fleet-rotation] planned app=%s old=%s new=%s rotation_id=%s",
        app_slug, old_key.key_id, new_key.key_id, rotation.pk,
    )

    return PlanResult(
        rotation_id=str(rotation.pk),
        status=rotation.status,
        old_key_id=old_key.key_id,
        new_key_id=new_key.key_id,
        new_key_secret=new_secret,
        ends_at=rotation.ends_at.isoformat() if rotation.ends_at else "",
    )


# ──────────────────────────────────────────────────────────────────────
# activate
# ──────────────────────────────────────────────────────────────────────


@transaction.atomic
def activate_rotation(*, rotation_id: str) -> StateResult:
    """Move a planned rotation into active state.

    Side effects:
    - rotation.status = active
    - rotation.starts_at = now
    - old_key.status flips active → draining (still verifies sigs but
      flagged as deprecating)

    Idempotent: calling activate() on an already-active rotation is a
    no-op that returns the current state.
    """
    rotation = _get_rotation_for_update(rotation_id)

    if rotation.status == FleetServiceRotation.STATUS_ACTIVE:
        # Idempotent return
        return _state_from(rotation)

    if rotation.status != FleetServiceRotation.STATUS_PLANNED:
        raise RotationError(
            f"cannot activate rotation in status={rotation.status!r}; "
            f"must be 'planned'"
        )

    now = timezone.now()
    rotation.status = FleetServiceRotation.STATUS_ACTIVE
    rotation.starts_at = now
    rotation.save(update_fields=["status", "starts_at", "updated_at"])

    # Old key → draining
    rotation.old_key.status = FleetServiceKey.STATUS_DRAINING
    rotation.old_key.save(update_fields=["status", "updated_at"])

    logger.info(
        "[fleet-rotation] activated rotation_id=%s old=%s→draining new=%s active",
        rotation.pk, rotation.old_key.key_id, rotation.new_key.key_id,
    )

    return _state_from(rotation)


# ──────────────────────────────────────────────────────────────────────
# complete
# ──────────────────────────────────────────────────────────────────────


@transaction.atomic
def complete_rotation(
    *,
    rotation_id: str,
    force: bool = False,
    require_new_key_used_within_hours: int = 6,
) -> StateResult:
    """Finalize a rotation: disable the old key.

    Preconditions:
    - rotation must be in `active` state
    - new_key.last_used_at must be within the last
      `require_new_key_used_within_hours` (default 6h), OR
      `force=true` is passed

    Side effects:
    - rotation.status = completed
    - old_key.status = disabled, old_key.not_after = now
    - identity.status = active (back from rotating)

    Idempotent: calling complete() on an already-completed rotation
    is a no-op that returns the current state.
    """
    rotation = _get_rotation_for_update(rotation_id)

    if rotation.status == FleetServiceRotation.STATUS_COMPLETED:
        return _state_from(rotation)

    if rotation.status != FleetServiceRotation.STATUS_ACTIVE:
        raise RotationError(
            f"cannot complete rotation in status={rotation.status!r}; "
            f"must be 'active'"
        )

    # Safety check: new key should have been used recently to confirm
    # the fleet app has actually flipped over to it.
    if not force:
        threshold = timezone.now() - timedelta(
            hours=require_new_key_used_within_hours
        )
        last_used = rotation.new_key.last_used_at
        if last_used is None or last_used < threshold:
            raise RotationError(
                f"new key {rotation.new_key.key_id!r} has not been used "
                f"within {require_new_key_used_within_hours}h "
                f"(last_used_at={last_used}); pass force=true to override"
            )

    now = timezone.now()
    rotation.status = FleetServiceRotation.STATUS_COMPLETED
    rotation.save(update_fields=["status", "updated_at"])

    # Disable old key
    rotation.old_key.status = FleetServiceKey.STATUS_DISABLED
    rotation.old_key.not_after = now
    rotation.old_key.save(update_fields=["status", "not_after", "updated_at"])

    # Identity back to active
    rotation.service.status = FleetServiceIdentity.STATUS_ACTIVE
    rotation.service.save(update_fields=["status", "updated_at"])

    logger.info(
        "[fleet-rotation] completed rotation_id=%s old=%s→disabled new=%s active force=%s",
        rotation.pk, rotation.old_key.key_id, rotation.new_key.key_id, force,
    )

    return _state_from(rotation)


# ──────────────────────────────────────────────────────────────────────
# abort
# ──────────────────────────────────────────────────────────────────────


@transaction.atomic
def abort_rotation(*, rotation_id: str) -> StateResult:
    """Cancel a rotation: disable the new key, restore the old key.

    Allowed from `planned` or `active`. **REJECTED** from `completed`
    or `aborted` — once a rotation has finalized you can't un-complete
    it; mint a new rotation if you need to roll back.

    Side effects:
    - rotation.status = aborted
    - new_key.status = disabled, new_key.not_after = now
    - old_key.status = active (restored from draining if it had moved)
    - identity.status = active (back from rotating)
    """
    rotation = _get_rotation_for_update(rotation_id)

    if rotation.status == FleetServiceRotation.STATUS_ABORTED:
        return _state_from(rotation)

    if rotation.status == FleetServiceRotation.STATUS_COMPLETED:
        raise RotationError(
            "cannot abort a completed rotation; mint a new rotation "
            "to roll back the key swap"
        )

    if rotation.status not in (
        FleetServiceRotation.STATUS_PLANNED,
        FleetServiceRotation.STATUS_ACTIVE,
    ):
        raise RotationError(
            f"cannot abort rotation in status={rotation.status!r}"
        )

    now = timezone.now()
    rotation.status = FleetServiceRotation.STATUS_ABORTED
    rotation.save(update_fields=["status", "updated_at"])

    # Disable new key — it never got promoted
    rotation.new_key.status = FleetServiceKey.STATUS_DISABLED
    rotation.new_key.not_after = now
    rotation.new_key.save(update_fields=["status", "not_after", "updated_at"])

    # Restore old key to active (it may have moved to draining via activate())
    if rotation.old_key.status == FleetServiceKey.STATUS_DRAINING:
        rotation.old_key.status = FleetServiceKey.STATUS_ACTIVE
        rotation.old_key.save(update_fields=["status", "updated_at"])

    rotation.service.status = FleetServiceIdentity.STATUS_ACTIVE
    rotation.service.save(update_fields=["status", "updated_at"])

    logger.info(
        "[fleet-rotation] aborted rotation_id=%s new=%s→disabled old=%s restored",
        rotation.pk, rotation.new_key.key_id, rotation.old_key.key_id,
    )

    return _state_from(rotation)


# ──────────────────────────────────────────────────────────────────────
# Internals
# ──────────────────────────────────────────────────────────────────────


def _get_rotation_for_update(rotation_id: str) -> FleetServiceRotation:
    try:
        return FleetServiceRotation.objects.select_for_update().select_related(
            "service", "old_key", "new_key"
        ).get(pk=rotation_id)
    except FleetServiceRotation.DoesNotExist as e:
        raise RotationError(f"unknown rotation_id={rotation_id!r}") from e


def _state_from(rotation: FleetServiceRotation) -> StateResult:
    return StateResult(
        rotation_id=str(rotation.pk),
        status=rotation.status,
        old_key_id=rotation.old_key.key_id,
        new_key_id=rotation.new_key.key_id,
        old_key_status=rotation.old_key.status,
        new_key_status=rotation.new_key.status,
        starts_at=rotation.starts_at.isoformat() if rotation.starts_at else None,
        ends_at=rotation.ends_at.isoformat() if rotation.ends_at else None,
    )


__all__ = [
    "RotationError",
    "PlanResult",
    "StateResult",
    "plan_rotation",
    "activate_rotation",
    "complete_rotation",
    "abort_rotation",
]
