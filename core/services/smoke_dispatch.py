"""Smoke context minimization — strip non-allowlisted keys from fleet-smoke
dispatch contexts before they hit ``AgentExecution.input_data.context``.

Session 1213 (deliverable ``afe36715-721c-400f-b36f-4b9717467b66``). Spend
audit on 2026-06-23 found smoke turns averaging 35-68K tokens because spec
bodies (URC ~6KB, CampaignOrchestrator ~10KB) round-tripped under
``context.research`` on every PA-initiated agent dispatch. This module gates
the dispatch path so smokes carry only routing-essential keys.

Wrap point: ``core/services/tool_dispatcher.py:_handle_agent_tool`` right
before ``execute_agent_task.apply_async``. Single choke point — every
PA-initiated agent dispatch flows through there.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Tuple

logger = logging.getLogger(__name__)

# Keys allowed through to the agent when context.mode is a smoke mode.
# Everything else is stripped (or rejected, depending on enforcement mode).
SMOKE_CONTEXT_KEYS: frozenset[str] = frozenset({
    "mode",             # required marker
    "smoke_id",         # joins back to smoke evidence deliverable
    "receipt_only",     # legacy bool, forward-compat with URC Phase B
    "user_id",          # provenance + downstream attribution
    "conversation_id",  # task_notification routing (Session 1088)
    "workspace_id",     # deliverable provenance binding
    "auto_followup",    # dispatcher hint (suppresses completion banner)
})

# Modes that trigger the allowlist. outbound_pack is intentionally NOT here:
# Session 1208 CampaignOrchestrator legitimately needs spec bodies in
# context.research for the $2k Automation Sprint flow.
SMOKE_MODES: frozenset[str] = frozenset({
    "receipt_only",
    "fleet_smoke",
})

# Env-gated enforcement. strip = drop forbidden keys + log; warn = log only;
# error = raise. Default `strip` ships cost reduction non-breakingly.
ENFORCEMENT_ENV = "SMOKE_CONTEXT_ENFORCEMENT_MODE"
ENFORCEMENT_MODES: frozenset[str] = frozenset({"warn", "strip", "error"})

# AC-4 byte cap. Soft in strip/warn (log only), hard in error (raise).
SMOKE_CONTEXT_BYTE_CAP = 200


class SmokeContextViolation(ValueError):
    """Raised in ``error`` mode when a smoke dispatch carries forbidden keys."""


def _enforcement_mode() -> str:
    raw = (os.environ.get(ENFORCEMENT_ENV) or "strip").lower().strip()
    return raw if raw in ENFORCEMENT_MODES else "strip"


def _is_smoke_context(context: Dict[str, Any]) -> bool:
    mode = context.get("mode")
    return isinstance(mode, str) and mode in SMOKE_MODES


def apply_smoke_allowlist(context: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Return ``(possibly-stripped context, metadata)``.

    Pass-through (no change) when context is not a smoke dispatch. For smoke
    dispatches: aliases ``smoke``→``smoke_id``, then applies the allowlist
    per enforcement mode. ``metadata`` records what happened for telemetry.
    """
    if not isinstance(context, dict):
        return context, {"smoke_gate": "skipped_non_dict"}
    if not _is_smoke_context(context):
        return context, {"smoke_gate": "non_smoke"}

    # Alias ``smoke`` → ``smoke_id`` before allowlist check.
    working = dict(context)
    if "smoke" in working and "smoke_id" not in working:
        working["smoke_id"] = working.pop("smoke")

    forbidden = sorted(k for k in working if k not in SMOKE_CONTEXT_KEYS)
    stripped = {k: v for k, v in working.items() if k in SMOKE_CONTEXT_KEYS}
    pre_bytes = len(json.dumps(working, default=str).encode("utf-8"))
    post_bytes = len(json.dumps(stripped, default=str).encode("utf-8"))
    over_cap = post_bytes > SMOKE_CONTEXT_BYTE_CAP
    enforcement = _enforcement_mode()
    mode = working.get("mode")

    # Fast path: nothing to strip and post-strip size is under cap.
    if not forbidden and not over_cap:
        return working, {"smoke_gate": "clean", "mode": mode}

    if enforcement == "error":
        # Hard cap: raise on forbidden keys OR oversized post-strip context.
        problems: list[str] = []
        if forbidden:
            problems.append(f"non-allowlisted keys: {forbidden}")
        if over_cap:
            problems.append(f"post-strip bytes={post_bytes} > cap={SMOKE_CONTEXT_BYTE_CAP}")
        raise SmokeContextViolation(
            f"Smoke dispatch (mode={mode!r}) violated contract — "
            + "; ".join(problems)
            + f". Allowlist: {sorted(SMOKE_CONTEXT_KEYS)}."
        )

    if enforcement == "warn":
        logger.warning(
            "[smoke_dispatch] mode=%s forbidden_keys=%s pre_bytes=%d "
            "(warn-only, not stripped) over_cap=%s",
            mode, forbidden, pre_bytes, over_cap,
        )
        return working, {
            "smoke_gate": "warned",
            "mode": mode,
            "forbidden_keys": forbidden,
            "pre_bytes": pre_bytes,
            "post_bytes_if_stripped": post_bytes,
            "over_cap": over_cap,
        }

    # strip (default)
    logger.info(
        "[smoke_dispatch] mode=%s stripped_keys=%s pre_bytes=%d post_bytes=%d",
        mode, forbidden, pre_bytes, post_bytes,
    )
    if over_cap:
        # AC-4 soft cap: log if post-strip is still oversized. Allowlist-only
        # context with all 7 keys + UUID-shaped IDs can exceed 200B; that's
        # OK in strip/warn — operators see the warning and can shorten IDs.
        logger.warning(
            "[smoke_dispatch] mode=%s post_bytes=%d exceeds soft cap=%d "
            "(allowlist-only fields are large; consider shortening UUID-shaped "
            "smoke_id / workspace_id / conversation_id)",
            mode, post_bytes, SMOKE_CONTEXT_BYTE_CAP,
        )
    return stripped, {
        "smoke_gate": "stripped",
        "mode": mode,
        "stripped_keys": forbidden,
        "pre_bytes": pre_bytes,
        "post_bytes": post_bytes,
        "over_cap": over_cap,
    }
