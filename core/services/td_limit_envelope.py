"""
Shared retrieval-limit envelope helper for PA tool handlers.

Extracted at Session 2730 (Batch C tool 3 of the Rigby Tool Validation
Engineering Campaign) from four inline copies of the same pattern:

- ``deliverable_tool.list`` / ``.search`` at
  ``core/services/td_handlers_agents.py:1621`` (F-D-5, Batch A tool 1).
- ``content_tool.list_recent`` at
  ``core/services/td_handlers_core.py:4013`` (F-D-5 mirror).
- ``ops_tool.kb_browse`` at
  ``core/services/td_handlers_core.py:5267`` (F-KB-1, Batch A tool 3).
- ``repo_tool.tree`` / ``.search`` at
  ``core/services/td_handlers_gateway.py:113`` (F-RT-2 / F-RT-5,
  Batch B tool 2).

The pattern surfaces a **first-class signal** when a caller's requested
retrieval limit exceeds the handler's hard cap. Rigby's LLM autofill
of missing ``limit`` arguments — or explicit high values — no longer
silently returns a bounded slice; the response envelope carries::

    {
        'limit_capped': True,
        'requested_limit': <int the caller asked for>,
        'effective_limit': <int the handler used>,
        'hard_max': <int the handler's cap>,
    }

When no cap fires, the envelope is empty — call sites can spread it
into their response dict unconditionally without polluting the shape.

Autofill defenses baked in (mirrors ``td_autofill_safety`` module):

- Non-integer ``limit`` (``None`` / empty string / list / etc.) falls
  back to ``default``. Prevents ``TypeError`` from an autofilled ``''``.
- **Integer ``0``** falls back to ``default``. GPT-5.2 autofills declared
  optional integers with ``0``; a silent ``limit=0`` would return an
  empty list with no signal to Rigby. Session 1227 PR2 crystallized this
  for ``deliverable_tool.duplicates``; this module extends the defense
  to every migrated site.
- **Negative** ``limit`` also falls back to ``default`` — negative
  slice indices in Python don't have the "take last N" semantics Rigby
  might expect from a REST-shaped API, and no handler in the fleet
  currently accepts them.

MEMORY rules load-bearing here:

- ``feedback_llm_autofills_boolean_params_with_false``
- ``feedback_deliverable_tool_use_append_for_large_payloads``
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Tuple


def compute_limit(
    payload: Mapping[str, Any],
    default: int,
    hard_max: int,
    *,
    key: str = 'limit',
) -> Tuple[int, Dict[str, Any]]:
    """Compute the effective retrieval limit + F-D-5 envelope dict.

    Args:
        payload: the handler's ``payload`` dict (the arguments Rigby's
            LLM produced, or a direct-caller-built dict).
        default: fallback limit when the payload's ``limit`` is missing,
            non-integer, zero, or negative. Should match the schema's
            documented default so Rigby's mental model stays coherent.
        hard_max: the handler's cap. Requests above this are clamped and
            the returned envelope carries the F-D-5 shape.
        key: payload key to read. Defaults to ``'limit'``. Override for
            handlers that use ``'max'``, ``'count'``, or other names.

    Returns:
        ``(effective_limit, envelope_dict)``. Callers should spread the
        envelope into their response dict::

            limit, _envelope = compute_limit(payload, default=10, hard_max=50)
            qs = Model.objects.all()[:limit]
            return {'action': 'list', 'items': list(qs), **_envelope}

        The envelope is empty ``{}`` when no cap fires — spreading it
        into a return dict is a no-op in that case.
    """
    raw = payload.get(key, default)
    try:
        requested = int(raw)
    except (TypeError, ValueError):
        requested = default

    # Autofill / caller-error defenses. A requested limit of 0 or
    # negative is never the caller's real intent — LLM autofill fills
    # missing int params with 0; direct callers with negative slices
    # would break the ORM. Fall back to default.
    if requested <= 0:
        requested = default

    effective = min(requested, hard_max)
    if requested > hard_max:
        return effective, {
            'limit_capped': True,
            'requested_limit': requested,
            'effective_limit': effective,
            'hard_max': hard_max,
        }
    return effective, {}
