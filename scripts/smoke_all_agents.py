"""One-shot full-AGENT_MAP capability smoke.

Iterates all 83 entries in `AgentRouter.AGENT_MAP`, dispatches each via
`execute_agent_task.apply_async()` with `context.mode='fleet_smoke'` + a
short receipt-only task, then polls AgentExecution rows until every
dispatch settles or a global wall-clock cap fires. Tabulates per-agent
status / runtime / error_message / deliverable_id.

Session 1231 follow-on to Chris's question "can Rigby trigger each
agent and get an output?" — covers the 47 agents the WorkflowAgent
harness doesn't touch.

Usage::

    .venv/bin/python scripts/smoke_all_agents.py

Skips the `claude_code_coordination` intent path entirely — that's a
PA-only routing target, not an agent class.
"""
from __future__ import annotations

import os
import sys
import time
import uuid

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

from core.agent_router import AgentRouter  # noqa: E402
from core.models import AgentExecution  # noqa: E402
from core.tasks import execute_agent_task  # noqa: E402


User = get_user_model()


CAPABILITY_PING_TASK = (
    "Fleet smoke: return one-sentence receipt of capability. "
    "No deliverables. No code review. No file writes. "
    "Format: 'AgentName ready' followed by one sentence about your scope."
)

PER_AGENT_TIMEOUT_SECONDS = 90
GLOBAL_WALL_CLOCK_SECONDS = 900  # 15 min cap


def main() -> int:
    user = User.objects.get(username="chris")
    router = AgentRouter(user=user)
    agent_names = sorted(router.AGENT_MAP.keys())
    print(f"Dispatching {len(agent_names)} agents from AGENT_MAP...")

    smoke_id = uuid.uuid4().hex[:12]
    dispatched: dict[str, str] = {}  # agent_name -> celery_task_id
    dispatch_errors: dict[str, str] = {}  # agent_name -> error

    context = {
        "mode": "fleet_smoke",
        "smoke_id": smoke_id,
        "user_id": str(user.id),
        "auto_followup": False,
    }

    t0 = time.time()
    for name in agent_names:
        try:
            res = execute_agent_task.apply_async(
                args=[name, CAPABILITY_PING_TASK, context],
                queue="long_running",
            )
            dispatched[name] = res.id
        except Exception as e:
            dispatch_errors[name] = f"{type(e).__name__}: {e}"

    dispatch_time = time.time() - t0
    print(f"  dispatched={len(dispatched)} errors={len(dispatch_errors)} "
          f"({dispatch_time:.1f}s)")

    if dispatch_errors:
        print()
        print("=== DISPATCH ERRORS ===")
        for n, err in dispatch_errors.items():
            print(f"  {n}: {err}")

    # Poll AgentExecution rows for each dispatch
    pending = set(dispatched.keys())
    results: dict[str, dict] = {}
    poll_start = time.time()
    last_print = 0.0
    while pending and (time.time() - poll_start) < GLOBAL_WALL_CLOCK_SECONDS:
        # Find newly completed
        for name in list(pending):
            celery_id = dispatched[name]
            ex = AgentExecution.objects.filter(
                agent__name=name,
                input_data__celery_task_id=celery_id,
            ).first()
            # Fall back to recent runs of this agent within smoke window
            if ex is None:
                ex = AgentExecution.objects.filter(
                    agent__name=name,
                    created_at__gte=django_now() - django_td(seconds=int(time.time() - t0) + 60),
                ).order_by("-created_at").first()
            if ex and ex.status in ("completed", "failed", "cancelled", "skipped"):
                results[name] = {
                    "exec_id": str(ex.id),
                    "status": ex.status,
                    "runtime_ms": ex.execution_time_ms,
                    "error_message": (ex.error_message or "")[:200],
                    "has_deliverable": _exec_produced_deliverable(ex),
                }
                pending.discard(name)
        # Update progress occasionally
        elapsed = time.time() - poll_start
        if elapsed - last_print > 15:
            print(f"  [{elapsed:6.1f}s] pending={len(pending)} settled={len(results)}")
            last_print = elapsed
        if pending:
            time.sleep(2)

    # Mark anything still pending as timed-out from harness POV
    for name in pending:
        results[name] = {
            "exec_id": "<harness-timeout>",
            "status": "harness_timeout",
            "runtime_ms": int((time.time() - poll_start) * 1000),
            "error_message": "harness wall-clock cap hit before AgentExecution settled",
            "has_deliverable": False,
        }

    total_time = time.time() - t0
    print()
    print(f"=== RESULTS ({total_time:.1f}s total) ===")
    print()

    # Bucket
    by_bucket: dict[str, list[str]] = {}
    for name, r in sorted(results.items()):
        bucket = r["status"]
        by_bucket.setdefault(bucket, []).append(name)

    for bucket in sorted(by_bucket.keys()):
        names = by_bucket[bucket]
        print(f"=== {bucket.upper()} ({len(names)}) ===")
        for n in names:
            r = results[n]
            err = r["error_message"]
            deliv = "📄" if r["has_deliverable"] else "  "
            print(f"  {deliv} {n:40s} runtime={str(r['runtime_ms'])+'ms':>10s}  "
                  f"{(err[:80]) if err else ''}")
        print()

    # Summary line
    pass_count = len(by_bucket.get("completed", []))
    fail_count = len(by_bucket.get("failed", []))
    other = sum(len(v) for k, v in by_bucket.items()
                if k not in ("completed", "failed"))
    print(f"Summary: {pass_count} pass / {fail_count} fail / {other} other "
          f"({pass_count/len(agent_names)*100:.1f}% pass)")
    print(f"smoke_id={smoke_id}")
    return 0


def _exec_produced_deliverable(ex) -> bool:
    """Inspect AgentExecution to see if it created/linked a deliverable."""
    od = ex.output_data or {}
    if od.get("deliverable_id"):
        return True
    if (od.get("data") or {}).get("deliverable_id"):
        return True
    # Also check via reverse: any Deliverable created in the exec window
    # by this agent. Cheap heuristic — drops false negatives where the
    # agent persists out-of-band.
    from core.models_deliverables import Deliverable
    if ex.completed_at and ex.created_at:
        return Deliverable.objects.filter(
            agent_name=ex.agent.name if ex.agent else "",
            created_at__gte=ex.created_at,
            created_at__lte=ex.completed_at,
        ).exists()
    return False


def django_now():
    from django.utils import timezone
    return timezone.now()


def django_td(**kwargs):
    from datetime import timedelta
    return timedelta(**kwargs)


if __name__ == "__main__":
    sys.exit(main())
