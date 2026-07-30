"""Rigby Tool Gap Ledger reconciliation enforcement at session close.

When a session's work touches a ledger row (references `Ledger #N` in its
handoff), the row's status must be flipped in the ledger deliverable with
PR/commit evidence BEFORE close. Sessions 2931 / 2938 / 2941 all shipped
code that fully closed a ledger row but forgot to flip the row's status;
S2942 caught two of those retroactively; S3041 caught two more (#5 + #16)
in the same session.

This module makes skipping a ledger-status flip a **conscious act**: at
close time, the operator must either (a) ensure every `Ledger #N`
reference in the handoff has a corresponding `Ledger #N status flip:`
block in the ledger deliverable content, OR (b) pass
``--allow-ledger-drift`` (logged for audit). No silent drift.

Twin-mirror precedent applied per S3041 T0 SIGN — same shape as
``twin_mirror_enforcement.assert_twin_mirror_at_close``: structured
inputs (handoff-file parse + deliverable-content parse) plus explicit,
audited escape hatch. Handoff-only parse (not git log) avoids
false-positive blocks per Rigby S3041 tightening.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional
from uuid import UUID


DEFAULT_LEDGER_DELIVERABLE_ID = "5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0"

_LEDGER_REFERENCE_PATTERN = re.compile(r"Ledger\s+#(\d+)", re.IGNORECASE)


class LedgerReconciliationError(Exception):
    """Raised when close cannot proceed under the Rigby Tool Gap Ledger
    reconciliation rule (S3041 meta-fix)."""


@dataclass(frozen=True)
class LedgerReconciliationResult:
    """Outcome shape returned to the CLI for stdout reporting."""

    mode: str  # 'clean' | 'allowed_drift' | 'no_handoff'
    handoff_path: Optional[Path]
    referenced_entries: List[int] = field(default_factory=list)
    flipped_entries: List[int] = field(default_factory=list)
    drift_entries: List[int] = field(default_factory=list)


def extract_ledger_references(text: str) -> List[int]:
    """Return sorted-unique integers N from any ``Ledger #N`` occurrence
    in ``text``. Deduplicated because a single row may be referenced
    multiple times in the same handoff (e.g., in the summary + evidence
    block).

    Pattern is case-insensitive and tolerates one-or-more whitespace
    characters between ``Ledger`` and ``#``. It intentionally does NOT
    match ``ledger row #N`` / ``entry #N`` / other spellings — the
    convention is ``Ledger #N`` per every ratification handoff since the
    ledger deliverable existed.
    """
    matches = _LEDGER_REFERENCE_PATTERN.findall(text)
    return sorted({int(m) for m in matches})


def detect_flipped_entries(ledger_content: str, referenced: Iterable[int]) -> List[int]:
    """Return the subset of ``referenced`` entries that have a
    ``Ledger #N status flip`` block in the ledger deliverable content.

    Match is case-insensitive and tolerates any whitespace between
    ``Ledger`` and ``#N`` and ``status flip``. The presence of a flip
    block anywhere in the ledger content (including prior-session
    reconciliation sections) counts — a flip once shipped remains
    flipped.
    """
    flipped: List[int] = []
    for n in referenced:
        pattern = re.compile(
            rf"Ledger\s+#{n}\s+status\s+flip", re.IGNORECASE
        )
        if pattern.search(ledger_content):
            flipped.append(n)
    return flipped


def check_ledger_reconciliation_at_close(
    *,
    handoff_path: Optional[str],
    ledger_deliverable_id: Optional[str] = None,
    allow_ledger_drift: bool = False,
) -> LedgerReconciliationResult:
    """Enforce the S3041 meta-fix at ``session_lifecycle close`` time.

    Args:
        handoff_path: Filesystem path to the session handoff being
            closed. If ``None`` or the path does not exist, returns
            ``mode='no_handoff'`` (silent no-op — first-time users /
            retire-only closes / cascade-only closes have no handoff to
            check).
        ledger_deliverable_id: UUID string for the Rigby Tool Gap Ledger
            deliverable to check against. Defaults to
            ``DEFAULT_LEDGER_DELIVERABLE_ID``.
        allow_ledger_drift: Explicit escape hatch. When True, drift is
            reported in the result but no exception is raised. Logged for
            audit at the CLI layer.

    Returns:
        ``LedgerReconciliationResult`` describing the outcome.

    Raises:
        LedgerReconciliationError: on any of — handoff references a
            ledger row that is not flipped in the ledger deliverable AND
            ``allow_ledger_drift=False``; or the ledger deliverable is
            not found; or ``ledger_deliverable_id`` is not a valid UUID.
    """
    if not handoff_path:
        return LedgerReconciliationResult(
            mode="no_handoff",
            handoff_path=None,
        )

    handoff = Path(handoff_path)
    if not handoff.exists():
        return LedgerReconciliationResult(
            mode="no_handoff",
            handoff_path=handoff,
        )

    handoff_text = handoff.read_text(encoding="utf-8")
    referenced = extract_ledger_references(handoff_text)

    if not referenced:
        return LedgerReconciliationResult(
            mode="clean",
            handoff_path=handoff,
            referenced_entries=[],
            flipped_entries=[],
            drift_entries=[],
        )

    ledger_id = ledger_deliverable_id or DEFAULT_LEDGER_DELIVERABLE_ID
    try:
        ledger_uuid = UUID(ledger_id)
    except (ValueError, TypeError) as exc:
        raise LedgerReconciliationError(
            f"--ledger-deliverable-id is not a valid UUID: {ledger_id!r}"
        ) from exc

    from core.models_deliverables import Deliverable

    ledger_row = Deliverable.objects.filter(id=ledger_uuid).first()
    if ledger_row is None:
        raise LedgerReconciliationError(
            f"Ledger deliverable {ledger_uuid} not found. "
            f"Pass --ledger-deliverable-id <UUID> to override or "
            f"--allow-ledger-drift to skip."
        )

    ledger_content = ledger_row.content or ""
    flipped = detect_flipped_entries(ledger_content, referenced)
    drift = sorted(set(referenced) - set(flipped))

    if drift and not allow_ledger_drift:
        drift_str = ", ".join(f"#{n}" for n in drift)
        raise LedgerReconciliationError(
            f"S3041 meta-fix: handoff references Ledger {drift_str} but "
            f"no matching `Ledger #N status flip` block found in ledger "
            f"deliverable {ledger_uuid}.\n"
            f"  Either flip the row status in the ledger content "
            f"(mirror the S3041/S2942 reconciliation shape) OR pass "
            f"--allow-ledger-drift to skip (logged for audit).\n"
            f"  See docs/handoffs/SESSION_3041_LEDGER_RECONCILIATION.md "
            f"for the flip-block template."
        )

    return LedgerReconciliationResult(
        mode="allowed_drift" if drift else "clean",
        handoff_path=handoff,
        referenced_entries=referenced,
        flipped_entries=flipped,
        drift_entries=drift,
    )
