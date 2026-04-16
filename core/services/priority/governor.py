"""
Beat Task Governor — pre-dispatch gate for autonomous agent work.

This module is the core of Layer 2 in the Agent Governance plan. It sits
between beat-task cron triggers and agent execution, deciding whether a
given agent dispatch should proceed based on:

1. **Mission alignment** — does this agent match an active priority?
   Uses the existing PriorityRouter.check() logic.
2. **Circuit breaker** — has this agent been failing too much recently?
   Tracks rolling failure rate and auto-disables on threshold breach.

## Integration points

Called from ``_impl_universal_agent_workspace_output`` in
``core/tasks_agents.py`` — the single chokepoint for all beat-task
agent dispatches. User-triggered dispatches (trigger_source='user_chat'
or 'user') bypass the governor entirely.

## Fail-open contract

Same as the rest of the priority package: any exception in the governor
returns PROCEED. We'd rather run an unaligned agent than block production
traffic on a governor bug.
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


# ── Configuration ─────────────────────────────────────────────────────

# Master gate for the governor. Independent of PRIORITY_ROUTER_ENABLED
# (which controls the semaphore/throttle layer). This gate controls
# whether beat tasks are SKIPPED entirely when misaligned.
GOVERNOR_ENABLED_ENV = "BEAT_GOVERNOR_ENABLED"

# Circuit breaker settings
CB_WINDOW_SIZE = int(os.environ.get("CB_WINDOW_SIZE", "20"))  # last N executions
CB_FAILURE_THRESHOLD = float(os.environ.get("CB_FAILURE_THRESHOLD", "0.40"))  # 40%
CB_COOLDOWN_SECONDS = int(os.environ.get("CB_COOLDOWN_SECONDS", "3600"))  # 1 hour


def _governor_enabled() -> bool:
    raw = os.environ.get(GOVERNOR_ENABLED_ENV, "").strip().lower()
    return raw in ("true", "1", "yes", "on")


# ── GovernorDecision ──────────────────────────────────────────────────

@dataclass
class GovernorDecision:
    """The outcome of a governor check."""
    proceed: bool
    reason: str  # 'aligned', 'misaligned_skip', 'circuit_breaker', 'governor_off', 'user_triggered', 'fail_open'
    agent_name: str
    detail: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "proceed": self.proceed,
            "reason": self.reason,
            "agent_name": self.agent_name,
            "detail": self.detail,
        }


# ── Rate-limited logging ─────────────────────────────────────────────

_last_fail_log_ts: float = 0.0


def _log_governor_failure() -> None:
    global _last_fail_log_ts
    try:
        now = time.monotonic()
        if now - _last_fail_log_ts > 60.0:
            _last_fail_log_ts = now
            logger.exception(
                "[governor] fail-open: exception suppressed, dispatch proceeding"
            )
    except Exception:
        pass


# ── Circuit Breaker ───────────────────────────────────────────────────

def check_circuit_breaker(agent_name: str) -> Optional[str]:
    """
    Check if an agent's circuit breaker has tripped.

    Returns None if the agent is OK to proceed, or a reason string if
    the circuit breaker is open (agent should be skipped).

    Uses Django cache (Redis) to track breaker state so it survives
    worker restarts. The actual failure rate is computed from the DB
    only when the cache entry is missing or expired.
    """
    try:
        from django.core.cache import cache

        # Check if this agent is in cooldown
        cooldown_key = f"cb:cooldown:{agent_name}"
        cooldown_until = cache.get(cooldown_key)
        if cooldown_until:
            return f"circuit breaker open until cooldown expires (tripped due to high failure rate)"

        # Check rolling failure rate from recent executions
        rate_key = f"cb:rate:{agent_name}"
        cached_rate = cache.get(rate_key)

        if cached_rate is None:
            # Cache miss — compute from DB
            cached_rate = _compute_failure_rate(agent_name)
            # Cache for 5 minutes to avoid DB hammering
            cache.set(rate_key, cached_rate, timeout=300)

        if cached_rate is not None and cached_rate >= CB_FAILURE_THRESHOLD:
            # Trip the breaker
            _trip_circuit_breaker(agent_name, cached_rate)
            return (
                f"circuit breaker tripped: {cached_rate:.0%} failure rate "
                f"over last {CB_WINDOW_SIZE} executions (threshold: {CB_FAILURE_THRESHOLD:.0%})"
            )

        return None  # agent is OK

    except Exception:
        return None  # fail-open


def _compute_failure_rate(agent_name: str) -> Optional[float]:
    """Compute rolling failure rate from last N executions."""
    try:
        from core.models_unified_system import AgentExecution

        recent = (
            AgentExecution.objects
            .filter(agent__name=agent_name)
            .order_by('-created_at')
            .values_list('status', flat=True)[:CB_WINDOW_SIZE]
        )
        statuses = list(recent)
        if len(statuses) < 5:
            return None  # not enough data to judge

        failed = sum(1 for s in statuses if s == 'failed')
        return failed / len(statuses)

    except Exception:
        return None


def _trip_circuit_breaker(agent_name: str, failure_rate: float) -> None:
    """Trip the breaker: set cooldown and create a HumanAttentionItem."""
    try:
        from django.core.cache import cache

        cooldown_key = f"cb:cooldown:{agent_name}"
        cache.set(cooldown_key, True, timeout=CB_COOLDOWN_SECONDS)

        # Invalidate the rate cache so next check after cooldown recomputes
        cache.delete(f"cb:rate:{agent_name}")

        logger.warning(
            "[governor] Circuit breaker TRIPPED for %s: %.0f%% failure rate "
            "over last %d executions. Cooldown: %ds.",
            agent_name, failure_rate * 100, CB_WINDOW_SIZE, CB_COOLDOWN_SECONDS,
        )

        # Create HumanAttentionItem so Rigby/Chris know
        _create_attention_item(agent_name, failure_rate)

    except Exception:
        logger.exception("[governor] Failed to trip circuit breaker for %s", agent_name)


def _create_attention_item(agent_name: str, failure_rate: float) -> None:
    """Create a HumanAttentionItem for a tripped circuit breaker."""
    try:
        from core.models_unified_system import HumanAttentionItem
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.filter(is_superuser=True).first()
        if not user:
            return

        HumanAttentionItem.objects.create(
            user=user,
            title=f"Circuit breaker tripped: {agent_name}",
            description=(
                f"{agent_name} has been auto-disabled for {CB_COOLDOWN_SECONDS // 60} minutes "
                f"due to {failure_rate:.0%} failure rate over the last {CB_WINDOW_SIZE} executions. "
                f"The agent will auto-re-enable after cooldown. Check logs for failure details."
            ),
            priority='high',
            category='system',
            source='governor',
        )
    except Exception:
        pass  # attention item creation must never break the governor


# ── Main Governor Check ───────────────────────────────────────────────

def should_dispatch(
    agent_name: str,
    trigger_source: Optional[str] = None,
    task: Optional[str] = None,
) -> GovernorDecision:
    """
    The single entry point for the Beat Task Governor. Call this before
    dispatching any autonomous agent work.

    Returns a GovernorDecision. If proceed=False, the caller should skip
    the dispatch and log the reason.

    User-triggered work (trigger_source='user_chat' or 'user') always
    proceeds — the governor only gates autonomous beat-task work.
    """
    try:
        # User-triggered work is never gated
        user_triggers = {'user_chat', 'user', 'pa_tool', 'direct'}
        if trigger_source in user_triggers:
            return GovernorDecision(
                proceed=True,
                reason='user_triggered',
                agent_name=agent_name,
            )

        # Check master gate
        if not _governor_enabled():
            return GovernorDecision(
                proceed=True,
                reason='governor_off',
                agent_name=agent_name,
            )

        # Layer 3: Circuit breaker check (independent of mission alignment)
        cb_reason = check_circuit_breaker(agent_name)
        if cb_reason:
            logger.info(
                "[governor] SKIP %s: %s",
                agent_name, cb_reason,
            )
            return GovernorDecision(
                proceed=False,
                reason='circuit_breaker',
                agent_name=agent_name,
                detail=cb_reason,
            )

        # Layer 2: Mission alignment check via PriorityRouter
        from core.services.priority.priority_router import PriorityRouter
        router = PriorityRouter()
        decision = router.check(
            agent_name=agent_name,
            task=task,
            trigger_source=trigger_source,
        )

        if decision.matched:
            logger.debug(
                "[governor] PROCEED %s: aligned (via=%s, priority=%s)",
                agent_name, decision.matched_via, decision.priority_name,
            )
            return GovernorDecision(
                proceed=True,
                reason='aligned',
                agent_name=agent_name,
                detail=f"matched via {decision.matched_via}: {decision.priority_name}",
            )
        else:
            logger.info(
                "[governor] SKIP %s: misaligned with active priorities",
                agent_name,
            )
            return GovernorDecision(
                proceed=False,
                reason='misaligned_skip',
                agent_name=agent_name,
                detail="no active priority matched this agent",
            )

    except Exception:
        _log_governor_failure()
        return GovernorDecision(
            proceed=True,
            reason='fail_open',
            agent_name=agent_name,
            detail='governor exception suppressed',
        )


def reset_circuit_breaker(agent_name: str) -> bool:
    """Manually reset a tripped circuit breaker. Used by PA tool."""
    try:
        from django.core.cache import cache
        cache.delete(f"cb:cooldown:{agent_name}")
        cache.delete(f"cb:rate:{agent_name}")
        logger.info("[governor] Circuit breaker manually reset for %s", agent_name)
        return True
    except Exception:
        return False


def get_governor_status() -> dict:
    """Return current governor state for PA tools and dashboards."""
    try:
        from django.core.cache import cache
        from core.models_unified_system import ActivePriority

        priorities = ActivePriority.get_active_priorities()

        # Check which agents are in circuit breaker cooldown
        # We can't enumerate all cache keys, so check the known agents
        tripped_agents = []
        try:
            from core.agent_router import AGENT_MAP
            for agent_name in AGENT_MAP:
                if cache.get(f"cb:cooldown:{agent_name}"):
                    tripped_agents.append(agent_name)
        except Exception:
            pass

        return {
            "governor_enabled": _governor_enabled(),
            "active_priorities": len(priorities),
            "priority_names": [p["name"] for p in priorities],
            "circuit_breakers_tripped": tripped_agents,
            "config": {
                "cb_window_size": CB_WINDOW_SIZE,
                "cb_failure_threshold": CB_FAILURE_THRESHOLD,
                "cb_cooldown_seconds": CB_COOLDOWN_SECONDS,
            },
        }
    except Exception:
        return {"governor_enabled": _governor_enabled(), "error": "status unavailable"}
