"""
Session 1098 PR #3 — CancelTokenRegistry

Global registry mapping ``execution_id`` → cooperative cancel state. Any
code path with the execution_id can query or trigger cancellation; the
LLM wrapper (``core/services/llm_call_wrapper.py``) consults the registry
before starting and after finishing a call, and long-running agent loops
can call ``check_execution_cancelled()`` at safe checkpoints.

Storage: Redis when available (shared across Celery workers + Daphne),
with in-memory fallback for tests / when Redis is down. Never blocks
the caller: every operation is best-effort and swallows infrastructure
errors.

Contract (per Rigby's conversation ``pa-d19c1674b936``):

- **Idempotent:** setting cancel twice is a no-op; clearing a non-existent
  key is a no-op; checking a never-set key returns False.
- **Missing token == existing behavior:** code paths without an
  execution_id (or running before PR #3 migrations complete) behave
  exactly as they did before this module landed.
- **State + reason + location:** cancel records include a reason string
  and a location marker (e.g., ``"LLMCallWrapper:pre-call"``) so
  dashboards can show where cancellation was observed.

The persisted shape is a single Redis hash per execution::

    cancel:<execution_id> = {
        "cancelled": "1",
        "reason": "<string>",
        "requested_at": "<iso8601>",
        "observed_at": "<iso8601|null>",
        "observed_location": "<string|null>"
    }

TTL is 24h — long enough for any reasonable long-running task to
observe the cancel, short enough to keep the keyspace tidy.
"""

from __future__ import annotations

import logging
import os
import threading
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)

# 24h — longer than the longest configured agent timeout (1500s) with
# plenty of margin. See core/services/agent_timeouts.py.
CANCEL_KEY_TTL_SECONDS = 24 * 60 * 60

# Redis key prefix. Dashboards filter by this to list cancelled runs.
_REDIS_KEY_PREFIX = "cancel:"

# Fallback in-memory registry when Redis is unavailable. Thread-safe.
_mem_registry: Dict[str, Dict[str, str]] = {}
_mem_lock = threading.Lock()


_ExecutionIdLike = Optional[Union[uuid.UUID, str]]


def _coerce_execution_id(value: _ExecutionIdLike) -> Optional[str]:
    """Accept UUID/str/None; return canonical string form or None."""
    if value is None:
        return None
    if isinstance(value, uuid.UUID):
        return str(value)
    try:
        # Normalize arbitrary-case UUIDs to their canonical form.
        return str(uuid.UUID(str(value)))
    except (ValueError, TypeError):
        return None


def _redis_key(execution_id: str) -> str:
    return f"{_REDIS_KEY_PREFIX}{execution_id}"


def _get_redis():
    """Return a Redis client if available, else None.

    We lazy-import redis and fetch the REDIS_URL from Django settings
    at call time so this module stays importable in test contexts
    without redis installed.
    """
    try:
        import redis as redis_lib
        from django.conf import settings

        url = getattr(settings, "REDIS_URL", None) or os.environ.get("REDIS_URL")
        if not url:
            return None
        return redis_lib.Redis.from_url(
            url, decode_responses=True, socket_timeout=1.0,
            socket_connect_timeout=1.0,
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("cancel_registry: redis unavailable: %s", exc)
        return None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─────────────────────────── public API ──────────────────────────────── #


def request_execution_cancel(
    execution_id: _ExecutionIdLike,
    *,
    reason: str = "",
    requested_by: str = "",
) -> bool:
    """Signal that an in-flight execution should stop.

    Idempotent: repeated calls return True without changing anything.
    Missing / invalid execution_id returns False silently.

    Returns True on success (whether first or repeat), False if the
    execution_id couldn't be coerced or the storage write failed.
    """
    exec_id = _coerce_execution_id(execution_id)
    if not exec_id:
        return False

    entry = {
        "cancelled": "1",
        "reason": (reason or "")[:500],
        "requested_by": (requested_by or "")[:120],
        "requested_at": _now_iso(),
    }

    r = _get_redis()
    if r is not None:
        try:
            key = _redis_key(exec_id)
            # Write-once: only populate requested_at if not already set,
            # so repeated calls keep the first request's timestamp but
            # the token is still "cancelled=1".
            existing = r.hget(key, "cancelled")
            if existing == "1":
                # Already cancelled; don't clobber requested_at.
                return True
            r.hset(key, mapping=entry)
            r.expire(key, CANCEL_KEY_TTL_SECONDS)
            logger.info(
                "[cancel_registry] cancel requested execution_id=%s "
                "reason=%r by=%r",
                exec_id, reason, requested_by,
            )
            return True
        except Exception as exc:
            logger.warning(
                "[cancel_registry] redis hset failed, falling back to "
                "memory: %s", exc,
            )

    with _mem_lock:
        if _mem_registry.get(exec_id, {}).get("cancelled") == "1":
            return True
        _mem_registry[exec_id] = entry
    logger.info(
        "[cancel_registry] cancel requested (in-memory) execution_id=%s "
        "reason=%r by=%r",
        exec_id, reason, requested_by,
    )
    return True


def is_execution_cancelled(execution_id: _ExecutionIdLike) -> bool:
    """Return True if ``request_execution_cancel`` was called for this id
    OR for any ancestor in the execution tree (Session 1098 PR #4).

    The ancestor walk reads ``AgentExecution.parent_execution_id``. A
    cancel on the root execution cancels every child still running. The
    walk is capped at ``_MAX_ANCESTOR_DEPTH`` to prevent infinite loops
    on malformed lineage data; past the cap, we treat further ancestors
    as "unknown" and return the self-only result.

    Returns False on any infrastructure error — a broken Redis or
    missing AgentExecution row must never make the system claim
    "cancelled" spuriously.
    """
    exec_id = _coerce_execution_id(execution_id)
    if not exec_id:
        return False

    # Self check — fast path, no DB read.
    if _raw_is_cancelled(exec_id):
        return True

    # Ancestor walk — single DB query per ancestor, capped.
    try:
        return _any_ancestor_cancelled(exec_id)
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug(
            "[cancel_registry] ancestor walk failed: %s — returning False",
            exc,
        )
        return False


# Session 1098 PR #4: cap the ancestor walk so malformed lineage data
# (self-reference, cycle) can't trap the check in a loop. 25 is far
# deeper than any legitimate dispatch tree we've observed.
_MAX_ANCESTOR_DEPTH = 25


def _raw_is_cancelled(exec_id: str) -> bool:
    """Check the registry for an exact execution_id. No ancestor walk."""
    r = _get_redis()
    if r is not None:
        try:
            value = r.hget(_redis_key(exec_id), "cancelled")
            return value == "1"
        except Exception as exc:
            logger.debug(
                "[cancel_registry] redis hget failed, falling back: %s", exc,
            )

    with _mem_lock:
        return _mem_registry.get(exec_id, {}).get("cancelled") == "1"


def _any_ancestor_cancelled(exec_id: str) -> bool:
    """Walk parent_execution_id chain and return True on the first
    cancelled ancestor. Returns False past the depth cap."""
    try:
        from core.models_unified_system import AgentExecution
    except Exception:
        # Model unavailable (tests importing this module without Django
        # fully configured). No ancestor walk possible; return False.
        return False

    visited: set = set()
    current = exec_id
    depth = 0

    while depth < _MAX_ANCESTOR_DEPTH:
        if current in visited:
            # Cycle detected — lineage data is malformed. Stop walking;
            # fall through to "no cancelled ancestor found".
            logger.warning(
                "[cancel_registry] cycle detected in ancestor chain "
                "starting from %s at %s — aborting walk",
                exec_id, current,
            )
            return False
        visited.add(current)

        try:
            row = AgentExecution.objects.filter(
                id=current,
            ).values('parent_execution_id').first()
        except Exception as exc:
            logger.debug(
                "[cancel_registry] AgentExecution lookup failed for %s: %s",
                current, exc,
            )
            return False

        if not row:
            # Execution row unknown — no more ancestors to check.
            return False
        parent_id = row.get('parent_execution_id')
        if not parent_id:
            # Reached root. No cancelled ancestor.
            return False
        parent_id_str = str(parent_id)

        if _raw_is_cancelled(parent_id_str):
            return True

        current = parent_id_str
        depth += 1

    # Exhausted depth cap — treat as inconclusive (False) rather than
    # infinite loop. Rigby's spec: "mark as inconclusive rather than
    # infinite loop."
    logger.warning(
        "[cancel_registry] ancestor walk exceeded depth cap (%s) "
        "starting from %s — treating as not-cancelled",
        _MAX_ANCESTOR_DEPTH, exec_id,
    )
    return False


def mark_observed(
    execution_id: _ExecutionIdLike,
    *,
    location: str,
) -> None:
    """Record where the cancellation was first observed.

    Dashboards use ``observed_location`` to answer "where did cancel
    take effect?". Callers invoke this the first time they see the
    token fired (before raising LLMCallCancelled).

    Best-effort: failures never propagate.
    """
    exec_id = _coerce_execution_id(execution_id)
    if not exec_id or not location:
        return

    r = _get_redis()
    if r is not None:
        try:
            key = _redis_key(exec_id)
            # Only set once — the first observation wins.
            if not r.hget(key, "observed_location"):
                r.hset(
                    key,
                    mapping={
                        "observed_at": _now_iso(),
                        "observed_location": location[:200],
                    },
                )
            return
        except Exception as exc:  # pragma: no cover - defensive
            logger.debug("[cancel_registry] mark_observed redis: %s", exc)

    with _mem_lock:
        entry = _mem_registry.get(exec_id)
        if entry and not entry.get("observed_location"):
            entry["observed_at"] = _now_iso()
            entry["observed_location"] = location[:200]


def get_cancel_state(execution_id: _ExecutionIdLike) -> Optional[Dict[str, Any]]:
    """Return the full cancel record for this execution, or None.

    Dashboard / ops helper — not on the hot path.
    """
    exec_id = _coerce_execution_id(execution_id)
    if not exec_id:
        return None

    r = _get_redis()
    if r is not None:
        try:
            data = r.hgetall(_redis_key(exec_id))
            return dict(data) if data else None
        except Exception:
            pass

    with _mem_lock:
        entry = _mem_registry.get(exec_id)
        return dict(entry) if entry else None


def clear_execution_cancel(execution_id: _ExecutionIdLike) -> bool:
    """Remove any cancel record for this id. Used by tests + cleanup.

    Returns True if a key was cleared, False if none existed. Never
    raises.
    """
    exec_id = _coerce_execution_id(execution_id)
    if not exec_id:
        return False

    cleared = False
    r = _get_redis()
    if r is not None:
        try:
            cleared = bool(r.delete(_redis_key(exec_id)))
        except Exception:
            pass

    with _mem_lock:
        if _mem_registry.pop(exec_id, None) is not None:
            cleared = True

    return cleared


def _reset_memory_registry_for_tests() -> None:
    """Used exclusively by tests to get a clean in-memory state.

    Not a public API; importing this in production code is a smell.
    """
    with _mem_lock:
        _mem_registry.clear()


__all__ = [
    "request_execution_cancel",
    "is_execution_cancelled",
    "mark_observed",
    "get_cancel_state",
    "clear_execution_cancel",
    "CANCEL_KEY_TTL_SECONDS",
]
