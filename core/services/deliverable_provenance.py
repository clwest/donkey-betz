"""
Session 1184: Deliverable provenance read helper.

Builds the canonical `provenance` block surfaced by deliverable_tool.detail
(and any other read path that wants the chain): origin_execution_id,
trigger_source, created_by_agent, trace_id, and the tool calls associated
with the originating execution.

Design notes:

- The factory writes parent_object_type='agent_execution' + parent_object_id
  = AgentExecution.id (Session 843 contract). We treat parent_object_id as
  origin_execution_id when parent_object_type matches.
- For deliverables created directly via PA/tool layer without an
  AgentExecution context, the factory synthesizes a lightweight
  AgentExecution row first (status='completed', parent_object_type=
  'deliverable_factory') and links to it the same way.
- tool_calls are derived via trace_id pivot: AgentExecution.trace_id ↔
  ToolCallRecord.trace_id (no new FK).
- Legacy deliverables (parent_object_id NULL) get a `legacy_no_provenance`
  flag so callers can surface that fact explicitly.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _serialize_tool_call(record) -> Dict[str, Any]:
    return {
        'id': str(record.id),
        'tool_name': record.tool_name,
        'success': record.success,
        'latency_ms': record.latency_ms,
        'created_at': record.created_at.isoformat() if record.created_at else None,
    }


def build_provenance_block(deliverable) -> Dict[str, Any]:
    """Return a normalized provenance dict for a Deliverable instance.

    Shape:
        {
            "origin_execution_id": "<uuid|null>",
            "trigger_source": "<str>",
            "created_by_agent": "<str>",
            "trace_id": "<uuid|null>",
            "tool_calls": [{id, tool_name, success, latency_ms, created_at}, ...],
            "legacy_no_provenance": True|False,
            "synthesized": True|False,
        }
    """
    metadata = deliverable.metadata or {}
    block: Dict[str, Any] = {
        'origin_execution_id': None,
        'trigger_source': metadata.get('trigger_source') or 'unknown',
        'created_by_agent': deliverable.agent_name or '',
        'trace_id': None,
        'tool_calls': [],
        'legacy_no_provenance': False,
        'synthesized': bool(metadata.get('origin_execution_synthesized', False)),
    }

    parent_type = deliverable.parent_object_type or ''
    parent_id = deliverable.parent_object_id

    if not parent_id or parent_type not in ('agent_execution', 'deliverable_factory'):
        block['legacy_no_provenance'] = True
        return block

    block['origin_execution_id'] = str(parent_id)

    # Resolve the execution → trace_id → ToolCallRecord chain. All lookups
    # fail open: a missing execution row or trace_id leaves the block with
    # the id alone and a debug log.
    try:
        from core.models_unified_system import AgentExecution
        execution = AgentExecution.objects.filter(id=parent_id).only(
            'id', 'trace_id', 'owner_agent', 'task',
        ).first()
    except Exception as exc:
        logger.debug(
            "[deliverable_provenance] AgentExecution lookup failed for %s: %s",
            parent_id, exc,
        )
        execution = None

    if execution is None:
        return block

    if execution.owner_agent and not block['created_by_agent']:
        block['created_by_agent'] = execution.owner_agent

    if not execution.trace_id:
        return block

    block['trace_id'] = str(execution.trace_id)

    try:
        from core.models_tool_calls import ToolCallRecord
        records = list(
            ToolCallRecord.objects.filter(trace_id=execution.trace_id)
            .order_by('created_at')[:25]
        )
        block['tool_calls'] = [_serialize_tool_call(r) for r in records]
    except Exception as exc:
        logger.debug(
            "[deliverable_provenance] ToolCallRecord lookup failed for trace %s: %s",
            execution.trace_id, exc,
        )

    return block


def build_provenance_summary(deliverable) -> Dict[str, Any]:
    """Compact version for list views — strips the tool_calls payload."""
    block = build_provenance_block(deliverable)
    block.pop('tool_calls', None)
    return block
