"""Retry-storm prevention: exponential backoff + retry budgets.

Session 1165 — COO Nervous System Backlog item #6 (MUST tier).
Canonical primitives for periodic-task retry behavior.

Two distinct mechanisms, exposed as explicit helpers (no magic decorator):

1. **Exponential backoff** — `compute_retry_countdown()` returns a
   countdown in seconds that grows as `base * 2**retries`, capped at
   `max_delay`, with optional ±25% jitter. Replaces the inconsistent
   linear / fixed / default countdown patterns across the codebase.

2. **Retry budgets** — `check_retry_budget()` increments a per-task,
   per-window counter in Redis (via Django cache) and refuses retry
   if the counter exceeds the window budget. Caps cascading failures
   where a broken upstream would otherwise burn unlimited retries.

## Why no decorator?

Earlier draft (Session 1165 design) wrapped the task body in a
decorator that caught exceptions and called `self.retry()` from the
wrapper. That collides with Celery's `Retry` exception machinery — if
the body explicitly calls `self.retry(exc=e)`, that raises `Retry`,
which the wrapper would re-catch as `Exception` and try to retry
again. Two cleaner-to-reason-about helpers + explicit callsite usage
keeps the control flow transparent.

## Callsite pattern

Before (Session 1165 #6 baseline):

    try:
        ...
    except Exception as e:
        logger.error(f"[TASK] Failed: {e}")
        raise self.retry(exc=e)

After:

    try:
        ...
    except Exception as e:
        logger.error(f"[TASK] Failed: {e}")
        from core.services.retry_policy import (
            check_retry_budget, compute_retry_countdown,
        )
        allowed, reason = check_retry_budget(
            "my_task", window_seconds=3600, max_retries=10,
        )
        if not allowed:
            logger.warning(f"[TASK] retry DENIED — {reason}")
            return {"retry_denied": True, "reason": reason}
        raise self.retry(
            exc=e,
            countdown=compute_retry_countdown(
                self.request.retries, base=60,
            ),
        )

## Design notes (from Rigby's Session 1165 review in `pa-f93d77e34f5d`)

- **Storage:** Django cache backend (Redis under the hood). Same
  approach as `core/services/redis_lock.py`. Sidesteps the Session
  1144 Redis-pooling-sweep backlog by not adding another inline
  client.
- **Cache atomicity:** `cache.incr()` is atomic on the Redis backend.
  On a hypothetical non-atomic backend, we degrade to "allow but log"
  rather than hard-block — preserving forward progress over strict
  correctness.
- **Countdown floor:** minimum 5 seconds even when `base * 2**0` is
  smaller under jitter. Protects against near-zero countdowns.
- **Counter increments on every check:** callers should only call
  `check_retry_budget` when they're about to schedule a retry, not
  on initial attempts.
- **Default fingerprint:** task_name only (global budget). Callsites
  with multi-tenant semantics should pass a fingerprint
  (`user_id`, `workspace_id`, etc.) so a single bad upstream doesn't
  freeze all callers globally.
- **Deny-fast reason strings:** when budget is exhausted, the helper
  returns a clear `(False, reason)` tuple instead of raising. Caller
  decides whether to fail-soft (log + skip) or hard.

## Memory rule context

Session 1144 backlog item #9 (Redis pooling sweep) intentionally not
joined here. Sister module to `core/services/redis_lock.py` —
matching primitive shape, matching backend.
"""

from __future__ import annotations

import logging
import random
from typing import Optional, Tuple

from django.core.cache import cache

logger = logging.getLogger(__name__)

BUDGET_KEY_PREFIX = "retry_budget:"

# Conservative floor for any computed countdown. Even base * 2**0 with
# negative jitter shouldn't dip below 5s; that just hammers the worker.
COUNTDOWN_FLOOR = 5

# Hard ceiling for any computed countdown. Protects against pathological
# combinations of `base` + `2**retries` reaching multi-hour delays where
# the task would have outlived its `expires` window anyway.
COUNTDOWN_CEILING = 3600


def compute_retry_countdown(
    retries: int,
    base: int = 60,
    max_delay: int = COUNTDOWN_CEILING,
    jitter: bool = True,
) -> int:
    """Canonical exponential-with-jitter retry countdown.

    Args:
        retries: Current retry count (Celery's `self.request.retries`).
        base: Seconds for the first retry (retries=0). Default 60s.
        max_delay: Hard cap on returned countdown.
        jitter: Apply ±25% randomization around the computed delay.

    Returns:
        Countdown in seconds, bounded by [COUNTDOWN_FLOOR, max_delay].

    Examples:
        compute_retry_countdown(0, base=60) → ~60s ± 25%  (in [45, 75])
        compute_retry_countdown(1, base=60) → ~120s ± 25% (in [90, 150])
        compute_retry_countdown(5, base=60) → ~1920s, capped → 3600s
    """
    delay = base * (2 ** max(0, retries))
    if jitter:
        # ±25% randomization. Multiplier in [0.75, 1.25].
        delay = int(delay * (0.75 + random.random() * 0.5))
    return max(COUNTDOWN_FLOOR, min(delay, max_delay))


def check_retry_budget(
    task_name: str,
    window_seconds: int = 3600,
    max_retries: int = 10,
    fingerprint: Optional[str] = None,
) -> Tuple[bool, str]:
    """Increment + check the retry budget for a task in a window.

    Args:
        task_name: Logical task identifier (e.g., dotted celery name).
        window_seconds: Sliding window during which retries are counted.
            Counter expires after this many seconds; effectively the
            budget reset interval.
        max_retries: Maximum retries allowed within the window before
            denying further attempts.
        fingerprint: Optional sub-scope for multi-tenant tasks
            (e.g., `f"user:{user_id}"`). When provided, the budget is
            tracked per-fingerprint; one bad caller doesn't poison
            siblings.

    Returns:
        (allowed: bool, reason: str). `allowed=True` means the budget
        is incremented and the caller can retry. `allowed=False` means
        the budget is exhausted; reason describes the cap.

    Notes:
        - Atomic on the Redis backend (`cache.incr` → Redis INCR).
        - On non-atomic backends, falls back to allow-and-log.
        - Increment happens on every call. Call only when about to
          schedule a retry, not on every task invocation.
    """
    suffix = f":{fingerprint}" if fingerprint else ""
    key = f"{BUDGET_KEY_PREFIX}{task_name}{suffix}"

    try:
        # `cache.incr` raises ValueError if the key doesn't exist on
        # most backends, so initialize lazily.
        try:
            current = cache.incr(key)
        except ValueError:
            cache.set(key, 1, timeout=window_seconds)
            current = 1
    except Exception as e:
        # Degraded mode — non-atomic backend or transient cache miss.
        # Allow + log; better to over-retry than freeze the queue.
        logger.warning(
            "retry_policy.check_retry_budget: cache failure for %s — "
            "degrading to allow (%s: %s)",
            key, type(e).__name__, e,
        )
        return True, "allow_degraded"

    if current > max_retries:
        return (
            False,
            f"budget_exhausted: {current}/{max_retries} retries in "
            f"{window_seconds}s window (key={key})",
        )
    fp_tag = f" fingerprint={fingerprint}" if fingerprint else ""
    return True, f"allowed: {current}/{max_retries}{fp_tag}"


def reset_retry_budget(task_name: str, fingerprint: Optional[str] = None) -> bool:
    """Manually reset a retry budget counter.

    For ops surfaces / debug REPL — clears the counter so the next
    retry attempt starts fresh. Useful after fixing the root cause of
    a budget exhaustion incident.

    Returns:
        True if the key was deleted, False if it didn't exist.
    """
    suffix = f":{fingerprint}" if fingerprint else ""
    key = f"{BUDGET_KEY_PREFIX}{task_name}{suffix}"
    return bool(cache.delete(key))
