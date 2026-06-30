"""Platform Audit job — task runner via MissionRunner (Session 1257 PR 2.2).

Wires the existing PlatformAuditAgent's read-only tool methods into a
MissionRunner-driven mission. Each cascade step calls one of the
agent's pure-Python audit tools (no LLM calls) and persists its
findings into mission.summary. Step 5 builds a markdown audit
Deliverable deterministically — no LLM synthesis.

MissionRunner owns the lifecycle: OpsRun creation + idempotency,
OpsRunEvent timeline, error-signature classification, escalation
Deliverable (separate from the audit Deliverable — escalation is the
failure-surface, audit is the success-surface), verdict emission,
shift-report DM dispatch.

This module owns the job-specific bits:
  * 5 step functions wrapping the agent's tool methods
  * Markdown audit-report builder + Deliverable persistence (step 5)
  * Escalation body formatter (platform-audit-specific)
  * Shift-report body formatter + thin wrapper around the framework
    ``post_shift_report`` helper
  * ``build_platform_audit_runner()`` factory

**No LLM budget consumed.** Each step calls a pure-Python tool method:
file reads (step 1), ``os.getenv`` lookups (steps 2–3), ORM
``.count()`` queries (step 4), and deterministic markdown
construction (step 5). PlatformAuditAgent's ``execute()`` (the only
LLM entry point on the agent) is deliberately NOT used.

**No closure-capture, no shared mutable state.** Each step
instantiates ``PlatformAuditAgent(user=None)`` inline (cheap; the
agent's ``__init__`` is light). The factory is pure — same shape as
docs_cascade after PR 1.3.

**Defensive guards live at the step boundary**, not at the postflight,
because this job has no postflight (no before/after probes; no drift
observation). If a step fails, MissionRunner emits the failed event
and the escalation flow takes over.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from django.utils import timezone

from core.employees import PLATFORM_AUDITOR, PLATFORM_AUDIT_JOB
from core.employees.jobs import EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME
from core.employees.mission_runner import (
    EscalationDeliverableSpec,
    FailureContext,
    MissionRunner,
    MissionRunnerConfig,
    PAPostContext,
    Step,
    StepResult,
)

logger = logging.getLogger(__name__)


# ── Constants ─────────────────────────────────────────────────────────

MISSION_RUN_KIND = PLATFORM_AUDIT_JOB.mission_run_kind  # 'platform_audit'

# Escalation labels (per-employee — keep here).
# Confidence + dedupe window defaults live on ``MissionRunnerConfig``
# (mission_runner.py:255-258 + :497-502); platform_audit takes the
# defaults so they are NOT redeclared here. The workspace name lives in
# ``core.employees.jobs.EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME`` and is
# imported above (also used by the audit-deliverable workspace ORM
# lookup below — keep the import even though config.workspace_name is
# no longer passed).
DELIVERABLE_TITLE_PREFIX = "Platform Audit Escalation"
ESCALATION_SOURCE = "PlatformAuditor"

# The 6 canonical docs scanned in step 1. PR 2.1 contract names these.
CANONICAL_DOCS: Tuple[str, ...] = (
    "CLAUDE.md",
    "00-START-NEXT-SESSION.md",
    "SPIDERS.md",
    "AGENTS.md",
    "SERVICES.md",
    "ARCHITECTURE.md",
)

# The 8 canonical models counted in step 4. PR 2.1 contract names these.
CANONICAL_MODELS: Tuple[str, ...] = (
    "Agent",
    "AgentExecution",
    "AgentMemory",
    "LegacySpiderData",
    "Conversation",
    "User",
    "ImageHistory",
    "VideoHistory",
)

# Audit type label written into mission.summary.
AUDIT_TYPE_DEFAULT = "comprehensive"

# Audit report Deliverable configuration.
AUDIT_REPORT_TITLE_PREFIX = "Platform Audit"
AUDIT_REPORT_DELIVERABLE_TYPE = "analysis"
AUDIT_REPORT_CATEGORY = "Platform Audit"

# Shift-report thread subject for the inbox DM.
SHIFT_REPORT_THREAD_SUBJECT = "Platform Auditor — Platform Audit"


# ── Summary persistence helper ────────────────────────────────────────


def _persist_to_summary(mission, **fields: Any) -> None:
    """Atomically merge ``fields`` into ``mission.summary``.

    Each step writes its findings via this helper. MissionRunner's
    own ``_persist_summary`` later merges runner-level keys
    (wall_time_ms, verdict, failed_step, error_tail, …) without
    overwriting step-written keys — the two key sets don't collide.
    """
    existing = mission.summary or {}
    mission.summary = {**existing, **fields}
    mission.save(update_fields=["summary"])


# ── Agent factory (per-step instantiation; no shared state) ───────────


def _make_agent():
    """Return a fresh ``PlatformAuditAgent`` instance.

    Each step instantiates its own agent. The agent's ``__init__`` is
    light (BaseAgent setup; no LLM client construction). Keeping this
    per-step instead of a module-level singleton means no shared
    mutable state between concurrent missions and no test bleed.
    """
    from core.agents.platform_audit_agent import PlatformAuditAgent

    return PlatformAuditAgent(user=None)


# ── Step 1: read_documentation ────────────────────────────────────────


def step_1_read_docs(mission) -> StepResult:
    """Step 1 — read the 6 canonical platform docs.

    Each doc is read individually; missing files are logged as
    degraded evidence but do NOT fail the step (the contract treats
    docs as best-effort observation). The step writes
    ``docs_audited`` (list of doc names actually read) into
    mission.summary; total chars across read docs is captured for
    the synthesis step.
    """
    start = time.monotonic()
    agent = _make_agent()
    docs_audited: List[str] = []
    docs_missing: List[str] = []
    docs_errors: List[Dict[str, str]] = []
    total_chars = 0

    for doc_name in CANONICAL_DOCS:
        try:
            result = agent._read_documentation(doc_name)
            if "error" in result:
                docs_missing.append(doc_name)
                docs_errors.append(
                    {"doc": doc_name, "error": str(result["error"])}
                )
                continue
            length = int(result.get("length") or 0)
            total_chars += length
            docs_audited.append(doc_name)
        except Exception as exc:
            docs_missing.append(doc_name)
            docs_errors.append(
                {"doc": doc_name, "error": f"{type(exc).__name__}: {exc}"}
            )

    duration_ms = int((time.monotonic() - start) * 1000)
    degraded = bool(docs_missing)

    _persist_to_summary(
        mission,
        docs_audited=docs_audited,
        docs_audited_count=len(docs_audited),
        docs_missing=docs_missing,
        docs_total_chars=total_chars,
    )
    if degraded:
        _persist_to_summary(mission, degraded_evidence=True)

    return StepResult(
        passed=True,
        output=(
            f"Read {len(docs_audited)}/{len(CANONICAL_DOCS)} docs; "
            f"missing: {docs_missing or 'none'}; total chars "
            f"{total_chars}."
        ),
        duration_ms=duration_ms,
        extra={
            "docs_read": len(docs_audited),
            "docs_missing_count": len(docs_missing),
            "total_chars": total_chars,
        },
    )


# ── Step 2: inventory_integrations ────────────────────────────────────


def step_2_inventory_integrations(mission) -> StepResult:
    """Step 2 — inventory all integration credentials by category."""
    start = time.monotonic()
    agent = _make_agent()
    try:
        result = agent._inventory_integrations(
            category="all", status_filter="all"
        )
    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        return StepResult(
            passed=False,
            output=(
                f"inventory_integrations raised "
                f"{type(exc).__name__}: {exc}"
            ),
            duration_ms=duration_ms,
        )

    total = int(result.get("total") or 0)
    configured = int(result.get("configured") or 0)
    missing = int(result.get("missing") or 0)
    integrations = result.get("integrations") or []

    by_category: Dict[str, int] = {}
    missing_names: List[str] = []
    for integ in integrations:
        cat = str(integ.get("category") or "uncategorized")
        by_category[cat] = by_category.get(cat, 0) + 1
        if not integ.get("configured"):
            missing_names.append(str(integ.get("name") or "?"))

    _persist_to_summary(
        mission,
        integrations_audited_count=total,
        integrations_configured_count=configured,
        integrations_missing_count=missing,
        integrations_by_category=by_category,
        integrations_missing_names=missing_names,
    )

    duration_ms = int((time.monotonic() - start) * 1000)
    return StepResult(
        passed=True,
        output=(
            f"Inventoried {total} integrations: {configured} configured, "
            f"{missing} missing across {len(by_category)} categories."
        ),
        duration_ms=duration_ms,
        extra={
            "total": total,
            "configured": configured,
            "missing": missing,
        },
    )


# ── Step 3: check_env_config ──────────────────────────────────────────


def step_3_check_env_config(mission) -> StepResult:
    """Step 3 — audit env-var configuration coverage (values masked)."""
    start = time.monotonic()
    agent = _make_agent()
    try:
        result = agent._check_env_config(category="all")
    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        return StepResult(
            passed=False,
            output=(
                f"check_env_config raised {type(exc).__name__}: {exc}"
            ),
            duration_ms=duration_ms,
        )

    by_category: Dict[str, Dict[str, int]] = {}
    total_checked = 0
    total_configured = 0
    total_missing = 0
    for cat, vars_dict in result.items():
        if not isinstance(vars_dict, dict):
            continue
        configured_count = sum(
            1 for v in vars_dict.values()
            if isinstance(v, dict) and v.get("configured")
        )
        cat_total = len(vars_dict)
        by_category[str(cat)] = {
            "total": cat_total,
            "configured": configured_count,
            "missing": cat_total - configured_count,
        }
        total_checked += cat_total
        total_configured += configured_count
        total_missing += cat_total - configured_count

    _persist_to_summary(
        mission,
        env_vars_checked_count=total_checked,
        env_vars_configured_count=total_configured,
        env_vars_missing_count=total_missing,
        env_vars_by_category=by_category,
    )

    duration_ms = int((time.monotonic() - start) * 1000)
    return StepResult(
        passed=True,
        output=(
            f"Checked {total_checked} env vars: "
            f"{total_configured} configured, {total_missing} missing "
            f"across {len(by_category)} categories."
        ),
        duration_ms=duration_ms,
        extra={
            "checked": total_checked,
            "configured": total_configured,
            "missing": total_missing,
        },
    )


# ── Step 4: count_database_models ─────────────────────────────────────


def step_4_count_database_models(mission) -> StepResult:
    """Step 4 — count rows in the 8 canonical models."""
    start = time.monotonic()
    agent = _make_agent()
    try:
        result = agent._count_database_models(
            models=list(CANONICAL_MODELS)
        )
    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        return StepResult(
            passed=False,
            output=(
                f"count_database_models raised "
                f"{type(exc).__name__}: {exc}"
            ),
            duration_ms=duration_ms,
        )

    counts: Dict[str, Optional[int]] = {}
    errored_models: List[str] = []
    total_rows = 0
    for model_name in CANONICAL_MODELS:
        entry = result.get(model_name) or {}
        if "count" in entry:
            count = int(entry["count"])
            counts[model_name] = count
            total_rows += count
        else:
            counts[model_name] = None
            errored_models.append(model_name)

    _persist_to_summary(
        mission,
        models_counted=counts,
        models_total_rows=total_rows,
        models_errored=errored_models,
    )
    if errored_models:
        _persist_to_summary(mission, degraded_evidence=True)

    duration_ms = int((time.monotonic() - start) * 1000)
    return StepResult(
        passed=True,
        output=(
            f"Counted {len(CANONICAL_MODELS) - len(errored_models)}/"
            f"{len(CANONICAL_MODELS)} models; total rows {total_rows}; "
            f"errored: {errored_models or 'none'}."
        ),
        duration_ms=duration_ms,
        extra={
            "models_ok": len(CANONICAL_MODELS) - len(errored_models),
            "models_errored_count": len(errored_models),
            "total_rows": total_rows,
        },
    )


# ── Step 5: generate_audit_report (deterministic markdown) ────────────


def step_5_generate_audit_report(mission) -> StepResult:
    """Step 5 — build the audit Deliverable from prior step data.

    Reads the data accumulated in mission.summary by steps 1–4 and
    builds a structured markdown report with the 6 contract sections.
    Persists the report as a Deliverable
    (type='analysis', category='Platform Audit'). The Deliverable id +
    char length + findings/issues counts land in mission.summary so
    the verdict + shift-report can reference them.

    Recommendations are derived from the inventory step (missing
    integrations) and the env-config step (missing env vars) — same
    shape as PlatformAuditAgent._generate_audit_report's
    recommendations list, computed directly without re-running the
    earlier tools.
    """
    start = time.monotonic()
    summary = mission.summary or {}

    today_str = timezone.localtime().strftime("%Y-%m-%d")
    when_iso = timezone.localtime().isoformat()

    # Recommendations + findings derivation.
    recommendations: List[Dict[str, str]] = []
    missing_integrations = summary.get("integrations_missing_names") or []
    if missing_integrations:
        recommendations.append({
            "priority": "high",
            "finding": (
                f"Missing credentials for {len(missing_integrations)} "
                f"integration(s): {', '.join(missing_integrations[:6])}"
                + (
                    "..." if len(missing_integrations) > 6 else ""
                )
            ),
            "action": (
                "Configure these environment variables in the deploy "
                "target."
            ),
        })

    env_missing = int(summary.get("env_vars_missing_count") or 0)
    if env_missing > 0:
        recommendations.append({
            "priority": "medium",
            "finding": (
                f"{env_missing} env variable(s) absent across the "
                "audited categories"
            ),
            "action": (
                "Review which env vars are required for production "
                "vs which are optional and document the gaps."
            ),
        })

    models_errored = summary.get("models_errored") or []
    if models_errored:
        recommendations.append({
            "priority": "medium",
            "finding": (
                f"DB model count probe failed for: "
                f"{', '.join(models_errored)}"
            ),
            "action": (
                "Check whether the model mapping in "
                "PlatformAuditAgent still matches the current app "
                "registry."
            ),
        })

    findings_count = (
        int(summary.get("integrations_missing_count") or 0)
        + int(summary.get("env_vars_missing_count") or 0)
        + len(models_errored)
    )
    issues_found_count = sum(
        1 for r in recommendations if r["priority"] == "high"
    )

    # Build the report body.
    body = _build_audit_report_markdown(
        today_str=today_str,
        when_iso=when_iso,
        mission=mission,
        summary=summary,
        recommendations=recommendations,
        findings_count=findings_count,
        issues_found_count=issues_found_count,
    )

    # Persist the Deliverable.
    try:
        deliverable_id = _persist_audit_deliverable(
            mission=mission, today_str=today_str, body=body
        )
    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        return StepResult(
            passed=False,
            output=(
                "Failed to persist audit Deliverable: "
                f"{type(exc).__name__}: {exc}"
            ),
            duration_ms=duration_ms,
        )

    _persist_to_summary(
        mission,
        audit_type=AUDIT_TYPE_DEFAULT,
        findings_count=findings_count,
        issues_found_count=issues_found_count,
        report_deliverable_id=deliverable_id,
        report_chars=len(body),
        recommendations=recommendations,
    )

    duration_ms = int((time.monotonic() - start) * 1000)
    return StepResult(
        passed=True,
        output=(
            f"Audit report Deliverable {deliverable_id} created "
            f"({len(body)} chars); {findings_count} findings, "
            f"{issues_found_count} issues."
        ),
        duration_ms=duration_ms,
        extra={
            "deliverable_id": deliverable_id,
            "report_chars": len(body),
            "findings_count": findings_count,
            "issues_found_count": issues_found_count,
        },
    )


def _persist_audit_deliverable(
    *, mission, today_str: str, body: str
) -> str:
    """Create the audit-report Deliverable + return its id as string."""
    from core.models_deliverables import Deliverable, PublishIntent
    from core.models_skin_layer import ProjectWorkspace

    workspace = ProjectWorkspace.objects.filter(
        name__iexact=EMPLOYEE_OS_DEFAULT_WORKSPACE_NAME
    ).first()
    workspace_id = workspace.id if workspace else None

    deliverable = Deliverable(
        title=f"{AUDIT_REPORT_TITLE_PREFIX} — {today_str}",
        slug=f"platform-audit-{today_str}-{uuid.uuid4().hex[:8]}",
        deliverable_type=AUDIT_REPORT_DELIVERABLE_TYPE,
        publish_intent=PublishIntent.PUBLISH_CANDIDATE,
        category=AUDIT_REPORT_CATEGORY,
        content=body,
        preview_content=body[:500] + ("..." if len(body) > 500 else ""),
        workspace_id=workspace_id,
        # MissionRunner's escalation flow knows about the
        # create-default-completed quirk for its OWN Deliverables
        # (PublishCandidate escalation flow); for the audit-report
        # Deliverable we just create at 'ready' so it's immediately
        # visible.
        status="ready",
    )
    deliverable.save()
    return str(deliverable.id)


def _build_audit_report_markdown(
    *,
    today_str: str,
    when_iso: str,
    mission,
    summary: Dict[str, Any],
    recommendations: List[Dict[str, str]],
    findings_count: int,
    issues_found_count: int,
) -> str:
    """Construct the markdown audit report body (no LLM)."""
    docs_audited = summary.get("docs_audited") or []
    docs_missing = summary.get("docs_missing") or []
    integrations_total = int(summary.get("integrations_audited_count") or 0)
    integrations_configured = int(
        summary.get("integrations_configured_count") or 0
    )
    integrations_missing = int(
        summary.get("integrations_missing_count") or 0
    )
    integrations_by_category = summary.get("integrations_by_category") or {}
    env_total = int(summary.get("env_vars_checked_count") or 0)
    env_configured = int(summary.get("env_vars_configured_count") or 0)
    env_missing = int(summary.get("env_vars_missing_count") or 0)
    env_by_category = summary.get("env_vars_by_category") or {}
    models_counted = summary.get("models_counted") or {}
    models_total_rows = int(summary.get("models_total_rows") or 0)
    models_errored = summary.get("models_errored") or []
    integrations_missing_names = (
        summary.get("integrations_missing_names") or []
    )

    lines: List[str] = []
    lines.append(f"# {AUDIT_REPORT_TITLE_PREFIX} — {today_str}")
    lines.append("")
    lines.append(f"**audit_type:** `{AUDIT_TYPE_DEFAULT}`")
    lines.append(f"**when:** {when_iso}")
    lines.append(f"**mission_id:** `{mission.id}`")
    lines.append(
        f"**findings:** {findings_count}; "
        f"**issues:** {issues_found_count}"
    )
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append(
        f"- Read {len(docs_audited)}/{len(CANONICAL_DOCS)} canonical docs "
        f"({sum(1 for _ in docs_missing)} missing)."
    )
    lines.append(
        f"- Inventoried {integrations_total} integrations: "
        f"{integrations_configured} configured, "
        f"{integrations_missing} missing."
    )
    lines.append(
        f"- Audited {env_total} env variables across "
        f"{len(env_by_category)} categories: "
        f"{env_configured} configured, {env_missing} missing."
    )
    lines.append(
        f"- Counted {len(models_counted)} database models "
        f"({models_total_rows} total rows)."
    )
    lines.append(
        f"- {findings_count} findings, {issues_found_count} high-priority "
        "issues."
    )
    lines.append("")

    # Integration Health
    lines.append("## Integration Health")
    if integrations_by_category:
        for cat, count in sorted(integrations_by_category.items()):
            lines.append(f"- **{cat}**: {count}")
    if integrations_missing_names:
        lines.append("")
        lines.append("**Missing credentials:**")
        for name in integrations_missing_names:
            lines.append(f"- {name}")
    lines.append("")

    # Configuration Status
    lines.append("## Configuration Status")
    if env_by_category:
        for cat, stats in sorted(env_by_category.items()):
            lines.append(
                f"- **{cat}**: {stats.get('configured', 0)}"
                f"/{stats.get('total', 0)} configured "
                f"({stats.get('missing', 0)} missing)"
            )
    lines.append("")

    # Database Health
    lines.append("## Database Health")
    for model_name in CANONICAL_MODELS:
        count = models_counted.get(model_name)
        if count is None:
            lines.append(f"- **{model_name}**: probe error")
        else:
            lines.append(f"- **{model_name}**: {count} rows")
    lines.append("")

    # Documentation Sweep
    lines.append("## Documentation Sweep")
    lines.append(
        f"Read {len(docs_audited)} of {len(CANONICAL_DOCS)} canonical "
        "docs:"
    )
    for doc in docs_audited:
        lines.append(f"- ✓ {doc}")
    for doc in docs_missing:
        lines.append(f"- ✗ {doc} (missing)")
    lines.append("")

    # Top Risks
    lines.append("## Top Risks")
    if recommendations:
        for r in recommendations:
            lines.append(
                f"- **[{r['priority']}]** {r['finding']}"
            )
            lines.append(f"  - **Action:** {r['action']}")
    else:
        lines.append("- No high-priority risks surfaced.")
    lines.append("")

    # Green Checks
    lines.append("## Green Checks")
    if integrations_configured > 0:
        lines.append(
            f"- {integrations_configured} integration(s) configured."
        )
    if env_configured > 0:
        lines.append(
            f"- {env_configured} env variable(s) configured across "
            f"{len(env_by_category)} categories."
        )
    if models_total_rows > 0:
        lines.append(
            f"- Database has {models_total_rows} row(s) across "
            f"{len([m for m in models_counted.values() if m is not None])} "
            "models (probe successful)."
        )
    if not models_errored:
        lines.append("- All database model probes succeeded.")
    lines.append("")

    lines.append("---")
    lines.append(
        "*Generated by Platform Auditor (MissionRunner-driven, "
        "no LLM synthesis in v0).*"
    )

    return "\n".join(lines)


# ── Escalation body formatter (failure path) ──────────────────────────


def build_escalation_body(ctx: FailureContext) -> str:
    """Platform-audit-specific escalation Deliverable body.

    Shape mirrors the docs cascade escalation body but uses
    Platform-Auditor-flavored language and counts. Called by
    MissionRunner only when a step fails.
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
        f"# Platform Audit Escalation — {today_str}",
        "",
        f"**failed_step:** `{ctx.failed_step}`",
        f"**when:** {when_iso}  ",
        f"**run_duration_so_far:** {run_duration_label}",
        f"**error_signature:** `{ctx.error_signature}`",
        f"**ops_run_id:** `{ctx.mission_id}`",
        "",
        "## what_happened",
        (
            f"Step `{ctx.failed_step}` of the Platform Audit cascade "
            "raised or returned a failure shape before the audit "
            "Deliverable could be synthesized."
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

    Used only if a pa_post_fn hook is wired. PR 2.2 leaves
    ``pa_post_fn=None`` because PLATFORM_AUDITOR has no
    ``primary_chat_id`` (the auditor's visibility is via the inbox
    shift-report DM + the audit Deliverable).
    """
    return (
        f"Platform Audit FAILED at {ctx.failed_step} "
        f"(signature {ctx.error_signature}, mission {ctx.mission_id})."
    )


# ── Escalation deliverable spec factory ───────────────────────────────


def _platform_audit_escalation_spec_factory(
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


# ── Shift-report dispatch ─────────────────────────────────────────────


def _format_shift_report_body(mission, summary: Dict[str, Any]) -> str:
    """Platform-audit-specific shift-report DM body.

    Three terminal branches matching docs_manager's shape:
      * certified — "Platform Audit mission <id> passed. <stats>. Report
        deliverable <id>."
      * rejected  — "Platform Audit mission <id> failed at <step>.
        Escalation deliverable <id>."
      * deferred  — "Platform Audit mission <id> deferred."
    """
    verdict = summary.get("verdict")
    wall_ms = summary.get("wall_time_ms")
    seconds = (
        f"{wall_ms / 1000:.1f}"
        if isinstance(wall_ms, (int, float))
        else "?"
    )

    if verdict == "certified":
        integrations = int(summary.get("integrations_audited_count") or 0)
        env_vars = int(summary.get("env_vars_checked_count") or 0)
        models = len(summary.get("models_counted") or {})
        findings = int(summary.get("findings_count") or 0)
        issues = int(summary.get("issues_found_count") or 0)
        report_id = summary.get("report_deliverable_id")
        report_phrase = (
            f"Report deliverable {report_id}."
            if report_id
            else "Report deliverable not recorded."
        )
        return (
            f"Platform Audit mission {mission.id} passed. "
            f"Audited {integrations} integrations / {env_vars} env "
            f"vars / {models} models in {seconds}s. "
            f"Findings {findings}, issues {issues}. {report_phrase}"
        )

    if verdict == "rejected":
        failed_step = summary.get("failed_step") or "<unknown step>"
        escalation_id = summary.get("escalation_deliverable_id")
        esc_phrase = (
            f"Escalation deliverable {escalation_id} created."
            if escalation_id
            else "No escalation deliverable recorded."
        )
        return (
            f"Platform Audit mission {mission.id} failed at "
            f"{failed_step}. {esc_phrase}"
        )

    if verdict == "deferred":
        return (
            f"Platform Audit mission {mission.id} deferred. "
            "Awaiting follow-up review."
        )

    return (
        f"Platform Audit mission {mission.id} reached terminal state "
        f"with verdict={verdict!r}."
    )


# Extra metadata keys carried in the DM (beyond comms.py BASE keys).
_SHIFT_REPORT_EXTRA_KEYS: Tuple[str, ...] = (
    "audit_type",
    "findings_count",
    "issues_found_count",
    "report_deliverable_id",
    "failed_step",
    "escalation_deliverable_id",
)


def post_platform_audit_shift_report(mission) -> Dict[str, Any]:
    """Post a Platform Audit shift-report DM for ``mission``.

    Delegates to the framework ``post_shift_report`` helper with
    platform-audit-specific subject + body formatter + extra
    metadata keys + ``sender_type='system'`` (the auditor has no
    chat identity in v0).
    """
    from core.employees.comms import post_shift_report

    return post_shift_report(
        employee=PLATFORM_AUDITOR,
        job="platform_audit",
        mission=mission,
        body_formatter=_format_shift_report_body,
        extra_metadata_keys=_SHIFT_REPORT_EXTRA_KEYS,
        thread_subject=SHIFT_REPORT_THREAD_SUBJECT,
        sender_type="system",
    )


def _shift_report_hook(mission) -> Dict[str, Any]:
    """MissionRunner ``shift_report_fn`` hook — delegates to the wrapper."""
    return post_platform_audit_shift_report(mission)


# ── Public factory ────────────────────────────────────────────────────


def build_platform_audit_runner() -> MissionRunner:
    """Wire the Platform Audit job into a MissionRunner.

    Called by the Celery task in ``core.tasks_platform_audit``. Pure:
    no per-call mutable state, no closure-capture (PR 1.3 PostflightContext
    pattern made this unnecessary).
    """
    # Confidence + dedupe values are NOT passed — MissionRunnerConfig's
    # field defaults (0.95 / 0.6 / 0.0 / 24h) apply. The escalation
    # workspace travels via ``EscalationDeliverableSpec.workspace_name``
    # on the spec factory above.
    config = MissionRunnerConfig(
        # Identity
        employee_handle=PLATFORM_AUDITOR.handle,
        employee_display_name=PLATFORM_AUDITOR.display_name,
        runs_as_username=PLATFORM_AUDITOR.runs_as_username,
        primary_chat_id=PLATFORM_AUDITOR.primary_chat_id,  # None in v0
        # Job
        mission_run_kind=MISSION_RUN_KIND,
        job_title=PLATFORM_AUDIT_JOB.title,
        # Escalation (employee-specific only — workspace travels via spec)
        escalation_source=ESCALATION_SOURCE,
        escalation_title_prefix=DELIVERABLE_TITLE_PREFIX,
        # No pin_settings_key — the auditor has no pinned PA chat in v0.
        pin_settings_key=None,
    )

    steps = [
        Step(name="step_1_read_docs", fn=step_1_read_docs),
        Step(
            name="step_2_inventory_integrations",
            fn=step_2_inventory_integrations,
        ),
        Step(
            name="step_3_check_env_config", fn=step_3_check_env_config
        ),
        Step(
            name="step_4_count_database_models",
            fn=step_4_count_database_models,
        ),
        Step(
            name="step_5_generate_audit_report",
            fn=step_5_generate_audit_report,
        ),
    ]

    return MissionRunner(
        config=config,
        steps=steps,
        escalation_body_formatter=build_escalation_body,
        escalation_summary_formatter=build_pa_summary_line,
        escalation_deliverable_spec_factory=(
            _platform_audit_escalation_spec_factory
        ),
        shift_report_fn=_shift_report_hook,
        # v0: no PA chat post (PLATFORM_AUDITOR has no primary_chat_id;
        # contract says visibility goes via inbox + audit Deliverable).
        pa_post_fn=None,
        # No preflight / postflight needed — this job has no
        # before/after count probes and no drift observation
        # (cleaner than docs_cascade).
        preflight_fn=None,
        postflight_fn=None,
    )
