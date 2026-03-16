"""
Operation Recorder — Universal activity tracking for workspace operations.

Fire-and-forget utility that records every significant platform action
as a WorkspaceOperation. Never blocks the calling path.

Usage:
    from core.services.operation_recorder import record_op

    record_op(
        workspace_id='4728ea99-...',
        op_type='tool_call',
        title='ops_tool.slo_status',
        actor_type='system',
        actor_id='PersonalAssistant',
    )
"""

import logging
import uuid
from typing import Optional

logger = logging.getLogger(__name__)


def record_op(
    workspace_id: Optional[str] = None,
    op_type: str = 'system_event',
    title: str = '',
    description: str = '',
    actor_type: str = 'system',
    actor_id: Optional[str] = None,
    file_path: str = '',
    success: bool = True,
    error_message: str = '',
    execution_time_ms: int = 0,
    metadata: Optional[dict] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
    content: str = '',
):
    """
    Record a workspace operation. Fire-and-forget — never raises.

    Args:
        workspace_id: UUID of the workspace (auto-detects active if None)
        op_type: Operation type (tool_call, bpaas_project_create, deploy, etc.)
        title: Short description shown in the Operations tab
        description: Detailed description
        actor_type: 'user', 'agent', or 'system'
        actor_id: User ID, agent name, or service name
        file_path: File path if applicable
        success: Whether the operation succeeded
        error_message: Error details if failed
        execution_time_ms: Duration in milliseconds
        metadata: Additional structured data (JSON-serializable)
        entity_type: Type of entity affected (deliverable, initiative, etc.)
        entity_id: ID of the affected entity
        correlation_id: Request/task/execution ID for tracing
        content: Content produced (for file operations)
    """
    try:
        from core.models_skin_layer import ProjectWorkspace, WorkspaceOperation

        # Auto-detect active workspace if not specified
        ws = None
        if workspace_id:
            try:
                ws = ProjectWorkspace.objects.get(id=workspace_id)
            except ProjectWorkspace.DoesNotExist:
                pass

        if not ws:
            ws = ProjectWorkspace.objects.filter(is_active=True).first()

        if not ws:
            # No workspace available — log but don't fail
            logger.debug("[record_op] No workspace for op: %s %s", op_type, title)
            return

        # Map op_type to WorkspaceOperation's operation_type choices
        # Extend the choices mapping for new operation types
        type_mapping = {
            'tool_call': 'command_exec',
            'bpaas_project_create': 'file_create',
            'bpaas_close_pack': 'file_create',
            'preview_env_create': 'command_exec',
            'preview_deploy': 'deploy',
            'preview_destroy': 'command_exec',
            'magic_link_create': 'command_exec',
            'initiative_create': 'file_create',
            'initiative_promote': 'command_exec',
            'initiative_complete': 'command_exec',
            'deliverable_create': 'file_create',
            'deliverable_publish': 'command_exec',
            'deploy_start': 'deploy',
            'deploy_succeeded': 'deploy',
            'deploy_failed': 'deploy',
            'feedback_submit': 'file_create',
            'feedback_triage': 'command_exec',
            'vip_invite_create': 'command_exec',
            'vip_invite_exchange': 'command_exec',
        }

        operation_type = type_mapping.get(op_type, 'command_exec')

        # Build agent name from actor info
        agent_name = actor_id or actor_type
        agent_task = title

        # Build description with metadata
        full_description = description
        if metadata:
            import json
            meta_str = json.dumps(metadata, default=str)[:500]
            if full_description:
                full_description += f"\n\nMetadata: {meta_str}"
            else:
                full_description = meta_str

        # Add entity reference to description
        if entity_type and entity_id:
            ref = f"\n[{entity_type}: {entity_id}]"
            full_description = (full_description or '') + ref

        if correlation_id:
            full_description = (full_description or '') + f"\n[correlation: {correlation_id}]"

        WorkspaceOperation.objects.create(
            workspace=ws,
            user=ws.user,
            operation_type=operation_type,
            file_path=file_path or f"[{op_type}]",
            agent_name=agent_name,
            agent_task=agent_task,
            description=full_description[:2000] if full_description else '',
            success=success,
            error_message=error_message[:500] if error_message else '',
            execution_time_ms=execution_time_ms,
            file_content_after=content[:5000] if content else '',
            can_rollback=False,
        )

        # Update workspace operation counters
        ProjectWorkspace.objects.filter(id=ws.id).update(
            total_operations=models_F('total_operations') + 1,
            last_operation_at=_now(),
        )

    except Exception as e:
        # Never let operation recording break the calling path
        logger.warning("[record_op] Failed to record: %s %s: %s", op_type, title, e)


def _now():
    from django.utils import timezone
    return timezone.now()


def models_F(field):
    from django.db.models import F
    return F(field)
