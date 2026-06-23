"""Lock-in test for Session 1219 Phase 2 wall-clock-timeout source rename.

The watchdog investigation (deliverable 6b00c112-…) recommended distinguishing
the three timeout-source attributions used in `_record_timeout_signature`:

  - `'agent_wall_clock'`   — per-agent wall-clock fired inside the Celery task
                              wrapper (`core/tasks_agents.py`).
  - `'router_wall_clock'`  — same per-agent wall-clock fired via direct router
                              dispatch (`core/agent_router.py`).
  - `'watchdog_cleanup'`   — cleanup-watchdog beat task swept a stale row
                              (`core/tasks_agents.py:_impl_cleanup_stale_agent_executions`).

If a future refactor reverts the rename, failure_signatures will fold the
Celery-task path back into the legacy `'wall_clock'` bucket — which the
investigation deliverable specifically called out as ambiguous. This test
catches that regression at PR time.
"""

import re
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]


def test_tasks_agents_uses_agent_wall_clock_source():
    """`core/tasks_agents.py` must emit `timeout_source='agent_wall_clock'` from
    its `_FuturesTimeout` handler."""
    src = (REPO / "core/tasks_agents.py").read_text()
    # Must mention the new name at least once
    assert "'agent_wall_clock'" in src or '"agent_wall_clock"' in src, (
        "tasks_agents.py is expected to emit timeout_source='agent_wall_clock' "
        "after Session 1219 Phase 2"
    )
    # Must NOT still emit the legacy bare 'wall_clock' name
    legacy_hits = re.findall(r"timeout_source\s*=\s*['\"]wall_clock['\"]", src)
    assert not legacy_hits, (
        f"tasks_agents.py still emits the legacy bare 'wall_clock' "
        f"timeout_source — Session 1219 Phase 2 should have renamed it to "
        f"'agent_wall_clock' for attribution clarity. Hits: {legacy_hits}"
    )


def test_agent_router_uses_router_wall_clock_source():
    """`core/agent_router.py` must emit `timeout_source='router_wall_clock'`
    from its own `_RouterFuturesTimeout` handler. This name is unchanged
    from prior sessions — Phase 2 only renamed the Celery-task path."""
    src = (REPO / "core/agent_router.py").read_text()
    assert "'router_wall_clock'" in src or '"router_wall_clock"' in src


def test_wall_clock_timeout_paths_perform_early_save():
    """Both wall-clock-timeout handlers must call `execution_record.save()`
    with the failed status before falling through to the downstream
    enrichment block. The investigation deliverable showed that downstream
    URC / JSON / circuit-breaker code can raise and leave the row in
    'in_progress' until the cleanup watchdog catches it."""
    for path in ("core/tasks_agents.py", "core/agent_router.py"):
        src = (REPO / path).read_text()
        assert "early-saved failed status" in src, (
            f"{path} is expected to emit an early-save log marker so the "
            f"wall-clock-timeout path is observable in production logs"
        )
