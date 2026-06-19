"""Singleton-task locks (Redis-backed via Django cache).

Session 1165 — COO Nervous System Backlog item #3 (MUST tier):
periodic-task stampede prevention. Canonical SETNX-style lock primitive
+ `@singleton_task` decorator. Replaces three ad-hoc `cache.add(...)`
sites in `core/tasks.py` + `core/tasks_content.py` and gates a small
set of high-stampede-risk periodic tasks (see decorator usages).

## Design notes

- **Storage:** Django cache (`django.core.cache`). Already Redis-backed
  via the production settings; works identically to a raw `SET NX`.
- **Release semantics:** **TTL-only**. We do NOT explicitly `cache.delete`
  the key on success. Django cache lacks atomic compare-and-delete, and
  unconditional delete is unsafe under TTL contention (the long-running
  holder's TTL could expire while the task is mid-flight; a second
  acquirer takes the lock; the original holder finishes and deletes the
  newer holder's lock; a third invocation now stampedes). Rigby's
  Session 1165 design verdict: "TTL-only is acceptable if compare-delete
  is hard." Pick TTL = expected_duration * 2 conservatively; if a task
  legitimately runs >TTL, that's a separate finding, not a lock bug.
- **Lock value:** task_id when available (debuggable via Redis MONITOR
  or `cache.get(LOCK_PREFIX + name)`); falls back to "1".
- **Key format:** `singleton_lock:<name>`. Stable prefix so an ops
  surface (future) can `KEYS singleton_lock:*` to enumerate held locks.
- **On collision:** decorator returns `{"skipped": True, ...}`. Beat
  fires + dispatcher accepts; the SKIPPED row in `CeleryTaskEvent`
  carries the stampede event for observability.

Memory rule context: Session 1144 backlog item — Redis pooling sweep
(~40 inline `redis.Redis.from_url(...)` sites) is queued separately;
this module intentionally does NOT add another inline Redis client and
sidesteps that technical debt by using the Django cache backend.
"""

from __future__ import annotations

import functools
import logging
from contextlib import contextmanager
from typing import Optional

from django.core.cache import cache

logger = logging.getLogger(__name__)

LOCK_PREFIX = "singleton_lock:"


def acquire_singleton_lock(
    name: str, ttl: int = 600, value: Optional[str] = None
) -> bool:
    """Try to acquire a singleton lock; return True on success.

    Lower-level alternative to `singleton_lock` (context manager) and
    `@singleton_task` (decorator). Used by callsites that need
    fine-grained early-release semantics — e.g., acquire, run preflight
    checks, release early on certain branches via
    `release_singleton_lock(name)`, otherwise proceed with main work
    and let TTL handle final release.

    Args:
        name: Lock identifier (stored under `singleton_lock:<name>`).
        ttl: Seconds before auto-release.
        value: Value stored under the key (defaults to "1"). Pass
            task_id for debugging.

    Returns:
        True if the lock was newly acquired; False if a holder exists.
    """
    return bool(cache.add(LOCK_PREFIX + name, value or "1", timeout=ttl))


def release_singleton_lock(name: str) -> bool:
    """Explicitly release a singleton lock (delete the key).

    Used by manual `with singleton_lock(...)` callers that want to
    free the lock on an EARLY-EXIT path BEFORE the TTL expires (e.g.,
    a budget-defer or no-input shortcut). The decorator path
    (`@singleton_task`) deliberately does NOT call this — it leaves
    release to TTL.

    Race-condition caveat (per Rigby's Session 1165 nuance): this is
    a blind delete, not compare-and-delete. Safe IF the caller is
    confident their task body has not exceeded the lock TTL (which
    would let a second acquirer take the lock that this call would
    then erroneously erase). For the typical EARLY-EXIT use case
    (release immediately after acquire because preconditions failed)
    this is safe by construction; total path is well under TTL.

    Returns:
        True if the key was deleted, False if it didn't exist.
    """
    return bool(cache.delete(LOCK_PREFIX + name))


@contextmanager
def singleton_lock(name: str, ttl: int = 600, value: Optional[str] = None):
    """Acquire a SETNX-style singleton lock; yield True if acquired.

    Args:
        name: Lock identifier (e.g., task dotted name). Stored as
            `singleton_lock:<name>` after the canonical prefix.
        ttl: Seconds before auto-release. Conservative default 600s.
            Pick task-specific values via `expected_duration * 2`.
        value: Value to store under the key (defaults to "1"). Pass
            `self.request.id` for debuggable lock ownership.

    Yields:
        True if the lock was newly acquired; False if a holder exists.

    Notes:
        TTL-only release. No `cache.delete` on exit — TTL is the only
        release path. See module docstring for rationale.
    """
    key = LOCK_PREFIX + name
    acquired = cache.add(key, value or "1", timeout=ttl)
    try:
        yield acquired
    finally:
        # Intentional no-op. TTL handles release.
        pass


def singleton_task(name: str, ttl: int = 600):
    """Decorator: wrap a Celery task body in a `singleton_lock`.

    Place INSIDE the `@shared_task` / `@app.task` decorator so it
    wraps the function body, not the Celery `Task` wrapper. The
    underlying task must use `bind=True` if you want the task_id
    captured in the lock value (recommended for debugging).

    Example:
        @shared_task(bind=True)
        @singleton_task("capture-pa-acks-health-snapshot", ttl=2400)
        def capture_pa_acks_health_snapshot(self):
            ...

    On collision the task body is skipped and the wrapper returns:
        {"skipped": True, "reason": "concurrent run",
         "lock_name": <name>, "task_id": <id or None>}
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            task_id = None
            if args and hasattr(args[0], "request"):
                task_id = getattr(args[0].request, "id", None)
            with singleton_lock(name, ttl=ttl, value=task_id) as acquired:
                if not acquired:
                    logger.info(
                        "[singleton_task] skipping %s — concurrent run "
                        "detected (task_id=%s, ttl=%ds)",
                        name, task_id, ttl,
                    )
                    return {
                        "skipped": True,
                        "reason": "concurrent run",
                        "lock_name": name,
                        "task_id": task_id,
                    }
                return func(*args, **kwargs)
        return wrapper
    return decorator
