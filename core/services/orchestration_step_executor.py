"""
Orchestration Step Executor - Agent Execution Service
======================================================

Session 764: Executes individual workflow steps by routing to agents
and capturing outputs, costs, and timing.

Uses the existing AgentRouter for agent execution.
"""

import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from django.utils import timezone

logger = logging.getLogger(__name__)


class OrchestrationStepExecutor:
    """
    Executes individual steps within an orchestration workflow.

    Wraps the AgentRouter to:
    - Track execution timing
    - Capture agent costs
    - Store step outputs
    - Handle timeouts
    """

    def __init__(self):
        self._router = None

    @property
    def router(self):
        """Lazy-load agent router."""
        if self._router is None:
            from core.agent_router import AgentRouter
            self._router = AgentRouter()
        return self._router

    def execute(
        self,
        execution,
        step,
        context: Dict[str, Any],
        attempt: int = 0
    ) -> Dict[str, Any]:
        """
        Execute a single step.

        Args:
            execution: OrchestrationExecution instance
            step: CustomWorkflowStep instance
            context: Execution context with inputs and previous outputs
            attempt: Current retry attempt number

        Returns:
            Dict with keys: success, output, cost, tokens, error
        """
        from core.models_orchestration import OrchestrationStepExecution

        # Create or get step execution record
        step_exec, created = OrchestrationStepExecution.objects.get_or_create(
            orchestration=execution,
            step_number=step.order,
            defaults={
                'workflow_step': step,
                'agent_name': step.agent,
                'status': 'pending',
                'input_data': self._build_input(step, context),
                'retry_count': attempt,
            }
        )

        if not created:
            step_exec.retry_count = attempt
            step_exec.save(update_fields=['retry_count'])

        step_exec.mark_running()

        try:
            # Build the task description from step config
            task = self._build_task(step, context)

            # Set up timeout
            timeout = step.timeout_seconds or 300

            # Get user for router
            user = execution.triggered_by

            # Execute via agent router
            logger.info(
                f"Executing step {step.order} ({step.agent}): {task[:100]}..."
            )

            result = self.router.route(
                agent_name=step.agent,
                task=task,
                context={
                    'orchestration_id': str(execution.id),
                    'step_number': step.order,
                    'workflow_name': execution.workflow.name,
                    **context.get('input', {}),
                },
                user=user,
                timeout=timeout
            )

            # Extract output and cost from result
            if hasattr(result, 'to_dict'):
                output = result.to_dict()
            elif isinstance(result, dict):
                output = result
            else:
                output = {'result': str(result)}

            # Get cost from agent if available
            cost = Decimal('0.0000')
            tokens = 0

            if hasattr(result, 'cost'):
                cost = Decimal(str(result.cost))
            elif isinstance(result, dict):
                cost = Decimal(str(result.get('cost', 0)))
                tokens = result.get('tokens', 0)

            # Session 765: Capture execution_id for intelligence linking
            execution_id = None
            if hasattr(result, 'execution_id') and result.execution_id:
                execution_id = result.execution_id
                step_exec.execution_id = execution_id
                step_exec.save(update_fields=['execution_id'])
                logger.info(f"Step {step.order} linked to execution {execution_id}")
            elif isinstance(result, dict) and result.get('execution_id'):
                execution_id = result.get('execution_id')
                step_exec.execution_id = execution_id
                step_exec.save(update_fields=['execution_id'])

            # Mark step as completed
            step_exec.mark_completed(output, cost, tokens)

            logger.info(
                f"Step {step.order} completed successfully. "
                f"Cost: ${cost}, Tokens: {tokens}"
            )

            return {
                'success': True,
                'output': output,
                'cost': cost,
                'tokens': tokens,
            }

        except TimeoutError as e:
            error_msg = f"Step timed out after {step.timeout_seconds}s"
            step_exec.mark_failed(error_msg)
            logger.warning(f"Step {step.order} timed out: {e}")

            return {
                'success': False,
                'error': error_msg,
            }

        except Exception as e:
            error_msg = str(e)
            step_exec.mark_failed(error_msg)
            logger.error(f"Step {step.order} failed: {e}", exc_info=True)

            return {
                'success': False,
                'error': error_msg,
            }

    def _build_input(self, step, context: Dict[str, Any]) -> Dict[str, Any]:
        """Build input data for the step."""
        input_data = {
            'step_config': step.config or {},
            'workflow_input': context.get('input', {}),
        }

        # Include outputs from dependencies
        deps = step.depends_on_steps or []
        step_outputs = context.get('step_outputs', {})

        for dep in deps:
            dep_key = str(dep)
            if dep_key in step_outputs:
                input_data[f'step_{dep}_output'] = step_outputs[dep_key]

        # Include previous step output for sequential execution
        prev_step = step.order - 1
        if str(prev_step) in step_outputs:
            input_data['previous_output'] = step_outputs[str(prev_step)]

        return input_data

    def _build_task(self, step, context: Dict[str, Any]) -> str:
        """Build the task description for the agent."""
        # Get template from step config
        template = step.config.get('prompt_template', step.description)

        if not template:
            # Default task based on step name
            template = f"Execute {step.name}: {step.description or 'No description'}"

        # Substitute variables from context
        task = template

        # Replace input variables
        for key, value in context.get('input', {}).items():
            placeholder = f'{{{key}}}'
            if placeholder in task:
                task = task.replace(placeholder, str(value))

        # Replace step output variables
        for step_num, output in context.get('step_outputs', {}).items():
            if isinstance(output, dict):
                for key, value in output.items():
                    placeholder = f'{{step_{step_num}.{key}}}'
                    if placeholder in task:
                        task = task.replace(placeholder, str(value))
            placeholder = f'{{step_{step_num}}}'
            if placeholder in task:
                task = task.replace(placeholder, str(output))

        return task


# Singleton instance
step_executor = OrchestrationStepExecutor()
