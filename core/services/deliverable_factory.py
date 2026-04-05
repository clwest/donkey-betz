"""
DeliverableFactory — Single gateway for creating Deliverables.

Consolidates 23+ scattered Deliverable.objects.create() calls into one
factory with consistent metadata, workspace assignment, and provenance tracking.

Usage:
    from core.services.deliverable_factory import create_deliverable

    deliverable = create_deliverable(
        title="Market Analysis Report",
        content="## Findings\n...",
        agent_name="ResearchAgent",
        category="Research",
        user=request.user,
        # Optional:
        workspace_id=workspace.id,
        trace_id=trace_id,
        parent_execution_id=execution.id,
        tags=["research", "market"],
        content_format="markdown",
        quality_score=0.85,
        metadata={"source": "scheduled_run"},
    )
"""

import logging
import uuid
from typing import Optional, List, Any

from django.conf import settings

logger = logging.getLogger(__name__)


def create_deliverable(
    title: str,
    content: str,
    agent_name: str,
    category: str = 'General',
    deliverable_type: str = 'document',
    user=None,
    workspace_id: Optional[str] = None,
    trace_id: Optional[str] = None,
    parent_execution_id: Optional[str] = None,
    parent_object_type: str = '',
    tags: Optional[List[str]] = None,
    content_format: str = 'markdown',
    quality_score: float = 0.0,
    confidence_score: float = 0.0,
    is_saved: bool = False,
    is_pinned: bool = False,
    agent_task: str = '',
    metadata: Optional[dict] = None,
    initiative_id: Optional[str] = None,
    dream_id: Optional[str] = None,
    source_operation_id: Optional[str] = None,
    # Pass-through for any additional model fields
    **extra_fields,
) -> Any:
    """
    Create a Deliverable with consistent metadata and workspace assignment.

    This is the ONLY function that should create Deliverables going forward.
    All 23+ existing creation paths should migrate to this factory.

    Returns the created Deliverable instance.
    """
    from core.models_deliverables import Deliverable

    # Auto-assign workspace if not provided
    if not workspace_id and user:
        workspace_id = _get_active_workspace_id(user)

    # Build preview
    preview = content[:500] if content else ''

    # Build creation kwargs
    kwargs = {
        'title': title[:500],  # Enforce max length
        'content': content,
        'agent_name': agent_name,
        'category': category,
        'deliverable_type': deliverable_type,
        'content_format': content_format,
        'preview_content': preview,
        'quality_score': quality_score,
        'confidence_score': confidence_score,
        'is_saved': is_saved,
        'is_pinned': is_pinned,
        'agent_task': agent_task,
        'tags': tags or [],
        'metadata': metadata or {},
    }

    # Optional foreign keys
    if user:
        kwargs['user'] = user
    if workspace_id:
        kwargs['workspace_id'] = workspace_id
    if trace_id:
        kwargs['trace_id'] = trace_id
    if parent_execution_id:
        kwargs['parent_object_type'] = parent_object_type or 'agent_execution'
        kwargs['parent_object_id'] = parent_execution_id
    if initiative_id:
        kwargs['initiative_id'] = initiative_id
    if dream_id:
        kwargs['dream_id'] = dream_id
    if source_operation_id:
        kwargs['source_operation_id'] = source_operation_id

    # Merge any extra fields (for backward compat with existing callers)
    kwargs.update(extra_fields)

    try:
        deliverable = Deliverable.objects.create(**kwargs)
        logger.info(
            f"[DeliverableFactory] Created: {deliverable.id} "
            f"'{title[:60]}' by {agent_name} "
            f"(workspace={workspace_id or 'none'}, user={getattr(user, 'id', 'none')})"
        )
        return deliverable
    except Exception as e:
        logger.error(
            f"[DeliverableFactory] Failed to create deliverable: {e} "
            f"(title='{title[:60]}', agent={agent_name})"
        )
        raise


def _get_active_workspace_id(user) -> Optional[str]:
    """Get the user's active workspace ID, or default workspace."""
    try:
        from core.models_skin_layer import ProjectWorkspace
        ws = ProjectWorkspace.objects.filter(
            user=user, is_active=True
        ).values_list('id', flat=True).first()
        if ws:
            return str(ws)
        # Fallback: any workspace owned by user
        ws = ProjectWorkspace.objects.filter(
            user=user
        ).values_list('id', flat=True).first()
        return str(ws) if ws else None
    except Exception:
        return None
