"""
Employee Communications (Session 1253 PR 4 + PR-A).

Generic shift-report helper. ANY (employee, job) pair can post one
DirectMessage per terminal mission into a persistent inbox thread.

PR-A (generalization): the helper is no longer hardcoded to Rigby /
Documentation Manager. Job-specific configuration (thread subject,
body formatter, extra metadata keys) is passed in by the caller — the
Documentation Manager calls go through ``core.employees.comms_docs_manager``
which carries the docs-specific defaults. See
``docs/EMPLOYEE_OS_PRIMITIVES.md`` for the full lifecycle and the
anti-duplication matrix.

Hard contract (preserved across the refactor):

  * One persistent thread per (employee, job), keyed by
    ``metadata.employee`` + ``metadata.job``. Deterministic
    get-or-create. Subject ignored on lookup so typos cannot duplicate.
  * One DM per terminal mission. Idempotent on (thread, mission_id) —
    re-calling the helper for the same mission is a no-op.
  * Non-terminal missions (status='running' / 'pending') produce no DM.
  * Bounded JSON metadata only — never the full error tail.
  * Additive to existing Deliverable + PA-chat escalation. No
    replacement of either.
  * No push notification, no mobile work, no proactive-notification
    chain, no write surface to the LLM.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional, Sequence

from django.utils import timezone


logger = logging.getLogger(__name__)


# ── Shared constants ─────────────────────────────────────────────────


THREAD_KIND = "employee_shift_report"

# Terminal statuses + verdicts (anything else means "still in flight").
_TERMINAL_STATUSES = {"passed", "failed", "partial"}
_TERMINAL_VERDICTS = {"certified", "rejected", "deferred"}

# Base metadata keys every shift report carries. Job-specific helpers
# may extend this set via ``extra_metadata_keys``, but never replace it.
BASE_METADATA_KEYS: tuple[str, ...] = (
    "employee",
    "job",
    "mission_id",
    "verdict",
    "status",
    "wall_time_ms",
)


# ── Body formatter (generic default) ─────────────────────────────────


BodyFormatter = Callable[[Any, Dict[str, Any]], str]


def default_body_formatter(mission, summary: Dict[str, Any]) -> str:
    """Generic shift-report body when the caller supplies no formatter.

    Job-specific helpers (e.g. ``comms_docs_manager.format_body``)
    override this with templates approved by the job owner. The default
    is a safe, structured one-liner that mentions verdict + mission_id +
    wall time. Never references job-specific keys like ``failed_step``
    or ``drift_count`` — those belong to docs-cascade specifics.
    """
    verdict = summary.get("verdict") or "<unknown>"
    wall_ms = summary.get("wall_time_ms")
    seconds = (
        f"{wall_ms / 1000:.1f}s"
        if isinstance(wall_ms, (int, float))
        else "unknown duration"
    )
    return (
        f"Mission {mission.id} reached terminal verdict "
        f"{verdict!r} (wall {seconds})."
    )


# ── Metadata projection ──────────────────────────────────────────────


def _build_metadata(
    *,
    employee_key: str,
    job_key: str,
    mission,
    summary: Dict[str, Any],
    extra_metadata_keys: Sequence[str],
) -> Dict[str, Any]:
    """Project mission summary into the bounded inbox-DM metadata shape.

    Always carries ``BASE_METADATA_KEYS``. Caller-supplied
    ``extra_metadata_keys`` are appended verbatim — caller is
    responsible for keeping that set small and JSON-safe (never an
    unbounded error tail, full LLM output, etc.).
    """
    meta: Dict[str, Any] = {
        "employee": employee_key,
        "job": job_key,
        "mission_id": str(mission.id),
        "verdict": summary.get("verdict"),
        "status": mission.status,
        "wall_time_ms": summary.get("wall_time_ms"),
    }
    for key in extra_metadata_keys:
        # Job-specific keys come straight from the summary; missing →
        # null so the shape is stable.
        meta[key] = summary.get(key)
    return meta


# ── Terminal-state gate ─────────────────────────────────────────────


def _is_terminal(mission) -> bool:
    """True iff the mission has reached a final state.

    Checks both ``OpsRun.status`` and ``summary.verdict`` — either side
    landing terminal is sufficient. Status alone is enough on its own;
    verdict alone catches the case where verdict was emitted but the
    status field hasn't been refreshed yet on the caller's handle.
    """
    if mission.status in _TERMINAL_STATUSES:
        return True
    summary = mission.summary or {}
    return summary.get("verdict") in _TERMINAL_VERDICTS


# ── Recipient lookup ─────────────────────────────────────────────────


def _resolve_recipient_user(employee):
    """Return the User the employee reports to (per the contract).

    Reads ``employee.runs_as_username`` — every AIEmployee declares it.
    """
    from django.contrib.auth import get_user_model

    UserModel = get_user_model()
    return UserModel.objects.filter(
        username=employee.runs_as_username
    ).first()


# ── Thread get-or-create ─────────────────────────────────────────────


def _get_or_create_thread(
    *,
    employee_key: str,
    job_key: str,
    recipient_user,
    subject: str,
):
    """Find or create the single persistent thread for (employee, job).

    Lookup is keyed by ``metadata.employee + metadata.job`` only —
    subject typos cannot cause duplicates. If multiple threads exist
    for the same key (race / migration anomaly), the oldest wins and
    we log a warning so cleanup can be scheduled.

    Archived threads are intentionally excluded; if a thread was
    archived, the helper creates a fresh one rather than reactivating.
    """
    from core.models_messaging import MessageThread, ThreadParticipant

    qs = MessageThread.objects.filter(
        metadata__employee=employee_key,
        metadata__job=job_key,
        is_archived=False,
    ).order_by("created_at")

    existing = list(qs[:2])
    if len(existing) > 1:
        logger.warning(
            "[employee_comms] multiple shift-report threads exist for "
            "(employee=%s, job=%s); using oldest %s. Cleanup advised.",
            employee_key, job_key, existing[0].id,
        )
    if existing:
        thread = existing[0]
    else:
        thread = MessageThread.objects.create(
            subject=subject,
            thread_type="dm",
            metadata={
                "employee": employee_key,
                "job": job_key,
                "thread_kind": THREAD_KIND,
            },
        )

    if recipient_user is not None:
        ThreadParticipant.objects.get_or_create(
            thread=thread, user=recipient_user
        )

    return thread


# ── Idempotency check ────────────────────────────────────────────────


def _existing_dm_for_mission(thread, mission_id_str: str):
    """Return any existing DM in this thread keyed to this mission_id."""
    from core.models_messaging import DirectMessage

    return DirectMessage.objects.filter(
        thread=thread,
        metadata__mission_id=mission_id_str,
    ).first()


# ── Public entry point ───────────────────────────────────────────────


def post_shift_report(
    *,
    employee,
    job: str,
    mission,
    body_formatter: Optional[BodyFormatter] = None,
    extra_metadata_keys: Sequence[str] = (),
    thread_subject: Optional[str] = None,
    sender_type: str = "system",
) -> Dict[str, Any]:
    """Post one shift-report DM for a terminal mission.

    Args:
        employee: an ``AIEmployee`` (frozen dataclass) — must expose
            ``handle``, ``display_name``, ``runs_as_username``.
        job: the job key string (e.g. ``"docs_manager"``).
        mission: an OpsRun row with ``id``, ``status``, ``summary``.
        body_formatter: optional callable
            ``(mission, summary) -> str``. Defaults to a generic
            "Mission <id> reached verdict X" one-liner. Job-specific
            templates (e.g., docs_manager's "passed/failed/deferred"
            shape) live in their own module and are passed in here.
        extra_metadata_keys: optional sequence of additional summary
            keys to include in the DM metadata beyond
            ``BASE_METADATA_KEYS``. Caller MUST keep this set small
            and JSON-safe (no error_tail, no full LLM payloads).
        thread_subject: optional thread title. Defaults to
            ``"{employee.display_name} — {job}"``.
        sender_type: ``DirectMessage.sender_type`` value to use.
            Defaults to ``"system"``. Rigby callers pass ``"rigby"``
            (one of the model's allowed choices). Constrained by
            ``DirectMessage.SENDER_TYPE_CHOICES`` (max_length=10).

    Idempotent on (thread, mission_id). Non-terminal missions return
    a ``skipped`` envelope. Recipient-user-missing also skips (never
    raises) so a comms failure can never crash the caller.

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

    employee_key = employee.handle
    job_key = job

    if not _is_terminal(mission):
        return {
            "ok": True,
            "created": False,
            "skipped_reason": "non_terminal",
            "thread_id": None,
            "message_id": None,
        }

    recipient = _resolve_recipient_user(employee)
    if recipient is None:
        logger.warning(
            "[employee_comms] no recipient user found "
            "(employee=%s username=%s); skipping shift report for "
            "mission %s.",
            employee_key, employee.runs_as_username, mission.id,
        )
        return {
            "ok": True,
            "created": False,
            "skipped_reason": "no_recipient",
            "thread_id": None,
            "message_id": None,
        }

    subject = (
        thread_subject
        if thread_subject is not None
        else f"{employee.display_name} — {job_key}"
    )
    thread = _get_or_create_thread(
        employee_key=employee_key,
        job_key=job_key,
        recipient_user=recipient,
        subject=subject,
    )

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
    formatter: BodyFormatter = body_formatter or default_body_formatter
    body = formatter(mission, summary)
    metadata = _build_metadata(
        employee_key=employee_key,
        job_key=job_key,
        mission=mission,
        summary=summary,
        extra_metadata_keys=tuple(extra_metadata_keys),
    )

    # sender=None: AI employees have no User row. sender_type is the
    # discriminator the inbox UI uses to render the employee name;
    # constrained by DirectMessage.SENDER_TYPE_CHOICES.
    msg = DirectMessage.objects.create(
        thread=thread,
        sender=None,
        sender_type=sender_type,
        body=body,
        metadata=metadata,
    )

    thread.updated_at = timezone.now()
    thread.save(update_fields=["updated_at"])

    logger.info(
        "[employee_comms] shift_report employee=%s job=%s "
        "mission=%s verdict=%s thread=%s message=%s",
        employee_key, job_key, mission_id_str,
        summary.get("verdict"), thread.id, msg.id,
    )

    return {
        "ok": True,
        "created": True,
        "skipped_reason": None,
        "thread_id": str(thread.id),
        "message_id": str(msg.id),
    }
