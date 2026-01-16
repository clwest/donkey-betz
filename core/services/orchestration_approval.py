"""
Orchestration Approval Service
==============================

Session 764: Manages approval gates for orchestration workflows.
Integrates with Mission Control for human-in-the-loop decisions.
"""

import logging
from datetime import timedelta
from typing import Dict, Any, Optional
from django.utils import timezone

logger = logging.getLogger(__name__)


class OrchestrationApprovalService:
    """
    Manages approval gates for workflow steps.

    Creates attention items in Mission Control when steps require
    human approval before or after execution.
    """

    def __init__(self):
        self._mission_control = None
        self._register_handlers()

    def _register_handlers(self):
        """Register handlers with Mission Control executor."""
        try:
            from core.services.mission_control_executor import mission_control_executor

            mission_control_executor.register(
                'approve_orchestration_step',
                self._handle_approve
            )
            mission_control_executor.register(
                'reject_orchestration_step',
                self._handle_reject
            )
            mission_control_executor.register(
                'modify_orchestration_step',
                self._handle_modify
            )

            logger.info("Registered orchestration approval handlers with Mission Control")
        except Exception as e:
            logger.warning(f"Could not register Mission Control handlers: {e}")

    @property
    def attention_bridge(self):
        """Get the human attention bridge."""
        from core.services.human_attention_bridge import attention_bridge
        return attention_bridge

    def create_approval_gate(
        self,
        execution,
        step,
        step_execution
    ):
        """
        Create an approval gate for a step that requires approval.

        Args:
            execution: OrchestrationExecution instance
            step: CustomWorkflowStep instance
            step_execution: OrchestrationStepExecution instance
        """
        from core.models_orchestration import OrchestrationApprovalGate
        from core.models_human_interface import HumanAttentionItem

        # Get approval config
        config = step.approval_config or {}
        timeout_hours = config.get('approval_timeout_hours', 24)
        auto_approve = config.get('auto_approve_on_timeout', False)
        approval_message = config.get('approval_message', f'Step {step.order} requires approval')

        # Calculate expiration
        expires_at = timezone.now() + timedelta(hours=timeout_hours) if timeout_hours else None

        # Create attention item
        user = execution.triggered_by

        try:
            attention_item = HumanAttentionItem.objects.create(
                user=user,
                source_type='orchestration',
                source_id=str(execution.id),
                source_agent=step.agent,
                item_type='approval',
                title=f'Workflow Step Approval: {step.name}',
                summary=approval_message,
                urgency='high',
                payload={
                    'orchestration_id': str(execution.id),
                    'step_number': step.order,
                    'step_name': step.name,
                    'agent_name': step.agent,
                    'step_input': step_execution.input_data,
                    'workflow_name': execution.workflow.name,
                    'auto_approve_on_timeout': auto_approve,
                },
                expires_at=expires_at,
            )

            # Create approval gate
            gate = OrchestrationApprovalGate.objects.create(
                orchestration=execution,
                step_execution=step_execution,
                status='pending',
                approval_config=config,
                expires_at=expires_at,
            )
            gate.set_attention_item(attention_item)
            gate.save()

            logger.info(
                f"Created approval gate for step {step.order} in execution {execution.id}"
            )

            return gate

        except Exception as e:
            logger.error(f"Failed to create approval gate: {e}", exc_info=True)
            raise

    def create_error_approval_gate(
        self,
        execution,
        step,
        error_message: str
    ):
        """
        Create an approval gate for a step that failed.

        Allows human to review error and decide to retry, skip, or abort.
        """
        from core.models_orchestration import (
            OrchestrationApprovalGate,
            OrchestrationStepExecution
        )
        from core.models_human_interface import HumanAttentionItem

        # Get the failed step execution
        step_exec = execution.step_executions.filter(
            step_number=step.order
        ).last()

        if not step_exec:
            logger.error(f"No step execution found for step {step.order}")
            return None

        user = execution.triggered_by

        try:
            attention_item = HumanAttentionItem.objects.create(
                user=user,
                source_type='orchestration_error',
                source_id=str(execution.id),
                source_agent=step.agent,
                item_type='error_review',
                title=f'Workflow Error: {step.name}',
                summary=f'Step failed: {error_message[:200]}',
                urgency='high',
                payload={
                    'orchestration_id': str(execution.id),
                    'step_number': step.order,
                    'step_name': step.name,
                    'agent_name': step.agent,
                    'error_message': error_message,
                    'retry_count': step_exec.retry_count,
                    'workflow_name': execution.workflow.name,
                    'available_actions': ['retry', 'skip', 'abort'],
                },
            )

            gate = OrchestrationApprovalGate.objects.create(
                orchestration=execution,
                step_execution=step_exec,
                status='pending',
                approval_config={'error_review': True},
            )
            gate.set_attention_item(attention_item)
            gate.save()

            logger.info(
                f"Created error approval gate for step {step.order} in execution {execution.id}"
            )

            return gate

        except Exception as e:
            logger.error(f"Failed to create error approval gate: {e}", exc_info=True)
            return None

    def check_auto_approvals(self):
        """
        Check for expired approval gates that should be auto-approved.

        Called periodically by Celery Beat.
        """
        from core.models_orchestration import OrchestrationApprovalGate

        now = timezone.now()

        # Find expired pending gates with auto-approve enabled
        expired_gates = OrchestrationApprovalGate.objects.filter(
            status='pending',
            expires_at__lt=now,
            approval_config__auto_approve_on_timeout=True
        )

        auto_approved_count = 0

        for gate in expired_gates:
            try:
                gate.auto_approve()

                # Resume the execution
                from core.services.orchestration_engine import orchestration_engine
                orchestration_engine.resume_execution(str(gate.orchestration.id))

                auto_approved_count += 1
                logger.info(
                    f"Auto-approved gate {gate.id} for execution {gate.orchestration.id}"
                )

            except Exception as e:
                logger.error(f"Failed to auto-approve gate {gate.id}: {e}")

        if auto_approved_count > 0:
            logger.info(f"Auto-approved {auto_approved_count} orchestration gates")

        # Mark non-auto-approve gates as expired
        expired_no_auto = OrchestrationApprovalGate.objects.filter(
            status='pending',
            expires_at__lt=now,
        ).exclude(
            approval_config__auto_approve_on_timeout=True
        )

        expired_count = expired_no_auto.update(status='expired')
        if expired_count > 0:
            logger.info(f"Marked {expired_count} orchestration gates as expired")

    def _handle_approve(
        self,
        attention_item,
        user,
        feedback: str,
        extra_data: Dict[str, Any]
    ):
        """Handle approve action from Mission Control."""
        from core.services.mission_control_executor import ExecutionResult, ActionResult
        from core.models_orchestration import OrchestrationApprovalGate

        try:
            payload = attention_item.payload or {}
            orchestration_id = payload.get('orchestration_id')

            if not orchestration_id:
                return ExecutionResult(
                    action_id='approve_orchestration_step',
                    status=ActionResult.FAILED,
                    message='No orchestration ID in payload'
                )

            # Find the approval gate
            gate = OrchestrationApprovalGate.objects.filter(
                attention_item_id=attention_item.id,
                status='pending'
            ).first()

            if not gate:
                return ExecutionResult(
                    action_id='approve_orchestration_step',
                    status=ActionResult.FAILED,
                    message='Approval gate not found or already processed'
                )

            # Approve the gate
            gate.approve(user, feedback)

            # Resume the execution
            from core.services.orchestration_engine import orchestration_engine
            orchestration_engine.resume_execution(orchestration_id)

            return ExecutionResult(
                action_id='approve_orchestration_step',
                status=ActionResult.SUCCESS,
                message=f'Step approved and workflow resumed',
                data={'orchestration_id': orchestration_id}
            )

        except Exception as e:
            logger.error(f"Failed to approve orchestration step: {e}", exc_info=True)
            return ExecutionResult(
                action_id='approve_orchestration_step',
                status=ActionResult.FAILED,
                message=str(e)
            )

    def _handle_reject(
        self,
        attention_item,
        user,
        feedback: str,
        extra_data: Dict[str, Any]
    ):
        """Handle reject action from Mission Control."""
        from core.services.mission_control_executor import ExecutionResult, ActionResult
        from core.models_orchestration import OrchestrationApprovalGate, OrchestrationExecution

        try:
            payload = attention_item.payload or {}
            orchestration_id = payload.get('orchestration_id')

            if not orchestration_id:
                return ExecutionResult(
                    action_id='reject_orchestration_step',
                    status=ActionResult.FAILED,
                    message='No orchestration ID in payload'
                )

            # Find the approval gate
            gate = OrchestrationApprovalGate.objects.filter(
                attention_item_id=attention_item.id,
                status='pending'
            ).first()

            if gate:
                gate.reject(user, feedback)

            # Fail the execution
            execution = OrchestrationExecution.objects.get(id=orchestration_id)
            execution.mark_failed(
                f'Rejected by {user.username}: {feedback or "No reason given"}',
                payload.get('step_number')
            )

            return ExecutionResult(
                action_id='reject_orchestration_step',
                status=ActionResult.SUCCESS,
                message='Step rejected and workflow failed',
                data={'orchestration_id': orchestration_id}
            )

        except Exception as e:
            logger.error(f"Failed to reject orchestration step: {e}", exc_info=True)
            return ExecutionResult(
                action_id='reject_orchestration_step',
                status=ActionResult.FAILED,
                message=str(e)
            )

    def _handle_modify(
        self,
        attention_item,
        user,
        feedback: str,
        extra_data: Dict[str, Any]
    ):
        """Handle modify action - approve with changes."""
        from core.services.mission_control_executor import ExecutionResult, ActionResult
        from core.models_orchestration import OrchestrationApprovalGate

        try:
            payload = attention_item.payload or {}
            orchestration_id = payload.get('orchestration_id')
            modifications = extra_data.get('modifications', {})

            if not orchestration_id:
                return ExecutionResult(
                    action_id='modify_orchestration_step',
                    status=ActionResult.FAILED,
                    message='No orchestration ID in payload'
                )

            # Find the approval gate
            gate = OrchestrationApprovalGate.objects.filter(
                attention_item_id=attention_item.id,
                status='pending'
            ).first()

            if gate:
                gate.modify(user, modifications, feedback)

            # Resume with modifications
            from core.services.orchestration_engine import orchestration_engine
            orchestration_engine.resume_execution(orchestration_id, modifications)

            return ExecutionResult(
                action_id='modify_orchestration_step',
                status=ActionResult.SUCCESS,
                message='Step modified and workflow resumed',
                data={
                    'orchestration_id': orchestration_id,
                    'modifications': modifications
                }
            )

        except Exception as e:
            logger.error(f"Failed to modify orchestration step: {e}", exc_info=True)
            return ExecutionResult(
                action_id='modify_orchestration_step',
                status=ActionResult.FAILED,
                message=str(e)
            )


# Singleton instance
approval_service = OrchestrationApprovalService()
