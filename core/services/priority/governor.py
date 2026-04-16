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

# ── Demo Autonomy Mode (Session 1090) ────────────────────────────────
# When DEMO_MODE=true, ONLY allowlisted agents may execute — regardless
# of trigger source.  This prevents random autonomous runs, cost spikes,
# or irrelevant outputs during a live demo recording.
#
# The allowlist is intentionally short: read-only audits, content
# pipeline (write → edit), a few visual wow-factor agents, and the
# executive briefing agents.  Anything that can hang, spend heavily,
# or publish/send outbound is excluded.
DEMO_AUTONOMY_ALLOWLIST: frozenset = frozenset({
    # ── Read-only / low-cost ──
    'PlatformAuditAgent',
    'SystemIntelligenceAgent',
    'ResearchAgent',
    'TrendAnalysisAgent',
    'CompetitorAnalysisAgent',
    'OpportunityScoringAgent',
    # ── Content pipeline ──
    'ContentWriterAgent',
    'EditorAgent',
    'ContentStrategyAgent',
    'SEOOptimizerAgent',
    # ── Visual wow-factor ──
    'ImageAgent',
    # ── Executive briefing (grounded via PCS) ──
    'CTOAgent',
    'COOAgent',
    # ── Demo narrative agents ──
    'ContentAuditAgent',
    'PromptEngineeringAgent',
})

# Hard cap: max agent executions per hour in demo mode
DEMO_MAX_EXECUTIONS_PER_HOUR = int(os.environ.get("DEMO_MAX_EXECUTIONS_PER_HOUR", "30"))


def _demo_mode_enabled() -> bool:
    raw = os.environ.get("DEMO_MODE", "").strip().lower()
    return raw in ("true", "1", "yes", "on")


def _check_demo_mode(agent_name: str) -> Optional[GovernorDecision]:
    """If demo mode is on, only allowlisted agents may proceed.

    Returns a BLOCK decision if the agent is not on the allowlist,
    or None if demo mode is off or the agent is allowed.
    """
    if not _demo_mode_enabled():
        return None

    if agent_name in DEMO_AUTONOMY_ALLOWLIST:
        # Check hourly execution cap
        try:
            from django.core.cache import cache
            key = f"demo:hourly_count:{time.strftime('%Y%m%d%H')}"
            count = cache.get(key, 0)
            if count >= DEMO_MAX_EXECUTIONS_PER_HOUR:
                return GovernorDecision(
                    proceed=False,
                    reason='demo_hourly_cap',
                    agent_name=agent_name,
                    detail=f"demo mode hourly cap reached: {count}/{DEMO_MAX_EXECUTIONS_PER_HOUR}",
                )
            cache.set(key, count + 1, timeout=3600)
        except Exception:
            pass  # fail-open on cache errors
        return None  # allowed

    return GovernorDecision(
        proceed=False,
        reason='demo_blocked',
        agent_name=agent_name,
        detail=f"agent not in DEMO_AUTONOMY_ALLOWLIST ({len(DEMO_AUTONOMY_ALLOWLIST)} allowed)",
    )


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


# ── Per-Mission Telemetry (Redis counters) ────────────────────────────

def _today_key() -> str:
    """Return today's date string for daily counter keys."""
    from datetime import date
    return date.today().isoformat()


def _safe_cache_key(mission_name: str) -> str:
    """Sanitize mission name for use in Django cache keys."""
    import re
    return re.sub(r'[^a-zA-Z0-9_-]', '_', mission_name)[:80]


def record_mission_dispatch(mission_name: str) -> None:
    """Increment the daily dispatch counter for a mission."""
    try:
        from django.core.cache import cache
        key = f"gov:dispatches:{_safe_cache_key(mission_name)}:{_today_key()}"
        val = cache.get(key, 0)
        cache.set(key, val + 1, timeout=86400)  # expires in 24h
    except Exception:
        pass


def record_mission_skip(mission_name: str, reason: str) -> None:
    """Increment the daily skip counter for a mission."""
    try:
        from django.core.cache import cache
        key = f"gov:skips:{_safe_cache_key(mission_name)}:{_today_key()}"
        val = cache.get(key, 0)
        cache.set(key, val + 1, timeout=86400)
    except Exception:
        pass


def get_mission_daily_count(mission_name: str) -> int:
    """Get today's dispatch count for a mission."""
    try:
        from django.core.cache import cache
        key = f"gov:dispatches:{_safe_cache_key(mission_name)}:{_today_key()}"
        return cache.get(key, 0)
    except Exception:
        return 0


def check_mission_budget(mission_name: str, max_daily: Optional[int]) -> Optional[str]:
    """
    Check if a mission's daily execution budget is exhausted.
    Returns None if OK, or a reason string if budget is spent.
    """
    if max_daily is None:
        return None  # unlimited

    current = get_mission_daily_count(mission_name)
    if current >= max_daily:
        return (
            f"daily budget exhausted: {current}/{max_daily} executions today"
        )
    return None


def get_mission_telemetry() -> dict:
    """Get telemetry for all active missions — dispatches, skips, budget usage."""
    try:
        from django.core.cache import cache
        from core.models_unified_system import ActivePriority

        today = _today_key()
        missions = []
        for p in ActivePriority.objects.filter(status='active').order_by('priority_rank'):
            safe_name = _safe_cache_key(p.name)
            dispatches = cache.get(f"gov:dispatches:{safe_name}:{today}", 0)
            skips = cache.get(f"gov:skips:{safe_name}:{today}", 0)
            budget_used = None
            if p.max_daily_executions:
                budget_used = f"{dispatches}/{p.max_daily_executions}"
            missions.append({
                'name': p.name,
                'enabled': p.enabled,
                'rank': p.priority_rank,
                'dispatches_today': dispatches,
                'skips_today': skips,
                'budget': budget_used,
                'max_daily': p.max_daily_executions,
                'tags': list(p.tags or []),
            })
        return {'date': today, 'missions': missions}
    except Exception:
        return {'date': _today_key(), 'missions': [], 'error': 'telemetry unavailable'}


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
        # Session 1090: Demo mode check — applies to ALL trigger sources.
        # Must run before the user_triggers bypass.
        demo_block = _check_demo_mode(agent_name)
        if demo_block is not None:
            logger.info(
                "[governor] DEMO BLOCK %s: %s", agent_name, demo_block.detail,
            )
            return demo_block

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
            mission_name = decision.priority_name or 'unknown'

            # Layer 4: Check daily execution budget for this mission
            # Find the mission's budget from the cached priorities
            budget_limit = None
            priorities = router._get_cached_priorities()
            for p in priorities:
                if p.get('name') == mission_name:
                    budget_limit = p.get('max_daily_executions')
                    break

            budget_reason = check_mission_budget(mission_name, budget_limit)
            if budget_reason:
                logger.info(
                    "[governor] SKIP %s: mission '%s' %s",
                    agent_name, mission_name, budget_reason,
                )
                record_mission_skip(mission_name, 'budget_exhausted')
                return GovernorDecision(
                    proceed=False,
                    reason='budget_exhausted',
                    agent_name=agent_name,
                    detail=f"mission '{mission_name}': {budget_reason}",
                )

            # All checks passed — record and proceed
            record_mission_dispatch(mission_name)
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
            record_mission_skip('_unaligned', 'misaligned')
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
        tripped_agents = []
        try:
            from core.agent_router import AgentRouter
            router = AgentRouter()
            for agent_name in router.AGENT_MAP:
                if cache.get(f"cb:cooldown:{agent_name}"):
                    tripped_agents.append(agent_name)
        except Exception:
            pass

        # Include disabled missions for visibility
        disabled_missions = []
        try:
            disabled = ActivePriority.objects.filter(
                status='active', enabled=False
            )
            disabled_missions = [p.name for p in disabled]
        except Exception:
            pass

        telemetry = get_mission_telemetry()

        result = {
            "governor_enabled": _governor_enabled(),
            "demo_mode": _demo_mode_enabled(),
            "active_priorities": len(priorities),
            "priority_names": [p["name"] for p in priorities],
            "disabled_missions": disabled_missions,
            "circuit_breakers_tripped": tripped_agents,
            "telemetry": telemetry,
            "config": {
                "cb_window_size": CB_WINDOW_SIZE,
                "cb_failure_threshold": CB_FAILURE_THRESHOLD,
                "cb_cooldown_seconds": CB_COOLDOWN_SECONDS,
            },
        }
        if _demo_mode_enabled():
            result["demo_allowlist"] = sorted(DEMO_AUTONOMY_ALLOWLIST)
            result["demo_max_executions_per_hour"] = DEMO_MAX_EXECUTIONS_PER_HOUR
        return result
    except Exception:
        return {"governor_enabled": _governor_enabled(), "demo_mode": _demo_mode_enabled(), "error": "status unavailable"}
