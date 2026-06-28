"""
Rigby Shift Brief — operator handoff at the start of a session (PR 12A).

The Shift Brief is Rigby's verbal handoff to Chris when he sits down at the
platform. Not a dashboard, not a digest — a one-minute "here's what matters
today" pulse that bundles 7 read-only tool calls into a single structured
response.

Distinct from the existing ``morning_brief`` workflow (multi-LLM, 5-7 min
read, persisted deliverable). This is operational status, not content.

Six fixed sections (preferred render order):

    1. Today's top priority      (1 line, derived from #4 + #5 + #6)
    2. Platform health           (traffic light + supporting bullets)
    3. Active risks              (queues / alerts / session / flag drift)
    4. What changed              (since cutoff — execs, deliverables, audits)
    5. What NOT to work on       (deferred / dormant / gated work)
    6. Suggested next action     (single concrete step)

Header carries traffic-light state (GREEN / YELLOW / RED). Footer carries
runtime + count of degraded sub-tools.

Side-effect free. No model writes. No LLM. Graceful degradation on every
sub-tool — a single sub-tool failure adds to ``degraded_fields`` and the
brief still renders.

Usage:
    from core.services.rigby_shift_brief import build_shift_brief
    result = build_shift_brief(user_id=42, conversation_id='pa-...')
    print(result['summary_text'])
"""
from __future__ import annotations

import concurrent.futures
import logging
import time
from typing import Any, Callable, Optional

from django.conf import settings
from django.utils import timezone


logger = logging.getLogger(__name__)


# Per-sub-tool wall-clock timeout. Two seconds is enough headroom for any
# healthy ORM/Redis read but short enough that, even if ALL sub-tools time
# out (celery broker down, DB slow), the brief still returns in <20s with
# clear "degraded" signals. The acceptance criterion <5s is met when at
# least the cheap sub-tools (ops_digest, recent_activity, flag_state)
# respond promptly.
SUB_TOOL_TIMEOUT_SECONDS = 2.0


# ── Traffic-light thresholds ────────────────────────────────────────────────
# YELLOW = any single degraded sub-tool OR any new finding (P0/P1) OR
#          session_health.recommendation == 'suggest_fresh' OR
#          any queue YELLOW OR any worker offline.
# RED    = >=2 degraded sub-tools OR any P0 finding unresolved OR
#          session_health.recommendation == 'strongly_recommend_fresh' OR
#          any queue RED/CRITICAL OR worker_health returned no workers.
# GREEN  = none of the above.
RECOMMENDATION_RED = "strongly_recommend_fresh"
RECOMMENDATION_YELLOW = "suggest_fresh"

# The four Session 1250 dormant flags. Their default is OFF; any True value
# is unusual enough to be worth surfacing in "What NOT to work on."
S1250_FLAGS = (
    "RIGBY_EVENT_INTAKE_ENABLED",
    "RIGBY_INTERNAL_WORK_QUEUE_ENABLED",
    "RIGBY_WORK_QUEUE_REVIEW_ENABLED",
    "RIGBY_DELEGATION_ENABLED",
)

# Output cap (acceptance criterion #2: under 1200 chars). We aim for ~1000.
MAX_BRIEF_CHARS = 1200


def build_shift_brief(
    user_id: Optional[int],
    *,
    conversation_id: Optional[str] = None,
    window: str = "24h",
) -> dict[str, Any]:
    """Build the Shift Brief.

    Args:
        user_id: PA user id (passed through to sub-tools that need it).
        conversation_id: Pinned conversation to health-check. If None, the
            session sub-section reports "no conversation supplied".
        window: Lookback window passed to ops_digest. One of
            ``10m / 1h / 6h / 24h``.

    Returns dict with keys:
        ok:              bool — True if the brief built (even if degraded).
        summary_text:    str  — formatted 6-section brief, <1200 chars.
        traffic_light:   str  — GREEN | YELLOW | RED.
        sections:        dict — per-section structured payload.
        metadata:        dict — runtime_ms, degraded_fields, tools_called.
    """
    started = time.monotonic()
    now = timezone.now()
    degraded_fields: list[str] = []
    tools_called: list[str] = []

    # Lazy import — avoid module-load cycle through ToolDispatcher.
    from core.services.tool_dispatcher import ToolDispatcher
    dispatcher = ToolDispatcher()

    # Sub-tool roster. Each entry: (label, callable). All are dispatched in
    # parallel so the wall-clock budget is max(sub_tool_times), not sum.
    # A single-worker executor would have serialized cancelled-but-still-
    # running threads (Python threads can't cooperatively cancel blocking
    # IO like celery.inspect()), so a slow sub-tool would block every
    # later one — exactly the symptom this design avoids.
    cutoff_hours = {"10m": 1, "1h": 1, "6h": 6, "24h": 24}.get(window, 24)
    sub_tools: list[tuple[str, Callable[[], Any]]] = [
        ("ops_digest", lambda: dispatcher._handle_ops_digest(  # type: ignore[attr-defined]
            tool_name="ops_digest_tool",
            payload={"action": "generate", "window": window},
            user_id=user_id,
            trace_id="shift-brief",
        )),
        ("worker_health", lambda: dispatcher._handle_cockpit(  # type: ignore[attr-defined]
            tool_name="cockpit_tool",
            payload={"action": "worker_health"},
            user_id=user_id,
            trace_id="shift-brief",
        )),
        ("queue_lengths", lambda: dispatcher._handle_cockpit(  # type: ignore[attr-defined]
            tool_name="cockpit_tool",
            payload={"action": "queue_lengths"},
            user_id=user_id,
            trace_id="shift-brief",
        )),
        ("audit_findings", lambda: dispatcher._handle_audit(  # type: ignore[attr-defined]
            tool_name="audit_tool",
            payload={"action": "findings", "limit": 10},
            user_id=user_id,
            trace_id="shift-brief",
        )),
        ("recent_activity", lambda: dispatcher._handle_recent_activity(  # type: ignore[attr-defined]
            tool_name="recent_activity_tool",
            payload={"action": "summary", "hours": cutoff_hours},
            user_id=user_id,
            trace_id="shift-brief",
        )),
        ("flag_state", lambda: {
            name: bool(getattr(settings, name, False)) for name in S1250_FLAGS
        }),
    ]
    if conversation_id:
        sub_tools.append((
            "session_health",
            lambda: dispatcher._handle_session(  # type: ignore[attr-defined]
                tool_name="session_tool",
                payload={"action": "health_check", "conversation_id": conversation_id},
                user_id=user_id,
                trace_id="shift-brief",
            ),
        ))

    # Fan out — one worker per sub-tool so timeouts don't queue behind
    # each other.
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=len(sub_tools))
    futures: dict[str, concurrent.futures.Future[Any]] = {}
    for label, fn in sub_tools:
        tools_called.append(label)
        futures[label] = executor.submit(fn)

    results: dict[str, Any] = {}
    for label, future in futures.items():
        try:
            results[label] = future.result(timeout=SUB_TOOL_TIMEOUT_SECONDS)
        except concurrent.futures.TimeoutError:
            degraded_fields.append(label)
            logger.warning(
                "rigby_shift_brief: sub-tool %r exceeded %.1fs timeout",
                label, SUB_TOOL_TIMEOUT_SECONDS,
            )
            future.cancel()
            results[label] = None
        except Exception as exc:
            degraded_fields.append(label)
            logger.warning(
                "rigby_shift_brief: sub-tool %r degraded (%s: %s)",
                label, type(exc).__name__, exc,
            )
            results[label] = None

    ops_digest = results.get("ops_digest")
    worker_health = results.get("worker_health")
    queue_lengths = results.get("queue_lengths")
    audit_findings = results.get("audit_findings")
    recent_activity = results.get("recent_activity")
    flag_state = results.get("flag_state")
    session_health = results.get("session_health")  # None if no conversation_id

    # ── Derive traffic light ────────────────────────────────────────────────
    traffic_light = _derive_traffic_light(
        degraded_count=len(degraded_fields),
        ops_digest=ops_digest,
        worker_health=worker_health,
        queue_lengths=queue_lengths,
        session_health=session_health,
        audit_findings=audit_findings,
    )

    # ── Assemble structured sections ────────────────────────────────────────
    sections = _assemble_sections(
        now=now,
        window=window,
        traffic_light=traffic_light,
        ops_digest=ops_digest,
        worker_health=worker_health,
        queue_lengths=queue_lengths,
        session_health=session_health,
        audit_findings=audit_findings,
        recent_activity=recent_activity,
        flag_state=flag_state,
        degraded_fields=degraded_fields,
    )

    # Release executor threads — cancelled futures may still be running.
    executor.shutdown(wait=False, cancel_futures=True)

    runtime_ms = int((time.monotonic() - started) * 1000)

    summary_text = _render_brief(
        now=now,
        traffic_light=traffic_light,
        sections=sections,
        runtime_ms=runtime_ms,
        degraded_fields=degraded_fields,
        tools_called=tools_called,
    )

    # If we somehow exceeded the cap (defensive — shouldn't happen with the
    # bullet caps below), hard-trim and note in metadata.
    truncated = False
    if len(summary_text) > MAX_BRIEF_CHARS:
        summary_text = summary_text[: MAX_BRIEF_CHARS - 3] + "..."
        truncated = True

    return {
        "ok": True,
        "summary_text": summary_text,
        "traffic_light": traffic_light,
        "sections": sections,
        "metadata": {
            "runtime_ms": runtime_ms,
            "degraded_fields": degraded_fields,
            "tools_called": tools_called,
            "truncated": truncated,
            "char_count": len(summary_text),
            "generated_at": now.isoformat(),
            "window": window,
            "conversation_id": conversation_id,
        },
    }


# ── Section assembly ────────────────────────────────────────────────────────


def _assemble_sections(
    *,
    now,
    window: str,
    traffic_light: str,
    ops_digest: Optional[dict],
    worker_health: Optional[dict],
    queue_lengths: Optional[dict],
    session_health: Optional[dict],
    audit_findings: Optional[dict],
    recent_activity: Optional[dict],
    flag_state: Optional[dict],
    degraded_fields: list[str],
) -> dict[str, Any]:
    """Build the structured payload for each of the 6 sections."""

    # Section 2 — Platform health bullets
    health_bullets: list[str] = []
    if ops_digest and isinstance(ops_digest, dict):
        digest = ops_digest.get("digest") or {}
        activity = digest.get("activity", {}) or {}
        autopilot = digest.get("autopilot", {}) or {}
        blocked = digest.get("blocked_agents", []) or []
        top_failures = digest.get("top_failures", []) or []
        runs = activity.get("agent_runs", 0)
        tasks = activity.get("celery_tasks", 0)
        failures = activity.get("task_failures", 0)
        health_bullets.append(
            f"{runs} agent runs · {tasks} celery tasks · {failures} failures ({window})."
        )
        if blocked:
            health_bullets.append(
                f"Blocked agents: {', '.join(blocked[:3])}"
                + (f" (+{len(blocked) - 3} more)" if len(blocked) > 3 else "")
            )
        if top_failures:
            top = top_failures[0]
            cat = top.get("category", "?")
            hits = top.get("hit_count", 0)
            health_bullets.append(f"Top failure: {cat} ({hits} hits).")
        if autopilot.get("blocks_24h", 0):
            health_bullets.append(f"Autopilot blocks 24h: {autopilot['blocks_24h']}.")

    # Section 3 — Active risks
    risk_bullets: list[str] = []
    # Session health
    if session_health and isinstance(session_health, dict):
        score = session_health.get("score")
        rec = session_health.get("recommendation", "continue")
        if rec == RECOMMENDATION_RED:
            risk_bullets.append(f"Session: rotate immediately (score {score}, {rec}).")
        elif rec == RECOMMENDATION_YELLOW:
            risk_bullets.append(f"Session: rotation suggested (score {score}).")
    # Queue pressure
    if queue_lengths and isinstance(queue_lengths, dict):
        overall = queue_lengths.get("overall_state") or queue_lengths.get("state")
        # cockpit_tool.queue_lengths nests per-queue states under 'queues'
        queues_block = queue_lengths.get("queues") or {}
        hot = [
            q for q, info in queues_block.items()
            if isinstance(info, dict) and info.get("state") in ("RED", "CRITICAL", "YELLOW")
        ]
        if hot:
            risk_bullets.append(f"Queue pressure: {', '.join(sorted(hot)[:3])}.")
        elif overall in ("RED", "CRITICAL", "YELLOW"):
            risk_bullets.append(f"Queue overall state: {overall}.")
    # Worker count
    if worker_health and isinstance(worker_health, dict):
        workers = worker_health.get("workers") or []
        if not workers:
            risk_bullets.append("Worker fleet: 0 workers responding.")
    # Flag drift — surface only if any S1250 flag is ON (default expected OFF).
    if flag_state and isinstance(flag_state, dict):
        on_flags = [name for name, val in flag_state.items() if val]
        if on_flags:
            risk_bullets.append(
                f"S1250 flags ON ({len(on_flags)}/4): {', '.join(on_flags[:2])}"
                + ("…" if len(on_flags) > 2 else "")
            )
    if not risk_bullets:
        risk_bullets.append("None — all clear.")

    # Section 4 — What changed
    change_bullets: list[str] = []
    if recent_activity and isinstance(recent_activity, dict):
        secs = recent_activity.get("sections") or {}
        celery = secs.get("celery_tasks", {}) or {}
        if isinstance(celery, dict) and "total" in celery:
            change_bullets.append(f"{celery.get('total', 0)} celery tasks fired.")
        spider = secs.get("spider_data", {}) or {}
        if isinstance(spider, dict) and spider.get("total_items"):
            change_bullets.append(
                f"{spider['total_items']} spider items "
                f"({spider.get('distinct_spiders', 0)} spiders)."
            )
    if audit_findings and isinstance(audit_findings, dict):
        found_count = audit_findings.get("count", 0)
        if found_count:
            change_bullets.append(f"{found_count} audit findings in surface.")
    if not change_bullets:
        change_bullets.append("Quiet window — no notable activity.")

    # Section 5 — What NOT to work on
    skip_bullets: list[str] = []
    if flag_state and not any((flag_state or {}).values()):
        skip_bullets.append("Don't flip S1250 flags — dormant by design.")
    skip_bullets.append("Don't re-open closed audit findings without new evidence.")

    # Section 1 — Top priority (derived from risks / findings / activity)
    top_priority = _derive_top_priority(
        traffic_light=traffic_light,
        risk_bullets=risk_bullets,
        audit_findings=audit_findings,
        session_health=session_health,
    )

    # Section 6 — Suggested next action (one concrete step)
    next_action = _derive_next_action(
        traffic_light=traffic_light,
        risk_bullets=risk_bullets,
        audit_findings=audit_findings,
        session_health=session_health,
        degraded_fields=degraded_fields,
    )

    return {
        "top_priority": top_priority,
        "platform_health": health_bullets[:3],
        "active_risks": risk_bullets[:3],
        "what_changed": change_bullets[:3],
        "what_not_to_work_on": skip_bullets[:2],
        "next_action": next_action,
    }


# ── Derivation rules ────────────────────────────────────────────────────────


def _derive_traffic_light(
    *,
    degraded_count: int,
    ops_digest: Optional[dict],
    worker_health: Optional[dict],
    queue_lengths: Optional[dict],
    session_health: Optional[dict],
    audit_findings: Optional[dict],
) -> str:
    red = False
    yellow = False

    if degraded_count >= 2:
        red = True
    elif degraded_count >= 1:
        yellow = True

    if session_health and isinstance(session_health, dict):
        rec = session_health.get("recommendation")
        if rec == RECOMMENDATION_RED:
            red = True
        elif rec == RECOMMENDATION_YELLOW:
            yellow = True

    if queue_lengths and isinstance(queue_lengths, dict):
        for info in (queue_lengths.get("queues") or {}).values():
            if not isinstance(info, dict):
                continue
            state = info.get("state")
            if state in ("RED", "CRITICAL"):
                red = True
            elif state == "YELLOW":
                yellow = True

    if worker_health and isinstance(worker_health, dict):
        if not (worker_health.get("workers") or []):
            red = True

    if audit_findings and isinstance(audit_findings, dict):
        for f in audit_findings.get("findings", []) or []:
            if f.get("priority") == "P0" and f.get("status") != "resolved":
                red = True
                break
            if f.get("priority") == "P1" and f.get("status") != "resolved":
                yellow = True

    if red:
        return "RED"
    if yellow:
        return "YELLOW"
    return "GREEN"


def _derive_top_priority(
    *,
    traffic_light: str,
    risk_bullets: list[str],
    audit_findings: Optional[dict],
    session_health: Optional[dict],
) -> str:
    if traffic_light == "RED":
        return "Stabilize platform before opening new work."
    if session_health and session_health.get("recommendation") == RECOMMENDATION_YELLOW:
        return "Rotate the session pin, then continue."
    if audit_findings and isinstance(audit_findings, dict):
        for f in audit_findings.get("findings", []) or []:
            if (
                f.get("priority") in ("P0", "P1")
                and f.get("status") not in ("resolved", "wont_fix")
            ):
                title = (f.get("title") or "open finding")[:60]
                return f"Triage open {f.get('priority')} finding: {title}."
    return "Focus on the active session priority."


def _derive_next_action(
    *,
    traffic_light: str,
    risk_bullets: list[str],
    audit_findings: Optional[dict],
    session_health: Optional[dict],
    degraded_fields: list[str],
) -> str:
    if degraded_fields:
        return (
            f"Investigate degraded sub-tools: {', '.join(degraded_fields[:2])}"
            + ("…" if len(degraded_fields) > 2 else "")
            + "."
        )
    if traffic_light == "RED":
        return "Check ops_digest + worker_health output above and unblock the red item."
    if session_health and session_health.get("recommendation") == RECOMMENDATION_YELLOW:
        return "Run session_tool.create_fresh, then resume."
    return "Open today's planned PR and proceed."


# ── Format rendering ────────────────────────────────────────────────────────


def _render_brief(
    *,
    now,
    traffic_light: str,
    sections: dict,
    runtime_ms: int,
    degraded_fields: list[str],
    tools_called: list[str],
) -> str:
    icon = {"GREEN": "GREEN", "YELLOW": "YELLOW", "RED": "RED"}[traffic_light]
    header = f"Rigby Shift Brief — {now.strftime('%a %Y-%m-%d %H:%MZ')} — {icon}"

    def _block(title: str, bullets: list[str]) -> str:
        body = "\n".join(f"  - {b}" for b in bullets if b)
        return f"\n[ {title} ]\n{body}" if body else f"\n[ {title} ]\n  - (none)"

    parts = [header]
    parts.append(f"\n[ Top priority ]\n  {sections['top_priority']}")
    parts.append(_block("Platform health", sections["platform_health"]))
    parts.append(_block("Active risks", sections["active_risks"]))
    parts.append(_block("What changed", sections["what_changed"]))
    parts.append(_block("What NOT to work on", sections["what_not_to_work_on"]))
    parts.append(f"\n[ Suggested next action ]\n  {sections['next_action']}")

    footer = (
        f"\n-- built in {runtime_ms}ms · {len(tools_called)} tools · "
        f"{len(degraded_fields)} degraded"
    )
    parts.append(footer)

    return "".join(parts)
