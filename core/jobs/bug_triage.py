"""Bug Triage Specialist job — task runner via MissionRunner (Session 1267 PR 4.2).

Wires the Bug Triage Specialist's daily failure-pattern scan into a
MissionRunner-driven mission. Each step queries one read-only
telemetry source (CeleryTaskEvent / AgentExecution / OpsRun /
OpsRunEvent) over a fixed 24h window, persists structured findings
into ``mission.summary``, and step 6 produces a deterministic
markdown Deliverable with the six contract sections.

MissionRunner owns the lifecycle: OpsRun creation + idempotency,
OpsRunEvent timeline, error-signature classification, escalation
Deliverable (separate from the triage Deliverable — escalation is
the failure-surface, triage is the daily-read-surface), and the
post-run shift-report DM.

**No auto-certification in v0 (Rigby SIGN D1).** MissionRunner's
``auto_emit_verdict=False`` config flag (S1267) suppresses the
default ``verdict_issued:*`` OpsRunEvent + ``emit_mission_verdict``
call. The mission still flips ``OpsRun.status`` to passed/failed via
``_flip_status_without_verdict`` so the lifecycle completes, but the
certification surface stays with Rigby/human review of the daily
triage Deliverable — Rigby (or Chris) issues the actual
``mission_verdict`` via the PA tool after reading the Deliverable.

**Deterministic markdown synthesis (no LLM in v0).** Step 6 builds
the six-section triage report from the data accumulated by steps
1-5 using pure-Python markdown construction. The JobContract's
``evidence_tables`` lists ``LLMCallEvent`` as a future addition;
shipping v0 with deterministic synthesis means no LLM cost and no
flake from synthesis timeouts. If/when LLM-augmented recommendations
land in a follow-up, the contract claim becomes accurate without
a contract update.

**Bounded summary (Rigby SIGN D5).** Postflight transforms any
``error_tail`` written by the failure escalation path into
``error_tail_preview`` (last N lines) + ``has_full_error_tail``
(bool). The full tail remains in ``OpsRunEvent.detail`` — the
escalation deliverable body has the full text. This keeps
``OpsRun.summary`` queryable without bloating it.

This module owns the job-specific bits:

  * 7 step functions reading from the 4 telemetry sources + the
    deterministic Markdown synthesis
  * Triage-report Deliverable persistence (step 6)
  * Postflight that converts the summary to the bounded shape
  * Escalation body formatter (Bug-Triage-flavored)
  * Shift-report body formatter + thin wrapper around the framework
    ``post_shift_report`` helper
  * ``build_bug_triage_runner()`` factory
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.utils import timezone

from core.employees import BUG_TRIAGE_JOB, BUG_TRIAGE_SPECIALIST
from core.employees._persistence import _persist_to_summary
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

MISSION_RUN_KIND = BUG_TRIAGE_JOB.mission_run_kind  # 'bug_triage_daily'

# Escalation labels (per-employee — keep here).
# Confidence + dedupe window defaults live on ``MissionRunnerConfig``;
# Bug Triage takes the defaults so they are NOT redeclared here.
DELIVERABLE_TITLE_PREFIX = "Bug Triage Escalation"
ESCALATION_SOURCE = "BugTriageSpecialist"

# Triage-report Deliverable configuration.
TRIAGE_REPORT_TITLE_PREFIX = "Bug Triage"
TRIAGE_REPORT_DELIVERABLE_TYPE = "analysis"
TRIAGE_REPORT_CATEGORY = "Bug Triage"

# Shift-report thread subject for the inbox DM.
SHIFT_REPORT_THREAD_SUBJECT = "Bug Triage Specialist — Daily Bug Triage"

# Window the triage scans (Rigby SIGN spec — fixed 24h).
WINDOW_HOURS = 24

# Cluster signature prefix length — Rigby SIGN D8 "first 80 chars of
# error_message" applies to both the cluster signature AND
# MissionRunner.make_error_signature dedupe. Kept as a module constant
# so future tuning lands in one place.
ERROR_MESSAGE_PREFIX_CHARS = 80

# Bounded summary (Rigby SIGN D5) — last N lines of error_tail kept in
# ``OpsRun.summary.error_tail_preview``; full text stays in
# OpsRunEvent.detail + the escalation Deliverable body.
ERROR_TAIL_PREVIEW_LINES = 10

# Step row caps — keep mission.summary bounded; the underlying
# OpsRunEvent.detail carries fuller per-step counts when needed.
MAX_FAILURES_RETURNED = 500
MAX_AUTHORITY_EVENTS_RETURNED = 500
MAX_MISSIONS_RETURNED = 500


# ── Window helpers ───────────────────────────────────────────────────


def _now() -> datetime:
    return timezone.now()


def _window_start(now: Optional[datetime] = None) -> datetime:
    return (now or _now()) - timedelta(hours=WINDOW_HOURS)


# ── Cluster signature helpers (Rigby SIGN D8) ────────────────────────


def _cluster_signature(
    *, source: str, primary: str, error_type: str, error_message: str
) -> str:
    """Compose the cluster signature for one failure row.

    Format: ``"{source}|{primary}|{error_type}|{prefix}"`` where
    ``primary`` is the task_name (for celery) or agent_name (for
    agent) and ``prefix`` is the first
    ``ERROR_MESSAGE_PREFIX_CHARS`` chars of the error message. Empty
    fields are written as ``"(none)"`` so the signature stays
    unambiguous when telemetry is sparse.
    """
    primary_clean = (primary or "(none)").strip() or "(none)"
    err_type_clean = (error_type or "(none)").strip() or "(none)"
    msg_clean = (error_message or "").strip().replace("\n", " ")
    prefix = msg_clean[:ERROR_MESSAGE_PREFIX_CHARS] or "(none)"
    return f"{source}|{primary_clean}|{err_type_clean}|{prefix}"


# ── Step 1: collect_celery_failures ──────────────────────────────────


def step_1_collect_celery_failures(mission) -> StepResult:
    """Step 1 — read CeleryTaskEvent FAILUREs in last 24h.

    Persists ``celery_failures_count`` + ``celery_failures`` (bounded
    list of dicts) + ``celery_cluster_aggregates``
    (``{signature: count}`` map for step 5). Also stamps
    ``window_start_iso`` / ``window_end_iso`` since Step 1 is the
    first to know the window.
    """
    start = time.monotonic()

    # Lazy import — Bug Triage module is task-imported by Celery + by
    # the management command; keeping Django models out of the
    # module-level import surface avoids app-ready ordering pitfalls.
    from core.models_celery_telemetry import CeleryTaskEvent

    now = _now()
    window_start = _window_start(now)

    rows: List[Dict[str, Any]] = []
    aggregates: Dict[str, int] = {}
    queryset = (
        CeleryTaskEvent.objects.filter(
            status="FAILURE",
            started_at__gte=window_start,
        )
        .values(
            "task_name", "agent_name", "error_type",
            "error_message", "started_at",
        )
        .order_by("-started_at")[:MAX_FAILURES_RETURNED]
    )
    for row in queryset:
        sig = _cluster_signature(
            source="celery",
            primary=str(row.get("task_name") or ""),
            error_type=str(row.get("error_type") or ""),
            error_message=str(row.get("error_message") or ""),
        )
        aggregates[sig] = aggregates.get(sig, 0) + 1
        rows.append({
            "task_name": str(row.get("task_name") or ""),
            "agent_name": str(row.get("agent_name") or ""),
            "error_type": str(row.get("error_type") or ""),
            "error_message_preview": str(
                row.get("error_message") or ""
            )[:ERROR_MESSAGE_PREFIX_CHARS],
            "started_at_iso": (
                row["started_at"].isoformat()
                if row.get("started_at") else None
            ),
            "signature": sig,
        })

    _persist_to_summary(
        mission,
        window_start_iso=window_start.isoformat(),
        window_end_iso=now.isoformat(),
        celery_failures_count=len(rows),
        celery_failures=rows,
        celery_cluster_aggregates=aggregates,
    )

    duration_ms = int((time.monotonic() - start) * 1000)
    return StepResult(
        passed=True,
        output=(
            f"Collected {len(rows)} Celery FAILURE row(s) in last "
            f"{WINDOW_HOURS}h across {len(aggregates)} signature(s)."
        ),
        duration_ms=duration_ms,
        extra={"rows": len(rows), "signatures": len(aggregates)},
    )


# ── Step 2: collect_agent_failures ───────────────────────────────────


def step_2_collect_agent_failures(mission) -> StepResult:
    """Step 2 — read AgentExecution rows with status='failed' in last 24h.

    Persists ``agent_failures_count`` + ``agent_failures`` (bounded
    list) + ``agent_cluster_aggregates`` map.
    """
    start = time.monotonic()

    # Lazy import — see step 1 docstring.
    from core.models_unified_system import AgentExecution

    window_start = _window_start()

    rows: List[Dict[str, Any]] = []
    aggregates: Dict[str, int] = {}
    queryset = (
        AgentExecution.objects.filter(
            status="failed",
            created_at__gte=window_start,
        )
        .select_related("agent")
        .order_by("-created_at")[:MAX_FAILURES_RETURNED]
    )
    for execution in queryset:
        agent_name = getattr(
            getattr(execution, "agent", None), "agent_name", ""
        ) or ""
        error_message = execution.error_message or ""
        # AgentExecution has no separate error_type column; derive a
        # best-effort label from the first line of error_message.
        error_type = (error_message.split("\n", 1)[0] or "")[
            :ERROR_MESSAGE_PREFIX_CHARS
        ]
        sig = _cluster_signature(
            source="agent",
            primary=agent_name,
            error_type=error_type,
            error_message=error_message,
        )
        aggregates[sig] = aggregates.get(sig, 0) + 1
        rows.append({
            "agent_name": agent_name,
            "task_preview": (execution.task or "")[
                :ERROR_MESSAGE_PREFIX_CHARS
            ],
            "error_message_preview": error_message[
                :ERROR_MESSAGE_PREFIX_CHARS
            ],
            "created_at_iso": (
                execution.created_at.isoformat()
                if execution.created_at else None
            ),
            "signature": sig,
        })

    _persist_to_summary(
        mission,
        agent_failures_count=len(rows),
        agent_failures=rows,
        agent_cluster_aggregates=aggregates,
    )

    duration_ms = int((time.monotonic() - start) * 1000)
    return StepResult(
        passed=True,
        output=(
            f"Collected {len(rows)} AgentExecution failure(s) in last "
            f"{WINDOW_HOURS}h across {len(aggregates)} signature(s)."
        ),
        duration_ms=duration_ms,
        extra={"rows": len(rows), "signatures": len(aggregates)},
    )


# ── Step 3: collect_mission_verdicts ─────────────────────────────────


def step_3_collect_mission_verdicts(mission) -> StepResult:
    """Step 3 — read OpsRun(domain='mission') rows in last 24h.

    Groups by terminal status + ``summary.verdict`` and persists the
    five required ``missions_*`` counts. The triage's own OpsRun is
    excluded from the counts so it doesn't self-count.
    """
    start = time.monotonic()

    from core.models_ops_runs import OpsRun

    window_start = _window_start()

    queryset = (
        OpsRun.objects.filter(
            domain="mission",
            started_at__gte=window_start,
        )
        .exclude(id=mission.id)
        .values("id", "status", "summary", "run_kind", "started_at")
        .order_by("-started_at")[:MAX_MISSIONS_RETURNED]
    )
    total = 0
    certified = 0
    rejected = 0
    deferred = 0
    in_progress = 0
    by_run_kind: Dict[str, int] = {}
    rows: List[Dict[str, Any]] = []
    for row in queryset:
        total += 1
        status = str(row.get("status") or "")
        summary = row.get("summary") or {}
        verdict = (
            str(summary.get("verdict") or "").lower()
            if isinstance(summary, dict) else ""
        )
        if status == "passed" or verdict == "certified":
            certified += 1
        elif status == "failed" or verdict == "rejected":
            rejected += 1
        elif status == "partial" or verdict == "deferred":
            deferred += 1
        elif status == "running":
            in_progress += 1
        run_kind = str(row.get("run_kind") or "")
        if run_kind:
            by_run_kind[run_kind] = by_run_kind.get(run_kind, 0) + 1
        rows.append({
            "id": str(row["id"]),
            "status": status,
            "verdict": verdict or None,
            "run_kind": run_kind,
            "started_at_iso": (
                row["started_at"].isoformat()
                if row.get("started_at") else None
            ),
        })

    _persist_to_summary(
        mission,
        missions_today_total=total,
        missions_certified_count=certified,
        missions_rejected_count=rejected,
        missions_deferred_count=deferred,
        missions_in_progress_count=in_progress,
        missions_by_run_kind=by_run_kind,
        missions_today=rows,
    )

    duration_ms = int((time.monotonic() - start) * 1000)
    return StepResult(
        passed=True,
        output=(
            f"Collected {total} mission(s) in last {WINDOW_HOURS}h "
            f"(certified={certified}, rejected={rejected}, "
            f"deferred={deferred}, in_progress={in_progress})."
        ),
        duration_ms=duration_ms,
        extra={"total": total, "by_run_kind": by_run_kind},
    )


# ── Step 4: collect_authority_events ─────────────────────────────────


def step_4_collect_authority_events(mission) -> StepResult:
    """Step 4 — read OpsRunEvent rows with label='authority_contract_observed'.

    Supports S1264 enforce-mode prereq #2 baseline accumulation. The
    employee handle is extracted from ``detail.employee_handle``;
    rows missing that field fall under ``(unknown)``.
    """
    start = time.monotonic()

    from core.models_ops_runs import OpsRunEvent

    window_start = _window_start()

    queryset = (
        OpsRunEvent.objects.filter(
            label="authority_contract_observed",
            created_at__gte=window_start,
        )
        .values("detail", "created_at")
        .order_by("-created_at")[:MAX_AUTHORITY_EVENTS_RETURNED]
    )
    total = 0
    by_employee: Dict[str, int] = {}
    rows: List[Dict[str, Any]] = []
    for row in queryset:
        total += 1
        detail = row.get("detail") or {}
        handle = (
            str(detail.get("employee_handle") or "").lower()
            if isinstance(detail, dict) else ""
        ) or "(unknown)"
        by_employee[handle] = by_employee.get(handle, 0) + 1
        rows.append({
            "employee_handle": handle,
            "created_at_iso": (
                row["created_at"].isoformat()
                if row.get("created_at") else None
            ),
        })

    _persist_to_summary(
        mission,
        authority_events_count=total,
        authority_events_by_employee=by_employee,
        authority_events=rows,
    )

    duration_ms = int((time.monotonic() - start) * 1000)
    return StepResult(
        passed=True,
        output=(
            f"Collected {total} authority_contract_observed event(s) "
            f"in last {WINDOW_HOURS}h from "
            f"{len(by_employee)} employee(s)."
        ),
        duration_ms=duration_ms,
        extra={"total": total, "by_employee": by_employee},
    )


# ── Step 5: cluster_by_signature ─────────────────────────────────────


def step_5_cluster_by_signature(mission) -> StepResult:
    """Step 5 — merge step 1 + step 2 aggregates and rank by occurrence.

    Persists ``cluster_count`` (distinct signatures across both
    sources), ``top_cluster_signature`` (string), and
    ``top_cluster_occurrences`` (int). When no failures fired in
    either source, all three carry zero / None values so the
    downstream report can render the empty case cleanly.
    """
    start = time.monotonic()

    summary = mission.summary or {}
    celery_aggregates = summary.get("celery_cluster_aggregates") or {}
    agent_aggregates = summary.get("agent_cluster_aggregates") or {}

    merged: Dict[str, int] = {}
    for sig, count in celery_aggregates.items():
        merged[sig] = merged.get(sig, 0) + int(count)
    for sig, count in agent_aggregates.items():
        merged[sig] = merged.get(sig, 0) + int(count)

    cluster_count = len(merged)
    top_cluster_signature: Optional[str] = None
    top_cluster_occurrences = 0
    if merged:
        top_cluster_signature, top_cluster_occurrences = max(
            merged.items(), key=lambda kv: kv[1]
        )

    # Bounded sorted list for the report (top 10 — never the full
    # merged dict; that would explode summary size with N>>0
    # signatures).
    top_clusters = sorted(
        merged.items(), key=lambda kv: kv[1], reverse=True
    )[:10]

    _persist_to_summary(
        mission,
        cluster_count=cluster_count,
        top_cluster_signature=top_cluster_signature,
        top_cluster_occurrences=top_cluster_occurrences,
        top_clusters=[
            {"signature": sig, "occurrences": count}
            for sig, count in top_clusters
        ],
    )

    duration_ms = int((time.monotonic() - start) * 1000)
    return StepResult(
        passed=True,
        output=(
            f"Clustered failures into {cluster_count} distinct "
            f"signature(s); top occurrences {top_cluster_occurrences}."
        ),
        duration_ms=duration_ms,
        extra={
            "cluster_count": cluster_count,
            "top_cluster_occurrences": top_cluster_occurrences,
        },
    )


# ── Step 6: generate_triage_report ───────────────────────────────────


def step_6_generate_triage_report(mission) -> StepResult:
    """Step 6 — build the triage Deliverable with the 6 required sections.

    Reads everything accumulated in mission.summary by steps 1-5 and
    produces a deterministic markdown report. Persists the Deliverable
    + writes ``report_deliverable_id`` / ``report_chars`` /
    ``recommendations_count`` into the summary.

    No LLM (v0) — synthesis is pure-Python markdown construction.
    The Recommendations section is rule-derived from the top cluster
    + counts.
    """
    start = time.monotonic()

    summary = mission.summary or {}
    today_local = timezone.localtime()
    today_str = today_local.strftime("%Y-%m-%d")
    when_iso = today_local.isoformat()

    recommendations = _derive_recommendations(summary)
    body = _build_triage_report_markdown(
        today_str=today_str,
        when_iso=when_iso,
        mission=mission,
        summary=summary,
        recommendations=recommendations,
    )

    try:
        deliverable_id = _persist_triage_deliverable(
            mission=mission, today_str=today_str, body=body
        )
    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        return StepResult(
            passed=False,
            output=(
                "Failed to persist triage Deliverable: "
                f"{type(exc).__name__}: {exc}"
            ),
            duration_ms=duration_ms,
        )

    _persist_to_summary(
        mission,
        report_deliverable_id=deliverable_id,
        report_chars=len(body),
        recommendations_count=len(recommendations),
        recommendations=recommendations,
    )

    duration_ms = int((time.monotonic() - start) * 1000)
    return StepResult(
        passed=True,
        output=(
            f"Triage Deliverable {deliverable_id} created "
            f"({len(body)} chars); {len(recommendations)} recommendation(s)."
        ),
        duration_ms=duration_ms,
        extra={
            "deliverable_id": deliverable_id,
            "report_chars": len(body),
            "recommendations_count": len(recommendations),
        },
    )


# ── Step 7: record_run_summary ───────────────────────────────────────


def step_7_record_run_summary(mission) -> StepResult:
    """Step 7 — record final run summary metadata.

    No-op-ish: MissionRunner handles status flip via
    ``_flip_status_without_verdict`` (because
    ``auto_emit_verdict=False``); this step exists to emit a
    timeline event so step events fire even on the clean path
    (Rigby SIGN D4). The bounded summary transformation
    (``error_tail`` → ``error_tail_preview`` + ``has_full_error_tail``)
    lives in ``_postflight`` since postflight runs on the failure
    path too — Step 7 never runs on failure.
    """
    start = time.monotonic()

    summary = mission.summary or {}
    celery = int(summary.get("celery_failures_count") or 0)
    agent = int(summary.get("agent_failures_count") or 0)
    missions = int(summary.get("missions_today_total") or 0)
    authority = int(summary.get("authority_events_count") or 0)
    clusters = int(summary.get("cluster_count") or 0)

    duration_ms = int((time.monotonic() - start) * 1000)
    return StepResult(
        passed=True,
        output=(
            f"Run summary recorded: {celery} celery + {agent} agent "
            f"failures, {missions} missions, {authority} authority "
            f"events, {clusters} clusters. No auto-certification (v0)."
        ),
        duration_ms=duration_ms,
        extra={
            "celery_failures_count": celery,
            "agent_failures_count": agent,
            "missions_today_total": missions,
            "cluster_count": clusters,
        },
    )


# ── Recommendation derivation (rule-based, no LLM) ───────────────────


def _derive_recommendations(summary: Dict[str, Any]) -> List[Dict[str, str]]:
    """Build the prioritized recommendations list from accumulated data.

    Pure rules — no LLM call. Each rule fires conditionally on the
    summary contents from steps 1-5.
    """
    recommendations: List[Dict[str, str]] = []

    top_sig = summary.get("top_cluster_signature")
    top_occ = int(summary.get("top_cluster_occurrences") or 0)
    if top_sig and top_occ >= 3:
        recommendations.append({
            "priority": "high",
            "finding": (
                f"Recurring failure cluster (×{top_occ}): {top_sig}"
            ),
            "action": (
                "Investigate the root cause of the top failure pattern. "
                "Open a follow-up PR if a code fix is warranted."
            ),
        })

    celery_count = int(summary.get("celery_failures_count") or 0)
    if celery_count > 20:
        recommendations.append({
            "priority": "high",
            "finding": (
                f"{celery_count} Celery task FAILUREs in last "
                f"{WINDOW_HOURS}h — significantly above baseline."
            ),
            "action": (
                "Sample 3-5 failures across signatures to spot whether "
                "this is a single source-of-truth outage or a broader "
                "regression."
            ),
        })

    agent_count = int(summary.get("agent_failures_count") or 0)
    if agent_count > 10:
        recommendations.append({
            "priority": "medium",
            "finding": (
                f"{agent_count} AgentExecution failure(s) in last "
                f"{WINDOW_HOURS}h."
            ),
            "action": (
                "Confirm which agents account for the bulk and whether "
                "any are exercising a degraded upstream (e.g., spider "
                "source drought)."
            ),
        })

    missions_rejected = int(
        summary.get("missions_rejected_count") or 0
    )
    if missions_rejected > 0:
        recommendations.append({
            "priority": "medium",
            "finding": (
                f"{missions_rejected} mission(s) failed in last "
                f"{WINDOW_HOURS}h."
            ),
            "action": (
                "Review the corresponding escalation Deliverables; "
                "decide whether to retry, defer, or open a fix PR."
            ),
        })

    auth_total = int(summary.get("authority_events_count") or 0)
    if auth_total > 0:
        recommendations.append({
            "priority": "low",
            "finding": (
                f"{auth_total} authority_contract_observed event(s) "
                f"recorded — extends S1264 enforce-mode baseline."
            ),
            "action": (
                "No action required; baseline accrues automatically. "
                "Cross-reference with monthly authority audits."
            ),
        })

    return recommendations


# ── Deliverable persistence ──────────────────────────────────────────


def _persist_triage_deliverable(
    *, mission, today_str: str, body: str,
) -> str:
    """Create the triage-report Deliverable + return its id as string."""
    from core.models_deliverables import Deliverable, PublishIntent
    from core.models_skin_layer import ProjectWorkspace

    workspace = ProjectWorkspace.objects.filter(
        name__iexact=EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME
    ).first()
    workspace_id = workspace.id if workspace else None

    deliverable = Deliverable(
        title=f"{TRIAGE_REPORT_TITLE_PREFIX} — {today_str}",
        slug=f"bug-triage-{today_str}-{uuid.uuid4().hex[:8]}",
        deliverable_type=TRIAGE_REPORT_DELIVERABLE_TYPE,
        publish_intent=PublishIntent.PUBLISH_CANDIDATE,
        category=TRIAGE_REPORT_CATEGORY,
        content=body,
        preview_content=body[:500] + ("..." if len(body) > 500 else ""),
        workspace_id=workspace_id,
        # Match PA pattern — create directly at 'ready' so the
        # Deliverable is immediately visible in the workspace.
        # (PA workaround for the S1252 create-defaults-completed
        # footgun; same applies here per Rigby D3.)
        status="ready",
    )
    deliverable.save()
    return str(deliverable.id)


# ── Markdown report builder ──────────────────────────────────────────


def _build_triage_report_markdown(
    *,
    today_str: str,
    when_iso: str,
    mission,
    summary: Dict[str, Any],
    recommendations: List[Dict[str, str]],
) -> str:
    """Construct the markdown triage report (no LLM)."""
    window_start_iso = summary.get("window_start_iso", "?")
    window_end_iso = summary.get("window_end_iso", "?")
    celery_count = int(summary.get("celery_failures_count") or 0)
    agent_count = int(summary.get("agent_failures_count") or 0)
    missions_total = int(summary.get("missions_today_total") or 0)
    missions_certified = int(summary.get("missions_certified_count") or 0)
    missions_rejected = int(summary.get("missions_rejected_count") or 0)
    missions_deferred = int(summary.get("missions_deferred_count") or 0)
    missions_in_progress = int(
        summary.get("missions_in_progress_count") or 0
    )
    missions_by_run_kind = summary.get("missions_by_run_kind") or {}
    authority_count = int(summary.get("authority_events_count") or 0)
    authority_by_employee = summary.get(
        "authority_events_by_employee"
    ) or {}
    cluster_count = int(summary.get("cluster_count") or 0)
    top_cluster_signature = summary.get("top_cluster_signature")
    top_cluster_occurrences = int(
        summary.get("top_cluster_occurrences") or 0
    )
    top_clusters = summary.get("top_clusters") or []

    lines: List[str] = []
    lines.append(f"# {TRIAGE_REPORT_TITLE_PREFIX} — {today_str}")
    lines.append("")
    lines.append(f"**window_start:** {window_start_iso}  ")
    lines.append(f"**window_end:** {window_end_iso}  ")
    lines.append(f"**when:** {when_iso}  ")
    lines.append(f"**mission_id:** `{mission.id}`")
    lines.append("")

    # 1. Window Summary
    lines.append("## Window Summary")
    lines.append(
        f"- Celery task FAILUREs (24h): **{celery_count}**"
    )
    lines.append(
        f"- AgentExecution failures (24h): **{agent_count}**"
    )
    lines.append(
        f"- Missions executed (24h): **{missions_total}** "
        f"({missions_certified} certified, {missions_rejected} rejected, "
        f"{missions_deferred} deferred, {missions_in_progress} in-progress)"
    )
    lines.append(
        f"- Authority contract observations (24h): **{authority_count}**"
    )
    lines.append(
        f"- Distinct failure-signature clusters: **{cluster_count}**"
    )
    lines.append("")

    # 2. Top Failure Patterns
    lines.append("## Top Failure Patterns")
    if not top_clusters:
        lines.append(
            "_No failure clusters in window — no Celery FAILUREs and no "
            "AgentExecution failures._"
        )
    else:
        for idx, cluster in enumerate(top_clusters, start=1):
            sig = str(cluster.get("signature") or "(unknown)")
            occ = int(cluster.get("occurrences") or 0)
            lines.append(f"{idx}. **×{occ}** — `{sig}`")
    lines.append("")

    # 3. Mission Verdicts Today
    lines.append("## Mission Verdicts Today")
    if missions_total == 0:
        lines.append("_No missions ran in window._")
    else:
        lines.append(
            f"- Certified: **{missions_certified}**  "
        )
        lines.append(
            f"- Rejected: **{missions_rejected}**  "
        )
        lines.append(
            f"- Deferred: **{missions_deferred}**  "
        )
        lines.append(
            f"- In-progress: **{missions_in_progress}**"
        )
        if missions_by_run_kind:
            lines.append("")
            lines.append("By run_kind:")
            for kind, count in sorted(missions_by_run_kind.items()):
                lines.append(f"- `{kind}`: {count}")
    lines.append("")

    # 4. Authority Telemetry Today
    lines.append("## Authority Telemetry Today")
    if authority_count == 0:
        lines.append(
            "_No `authority_contract_observed` events fired in window._"
        )
    else:
        lines.append(
            f"Total events: **{authority_count}** across "
            f"{len(authority_by_employee)} employee(s)."
        )
        lines.append("")
        for handle, count in sorted(authority_by_employee.items()):
            lines.append(f"- `{handle}`: {count}")
    lines.append("")

    # 5. Recommendations
    lines.append("## Recommendations")
    if not recommendations:
        lines.append(
            "_Nothing actionable surfaced — window is clean._"
        )
    else:
        for rec in recommendations:
            priority = rec.get("priority", "low")
            finding = rec.get("finding", "(no finding)")
            action = rec.get("action", "(no action)")
            lines.append(f"- **[{priority}]** {finding}")
            lines.append(f"  - **Action:** {action}")
    lines.append("")

    # 6. Green Checks
    lines.append("## Green Checks")
    if celery_count == 0:
        lines.append("- No Celery FAILUREs in window.")
    if agent_count == 0:
        lines.append("- No AgentExecution failures in window.")
    if missions_rejected == 0 and missions_total > 0:
        lines.append(
            f"- All {missions_total} mission(s) completed cleanly."
        )
    if top_cluster_occurrences == 0:
        lines.append("- No recurring failure cluster of concern.")
    if (
        celery_count > 0
        or agent_count > 0
        or missions_rejected > 0
        or top_cluster_occurrences > 0
    ):
        # At least one negative existed — make sure the section isn't empty.
        pass
    if not lines[-1].startswith("- ") and not lines[-1].endswith(":"):
        # Section is empty (all conditions failed) — add a sentinel.
        lines.append(
            "- _No clean indicators in window — review recommendations._"
        )
    lines.append("")

    lines.append("---")
    lines.append(
        f"*Generated by Bug Triage Specialist (MissionRunner-driven, "
        f"no LLM synthesis in v0; top {len(top_clusters)} clusters shown).*"
    )

    return "\n".join(lines)


# ── Postflight: bounded summary transform (Rigby SIGN D5) ────────────


def _postflight(ctx: PostflightContext) -> None:
    """Transform any ``error_tail`` in summary into bounded form.

    Runs on BOTH success and failure paths. On success path,
    ``error_tail`` is normally absent → posts ``error_tail_preview=None``
    + ``has_full_error_tail=False`` so the contract-required keys
    are always present. On failure path, ``error_tail`` was set by
    MissionRunner's escalation flow → keep last N lines + flip the
    boolean. The full tail remains in the OpsRunEvent.detail + the
    escalation Deliverable body (per Rigby SIGN D5 + evidence_tables
    pointer).
    """
    summary_acc = ctx.summary_acc
    full_tail = str(summary_acc.get("error_tail") or "")
    if full_tail:
        # Keep last N lines; cap each line's length lightly so a single
        # mega-line doesn't blow up the summary.
        tail_lines = full_tail.splitlines()
        preview_lines = tail_lines[-ERROR_TAIL_PREVIEW_LINES:]
        summary_acc["error_tail_preview"] = "\n".join(preview_lines)
        summary_acc["has_full_error_tail"] = True
    else:
        summary_acc["error_tail_preview"] = None
        summary_acc["has_full_error_tail"] = False
    # Drop the raw ``error_tail`` from the summary — the contract
    # explicitly bound the summary (Rigby SIGN D5). Full tail is
    # already on the OpsRunEvent timeline.
    summary_acc.pop("error_tail", None)


# ── Escalation body formatter (failure path) ─────────────────────────


def build_escalation_body(ctx: FailureContext) -> str:
    """Bug-Triage-specific escalation Deliverable body.

    Same shape as the PA + docs cascade escalation body but with
    Bug-Triage-flavored language and the full error tail (the
    escalation Deliverable is where the full tail lives per
    Rigby SIGN D5).
    """
    today_local = timezone.localtime()
    today_str = today_local.strftime("%Y-%m-%d")
    when_iso = today_local.isoformat()
    duration_seconds = max(
        0, int((ctx.finished_at - ctx.started_at).total_seconds())
    )
    minutes, seconds = divmod(duration_seconds, 60)
    run_duration_label = f"{minutes}m {seconds}s"

    lines = [
        f"# {DELIVERABLE_TITLE_PREFIX} — {today_str}",
        "",
        f"**failed_step:** `{ctx.failed_step}`",
        f"**when:** {when_iso}  ",
        f"**run_duration_so_far:** {run_duration_label}",
        f"**error_signature:** `{ctx.error_signature}`",
        f"**ops_run_id:** `{ctx.mission_id}`",
        "",
        "## what_happened",
        (
            f"Step `{ctx.failed_step}` of the Daily Bug Triage cascade "
            "raised or returned a failure shape before the triage "
            "Deliverable could be persisted. The triage report for "
            "this window is unavailable — investigate the failure "
            "before re-running."
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

    Used only if a ``pa_post_fn`` hook is wired. PR 4.2 leaves
    ``pa_post_fn=None`` because BUG_TRIAGE_SPECIALIST has no
    ``primary_chat_id`` (visibility is via the inbox shift-report DM +
    the triage Deliverable).
    """
    return (
        f"Bug Triage FAILED at {ctx.failed_step} "
        f"(signature {ctx.error_signature}, mission {ctx.mission_id})."
    )


# ── Escalation deliverable spec factory ──────────────────────────────


def _bug_triage_escalation_spec_factory(
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


# ── Shift-report dispatch ────────────────────────────────────────────


def _format_shift_report_body(mission, summary: Dict[str, Any]) -> str:
    """Bug-Triage-specific shift-report DM body.

    Branches: completed-clean (passed status; no auto-cert verdict)
    vs failed. The "verdict" semantic for Bug Triage v0 lives with
    the OpsRun.status because ``auto_emit_verdict=False`` (no
    ``verdict_issued:*`` OpsRunEvent fires from the runner —
    certification is the operator's call later via the PA tool).
    """
    status = (mission.status or "").lower()
    wall_ms = summary.get("wall_time_ms")
    seconds = (
        f"{wall_ms / 1000:.1f}"
        if isinstance(wall_ms, (int, float))
        else "?"
    )

    if status == "passed":
        celery = int(summary.get("celery_failures_count") or 0)
        agent = int(summary.get("agent_failures_count") or 0)
        missions = int(summary.get("missions_today_total") or 0)
        clusters = int(summary.get("cluster_count") or 0)
        recs = int(summary.get("recommendations_count") or 0)
        report_id = summary.get("report_deliverable_id")
        report_phrase = (
            f"Triage deliverable {report_id}."
            if report_id
            else "Triage deliverable not recorded."
        )
        return (
            f"Bug Triage mission {mission.id} completed cleanly "
            f"in {seconds}s. "
            f"Window: {celery} celery + {agent} agent failures, "
            f"{missions} missions, {clusters} clusters, {recs} "
            f"recommendation(s). {report_phrase} Awaiting "
            f"Rigby/human verdict via PA tool (v0 does not auto-certify)."
        )

    if status == "failed":
        failed_step = summary.get("failed_step") or "<unknown step>"
        escalation_id = summary.get("escalation_deliverable_id")
        esc_phrase = (
            f"Escalation deliverable {escalation_id} created."
            if escalation_id
            else "No escalation deliverable recorded."
        )
        return (
            f"Bug Triage mission {mission.id} failed at "
            f"{failed_step}. {esc_phrase}"
        )

    return (
        f"Bug Triage mission {mission.id} reached terminal state "
        f"with status={status!r}."
    )


# Extra metadata keys carried in the DM (beyond comms.py BASE keys).
_SHIFT_REPORT_EXTRA_KEYS: Tuple[str, ...] = (
    "celery_failures_count",
    "agent_failures_count",
    "missions_today_total",
    "cluster_count",
    "top_cluster_occurrences",
    "report_deliverable_id",
    "recommendations_count",
    "failed_step",
    "escalation_deliverable_id",
)


def post_bug_triage_shift_report(mission) -> Dict[str, Any]:
    """Post a Bug Triage shift-report DM for ``mission``.

    Delegates to the framework ``post_shift_report`` helper with
    Bug-Triage-specific subject + body formatter + extra metadata
    keys + ``sender_type='system'``.
    """
    from core.employees.comms import post_shift_report

    return post_shift_report(
        employee=BUG_TRIAGE_SPECIALIST,
        job="triage_daily",
        mission=mission,
        body_formatter=_format_shift_report_body,
        extra_metadata_keys=_SHIFT_REPORT_EXTRA_KEYS,
        thread_subject=SHIFT_REPORT_THREAD_SUBJECT,
        sender_type="system",
    )


def _shift_report_hook(mission) -> Dict[str, Any]:
    """MissionRunner ``shift_report_fn`` hook — delegates to the wrapper."""
    return post_bug_triage_shift_report(mission)


# ── Public factory ───────────────────────────────────────────────────


def build_bug_triage_runner() -> MissionRunner:
    """Wire the Daily Bug Triage job into a MissionRunner.

    Called by the Celery task in ``core.tasks_bug_triage``. Pure: no
    per-call mutable state, no closure-capture.

    Bug Triage is the first employee to opt out of server-side
    verdict emission (``auto_emit_verdict=False``) per Rigby SIGN
    D1 — Rigby/human writes the actual ``mission_verdict`` later
    via the PA tool path after reviewing the daily triage Deliverable.
    """
    config = MissionRunnerConfig(
        # Identity
        employee_handle=BUG_TRIAGE_SPECIALIST.handle,
        employee_display_name=BUG_TRIAGE_SPECIALIST.display_name,
        runs_as_username=BUG_TRIAGE_SPECIALIST.runs_as_username,
        primary_chat_id=BUG_TRIAGE_SPECIALIST.primary_chat_id,  # None
        # Job
        mission_run_kind=MISSION_RUN_KIND,
        job_title=BUG_TRIAGE_JOB.title,
        # Session 1264 — opt into authority warn-mode observation.
        job_contract=BUG_TRIAGE_JOB,
        # Escalation
        escalation_source=ESCALATION_SOURCE,
        escalation_title_prefix=DELIVERABLE_TITLE_PREFIX,
        # No pin_settings_key — Bug Triage has no pinned PA chat in v0.
        pin_settings_key=None,
        # Session 1267 — opt OUT of server-side verdict emission.
        # MissionRunner still flips OpsRun.status to passed/failed;
        # no verdict_issued OpsRunEvent fires. Certification stays
        # with Rigby/human via the PA tool path.
        auto_emit_verdict=False,
    )

    steps = [
        Step(
            name="step_1_collect_celery_failures",
            fn=step_1_collect_celery_failures,
        ),
        Step(
            name="step_2_collect_agent_failures",
            fn=step_2_collect_agent_failures,
        ),
        Step(
            name="step_3_collect_mission_verdicts",
            fn=step_3_collect_mission_verdicts,
        ),
        Step(
            name="step_4_collect_authority_events",
            fn=step_4_collect_authority_events,
        ),
        Step(
            name="step_5_cluster_by_signature",
            fn=step_5_cluster_by_signature,
        ),
        Step(
            name="step_6_generate_triage_report",
            fn=step_6_generate_triage_report,
        ),
        Step(
            name="step_7_record_run_summary",
            fn=step_7_record_run_summary,
        ),
    ]

    return MissionRunner(
        config=config,
        steps=steps,
        escalation_body_formatter=build_escalation_body,
        escalation_summary_formatter=build_pa_summary_line,
        escalation_deliverable_spec_factory=(
            _bug_triage_escalation_spec_factory
        ),
        shift_report_fn=_shift_report_hook,
        # v0: no PA chat post (BUG_TRIAGE_SPECIALIST has no
        # primary_chat_id; visibility goes via inbox + triage
        # Deliverable).
        pa_post_fn=None,
        preflight_fn=None,
        # Bounded summary transform happens here (Rigby SIGN D5).
        postflight_fn=_postflight,
    )
