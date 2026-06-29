"""
Employee Communications (Session 1253 PR 4).

Pure-function helper to post one DirectMessage per terminal mission
from an AI employee (Rigby) into a persistent inbox thread visible to
Chris in the existing /inbox web UI.

Hard contract (per Rigby SIGN-WITH-EDITS):

  * Persistent thread per (employee, job), keyed by
    ``metadata.employee`` + ``metadata.job``. Deterministic
    get-or-create. Exact subject: "Rigby — Documentation Manager".
  * One DM per terminal mission. Idempotent on (thread, mission_id) —
    re-calling the helper for the same mission is a no-op.
  * Non-terminal missions (status='running' / 'pending') produce no DM.
  * Bounded JSON metadata only — never the full error tail.
  * Additive to existing Deliverable + PA-chat escalation. No
    replacement of either.
  * No push notification. No mobile work. No proactive-notification
    chain. No write surface to the LLM.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from django.contrib.auth import get_user_model
from django.utils import timezone

from core.employees import RIGBY, DOCUMENTATION_MANAGER


logger = logging.getLogger(__name__)


# ── Thread-identity constants ─────────────────────────────────────────

THREAD_SUBJECT = "Rigby — Documentation Manager"
THREAD_KIND = "employee_shift_report"
EMPLOYEE_KEY = RIGBY.handle             # "rigby"
JOB_KEY = "docs_manager"

# Terminal statuses + verdicts (anything else means "still in flight").
_TERMINAL_STATUSES = {"passed", "failed", "partial"}
_TERMINAL_VERDICTS = {"certified", "rejected", "deferred"}


# ── Body templates ────────────────────────────────────────────────────


def _format_body(mission, summary: Dict[str, Any]) -> str:
    """Build the body string per Rigby's exact templates."""
    verdict = summary.get("verdict")
    wall_ms = summary.get("wall_time_ms")
    seconds = (
        f"{wall_ms / 1000:.1f}"
        if isinstance(wall_ms, (int, float))
        else "?"
    )

    if verdict == "certified":
        drift = summary.get("drift_count")
        drift_part = (
            f"Drift {drift} items observed."
            if isinstance(drift, int)
            else "Drift count unavailable."
        )
        return (
            f"Docs Manager mission {mission.id} passed. "
            f"Docs cascade completed in {seconds}s. "
            f"{drift_part} No escalation."
        )

    if verdict == "rejected":
        failed_step = summary.get("failed_step") or "<unknown step>"
        escalation_id = summary.get("escalation_deliverable_id")
        if escalation_id:
            esc_sentence = (
                f"Escalation deliverable {escalation_id} created."
            )
        else:
            esc_sentence = "No escalation deliverable recorded."
        return (
            f"Docs Manager mission {mission.id} failed at "
            f"{failed_step}. {esc_sentence}"
        )

    if verdict == "deferred":
        return (
            f"Docs Manager mission {mission.id} deferred. "
            f"Awaiting follow-up review."
        )

    # Shouldn't reach — _is_terminal gates the call site. Guard anyway.
    return (
        f"Docs Manager mission {mission.id} reached terminal state "
        f"with verdict={verdict!r}."
    )


# ── Bounded metadata projection (per Rigby edit #4) ───────────────────


_METADATA_ALLOWED_KEYS = (
    "mission_id",
    "verdict",
    "status",
    "wall_time_ms",
    "drift_count",
    "failed_step",
    "escalation_deliverable_id",
)


def _build_metadata(mission, summary: Dict[str, Any]) -> Dict[str, Any]:
    """Project mission summary into the bounded inbox-DM metadata shape.

    Hard-bounded to the seven keys Rigby signed off on. Never includes
    error_tail, error_tail_preview, ops-run UUIDs other than
    ``mission_id``, or anything that could grow unbounded.
    """
    meta: Dict[str, Any] = {
        "employee": EMPLOYEE_KEY,
        "job": JOB_KEY,
        "mission_id": str(mission.id),
        "verdict": summary.get("verdict"),
        "status": mission.status,
        "wall_time_ms": summary.get("wall_time_ms"),
        "drift_count": summary.get("drift_count"),
        "failed_step": summary.get("failed_step"),
        "escalation_deliverable_id": summary.get(
            "escalation_deliverable_id"
        ),
    }
    return meta


# ── Terminal-state gate ───────────────────────────────────────────────


def _is_terminal(mission) -> bool:
    """True iff the mission has reached a final certified/rejected/deferred state.

    Checks both ``OpsRun.status`` and ``summary.verdict`` — either side
    landing terminal is sufficient. Status alone is enough on its own;
    verdict alone catches the case where verdict was emitted but the
    status field hasn't been refreshed yet on the caller's mission
    handle.
    """
    if mission.status in _TERMINAL_STATUSES:
        return True
    summary = mission.summary or {}
    return summary.get("verdict") in _TERMINAL_VERDICTS


# ── Recipient lookup ──────────────────────────────────────────────────


def _resolve_recipient_user():
    """Return the User row Rigby reports to (per the contract).

    Rigby's ``runs_as_username`` is the user she acts as server-side
    AND the user who should see her shift reports. v0: chris.
    """
    UserModel = get_user_model()
    return UserModel.objects.filter(
        username=RIGBY.runs_as_username
    ).first()


# ── Thread get-or-create ──────────────────────────────────────────────


def _get_or_create_thread(recipient_user):
    """Find or create the single persistent thread for this (employee, job).

    Lookup is keyed by ``metadata.employee + metadata.job`` so subject
    typos cannot create duplicates. If two threads exist for the same
    key (race / migration anomaly), the oldest one wins — we log a
    warning rather than fail.
    """
    from core.models_messaging import MessageThread, ThreadParticipant

    qs = MessageThread.objects.filter(
        metadata__employee=EMPLOYEE_KEY,
        metadata__job=JOB_KEY,
        is_archived=False,
    ).order_by("created_at")

    existing = list(qs[:2])
    if len(existing) > 1:
        logger.warning(
            "[employee_comms] multiple shift-report threads exist for "
            "(employee=%s, job=%s); using oldest %s. Cleanup advised.",
            EMPLOYEE_KEY, JOB_KEY, existing[0].id,
        )
    if existing:
        thread = existing[0]
    else:
        thread = MessageThread.objects.create(
            subject=THREAD_SUBJECT,
            thread_type="dm",
            metadata={
                "employee": EMPLOYEE_KEY,
                "job": JOB_KEY,
                "thread_kind": THREAD_KIND,
            },
        )

    if recipient_user is not None:
        ThreadParticipant.objects.get_or_create(
            thread=thread, user=recipient_user
        )

    return thread


# ── Idempotency check ─────────────────────────────────────────────────


def _existing_dm_for_mission(thread, mission_id_str: str):
    """Return any existing DM in this thread keyed to this mission_id."""
    from core.models_messaging import DirectMessage

    return DirectMessage.objects.filter(
        thread=thread,
        metadata__mission_id=mission_id_str,
    ).first()


# ── Public entry point ───────────────────────────────────────────────


def post_shift_report(mission) -> Dict[str, Any]:
    """Post one DirectMessage shift report for a terminal mission.

    Idempotent on (thread, mission_id). Non-terminal missions return
    a ``skipped`` envelope. Recipient-user-missing also skips (never
    raises) so a cascade failure here can never crash the docs task.

    Returns::
        {
            ok: bool,
            created: bool,                # true on first write
            skipped_reason: str | None,   # 'non_terminal', 'duplicate',
                                          # 'no_recipient', or None
            thread_id: str | None,
            message_id: str | None,
        }
    """
    from core.models_messaging import DirectMessage

    if not _is_terminal(mission):
        return {
            "ok": True,
            "created": False,
            "skipped_reason": "non_terminal",
            "thread_id": None,
            "message_id": None,
        }

    recipient = _resolve_recipient_user()
    if recipient is None:
        logger.warning(
            "[employee_comms] no recipient user found "
            "(username=%s); skipping shift report for mission %s.",
            RIGBY.runs_as_username, mission.id,
        )
        return {
            "ok": True,
            "created": False,
            "skipped_reason": "no_recipient",
            "thread_id": None,
            "message_id": None,
        }

    thread = _get_or_create_thread(recipient)
    mission_id_str = str(mission.id)

    existing_dm = _existing_dm_for_mission(thread, mission_id_str)
    if existing_dm is not None:
        return {
            "ok": True,
            "created": False,
            "skipped_reason": "duplicate",
            "thread_id": str(thread.id),
            "message_id": str(existing_dm.id),
        }

    summary = mission.summary or {}
    body = _format_body(mission, summary)
    metadata = _build_metadata(mission, summary)

    # sender=None (Rigby has no User row); sender_type='rigby' is the
    # discriminator the inbox UI uses to render her name.
    msg = DirectMessage.objects.create(
        thread=thread,
        sender=None,
        sender_type="rigby",
        body=body,
        metadata=metadata,
    )

    # Bump thread updated_at so the inbox list orders this thread to top.
    thread.updated_at = timezone.now()
    thread.save(update_fields=["updated_at"])

    logger.info(
        "[employee_comms] shift_report mission=%s verdict=%s "
        "thread=%s message=%s",
        mission_id_str,
        summary.get("verdict"),
        thread.id,
        msg.id,
    )

    return {
        "ok": True,
        "created": True,
        "skipped_reason": None,
        "thread_id": str(thread.id),
        "message_id": str(msg.id),
    }
