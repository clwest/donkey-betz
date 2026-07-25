"""Substrate-native response → canonical response converters.

Each Tier-1 slice YAML declares a ``canonical_field_mapping`` block
(see ``evals/tier1/system_intelligence_agent.yaml:65-87``) that names the
derivation rule from substrate-native output (e.g., ``AgentResult`` for
``AgentExecution`` slices, or ``ChatConversation`` row + metadata for
``ChatConversation`` slices) to the canonical response shape validators
consume (``summary`` / ``evidence_pointers`` / ``health_status``).

The rules themselves are declarative in YAML but their implementations
live here so per-slice mappings are versioned in code and can be unit
tested independently of the YAML. Missing canonicalizers return
``None`` — the harness treats such prompts as INCONCLUSIVE rather than
falling through to a fabricated shape.

**PR-2a scope (S2965):** ``SystemIntelligenceAgent`` (slice 1) only.

**PR-2b scope (S2966):** 7 additional canonicalizers landing —
``ResearchAgent`` (slice 2), ``DevOpsAgent`` (slice 3),
``WorkflowOrchestrationAgent`` (slice 4), ``LegalDocDrafterAgent``
(slice 5), ``ContentWriterAgent`` (slice 6),
``CompetitorAnalysisAgent`` (slice 7), and ``Rigby`` (slice 8, the
first ``ChatConversation``-substrate canonicalizer). Each mirrors its
slice YAML's ``canonical_field_mapping`` derivation_rule verbatim so
authoring drift between YAML and code shows up as a canonicalizer
divergence rather than silent misvalidation.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any


CanonicalResponse = dict[str, Any]
Canonicalizer = Callable[[Any], CanonicalResponse]


# ── SystemIntelligenceAgent (canon_version=1, S2955-frozen) ─────────────


_ITEM_ID_RE = re.compile(r"[A-Za-z]+:[A-Za-z0-9_-]+")


def _get_attr_or_key(source: Any, name: str, default: Any = None) -> Any:
    """Uniform attribute/key access for AgentResult (dataclass-ish) or dict."""
    if isinstance(source, dict):
        return source.get(name, default)
    return getattr(source, name, default)


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

    message = str(_get_attr_or_key(agent_result, "message") or "")
    success = bool(_get_attr_or_key(agent_result, "success"))
    tool_calls = _get_attr_or_key(agent_result, "tool_calls") or []
    data = _get_attr_or_key(agent_result, "data") or {}

    pointers: list[dict[str, Any]] = []
    if isinstance(tool_calls, list):
        for idx, call in enumerate(tool_calls):
            if isinstance(call, dict):
                pointers.append({
                    "kind": "tool_call",
                    "index": idx,
                    "tool": call.get("tool"),
                    "arguments": call.get("arguments"),
                })
    for match in _ITEM_ID_RE.findall(message):
        pointers.append({"kind": "item_id", "ref": match})

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


# ── ResearchAgent (canon_version=1, S2956-frozen) ───────────────────────


def _research_v1_canonicalize(agent_result: Any) -> CanonicalResponse:
    """ResearchAgent → canonical response.

    Derivation rules (from ``evals/tier1/research_agent.yaml``
    canonical_field_mapping):

    * ``summary`` = ``AgentResult.message`` (native).
    * ``evidence_pointers`` = ``data.evidence_claims`` preferred;
      fall back to ``tool_calls`` entries.
    * ``health_status`` = derived from ``success`` + ``data.contract.status``.
    """
    if agent_result is None:
        return {}

    message = str(_get_attr_or_key(agent_result, "message") or "")
    success = bool(_get_attr_or_key(agent_result, "success"))
    data = _get_attr_or_key(agent_result, "data") or {}
    tool_calls = _get_attr_or_key(agent_result, "tool_calls") or []

    pointers: list[dict[str, Any]] = []
    evidence_claims = (data or {}).get("evidence_claims") if isinstance(data, dict) else None
    if isinstance(evidence_claims, list) and evidence_claims:
        for idx, claim in enumerate(evidence_claims):
            if isinstance(claim, dict):
                pointers.append({
                    "kind": "evidence_claim",
                    "index": idx,
                    "source_url": claim.get("source_url") or claim.get("url"),
                })
    elif isinstance(tool_calls, list):
        for idx, call in enumerate(tool_calls):
            if isinstance(call, dict):
                pointers.append({
                    "kind": "tool_call",
                    "index": idx,
                    "tool": call.get("tool"),
                    "arguments": call.get("arguments"),
                })

    if not success:
        health_status = "unavailable"
    else:
        contract = (data or {}).get("contract") if isinstance(data, dict) else None
        contract_status = (contract or {}).get("status") if isinstance(contract, dict) else None
        if contract_status == "RESOLVED":
            health_status = "healthy"
        elif contract_status == "BLOCKED":
            health_status = "degraded"
        elif contract_status in (None, "UNKNOWN"):
            health_status = "degraded"
        else:
            health_status = "healthy"

    return {
        "summary": message,
        "evidence_pointers": pointers,
        "health_status": health_status,
    }


# ── DevOpsAgent (canon_version=1, S2957-frozen) ─────────────────────────


def _devops_v1_canonicalize(agent_result: Any) -> CanonicalResponse:
    """DevOpsAgent → canonical response.

    Derivation rules (from ``evals/tier1/devops_agent.yaml``):

    * ``summary`` = ``AgentResult.message`` (native).
    * ``evidence_pointers`` = ``tool_calls`` preferred; fall back A =
      ``data.workspace_write.files`` (config path); fall back B =
      message text length (advisory path — legitimate for health-check
      queries where LLM chose not to dispatch tools).
    * ``health_status`` = derived from ``success`` + tool_calls presence +
      workspace_write result.
    """
    if agent_result is None:
        return {}

    message = str(_get_attr_or_key(agent_result, "message") or "")
    success = bool(_get_attr_or_key(agent_result, "success"))
    data = _get_attr_or_key(agent_result, "data") or {}
    tool_calls = _get_attr_or_key(agent_result, "tool_calls") or []

    pointers: list[dict[str, Any]] = []
    tool_calls_ok = False
    if isinstance(tool_calls, list) and tool_calls:
        for idx, call in enumerate(tool_calls):
            if isinstance(call, dict):
                result = call.get("result") or {}
                call_ok = (
                    result.get("success", True) if isinstance(result, dict) else True
                )
                pointers.append({
                    "kind": "tool_call",
                    "index": idx,
                    "tool": call.get("tool"),
                    "result_success": call_ok,
                })
                if not call_ok:
                    tool_calls_ok = False
                    break
        else:
            tool_calls_ok = True

    workspace_write = (data or {}).get("workspace_write") if isinstance(data, dict) else None
    workspace_written = (
        (workspace_write or {}).get("written", False)
        if isinstance(workspace_write, dict) else False
    )
    if isinstance(workspace_write, dict):
        files = workspace_write.get("files") or []
        if isinstance(files, list):
            for idx, f in enumerate(files):
                pointers.append({
                    "kind": "workspace_file",
                    "index": idx,
                    "path": (f.get("path") if isinstance(f, dict) else str(f)),
                })

    if not success:
        health_status = "unavailable"
    elif not tool_calls and message:
        # Advisory path — legitimate for health-check / recommendation asks.
        health_status = "healthy"
    elif tool_calls_ok and workspace_written:
        health_status = "healthy"
    elif tool_calls_ok and not workspace_written:
        health_status = "degraded"
    else:
        health_status = "degraded"

    return {
        "summary": message,
        "evidence_pointers": pointers,
        "health_status": health_status,
    }


# ── WorkflowOrchestrationAgent (canon_version=1, S2958-frozen) ──────────


def _workflow_v1_canonicalize(agent_result: Any) -> CanonicalResponse:
    """WorkflowOrchestrationAgent → canonical response.

    Derivation rules (from ``evals/tier1/workflow_orchestration_agent.yaml``):

    * ``summary`` = ``AgentResult.message`` (native, 5 possible shapes).
    * ``evidence_pointers`` = cascading tiers:
        1. ``data.step_results`` (preferred, currently empty on happy paths
           per wrapper-key-mismatch fold F1 — code fix in follow-up PR)
        2. ``data.image_ids``
        3. ``data.video_ids``
        4. ``data.project_created``
        5. ``data.workflow_steps`` (conceptual path)
      Tier 6 (integration DB queries) OUT OF SCOPE for Tier-1 validators.
      Note: ``tool_calls`` is hardcoded ``[]`` on this agent (``tools=[]``);
      not treated as failure signal.
    * ``health_status`` = derived from ``success`` + tier-population.
    """
    if agent_result is None:
        return {}

    message = str(_get_attr_or_key(agent_result, "message") or "")
    success = bool(_get_attr_or_key(agent_result, "success"))
    data = _get_attr_or_key(agent_result, "data") or {}
    if not isinstance(data, dict):
        data = {}

    pointers: list[dict[str, Any]] = []
    for tier_key, kind_label in (
        ("step_results", "step_result"),
        ("image_ids", "image_id"),
        ("video_ids", "video_id"),
        ("workflow_steps", "workflow_step"),
    ):
        entries = data.get(tier_key) or []
        if isinstance(entries, list):
            for idx, entry in enumerate(entries):
                pointers.append({"kind": kind_label, "index": idx, "value": entry})
            if pointers:
                break
    project_created = data.get("project_created")
    if isinstance(project_created, dict) and project_created.get("success"):
        pointers.append({
            "kind": "project_created",
            "project_id": project_created.get("project_id"),
        })

    if not success:
        health_status = "unavailable"
    elif pointers:
        health_status = "healthy"
    elif "timed out" in message.lower():
        health_status = "unavailable"
    else:
        health_status = "degraded"

    return {
        "summary": message,
        "evidence_pointers": pointers,
        "health_status": health_status,
    }


# ── LegalDocDrafterAgent (canon_version=1, S2959-frozen) ────────────────


def _legal_v1_canonicalize(agent_result: Any) -> CanonicalResponse:
    """LegalDocDrafterAgent → canonical response.

    Derivation rules (from ``evals/tier1/legal_doc_drafter_agent.yaml``):

    Standard mode: tool_calls preferred; fallback A =
    ``data.saved_document_ids``; fallback B = ``data.saved_research_ids``;
    fallback C = message length (advisory path).

    Denied-motion mode (execute() branch): programmatic dispatch bypasses
    GPT tool_calls; evidence is ``data.saved_document_ids`` OR
    JDF-marker regex on message.
    """
    if agent_result is None:
        return {}

    message = str(_get_attr_or_key(agent_result, "message") or "")
    success = bool(_get_attr_or_key(agent_result, "success"))
    data = _get_attr_or_key(agent_result, "data") or {}
    if not isinstance(data, dict):
        data = {}
    tool_calls = _get_attr_or_key(agent_result, "tool_calls") or []

    pointers: list[dict[str, Any]] = []
    if isinstance(tool_calls, list):
        for idx, call in enumerate(tool_calls):
            if isinstance(call, dict):
                pointers.append({
                    "kind": "tool_call",
                    "index": idx,
                    "tool": call.get("tool"),
                    "arguments": call.get("arguments"),
                })
    for id_field, kind_label in (
        ("saved_document_ids", "saved_document_id"),
        ("saved_research_ids", "saved_research_id"),
    ):
        ids = data.get(id_field) or []
        if isinstance(ids, list):
            for entry_id in ids:
                pointers.append({"kind": kind_label, "id": str(entry_id)})

    tool_calls_ok = True
    if isinstance(tool_calls, list):
        for call in tool_calls:
            if isinstance(call, dict):
                preview = call.get("result_preview") or ""
                if not preview or str(preview).startswith("Error:"):
                    tool_calls_ok = False
                    break

    if not success:
        health_status = "unavailable"
    elif not tool_calls and len(message) >= 200:
        health_status = "healthy"
    elif tool_calls_ok and (
        data.get("saved_document_ids") or data.get("saved_research_ids")
    ):
        health_status = "healthy"
    elif tool_calls_ok:
        health_status = "degraded"
    else:
        health_status = "unavailable"

    return {
        "summary": message,
        "evidence_pointers": pointers,
        "health_status": health_status,
    }


# ── ContentWriterAgent (canon_version=1, S2960-frozen) ──────────────────


def _content_v1_canonicalize(agent_result: Any) -> CanonicalResponse:
    """ContentWriterAgent → canonical response.

    Derivation rules (from ``evals/tier1/content_writer_agent.yaml``): 5
    mode branches (STANDARD / REWRITE / DIRECTED / DIAGNOSTIC /
    SELF-DESCRIPTION). Evidence pointers cascade by mode.

    * STANDARD: ``data.content.full_text`` + ``data.provenance`` +
      ``data.publishable``.
    * REWRITE / DIRECTED: ``data.content.full_text`` (>=500) +
      ``data.metadata.{rewrite,directed}_mode=True``.
    * DIAGNOSTIC: verbatim task→body (no additional structure).
    * SELF-DESCRIPTION: ``data.type='self_description'`` +
      ``data.capabilities``.
    """
    if agent_result is None:
        return {}

    message = str(_get_attr_or_key(agent_result, "message") or "")
    success = bool(_get_attr_or_key(agent_result, "success"))
    data = _get_attr_or_key(agent_result, "data") or {}
    if not isinstance(data, dict):
        data = {}

    content = data.get("content") or {}
    metadata = data.get("metadata") or {}
    full_text = content.get("full_text") if isinstance(content, dict) else None

    pointers: list[dict[str, Any]] = []
    if data.get("type") == "self_description":
        pointers.append({
            "kind": "self_description",
            "capabilities": data.get("capabilities") or [],
        })
    elif data.get("diagnostic_mode"):
        pointers.append({"kind": "diagnostic_content", "length": len(full_text or "")})
    elif isinstance(metadata, dict) and (
        metadata.get("rewrite_mode") or metadata.get("directed_mode")
    ):
        pointers.append({
            "kind": "content_body",
            "mode": "rewrite" if metadata.get("rewrite_mode") else "directed",
            "length": len(full_text or ""),
        })
    else:
        # STANDARD mode.
        if full_text:
            pointers.append({"kind": "content_body", "length": len(full_text)})
        provenance = data.get("provenance") or {}
        if isinstance(provenance, dict):
            sources = provenance.get("sources") or []
            if isinstance(sources, list):
                for idx, src in enumerate(sources):
                    pointers.append({"kind": "provenance_source", "index": idx, "source": src})
        if data.get("publishable"):
            pointers.append({"kind": "publishable_flag", "value": True})

    if not success:
        health_status = "unavailable"
    elif data.get("type") == "self_description":
        health_status = "healthy"
    elif data.get("diagnostic_mode"):
        health_status = "healthy"
    elif full_text and len(full_text) >= 200:
        health_status = "healthy"
    elif full_text:
        health_status = "degraded"
    else:
        health_status = "degraded"

    return {
        "summary": message,
        "evidence_pointers": pointers,
        "health_status": health_status,
    }


# ── CompetitorAnalysisAgent (canon_version=1, S2961-frozen) ─────────────


def _competitor_v1_canonicalize(agent_result: Any) -> CanonicalResponse:
    """CompetitorAnalysisAgent → canonical response.

    Derivation rules (from ``evals/tier1/competitor_analysis_agent.yaml``):

    STANDARD mode: ``data.analysis.analysis`` synthesis body +
    ``data.analysis.data_points_analyzed`` + ``data.raw_data`` +
    ``tool_calls`` + ``data.domain_relevance``. Fallback A (persistence):
    ``data.saved_id``.
    VIABILITY_EARLY_EXIT: ``data.type='viability_feedback'`` +
    ``data.viability`` block.
    EVIDENCE_GATE: message text is the "Insufficient..." refusal.
    """
    if agent_result is None:
        return {}

    message = str(_get_attr_or_key(agent_result, "message") or "")
    success = bool(_get_attr_or_key(agent_result, "success"))
    data = _get_attr_or_key(agent_result, "data") or {}
    if not isinstance(data, dict):
        data = {}
    tool_calls = _get_attr_or_key(agent_result, "tool_calls") or []

    pointers: list[dict[str, Any]] = []
    if data.get("type") == "viability_feedback":
        viability = data.get("viability") or {}
        pointers.append({
            "kind": "viability_feedback",
            "score": viability.get("score") if isinstance(viability, dict) else None,
        })
    else:
        analysis = data.get("analysis") or {}
        if isinstance(analysis, dict):
            if analysis.get("analysis"):
                pointers.append({
                    "kind": "analysis_body",
                    "length": len(str(analysis.get("analysis") or "")),
                    "data_points_analyzed": analysis.get("data_points_analyzed"),
                })
        raw_data = data.get("raw_data") or []
        if isinstance(raw_data, list):
            for idx, entry in enumerate(raw_data[:20]):  # cap enumeration
                pointers.append({
                    "kind": "raw_data",
                    "index": idx,
                    "source": (entry.get("source") if isinstance(entry, dict) else None),
                })
        if isinstance(tool_calls, list):
            for idx, call in enumerate(tool_calls):
                if isinstance(call, dict):
                    pointers.append({
                        "kind": "tool_call",
                        "index": idx,
                        "tool": call.get("tool"),
                    })
        if data.get("saved_id"):
            pointers.append({"kind": "saved_id", "id": str(data.get("saved_id"))})

    if not success:
        health_status = "unavailable"
    elif data.get("type") == "viability_feedback":
        health_status = "degraded"
    elif "Insufficient" in message[:30]:
        health_status = "degraded"
    elif pointers:
        health_status = "healthy"
    else:
        health_status = "degraded"

    return {
        "summary": message,
        "evidence_pointers": pointers,
        "health_status": health_status,
    }


# ── Rigby (canon_version=1, S2962-frozen — ChatConversation substrate) ─
#
# First non-AgentResult canonicalizer: input is a ``ChatConversation``
# row (not an ``AgentResult`` object). Derivation rules per
# ``evals/tier1/rigby_agent.yaml`` canonical_field_mapping.


def _rigby_v1_canonicalize(chat_conversation_row: Any) -> CanonicalResponse:
    """Rigby (UnifiedPAEntrypoint) → canonical response, from ChatConversation row.

    Derivation rules (from ``evals/tier1/rigby_agent.yaml``):

    * ``summary`` = ``ChatConversation.assistant_response`` (native).
    * ``evidence_pointers`` = derived from
      ``ChatConversation.metadata.tool_calls`` (Shape B sync-dispatch) OR
      ``metadata.artifact_pointers`` (Shape A async-callback). ToolCallRecord
      ledger join is the canonical evidence source but handled by the
      adapter (already reflected in ``ctx.evidence_ledger_refs``); this
      canonicalizer surfaces the substrate-native cache.
    * ``health_status`` = derived from response completeness +
      metadata.status + tool-run integrity (per rigby_v1 rules).
    """
    if chat_conversation_row is None:
        return {}

    assistant_response = str(getattr(chat_conversation_row, "assistant_response", "") or "")
    metadata = getattr(chat_conversation_row, "metadata", {}) or {}
    if not isinstance(metadata, dict):
        metadata = {}

    pointers: list[dict[str, Any]] = []
    # Shape B (sync-dispatch): tool_calls + tool_results.
    tool_calls = metadata.get("tool_calls") or []
    if isinstance(tool_calls, list):
        for idx, call in enumerate(tool_calls):
            if isinstance(call, dict):
                pointers.append({
                    "kind": "metadata_tool_call",
                    "index": idx,
                    "tool": call.get("tool"),
                })
    tool_results = metadata.get("tool_results") or []
    if isinstance(tool_results, list):
        for idx, res in enumerate(tool_results):
            if isinstance(res, dict):
                pointers.append({
                    "kind": "metadata_tool_result",
                    "index": idx,
                    "ok": res.get("ok"),
                })
    # Shape A (async-callback): artifact_pointers.
    artifacts = metadata.get("artifact_pointers") or []
    if isinstance(artifacts, list):
        for idx, art in enumerate(artifacts):
            pointers.append({"kind": "artifact_pointer", "index": idx, "ref": art})

    # Health status derivation (per rigby_v1 rules).
    if not assistant_response:
        health_status = "unavailable"
    elif metadata.get("status") == "failed" or metadata.get("error_signature"):
        health_status = "unavailable"
    elif (
        len(assistant_response) < 200
        and re.match(
            r"^(?:sorry|apologies|i (?:cannot|can\'t|couldn\'t|was unable to))",
            assistant_response,
            re.IGNORECASE,
        )
    ):
        health_status = "degraded"
    elif metadata.get("routed_to") and any(
        (r.get("ok") is True) for r in tool_results if isinstance(r, dict)
    ):
        health_status = "healthy"
    elif len(assistant_response) >= 200 and any(
        (r.get("ok") is True) for r in tool_results if isinstance(r, dict)
    ):
        health_status = "healthy"
    elif len(assistant_response) >= 40 and metadata.get("intent") in (
        "general", "session_management", "boardroom"
    ) and not tool_calls:
        health_status = "healthy"
    else:
        health_status = "healthy"

    return {
        "summary": assistant_response,
        "evidence_pointers": pointers,
        "health_status": health_status,
    }


# ── Registry ────────────────────────────────────────────────────────────


REGISTRY: dict[str, Canonicalizer] = {
    "SystemIntelligenceAgent": _sia_v1_canonicalize,
    "ResearchAgent": _research_v1_canonicalize,
    "DevOpsAgent": _devops_v1_canonicalize,
    "WorkflowOrchestrationAgent": _workflow_v1_canonicalize,
    "LegalDocDrafterAgent": _legal_v1_canonicalize,
    "ContentWriterAgent": _content_v1_canonicalize,
    "CompetitorAnalysisAgent": _competitor_v1_canonicalize,
    "Rigby": _rigby_v1_canonicalize,
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
