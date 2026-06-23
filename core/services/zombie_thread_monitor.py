"""Zombie agent-thread monitor — Session 1220 P1.

Records and surfaces the rate at which the wall-clock-timeout
(`_FuturesTimeout`) handlers in `core/tasks_agents.py` and
`core/agent_router.py` fire. Per the Session 1219 Phase 3 investigation
(deliverable `cf80d413-…`), each such fire spawns a zombie thread that
keeps running until the agent body returns naturally (typically when the
synchronous OpenAI / spider call times out, ~90s) or until the Celery
child process recycles via ``--max-tasks-per-child``.

Phases 1 + 2 already close the *visible* symptom (orphaned ``AgentExecution``
rows). This module is the *observability* counterpart: it answers "how often
is this happening, for which agents, in which hour?" so we can alert on
structural-hang spikes (e.g., upstream LLM provider degraded).

Design (Option D from Phase 3 deliverable):

- Per-agent, per-hour counter at key ``zombie_threads:{agent_name}:{YYYYMMDDHH}``
  with 24h TTL. ``cache.add`` then ``cache.incr`` to handle the
  "key doesn't exist" case cleanly without races.
- Per-day registry of agent names that had any zombie in that day:
  ``zombie_threads_seen:{YYYYMMDD}`` storing a JSON list. Used by the
  query path to know which agent keys to fetch. 30-day TTL.

Fail-open: any cache exception is logged and swallowed. Monitoring must
never break dispatch.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from django.core.cache import cache

logger = logging.getLogger(__name__)

_KEY_PREFIX_COUNTER = 'zombie_threads'
_KEY_PREFIX_REGISTRY = 'zombie_threads_seen'

_COUNTER_TTL_S = 60 * 60 * 24       # 24h — keep ~last 24 hourly buckets
_REGISTRY_TTL_S = 60 * 60 * 24 * 30  # 30d — wide enough to outlive any query window


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _hour_bucket(dt: datetime) -> str:
    """``YYYYMMDDHH`` string for the hourly counter key."""
    return dt.strftime('%Y%m%d%H')


def _day_bucket(dt: datetime) -> str:
    """``YYYYMMDD`` string for the per-day agent-registry key."""
    return dt.strftime('%Y%m%d')


def _counter_key(agent_name: str, hour_bucket: str) -> str:
    return f'{_KEY_PREFIX_COUNTER}:{agent_name}:{hour_bucket}'


def _registry_key(day_bucket: str) -> str:
    return f'{_KEY_PREFIX_REGISTRY}:{day_bucket}'


def record_zombie_thread(agent_name: str) -> None:
    """Increment the per-agent, per-hour zombie counter.

    Called from the ``_FuturesTimeout`` handlers in
    ``core/tasks_agents.py`` and ``core/agent_router.py`` after the timeout
    has been logged + the failed ``AgentResult`` has been built.

    Idempotent within an hour: increments the current hour bucket. Fails
    open on any cache exception — monitoring must not break dispatch.
    """
    if not agent_name:
        return
    try:
        now = _now_utc()
        ckey = _counter_key(agent_name, _hour_bucket(now))
        # cache.add returns True if the key was set (didn't exist); False if
        # the key already existed and was not overwritten. After add(=1)
        # succeeds, subsequent incr calls land on top of it.
        if not cache.add(ckey, 1, timeout=_COUNTER_TTL_S):
            try:
                cache.incr(ckey, 1)
            except ValueError:
                # Race: another worker incremented after our add() saw the
                # key existed but before our incr() landed, and the TTL
                # expired between. Re-add at 1 — small undercounting in
                # extreme races is acceptable for a coarse-grained monitor.
                cache.set(ckey, 1, timeout=_COUNTER_TTL_S)

        # Update the per-day agent registry so the query path can enumerate
        # which agents had any zombie activity. Race-tolerant — set
        # semantics dedupe naturally.
        rkey = _registry_key(_day_bucket(now))
        existing = cache.get(rkey)
        if isinstance(existing, list):
            if agent_name not in existing:
                existing.append(agent_name)
                cache.set(rkey, existing, timeout=_REGISTRY_TTL_S)
        else:
            cache.set(rkey, [agent_name], timeout=_REGISTRY_TTL_S)
    except Exception:
        logger.exception(
            "[zombie_thread_monitor] record_zombie_thread failed for agent=%s "
            "(fail-open — dispatch continues)", agent_name,
        )


def get_zombie_rate(hours: int = 24, agent_name: Optional[str] = None) -> Dict:
    """Return a per-agent, per-hour breakdown of zombie-thread spawns.

    Args:
      hours: Number of hours back to query (1..168). Default 24.
      agent_name: Optional filter to a single agent. If None, returns all
        agents with non-zero counts in the window.

    Returns a dict shaped like::

        {
          'window_hours': 24,
          'from_hour': 'YYYYMMDDHH',
          'to_hour': 'YYYYMMDDHH',
          'by_agent': {
            'CTOAgent': {'total': 4, 'by_hour': {'YYYYMMDDHH': 2, ...}},
            ...
          },
          'top_offenders': [{'agent_name': 'CTOAgent', 'total': 4}, ...],
        }

    Fails open: returns an empty result on any cache exception.
    """
    hours = max(1, min(int(hours), 168))
    now = _now_utc()
    try:
        # Build the list of (hour_dt, hour_bucket) and (day_dt, day_bucket)
        # the window touches.
        hour_dts = [now - timedelta(hours=h) for h in range(hours)]
        hour_buckets = [_hour_bucket(dt) for dt in hour_dts]

        # Enumerate the agents that may have entries in this window — fetch
        # the per-day registries covering the window's days.
        day_buckets = sorted({_hour_bucket(dt)[:8] for dt in hour_dts})
        agents_seen: set[str] = set()
        for dbk in day_buckets:
            day_agents = cache.get(_registry_key(dbk))
            if isinstance(day_agents, list):
                agents_seen.update(day_agents)
        if agent_name:
            agents_seen = {agent_name} if agent_name in agents_seen else set()

        if not agents_seen:
            return {
                'window_hours': hours,
                'from_hour': hour_buckets[-1] if hour_buckets else None,
                'to_hour': hour_buckets[0] if hour_buckets else None,
                'by_agent': {},
                'top_offenders': [],
            }

        # Batch-fetch all counter keys we care about.
        keys_to_fetch: List[str] = []
        for agent in agents_seen:
            for hbk in hour_buckets:
                keys_to_fetch.append(_counter_key(agent, hbk))
        fetched = cache.get_many(keys_to_fetch)

        by_agent: Dict[str, Dict] = {}
        for agent in agents_seen:
            per_hour: Dict[str, int] = {}
            total = 0
            for hbk in hour_buckets:
                v = fetched.get(_counter_key(agent, hbk))
                if v:
                    try:
                        n = int(v)
                    except (TypeError, ValueError):
                        n = 0
                    if n > 0:
                        per_hour[hbk] = n
                        total += n
            if total > 0:
                by_agent[agent] = {'total': total, 'by_hour': per_hour}

        top = sorted(
            ({'agent_name': a, 'total': info['total']} for a, info in by_agent.items()),
            key=lambda r: r['total'],
            reverse=True,
        )

        return {
            'window_hours': hours,
            'from_hour': hour_buckets[-1] if hour_buckets else None,
            'to_hour': hour_buckets[0] if hour_buckets else None,
            'by_agent': by_agent,
            'top_offenders': top,
        }
    except Exception:
        logger.exception(
            "[zombie_thread_monitor] get_zombie_rate failed "
            "(fail-open — returning empty result)",
        )
        return {
            'window_hours': hours,
            'from_hour': None,
            'to_hour': None,
            'by_agent': {},
            'top_offenders': [],
            'error': 'monitor query failed — see worker logs',
        }
