"""Session 1199 — Tool-context propagation for §6.2 cascade Step 2.

Carries the outer tool-call payload's ``initiative_id`` through the
execution chain so deep callers of ``create_deliverable()`` can resolve
the right Initiative without every layer having to know about it.

Design memo: docs/specs/INITIATIVES_FIRST_BACKBONE.md §6.2 (Step 2 of
the cascade). Implementation activates Step 2 which was wired but
inactive in Session 1198.

Uses ``contextvars`` so async tool calls don't leak context across
tasks. Set at the dispatcher entry point; read at
``create_deliverable()``. No other code needs to be aware.
"""

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Dict, Iterator, Optional


# The default is None — most code paths don't have tool context. The
# inference function tolerates ``tool_context=None`` cleanly (Step 2
# is skipped, cascade moves to Step 3).
_tool_context: ContextVar[Optional[Dict[str, Any]]] = ContextVar(
    "tool_context", default=None,
)


def get_current_tool_context() -> Optional[Dict[str, Any]]:
    """Read the current tool context dict, or None if not set.

    Safe to call anywhere — returns None outside a scope, never raises.
    """
    return _tool_context.get()


@contextmanager
def tool_context_scope(payload: Optional[Dict[str, Any]]) -> Iterator[None]:
    """Stash the relevant fields from ``payload`` for the duration of
    this scope.

    Currently extracts only ``initiative_id`` — the field §6.2 Step 2
    consumes. Future cascade steps may extract more (e.g., agent
    hint, workspace override) without changing this signature.

    Idempotent + safe to nest: inner scopes override outer for the
    nesting duration, then restore the outer context on exit (standard
    ``ContextVar.set/reset`` semantics).

    Yields nothing; use as ``with tool_context_scope(payload): ...``.
    """
    if not isinstance(payload, dict):
        # No payload → no context to set. Pass through cleanly.
        yield
        return

    initiative_id = payload.get("initiative_id")
    if not initiative_id:
        # Nothing to propagate. Skip the contextvar write so we don't
        # mask any outer scope's value with an empty dict.
        yield
        return

    ctx: Dict[str, Any] = {"initiative_id": str(initiative_id)}
    token = _tool_context.set(ctx)
    try:
        yield
    finally:
        _tool_context.reset(token)
