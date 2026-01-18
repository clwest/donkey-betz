"""
Orchestration Step Executor - Agent Execution Service
======================================================

Session 764: Executes individual workflow steps by routing to agents
and capturing outputs, costs, and timing.

Session 767: Added timeout enforcement using concurrent.futures.

Uses the existing AgentRouter for agent execution.
"""

import logging
import concurrent.futures
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

        # Session 768: Emit step started event
        from core.services.orchestration_events import emit_step_started
        emit_step_started(execution, step)

        try:
            # Build the task description from step config
            task = self._build_task(step, context)

            # Set up timeout (Session 767: Now actually enforced)
            timeout = step.timeout_seconds or 300

            # Get user for router
            user = execution.triggered_by

            # Execute via agent router
            logger.info(
                f"Executing step {step.order} ({step.agent}): {task[:100]}..."
            )
            logger.info(f"Step timeout: {timeout} seconds")

            # Build context for the agent (user and timeout go in context, not as separate params)
            agent_context = {
                'orchestration_id': str(execution.id),
                'step_number': step.order,
                'workflow_name': execution.workflow.name,
                'timeout_seconds': timeout,
                **context.get('input', {}),
            }

            # Add user info to context if available
            if user:
                agent_context['user_id'] = user.id if hasattr(user, 'id') else None
                agent_context['username'] = user.username if hasattr(user, 'username') else str(user)

            # Session 769: Pre-gather context BEFORE starting the timeout
            # This fixes the race condition where context gathering takes too long
            # and the step times out before the agent even starts executing
            logger.info(f"Step {step.order}: Pre-gathering context for {step.agent}...")
            context_start = timezone.now()
            pre_gathered_context = self.router.gather_context(
                agent_name=step.agent,
                task=task,
                context=agent_context,
            )
            context_time = (timezone.now() - context_start).total_seconds()
            logger.info(f"Step {step.order}: Context gathered in {context_time:.1f}s")

            # Session 767: Execute with timeout enforcement
            # Now the timeout only applies to agent execution, not context gathering
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            try:
                future = executor.submit(
                    self.router.route,
                    agent_name=step.agent,
                    task=task,
                    context=agent_context,
                    pre_gathered_context=pre_gathered_context,
                )
                try:
                    result = future.result(timeout=timeout)
                except concurrent.futures.TimeoutError:
                    # Timeout occurred - shutdown immediately without waiting
                    logger.warning(f"Step {step.order} timeout - shutting down executor without waiting")
                    executor.shutdown(wait=False, cancel_futures=True)
                    raise TimeoutError(f"Agent {step.agent} timed out after {timeout} seconds")
            finally:
                # Normal completion - wait for clean shutdown
                if not future.done():
                    executor.shutdown(wait=False, cancel_futures=True)
                else:
                    executor.shutdown(wait=False)

            # Extract output and cost from result
            if hasattr(result, 'to_dict'):
                output = result.to_dict()
            elif isinstance(result, dict):
                output = result
            else:
                output = {'result': str(result)}

            # Get cost and tokens from agent if available
            cost = Decimal('0.0000')
            tokens = 0
            # Session 769: Track external API costs
            external_cost = Decimal('0.0000')
            external_breakdown = {}

            if hasattr(result, 'cost'):
                cost = Decimal(str(result.cost))
            if hasattr(result, 'tokens_used'):
                tokens = result.tokens_used or 0

            # Also check dict format
            if isinstance(result, dict):
                if not cost:
                    cost = Decimal(str(result.get('cost', 0)))
                # Session 769: Check both 'tokens_used' and 'tokens' fields
                if not tokens:
                    tokens = result.get('tokens_used') or result.get('tokens') or 0

                # Session 769: Extract external API costs from agent results
                # Agents return cost_breakdown with keys like 'elevenlabs_tts', 'stability_ai', etc.
                if 'total_external_cost' in result:
                    external_cost = Decimal(str(result['total_external_cost']))
                if 'cost_breakdown' in result:
                    cost_data = result['cost_breakdown']
                    # Extract external costs (non-LLM)
                    for key in ['elevenlabs_tts', 'stability_ai', 'runway_ml', 'trained_voice']:
                        if key in cost_data:
                            val = cost_data[key]
                            external_breakdown[key] = float(val) if val else 0
                            if not external_cost:
                                external_cost += Decimal(str(val)) if val else Decimal('0')

            # Also check object attributes for external costs
            if hasattr(result, 'total_external_cost') and result.total_external_cost:
                external_cost = Decimal(str(result.total_external_cost))
            if hasattr(result, 'cost_breakdown') and result.cost_breakdown:
                for key in ['elevenlabs_tts', 'stability_ai', 'runway_ml', 'trained_voice']:
                    if key in result.cost_breakdown:
                        external_breakdown[key] = float(result.cost_breakdown[key])

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
            # Session 769: Include external costs
            step_exec.mark_completed(
                output, cost, tokens,
                external_cost=external_cost if external_cost else None,
                external_breakdown=external_breakdown if external_breakdown else None
            )

            logger.info(
                f"Step {step.order} completed successfully. "
                f"Cost: ${cost}, Tokens: {tokens}, "
                f"External: ${external_cost} {external_breakdown if external_breakdown else ''}"
            )

            # Session 768: Emit step completed event
            from core.services.orchestration_events import emit_step_completed
            emit_step_completed(execution, step, float(cost), tokens)

            return {
                'success': True,
                'output': output,
                'cost': cost,
                'tokens': tokens,
                # Session 769: Include external costs in return
                'external_cost': external_cost,
                'external_breakdown': external_breakdown,
            }

        except TimeoutError as e:
            error_msg = f"Step timed out after {step.timeout_seconds}s"
            step_exec.mark_failed(error_msg)
            logger.warning(f"Step {step.order} timed out: {e}")

            # Session 768: Emit step failed event
            from core.services.orchestration_events import emit_step_failed
            emit_step_failed(execution, step, error_msg)

            return {
                'success': False,
                'error': error_msg,
            }

        except Exception as e:
            error_msg = str(e)
            step_exec.mark_failed(error_msg)
            logger.error(f"Step {step.order} failed: {e}", exc_info=True)

            # Session 768: Emit step failed event
            from core.services.orchestration_events import emit_step_failed
            emit_step_failed(execution, step, error_msg)

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
        # Session 767: Build task with full context from config (description is truncated)
        config = step.config or {}

        # Check for dream context (from dream_execution_pipeline)
        dream_ctx = config.get('dream_context', {})
        if dream_ctx:
            task_parts = [step.name.split(': ', 1)[-1] if ': ' in step.name else step.description.split('\n')[0]]
            task_parts.append("")
            task_parts.append("Context from dream:")
            task_parts.append(f"- Title: {dream_ctx.get('title', 'N/A')}")
            task_parts.append(f"- Content: {dream_ctx.get('content', 'N/A')}")
            task_parts.append(f"- Type: {dream_ctx.get('type', 'N/A')}")
            return '\n'.join(task_parts)

        # Check for hivemind context (from hivemind_execution_pipeline)
        hivemind_ctx = config.get('hivemind_context', {})
        if hivemind_ctx:
            task_parts = [step.name.split(': ', 1)[-1] if ': ' in step.name else step.description.split('\n')[0]]
            task_parts.append("")
            task_parts.append("Context from HiveMind Session:")
            task_parts.append(f"- Question: {hivemind_ctx.get('question', 'N/A')}")
            task_parts.append(f"- Synthesis: {hivemind_ctx.get('synthesis', 'N/A')}")
            task_parts.append(f"- Mode: {hivemind_ctx.get('mode', 'N/A')}")
            return '\n'.join(task_parts)

        # Get template from step config or fall back to description
        template = config.get('prompt_template', step.description)

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
