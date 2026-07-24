"""Ledger #16 — twin-mirror enforcement at session close.

Every ratifiable engineering artifact has TWO canonical representations
per ``feedback_twin_deliverable_at_every_ratification``:

  1. **content_mirror**  — engineering truth (typically ``category=
     'initiative_phase_doc'`` or similar; the WHAT was built)
  2. **ratification_envelope** — governance truth (``deliverable_type=
     'ratification_record'``; the WHY/HOW-ratified)

Sessions S2937 / S2938 / S2939 all shipped without twin mirrors — the
close ceremony completed, humans moved on, mirrors were forgotten.
Backfill via ``scripts/backfill_s2818_s2824_workspace_mirrors.py``
recovered older gaps but only after Chris flagged the drift.

This module makes skipping mirrors a **conscious act**: at close time,
the operator must EITHER (a) pass ``--content-mirror-id`` +
``--ratification-envelope-id`` (verified against the DB), OR
(b) pass ``--allow-no-mirror`` (logged for audit). No implicit skip.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


class TwinMirrorEnforcementError(Exception):
    """Raised when close cannot proceed under Ledger #16 twin-mirror rule."""


@dataclass(frozen=True)
class MirrorVerificationResult:
    """Outcome shape returned to the CLI for stdout reporting."""

    mode: str  # 'verified' | 'allowed_no_mirror'
    content_mirror_id: Optional[UUID]
    ratification_envelope_id: Optional[UUID]
    content_mirror_title: Optional[str]
    ratification_envelope_title: Optional[str]


def assert_twin_mirror_at_close(
    *,
    content_mirror_id: Optional[str],
    ratification_envelope_id: Optional[str],
    allow_no_mirror: bool,
) -> MirrorVerificationResult:
    """Enforce Ledger #16 at ``session_lifecycle close`` time.

    Args:
        content_mirror_id: UUID string for the engineering-truth mirror,
            or ``None``.
        ratification_envelope_id: UUID string for the governance-truth
            envelope, or ``None``.
        allow_no_mirror: Explicit escape hatch for cascade-only closes
            or sessions where no mirrors were written.

    Returns:
        ``MirrorVerificationResult`` describing the outcome for CLI
        stdout.

    Raises:
        TwinMirrorEnforcementError: on any of — both flags missing;
            only one mirror ID provided; either ID doesn't parse as a
            UUID; either ID doesn't exist in the DB; either row is
            ``diagnostic_status='diagnostic'``; the envelope row's
            ``deliverable_type`` is not ``'ratification_record'``.
    """
    has_content = bool(content_mirror_id)
    has_envelope = bool(ratification_envelope_id)

    if allow_no_mirror and (has_content or has_envelope):
        raise TwinMirrorEnforcementError(
            "--allow-no-mirror is mutually exclusive with "
            "--content-mirror-id / --ratification-envelope-id. "
            "Either provide both mirror IDs OR skip enforcement, not both."
        )

    if allow_no_mirror:
        return MirrorVerificationResult(
            mode="allowed_no_mirror",
            content_mirror_id=None,
            ratification_envelope_id=None,
            content_mirror_title=None,
            ratification_envelope_title=None,
        )

    if not has_content and not has_envelope:
        raise TwinMirrorEnforcementError(
            "Ledger #16: close requires twin-mirror verification.\n"
            "  Provide BOTH --content-mirror-id <UUID> AND "
            "--ratification-envelope-id <UUID>\n"
            "  OR pass --allow-no-mirror to skip (logged for audit).\n"
            "  See docs/PA_TOOL_AUDIT.md and "
            "`feedback_twin_deliverable_at_every_ratification` "
            "for the twin-mirror contract."
        )

    if has_content != has_envelope:
        missing = (
            "--ratification-envelope-id" if has_content
            else "--content-mirror-id"
        )
        raise TwinMirrorEnforcementError(
            f"Ledger #16: twin-mirror requires BOTH IDs. Missing: {missing}"
        )

    try:
        content_uuid = UUID(content_mirror_id)  # type: ignore[arg-type]
    except (ValueError, TypeError) as exc:
        raise TwinMirrorEnforcementError(
            f"--content-mirror-id is not a valid UUID: "
            f"{content_mirror_id!r}"
        ) from exc

    try:
        envelope_uuid = UUID(ratification_envelope_id)  # type: ignore[arg-type]
    except (ValueError, TypeError) as exc:
        raise TwinMirrorEnforcementError(
            f"--ratification-envelope-id is not a valid UUID: "
            f"{ratification_envelope_id!r}"
        ) from exc

    # Ledger #16 requires TWO distinct artifacts. Passing the same UUID
    # for both would defeat the contract (Rigby T1 SIGN F-BLOCKING).
    if content_uuid == envelope_uuid:
        raise TwinMirrorEnforcementError(
            f"--content-mirror-id and --ratification-envelope-id must "
            f"reference DIFFERENT Deliverable rows. Twin-mirror requires "
            f"two artifacts: engineering truth (content) + governance "
            f"truth (envelope). Got the same UUID for both: {content_uuid}"
        )

    from core.models_deliverables import Deliverable

    content_row = Deliverable.objects.filter(id=content_uuid).first()
    if content_row is None:
        raise TwinMirrorEnforcementError(
            f"--content-mirror-id {content_uuid} not found in Deliverable table."
        )
    if content_row.diagnostic_status == "diagnostic":
        raise TwinMirrorEnforcementError(
            f"--content-mirror-id {content_uuid} is flagged "
            f"diagnostic_status='diagnostic' — cannot serve as twin mirror. "
            f"Clear the diagnostic flags first (see "
            f"`feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`)."
        )

    envelope_row = Deliverable.objects.filter(id=envelope_uuid).first()
    if envelope_row is None:
        raise TwinMirrorEnforcementError(
            f"--ratification-envelope-id {envelope_uuid} not found in "
            f"Deliverable table."
        )
    if envelope_row.diagnostic_status == "diagnostic":
        raise TwinMirrorEnforcementError(
            f"--ratification-envelope-id {envelope_uuid} is flagged "
            f"diagnostic_status='diagnostic' — cannot serve as twin mirror. "
            f"Clear the diagnostic flags first (see "
            f"`feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`)."
        )
    if envelope_row.deliverable_type != "ratification_record":
        raise TwinMirrorEnforcementError(
            f"--ratification-envelope-id {envelope_uuid} has "
            f"deliverable_type={envelope_row.deliverable_type!r}, expected "
            f"'ratification_record'. Update the row's deliverable_type or "
            f"pass a different envelope ID."
        )

    return MirrorVerificationResult(
        mode="verified",
        content_mirror_id=content_uuid,
        ratification_envelope_id=envelope_uuid,
        content_mirror_title=content_row.title,
        ratification_envelope_title=envelope_row.title,
    )
