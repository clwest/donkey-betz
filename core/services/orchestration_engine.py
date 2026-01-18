"""
Orchestration Engine - Multi-Agent Workflow Coordinator
========================================================

Session 764: Central coordinator for workflow execution with:
- Sequential/parallel/dependency-based step execution
- Checkpoint and resume capability
- Human-in-the-loop approval gates
- Cost tracking and budget enforcement
- Retry logic with configurable limits

Usage:
    from core.services.orchestration_engine import orchestration_engine

    # Execute a workflow
    execution = orchestration_engine.execute_workflow(
        workflow=workflow,
        user=request.user,
        input_data={'topic': 'AI trends'}
    )

    # Resume from checkpoint
    orchestration_engine.resume_execution(execution_id)

    # Check status
    status = orchestration_engine.get_execution_status(execution_id)
"""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


class OrchestrationEngine:
    """
    Central coordinator for multi-agent workflow execution.

    Manages the lifecycle of workflow executions including:
    - Step sequencing (sequential, parallel, dependency-based)
    - Checkpointing after each step
    - Approval gate pauses
    - Error handling and retries
    - Cost aggregation
    """

    def __init__(self):
        self._step_executor = None
        self._checkpoint_manager = None
        self._dependency_resolver = None
        self._approval_service = None

    @property
    def step_executor(self):
        """Lazy-load step executor."""
        if self._step_executor is None:
            from core.services.orchestration_step_executor import step_executor
            self._step_executor = step_executor
        return self._step_executor

    @property
    def checkpoint_manager(self):
        """Lazy-load checkpoint manager."""
        if self._checkpoint_manager is None:
            from core.services.orchestration_checkpoint import checkpoint_manager
            self._checkpoint_manager = checkpoint_manager
        return self._checkpoint_manager

    @property
    def dependency_resolver(self):
        """Lazy-load dependency resolver."""
        if self._dependency_resolver is None:
            from core.services.orchestration_dependencies import dependency_resolver
            self._dependency_resolver = dependency_resolver
        return self._dependency_resolver

    @property
    def approval_service(self):
        """Lazy-load approval service."""
        if self._approval_service is None:
            from core.services.orchestration_approval import approval_service
            self._approval_service = approval_service
        return self._approval_service

    def execute_workflow(
        self,
        workflow,
        user,
        input_data: Dict[str, Any] = None,
        async_mode: bool = False
    ):
        """
        Start executing a workflow.

        Args:
            workflow: CustomWorkflow instance
            user: User triggering the execution
            input_data: Initial data to pass to the workflow
            async_mode: If True, return immediately and run in background

        Returns:
            OrchestrationExecution instance
        """
        from core.models_orchestration import OrchestrationExecution

        # Create execution record
        # Note: timeout_at is set when execution actually starts, not at creation time
        # This prevents issues with queued async executions timing out before they start
        execution = OrchestrationExecution.objects.create(
            workflow=workflow,
            triggered_by=user,
            input_data=input_data or {},
            status='pending',
            total_steps=workflow.steps.count(),
            timeout_at=None  # Session 767: Set at start time, not creation time
        )

        logger.info(
            f"Created orchestration execution {execution.id} for workflow '{workflow.name}'"
        )

        if async_mode:
            # Queue for background processing
            from core.tasks import execute_orchestration_async
            execute_orchestration_async.delay(str(execution.id))
            return execution

        # Execute synchronously
        return self._execute(execution)

    def resume_execution(self, execution_id: str, modifications: Dict[str, Any] = None):
        """
        Resume a paused or failed execution.

        Args:
            execution_id: ID of the execution to resume
            modifications: Optional data modifications from approval

        Returns:
            OrchestrationExecution instance after resume attempt
        """
        from core.models_orchestration import OrchestrationExecution

        try:
            execution = OrchestrationExecution.objects.get(id=execution_id)
        except OrchestrationExecution.DoesNotExist:
            logger.error(f"Execution not found: {execution_id}")
            raise ValueError(f"Execution not found: {execution_id}")

        if execution.status not in ('paused', 'failed'):
            logger.warning(f"Cannot resume execution {execution_id} with status: {execution.status}")
            return execution

        # Apply any modifications from approval
        if modifications:
            checkpoint = execution.checkpoint_data or {}
            checkpoint['modifications'] = modifications
            execution.checkpoint_data = checkpoint
            execution.save(update_fields=['checkpoint_data'])

        execution.mark_running()
        logger.info(f"Resuming execution {execution_id} from step {execution.current_step}")

        return self._execute(execution)

    def cancel_execution(self, execution_id: str, reason: str = None):
        """Cancel a running or paused execution."""
        from core.models_orchestration import OrchestrationExecution

        try:
            execution = OrchestrationExecution.objects.get(id=execution_id)
        except OrchestrationExecution.DoesNotExist:
            raise ValueError(f"Execution not found: {execution_id}")

        if execution.status in ('completed', 'cancelled'):
            return execution

        execution.status = 'cancelled'
        execution.error_message = reason or 'Cancelled by user'
        execution.completed_at = timezone.now()
        execution.save()

        logger.info(f"Cancelled execution {execution_id}: {reason}")
        return execution

    def get_execution_status(self, execution_id: str) -> Dict[str, Any]:
        """Get detailed status of an execution."""
        from core.models_orchestration import OrchestrationExecution

        try:
            execution = OrchestrationExecution.objects.get(id=execution_id)
        except OrchestrationExecution.DoesNotExist:
            return {'error': 'Execution not found'}

        # Get step executions
        step_statuses = []
        for step_exec in execution.step_executions.all().order_by('step_number'):
            step_statuses.append({
                'step_number': step_exec.step_number,
                'agent_name': step_exec.agent_name,
                'status': step_exec.status,
                'duration_seconds': step_exec.duration_seconds,
                'cost': float(step_exec.cost) if step_exec.cost else 0,
                'retry_count': step_exec.retry_count,
                'error_message': step_exec.error_message,
            })

        # Check for pending approval gates
        pending_approvals = execution.approval_gates.filter(status='pending')

        return {
            'id': str(execution.id),
            'workflow_name': execution.workflow.name,
            'status': execution.status,
            'current_step': execution.current_step,
            'total_steps': execution.total_steps,
            'progress_percent': (
                round(execution.current_step / execution.total_steps * 100)
                if execution.total_steps > 0 else 0
            ),
            'total_cost': float(execution.total_cost),
            'total_tokens': execution.total_tokens,
            'error_message': execution.error_message,
            'started_at': execution.started_at.isoformat() if execution.started_at else None,
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'steps': step_statuses,
            'pending_approvals': pending_approvals.count(),
            'final_output': execution.final_output,
        }

    def _execute(self, execution) -> 'OrchestrationExecution':
        """
        Main execution loop.

        Executes steps in order based on execution_mode:
        - sequential: One step at a time
        - parallel: All independent steps at once
        - dependency: Based on depends_on_steps

        Checkpoints after each successful step.
        Pauses on approval gates.
        Retries on failure up to max_retries.
        """
        from core.models_orchestration import (
            OrchestrationExecution,
            OrchestrationStepExecution
        )

        # Session 768: Import event emission
        from core.services.orchestration_events import (
            emit_execution_started, emit_execution_completed, emit_execution_failed
        )

        workflow = execution.workflow
        execution.status = 'running'
        execution.started_at = execution.started_at or timezone.now()
        # Session 767: Set timeout_at from actual start time, not creation time
        if not execution.timeout_at:
            execution.timeout_at = timezone.now() + timedelta(seconds=workflow.timeout_seconds)
        execution.save(update_fields=['status', 'started_at', 'timeout_at'])

        # Session 768: Emit execution started event
        emit_execution_started(execution)

        try:
            # Get ordered steps
            steps = list(workflow.steps.all().order_by('order'))

            # Build execution context from input data
            context = {
                'input': execution.input_data,
                'step_outputs': execution.checkpoint_data.get('step_outputs', {}),
                'modifications': execution.checkpoint_data.get('modifications', {}),
            }

            # Determine which steps to run based on execution mode
            if workflow.execution_mode == 'parallel':
                return self._execute_parallel(execution, steps, context)
            elif workflow.execution_mode == 'dependency':
                return self._execute_dependency(execution, steps, context)
            else:
                return self._execute_sequential(execution, steps, context)

        except Exception as e:
            logger.error(f"Orchestration execution failed: {e}", exc_info=True)
            execution.mark_failed(str(e), execution.current_step)
            # Session 768: Emit execution failed event
            emit_execution_failed(execution, str(e))
            return execution

    def _execute_sequential(
        self,
        execution,
        steps: List,
        context: Dict[str, Any]
    ) -> 'OrchestrationExecution':
        """Execute steps one at a time in order."""
        from core.models_orchestration import OrchestrationStepExecution

        for step in steps:
            # Skip already completed steps (for resume)
            if step.order <= execution.current_step:
                continue

            # Check timeout
            if execution.timeout_at and timezone.now() > execution.timeout_at:
                execution.status = 'timed_out'
                execution.error_message = 'Workflow timeout exceeded'
                execution.save()
                return execution

            # Check budget
            if not self._check_budget(execution, step):
                execution.mark_failed(
                    f'Budget exceeded at step {step.order}',
                    step.order
                )
                return execution

            # Execute the step
            result = self._execute_step(execution, step, context)

            if result == 'paused':
                # Approval gate triggered
                return execution
            elif result == 'failed':
                # Check if we should pause for human review
                if execution.workflow.require_approval_on_error:
                    self.approval_service.create_error_approval_gate(
                        execution, step, execution.step_executions.filter(
                            step_number=step.order
                        ).last().error_message
                    )
                    execution.mark_paused('Step failed - waiting for human review')
                    return execution
                else:
                    return execution

            # Update context with step output
            step_exec = execution.step_executions.filter(step_number=step.order).first()
            if step_exec and step_exec.output_data:
                context['step_outputs'][str(step.order)] = step_exec.output_data

        # All steps completed
        execution.mark_completed(self._aggregate_outputs(execution))
        logger.info(f"Workflow execution {execution.id} completed successfully")
        # Session 768: Emit completion event
        from core.services.orchestration_events import emit_execution_completed
        emit_execution_completed(execution)
        return execution

    def _execute_parallel(
        self,
        execution,
        steps: List,
        context: Dict[str, Any]
    ) -> 'OrchestrationExecution':
        """Execute all independent steps in parallel."""
        import concurrent.futures

        # Group steps by dependency
        independent_steps = [s for s in steps if not s.depends_on_steps]
        dependent_steps = [s for s in steps if s.depends_on_steps]

        # Execute independent steps in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = {}
            for step in independent_steps:
                if step.order <= execution.current_step:
                    continue
                future = executor.submit(self._execute_step, execution, step, context)
                futures[future] = step

            for future in concurrent.futures.as_completed(futures):
                step = futures[future]
                result = future.result()
                if result == 'paused':
                    # Cancel remaining futures
                    for f in futures:
                        f.cancel()
                    return execution
                elif result == 'failed':
                    # Handle based on require_approval_on_error
                    if execution.workflow.require_approval_on_error:
                        for f in futures:
                            f.cancel()
                        return execution

        # Then execute dependent steps sequentially
        for step in dependent_steps:
            if step.order <= execution.current_step:
                continue

            # Check if dependencies are met
            deps = step.depends_on_steps or []
            deps_met = all(
                str(d) in context['step_outputs'] for d in deps
            )

            if not deps_met:
                execution.mark_failed(
                    f'Dependencies not met for step {step.order}',
                    step.order
                )
                return execution

            result = self._execute_step(execution, step, context)
            if result in ('paused', 'failed'):
                return execution

        execution.mark_completed(self._aggregate_outputs(execution))
        # Session 768: Emit completion event
        from core.services.orchestration_events import emit_execution_completed
        emit_execution_completed(execution)
        return execution

    def _execute_dependency(
        self,
        execution,
        steps: List,
        context: Dict[str, Any]
    ) -> 'OrchestrationExecution':
        """Execute steps based on explicit dependencies."""
        # Build dependency graph
        ready_steps = self.dependency_resolver.get_ready_steps(
            steps, context['step_outputs']
        )

        while ready_steps:
            for step in ready_steps:
                if step.order <= execution.current_step:
                    continue

                result = self._execute_step(execution, step, context)

                if result == 'paused':
                    return execution
                elif result == 'failed':
                    if execution.workflow.require_approval_on_error:
                        return execution
                    # Check if this blocks other steps
                    blocked = self.dependency_resolver.get_blocked_steps(step, steps)
                    for blocked_step in blocked:
                        self._skip_step(execution, blocked_step, 'Dependency failed')

                # Update context
                step_exec = execution.step_executions.filter(step_number=step.order).first()
                if step_exec and step_exec.output_data:
                    context['step_outputs'][str(step.order)] = step_exec.output_data

            # Get next batch of ready steps
            ready_steps = self.dependency_resolver.get_ready_steps(
                steps, context['step_outputs']
            )

        execution.mark_completed(self._aggregate_outputs(execution))
        # Session 768: Emit completion event
        from core.services.orchestration_events import emit_execution_completed
        emit_execution_completed(execution)
        return execution

    def _execute_step(
        self,
        execution,
        step,
        context: Dict[str, Any]
    ) -> str:
        """
        Execute a single step.

        Returns:
            'success', 'paused', or 'failed'
        """
        from core.models_orchestration import OrchestrationStepExecution

        # Check if step requires approval BEFORE execution
        if step.requires_approval:
            # Check if already approved
            existing_gate = execution.approval_gates.filter(
                step_execution__step_number=step.order,
                status__in=['approved', 'modified', 'auto_approved']
            ).first()

            if not existing_gate:
                # Create pre-execution approval gate
                step_exec = OrchestrationStepExecution.objects.create(
                    orchestration=execution,
                    workflow_step=step,
                    step_number=step.order,
                    agent_name=step.agent,
                    status='waiting_approval',
                    input_data=self._build_step_input(step, context)
                )

                self.approval_service.create_approval_gate(
                    execution, step, step_exec
                )
                execution.mark_paused(f'Waiting for approval at step {step.order}')
                return 'paused'

        # Execute the step
        max_retries = step.retry_count or execution.workflow.max_retries

        for attempt in range(max_retries + 1):
            result = self.step_executor.execute(
                execution=execution,
                step=step,
                context=context,
                attempt=attempt
            )

            if result['success']:
                # Checkpoint after success
                execution.save_checkpoint(
                    step.order,
                    result.get('output', {}),
                    context
                )

                # Add cost
                cost = Decimal(str(result.get('cost', 0)))
                tokens = result.get('tokens', 0)
                # Session 769: Track external costs alongside LLM costs
                external_cost = result.get('external_cost')
                if external_cost:
                    external_cost = Decimal(str(external_cost))
                external_breakdown = result.get('external_breakdown')
                execution.add_cost(
                    cost, tokens,
                    external_cost=external_cost,
                    external_breakdown=external_breakdown
                )

                return 'success'

            if attempt < max_retries:
                logger.warning(
                    f"Step {step.order} failed (attempt {attempt + 1}/{max_retries + 1}): "
                    f"{result.get('error')}"
                )
                continue

        # All retries exhausted - check if rollback step is defined
        if step.rollback_step:
            logger.info(f"Step {step.order} failed, executing rollback step {step.rollback_step}")
            rollback_result = self._execute_rollback(execution, step, context)
            if rollback_result == 'success':
                logger.info(f"Rollback step {step.rollback_step} completed successfully")
            else:
                logger.warning(f"Rollback step {step.rollback_step} also failed")

        execution.mark_failed(
            result.get('error', 'Step execution failed'),
            step.order
        )
        return 'failed'

    def _build_step_input(self, step, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build input data for a step based on context and dependencies."""
        input_data = {
            'workflow_input': context.get('input', {}),
            'step_config': step.config or {},
        }

        # Include outputs from dependent steps
        deps = step.depends_on_steps or []
        for dep in deps:
            dep_output = context['step_outputs'].get(str(dep))
            if dep_output:
                input_data[f'step_{dep}_output'] = dep_output

        # Include any modifications from approval
        mods = context.get('modifications', {})
        if mods:
            input_data['modifications'] = mods

        return input_data

    def _check_budget(self, execution, step) -> bool:
        """Check if we have budget for this step."""
        workflow = execution.workflow

        # Check workflow budget
        if workflow.cost_budget:
            if execution.total_cost >= workflow.cost_budget:
                return False

        # Check step budget
        if step.cost_limit:
            remaining = workflow.cost_budget - execution.total_cost if workflow.cost_budget else None
            if remaining and step.cost_limit > remaining:
                return False

        return True

    def _skip_step(self, execution, step, reason: str):
        """Mark a step as skipped."""
        from core.models_orchestration import OrchestrationStepExecution

        OrchestrationStepExecution.objects.create(
            orchestration=execution,
            workflow_step=step,
            step_number=step.order,
            agent_name=step.agent,
            status='skipped',
            error_message=reason
        )

    def _execute_rollback(
        self,
        execution,
        failed_step,
        context: Dict[str, Any]
    ) -> str:
        """
        Execute a rollback step when the main step fails.

        Args:
            execution: OrchestrationExecution instance
            failed_step: The step that failed
            context: Current execution context

        Returns:
            'success' or 'failed'
        """
        from core.models_orchestration import OrchestrationStepExecution

        workflow = execution.workflow
        rollback_step_order = failed_step.rollback_step

        # Find the rollback step definition
        rollback_step = workflow.steps.filter(order=rollback_step_order).first()
        if not rollback_step:
            logger.error(f"Rollback step {rollback_step_order} not found in workflow")
            return 'failed'

        # Add failure context for the rollback step
        rollback_context = {
            **context,
            'rollback_info': {
                'failed_step_order': failed_step.order,
                'failed_step_name': failed_step.name,
                'failed_step_agent': failed_step.agent,
                'error_message': context.get('last_error', 'Unknown error'),
            }
        }

        try:
            # Execute the rollback step (no retries for rollback)
            result = self.step_executor.execute(
                execution=execution,
                step=rollback_step,
                context=rollback_context,
                attempt=0
            )

            if result['success']:
                # Mark the step execution as rolled_back
                step_exec = execution.step_executions.filter(
                    step_number=failed_step.order
                ).last()
                if step_exec:
                    step_exec.status = 'rolled_back'
                    step_exec.save(update_fields=['status', 'updated_at'])

                return 'success'
            else:
                return 'failed'

        except Exception as e:
            logger.error(f"Rollback step execution failed: {e}", exc_info=True)
            return 'failed'

    def _aggregate_outputs(self, execution) -> Dict[str, Any]:
        """Aggregate outputs from all steps into final output."""
        outputs = {}
        total_tokens = 0

        for step_exec in execution.step_executions.filter(status='completed'):
            if step_exec.output_data:
                outputs[step_exec.agent_name] = step_exec.output_data
                # Session 769: Sum tokens from step output_data.tokens_used
                step_tokens = step_exec.output_data.get('tokens_used') or step_exec.tokens_used or 0
                total_tokens += step_tokens

        # Session 769: Include comprehensive cost breakdown
        return {
            'step_outputs': outputs,
            'total_cost': float(execution.total_cost),
            'total_tokens': total_tokens,
            # Session 769: External API costs
            'total_external_cost': float(execution.total_external_cost or 0),
            'external_cost_breakdown': execution.external_cost_breakdown or {},
            # Combined total
            'total_combined_cost': float(
                (execution.total_cost or Decimal('0')) +
                (execution.total_external_cost or Decimal('0'))
            ),
            'completed_at': timezone.now().isoformat(),
        }


# Singleton instance
orchestration_engine = OrchestrationEngine()
