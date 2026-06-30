"""Documentation Manager docs cascade — job-specific implementation
(Session 1256 PR 1.2).

This module is the docs-cascade-specific "what" that plugs into the
generic MissionRunner "how" (lifecycle, escalation, verdict, etc.).
It owns:

  * the four cascade steps (build_docs_index, build_rag_corpus,
    sync_docs_index_to_documents, sync_docs_index_to_documents --embed)
  * step-4 timeout warning timer
  * pre-/post-flight count probes (Document, DocumentEmbedding,
    docs/_index.json)
  * drift observation (verify_doc_claims --only-drift)
  * docs-specific escalation Deliverable body formatter
  * docs-specific PA escalation summary line
  * docs-specific PA chat post hook (writes a ChatConversation row)
  * ``build_docs_manager_runner()`` factory that wires all of the above
    into a ``MissionRunner`` with the docs-cascade ``MissionRunnerConfig``

The mission lifecycle (OpsRun creation, OpsRunEvent timeline,
idempotency, error-signature classification, escalation create-or-
append, completed→ready audit transition, verdict emission, shift-
report dispatch) is delegated entirely to MissionRunner.

──────────────────────────────────────────────────────────────────────
Postflight context (PR 1.3+)
──────────────────────────────────────────────────────────────────────

MissionRunner's ``postflight_fn`` accepts a ``PostflightContext``
(``mission``, ``passed``, ``summary_acc``). The docs cascade's
postflight reads ``ctx.mission`` directly to emit two timeline events
the runner can't emit on its own:

  * On success: write the ``step_5_drift_observed`` info event onto
    the mission timeline.
  * On failure: write the ``step_5_skipped`` info event onto the
    mission timeline.

PR 1.2 used a closure-capture workaround (a ``mission_holder`` dict
populated by step wrappers, read by the postflight) because
MissionRunner's pre-1.3 postflight_fn signature was
``(passed, summary_acc)`` and did not carry the mission. PR 1.3 added
``PostflightContext`` to MissionRunner; this module then dropped the
closure-capture wrappers entirely. See PR #2739 (closure-capture
introduction) and PR #2740 (PostflightContext replacement) for
history.
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
import threading
import time
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Sequence

from django.conf import settings
from django.core.management import call_command
from django.utils import timezone

from core.employees import DOCUMENTATION_MANAGER, RIGBY
from core.employees.jobs import EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME
from core.employees.mission_runner import (
    EscalationDeliverableSpec,
    FailureContext,
    MissionRunner,
    MissionRunnerConfig,
    PAPostContext,
    PostflightContext,
    Step,
    StepResult,
)

logger = logging.getLogger(__name__)


# ── Constants ─────────────────────────────────────────────────────────

MISSION_RUN_KIND = DOCUMENTATION_MANAGER.mission_run_kind  # "docs_cascade"

# Step-4 timeout values from the JobContract.
_STEP_4_WARNING_SECONDS = DOCUMENTATION_MANAGER.embed_step_timeout.get(
    "warning_seconds", 600
)
_STEP_4_HARD_SECONDS = DOCUMENTATION_MANAGER.embed_step_timeout.get(
    "hard_seconds", 1800
)

# Escalation labels (per-employee — keep here).
# Confidence + dedupe window defaults live on ``MissionRunnerConfig``
# (mission_runner.py:255-258 + :497-502); the docs cascade takes the
# defaults so they are NOT redeclared here. The workspace name lives in
# ``core.employees.jobs.EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME`` and is
# imported above.
DELIVERABLE_TITLE_PREFIX = "Docs Manager Escalation"
ESCALATION_SOURCE = "DocsManager"
PIN_SETTINGS_KEY = "RIGBY_PRIMARY_PA_PIN"

# Single-event labels emitted from postflight (not standard runner-
# managed step events).
DRIFT_LABEL = "step_5_drift_observed"
STEP_5_SKIPPED_LABEL = "step_5_skipped"

# Step 4 warning label.
STEP_4_WARNING_LABEL = "step_4_warning"

# docs/_index.json — read by ``_probe_docs_indexed_count``.
DOCS_INDEX_JSON_PATH = Path(settings.BASE_DIR) / "docs" / "_index.json"


# ── Generic event emission helper (mirrors runner's internal pattern)
#
# The docs cascade emits two events from postflight that the runner
# itself cannot emit (drift observation success info row + step 5
# skipped on failure). This helper is the docs-cascade-side equivalent
# of MissionRunner._emit_event so both code paths share idempotency
# semantics.


def _emit_event(
    mission, label: str, event_type: str, **detail: Any
):
    """Idempotent ``(run, label)`` OpsRunEvent creation.

    Mirrors MissionRunner._emit_event's contract — re-emitting the
    same label against the same mission writes zero new rows.
    """
    from core.models_ops_runs import OpsRunEvent

    event, _created = OpsRunEvent.objects.get_or_create(
        run=mission,
        label=label,
        defaults={"event_type": event_type, "detail": detail},
    )
    return event


# ── Count probes ──────────────────────────────────────────────────────


def _safe_count(
    label: str, fn: Callable[[], int]
) -> tuple[Optional[int], Optional[str]]:
    """Run a count probe; return (value, error_str) — never raises.

    A failed probe sets degraded_evidence=True but does NOT escalate.
    Returning (None, "<error>") lets the caller decide how to surface
    the gap.
    """
    try:
        return int(fn()), None
    except Exception as exc:  # pragma: no cover — defensive
        logger.warning(
            "[DOCS_MANAGER_PROBE] label=%s error=%s: %s",
            label, type(exc).__name__, exc,
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
    """Derive from docs/_index.json — count the ``documents`` list."""
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
            type(exc).__name__, exc,
        )
        return None


def _safe_delta(before: Optional[int], after: Optional[int]) -> Optional[int]:
    if before is None or after is None:
        return None
    return after - before


# ── Step 4 timeout warning timer ──────────────────────────────────────


def _start_warning_timer(
    mission, warning_seconds: int = _STEP_4_WARNING_SECONDS
) -> threading.Timer:
    """Schedule a one-shot ``step_4_warning`` emission.

    Caller MUST ``.cancel()`` the returned Timer once step 4 completes
    so the warning doesn't fire on already-finished runs.
    """

    def _fire():
        try:
            logger.warning(
                "[DOCS_MANAGER_STEP_4_SLOW] elapsed_seconds=%d mission_id=%s",
                warning_seconds, mission.id,
            )
            _emit_event(
                mission,
                STEP_4_WARNING_LABEL,
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


# ── Cascade step implementations ──────────────────────────────────────


def _run_call_command_step(
    mission, label_prefix: str, cmd: str, extra_args: Sequence[str]
) -> StepResult:
    """Run a step via Django's call_command. Returns StepResult.

    Captures combined stdout+stderr into a StringIO so error_tail can
    be derived on failure. The runner emits ``<label_prefix>_started``
    and ``<label_prefix>_passed`` / ``_failed`` itself; this function
    doesn't emit those.
    """
    start = time.monotonic()
    captured = StringIO()
    try:
        call_command(cmd, *extra_args, stdout=captured, stderr=captured)
        duration_ms = int((time.monotonic() - start) * 1000)
        return StepResult(
            passed=True,
            output=captured.getvalue(),
            duration_ms=duration_ms,
            extra={"cmd": cmd, "exit_code": 0},
        )
    except SystemExit as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        output = captured.getvalue()
        return StepResult(
            passed=False,
            output=output,
            duration_ms=duration_ms,
            extra={
                "cmd": cmd,
                "exit_code": int(getattr(exc, "code", 1) or 1),
            },
        )
    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        output = captured.getvalue() + f"\n{type(exc).__name__}: {exc}"
        return StepResult(
            passed=False,
            output=output,
            duration_ms=duration_ms,
            extra={"cmd": cmd, "exit_code": 1},
        )


def _run_subprocess_step(
    mission,
    label_prefix: str,
    cmd: str,
    extra_args: Sequence[str],
    hard_timeout: int = _STEP_4_HARD_SECONDS,
) -> StepResult:
    """Run a step via subprocess so the hard timeout actually fires.

    Wires up the step-4 warning timer around the subprocess call.
    Returns StepResult.
    """
    warning_timer = _start_warning_timer(mission)
    start = time.monotonic()
    argv = ["python", "manage.py", cmd, *list(extra_args)]
    try:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=hard_timeout,
            check=False,
        )
        warning_timer.cancel()
        duration_ms = int((time.monotonic() - start) * 1000)
        output = (completed.stdout or "") + (completed.stderr or "")
        passed = completed.returncode == 0
        return StepResult(
            passed=passed,
            output=output,
            duration_ms=duration_ms,
            extra={
                "cmd": cmd,
                "exit_code": completed.returncode,
                "was_timeout": False,
            },
        )
    except subprocess.TimeoutExpired as exc:
        warning_timer.cancel()
        duration_ms = int((time.monotonic() - start) * 1000)
        output = (exc.stdout or b"").decode("utf-8", errors="replace") + (
            exc.stderr or b""
        ).decode("utf-8", errors="replace")
        return StepResult(
            passed=False,
            output=output,
            duration_ms=duration_ms,
            extra={
                "cmd": cmd,
                "exit_code": "timeout",
                "was_timeout": True,
                "timeout_seconds": hard_timeout,
            },
        )


def step_1_build_docs_index(mission) -> StepResult:
    return _run_call_command_step(
        mission, "step_1_index", "build_docs_index", []
    )


def step_2_build_rag_corpus(mission) -> StepResult:
    return _run_call_command_step(
        mission, "step_2_corpus", "build_rag_corpus", []
    )


def step_3_sync_docs_index_to_documents(mission) -> StepResult:
    return _run_call_command_step(
        mission, "step_3_sync", "sync_docs_index_to_documents", []
    )


def step_4_embed(mission) -> StepResult:
    return _run_subprocess_step(
        mission,
        "step_4_embed",
        "sync_docs_index_to_documents",
        ["--embed"],
        hard_timeout=_STEP_4_HARD_SECONDS,
    )


# ── Drift observation (Step 5 — observation-only on success) ──────────


def _run_drift_observation(
    mission,
) -> tuple[Optional[int], Optional[int], bool]:
    """Run `verify_doc_claims --only-drift --format json`.

    Returns (drift_count, drift_items_count, degraded_evidence_for_drift).
    Emits a single ``step_5_drift_observed`` info event onto the
    mission timeline. Never raises — degrades gracefully to
    (None, None, True) if the command output isn't parseable.
    """
    captured = StringIO()
    try:
        call_command(
            "verify_doc_claims",
            "--only-drift",
            "--format", "json",
            stdout=captured, stderr=captured,
        )
    except Exception as exc:
        logger.warning(
            "[DOCS_MANAGER_DRIFT] command failed: %s: %s",
            type(exc).__name__, exc,
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
        match = re.search(r"drift[^0-9]*(\d+)", raw, re.IGNORECASE)
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

    drift_count = None
    drift_items_count = None
    if isinstance(payload, dict):
        drift_count = payload.get("drift") or payload.get("drift_count")
        items = payload.get("items") or payload.get("drift_items")
        if isinstance(items, list):
            drift_items_count = len(items)
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


# ── Escalation body + PA summary formatters ───────────────────────────


def build_escalation_body(ctx: FailureContext) -> str:
    """Docs-specific escalation Deliverable body (matches PR 2 format)."""
    today_local = timezone.localtime()
    today_str = today_local.strftime("%Y-%m-%d")
    when_iso = today_local.isoformat()
    duration_seconds = max(
        0, int((ctx.finished_at - ctx.started_at).total_seconds())
    )
    minutes, seconds = divmod(duration_seconds, 60)
    run_duration_label = f"{minutes}m {seconds}s"

    lines = [
        f"# Docs Manager Escalation — {today_str}",
        "",
        f"**failed_step:** `{ctx.failed_step}`",
        f"**when:** {when_iso}  ",
        f"**run_duration_so_far:** {run_duration_label}",
        f"**error_signature:** `{ctx.error_signature}`",
        f"**ops_run_id:** `{ctx.mission_id}`",
        "",
        "## what_i_did",
        (
            f"Ran cascade step `{ctx.failed_step}`; "
            "process exited non-zero / timed out."
        ),
        "",
        "## counts_so_far",
        "```json",
        json.dumps(
            ctx.counts_so_far, indent=2, sort_keys=True, default=str
        ),
        "```",
        "",
        "## error_tail (last 100 lines)",
        "```",
        ctx.error_tail or "(empty)",
        "```",
        "",
        "---",
        "**Chris: approve next action (retry / investigate / "
        "assign Claude Code fix).**",
    ]
    return "\n".join(lines)


def build_pa_summary_line(ctx: FailureContext) -> str:
    """Docs-specific one-line PA chat escalation summary."""
    # Note: deliverable id is not in FailureContext; the PA post hook
    # has the deliverable id and rebuilds the line via PAPostContext.
    # This formatter is only invoked for the Deliverable body's
    # closing line context; PA chat uses post_pa_escalation directly.
    return (
        f"Docs Manager FAILED at {ctx.failed_step} — "
        f"(OpsRun {ctx.mission_id})."
    )


# ── PA chat escalation post hook ──────────────────────────────────────


def post_pa_escalation(post_ctx: PAPostContext) -> Optional[str]:
    """Write the one-line escalation summary into Rigby's pinned PA chat.

    Mirrors the PR 2 behavior:
      * conversation_id from MissionRunner's pin resolution
      * user_id resolves to RIGBY's runs_as_username
      * user_message: ``"[system: docs_manager escalation]"``
      * assistant_response: the formatted summary line
      * metadata: source / ops_run_id / deliverable_id

    Returns the ChatConversation row id (str) or None on failure.
    """
    from core.models import ChatConversation

    pin = post_ctx.primary_chat_id
    if not pin:
        logger.warning(
            "[DOCS_MANAGER_PA_POST] no active pin resolved; skipping post"
        )
        return None

    summary = (
        f"Docs Manager FAILED at {post_ctx.failed_step} — escalation "
        f"deliverable {post_ctx.deliverable_id} "
        f"(OpsRun {post_ctx.mission_id})."
    )
    try:
        row = ChatConversation.objects.create(
            conversation_id=pin,
            user_id=post_ctx.runs_as_user_id,
            user_message="[system: docs_manager escalation]",
            assistant_response=summary,
            metadata={
                "source": "docs_manager_daily",
                "ops_run_id": str(post_ctx.mission_id),
                "deliverable_id": post_ctx.deliverable_id,
            },
        )
        return str(getattr(row, "id", "") or "") or None
    except Exception as exc:
        logger.warning(
            "[DOCS_MANAGER_PA_POST] write failed: %s: %s",
            type(exc).__name__, exc,
        )
        return None


# ── Preflight + postflight hook builders (PR 1.3+) ────────────────────


def _make_preflight() -> Callable[[Dict[str, Any]], None]:
    """Return a preflight closure that probes before-counts."""

    def _preflight(summary_acc: Dict[str, Any]) -> None:
        # Initialize docs-specific summary slots so they exist even on
        # early failures (preserves the existing summary shape).
        summary_acc.setdefault("docs_indexed_count", None)
        summary_acc.setdefault("documents_count_before", None)
        summary_acc.setdefault("documents_count_after", None)
        summary_acc.setdefault("embeddings_count_before", None)
        summary_acc.setdefault("embeddings_count_after", None)
        summary_acc.setdefault("embedding_delta", None)
        summary_acc.setdefault("drift_count", None)
        summary_acc.setdefault("drift_items_count", None)

        summary_acc["documents_count_before"] = _probe_documents_count()
        summary_acc["embeddings_count_before"] = _probe_embeddings_count()
        if (
            summary_acc["documents_count_before"] is None
            or summary_acc["embeddings_count_before"] is None
        ):
            summary_acc["degraded_evidence"] = True

    return _preflight


def _postflight(ctx: "PostflightContext") -> None:
    """Postflight hook with mission-row access via PostflightContext.

    Reads ``ctx.mission`` directly (no closure-capture). On success
    probes after-counts + runs drift observation (emits
    ``step_5_drift_observed`` info event). On failure probes
    after-counts (state may be partially mutated) + emits
    ``step_5_skipped`` info event.

    **Defensive guard.** ``ctx.mission`` is contractually guaranteed
    non-None by MissionRunner (the runner constructs the context
    inside ``_run_mission`` after the OpsRun row is created). The
    guard here raises if that contract is ever broken, surfacing the
    regression at its source rather than silently dropping the
    step_5 timeline events.
    """
    if ctx.mission is None:
        raise RuntimeError(
            "docs_cascade postflight invoked with ctx.mission=None — "
            "MissionRunner contract violation. Cannot emit "
            "step_5_drift_observed / step_5_skipped without a mission "
            "row. Investigate the MissionRunner _run_mission flow."
        )

    mission = ctx.mission
    summary_acc = ctx.summary_acc

    if ctx.passed:
        summary_acc["docs_indexed_count"] = _probe_docs_indexed_count()
        summary_acc["documents_count_after"] = _probe_documents_count()
        summary_acc["embeddings_count_after"] = _probe_embeddings_count()
        summary_acc["embedding_delta"] = _safe_delta(
            summary_acc.get("embeddings_count_before"),
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

        drift_count, drift_items, drift_degraded = _run_drift_observation(
            mission
        )
        summary_acc["drift_count"] = drift_count
        summary_acc["drift_items_count"] = drift_items
        if drift_degraded:
            summary_acc["degraded_evidence"] = True
        return

    # Failure path
    summary_acc["documents_count_after"] = _probe_documents_count()
    summary_acc["embeddings_count_after"] = _probe_embeddings_count()
    summary_acc["embedding_delta"] = _safe_delta(
        summary_acc.get("embeddings_count_before"),
        summary_acc["embeddings_count_after"],
    )
    # Step 5 is the drift-observation slot. On cascade failure it never
    # runs — emit the skipped event so the timeline matches the pre-1.2
    # behavior (single ``step_5_skipped`` event, not the runner's
    # ``<name>_skipped`` for runner-managed steps).
    _emit_event(
        mission,
        STEP_5_SKIPPED_LABEL,
        "info",
        reason="prior_failure",
        cmd="verify_doc_claims --only-drift",
    )


def _docs_escalation_spec_factory(
    ctx: FailureContext,
) -> EscalationDeliverableSpec:
    """Docs-cascade-specific escalation spec.

    Targets the "Donkey Betz" workspace explicitly so escalation
    Deliverables don't fall back to the legacy config-level lookup.
    Other fields match the runner's baseline (publish_candidate,
    completed→ready with audit row).
    """
    return EscalationDeliverableSpec(
        workspace_name=EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME,
    )


# ── Public factory ────────────────────────────────────────────────────


def build_docs_manager_runner() -> MissionRunner:
    """Wire all docs-cascade-specific config + hooks into a MissionRunner.

    Called by the Celery task; also usable from tests + management
    commands. PR 1.3+: no per-call mutable state — the postflight reads
    ``ctx.mission`` directly from the PostflightContext MissionRunner
    constructs at run-time, so the factory is pure.

    Confidence + dedupe values are NOT passed — MissionRunnerConfig's
    field defaults (0.95 / 0.6 / 0.0 / 24h) apply. The escalation
    workspace travels via ``EscalationDeliverableSpec.workspace_name``
    on the spec factory above (spec precedence wins over
    ``config.workspace_name`` per ``_resolve_workspace_for_spec``).
    """
    config = MissionRunnerConfig(
        # Identity
        employee_handle=RIGBY.handle,
        employee_display_name=RIGBY.display_name,
        runs_as_username=RIGBY.runs_as_username,
        primary_chat_id=RIGBY.primary_chat_id,
        # Job
        mission_run_kind=MISSION_RUN_KIND,
        job_title=DOCUMENTATION_MANAGER.title,
        # Escalation (employee-specific only — workspace travels via spec)
        escalation_source=ESCALATION_SOURCE,
        escalation_title_prefix=DELIVERABLE_TITLE_PREFIX,
        # Pin override
        pin_settings_key=PIN_SETTINGS_KEY,
    )

    steps = [
        Step(name="step_1_index", fn=step_1_build_docs_index),
        Step(name="step_2_corpus", fn=step_2_build_rag_corpus),
        Step(name="step_3_sync", fn=step_3_sync_docs_index_to_documents),
        Step(name="step_4_embed", fn=step_4_embed),
    ]

    return MissionRunner(
        config=config,
        steps=steps,
        escalation_body_formatter=build_escalation_body,
        escalation_summary_formatter=build_pa_summary_line,
        escalation_deliverable_spec_factory=_docs_escalation_spec_factory,
        shift_report_fn=_shift_report_fn,
        pa_post_fn=post_pa_escalation,
        preflight_fn=_make_preflight(),
        postflight_fn=_postflight,
    )


def _shift_report_fn(mission) -> Dict[str, Any]:
    """Thin wrapper around the existing docs-manager shift-report DM.

    Delegates to ``core.employees.comms_docs_manager.post_docs_manager_shift_report``
    so the runner's ``shift_report_fn`` hook returns the same dict
    envelope existing tests expect.
    """
    from core.employees.comms_docs_manager import (
        post_docs_manager_shift_report,
    )

    return post_docs_manager_shift_report(mission)
