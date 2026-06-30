"""Chief of Staff morning brief — job-specific implementation
(Session 1257 PR 3.2).

Wires the existing morning_brief workflow (WorkflowOrchestrationAgent)
into a MissionRunner-driven mission. The runner owns lifecycle —
OpsRun creation + daily idempotency, OpsRunEvent timeline,
error-signature classification, escalation Deliverable, verdict
emission. The workflow itself owns everything else — the 8-step
internal orchestration, Decision Card structured/markdown form,
strategic-synthesis morning_brief branch, persistent "Morning Brief"
workspace bootstrap, and the final brief Deliverable creation.

This module owns the job-specific bits:

  * one ``step_brief_workflow`` step that wraps
    ``WorkflowOrchestrationAgent.execute(workflow='morning_brief')``
  * scalar-only extraction of required summary keys from the
    workflow result envelope (NO envelope persistence — Rigby
    S1257 SIGN-WITH-EDITS lock #2)
  * postflight-only ``brief_chars`` derivation via single ORM read of
    the created Deliverable's content length (Rigby S1257 SIGN-WITH-
    EDITS lock #1 — no workflow internal touches)
  * CoS-flavored escalation Deliverable body + summary line formatters
  * ``build_chief_of_staff_runner()`` factory

──────────────────────────────────────────────────────────────────────
Wrap-as-single-step contract
──────────────────────────────────────────────────────────────────────

The morning_brief workflow's 8 internal steps run unchanged inside
ONE MissionRunner Step. From MissionRunner's perspective the entire
brief is one atomic unit: the wrapper step either passes (workflow
returned success=True) or fails (workflow returned success=False OR
raised an exception). This preserves every existing workflow
semantic without modification.

Failure granularity is preserved via ``StepResult.extra[
'inner_failed_step']`` which surfaces the workflow's own failed-step
name into the OpsRunEvent.detail JSON, the escalation Deliverable
body, and the mission summary. The error-signature hash still
varies by inner-step error tail content even though the outer step
name is constant — dedupe semantics are intact.

──────────────────────────────────────────────────────────────────────
No PA chat post + no shift report (v0 per spec)
──────────────────────────────────────────────────────────────────────

``CHIEF_OF_STAFF.primary_chat_id is None`` and
``MORNING_BRIEF_JOB.escalation_visibility`` explicitly says "No PA
chat post for v0". Both ``pa_post_fn`` and ``shift_report_fn`` are
None in the runner config. The brief Deliverable itself is the
daily-read visibility surface; the escalation Deliverable is the
failure surface. No DM thread today.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import date as _date
from typing import Any, Callable, Dict, List, Optional

from django.contrib.auth import get_user_model
from django.utils import timezone

from core.employees import CHIEF_OF_STAFF, MORNING_BRIEF_JOB
from core.employees.jobs import EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME
from core.employees.mission_runner import (
    EscalationDeliverableSpec,
    FailureContext,
    MissionRunner,
    MissionRunnerConfig,
    PostflightContext,
    Step,
    StepResult,
)

logger = logging.getLogger(__name__)


# ── Constants ─────────────────────────────────────────────────────────

MISSION_RUN_KIND = MORNING_BRIEF_JOB.mission_run_kind  # "morning_brief"

# Escalation labels (per-employee — keep here).
# Confidence + dedupe window defaults live on ``MissionRunnerConfig``
# (mission_runner.py:255-258 + :497-502); morning_brief takes the
# defaults so they are NOT redeclared here. The workspace name lives in
# ``core.employees.jobs.EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME`` and is
# imported above.
DELIVERABLE_TITLE_PREFIX = "Chief of Staff Escalation"
ESCALATION_SOURCE = "ChiefOfStaff"

# The single Step name. Failure granularity travels in
# StepResult.extra['inner_failed_step'] — see module docstring.
STEP_NAME = "step_brief_workflow"

# Workflow constants — pulled directly so the wrapper stays in sync
# with the workflow template's source-of-truth step names.
_WORKFLOW_NAME = "morning_brief"
_STEP_NAME_ROTATION = "rotation_slot_resolve"
_STEP_NAME_LANE_1 = "lane_1_platform_readiness"
_STEP_NAME_LANE_2 = "lane_2_build_focus"
_STEP_NAME_LANE_3 = "lane_3_competitive_landscape"
_STEP_NAME_LANE_4 = "lane_4_rotating_focus"
_STEP_NAME_DECISION = "decision_card_synthesis"
_STEP_NAME_SYNTHESIS = "strategic_synthesis"
_STEP_NAME_CREATE = "create_deliverable"

_LANE_STEP_NAMES = (
    _STEP_NAME_LANE_1,
    _STEP_NAME_LANE_2,
    _STEP_NAME_LANE_3,
    _STEP_NAME_LANE_4,
)


# ── User resolution ───────────────────────────────────────────────────


def _resolve_chris_user():
    """Return the UnifiedUser the brief runs as.

    Mirrors the legacy ``generate_morning_brief_daily`` task's user
    resolution — the brief is always written for ``chris`` (sole
    platform user; see CLAUDE.md § Session 1098 fix). Returns the
    user instance or None.
    """
    User = get_user_model()
    return User.objects.filter(
        username__iexact=CHIEF_OF_STAFF.runs_as_username
    ).first()


# ── Summary persistence helper ────────────────────────────────────────


def _persist_to_summary(mission, **fields: Any) -> None:
    """Atomically merge ``fields`` into ``mission.summary``.

    Each scalar field is written individually so the summary stays
    JSON-safe + queryable (no nested workflow envelope per Rigby S1257
    SIGN-WITH-EDITS lock #2). MissionRunner's own ``_persist_summary``
    later merges runner-level keys (wall_time_ms, verdict, failed_step,
    error_tail, …) without overwriting step-written keys — the two
    key sets don't collide.
    """
    existing = mission.summary or {}
    mission.summary = {**existing, **fields}
    mission.save(update_fields=["summary"])


# ── Scalar extraction from workflow result ────────────────────────────


def _step_result_by_name(steps: List[Dict], name: str) -> Optional[Dict]:
    """Find a workflow step's result dict by its step name."""
    for s in steps:
        if s.get("name") == name:
            return s
    return None


def _extract_scalars(workflow_result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract scalar-only summary fields from the workflow envelope.

    Per Rigby S1257 SIGN-WITH-EDITS lock #2: ONLY the scalar fields
    required by ``MORNING_BRIEF_JOB.required_summary_keys`` are pulled
    out. The full workflow envelope is NEVER persisted to
    ``mission.summary`` (would explode JSON size + breaks queryability).

    Returns a dict ready to merge into mission.summary with these keys:

      * rotation_slot (str | None)
      * lane_4_slot_used (str | None)
      * lanes_completed_count (int, 0-4)
      * decision_count (int)
      * decision_card_chars (int)
      * deliverable_id (str UUID | None)
      * workspace_id (str UUID | None)
      * inner_failed_step (str | None)
      * inner_failed_step_error (str | None)

    ``brief_chars`` is NOT computed here — it's derived in
    ``_compute_brief_chars`` via a single ORM read of the created
    Deliverable's content length (Rigby S1257 SIGN-WITH-EDITS lock #1).
    """
    steps = workflow_result.get("steps", []) or []

    # rotation_slot
    rotation_step = _step_result_by_name(steps, _STEP_NAME_ROTATION)
    rotation_slot = (
        (rotation_step.get("result") or {}).get("rotation_slot")
        if rotation_step else None
    )

    # lane_4_slot_used
    lane_4_step = _step_result_by_name(steps, _STEP_NAME_LANE_4)
    lane_4_slot_used = (
        (lane_4_step.get("result") or {}).get("slot_used")
        if lane_4_step else None
    )

    # lanes_completed_count — count of lane steps that returned
    # success=True (the workflow's per-step ``success`` field, set by
    # ``_compile_final_result``).
    lanes_completed_count = 0
    for lane_name in _LANE_STEP_NAMES:
        lane_step = _step_result_by_name(steps, lane_name)
        if lane_step and lane_step.get("success") is True:
            lanes_completed_count += 1

    # decision_count + decision_card_chars
    decision_step = _step_result_by_name(steps, _STEP_NAME_DECISION)
    decision_result = (decision_step.get("result") or {}) if decision_step else {}
    decision_cards = decision_result.get("decision_cards") or []
    decision_card_text = decision_result.get("decision_card_text") or ""
    decision_count = (
        len(decision_cards) if isinstance(decision_cards, list) else 0
    )
    decision_card_chars = (
        len(decision_card_text) if isinstance(decision_card_text, str) else 0
    )

    # deliverable_id + workspace_id
    create_step = _step_result_by_name(steps, _STEP_NAME_CREATE)
    create_result = (create_step.get("result") or {}) if create_step else {}
    deliverable_id = create_result.get("deliverable_id")
    workspace_id = create_result.get("workspace_id")

    # inner_failed_step + inner_failed_step_error — find the first
    # step in iteration order with success=False (the workflow aborts
    # on first critical failure, so first match is the right one).
    inner_failed_step = None
    inner_failed_step_error = None
    for s in steps:
        if s.get("success") is False:
            inner_failed_step = s.get("name")
            inner_result = s.get("result") or {}
            inner_failed_step_error = inner_result.get("error")
            break

    return {
        "rotation_slot": rotation_slot,
        "lane_4_slot_used": lane_4_slot_used,
        "lanes_completed_count": lanes_completed_count,
        "decision_count": decision_count,
        "decision_card_chars": decision_card_chars,
        "deliverable_id": deliverable_id,
        "workspace_id": workspace_id,
        "inner_failed_step": inner_failed_step,
        "inner_failed_step_error": inner_failed_step_error,
    }


def _compute_brief_chars(deliverable_id: Optional[str]) -> int:
    """Derive ``brief_chars`` via single ORM read of Deliverable.content.

    Per Rigby S1257 SIGN-WITH-EDITS lock #1: ``brief_chars`` is
    derived postflight via a single bounded ORM read, NOT by adding a
    field to the workflow return envelope. The workflow contract stays
    untouched.

    Returns 0 when ``deliverable_id`` is None (workflow ran but didn't
    persist a brief — smoke-probe path) or when the lookup fails.
    """
    if not deliverable_id:
        return 0
    try:
        from core.models_deliverables import Deliverable

        content = (
            Deliverable.objects.filter(id=deliverable_id)
            .values_list("content", flat=True)
            .first()
        )
        return len(content or "")
    except Exception as exc:  # pragma: no cover — defensive
        logger.warning(
            "[CHIEF_OF_STAFF_BRIEF_CHARS] deliverable lookup failed "
            "for id=%r: %s: %s",
            deliverable_id, type(exc).__name__, exc,
        )
        return 0


def _build_step_output(workflow_result: Dict[str, Any]) -> str:
    """Build the wrapper step's ``output`` string from the workflow.

    On success: short summary of step counts. On failure: short summary
    + the inner failed step's error. The full lane texts + brief markdown
    are NOT echoed here — they live in the brief Deliverable (success
    path) or the workflow's per-step result dicts (which MissionRunner
    captures into the wrapper step's accumulated error_tail on failure).
    """
    steps = workflow_result.get("steps", []) or []
    success = bool(workflow_result.get("success"))
    completed = sum(1 for s in steps if s.get("success") is True)
    total = len(steps)
    if success:
        return (
            f"Morning brief workflow completed: "
            f"{completed}/{total} steps passed."
        )

    failed = next(
        (s for s in steps if s.get("success") is False),
        None,
    )
    failed_name = (failed or {}).get("name") or "<unknown>"
    failed_error = (
        ((failed or {}).get("result") or {}).get("error")
        or workflow_result.get("error")
        or "no error string captured"
    )
    return (
        f"Morning brief workflow FAILED at inner step "
        f"{failed_name!r}: {failed_error}"
    )


# ── The one wrapper step ──────────────────────────────────────────────


def step_brief_workflow(mission) -> StepResult:
    """Run the morning_brief workflow and capture scalar evidence.

    This is the ONE MissionRunner Step for the Chief of Staff job.
    From MissionRunner's perspective: it's an atomic unit that either
    passed or failed. From the workflow's perspective: the entire
    existing 8-step orchestration runs unchanged.

    Mission lifecycle ownership:
      * MissionRunner emits ``step_brief_workflow_started`` /
        ``_passed`` / ``_failed`` and the surrounding ``run_started`` +
        ``verdict_issued`` events.
      * This step persists the scalar evidence directly into
        ``mission.summary`` via ``_persist_to_summary`` so the runner's
        downstream reads (status tool, evidence join, dedupe) find
        scalar JSON-safe fields. NO full workflow envelope is persisted.

    Behavior on no-user (chris missing): returns ``passed=False`` with
    a clear error tail; the runner then escalates per its standard
    failure path. Matches the legacy task's user-resolution failure
    semantics.
    """
    from core.services.workflow_orchestration_agent import (
        WorkflowOrchestrationAgent,
    )

    start = time.monotonic()
    user = _resolve_chris_user()
    if user is None:
        duration_ms = int((time.monotonic() - start) * 1000)
        msg = (
            f"step_brief_workflow: no target user found "
            f"(username={CHIEF_OF_STAFF.runs_as_username!r} lookup "
            "returned None). Cannot dispatch workflow."
        )
        logger.error("[CHIEF_OF_STAFF_BRIEF_FAILED] %s", msg)
        return StepResult(
            passed=False,
            output=msg,
            duration_ms=duration_ms,
            extra={"user_resolution_failed": True},
        )

    today = _date.today().isoformat()
    agent = WorkflowOrchestrationAgent(user=user)
    try:
        result = agent.execute(
            workflow=_WORKFLOW_NAME,
            topic=f"Morning Brief — {today}",
        )
    except Exception as exc:
        # MissionRunner catches step exceptions itself and converts
        # them to StepResult; re-raise to let it record the traceback
        # cleanly via the runner's uniform error-handling path.
        logger.error(
            "[CHIEF_OF_STAFF_BRIEF_RAISED] type=%s: %s",
            type(exc).__name__, exc, exc_info=True,
        )
        raise

    # Extract scalars from the workflow envelope — never persist the
    # envelope itself (Rigby S1257 SIGN-WITH-EDITS lock #2).
    scalars = _extract_scalars(result)

    # brief_chars: postflight ORM read of the created Deliverable's
    # content length (Rigby S1257 SIGN-WITH-EDITS lock #1). Workflow
    # internal contract stays untouched.
    brief_chars = _compute_brief_chars(scalars.get("deliverable_id"))

    # Persist all scalar fields directly to mission.summary. These are
    # the keys MORNING_BRIEF_JOB.required_summary_keys names, minus
    # runner-managed keys (wall_time_ms, failed_step, error_tail,
    # degraded_evidence) which MissionRunner writes itself.
    _persist_to_summary(
        mission,
        rotation_slot=scalars["rotation_slot"],
        lane_4_slot_used=scalars["lane_4_slot_used"],
        lanes_completed_count=scalars["lanes_completed_count"],
        decision_count=scalars["decision_count"],
        decision_card_chars=scalars["decision_card_chars"],
        deliverable_id=scalars["deliverable_id"],
        workspace_id=scalars["workspace_id"],
        brief_chars=brief_chars,
        inner_failed_step=scalars["inner_failed_step"],
    )

    duration_ms = int((time.monotonic() - start) * 1000)
    success = bool(result.get("success"))
    output = _build_step_output(result)

    # extra is scalar-only — NEVER includes the workflow envelope.
    # Each key is JSON-safe so it travels cleanly through the
    # OpsRunEvent.detail JSONField via MissionRunner's _run_step.
    extra: Dict[str, Any] = {
        "inner_lanes_completed_count": scalars["lanes_completed_count"],
        "inner_decision_count": scalars["decision_count"],
        "inner_brief_chars": brief_chars,
    }
    if scalars.get("inner_failed_step"):
        extra["inner_failed_step"] = scalars["inner_failed_step"]
        # Keep the inner error string short for OpsRunEvent.detail.
        err = scalars.get("inner_failed_step_error") or ""
        extra["inner_failed_step_error_excerpt"] = (
            err[:240] + "..." if len(err) > 240 else err
        )

    return StepResult(
        passed=success,
        output=output,
        duration_ms=duration_ms,
        extra=extra,
    )


# ── Escalation body + summary formatters ──────────────────────────────


def build_escalation_body(ctx: FailureContext) -> str:
    """Chief-of-Staff-flavored escalation Deliverable body.

    Mirrors the docs cascade + platform audit body shapes with
    CoS-specific framing. The outer step name is always
    ``step_brief_workflow`` (the wrap-as-single-step pattern), so the
    body explicitly surfaces the workflow's inner failed step name
    from counts_so_far where available — that's where the actionable
    diagnostic lives.
    """
    today_local = timezone.localtime()
    today_str = today_local.strftime("%Y-%m-%d")
    when_iso = today_local.isoformat()
    duration_seconds = max(
        0, int((ctx.finished_at - ctx.started_at).total_seconds())
    )
    minutes, seconds = divmod(duration_seconds, 60)
    run_duration_label = f"{minutes}m {seconds}s"

    inner_failed_step = (
        ctx.counts_so_far.get("inner_failed_step") if ctx.counts_so_far
        else None
    )
    inner_failed_label = inner_failed_step or "<unknown inner step>"

    lines = [
        f"# Chief of Staff Escalation — {today_str}",
        "",
        f"**failed_step:** `{ctx.failed_step}`",
        f"**inner_failed_step:** `{inner_failed_label}`",
        f"**when:** {when_iso}  ",
        f"**run_duration_so_far:** {run_duration_label}",
        f"**error_signature:** `{ctx.error_signature}`",
        f"**ops_run_id:** `{ctx.mission_id}`",
        "",
        "## what_happened",
        (
            "The Morning Brief workflow did not ship today. The Chief "
            f"of Staff wrap step `{ctx.failed_step}` reported failure "
            f"because the underlying workflow's inner step "
            f"`{inner_failed_label}` raised or returned a failure shape "
            "before the brief Deliverable could be persisted."
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
    """One-line escalation summary string.

    Used only if a ``pa_post_fn`` hook is wired. PR 3.2 leaves
    ``pa_post_fn=None`` because ``CHIEF_OF_STAFF.primary_chat_id`` is
    None (the brief itself is the daily-read surface).
    """
    inner = (
        ctx.counts_so_far.get("inner_failed_step") if ctx.counts_so_far
        else None
    ) or "<unknown>"
    return (
        f"Chief of Staff Morning Brief FAILED at inner step {inner} "
        f"(signature {ctx.error_signature}, mission {ctx.mission_id})."
    )


# ── Escalation deliverable spec factory ───────────────────────────────


def _chief_of_staff_escalation_spec_factory(
    ctx: FailureContext,
) -> EscalationDeliverableSpec:
    """Targets the Donkey Betz workspace for escalation Deliverables.

    Other fields default to the baseline EscalationDeliverableSpec
    (type='report', category='ops', publish_intent='publish_candidate',
    completed→ready with audit row).
    """
    return EscalationDeliverableSpec(
        workspace_name=EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME,
    )


# ── Public factory ────────────────────────────────────────────────────


def build_chief_of_staff_runner() -> MissionRunner:
    """Wire the Chief of Staff Morning Brief into a MissionRunner.

    Called by the Celery task in ``core.tasks_chief_of_staff``. Pure:
    no per-call mutable state, no closure-capture (PR 1.3
    PostflightContext pattern made this unnecessary). Same shape as
    docs_cascade + platform_audit factories.
    """
    # Confidence + dedupe values are NOT passed — MissionRunnerConfig's
    # field defaults (0.95 / 0.6 / 0.0 / 24h) apply. The escalation
    # workspace travels via ``EscalationDeliverableSpec.workspace_name``
    # on the spec factory above.
    config = MissionRunnerConfig(
        # Identity
        employee_handle=CHIEF_OF_STAFF.handle,
        employee_display_name=CHIEF_OF_STAFF.display_name,
        runs_as_username=CHIEF_OF_STAFF.runs_as_username,
        primary_chat_id=CHIEF_OF_STAFF.primary_chat_id,  # None in v0
        # Job
        mission_run_kind=MISSION_RUN_KIND,
        job_title=MORNING_BRIEF_JOB.title,
        # Escalation (employee-specific only — workspace travels via spec)
        escalation_source=ESCALATION_SOURCE,
        escalation_title_prefix=DELIVERABLE_TITLE_PREFIX,
        # No pin_settings_key — CoS has no pinned PA chat in v0.
        pin_settings_key=None,
    )

    steps = [
        Step(name=STEP_NAME, fn=step_brief_workflow),
    ]

    return MissionRunner(
        config=config,
        steps=steps,
        escalation_body_formatter=build_escalation_body,
        escalation_summary_formatter=build_pa_summary_line,
        escalation_deliverable_spec_factory=(
            _chief_of_staff_escalation_spec_factory
        ),
        # v0 per spec § Boundary statements: no shift-report DM.
        # The brief itself is the daily-read visibility surface.
        shift_report_fn=None,
        # v0: no PA chat post (CHIEF_OF_STAFF has no primary_chat_id).
        pa_post_fn=None,
        # No preflight / postflight: the wrapper step writes all scalar
        # summary fields directly via _persist_to_summary; brief_chars
        # is derived inside the step after the workflow returns. There's
        # no before/after probe or drift observation to layer.
        preflight_fn=None,
        postflight_fn=None,
    )
