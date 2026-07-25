"""Substrate-native response → canonical response converters.

Each Tier-1 slice YAML declares a ``canonical_field_mapping`` block
(see ``evals/tier1/system_intelligence_agent.yaml:65-87``) that names the
derivation rule from substrate-native output (e.g., ``AgentResult`` for
``AgentExecution`` slices) to the canonical response shape validators
consume (``summary`` / ``evidence_pointers`` / ``health_status``).

The rules themselves are declarative in YAML but their implementations
live here so per-slice mappings are versioned in code and can be unit
tested independently of the YAML. Missing canonicalizers return
``None`` — the harness treats such prompts as INCONCLUSIVE rather than
falling through to a fabricated shape.

**PR-2a scope:** ``SystemIntelligenceAgent`` (slice 1) only, sufficient
for the SIA dogfood. Additional canonicalizers land alongside their
slice acceptance runners at PR-2b / follow-ons.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any


CanonicalResponse = dict[str, Any]
Canonicalizer = Callable[[Any], CanonicalResponse]


# ── SystemIntelligenceAgent (canon_version=1, S2955-frozen) ─────────────


_ITEM_ID_RE = re.compile(r"[A-Za-z]+:[A-Za-z0-9_-]+")


def _sia_v1_canonicalize(agent_result: Any) -> CanonicalResponse:
    """SystemIntelligenceAgent → canonical response, per slice YAML §canonical_field_mapping.

    Derivation rules (verbatim from ``evals/tier1/system_intelligence_agent.yaml``
    lines 65-87):

    * ``summary`` = ``AgentResult.message`` (native).
    * ``evidence_pointers`` = tool_calls references + regex-matched item.id
      references in the message (derived rule ``sia_v1_tool_calls_plus_item_ids``).
    * ``health_status`` = derived from ``AgentResult.success`` + severity
      counts (derived rule ``sia_v1_counts_and_success``).
    """
    if agent_result is None:
        return {}

    # ``AgentResult`` is a Pydantic-like dataclass; attribute access works
    # for both real ``AgentResult`` instances and dicts (defensive).
    def _get(attr: str, default: Any = None) -> Any:
        if isinstance(agent_result, dict):
            return agent_result.get(attr, default)
        return getattr(agent_result, attr, default)

    message = str(_get("message") or "")
    success = bool(_get("success"))
    tool_calls = _get("tool_calls") or []
    data = _get("data") or {}

    # ── evidence_pointers ──────────────────────────────────────────────
    pointers: list[dict[str, Any]] = []
    if isinstance(tool_calls, list):
        for idx, call in enumerate(tool_calls):
            if isinstance(call, dict):
                pointers.append(
                    {
                        "kind": "tool_call",
                        "index": idx,
                        "tool": call.get("tool"),
                        "arguments": call.get("arguments"),
                    }
                )

    # Regex-scan the message body for item IDs (e.g., ``sia:foo`` /
    # ``escalation:bar``). Anything matching ``prefix:identifier`` counts.
    for match in _ITEM_ID_RE.findall(message):
        pointers.append({"kind": "item_id", "ref": match})

    # ── health_status ──────────────────────────────────────────────────
    if not success:
        health_status = "unavailable"
    else:
        critical = int((data or {}).get("critical_count", 0) or 0) if isinstance(data, dict) else 0
        warning = int((data or {}).get("warning_count", 0) or 0) if isinstance(data, dict) else 0
        if critical > 0:
            health_status = "unhealthy"
        elif warning > 0:
            health_status = "degraded"
        else:
            health_status = "healthy"

    return {
        "summary": message,
        "evidence_pointers": pointers,
        "health_status": health_status,
    }


# ── Registry ────────────────────────────────────────────────────────────


REGISTRY: dict[str, Canonicalizer] = {
    "SystemIntelligenceAgent": _sia_v1_canonicalize,
}


def canonicalize(agent_name: str, agent_result: Any) -> CanonicalResponse | None:
    """Look up + invoke the canonicalizer for ``agent_name``.

    Returns ``None`` when no canonicalizer is registered — the mgmt
    command treats that as "cannot validate; INCONCLUSIVE per canon Item 6
    substrate abstraction" rather than falling through to a fabricated
    shape.
    """
    fn = REGISTRY.get(agent_name)
    if fn is None:
        return None
    return fn(agent_result)


__all__ = ["REGISTRY", "canonicalize", "CanonicalResponse"]
