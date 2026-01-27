"""
Session 843: Orchestration Contract - Trace Attachment Service

Ensures all agent outputs are properly linked with trace_id and project_id.
This service provides the "wiring" that connects artifacts to workflows.
"""
import uuid
import logging
from typing import Dict, Any, Optional

from django.utils import timezone

logger = logging.getLogger(__name__)


class TraceAttachmentService:
    """
    Post-execution service that attaches trace_id and project_id to outputs.

    Fallback Rules for trace_id:
    1. Use explicit trace_id from context
    2. Inherit from parent_object's trace_id
    3. Inherit from conversation's trace_id
    4. Generate new trace_id (root execution)

    Fallback Rules for project_id:
    1. Use explicit project_id from context
    2. Inherit from parent_object
    3. Infer from user's active project
    4. Leave null (logged as WiringDefect)
    """

    @staticmethod
    def generate_trace_id() -> uuid.UUID:
        """Generate a new trace_id for a root execution."""
        return uuid.uuid4()

    @staticmethod
    def resolve_trace_id(
        context: Dict[str, Any],
        parent_object: Optional[Any] = None,
    ) -> uuid.UUID:
        """
        Resolve trace_id using fallback rules.

        Args:
            context: Dictionary containing execution context
            parent_object: Optional parent object to inherit trace from

        Returns:
            UUID trace_id
        """
        # 1. Explicit in context
        if context.get('trace_id'):
            trace = context['trace_id']
            if isinstance(trace, str):
                try:
                    return uuid.UUID(trace)
                except ValueError:
                    logger.warning(f"Invalid trace_id string in context: {trace}")
            elif isinstance(trace, uuid.UUID):
                return trace

        # 2. From parent object
        if parent_object and hasattr(parent_object, 'trace_id') and parent_object.trace_id:
            return parent_object.trace_id

        # 3. From conversation in context
        if context.get('conversation_id'):
            try:
                from core.models_unified_system import AgentConversation
                conv = AgentConversation.objects.filter(id=context['conversation_id']).first()
                if conv and hasattr(conv, 'trace_id') and conv.trace_id:
                    return conv.trace_id
            except Exception as e:
                logger.debug(f"Could not resolve conversation for trace_id: {e}")

        # 4. Generate new (root execution)
        return TraceAttachmentService.generate_trace_id()

    @staticmethod
    def resolve_project_id(
        context: Dict[str, Any],
        parent_object: Optional[Any] = None,
        user: Optional[Any] = None,
    ) -> Optional[uuid.UUID]:
        """
        Resolve project_id using fallback rules.

        Args:
            context: Dictionary containing execution context
            parent_object: Optional parent object to inherit project from
            user: Optional user to find active project for

        Returns:
            UUID project_id or None
        """
        # 1. Explicit in context
        if context.get('project_id'):
            pid = context['project_id']
            if isinstance(pid, str):
                try:
                    return uuid.UUID(pid)
                except ValueError:
                    logger.warning(f"Invalid project_id string in context: {pid}")
            elif isinstance(pid, uuid.UUID):
                return pid

        # 2. From parent object
        if parent_object:
            if hasattr(parent_object, 'project_id') and parent_object.project_id:
                return parent_object.project_id
            if hasattr(parent_object, 'project') and parent_object.project:
                return parent_object.project.id

        # 3. From user's active project (if available)
        if user:
            try:
                from core.models_partnership import PartnershipProject
                active = PartnershipProject.objects.filter(
                    user=user,
                    status='in_progress'
                ).order_by('-updated_at').first()
                if active:
                    return active.id
            except Exception as e:
                logger.debug(f"Could not resolve user's active project: {e}")

        # 4. Return None (will be logged as WiringDefect)
        return None

    @classmethod
    def attach_to_object(
        cls,
        obj: Any,
        context: Dict[str, Any],
        parent_object: Optional[Any] = None,
        user: Optional[Any] = None,
        agent_name: str = '',
    ) -> Dict[str, Any]:
        """
        Attach trace_id and project_id to an object.

        Args:
            obj: The object to attach trace context to
            context: Dictionary containing execution context
            parent_object: Optional parent object to inherit from
            user: Optional user for project resolution
            agent_name: Name of the agent for defect logging

        Returns:
            Dict with applied values and any defects:
            {
                'trace_id': UUID,
                'project_id': UUID or None,
                'defects': list of defect dicts
            }
        """
        result = {
            'trace_id': None,
            'project_id': None,
            'defects': [],
        }

        # Resolve values
        result['trace_id'] = cls.resolve_trace_id(context, parent_object)
        result['project_id'] = cls.resolve_project_id(context, parent_object, user)

        # Apply to object
        if hasattr(obj, 'trace_id'):
            obj.trace_id = result['trace_id']

        if hasattr(obj, 'project_id'):
            obj.project_id = result['project_id']
        elif hasattr(obj, 'project'):
            if result['project_id']:
                try:
                    from core.models_partnership import PartnershipProject
                    obj.project = PartnershipProject.objects.get(id=result['project_id'])
                except Exception:
                    result['project_id'] = None

        # Log defects
        if result['project_id'] is None:
            result['defects'].append({
                'type': 'missing_project_id',
                'object_type': type(obj).__name__,
                'object_id': str(obj.id) if hasattr(obj, 'id') and obj.id else 'unsaved',
                'trace_id': str(result['trace_id']),
                'agent_name': agent_name,
            })

        # Record defects to database
        if result['defects']:
            cls._record_defects(result['defects'], result['trace_id'], context)

        return result

    @staticmethod
    def _record_defects(defects: list, trace_id: uuid.UUID, context: Dict[str, Any]):
        """
        Record wiring defects to database.

        Args:
            defects: List of defect dictionaries
            trace_id: The trace_id associated with these defects
            context: Execution context for debugging
        """
        try:
            from core.models_orchestration import WiringDefect

            for defect in defects:
                try:
                    # Generate a placeholder UUID for unsaved objects
                    obj_id = defect['object_id']
                    if obj_id == 'unsaved':
                        obj_id = uuid.uuid4()
                    else:
                        obj_id = uuid.UUID(obj_id) if isinstance(obj_id, str) else obj_id

                    WiringDefect.objects.create(
                        defect_type=defect['type'],
                        object_type=defect['object_type'],
                        object_id=obj_id,
                        trace_id=trace_id,
                        agent_name=defect.get('agent_name', ''),
                        execution_context={
                            'context_keys': list(context.keys()),
                            'has_user': 'user' in context or 'user_id' in context,
                            'has_conversation': 'conversation_id' in context,
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to record individual wiring defect: {e}")
        except Exception as e:
            logger.warning(f"Failed to record wiring defects: {e}")

    @classmethod
    def get_context_for_child(
        cls,
        parent_execution: Any,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Build context for child executions that preserves trace lineage.

        Args:
            parent_execution: The parent AgentExecution or similar object
            additional_context: Additional context to merge in

        Returns:
            Context dict with trace_id and parent info
        """
        context = additional_context.copy() if additional_context else {}

        # Inherit trace_id from parent
        if hasattr(parent_execution, 'trace_id') and parent_execution.trace_id:
            context['trace_id'] = parent_execution.trace_id

        # Inherit project_id from parent
        if hasattr(parent_execution, 'project_id') and parent_execution.project_id:
            context['project_id'] = parent_execution.project_id
        elif hasattr(parent_execution, 'project') and parent_execution.project:
            context['project_id'] = parent_execution.project.id

        # Set parent reference
        context['parent_object_type'] = type(parent_execution).__name__
        context['parent_object_id'] = str(parent_execution.id) if hasattr(parent_execution, 'id') else None

        return context


# Singleton instance for easy access
_service_instance: Optional[TraceAttachmentService] = None


def get_trace_attachment_service() -> TraceAttachmentService:
    """Get or create the singleton TraceAttachmentService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = TraceAttachmentService()
    return _service_instance
