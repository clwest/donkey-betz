"""
LLM-autofill safety helpers for PA tool handlers.

Background — Session 1227 discovered that GPT-5.2 in function-calling
mode autofills every declared optional boolean schema param with Python
``False`` and every optional integer with ``0``, whether or not the user
asked to filter. Naive handler checks of the form::

    if x is not None:                  # bool filter, fires on autofilled False
    if payload.get('x', default):      # int default; autofilled 0 wins
    dry_run = payload.get('dry_run', True)  # autofilled False flips to write

silently change behavior on plain tool calls. PR1 of Session 1227 caught
it via ``has_initiative`` returning the wrong 180/300 row count; PR2
caught the int variant in ``deliverable_tool.duplicates``; PR4 added the
belt-and-suspenders ``dry_run`` + ``confirm`` write gate on ``normalize``.

Session 1228 PR-A extracts the canonical defenses into this module so
the rest of the PA tool surface stops duplicating the pattern (and the
next handler author doesn't have to rediscover it). Memory rule:
``feedback_llm_autofills_boolean_params_with_false``.

Three helpers:

- :func:`coerce_optional_bool` — for boolean filter params with a
  meaningful "on" and "off" direction (e.g. ``has_initiative``,
  ``auth_required``). Returns ``True`` / ``False`` / ``None`` for
  applied / explicitly-reversed / no-filter.

- :func:`is_truthy` — for one-direction switches where only ``True``
  changes behavior (e.g. ``show_all``, ``include_full_content``).

- :func:`require_write_authorization` — for mutation gates. Returns
  ``(dry_run, write_authorized)``. Write requires BOTH an explicit
  ``dry_run`` falsy value AND an explicit ``confirm`` truthy value.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Tuple

# Truthy values accepted as explicit "yes, this filter / write / flag is
# intentional". Python bool ``True`` is included — Rigby has been passing
# True explicitly in PR1/PR2/PR4 contracts and that intent is real.
_TRUTHY = frozenset([True, 'true', 'True', 1, '1'])

# Explicit string sentinels for the reverse direction of an optional bool
# filter. Python bool ``False`` is INTENTIONALLY EXCLUDED — that is the
# LLM-autofill value. Numeric 0 / '0' also excluded; PR1 (has_initiative)
# accepted only the string forms.
_EXPLICIT_FALSE_STRINGS = frozenset(['false', 'False'])

# Values that satisfy the dry_run=falsy half of the write gate. Includes
# Python bool ``False`` because the second-factor ``confirm=true`` check
# defends against autofill (the LLM autofills confirm as False, blocking
# the gate). Matches the PR4 normalize precedent.
_DRY_RUN_FALSY = frozenset([False, 'false', 'False', 0, '0'])


def _safe_in(value: Any, container) -> bool:
    """Membership check that tolerates unhashable values (list/dict).

    Tool payloads are JSON-deserialized so any value can show up. Returning
    False on unhashable inputs is the right default — they're never explicit
    boolean intent.
    """
    try:
        return value in container
    except TypeError:
        return False


def is_truthy(value: Any) -> bool:
    """True iff ``value`` is an explicit truthy signal from the caller.

    Used for one-direction switches like ``show_all`` or
    ``include_full_content`` where only ``True`` changes behavior and
    the default (no flag) is the safe behavior.
    """
    return _safe_in(value, _TRUTHY)


def coerce_optional_bool(value: Any) -> Optional[bool]:
    """Coerce an optional boolean filter payload value.

    Returns:
        ``True``  — caller explicitly wants the filter ON
        (Python True, 'true'/'True', 1, '1').

        ``False`` — caller explicitly wants the filter OFF (reverse
        direction, e.g. ``has_initiative='false'`` = ``IS NULL``).
        Only the string sentinels ``'false'``/``'False'`` qualify; Python
        bool ``False`` is treated as LLM autofill noise.

        ``None``  — no filter requested. Covers missing key, ``None``,
        Python bool ``False`` (autofill), empty string, and anything
        else that isn't an explicit signal.

    Mirrors the PR1 ``has_initiative`` semantics.
    """
    if _safe_in(value, _TRUTHY):
        return True
    if _safe_in(value, _EXPLICIT_FALSE_STRINGS):
        return False
    return None


def require_write_authorization(
    payload: Mapping[str, Any],
    *,
    dry_run_key: str = 'dry_run',
    confirm_key: str = 'confirm',
) -> Tuple[bool, bool]:
    """Belt-and-suspenders mutation gate.

    Returns ``(dry_run, write_authorized)``.

    Write is authorized only when BOTH conditions hold:

    1. ``dry_run`` was explicitly set falsy (Python ``False``,
       ``'false'``/``'False'``, ``0``, ``'0'``).
    2. ``confirm`` was explicitly set truthy (Python ``True``,
       ``'true'``/``'True'``, ``1``, ``'1'``).

    GPT-5.2 autofills declared optional booleans with Python ``False``.
    The autofilled ``dry_run=False`` alone would flip a
    ``payload.get('dry_run', True)`` site into write mode. Requiring a
    separate ``confirm=True`` (which the LLM autofills as ``False``,
    blocking the gate) defends against the silent flip until LLM
    autofill behavior changes for confirm too.

    Matches the Session 1227 PR4 ``normalize`` precedent. The default
    is ``dry_run=True`` (safe preview) — callers can render preview
    response without checking ``write_authorized`` first.
    """
    dry_run_raw = payload.get(dry_run_key)
    explicit_falsy = _safe_in(dry_run_raw, _DRY_RUN_FALSY)
    confirm_raw = payload.get(confirm_key)
    confirm_ok = _safe_in(confirm_raw, _TRUTHY)
    write_authorized = explicit_falsy and confirm_ok
    dry_run = not write_authorized
    return dry_run, write_authorized
