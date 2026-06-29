"""
MissionRunner — reusable employee mission lifecycle engine (Session 1256 PR 1.1).

Generic class that owns the *lifecycle* of one mission execution:
mission row creation, OpsRunEvent timeline emission, step orchestration,
error-signature classification, escalation Deliverable create-or-append,
status-transition audit, terminal verdict emission, optional shift-report
dispatch, optional PA-chat escalation post.

MissionRunner does NOT own: LLM execution, step semantics, business logic,
agent dispatch, scheduling, authority enforcement, BodyCoordinator
integration, or any employee-specific config. Those belong to:

  * the **step functions** the caller passes in (one per step in the
    job's daily routine);
  * the caller's **JobContract / AIEmployee** (read off the contract,
    projected into a ``MissionRunnerConfig`` at the call site);
  * the caller's **shift_report_fn** + **pa_post_fn** hooks (None →
    no-op);
  * separate framework primitives (``emit_mission_verdict``,
    ``post_shift_report``) the caller wires into the hooks if desired.

This module intentionally imports **nothing** from:

  * ``core.tasks_documentation_manager`` (job-specific Celery task)
  * ``core.employees.comms_docs_manager`` (job-specific comms wrapper)
  * any specific ``AIEmployee`` / ``JobContract`` constants
    (``RIGBY``, ``DOCUMENTATION_MANAGER``, etc.)

The architectural design that motivated this extraction lives in the
Session 1255 MissionRunner Architectural Design Report (in conversation;
companion ``docs/EMPLOYEE_OS_PRIMITIVES.md`` covers the broader Employee
OS primitives the runner composes).

═══════════════════════════════════════════════════════════════════════
PUBLIC API
═══════════════════════════════════════════════════════════════════════

``MissionRunner(config, steps, **hooks).run() -> MissionRunResult``

Construct a runner from:

  * ``config: MissionRunnerConfig`` — frozen dataclass of identity +
    policy values (employee handle, mission_run_kind, confidence
    values, dedupe window, etc.). Constructed by the caller from
    AIEmployee + JobContract; the runner has no opinion about how
    these values are derived.
  * ``steps: Sequence[Step]`` — ordered named callables. Each step
    receives the mission ``OpsRun`` and either returns
    ``StepResult(passed=..., output=..., duration_ms=..., extra={...})``
    or raises. The runner converts raises into
    ``StepResult(passed=False)``.
  * ``escalation_body_formatter`` (optional) — ``FailureContext ->
    str``. Used on first escalation in a dedupe window. Defaults to a
    generic structured Markdown body.
  * ``escalation_summary_formatter`` (optional) — ``FailureContext ->
    str``. One-line summary for the PA escalation post. Defaults to a
    generic one-liner.
  * ``escalation_deliverable_spec_factory`` (optional) —
    ``FailureContext -> EscalationDeliverableSpec``. Returns the
    policy for *how* the escalation Deliverable is created
    (``deliverable_type`` / ``category`` / ``publish_intent`` /
    ``initial_status`` / ``force_ready`` / ``audit_completed_to_ready`` /
    workspace targeting). Defaults to a factory that returns
    ``EscalationDeliverableSpec()`` (the baseline PR 1.1 policy:
    type='report', category='ops',
    publish_intent='publish_candidate', initial_status='completed',
    force_ready=True, audit_completed_to_ready=True). Static-policy
    callers wrap a constant spec in ``lambda ctx: SPEC``.
  * ``shift_report_fn`` (optional) — ``OpsRun -> dict``. Called once
    on terminal mission. None → no shift report.
  * ``pa_post_fn`` (optional) — ``PAPostContext -> Optional[str]``.
    Called on escalation. None → no PA post.
  * ``preflight_fn`` (optional) — ``dict -> None``. Mutates the
    summary_acc dict in place before step execution. None → no
    preflight.
  * ``postflight_fn`` (optional) — ``(passed: bool, summary_acc:
    dict) -> None``. Mutates after step execution. None → no
    postflight.

Then call ``.run()`` to execute end-to-end. Returns a
``MissionRunResult`` envelope. **Never raises** (top-level catch logs +
returns ``ok=False``).

Optional secondary entry point: ``run_for_existing(mission)`` accepts a
pre-existing OpsRun row and drives the lifecycle on it, bypassing
daily idempotency. Intended for tests + advanced caller scenarios.

═══════════════════════════════════════════════════════════════════════
INVARIANTS
═══════════════════════════════════════════════════════════════════════

**I1 — Daily idempotency.** Two ``.run()`` calls on the same calendar
day (local timezone) for the same ``(mission_run_kind)`` resolve to
one OpsRun row. The second call returns a cached envelope with
``already_ran=True`` and never re-runs steps. Status of the cached
envelope reflects the current state of the persisted mission.

**I2 — In-progress safety.** If a prior invocation is still
``status='running'``, a concurrent ``.run()`` call returns a
``status='running'`` envelope without creating a second OpsRun. The
caller chose to not double-dispatch.

**I3 — Event idempotency.** Each ``OpsRunEvent`` is written via
``get_or_create(run=mission, label=<label>)``. Re-running the same step
against the same mission writes zero new rows; the existing event
remains.

**I4 — Verdict idempotency.** ``emit_mission_verdict`` is called via
the existing framework helper (which guarantees the event is
get_or_create'd and OpsRun.status only flips from 'running'). Repeat
calls are no-ops on event row + status.

**I5 — Step ordering.** Steps execute in the order given. The first
step to fail halts the cascade; remaining steps emit ``<name>_skipped``
events with ``reason='prior_failure'``.

**I6 — Escalation atomicity.** Escalation Deliverable creation
(create-new + status flip + audit row) and the
``escalation_emitted`` OpsRunEvent are written inside a single
DB transaction. Either both land or neither.

**I7 — Dedupe key.** The escalation dedupe key is
``(failed_step, error_signature)`` matched against OpsRuns with
``status='failed'`` and ``finished_at >= now - dedupe_window_hours``.
Same key within window → append to prior Deliverable (no new row).
Different key OR outside window → create new Deliverable.

**I8 — Hook containment.** ``shift_report_fn``, ``pa_post_fn``,
``preflight_fn``, ``postflight_fn`` exceptions are caught + logged.
The mission outcome is not changed; the result envelope still
reflects the cascade's actual verdict.

**I9 — No employee-specific imports.** This module imports nothing
from ``core.tasks_*`` job modules, nothing from
``core.employees.comms_docs_manager``, and does not reference
``RIGBY`` / ``DOCUMENTATION_MANAGER`` or any other specific employee
or job constant. Verified by a contract test
(``test_mission_runner.MissionRunnerImportContractTests``).

═══════════════════════════════════════════════════════════════════════
EVENT TIMELINE
═══════════════════════════════════════════════════════════════════════

For a successful 3-step mission, ``OpsRunEvent`` rows in
chronological order:

  1. ``run_started``                 (event_type='info')
  2. ``<step1>_started``             (event_type='step_start')
  3. ``<step1>_passed``              (event_type='step_pass')
  4. ``<step2>_started``             (event_type='step_start')
  5. ``<step2>_passed``              (event_type='step_pass')
  6. ``<step3>_started``             (event_type='step_start')
  7. ``<step3>_passed``              (event_type='step_pass')
  8. ``verdict_issued:certified``    (event_type='step_pass')

For a 3-step mission where step 2 fails:

  1. ``run_started``
  2. ``<step1>_started`` / ``<step1>_passed``
  3. ``<step2>_started`` / ``<step2>_failed``
  4. ``<step3>_skipped``             (reason='prior_failure')
  5. ``escalation_emitted``
  6. ``verdict_issued:rejected``

Terminal mission status: ``OpsRun.status`` flips to ``passed`` /
``failed`` / ``partial`` per ``emit_mission_verdict``.

═══════════════════════════════════════════════════════════════════════
ERROR SIGNATURE CANONICALIZATION
═══════════════════════════════════════════════════════════════════════

**MissionRunner owns the canonical error-signature normalization for
the Employee OS.** ``MissionRunner.make_error_signature(failed_step,
error_tail)`` is the single classifier; the implementation lives in
``_normalize_for_signature`` (module-level) and the public static
``make_error_signature`` (class-level). Callers — including tests,
escalation-lookup queries, and downstream tooling — re-derive
signatures by calling this method, never by reimplementing the
normalization.

**Pattern application order is load-bearing.** The volatile-substring
regex list runs in this order:

  1. **UUID** (8-4-4-4-12 hex). UUIDs are normalized as a *unit*
     before any pattern that could match a sub-string of them. This
     prevents the all-numeric trailing segment of UUIDs like
     ``550e8400-e29b-41d4-a716-446655440000`` from being replaced as
     a Unix epoch while the rest of the UUID stays untouched.
  2. **ISO-8601 timestamp** (with optional fractional + offset).
  3. **Bare HH:MM:SS clock.**
  4. **Long numeric** (≥10 digits — Unix-epoch-shaped).

The docs-manager helper that originally motivated this extraction
shipped with the patterns in the reverse order. Two PR 1.1 tests
(``test_signature_stable_across_uuids`` and
``test_uuid_normalization_runs_before_numeric_normalization``)
surfaced the latent ordering bug — the runner fixes it as part of the
canonical extraction.

**This may shift dedupe signatures when Documentation Manager
migrates in PR 1.2.** Failures that produced a stable signature under
the pre-extraction order may produce a different (but still stable)
signature under MissionRunner. This is intentional:

  * The runner's normalization order is **correct** (UUIDs are atomic
    units; matching their suffixes as epochs breaks signature
    stability).
  * The pre-extraction docs-manager signatures were silently wrong for
    failure tails containing UUIDs.
  * Existing escalation rows referencing old signatures are not
    migrated. The 24h dedupe window means any drift is bounded: an
    in-flight recurring failure may produce a new escalation
    Deliverable rather than appending to a prior one for one cycle
    after PR 1.2 lands; subsequent failures dedupe correctly.

**The new canonical ordering is the platform standard from PR 1.1
forward.** Future jobs adopting MissionRunner use this normalization
by construction. Any caller that needs to re-derive a historical
docs-manager signature for archival purposes can use the legacy
regex order — but new signatures are generated only by the runner's
classifier.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import time
import traceback
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


# ── Constants ─────────────────────────────────────────────────────────

DEFAULT_DEDUPE_WINDOW_HOURS = 24
DEFAULT_CONFIDENCE_SUCCESS_FULL = 0.95
DEFAULT_CONFIDENCE_SUCCESS_DEGRADED = 0.6
DEFAULT_CONFIDENCE_FAILURE = 0.0
ERROR_TAIL_LINES_FIRST = 100
ERROR_TAIL_LINES_RECURRENCE = 30

RUN_STARTED_LABEL = "run_started"
ESCALATION_LABEL = "escalation_emitted"

DEFAULT_ESCALATION_SOURCE = "MissionRunner"
DEFAULT_ESCALATION_TITLE_PREFIX = "Mission Escalation"

# Verdict vocabulary — duplicated as local constants so the module's
# top of file does not import from core.employees.mission_verdict.
# Verified equal to the framework constants by a contract test.
VERDICT_CERTIFIED = "certified"
VERDICT_REJECTED = "rejected"
VERDICT_DEFERRED = "deferred"

# Volatile-substring patterns used by error-signature normalization.
# UUID pattern runs FIRST so a UUID with an all-numeric trailing
# segment normalizes as a UUID, not as a Unix-epoch slice of its
# suffix. (The docs-manager helper has the same shape but originally
# in a different order — fixed here as part of the canonical
# extraction; PR 1.2 inherits the fixed order.)
_TIMESTAMP_PATTERNS = [
    # UUID (8-4-4-4-12 hex) — canonical-form replace before the
    # long-numeric pattern can match individual hex segments.
    re.compile(
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
    ),
    # ISO-8601-style timestamp (with optional fractional + offset).
    re.compile(
        r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"
        r"(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?"
    ),
    # Bare HH:MM:SS clock.
    re.compile(r"\b\d{2}:\d{2}:\d{2}(?:[.,]\d+)?\b"),
    # Long numeric (Unix epoch-ish; ≥10 digits).
    re.compile(r"\b\d{10,}(?:\.\d+)?\b"),
]


# ── Type definitions ─────────────────────────────────────────────────


@dataclass(frozen=True)
class StepResult:
    """Result returned by a step function.

    Steps may either return ``StepResult`` directly or raise; the runner
    converts raises into ``StepResult(passed=False, output=<traceback>)``
    so the error-signature path is uniform regardless of how the step
    surfaced the failure.
    """

    passed: bool
    output: str = ""
    duration_ms: int = 0
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Step:
    """One named step in a mission's daily routine.

    ``name``: used as the OpsRunEvent label prefix. For a step named
    ``"step_1_index"`` the runner emits events
    ``step_1_index_started`` / ``step_1_index_passed`` /
    ``step_1_index_failed`` / ``step_1_index_skipped``.

    ``fn``: the actual work. Receives the mission ``OpsRun`` row,
    returns a ``StepResult`` or raises. Lifecycle (events, signature,
    escalation) is owned by the runner, not the step.
    """

    name: str
    fn: Callable[[Any], StepResult]


@dataclass(frozen=True)
class FailureContext:
    """Context passed to escalation formatters."""

    mission_id: Any
    failed_step: str
    error_tail: str
    error_signature: str
    started_at: datetime
    finished_at: datetime
    counts_so_far: Dict[str, Any]


@dataclass(frozen=True)
class PAPostContext:
    """Context passed to the ``pa_post_fn`` hook."""

    failed_step: str
    deliverable_id: str
    mission_id: Any
    primary_chat_id: Optional[str]
    runs_as_user_id: Optional[Any]
    summary_line: str


@dataclass(frozen=True)
class EscalationDeliverableSpec:
    """Policy for how an escalation Deliverable is created.

    Honored by the runner on the create-new branch of
    ``_create_or_append_escalation_deliverable`` (the append branch
    appends to a prior Deliverable's content and does not re-evaluate
    type / publish_intent / status — those are frozen at first creation
    by design).

    Defaults preserve PR 1.1 baseline behavior exactly:
        deliverable_type='report', category='ops',
        publish_intent='publish_candidate' (matches
        ``PublishIntent.PUBLISH_CANDIDATE``),
        initial_status='completed', force_ready=True,
        audit_completed_to_ready=True,
        workspace_id=None, workspace_name=None.

    When all workspace fields are None, the runner falls back to the
    legacy ``MissionRunnerConfig.workspace_name`` lookup so existing
    config-level workspace pointers remain authoritative for callers
    that haven't migrated to spec-based workspace policy.

    ``audit_completed_to_ready=False`` flips the deliverable to
    ``ready`` without setting ``_transition_context`` — no
    ``DeliverableEvent('status_transition')`` audit row is emitted.
    Use this when a caller wants the visible state without paying for
    the audit-row write.

    ``force_ready=False`` skips the flip entirely; the deliverable
    stays at ``initial_status``. Use this when the caller is fine
    leaving the row at ``initial_status`` (e.g., a future job that
    wants escalations as ``draft`` until a separate review step
    promotes them).
    """

    deliverable_type: str = "report"
    category: str = "ops"
    # PublishIntent is a TextChoices enum whose values are bare strings;
    # using the string literal here keeps this dataclass free of Django
    # model imports at module load. The value equals
    # ``PublishIntent.PUBLISH_CANDIDATE``.
    publish_intent: str = "publish_candidate"
    initial_status: str = "completed"
    force_ready: bool = True
    audit_completed_to_ready: bool = True
    workspace_id: Optional[Any] = None
    workspace_name: Optional[str] = None


# Factory type — receives the FailureContext so callers can branch on
# attributes of the failure (e.g. severity from the signature, recurrence
# from prior summaries) when deciding spec values. Static callers wrap
# their constant spec in ``lambda ctx: SPEC``.
EscalationDeliverableSpecFactory = Callable[
    [FailureContext], EscalationDeliverableSpec
]


@dataclass(frozen=True)
class MissionRunResult:
    """Envelope returned by ``MissionRunner.run()``."""

    ok: bool
    mission_id: str
    status: str
    verdict: Optional[str]
    wall_time_ms: int
    summary: Dict[str, Any]
    already_ran: bool = False

    def as_dict(self) -> Dict[str, Any]:
        """For callers that want a plain JSON-safe dict."""
        return {
            "ok": self.ok,
            "mission_id": self.mission_id,
            "status": self.status,
            "verdict": self.verdict,
            "wall_time_ms": self.wall_time_ms,
            "summary": self.summary,
            "already_ran": self.already_ran,
        }


@dataclass(frozen=True)
class MissionRunnerConfig:
    """All policy/identity inputs MissionRunner needs.

    Constructed by the caller from an ``AIEmployee`` + ``JobContract``
    pair (or from raw values in tests). MissionRunner has no opinion
    about where these values come from. Per Rigby constraint #1, this
    is the small dependency struct that makes the runner's external
    contract explicit.
    """

    # Identity
    employee_handle: str
    employee_display_name: str
    runs_as_username: str
    primary_chat_id: Optional[str] = None

    # Job
    mission_run_kind: str = ""
    job_title: str = ""

    # Confidence values (job-tunable)
    confidence_success_full: float = DEFAULT_CONFIDENCE_SUCCESS_FULL
    confidence_success_degraded: float = DEFAULT_CONFIDENCE_SUCCESS_DEGRADED
    confidence_failure: float = DEFAULT_CONFIDENCE_FAILURE

    # Dedupe window (hours)
    dedupe_window_hours: int = DEFAULT_DEDUPE_WINDOW_HOURS

    # Escalation
    escalation_source: str = DEFAULT_ESCALATION_SOURCE
    escalation_title_prefix: str = DEFAULT_ESCALATION_TITLE_PREFIX
    workspace_name: Optional[str] = None

    # Optional settings key for pin override (e.g. "RIGBY_PRIMARY_PA_PIN").
    # When set, the runner consults Django settings under this key first
    # and falls back to ``primary_chat_id`` if the setting is empty.
    pin_settings_key: Optional[str] = None


# ── MissionRunner class ──────────────────────────────────────────────


class MissionRunner:
    """Reusable employee mission lifecycle engine.

    See the module docstring for the full public contract + invariants.
    """

    def __init__(
        self,
        *,
        config: MissionRunnerConfig,
        steps: Sequence[Step],
        escalation_body_formatter: Optional[
            Callable[[FailureContext], str]
        ] = None,
        escalation_summary_formatter: Optional[
            Callable[[FailureContext], str]
        ] = None,
        escalation_deliverable_spec_factory: Optional[
            EscalationDeliverableSpecFactory
        ] = None,
        shift_report_fn: Optional[Callable[[Any], Dict[str, Any]]] = None,
        pa_post_fn: Optional[
            Callable[[PAPostContext], Optional[str]]
        ] = None,
        preflight_fn: Optional[Callable[[Dict[str, Any]], None]] = None,
        postflight_fn: Optional[
            Callable[[bool, Dict[str, Any]], None]
        ] = None,
    ):
        if not config.mission_run_kind:
            raise ValueError(
                "MissionRunnerConfig.mission_run_kind is required; "
                "without it the daily-idempotency lookup cannot scope."
            )
        if not steps:
            raise ValueError(
                "MissionRunner requires at least one Step; got empty sequence."
            )
        self.config = config
        self.steps = tuple(steps)
        self.escalation_body_formatter = (
            escalation_body_formatter
            or _default_escalation_body_formatter
        )
        self.escalation_summary_formatter = (
            escalation_summary_formatter
            or _default_escalation_summary_formatter
        )
        self.escalation_deliverable_spec_factory = (
            escalation_deliverable_spec_factory
            or _default_escalation_deliverable_spec_factory
        )
        self.shift_report_fn = shift_report_fn
        self.pa_post_fn = pa_post_fn
        self.preflight_fn = preflight_fn
        self.postflight_fn = postflight_fn

    # ── Public entry points ──────────────────────────────────────────

    def run(self) -> MissionRunResult:
        """Run the mission end-to-end. Idempotent within the calendar day.

        Per invariants I1 + I2 + I8: never raises. Either runs the
        mission cleanly, returns a cached envelope for an existing
        mission, or catches a top-level error and returns an
        ``ok=False`` envelope with diagnostics in the summary dict.
        """
        try:
            existing = self._existing_mission_for_today()
            if existing is not None:
                return self._cached_envelope(existing)
            mission = self._create_mission_row()
            return self._run_mission(mission)
        except Exception as exc:  # pragma: no cover — defensive top
            logger.exception(
                "[MissionRunner] uncaught top-level exception "
                "(employee=%s, run_kind=%s): %s: %s",
                self.config.employee_handle,
                self.config.mission_run_kind,
                type(exc).__name__,
                exc,
            )
            return MissionRunResult(
                ok=False,
                mission_id="",
                status="unknown",
                verdict=None,
                wall_time_ms=0,
                summary={
                    "runner_error": f"{type(exc).__name__}: {exc}",
                },
            )

    def run_for_existing(self, mission) -> MissionRunResult:
        """Drive lifecycle on a pre-existing OpsRun row.

        Bypasses daily idempotency. Intended for tests + caller
        scenarios that have already created the mission row out-of-band
        (e.g., the ``run_now`` PA-tool path that wants to inject extra
        metadata before dispatch).
        """
        try:
            return self._run_mission(mission)
        except Exception as exc:  # pragma: no cover — defensive
            logger.exception(
                "[MissionRunner.run_for_existing] uncaught exception "
                "mission=%s: %s: %s",
                getattr(mission, "id", "?"),
                type(exc).__name__,
                exc,
            )
            return MissionRunResult(
                ok=False,
                mission_id=str(getattr(mission, "id", "")),
                status=getattr(mission, "status", "unknown"),
                verdict=None,
                wall_time_ms=0,
                summary={
                    "runner_error": f"{type(exc).__name__}: {exc}",
                },
            )

    # ── Mission row lifecycle ────────────────────────────────────────

    def _existing_mission_for_today(self):
        """Return today's OpsRun for this run_kind, if any (I1)."""
        from core.models_ops_runs import OpsRun

        today = timezone.localtime().date()
        return (
            OpsRun.objects.filter(
                domain="mission",
                run_kind=self.config.mission_run_kind,
                started_at__date=today,
            )
            .order_by("-started_at")
            .first()
        )

    def _create_mission_row(self):
        """Create the OpsRun row for this run (I1 negative case)."""
        from core.models_ops_runs import OpsRun

        return OpsRun.objects.create(
            title=(
                f"{self.config.mission_run_kind}: "
                f"{timezone.localtime().strftime('%Y-%m-%d')}"
            ),
            run_type="manual",
            domain="mission",
            run_kind=self.config.mission_run_kind,
            mission_id=uuid.uuid4(),
            triggered_by="beat",
            status="running",
            summary={"started_at_iso": timezone.now().isoformat()},
        )

    def _cached_envelope(self, existing) -> MissionRunResult:
        """Build the ``already_ran=True`` envelope for I1 + I2."""
        return MissionRunResult(
            ok=True,
            mission_id=str(existing.id),
            status=existing.status,
            verdict=(existing.summary or {}).get("verdict"),
            wall_time_ms=(existing.summary or {}).get("wall_time_ms", 0),
            summary=existing.summary or {},
            already_ran=True,
        )

    # ── Event emission (I3) ──────────────────────────────────────────

    def _emit_event(
        self, mission, label: str, event_type: str, **detail: Any
    ):
        """Idempotent ``(run, label)`` event creation (I3)."""
        from core.models_ops_runs import OpsRunEvent

        event, _created = OpsRunEvent.objects.get_or_create(
            run=mission,
            label=label,
            defaults={"event_type": event_type, "detail": detail},
        )
        return event

    # ── Step execution boundary (Rigby #4 + I5) ──────────────────────

    def _run_step(self, mission, step: Step) -> StepResult:
        """Execute one step with lifecycle events around it.

        Catches any step-raised exception and converts it into a
        ``StepResult(passed=False, output=<traceback>)`` so the
        error-signature path is uniform whether the step raised or
        returned ``passed=False`` explicitly.
        """
        self._emit_event(
            mission, f"{step.name}_started", "step_start", step=step.name
        )
        start = time.monotonic()
        try:
            result = step.fn(mission)
            duration_ms = int((time.monotonic() - start) * 1000)
            if not isinstance(result, StepResult):
                # Defensive: a step that returned something other than a
                # StepResult is treated as a failure with the wrong-shape
                # output preserved in the error tail.
                result = StepResult(
                    passed=False,
                    output=(
                        f"Step {step.name!r} returned non-StepResult "
                        f"value: {type(result).__name__}={result!r}"
                    ),
                    duration_ms=duration_ms,
                )
        except Exception as exc:
            duration_ms = int((time.monotonic() - start) * 1000)
            result = StepResult(
                passed=False,
                output=(
                    f"{type(exc).__name__}: {exc}\n"
                    f"{traceback.format_exc()}"
                ),
                duration_ms=duration_ms,
                extra={"raised": True, "exc_class": type(exc).__name__},
            )
        # Re-stamp duration in case the step didn't track it.
        if result.duration_ms == 0 and duration_ms > 0:
            result = StepResult(
                passed=result.passed,
                output=result.output,
                duration_ms=duration_ms,
                extra=result.extra,
            )
        self._emit_event(
            mission,
            f"{step.name}_passed" if result.passed else f"{step.name}_failed",
            "step_pass" if result.passed else "step_fail",
            step=step.name,
            duration_ms=result.duration_ms,
            **{
                k: v
                for k, v in (result.extra or {}).items()
                if isinstance(v, (str, int, float, bool, type(None)))
            },
        )
        return result

    # ── Mission orchestration ────────────────────────────────────────

    def _run_mission(self, mission) -> MissionRunResult:
        """Inner orchestration. Caller catches top-level errors."""
        summary_acc: Dict[str, Any] = {
            "wall_time_ms": 0,
            "failed_step": None,
            "error_tail": None,
            "degraded_evidence": False,
        }
        cascade_start = time.monotonic()
        self._emit_event(
            mission, RUN_STARTED_LABEL, "info",
            run_kind=self.config.mission_run_kind,
        )

        # Preflight (Rigby #7 optional hook — contained).
        if self.preflight_fn is not None:
            try:
                self.preflight_fn(summary_acc)
            except Exception as exc:
                logger.warning(
                    "[MissionRunner] preflight_fn raised; continuing. "
                    "mission=%s err=%s: %s",
                    mission.id, type(exc).__name__, exc,
                )
                summary_acc["degraded_evidence"] = True
                summary_acc["preflight_error"] = (
                    f"{type(exc).__name__}: {exc}"
                )
        self._persist_summary(mission, summary_acc)

        # Step loop (I5 ordering + skipped events).
        failed = False
        accumulated_output = ""
        failed_step_name: Optional[str] = None
        for idx, step in enumerate(self.steps):
            result = self._run_step(mission, step)
            accumulated_output += (
                f"\n--- {step.name} ---\n{result.output}"
            )
            if not result.passed:
                failed = True
                failed_step_name = step.name
                summary_acc["failed_step"] = step.name
                summary_acc["error_tail"] = _tail_lines(
                    accumulated_output, ERROR_TAIL_LINES_FIRST
                )
                summary_acc["error_signature"] = self.make_error_signature(
                    step.name, summary_acc["error_tail"] or ""
                )
                # Emit skipped events for remaining steps.
                for skipped in self.steps[idx + 1:]:
                    self._emit_event(
                        mission,
                        f"{skipped.name}_skipped",
                        "info",
                        reason="prior_failure",
                        step=skipped.name,
                    )
                break

        # Postflight (Rigby #7 optional hook — contained).
        if self.postflight_fn is not None:
            try:
                self.postflight_fn(not failed, summary_acc)
            except Exception as exc:
                logger.warning(
                    "[MissionRunner] postflight_fn raised; continuing. "
                    "mission=%s err=%s: %s",
                    mission.id, type(exc).__name__, exc,
                )
                summary_acc["degraded_evidence"] = True
                summary_acc["postflight_error"] = (
                    f"{type(exc).__name__}: {exc}"
                )

        summary_acc["wall_time_ms"] = int(
            (time.monotonic() - cascade_start) * 1000
        )
        self._persist_summary(mission, summary_acc)

        # Escalation + verdict (I6 + I7).
        if failed:
            escalation_response = self._handle_failure_escalation(
                mission=mission,
                failed_step=failed_step_name or "<unknown>",
                error_tail=summary_acc["error_tail"] or "",
                error_signature=summary_acc.get("error_signature", ""),
                counts_so_far={
                    k: v for k, v in summary_acc.items() if k != "error_tail"
                },
            )
            summary_acc.update(escalation_response)
            self._persist_summary(mission, summary_acc)
            verdict_response = self._emit_terminal_verdict(
                mission_id=mission.id,
                verdict=VERDICT_REJECTED,
                confidence=self.config.confidence_failure,
                evidence_refs=[
                    f"deliverable:{escalation_response.get('escalation_deliverable_id', '')}",
                    f"ops_run:{mission.id}",
                ],
                notes=(
                    f"Cascade failed at {failed_step_name}. "
                    "See escalation deliverable for full evidence."
                ),
            )
        else:
            confidence = (
                self.config.confidence_success_degraded
                if summary_acc["degraded_evidence"]
                else self.config.confidence_success_full
            )
            verdict_response = self._emit_terminal_verdict(
                mission_id=mission.id,
                verdict=VERDICT_CERTIFIED,
                confidence=confidence,
                notes=(
                    "Cascade completed cleanly. "
                    + (
                        "Evidence degraded — counts incomplete."
                        if summary_acc["degraded_evidence"]
                        else "All counts captured."
                    )
                ),
            )

        mission.refresh_from_db()

        # Shift report (Rigby #7 optional hook — contained).
        if self.shift_report_fn is not None:
            try:
                self.shift_report_fn(mission)
            except Exception as exc:
                logger.warning(
                    "[MissionRunner] shift_report_fn raised; "
                    "mission outcome unaffected. mission=%s err=%s: %s",
                    mission.id, type(exc).__name__, exc,
                )

        return MissionRunResult(
            ok=True,
            mission_id=str(mission.id),
            status=mission.status,
            verdict=verdict_response.get("verdict"),
            wall_time_ms=summary_acc["wall_time_ms"],
            summary=mission.summary or {},
        )

    # ── Persistence helpers ──────────────────────────────────────────

    def _persist_summary(self, mission, summary_acc: Dict[str, Any]) -> None:
        """Merge summary_acc into ``mission.summary`` and save."""
        existing = mission.summary or {}
        mission.summary = {**existing, **summary_acc}
        mission.save(update_fields=["summary"])

    # ── Error signature (Rigby #5) ───────────────────────────────────

    @staticmethod
    def make_error_signature(failed_step: str, error_tail: str) -> str:
        """Stable 16-char hex signature of (step + normalized error tail).

        Public + static: Rigby constraint #5 wants ONE canonical place
        for error-signature classification. The runner owns it; callers
        can re-derive it for testing or escalation lookups by calling
        this method.
        """
        normalized = _normalize_for_signature(error_tail)
        payload = failed_step.strip() + "||" + normalized
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]

    # ── Escalation (Rigby #6 + I6 + I7) ──────────────────────────────

    def _handle_failure_escalation(
        self,
        *,
        mission,
        failed_step: str,
        error_tail: str,
        error_signature: str,
        counts_so_far: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create or append escalation Deliverable + optional PA post.

        Returns a dict of fields to merge into ``mission.summary`` so
        subsequent reads (status tool, evidence join, dedupe lookup)
        can find the escalation pointers.
        """
        with transaction.atomic():
            (
                deliverable_id,
                deduped,
                prior_ops_run_id,
            ) = self._create_or_append_escalation_deliverable(
                mission=mission,
                failed_step=failed_step,
                error_tail=error_tail,
                error_signature=error_signature,
                counts_so_far=counts_so_far,
            )
            pa_post_id = self._post_pa_escalation(
                mission=mission,
                failed_step=failed_step,
                deliverable_id=deliverable_id,
                error_signature=error_signature,
                error_tail=error_tail,
                counts_so_far=counts_so_far,
            )
            self._emit_event(
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
                f"appended_to_{deliverable_id}"
                if deduped
                else "new_escalation"
            ),
        }

    def _find_prior_escalation_run(
        self,
        *,
        failed_step: str,
        signature: str,
        current_mission_id: Any,
    ):
        """Last-window same-(step, signature) failure (I7 dedupe key)."""
        from core.models_ops_runs import OpsRun

        cutoff = timezone.now() - timedelta(
            hours=self.config.dedupe_window_hours
        )
        return (
            OpsRun.objects.filter(
                domain="mission",
                run_kind=self.config.mission_run_kind,
                status="failed",
                finished_at__gte=cutoff,
                summary__failed_step=failed_step,
                summary__error_signature=signature,
            )
            .exclude(id=current_mission_id)
            .order_by("-finished_at")
            .first()
        )

    def _create_or_append_escalation_deliverable(
        self,
        *,
        mission,
        failed_step: str,
        error_tail: str,
        error_signature: str,
        counts_so_far: Dict[str, Any],
    ) -> Tuple[str, bool, Optional[str]]:
        """Create a new escalation Deliverable or append to a prior one.

        Returns ``(deliverable_id_str, deduped, prior_ops_run_id_str)``.
        """
        from core.models_deliverables import Deliverable, PublishIntent

        prior_run = self._find_prior_escalation_run(
            failed_step=failed_step,
            signature=error_signature,
            current_mission_id=mission.id,
        )

        if prior_run:
            prior_deliverable_id = (prior_run.summary or {}).get(
                "escalation_deliverable_id"
            )
            prior = None
            if prior_deliverable_id:
                try:
                    prior = Deliverable.objects.get(id=prior_deliverable_id)
                except Deliverable.DoesNotExist:
                    prior = None
            if prior is not None:
                stanza = (
                    f"\n\n## Recurrence: {timezone.now().isoformat()}\n"
                    f"- ops_run: `{mission.id}`\n"
                    f"- error_tail (last "
                    f"{ERROR_TAIL_LINES_RECURRENCE} lines):\n"
                    "```\n"
                    f"{_tail_lines(error_tail, ERROR_TAIL_LINES_RECURRENCE)}"
                    "\n```\n"
                )
                existing_content = prior.content or ""
                prior.content = existing_content + stanza
                prior.preview_content = (
                    prior.content[:500]
                    + ("..." if len(prior.content) > 500 else "")
                )
                prior.save(
                    update_fields=[
                        "content",
                        "preview_content",
                        "updated_at",
                    ]
                )
                return str(prior.id), True, str(prior_run.id)

        # New escalation.
        today_local = timezone.localtime()
        today_str = today_local.strftime("%Y-%m-%d")
        finished = mission.finished_at or timezone.now()
        ctx = FailureContext(
            mission_id=mission.id,
            failed_step=failed_step,
            error_tail=_tail_lines(error_tail, ERROR_TAIL_LINES_FIRST),
            error_signature=error_signature,
            started_at=mission.started_at,
            finished_at=finished,
            counts_so_far=counts_so_far,
        )
        body = self.escalation_body_formatter(ctx)
        spec = self.escalation_deliverable_spec_factory(ctx)
        workspace_id = self._resolve_workspace_for_spec(spec)

        deliverable = Deliverable(
            title=f"{self.config.escalation_title_prefix} — {today_str}",
            slug=(
                f"{_slugify(self.config.escalation_title_prefix)}-"
                f"{today_str}-{uuid.uuid4().hex[:8]}"
            ),
            deliverable_type=spec.deliverable_type,
            # PublishIntent enum values are bare strings; the spec
            # carries the string directly so the dataclass stays
            # import-free. Equivalent to PublishIntent.PUBLISH_CANDIDATE
            # for the default spec.
            publish_intent=spec.publish_intent,
            category=spec.category,
            content=body,
            preview_content=body[:500] + ("..." if len(body) > 500 else ""),
            workspace_id=workspace_id,
            # Default spec lands rows at 'completed' so the subsequent
            # force-ready step is a real transition that fires the
            # post_save signal and writes the DeliverableEvent audit
            # row. A custom spec may set initial_status='ready' to
            # skip the flip + audit row entirely.
            # Memory: feedback_deliverable_create_defaults_to_completed.md.
            status=spec.initial_status,
        )
        deliverable.save()

        # Optional completed→ready flip + audit transition, honoring
        # the spec's force_ready + audit_completed_to_ready knobs.
        if spec.force_ready and spec.initial_status != "ready":
            self._force_deliverable_ready(
                deliverable.id,
                ops_run_id=mission.id,
                error_signature=error_signature,
                emit_audit_event=spec.audit_completed_to_ready,
            )

        return str(deliverable.id), False, None

    def _force_deliverable_ready(
        self,
        deliverable_id: Any,
        *,
        ops_run_id: Any,
        error_signature: str,
        emit_audit_event: bool = True,
    ) -> None:
        """Flip a newly-created Deliverable from completed→ready.

        Default (``emit_audit_event=True``): stashes
        ``_transition_context`` on the instance so the
        ``deliverable_status_signals.record_status_transition``
        post_save receiver fires a
        ``DeliverableEvent('status_transition')`` row, then saves with
        ``update_fields=['status']``. Source is the configured
        ``escalation_source`` value so audit queries can filter on it.

        ``emit_audit_event=False``: flip status without setting
        ``_transition_context``. No ``DeliverableEvent`` row is
        written. Used by specs that want the visible state without
        paying for the audit-row write (e.g. test specs or
        low-severity escalations).

        When ``emit_audit_event=True``, ``ops_run_id`` + ``error_signature``
        are required so the audit row remains queryable. When False,
        both are still accepted for symmetry but neither is consulted.
        """
        from core.models_deliverables import Deliverable

        if emit_audit_event:
            if not error_signature:
                raise ValueError(
                    "_force_deliverable_ready(emit_audit_event=True) "
                    "requires a non-empty error_signature so the "
                    "audit row is queryable."
                )
            if not ops_run_id:
                raise ValueError(
                    "_force_deliverable_ready(emit_audit_event=True) "
                    "requires a non-null ops_run_id so the audit row "
                    "links back to the MissionRun."
                )

        user_id = self._resolve_runs_as_user_id()
        try:
            obj = Deliverable.objects.get(id=deliverable_id)
        except Deliverable.DoesNotExist:
            logger.warning(
                "[MissionRunner] deliverable=%s not found",
                deliverable_id,
            )
            return

        from_status = obj.status
        if from_status not in ("completed", "ready"):
            logger.warning(
                "[MissionRunner] deliverable=%s unexpected from_status=%s; "
                "not flipping",
                deliverable_id, from_status,
            )
            return
        if from_status == "ready":
            return

        if emit_audit_event:
            obj._transition_context = {
                "reason": (
                    f"{self.config.escalation_source} escalation: force "
                    "visible state for human review (workaround for "
                    "create-default-completed bug)."
                ),
                "actor_user_id": str(user_id) if user_id else None,
                "trace_id": None,
                "source": self.config.escalation_source,
                "ops_run_id": str(ops_run_id),
                "error_signature": error_signature,
            }
        obj.status = "ready"
        obj.save(update_fields=["status"])

    # ── Optional PA escalation post (Rigby #7) ───────────────────────

    def _post_pa_escalation(
        self,
        *,
        mission,
        failed_step: str,
        deliverable_id: str,
        error_signature: str,
        error_tail: str,
        counts_so_far: Dict[str, Any],
    ) -> Optional[str]:
        """Call ``pa_post_fn`` hook if supplied (Rigby #7).

        Returns the hook's return value (a row id string, or None).
        Exceptions inside the hook are caught — mission outcome is not
        affected (I8 + Rigby contract test #7).
        """
        if self.pa_post_fn is None:
            return None
        ctx = FailureContext(
            mission_id=mission.id,
            failed_step=failed_step,
            error_tail=error_tail,
            error_signature=error_signature,
            started_at=mission.started_at,
            finished_at=mission.finished_at or timezone.now(),
            counts_so_far=counts_so_far,
        )
        summary_line = self.escalation_summary_formatter(ctx)
        pin = self._resolve_active_pin()
        user_id = self._resolve_runs_as_user_id()
        post_ctx = PAPostContext(
            failed_step=failed_step,
            deliverable_id=deliverable_id,
            mission_id=mission.id,
            primary_chat_id=pin,
            runs_as_user_id=user_id,
            summary_line=summary_line,
        )
        try:
            return self.pa_post_fn(post_ctx)
        except Exception as exc:
            logger.warning(
                "[MissionRunner] pa_post_fn raised; mission outcome "
                "unaffected. mission=%s err=%s: %s",
                mission.id, type(exc).__name__, exc,
            )
            return None

    # ── Verdict emission ─────────────────────────────────────────────

    def _emit_terminal_verdict(
        self,
        *,
        mission_id: Any,
        verdict: str,
        confidence: float,
        evidence_refs: Optional[List[str]] = None,
        notes: str = "",
    ) -> Dict[str, Any]:
        """Wrap the framework ``emit_mission_verdict`` helper.

        Lazy import so the runner's module-level imports stay narrow
        (Rigby constraint #1).
        """
        from core.employees.mission_verdict import emit_mission_verdict

        try:
            return emit_mission_verdict(
                mission_id=mission_id,
                verdict=verdict,
                confidence=confidence,
                evidence_refs=evidence_refs,
                notes=notes,
                issued_by=self.config.employee_handle,
            )
        except Exception as exc:
            logger.warning(
                "[MissionRunner] verdict emission failed mission=%s "
                "err=%s: %s",
                mission_id, type(exc).__name__, exc,
            )
            return {"verdict": None, "error": str(exc)}

    # ── Resolution helpers ───────────────────────────────────────────

    def _resolve_runs_as_user_id(self) -> Optional[Any]:
        """Return the ``User.id`` for the configured runs_as_username."""
        User = get_user_model()
        user = User.objects.filter(
            username__iexact=self.config.runs_as_username
        ).first()
        return getattr(user, "id", None) if user else None

    def _resolve_workspace_id(self) -> Optional[Any]:
        """Look up the configured workspace by name; None if unset/missing.

        Legacy entry point — delegates to ``_resolve_workspace_by_name``
        for the actual ORM lookup. Preserved so callers that don't
        pass a spec still get config-level workspace resolution.
        """
        return self._resolve_workspace_by_name(self.config.workspace_name)

    def _resolve_workspace_by_name(self, name: Optional[str]) -> Optional[Any]:
        """ORM lookup for ``ProjectWorkspace`` by name (case-insensitive).

        Returns the workspace ``id`` or None if missing / unset / lookup
        error. Used by both the legacy ``_resolve_workspace_id`` path and
        the spec-aware ``_resolve_workspace_for_spec`` path.
        """
        if not name:
            return None
        try:
            from core.models_skin_layer import ProjectWorkspace

            ws = ProjectWorkspace.objects.filter(
                name__iexact=name
            ).first()
            return ws.id if ws else None
        except Exception as exc:
            logger.warning(
                "[MissionRunner] workspace lookup failed name=%s "
                "err=%s: %s",
                name, type(exc).__name__, exc,
            )
            return None

    def _resolve_workspace_for_spec(
        self, spec: "EscalationDeliverableSpec"
    ) -> Optional[Any]:
        """Spec-aware workspace resolution.

        Precedence:
          1. ``spec.workspace_id`` (explicit UUID) — used as-is.
          2. ``spec.workspace_name`` — looked up by name.
          3. ``config.workspace_name`` (legacy fallback) — looked up by
             name. Preserves existing config-level workspace pointers
             for callers that haven't migrated to per-mission spec.
          4. None.
        """
        if spec.workspace_id is not None:
            return spec.workspace_id
        if spec.workspace_name:
            return self._resolve_workspace_by_name(spec.workspace_name)
        return self._resolve_workspace_id()

    def _resolve_active_pin(self) -> Optional[str]:
        """Resolve the active PA chat pin per config fallback chain.

        If ``pin_settings_key`` is set, prefer the Django settings value
        under that key; fall back to ``config.primary_chat_id`` if
        empty/unset. Lets a job override its pin via env without
        amending the config code path.
        """
        if self.config.pin_settings_key:
            override = getattr(
                settings, self.config.pin_settings_key, None
            )
            if override:
                return override
        return self.config.primary_chat_id


# ── Module-level helpers ─────────────────────────────────────────────


def _tail_lines(text: str, n: int) -> str:
    """Return the last ``n`` lines of text joined by newlines."""
    if not text:
        return ""
    lines = text.splitlines()
    return "\n".join(lines[-n:])


def _normalize_for_signature(text: str) -> str:
    """Strip volatile substrings before hashing (timestamps + UUIDs)."""
    normalized = text
    for pat in _TIMESTAMP_PATTERNS:
        normalized = pat.sub("<TS>", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _slugify(text: str) -> str:
    """Tiny ascii-slug helper for deliverable slugs. Not URL-canonical."""
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "mission"


# ── Default formatters ───────────────────────────────────────────────


def _default_escalation_body_formatter(ctx: FailureContext) -> str:
    """Generic escalation Deliverable body.

    Used when the caller doesn't supply a custom formatter. Structured
    Markdown with the failure context, error signature, and counts.
    """
    duration_seconds = max(
        0, int((ctx.finished_at - ctx.started_at).total_seconds())
    )
    minutes, seconds = divmod(duration_seconds, 60)
    duration_label = f"{minutes}m {seconds}s"
    when_iso = ctx.finished_at.isoformat()

    lines = [
        f"# Mission Escalation — {when_iso[:10]}",
        "",
        f"**failed_step:** `{ctx.failed_step}`",
        f"**when:** {when_iso}",
        f"**run_duration:** {duration_label}",
        f"**error_signature:** `{ctx.error_signature}`",
        f"**mission_id:** `{ctx.mission_id}`",
        "",
        "## counts_so_far",
        "```json",
        json.dumps(
            ctx.counts_so_far, indent=2, sort_keys=True, default=str
        ),
        "```",
        "",
        "## error_tail",
        "```",
        ctx.error_tail or "(empty)",
        "```",
        "",
        "---",
        "**Human review required: approve next action.**",
    ]
    return "\n".join(lines)


def _default_escalation_summary_formatter(ctx: FailureContext) -> str:
    """Generic one-line PA-post summary."""
    return (
        f"Mission FAILED at {ctx.failed_step} "
        f"(signature {ctx.error_signature}, mission {ctx.mission_id})."
    )


def _default_escalation_deliverable_spec_factory(
    ctx: FailureContext,
) -> EscalationDeliverableSpec:
    """Default factory — returns a baseline spec for every failure.

    Returns ``EscalationDeliverableSpec()`` (all fields at their
    declared defaults). Preserves the PR 1.1 baseline behavior:
    type='report', category='ops',
    publish_intent='publish_candidate', initial_status='completed',
    force_ready=True, audit_completed_to_ready=True, no workspace
    override (falls through to ``MissionRunnerConfig.workspace_name``).

    Callers that need per-failure policy (e.g. a high-severity
    signature flips publish_intent='publish_required') pass their own
    factory at MissionRunner construction time. Static-policy callers
    use ``lambda ctx: EscalationDeliverableSpec(<custom fields>)``.
    """
    return EscalationDeliverableSpec()
