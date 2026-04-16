"""
Session 1086 PR 3b: Semaphore-based throttling for priority-aware routing.

Two ``threading.BoundedSemaphore`` instances at module scope, one per
throttle class:

- **matched** — high-concurrency lane for work that matches an active
  priority (or user-triggered work that hits the user_chat exempt path,
  or fail-open when the priority router has no opinion).
- **mismatched** — low-concurrency lane for work that doesn't match
  any active priority.

## Why threading.BoundedSemaphore and not asyncio.Semaphore

``AgentRouter.route()`` is called from BOTH synchronous Celery worker
contexts AND asynchronous Django Channels consumers. A pure
``asyncio.Semaphore`` would force every sync caller to event-loop-bridge,
which is both ugly and slow. A pure ``threading.Semaphore`` would
block an event loop when async code hits ``acquire()``, which stalls
every other coroutine on that loop.

Rigby's Session 1086 design review (conversation ``pa-ada44848ca6b``)
locked the hybrid: sync paths do ``sem.acquire(timeout=...)`` directly,
async paths do ``await asyncio.to_thread(sem.acquire, True, timeout)``
so the blocking wait happens on a worker thread and the event loop
stays free.

## Fail-open on timeout

If the semaphore is fully saturated and ``acquire()`` times out, the
dispatch **proceeds anyway** with a warning log. We're a scheduler,
not a gate — missed throttling under load is better than blocking
real work. The timeout is intentionally short (5s default) so a runaway
acquire storm doesn't pile up waiters.

## Env-configurable bounds

- ``PRIORITY_MATCHED_CONCURRENCY``    — default 8
- ``PRIORITY_MISMATCHED_CONCURRENCY`` — default 1
- ``PRIORITY_ACQUIRE_TIMEOUT_S``      — default 5.0
- ``PRIORITY_THROTTLE_ENABLED``       — default FALSE (master gate)

All values are read at module import time. To change them in a running
worker, restart the process — matches the contract Rigby set for
``PRIORITY_MATCHED_SEMAPHORE=8`` / ``PRIORITY_MISMATCHED_SEMAPHORE=1``
in the design review.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from contextlib import contextmanager
from typing import Any, Iterator, Optional

logger = logging.getLogger(__name__)


# ── Env configuration ──────────────────────────────────────────────────

def _read_int_env(name: str, default: int) -> int:
    try:
        raw = os.environ.get(name, "").strip()
        if not raw:
            return default
        val = int(raw)
        if val < 1:
            return default
        return val
    except (TypeError, ValueError):
        return default


def _read_float_env(name: str, default: float) -> float:
    try:
        raw = os.environ.get(name, "").strip()
        if not raw:
            return default
        val = float(raw)
        if val <= 0:
            return default
        return val
    except (TypeError, ValueError):
        return default


PRIORITY_THROTTLE_ENABLED_ENV = "PRIORITY_THROTTLE_ENABLED"
MATCHED_CONCURRENCY = _read_int_env("PRIORITY_MATCHED_CONCURRENCY", 8)
MISMATCHED_CONCURRENCY = _read_int_env("PRIORITY_MISMATCHED_CONCURRENCY", 1)
ACQUIRE_TIMEOUT_S = _read_float_env("PRIORITY_ACQUIRE_TIMEOUT_S", 5.0)


def _throttle_enabled() -> bool:
    """Live-read the throttle gate. Same ``true/1/yes/on`` semantics as
    ``PRIORITY_ROUTER_ENABLED``. Both gates are independent: you can run
    observer-only (router ON, throttle OFF), throttled (both ON), or
    fully disabled (router OFF — throttle is a no-op regardless)."""
    raw = os.environ.get(PRIORITY_THROTTLE_ENABLED_ENV, "").strip().lower()
    return raw in ("true", "1", "yes", "on")


# ── Module-level semaphores ────────────────────────────────────────────

# Created eagerly at import so every worker/process shares a single
# instance per interpreter. The BoundedSemaphore flavor raises
# ValueError if release() is called more times than acquire() —
# defensive against context-manager bugs that would otherwise silently
# inflate the permit count.

_matched_sem = threading.BoundedSemaphore(MATCHED_CONCURRENCY)
_mismatched_sem = threading.BoundedSemaphore(MISMATCHED_CONCURRENCY)


# ── Rate-limited fail-open log (same 60s pattern as enforce.py) ────────

_last_timeout_log_ts: float = 0.0


def _log_timeout_rate_limited(throttle_class: str, agent_name: str) -> None:
    """Warn (not error) on acquire timeout. Rate-limited so a saturated
    semaphore doesn't flood logs. The warning includes the throttle
    class + agent name so operators can correlate with Celery queue
    depth."""
    global _last_timeout_log_ts
    try:
        now = time.monotonic()
        if now - _last_timeout_log_ts > 60.0:
            _last_timeout_log_ts = now
            logger.warning(
                "[priority-throttle] acquire timeout (class=%s agent=%s). "
                "Dispatch proceeding without throttle to avoid starvation. "
                "If this fires repeatedly, increase PRIORITY_%s_CONCURRENCY.",
                throttle_class,
                agent_name,
                throttle_class.upper(),
            )
    except Exception:
        pass  # logging must never break dispatch


# ── Public API: acquire_for_decision() ─────────────────────────────────

@contextmanager
def acquire_for_decision(decision: Optional[Any], agent_name: str) -> Iterator[bool]:
    """
    Context manager that acquires the correct semaphore for a given
    :class:`PriorityDecision` and releases it on exit. Yields ``True``
    if the acquire succeeded (or wasn't attempted), ``False`` if the
    acquire timed out (caller should still proceed — fail-open).

    No-op cases (yields ``True`` immediately, no actual acquire):

    - ``decision is None`` (the router gate is OFF)
    - ``PRIORITY_THROTTLE_ENABLED`` is not set to true
    - ``decision.matched_via == 'user_chat_exempt'`` (user work is
      never throttled, regardless of matched/mismatched)

    Acquire cases:

    - ``decision.matched is True`` → matched semaphore (capacity 8)
    - ``decision.matched is False`` → mismatched semaphore (capacity 1)

    Timeout behavior: if ``acquire(timeout=ACQUIRE_TIMEOUT_S)`` returns
    False, yield ``False`` and proceed WITHOUT holding a permit. A rate-
    limited warning is logged. This is the fail-open guarantee — we
    never block real work on the throttle mechanism.

    Usage::

        decision = check_priority(agent_name, task, trigger_source=...)
        log_decision(decision, agent_name)
        with acquire_for_decision(decision, agent_name):
            result = agent.execute(...)
    """
    # Short-circuit: nothing to do
    if decision is None or not _throttle_enabled():
        yield True
        return

    # user_chat exempt → never throttle
    matched_via = getattr(decision, "matched_via", None)
    if matched_via == "user_chat_exempt":
        yield True
        return

    # Pick semaphore
    matched = getattr(decision, "matched", True)
    sem = _matched_sem if matched else _mismatched_sem
    throttle_class = "matched" if matched else "mismatched"

    acquired = False
    try:
        acquired = sem.acquire(blocking=True, timeout=ACQUIRE_TIMEOUT_S)
        if not acquired:
            _log_timeout_rate_limited(throttle_class, agent_name)
        yield acquired
    finally:
        if acquired:
            try:
                sem.release()
            except ValueError:
                # BoundedSemaphore raises if released more times than
                # acquired. Swallow + log — indicates a release-without-
                # acquire bug elsewhere, but fail-open per contract.
                logger.exception(
                    "[priority-throttle] BoundedSemaphore release overrun "
                    "(class=%s) — potential context-manager bug",
                    throttle_class,
                )


# ── Introspection helper (for tests + telemetry) ───────────────────────

def get_semaphore_stats() -> dict:
    """Return current semaphore state for tests, health checks, and
    future operator dashboards. ``threading.BoundedSemaphore`` doesn't
    expose the current value directly, so we can't report exact
    available permits — but we can report the configured bounds."""
    return {
        "matched_concurrency": MATCHED_CONCURRENCY,
        "mismatched_concurrency": MISMATCHED_CONCURRENCY,
        "acquire_timeout_s": ACQUIRE_TIMEOUT_S,
        "throttle_enabled": _throttle_enabled(),
    }
