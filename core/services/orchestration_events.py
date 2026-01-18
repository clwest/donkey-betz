"""
Orchestration Events - Real-time WebSocket Event Emission
==========================================================

Session 768: Emits orchestration events to connected WebSocket clients
for real-time UI updates.

Usage:
    from core.services.orchestration_events import emit_orchestration_event

    emit_orchestration_event('orchestration_started', {
        'execution_id': str(execution.id),
        'workflow_name': workflow.name,
    })
"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


def emit_orchestration_event(event_type: str, data: Dict[str, Any]) -> None:
    """
    Emit an orchestration event to all connected WebSocket clients.

    This is a synchronous wrapper that can be called from anywhere.

    Args:
        event_type: Type of event (e.g., 'orchestration_started')
        data: Event payload data
    """
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        if channel_layer is None:
            logger.warning("No channel layer available for WebSocket events")
            return

        async_to_sync(channel_layer.group_send)(
            'system_events',
            {
                'type': event_type,
                'data': data,
                'timestamp': datetime.now().isoformat(),
            }
        )

        logger.debug(f"Emitted orchestration event: {event_type}")

    except Exception as e:
        # Don't let event emission errors break the orchestration
        logger.warning(f"Failed to emit orchestration event {event_type}: {e}")


def emit_execution_started(execution) -> None:
    """Emit event when a workflow execution starts."""
    emit_orchestration_event('orchestration_started', {
        'execution_id': str(execution.id),
        'workflow_id': str(execution.workflow_id),
        'workflow_name': execution.workflow.name,
        'total_steps': execution.total_steps,
        'triggered_by': execution.triggered_by.username if execution.triggered_by else None,
    })


def emit_step_started(execution, step) -> None:
    """Emit event when a workflow step starts."""
    emit_orchestration_event('orchestration_step_started', {
        'execution_id': str(execution.id),
        'workflow_name': execution.workflow.name,
        'step_number': step.order,
        'step_name': step.name,
        'agent_name': step.agent,
        'total_steps': execution.total_steps,
    })


def emit_step_completed(execution, step, cost: float = 0, tokens: int = 0) -> None:
    """Emit event when a workflow step completes."""
    emit_orchestration_event('orchestration_step_completed', {
        'execution_id': str(execution.id),
        'workflow_name': execution.workflow.name,
        'step_number': step.order,
        'step_name': step.name,
        'agent_name': step.agent,
        'current_step': execution.current_step,
        'total_steps': execution.total_steps,
        'cost': cost,
        'tokens': tokens,
    })


def emit_step_failed(execution, step, error: str) -> None:
    """Emit event when a workflow step fails."""
    emit_orchestration_event('orchestration_step_failed', {
        'execution_id': str(execution.id),
        'workflow_name': execution.workflow.name,
        'step_number': step.order,
        'step_name': step.name,
        'agent_name': step.agent,
        'error': error[:500],  # Truncate long errors
    })


def emit_execution_paused(execution, reason: str = 'Waiting for approval') -> None:
    """Emit event when execution is paused for approval."""
    emit_orchestration_event('orchestration_paused', {
        'execution_id': str(execution.id),
        'workflow_name': execution.workflow.name,
        'current_step': execution.current_step,
        'total_steps': execution.total_steps,
        'reason': reason,
    })


def emit_execution_completed(execution) -> None:
    """Emit event when a workflow execution completes."""
    emit_orchestration_event('orchestration_completed', {
        'execution_id': str(execution.id),
        'workflow_name': execution.workflow.name,
        'total_cost': float(execution.total_cost),
        'total_tokens': execution.total_tokens,
        'completed_steps': execution.current_step,
        'total_steps': execution.total_steps,
    })


def emit_execution_failed(execution, error: str) -> None:
    """Emit event when a workflow execution fails."""
    emit_orchestration_event('orchestration_failed', {
        'execution_id': str(execution.id),
        'workflow_name': execution.workflow.name,
        'error_step': execution.error_step,
        'error': error[:500],  # Truncate long errors
        'current_step': execution.current_step,
        'total_steps': execution.total_steps,
    })
