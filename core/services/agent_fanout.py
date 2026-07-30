"""S3047: shared AgentExecution lineage + fanout compute.

Single-codepath source for the 7 fanout fields surfaced by both the
Rigby ``agent_job_status`` PA tool (S3046, td_handlers_agents.py) and
the REST ``execution_detail`` view (S3047, views_agent_execution.py).

Extracted verbatim from ``_handle_agent_job_status`` fanout block so
the PA tool and REST endpoint cannot drift on child/subtree semantics.
"""

from typing import Any, Dict

from core.models_unified_system import AgentExecution


CHILDREN_CAP = 20


def compute_fanout(execution: AgentExecution) -> Dict[str, Any]:
    """Return the 7 lineage + fanout fields for a materialized execution row.

    Fields:
        parent_execution_id: str | None
        root_execution_id: str | None
        child_count: int (true count of direct children, not capped)
        subtree_count: int (all descendants; excludes self)
        children: list[dict] projection of first ``CHILDREN_CAP`` direct children
        children_truncated: bool (child_count > CHILDREN_CAP)
        fanout_available: bool (always True — caller decides False for missing rows)

    Root fallback: legacy rows (pre-migration-0336) have root=NULL; use
    ``execution.id`` as the root anchor so the subtree query still runs.
    """
    root_id_for_subtree = execution.root_execution_id or execution.id
    child_count = AgentExecution.objects.filter(
        parent_execution_id=execution.id,
    ).count()
    subtree_count = AgentExecution.objects.filter(
        root_execution_id=root_id_for_subtree,
    ).exclude(id=execution.id).count()
    children_rows = list(
        AgentExecution.objects.filter(parent_execution_id=execution.id)
        .order_by('created_at')
        .values(
            'id', 'agent__name', 'status',
            'created_at', 'completed_at', 'execution_time_ms',
        )[:CHILDREN_CAP]
    )
    children = [
        {
            'execution_id': str(row['id']),
            'agent_name': row['agent__name'],
            'status': row['status'],
            'created_at': row['created_at'].isoformat() if row['created_at'] else None,
            'completed_at': row['completed_at'].isoformat() if row['completed_at'] else None,
            'duration_ms': row['execution_time_ms'],
        }
        for row in children_rows
    ]
    return {
        'parent_execution_id': (
            str(execution.parent_execution_id) if execution.parent_execution_id else None
        ),
        'root_execution_id': (
            str(execution.root_execution_id) if execution.root_execution_id else None
        ),
        'child_count': child_count,
        'subtree_count': subtree_count,
        'children': children,
        'children_truncated': child_count > CHILDREN_CAP,
        'fanout_available': True,
    }
