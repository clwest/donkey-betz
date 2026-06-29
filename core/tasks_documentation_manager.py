"""
Documentation Manager daily routine (Session 1252 PR 2).

One Celery task that runs Rigby's Documentation Manager job:

  1. Capture before-counts (Document + DocumentEmbedding + size of
     docs/_index.json after step 1).
  2. Run the 4-step docs cascade:
       - build_docs_index           (call_command, fast)
       - build_rag_corpus           (call_command, fast)
       - sync_docs_index_to_documents       (call_command, fast)
       - sync_docs_index_to_documents --embed  (subprocess.run with
         timeout=1800, 600s warning timer)
  3. Capture after-counts + drift observation
     (`verify_doc_claims --only-drift --format json`).
  4. On success: emit verdict_issued:certified via PR 1's helper. Silent.
  5. On failure: dedupe against last-24h same-signature OpsRun; either
     append to the prior escalation Deliverable OR create a new
     publish_candidate Deliverable. Then flip status to ready via the
     canonical content_tool/deliverable_tool.set_status path. Then post
     a one-line summary to Rigby's pinned PA conversation. Emit
     verdict_issued:rejected.

Idempotent within the same calendar day — second invocation returns
the existing mission_id with already_ran=True.

Contract source: ``core.employees.jobs.DOCUMENTATION_MANAGER``.
Verdict surface: ``core.employees.mission_verdict.emit_mission_verdict``.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import subprocess
import threading
import time
import uuid
from datetime import timedelta
from io import StringIO
from pathlib import Path
from typing import Any, Optional

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone

from core.employees import DOCUMENTATION_MANAGER, RIGBY
from core.employees.mission_verdict import (
    VERDICT_CERTIFIED,
    VERDICT_REJECTED,
    emit_mission_verdict,
)
from core.models_ops_runs import OpsRun, OpsRunEvent

logger = logging.getLogger(__name__)


# ── Constants ─────────────────────────────────────────────────────────

MISSION_RUN_KIND = "docs_cascade"

CASCADE_STEPS = [
    # (step_number, label_prefix, command_name, extra_args, runner)
    (1, "step_1_index", "build_docs_index", [], "call_command"),
    (2, "step_2_corpus", "build_rag_corpus", [], "call_command"),
    (3, "step_3_sync", "sync_docs_index_to_documents", [], "call_command"),
    # Step 4 runs via subprocess.run so the hard timeout actually fires;
    # Python call_command has no interruption surface.
    (4, "step_4_embed", "sync_docs_index_to_documents", ["--embed"], "subprocess"),
]

DRIFT_LABEL = "step_5_drift_observed"
ESCALATION_LABEL = "escalation_emitted"
RUN_STARTED_LABEL = "run_started"

# First-escalation error tail length per Rigby Q5; recurrence trim per Rigby Q7.
ERROR_TAIL_LINES_FIRST = 100
ERROR_TAIL_LINES_RECURRENCE = 30

# Step 4 timeout (per JobContract.embed_step_timeout)
_STEP_4_WARNING_SECONDS = DOCUMENTATION_MANAGER.embed_step_timeout.get(
    "warning_seconds", 600
)
_STEP_4_HARD_SECONDS = DOCUMENTATION_MANAGER.embed_step_timeout.get(
    "hard_seconds", 1800
)

# Dedupe window
DEDUPE_WINDOW_HOURS = 24

# Confidence values per outcome
CONFIDENCE_SUCCESS_FULL = 0.95
CONFIDENCE_SUCCESS_DEGRADED = 0.6
CONFIDENCE_FAILURE = 0.0

DOCS_INDEX_JSON_PATH = Path(settings.BASE_DIR) / "docs" / "_index.json"

# Status path used in escalation Deliverables; matches the contract.
DELIVERABLE_TITLE_PREFIX = "Docs Manager Escalation"

# Workspace lookup name for escalation Deliverables (per Rigby answer).
DONKEY_BETZ_WORKSPACE_NAME = "Donkey Betz"


# ── Idempotency ───────────────────────────────────────────────────────


def _existing_mission_for_today() -> Optional[OpsRun]:
    """Return any docs_cascade mission already started today (local).

    Returns the most recent one if multiple exist (shouldn't happen in
    practice — this is the safety net).
    """
    today = timezone.localtime().date()
    return (
        OpsRun.objects.filter(
            domain="mission",
            run_kind=MISSION_RUN_KIND,
            started_at__date=today,
        )
        .order_by("-started_at")
        .first()
    )


# ── Event emission helpers ────────────────────────────────────────────


def _emit_event(
    mission: OpsRun, label: str, event_type: str, **detail: Any
) -> OpsRunEvent:
    """Idempotent ``(run, label)`` event creation.

    Matches the S1250 rigby_event_intake pattern — get_or_create so
    re-runs of the same step against the same mission don't duplicate
    timeline rows.
    """
    event, _created = OpsRunEvent.objects.get_or_create(
        run=mission,
        label=label,
        defaults={"event_type": event_type, "detail": detail},
    )
    return event


# ── Count probes ──────────────────────────────────────────────────────


def _safe_count(label: str, fn) -> tuple[Optional[int], Optional[str]]:
    """Run a count probe; return (value, error_str) — never raises.

    Per Rigby Q3: a failed probe sets degraded_evidence=True but does
    NOT escalate. Returning (None, "<error>") lets the caller decide
    how to surface the gap.
    """
    try:
        return int(fn()), None
    except Exception as exc:  # pragma: no cover — defensive
        logger.warning(
            "[DOCS_MANAGER_PROBE] label=%s error=%s: %s",
            label,
            type(exc).__name__,
            exc,
        )
        return None, f"{type(exc).__name__}: {exc}"


def _probe_documents_count() -> Optional[int]:
    """ORM count of Document rows. None if model import fails."""
    val, _err = _safe_count(
        "documents_count",
        lambda: __import__(
            "content.models", fromlist=["Document"]
        ).Document.objects.count(),
    )
    return val


def _probe_embeddings_count() -> Optional[int]:
    """ORM count of DocumentEmbedding rows. None if model import fails."""
    val, _err = _safe_count(
        "embeddings_count",
        lambda: __import__(
            "content.models", fromlist=["DocumentEmbedding"]
        ).DocumentEmbedding.objects.count(),
    )
    return val


def _probe_docs_indexed_count() -> Optional[int]:
    """Derive from docs/_index.json (Rigby Q2: NOT from file size)."""
    try:
        with open(DOCS_INDEX_JSON_PATH, encoding="utf-8") as f:
            payload = json.load(f)
        docs = payload.get("documents")
        if isinstance(docs, list):
            return len(docs)
        return None
    except Exception as exc:  # pragma: no cover — defensive
        logger.warning(
            "[DOCS_MANAGER_PROBE] docs_indexed_count error=%s: %s",
            type(exc).__name__,
            exc,
        )
        return None


# ── Step 4 timeout warning (Rigby Q4 option c) ────────────────────────


def _start_warning_timer(
    mission: OpsRun, warning_seconds: int = _STEP_4_WARNING_SECONDS
) -> threading.Timer:
    """Schedule a one-shot warning emission at ``warning_seconds`` in.

    Fires only if the cascade is still in step 4. Caller MUST call
    ``.cancel()`` on the returned Timer once step 4 completes (success
    or failure) to prevent the warning firing on already-finished runs.
    """

    def _fire():
        try:
            logger.warning(
                "[DOCS_MANAGER_STEP_4_SLOW] elapsed_seconds=%d mission_id=%s",
                warning_seconds,
                mission.id,
            )
            _emit_event(
                mission,
                "step_4_warning",
                "info",
                elapsed_seconds=warning_seconds,
                note=(
                    "Step 4 (embed) still running past warning threshold. "
                    "No behavior change — hard timeout at "
                    f"{_STEP_4_HARD_SECONDS}s."
                ),
            )
        except Exception as exc:  # pragma: no cover — defensive
            logger.warning(
                "[DOCS_MANAGER_STEP_4_WARNING] emit failed: %s", exc
            )

    timer = threading.Timer(warning_seconds, _fire)
    timer.daemon = True
    timer.start()
    return timer


# ── Cascade step runners ──────────────────────────────────────────────


def _run_call_command_step(
    mission: OpsRun, step_num: int, label_prefix: str,
    cmd: str, extra_args: list[str],
) -> tuple[bool, str, int]:
    """Run a step via Django's call_command. Returns (passed, output, duration_ms).

    Captures combined stdout+stderr into a StringIO so error_tail can
    be derived on failure.
    """
    _emit_event(mission, f"{label_prefix}_started", "step_start", cmd=cmd)
    start = time.monotonic()
    captured = StringIO()
    try:
        call_command(cmd, *extra_args, stdout=captured, stderr=captured)
        duration_ms = int((time.monotonic() - start) * 1000)
        _emit_event(
            mission,
            f"{label_prefix}_passed",
            "step_pass",
            cmd=cmd,
            duration_ms=duration_ms,
            exit_code=0,
        )
        return True, captured.getvalue(), duration_ms
    except SystemExit as exc:
        # Django commands raise SystemExit on failure
        duration_ms = int((time.monotonic() - start) * 1000)
        output = captured.getvalue()
        _emit_event(
            mission,
            f"{label_prefix}_failed",
            "step_fail",
            cmd=cmd,
            duration_ms=duration_ms,
            exit_code=int(getattr(exc, "code", 1) or 1),
            error_summary=_tail_lines(output, 5),
        )
        return False, output, duration_ms
    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        output = captured.getvalue() + f"\n{type(exc).__name__}: {exc}"
        _emit_event(
            mission,
            f"{label_prefix}_failed",
            "step_fail",
            cmd=cmd,
            duration_ms=duration_ms,
            exit_code=1,
            error_summary=f"{type(exc).__name__}: {exc}",
        )
        return False, output, duration_ms


def _run_subprocess_step(
    mission: OpsRun, step_num: int, label_prefix: str,
    cmd: str, extra_args: list[str],
    hard_timeout: int = _STEP_4_HARD_SECONDS,
) -> tuple[bool, str, int, bool]:
    """Run a step via subprocess so hard timeout actually fires.

    Returns (passed, combined_output, duration_ms, was_timeout).
    """
    _emit_event(
        mission,
        f"{label_prefix}_started",
        "step_start",
        cmd=cmd,
        extra_args=extra_args,
        hard_timeout_seconds=hard_timeout,
    )
    warning_timer = _start_warning_timer(mission)
    start = time.monotonic()
    argv = ["python", "manage.py", cmd, *extra_args]
    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=hard_timeout,
            check=False,
        )
        duration_ms = int((time.monotonic() - start) * 1000)
        warning_timer.cancel()
        output = (completed.stdout or "") + (completed.stderr or "")
        passed = completed.returncode == 0
        _emit_event(
            mission,
            f"{label_prefix}_passed" if passed else f"{label_prefix}_failed",
            "step_pass" if passed else "step_fail",
            cmd=cmd,
            duration_ms=duration_ms,
            exit_code=completed.returncode,
            error_summary=None if passed else _tail_lines(output, 5),
        )
        return passed, output, duration_ms, False
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        warning_timer.cancel()
        output = (exc.stdout or b"").decode("utf-8", errors="replace") + (
            exc.stderr or b""
        ).decode("utf-8", errors="replace")
        _emit_event(
            mission,
            f"{label_prefix}_failed",
            "step_fail",
            cmd=cmd,
            duration_ms=duration_ms,
            exit_code="timeout",
            timeout_seconds=hard_timeout,
            error_summary=f"TimeoutExpired after {hard_timeout}s",
        )
        return False, output, duration_ms, True


# ── Drift observation (Rigby Q3) ──────────────────────────────────────


def _run_drift_observation(
    mission: OpsRun,
) -> tuple[Optional[int], Optional[int], bool]:
    """Run `verify_doc_claims --only-drift --format json`.

    Returns (drift_count, drift_items_count, degraded_evidence_for_drift).
    Never raises — gracefully degrades to (None, None, True) if the
    command output isn't parseable as JSON.
    """
    captured = StringIO()
    try:
        call_command(
            "verify_doc_claims",
            "--only-drift",
            "--format", "json",
            stdout=captured,
            stderr=captured,
        )
    except Exception as exc:
        logger.warning(
            "[DOCS_MANAGER_DRIFT] command failed: %s: %s",
            type(exc).__name__,
            exc,
        )
        _emit_event(
            mission,
            DRIFT_LABEL,
            "info",
            drift_count=None,
            drift_items_count=None,
            degraded_evidence=True,
            error=f"{type(exc).__name__}: {exc}",
        )
        return None, None, True

    raw = captured.getvalue().strip()
    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        # Fallback: regex parse for "Drift: N" style human output.
        match = re.search(
            r"drift[^0-9]*(\d+)", raw, re.IGNORECASE
        )
        if match:
            drift_count = int(match.group(1))
            _emit_event(
                mission, DRIFT_LABEL, "info",
                drift_count=drift_count,
                drift_items_count=None,
                degraded_evidence=False,
                source="regex_parse",
            )
            return drift_count, None, False
        _emit_event(
            mission, DRIFT_LABEL, "info",
            drift_count=None,
            drift_items_count=None,
            degraded_evidence=True,
            reason="output_not_parseable",
        )
        return None, None, True

    # Successful JSON parse — try several common shapes.
    drift_count = None
    drift_items_count = None
    if isinstance(payload, dict):
        # Shape A: {"drift": N, "items": [...]}
        drift_count = payload.get("drift") or payload.get("drift_count")
        items = payload.get("items") or payload.get("drift_items")
        if isinstance(items, list):
            drift_items_count = len(items)
        # Shape B: aggregate-only — count rows with status != ok
        if drift_count is None and "results" in payload:
            results = payload.get("results") or []
            if isinstance(results, list):
                drift_count = sum(
                    1 for r in results
                    if isinstance(r, dict) and r.get("status") != "ok"
                )
                drift_items_count = len(results)

    degraded = drift_count is None
    _emit_event(
        mission, DRIFT_LABEL, "info",
        drift_count=drift_count,
        drift_items_count=drift_items_count,
        degraded_evidence=degraded,
        source="json_parse",
    )
    return drift_count, drift_items_count, degraded


# ── Error tail + signature helpers ────────────────────────────────────


def _tail_lines(text: str, n: int) -> str:
    """Return the last n lines of text, joined by newlines."""
    if not text:
        return ""
    lines = text.splitlines()
    return "\n".join(lines[-n:])


_TIMESTAMP_PATTERNS = [
    # ISO-8601-like timestamps (2026-06-28T18:42:10, with optional ms/tz)
    re.compile(
        r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?"
    ),
    # Bare HH:MM:SS
    re.compile(r"\b\d{2}:\d{2}:\d{2}(?:[.,]\d+)?\b"),
    # Unix epoch-ish floats (10+ digits, optional decimals)
    re.compile(r"\b\d{10,}(?:\.\d+)?\b"),
    # UUIDs (likely to be per-run identifiers; not stable across failures)
    re.compile(
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
    ),
]


def _normalize_for_signature(text: str) -> str:
    """Strip volatile substrings before hashing so the same error type
    on different runs produces the same signature."""
    normalized = text
    for pat in _TIMESTAMP_PATTERNS:
        normalized = pat.sub("<TS>", normalized)
    # Collapse runs of whitespace so trivial formatting variation doesn't
    # change the hash.
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _signature_for(failed_step: str, error_tail: str) -> str:
    """SHA256 hex of (failed_step + normalized error_tail), prefix 16."""
    payload = (
        failed_step.strip() + "||" + _normalize_for_signature(error_tail)
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


# ── User + dispatcher helpers ─────────────────────────────────────────


def _resolve_runs_as_user_id() -> Optional[Any]:
    """Return the User.id Rigby acts as (per RIGBY.runs_as_username)."""
    User = get_user_model()
    user = User.objects.filter(
        username__iexact=RIGBY.runs_as_username
    ).first()
    return getattr(user, "id", None) if user else None


def _resolve_active_pin() -> str:
    """Active PA pin per the settings/contract fallback chain.

    Per the PR 2 design call: env-resolved value wins; contract constant
    is the fallback. Lets the pin rotate without amending the contract
    code every ~10-15 sessions.
    """
    return (
        getattr(settings, "RIGBY_PRIMARY_PA_PIN", None)
        or RIGBY.primary_chat_id
    )


def _resolve_workspace_id() -> Optional[Any]:
    """Look up the Donkey Betz workspace UUID. None if missing."""
    try:
        from core.models_skin_layer import ProjectWorkspace

        ws = ProjectWorkspace.objects.filter(
            name__iexact=DONKEY_BETZ_WORKSPACE_NAME
        ).first()
        return ws.id if ws else None
    except Exception as exc:
        logger.warning(
            "[DOCS_MANAGER_WORKSPACE] lookup failed: %s: %s",
            type(exc).__name__,
            exc,
        )
        return None


# ── Escalation flow ───────────────────────────────────────────────────


def _find_prior_escalation_run(
    failed_step: str, signature: str, current_mission_id: Any,
) -> Optional[OpsRun]:
    """Last 24h, same failed_step + same error_signature.

    Per Rigby Q7: lookup is OpsRun-first (source of truth), not by
    Deliverable title search.
    """
    cutoff = timezone.now() - timedelta(hours=DEDUPE_WINDOW_HOURS)
    return (
        OpsRun.objects.filter(
            domain="mission",
            run_kind=MISSION_RUN_KIND,
            status="failed",
            finished_at__gte=cutoff,
            summary__failed_step=failed_step,
            summary__error_signature=signature,
        )
        .exclude(id=current_mission_id)
        .order_by("-finished_at")
        .first()
    )


def _build_escalation_body(
    *,
    today_str: str,
    failed_step: str,
    when_iso: str,
    run_duration_label: str,
    error_tail: str,
    error_signature: str,
    counts_so_far: dict,
    ops_run_id: Any,
    what_i_did: str,
) -> str:
    """Build the escalation Deliverable body per Rigby Q5."""
    lines = [
        f"# Docs Manager Escalation — {today_str}",
        "",
        f"**failed_step:** `{failed_step}`",
        f"**when:** {when_iso}  ",
        f"**run_duration_so_far:** {run_duration_label}",
        f"**error_signature:** `{error_signature}`",
        f"**ops_run_id:** `{ops_run_id}`",
        "",
        "## what_i_did",
        what_i_did,
        "",
        "## counts_so_far",
        "```json",
        json.dumps(counts_so_far, indent=2, sort_keys=True),
        "```",
        "",
        "## error_tail (last 100 lines)",
        "```",
        error_tail or "(empty)",
        "```",
        "",
        "---",
        "**Chris: approve next action (retry / investigate / "
        "assign Claude Code fix).**",
    ]
    return "\n".join(lines)


def _create_or_append_escalation_deliverable(
    *,
    mission: OpsRun,
    failed_step: str,
    error_tail: str,
    error_signature: str,
    counts_so_far: dict,
) -> tuple[str, bool, Optional[str]]:
    """Create a new escalation Deliverable or append to a prior one.

    Returns (deliverable_id_str, deduped, prior_ops_run_id_str_or_None).
    """
    from core.models_deliverables import Deliverable, PublishIntent

    prior_run = _find_prior_escalation_run(
        failed_step=failed_step,
        signature=error_signature,
        current_mission_id=mission.id,
    )

    if prior_run:
        prior_deliverable_id = (prior_run.summary or {}).get(
            "escalation_deliverable_id"
        )
        if prior_deliverable_id:
            try:
                prior = Deliverable.objects.get(id=prior_deliverable_id)
            except Deliverable.DoesNotExist:
                prior = None
        else:
            prior = None
        if prior is not None:
            stanza = (
                f"\n\n## Recurrence: {timezone.now().isoformat()}\n"
                f"- ops_run: `{mission.id}`\n"
                f"- error_tail (last "
                f"{ERROR_TAIL_LINES_RECURRENCE} lines):\n"
                "```\n"
                f"{_tail_lines(error_tail, ERROR_TAIL_LINES_RECURRENCE)}\n"
                "```\n"
            )
            existing = prior.content or ""
            prior.content = existing + stanza
            prior.preview_content = (
                prior.content[:500]
                + ("..." if len(prior.content) > 500 else "")
            )
            prior.save(
                update_fields=["content", "preview_content", "updated_at"]
            )
            return str(prior.id), True, str(prior_run.id)

    # New escalation.
    today_local = timezone.localtime()
    today_str = today_local.strftime("%Y-%m-%d")
    when_iso = today_local.isoformat()
    finished = mission.finished_at or timezone.now()
    duration_seconds = int(
        (finished - mission.started_at).total_seconds()
    )
    minutes, seconds = divmod(duration_seconds, 60)
    run_duration_label = f"{minutes}m {seconds}s"

    body = _build_escalation_body(
        today_str=today_str,
        failed_step=failed_step,
        when_iso=when_iso,
        run_duration_label=run_duration_label,
        error_tail=_tail_lines(error_tail, ERROR_TAIL_LINES_FIRST),
        error_signature=error_signature,
        counts_so_far=counts_so_far,
        ops_run_id=mission.id,
        what_i_did=(
            f"Ran cascade step `{failed_step}`; "
            "process exited non-zero / timed out."
        ),
    )

    workspace_id = _resolve_workspace_id()
    deliverable = Deliverable(
        title=f"{DELIVERABLE_TITLE_PREFIX} — {today_str}",
        slug=f"docs-manager-escalation-{today_str}-{uuid.uuid4().hex[:8]}",
        deliverable_type="report",
        publish_intent=PublishIntent.PUBLISH_CANDIDATE,
        category="ops",
        content=body,
        preview_content=body[:500] + ("..." if len(body) > 500 else ""),
        workspace_id=workspace_id,
    )
    deliverable.save()

    # Per contract escalation_visibility step 2: force the new
    # publish_candidate deliverable from the create-default `completed`
    # to a visible `ready` state via the canonical set_status path.
    _force_deliverable_ready(deliverable.id)

    return str(deliverable.id), False, None


def _force_deliverable_ready(deliverable_id: Any) -> None:
    """Flip a newly-created Deliverable from completed→ready.

    Mirrors the contract of ``deliverable_tool action=set_status`` —
    stashes ``_transition_context`` on the instance so the
    ``deliverable_status_signals.record_status_transition`` post_save
    receiver fires a ``DeliverableEvent('status_transition')`` row,
    then saves with ``update_fields=['status']`` — but applies the
    mutation directly through the ORM instead of going through the
    PA dispatcher's ``execute_sync`` (which opens a fresh asyncio
    event loop and would close the Django DB connection mid-task).

    Per memory rule feedback_deliverable_create_defaults_to_completed.md,
    new Deliverable rows land as ``completed`` regardless of the
    explicit param — this is the standard workaround.
    """
    from core.models_deliverables import Deliverable

    user_id = _resolve_runs_as_user_id()
    try:
        obj = Deliverable.objects.get(id=deliverable_id)
    except Deliverable.DoesNotExist:
        logger.warning(
            "[DOCS_MANAGER_SET_STATUS] deliverable=%s not found",
            deliverable_id,
        )
        return

    from_status = obj.status
    if from_status not in ("completed", "ready"):
        # Set_status whitelist only allows completed↔ready transitions;
        # other states would error if dispatched. Skip silently — log
        # the surprise so we notice if it ever happens.
        logger.warning(
            "[DOCS_MANAGER_SET_STATUS] deliverable=%s unexpected "
            "from_status=%s; not flipping",
            deliverable_id, from_status,
        )
        return
    if from_status == "ready":
        # Already at target — nothing to do (idempotent on re-run).
        return

    obj._transition_context = {
        "reason": (
            "Docs Manager escalation: force visible state for "
            "Chris review (works around create default-completed bug)."
        ),
        "actor_user_id": str(user_id) if user_id else None,
        "trace_id": None,
        "source": "docs_manager_daily.force_deliverable_ready",
    }
    obj.status = "ready"
    obj.save(update_fields=["status"])


def _post_pa_chat_summary(
    *, failed_step: str, deliverable_id: str, ops_run_id: Any,
) -> Optional[str]:
    """Post the one-line escalation summary into Rigby's pinned PA chat.

    Per Rigby Q6: plain text, no @chris tag. Returns the ChatConversation
    row id (str) or None on failure.
    """
    from core.models import ChatConversation

    user_id = _resolve_runs_as_user_id()
    pin = _resolve_active_pin()
    if not pin:
        logger.warning(
            "[DOCS_MANAGER_PA_POST] no active pin resolved; skipping post"
        )
        return None

    summary = (
        f"Docs Manager FAILED at {failed_step} — escalation deliverable "
        f"{deliverable_id} (OpsRun {ops_run_id})."
    )
    try:
        row = ChatConversation.objects.create(
            conversation_id=pin,
            user_id=user_id,
            user_message="[system: docs_manager escalation]",
            assistant_response=summary,
            metadata={
                "source": "docs_manager_daily",
                "ops_run_id": str(ops_run_id),
                "deliverable_id": deliverable_id,
            },
        )
        return str(getattr(row, "id", "") or "") or None
    except Exception as exc:
        logger.warning(
            "[DOCS_MANAGER_PA_POST] write failed: %s: %s",
            type(exc).__name__,
            exc,
        )
        return None


# ── Mission core ──────────────────────────────────────────────────────


def _run_mission(mission: OpsRun) -> dict:
    """Inner run — separate so the @shared_task wrapper stays thin."""
    summary_acc: dict[str, Any] = {
        "docs_indexed_count": None,
        "documents_count_before": None,
        "documents_count_after": None,
        "embeddings_count_before": None,
        "embeddings_count_after": None,
        "embedding_delta": None,
        "drift_count": None,
        "drift_items_count": None,
        "degraded_evidence": False,
        "wall_time_ms": 0,
        "failed_step": None,
        "error_tail": None,
    }
    cascade_start = time.monotonic()
    _emit_event(mission, RUN_STARTED_LABEL, "info", run_kind=MISSION_RUN_KIND)

    # ── Preflight: before-count probes (per Rigby Q1) ──
    summary_acc["documents_count_before"] = _probe_documents_count()
    summary_acc["embeddings_count_before"] = _probe_embeddings_count()
    if (
        summary_acc["documents_count_before"] is None
        or summary_acc["embeddings_count_before"] is None
    ):
        summary_acc["degraded_evidence"] = True
    _persist_summary(mission, summary_acc)

    # ── Cascade steps 1-4 ──
    failed = False
    accumulated_output = ""
    for step_num, label_prefix, cmd, extra_args, runner in CASCADE_STEPS:
        if runner == "call_command":
            passed, output, _dur = _run_call_command_step(
                mission, step_num, label_prefix, cmd, extra_args
            )
        else:  # subprocess
            passed, output, _dur, _timed_out = _run_subprocess_step(
                mission, step_num, label_prefix, cmd, extra_args
            )
        accumulated_output += f"\n--- {label_prefix} ({cmd}) ---\n{output}"
        if not passed:
            failed = True
            failed_step_str = cmd + (
                " " + " ".join(extra_args) if extra_args else ""
            )
            summary_acc["failed_step"] = failed_step_str
            summary_acc["error_tail"] = _tail_lines(
                accumulated_output, ERROR_TAIL_LINES_FIRST
            )
            summary_acc["error_signature"] = _signature_for(
                failed_step_str, summary_acc["error_tail"] or ""
            )
            # Capture after-counts on failure path too — Document/Embedding
            # state may have partially changed.
            summary_acc["documents_count_after"] = _probe_documents_count()
            summary_acc["embeddings_count_after"] = _probe_embeddings_count()
            summary_acc["embedding_delta"] = _safe_delta(
                summary_acc["embeddings_count_before"],
                summary_acc["embeddings_count_after"],
            )
            # Mark skipped steps explicitly per Rigby Q9.
            for skipped in CASCADE_STEPS:
                if skipped[0] > step_num:
                    _emit_event(
                        mission,
                        f"{skipped[1]}_skipped",
                        "info",
                        reason="prior_failure",
                        cmd=skipped[2],
                    )
            _emit_event(
                mission,
                "step_5_skipped",
                "info",
                reason="prior_failure",
                cmd="verify_doc_claims --only-drift",
            )
            break

    if not failed:
        # ── Step 1 success: derive docs_indexed_count + after-counts ──
        summary_acc["docs_indexed_count"] = _probe_docs_indexed_count()
        summary_acc["documents_count_after"] = _probe_documents_count()
        summary_acc["embeddings_count_after"] = _probe_embeddings_count()
        summary_acc["embedding_delta"] = _safe_delta(
            summary_acc["embeddings_count_before"],
            summary_acc["embeddings_count_after"],
        )
        if any(
            summary_acc[k] is None
            for k in (
                "docs_indexed_count",
                "documents_count_after",
                "embeddings_count_after",
            )
        ):
            summary_acc["degraded_evidence"] = True

        # ── Step 5: drift observation ──
        drift_count, drift_items, drift_degraded = _run_drift_observation(
            mission
        )
        summary_acc["drift_count"] = drift_count
        summary_acc["drift_items_count"] = drift_items
        if drift_degraded:
            summary_acc["degraded_evidence"] = True

    summary_acc["wall_time_ms"] = int(
        (time.monotonic() - cascade_start) * 1000
    )
    _persist_summary(mission, summary_acc)

    # ── Step 6: verdict + escalation if failed ──
    if failed:
        escalation_response = _handle_failure_escalation(
            mission=mission,
            failed_step=summary_acc["failed_step"],
            error_tail=summary_acc["error_tail"] or "",
            error_signature=summary_acc["error_signature"],
            counts_so_far={
                k: summary_acc[k]
                for k in summary_acc
                if k != "error_tail"
            },
        )
        # Re-persist with escalation pointers.
        summary_acc.update(escalation_response)
        _persist_summary(mission, summary_acc)
        verdict_response = emit_mission_verdict(
            mission_id=mission.id,
            verdict=VERDICT_REJECTED,
            confidence=CONFIDENCE_FAILURE,
            evidence_refs=[
                f"deliverable:{escalation_response['escalation_deliverable_id']}",
                f"ops_run:{mission.id}",
            ],
            notes=(
                f"Cascade failed at {summary_acc['failed_step']}. "
                "See escalation deliverable for full evidence."
            ),
            issued_by=RIGBY.handle,
        )
    else:
        # Confidence downgrades when degraded evidence is present.
        confidence = (
            CONFIDENCE_SUCCESS_DEGRADED
            if summary_acc["degraded_evidence"]
            else CONFIDENCE_SUCCESS_FULL
        )
        verdict_response = emit_mission_verdict(
            mission_id=mission.id,
            verdict=VERDICT_CERTIFIED,
            confidence=confidence,
            notes=(
                "Cascade completed cleanly. "
                + ("Counts incomplete (degraded_evidence)." if summary_acc[
                    "degraded_evidence"
                ] else "All counts captured.")
            ),
            issued_by=RIGBY.handle,
        )

    mission.refresh_from_db()
    return {
        "ok": True,
        "mission_id": str(mission.id),
        "status": mission.status,
        "verdict": verdict_response["verdict"],
        "wall_time_ms": summary_acc["wall_time_ms"],
        "summary": summary_acc,
    }


def _persist_summary(mission: OpsRun, summary_acc: dict) -> None:
    """Merge ``summary_acc`` into ``mission.summary`` and save."""
    existing = mission.summary or {}
    mission.summary = {**existing, **summary_acc}
    mission.save(update_fields=["summary"])


def _safe_delta(before: Optional[int], after: Optional[int]) -> Optional[int]:
    if before is None or after is None:
        return None
    return after - before


def _handle_failure_escalation(
    *,
    mission: OpsRun,
    failed_step: str,
    error_tail: str,
    error_signature: str,
    counts_so_far: dict,
) -> dict:
    """Create-or-append escalation Deliverable + post PA summary.

    Returns dict of fields to merge into mission.summary so subsequent
    lookups (and PR 3's status tool) can find the escalation pointers.
    """
    (
        deliverable_id, deduped, prior_ops_run_id,
    ) = _create_or_append_escalation_deliverable(
        mission=mission,
        failed_step=failed_step,
        error_tail=error_tail,
        error_signature=error_signature,
        counts_so_far=counts_so_far,
    )
    pa_post_id = _post_pa_chat_summary(
        failed_step=failed_step,
        deliverable_id=deliverable_id,
        ops_run_id=mission.id,
    )
    _emit_event(
        mission, ESCALATION_LABEL, "info",
        deliverable_id=deliverable_id,
        ops_run_id=str(mission.id),
        error_signature=error_signature,
        deduped=deduped,
        prior_ops_run_id=prior_ops_run_id,
        pa_post_id=pa_post_id,
    )
    return {
        "escalation_deliverable_id": deliverable_id,
        "escalation_pa_post_id": pa_post_id,
        "escalation_deduped": deduped,
        "escalation_prior_ops_run_id": prior_ops_run_id,
        "dedupe_action": (
            f"appended_to_{deliverable_id}" if deduped else "new_escalation"
        ),
    }


# ── Celery task entry ─────────────────────────────────────────────────


@shared_task(
    bind=True,
    name="rigby_documentation_manager_daily",
    soft_time_limit=2700,    # 45min soft — give cascade headroom over 30min cap
    time_limit=3000,         # 50min hard — Celery-level kill above the soft
    acks_late=False,         # match process_pa_chat_task for consistency
    ignore_result=False,
)
def rigby_documentation_manager_daily(self) -> dict:
    """Run Rigby's Documentation Manager daily routine end-to-end.

    Idempotent within the same calendar day. Returns:
        {ok, mission_id, status, verdict, wall_time_ms, summary,
         already_ran (bool)}
    """
    existing = _existing_mission_for_today()
    if existing is not None:
        if existing.status != "running":
            logger.info(
                "[DOCS_MANAGER_TASK] mission %s already exists for today "
                "(status=%s); returning cached result.",
                existing.id, existing.status,
            )
            return {
                "ok": True,
                "mission_id": str(existing.id),
                "status": existing.status,
                "already_ran": True,
                "summary": existing.summary or {},
            }
        # If a previous invocation is still running we don't start another;
        # this would otherwise double-run the cascade.
        logger.warning(
            "[DOCS_MANAGER_TASK] mission %s is still running; not starting "
            "a duplicate cascade.",
            existing.id,
        )
        return {
            "ok": True,
            "mission_id": str(existing.id),
            "status": "running",
            "already_ran": True,
            "summary": existing.summary or {},
        }

    mission = OpsRun.objects.create(
        title=f"docs_cascade: {timezone.localtime().strftime('%Y-%m-%d')}",
        run_type="manual",
        domain="mission",
        run_kind=MISSION_RUN_KIND,
        mission_id=uuid.uuid4(),
        triggered_by="beat",
        status="running",
        summary={"started_at_iso": timezone.now().isoformat()},
    )
    logger.info(
        "[DOCS_MANAGER_TASK] starting mission %s", mission.id
    )
    return _run_mission(mission)
