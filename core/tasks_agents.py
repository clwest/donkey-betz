"""
Celery tasks for agent execution and orchestration.

Session 728: Migrated from agents/tasks.py to core/tasks_agents.py
"""

import logging
import json
import os  # noqa: F401
import time  # noqa: F401
import traceback
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union  # noqa: F401

from celery import shared_task, Task
from celery.exceptions import SoftTimeLimitExceeded  # noqa: F401
from django.db import transaction  # noqa: F401
from django.db.models import F, Count, Q  # noqa: F401
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from core.api_helpers import smart_truncate  # noqa: F401

from core.models.agents_registry import (
    AgentExecution,
    AgentStatus,
    AgentOrchestration,
    UnifiedAgentTemplate
)
from content.ai_providers import AIProviderManager

logger = logging.getLogger(__name__)
from core.tasks import (  # noqa: F401 — private helpers from tasks.py
    _apply_task_routing_override,
    _circuit_breaker_check,
    _circuit_breaker_record_timeout,
    _circuit_breaker_release,
    _extract_agent_output_content,
    _format_metrics_for_audit,
    _gather_live_system_metrics,
    _get_agent_class,
    _get_next_task_for_agent,
    _get_workspace_for_skin_layer,
    _is_media_task_blocked,
    _preflight_check_agent_data,
    _record_timeout_signature,
    _run_agent_warmup,
    _summarize_diff,
    _summarize_params,
    _upsert_insight,
)



class AgentExecutionTask(Task):
    """Custom Task class for agent execution with proper error handling"""

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        execution_id = kwargs.get('execution_id')
        if execution_id:
            try:
                execution = AgentExecution.objects.get(execution_id=execution_id)
                execution.status = AgentStatus.FAILED
                execution.error_message = str(exc)
                execution.error_traceback = str(einfo)
                execution.completed_at = timezone.now()
                execution.save()

                # Send WebSocket notification
                send_execution_update(execution_id, {
                    'status': 'failed',
                    'error': str(exc)
                })
            except AgentExecution.DoesNotExist:
                logger.error(f"Execution {execution_id} not found during failure handling")


def send_execution_update(execution_id: str, update_data: Dict[str, Any]):
    """Send real-time updates via WebSocket"""
    try:
        channel_layer = get_channel_layer()
        if channel_layer:
            async_to_sync(channel_layer.group_send)(
                f"agent_execution_{execution_id}",
                {
                    "type": "execution_update",
                    "execution_id": execution_id,
                    "data": update_data,
                    "timestamp": timezone.now().isoformat()
                }
            )
    except Exception as e:
        logger.error(f"Failed to send WebSocket update: {e}")


@shared_task(bind=True, base=AgentExecutionTask, max_retries=3)
def execute_agent(self, execution_id: str, **kwargs):
    """
    Main task for executing an agent.

    Args:
        execution_id: The unique ID of the AgentExecution instance
        **kwargs: Additional parameters for execution
    """
    try:
        # Get the execution instance
        execution = AgentExecution.objects.get(execution_id=execution_id)

        # Update status to running
        execution.status = AgentStatus.RUNNING
        execution.started_at = timezone.now()
        execution.current_step = "Initializing agent execution"
        execution.progress_percentage = 10
        execution.save()

        # Send WebSocket update
        send_execution_update(execution_id, {
            'status': 'running',
            'progress': 10,
            'current_step': 'Initializing agent execution'
        })

        # Get the agent template
        agent_template = execution.template

        # Initialize AI provider
        ai_manager = AIProviderManager()
        provider = ai_manager.get_provider(agent_template.llm_provider)

        if not provider:
            raise ValueError(f"AI provider {agent_template.llm_provider} not configured")

        # Update progress
        execution.current_step = "Preparing agent context"
        execution.progress_percentage = 30
        execution.save()

        send_execution_update(execution_id, {
            'progress': 30,
            'current_step': 'Preparing agent context'
        })

        # Build the execution context
        context = {
            'task_description': execution.task_description,
            'task_type': execution.task_type,
            'input_data': execution.input_data,
            'context': execution.context,
            'agent_capabilities': agent_template.capabilities,
            'agent_tools': agent_template.required_tools,
        }

        # Prepare GPT-5-mini compatible prompt with platform awareness
        from core.services.platform_integration import inject_platform_tools_prompt

        base_prompt = agent_template.system_prompt if agent_template.system_prompt else "Business specialist."
        platform_tools = inject_platform_tools_prompt()

        # Combine base prompt with platform integration
        system_prompt = f"{base_prompt}\n\n{platform_tools}"

        # Extract key info from input data for simple prompt
        opportunity = execution.input_data.get('opportunity', 'business opportunity')
        step = execution.input_data.get('step', execution.task_description)

        user_prompt = f"Please create a detailed action plan for this business task: {step}. This task is part of developing the {opportunity} opportunity. You should recommend only our internal platform tools and services. Write your response using complete sentences and clear explanations. Include specific steps, internal tools to use, and expected outcomes."

        # Update progress
        execution.current_step = "Processing with AI model"
        execution.progress_percentage = 50
        execution.save()

        send_execution_update(execution_id, {
            'progress': 50,
            'current_step': 'Processing with AI model'
        })

        # Execute the AI call with advisor consultation
        start_time = timezone.now()

        # Check if we should consult advisors (for important decisions)
        consult_advisors = (
            agent_template.specialization and
            any(domain in agent_template.specialization.lower()
                for domain in ['sports', 'crypto', 'option', 'trading', 'real', 'estate', 'market'])
        )

        collaborative_decision = None
        if consult_advisors:
            try:
                from intelligence.orchestration.agent_advisor_bridge import (
                    agent_advisor_bridge, AgentAdvisorContext
                )

                # Create context for collaboration
                advisor_context = AgentAdvisorContext(
                    agent_id=str(agent_template.id),
                    agent_name=agent_template.name,
                    task_description=execution.task_description,
                    domain=agent_template.specialization or 'general',
                    input_data=execution.input_data or {},
                    required_confidence=0.7,
                    max_advisors=3,
                    use_ml_enhancement=True
                )

                # Get collaborative decision
                collaborative_decision = agent_advisor_bridge.orchestrate_collaborative_decision(
                    advisor_context
                )

                # Enhance the prompt with advisor insights
                if collaborative_decision and collaborative_decision.confidence > 0.6:
                    advisor_insights = "\n\nAdvisor Insights:\n"
                    for reason in collaborative_decision.reasoning[:3]:
                        advisor_insights += f"- {reason}\n"

                    user_prompt = user_prompt + advisor_insights

                    # Log the collaboration
                    logger.info(f"Agent {agent_template.name} consulted {len(collaborative_decision.participating_advisors)} advisors")

            except Exception as e:
                logger.warning(f"Advisor consultation failed: {e}, proceeding without advisors")

        try:
            # Use the AI provider to generate response
            result = provider.generate_content(
                model=agent_template.llm_model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                config=agent_template.llm_config
            )

            # Check if generation was successful
            if not result.success:
                raise ValueError(f"Generation failed: {result.error_message}")

            # Extract the response content
            result_content = result.content

            # Calculate execution metrics
            end_time = timezone.now()
            execution_time = (end_time - start_time).total_seconds()

            # Use token usage from result
            token_usage = result.token_usage if result.token_usage else {}

            # Update execution with results
            execution.status = AgentStatus.COMPLETED
            execution.completed_at = end_time
            execution.execution_time_seconds = execution_time
            execution.result = {
                'output': result_content,
                'success': True,
                'execution_time': execution_time,
                'token_usage': token_usage
            }
            # Include collaboration data if available
            collaboration_data = {}
            if collaborative_decision:
                collaboration_data = {
                    'advisors_consulted': collaborative_decision.participating_advisors,
                    'consensus_confidence': collaborative_decision.confidence,
                    'ml_enhanced': len(collaborative_decision.ml_predictions) > 0,
                    'risk_assessment': collaborative_decision.risk_assessment,
                    'recommended_actions': collaborative_decision.recommended_actions[:3]
                }

            execution.output_data = {
                'response': result_content,
                'metadata': {
                    'model': agent_template.llm_model,
                    'provider': agent_template.llm_provider,
                    'execution_time': execution_time
                },
                'collaboration': collaboration_data
            }
            execution.llm_response = result_content
            execution.token_usage = token_usage
            execution.progress_percentage = 100
            execution.current_step = "Execution completed successfully"
            execution.save()

            # Update agent metrics
            agent_template.update_metrics(
                execution_time=execution_time,
                success=True,
                tokens=token_usage
            )

            # Send final WebSocket update
            send_execution_update(execution_id, {
                'status': 'completed',
                'progress': 100,
                'current_step': 'Execution completed successfully',
                'result': execution.result
            })

            logger.info(f"Agent execution {execution_id} completed successfully")
            return execution.result

        except Exception as ai_error:
            # Handle AI provider errors
            logger.error(f"AI provider error for execution {execution_id}: {ai_error}")

            # Try fallback provider if configured
            if agent_template.fallback_provider and agent_template.fallback_model:
                logger.info(f"Attempting fallback provider for execution {execution_id}")

                fallback_provider = ai_manager.get_provider(agent_template.fallback_provider)
                if fallback_provider:
                    try:
                        fallback_result = fallback_provider.generate_content(
                            model=agent_template.fallback_model,
                            system_prompt=system_prompt,
                            user_prompt=user_prompt,
                            config=agent_template.llm_config
                        )

                        # Process fallback response
                        if fallback_result.success:
                            result_content = fallback_result.content
                        else:
                            raise ValueError(f"Fallback generation failed: {fallback_result.error_message}")

                        execution.status = AgentStatus.COMPLETED
                        execution.completed_at = timezone.now()
                        execution.result = {
                            'output': result_content,
                            'success': True,
                            'used_fallback': True
                        }
                        execution.save()

                        send_execution_update(execution_id, {
                            'status': 'completed',
                            'progress': 100,
                            'result': execution.result
                        })

                        return execution.result

                    except Exception as fallback_error:
                        logger.error(f"Fallback provider also failed: {fallback_error}")
                        raise ai_error

            raise ai_error

    except AgentExecution.DoesNotExist:
        logger.error(f"AgentExecution with ID {execution_id} not found")
        raise

    except Exception as e:
        logger.error(f"Error executing agent {execution_id}: {e}\n{traceback.format_exc()}")

        # Update execution status
        try:
            execution = AgentExecution.objects.get(execution_id=execution_id)
            execution.status = AgentStatus.FAILED
            execution.error_message = str(e)
            execution.error_traceback = traceback.format_exc()
            execution.completed_at = timezone.now()
            execution.progress_percentage = 0
            execution.current_step = f"Execution failed: {str(e)}"
            execution.save()

            send_execution_update(execution_id, {
                'status': 'failed',
                'error': str(e),
                'progress': 0
            })

        except AgentExecution.DoesNotExist:
            pass

        # Retry the task if retries are available
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        else:
            raise


@shared_task(bind=True, max_retries=1, time_limit=60)
def execute_agent_async(self, execution_id: str):
    """
    Execute an agent asynchronously with timeout.
    This is a wrapper around execute_agent for better async control.
    """
    try:
        # Since we're already in a Celery task, just call the function directly
        # The 'self' parameter will be passed automatically by Celery
        return execute_agent(self, execution_id)
    except Exception as e:
        logger.error(f"Agent async execution failed for {execution_id}: {e}")

        # Mark execution as failed
        try:
            execution = AgentExecution.objects.get(execution_id=execution_id)
            execution.status = AgentStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            execution.save()
        except AgentExecution.DoesNotExist:
            pass

        # Retry if possible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=30)
        else:
            raise


@shared_task
def cleanup_old_executions(days_to_keep: int = 30):
    """
    Clean up old agent executions to prevent database bloat.

    Args:
        days_to_keep: Number of days to keep executions
    """
    cutoff_date = timezone.now() - timedelta(days=days_to_keep)

    # Delete old completed/failed executions
    deleted_count = AgentExecution.objects.filter(
        created_at__lt=cutoff_date,
        status__in=[AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.CANCELLED]
    ).delete()[0]

    logger.info(f"Cleaned up {deleted_count} old agent executions")
    return deleted_count


@shared_task
def check_stuck_executions():
    """
    Check for stuck executions and mark them as failed.
    """
    # Find executions that have been running for more than 1 hour
    one_hour_ago = timezone.now() - timedelta(hours=1)

    stuck_executions = AgentExecution.objects.filter(
        status=AgentStatus.RUNNING,
        started_at__lt=one_hour_ago
    )

    for execution in stuck_executions:
        execution.status = AgentStatus.FAILED
        execution.error_message = "Execution timed out after 1 hour"
        execution.completed_at = timezone.now()
        execution.save()

        send_execution_update(execution.execution_id, {
            'status': 'failed',
            'error': 'Execution timed out'
        })

        logger.warning(f"Marked execution {execution.execution_id} as failed due to timeout")

    return stuck_executions.count()


@shared_task(bind=True, max_retries=3)
def execute_orchestration(self, orchestration_id: str):
    """
    Execute an agent orchestration with multiple agents.

    Session 735: Updated to use REAL agent execution via AgentRouter.
    Each agent in the sequence is actually invoked and produces real output.

    Args:
        orchestration_id: The ID of the AgentOrchestration instance
    """
    import uuid
    from core.agent_router import AgentRouter, AgentNotFoundError

    try:
        orchestration = AgentOrchestration.objects.get(id=orchestration_id)

        logger.info(f"🚀 Starting REAL orchestration {orchestration_id}: {orchestration.name}")

        # Update orchestration status to running
        orchestration.status = AgentStatus.RUNNING
        orchestration.started_at = timezone.now()
        orchestration.save()

        # Get the prompt from workflow definition
        workflow_def = orchestration.workflow_definition or {}
        base_prompt = workflow_def.get('prompt', '')
        workflow_type = workflow_def.get('type', 'general')
        domain = workflow_def.get('domain', 'general')

        # Build a meaningful prompt if none provided
        if not base_prompt:
            base_prompt = f"Execute {workflow_type} workflow for {domain} domain. Orchestration: {orchestration.name}"

        # Session 735: Helper to normalize agent info (can be string or dict)
        def get_agent_name(agent_info):
            if isinstance(agent_info, str):
                return agent_info
            return agent_info.get('name', agent_info.get('agent', 'Unknown'))

        # Session 735: Helper to find or create a template for an agent name
        def get_or_create_template(agent_name):
            """Find template by name or create a placeholder"""
            template = UnifiedAgentTemplate.objects.filter(name=agent_name).first()
            if not template:
                template = UnifiedAgentTemplate.objects.filter(
                    name=agent_name.replace('Agent', '')
                ).first()
            if not template:
                template = UnifiedAgentTemplate.objects.create(
                    name=agent_name,
                    display_name=agent_name.replace('Agent', ' Agent'),
                    description=f"Auto-created template for {agent_name}",
                    specialization='general',
                    is_active=True
                )
            return template

        # Initialize the AgentRouter with the orchestration user
        router = AgentRouter(user=orchestration.user)

        # Track total execution time and cost
        total_execution_time_ms = 0
        total_cost = 0.0

        # Execute agents based on strategy
        if orchestration.execution_strategy == 'sequential':
            # Sequential execution - each agent builds on previous results
            previous_result = None
            accumulated_context = {
                'orchestration_id': str(orchestration_id),
                'orchestration_name': orchestration.name,
                'workflow_type': workflow_type,
                'domain': domain,
            }

            for i, agent_info in enumerate(orchestration.agent_sequence):
                agent_name = get_agent_name(agent_info)
                logger.info(f"🤖 [{i+1}/{len(orchestration.agent_sequence)}] Executing REAL agent: {agent_name}")

                # Update orchestration progress
                orchestration.current_agent_index = i
                orchestration.progress_percentage = int((i / len(orchestration.agent_sequence)) * 100)
                orchestration.save()

                # Get template for this agent
                template = get_or_create_template(agent_name)

                # Build task for this agent
                if i == 0:
                    # First agent gets the base prompt
                    task = base_prompt
                else:
                    # Subsequent agents get context from previous results
                    task = f"""Continue the {workflow_type} workflow.

Previous agent ({orchestration.agent_sequence[i-1]}) produced:
{previous_result[:2000] if previous_result else 'No previous output'}

Your task as {agent_name}: Build on the above and contribute your expertise."""

                # Session 758: Build context tracking for Integration Health observability
                from core.services.context_tracking import build_context_tracking
                context_tracking = build_context_tracking(agent_name, task)

                # Create execution record
                execution = AgentExecution.objects.create(
                    template=template,
                    user=orchestration.user,
                    parent_orchestration=orchestration,
                    execution_id=f"orch_{orchestration.id}_{i}_{uuid.uuid4().hex[:6]}",
                    task_description=task[:500],
                    context={
                        **accumulated_context,
                        'step': i + 1,
                        'total_steps': len(orchestration.agent_sequence),
                        'previous_result': previous_result[:1000] if previous_result else None,
                    },
                    input_data={
                        'task': task[:500],
                        'context_injected': context_tracking,
                    },
                    status=AgentStatus.RUNNING
                )

                # REAL AGENT EXECUTION via AgentRouter
                # Session 1108: Wall-clock timeout — prevents hung LLM calls
                # from blocking the orchestration indefinitely. Without this,
                # the only safety net is the 35-min cleanup reaper.
                _ORCH_AGENT_TIMEOUT = 600  # 10 min per agent step
                try:
                    from concurrent.futures import ThreadPoolExecutor as _OTPE, TimeoutError as _OFTimeout
                    def _orch_route():
                        from django.db import close_old_connections
                        close_old_connections()
                        try:
                            return router.route(
                                agent_name=agent_name,
                                task=task,
                                context={
                                    **accumulated_context,
                                    'previous_result': previous_result,
                                    'step': i + 1,
                                }
                            )
                        finally:
                            close_old_connections()

                    _opool = _OTPE(max_workers=1)
                    _ofuture = _opool.submit(_orch_route)
                    try:
                        agent_result = _ofuture.result(timeout=_ORCH_AGENT_TIMEOUT)
                    except _OFTimeout:
                        logger.error(
                            f"[Orchestration] WALL-CLOCK TIMEOUT: {agent_name} exceeded "
                            f"{_ORCH_AGENT_TIMEOUT}s — marking failed"
                        )
                        _record_timeout_signature(
                            agent_name=agent_name,
                            timeout_source='orchestration_wall_clock',
                            elapsed_seconds=_ORCH_AGENT_TIMEOUT,
                            execution_id=execution.id,
                        )
                        raise TimeoutError(f"{agent_name} exceeded {_ORCH_AGENT_TIMEOUT}s wall-clock timeout")
                    finally:
                        _opool.shutdown(wait=False)

                    # Extract result data - Session 735: Include cost and tokens
                    agent_cost = getattr(agent_result, 'cost', 0.0) or 0.0
                    agent_tokens = getattr(agent_result, 'tokens_used', 0) or 0

                    result_data = {
                        'success': agent_result.success,
                        'message': agent_result.message,
                        'data': agent_result.data if hasattr(agent_result, 'data') else None,
                        'execution_time_ms': agent_result.execution_time_ms,
                        'cost': agent_cost,
                        'tokens_used': agent_tokens,
                    }

                    execution.result = result_data
                    execution.status = AgentStatus.COMPLETED if agent_result.success else AgentStatus.FAILED
                    execution.completed_at = timezone.now()
                    execution.save()

                    # Track metrics - Session 735: Accumulate cost
                    total_execution_time_ms += agent_result.execution_time_ms or 0
                    total_cost += agent_cost

                    # Update accumulated context with this result
                    previous_result = agent_result.message or json.dumps(result_data)

                    logger.info(f"✅ {agent_name} completed: success={agent_result.success}, time={agent_result.execution_time_ms}ms, cost=${agent_cost:.4f}")

                except AgentNotFoundError as e:
                    # Agent not in router - log but continue
                    logger.warning(f"⚠️ Agent {agent_name} not found in router: {e}")
                    execution.result = {
                        'success': False,
                        'error': f'Agent {agent_name} not found in router',
                        'message': str(e)
                    }
                    execution.status = AgentStatus.FAILED
                    execution.save()
                    previous_result = f"Agent {agent_name} was skipped (not in router)"

                except Exception as e:
                    logger.error(f"❌ Agent {agent_name} failed: {e}")
                    execution.result = {
                        'success': False,
                        'error': str(e),
                    }
                    execution.status = AgentStatus.FAILED
                    execution.error_message = str(e)
                    execution.save()
                    previous_result = f"Agent {agent_name} failed: {str(e)[:200]}"

                # Store in intermediate results
                orchestration.intermediate_results.append({
                    'agent': agent_name,
                    'step': i + 1,
                    'result': execution.result,
                    'status': execution.status,
                })
                orchestration.save()

        elif orchestration.execution_strategy == 'parallel':
            # Parallel execution - all agents work on the same prompt independently
            from concurrent.futures import ThreadPoolExecutor, as_completed

            executions = []
            futures_map = {}

            # Create all execution records first
            for i, agent_info in enumerate(orchestration.agent_sequence):
                agent_name = get_agent_name(agent_info)
                template = get_or_create_template(agent_name)

                # Session 758: Build context tracking for Integration Health observability
                from core.services.context_tracking import build_context_tracking
                context_tracking = build_context_tracking(agent_name, base_prompt)

                execution = AgentExecution.objects.create(
                    template=template,
                    user=orchestration.user,
                    parent_orchestration=orchestration,
                    execution_id=f"orch_{orchestration.id}_{i}_{uuid.uuid4().hex[:6]}",
                    task_description=base_prompt[:500],
                    context={
                        'orchestration_id': str(orchestration_id),
                        'parallel': True,
                        'agent_name': agent_name
                    },
                    input_data={
                        'task': base_prompt[:500],
                        'context_injected': context_tracking,
                    },
                    status=AgentStatus.RUNNING
                )
                executions.append((execution, agent_name, i))

            # Execute all agents in parallel using ThreadPoolExecutor
            def execute_agent_task(execution, agent_name, task):
                try:
                    result = router.route(agent_name=agent_name, task=task, context={
                        'orchestration_id': str(orchestration_id),
                        'parallel': True,
                    })
                    return {
                        'success': result.success,
                        'message': result.message,
                        'data': result.data if hasattr(result, 'data') else None,
                        'execution_time_ms': result.execution_time_ms,
                    }
                except AgentNotFoundError:
                    return {'success': False, 'error': f'Agent {agent_name} not in router'}
                except Exception as e:
                    return {'success': False, 'error': str(e)}

            # Session 1108: Use shutdown(wait=False) + per-future timeout
            # to prevent hung agents from blocking the entire orchestration.
            _PARALLEL_AGENT_TIMEOUT = 600  # 10 min per agent
            executor = ThreadPoolExecutor(max_workers=min(4, len(executions)))
            try:
                for execution, agent_name, i in executions:
                    future = executor.submit(execute_agent_task, execution, agent_name, base_prompt)
                    futures_map[future] = (execution, agent_name, i)

                for future in as_completed(futures_map, timeout=_PARALLEL_AGENT_TIMEOUT):
                    execution, agent_name, i = futures_map[future]
                    try:
                        result_data = future.result(timeout=_PARALLEL_AGENT_TIMEOUT)
                        execution.result = result_data
                        execution.status = AgentStatus.COMPLETED if result_data.get('success') else AgentStatus.FAILED
                        execution.completed_at = timezone.now()
                        execution.save()

                        # Session 735: Track time and cost
                        total_execution_time_ms += result_data.get('execution_time_ms', 0) or 0
                        agent_cost = result_data.get('cost', 0.0) or 0.0
                        total_cost += agent_cost

                        orchestration.intermediate_results.append({
                            'agent': agent_name,
                            'result': result_data,
                            'status': execution.status,
                        })

                        logger.info(f"✅ [Parallel] {agent_name} completed, cost=${agent_cost:.4f}")

                    except Exception as e:
                        execution.result = {'success': False, 'error': str(e)}
                        execution.status = AgentStatus.FAILED
                        execution.save()
                        logger.error(f"❌ [Parallel] {agent_name} failed: {e}")

            except TimeoutError:
                # Session 1108: Some agents exceeded the parallel timeout.
                # Mark any still-running executions as failed.
                for _exec, _aname, _ in executions:
                    if _exec.status == AgentStatus.RUNNING:
                        _exec.status = AgentStatus.FAILED
                        _exec.result = {'success': False, 'error': f'{_aname} exceeded {_PARALLEL_AGENT_TIMEOUT}s timeout'}
                        _exec.completed_at = timezone.now()
                        _exec.save()
                        logger.error(f"[Orchestration] PARALLEL TIMEOUT: {_aname} exceeded {_PARALLEL_AGENT_TIMEOUT}s")
                        _record_timeout_signature(
                            agent_name=_aname,
                            timeout_source='orchestration_parallel_wall_clock',
                            elapsed_seconds=_PARALLEL_AGENT_TIMEOUT,
                            execution_id=_exec.id,
                        )
            finally:
                executor.shutdown(wait=False)

            orchestration.save()

        # Mark orchestration as completed - Session 735: Save total_cost
        orchestration.status = AgentStatus.COMPLETED
        orchestration.progress_percentage = 100
        orchestration.total_execution_time = total_execution_time_ms / 1000.0  # Convert to seconds
        orchestration.total_cost = Decimal(str(total_cost))  # Save accumulated cost
        orchestration.completed_at = timezone.now()
        orchestration.save()

        logger.info(f"🎉 Orchestration {orchestration_id} completed successfully! Time: {total_execution_time_ms}ms, Cost: ${total_cost:.4f}")

        # Send WebSocket notification
        send_execution_update(str(orchestration_id), {
            'status': 'completed',
            'message': f'Workflow {orchestration.name} completed with real agent execution',
            'total_time_ms': total_execution_time_ms,
        })

        return {
            'success': True,
            'orchestration_id': str(orchestration_id),
            'message': f'Executed {len(orchestration.agent_sequence)} REAL agents successfully',
            'total_execution_time_ms': total_execution_time_ms,
        }

    except AgentOrchestration.DoesNotExist:
        logger.error(f"Orchestration {orchestration_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error executing orchestration {orchestration_id}: {e}", exc_info=True)
        if 'orchestration' in locals():
            orchestration.status = AgentStatus.FAILED
            orchestration.completed_at = timezone.now()
            orchestration.save()
        raise


def _transform_orchestration_for_frontend(orchestration_results: dict, home_team: str, away_team: str) -> dict:
    """
    Transform complex orchestration results into frontend-friendly format.

    Frontend expects:
    {
        agents: [
            {name: "Agent Name", confidence: 85, analysis: "Detailed text with team names"}
        ],
        recommendation: {
            team: "Buffalo Bills",
            bet_type: "moneyline",
            stake_percent: 2.5,
            expected_value: 12.5
        },
        overall_confidence: 82
    }
    """
    frontend_format = {
        'agents': [],
        'recommendation': {},
        'overall_confidence': 75
    }

    try:
        # Extract agent results from all phases
        phase_results = orchestration_results.get('phase_results', {})

        for phase_name, phase_data in phase_results.items():
            agent_results = phase_data.get('results', {})

            for agent_id, agent_result in agent_results.items():
                # Skip failed agents
                if not agent_result.get('success', True):
                    continue

                # Get agent data
                agent_data = agent_result.get('data', {})
                agent_name = agent_result.get('agent_name', agent_id.replace('-', ' ').title())
                confidence = int(agent_data.get('confidence', 0.75) * 100)

                # Build analysis text from insights
                insights = agent_data.get('insights', [])
                if insights:
                    # Join insights into a readable analysis paragraph
                    analysis = ' '.join(insights)
                else:
                    # Fallback to generic message if no insights
                    analysis = f"{agent_name} completed analysis for {home_team} vs {away_team}"

                frontend_format['agents'].append({
                    'name': agent_name,
                    'confidence': confidence,
                    'analysis': analysis
                })

        # Extract final recommendation
        final_rec = orchestration_results.get('final_recommendation', {})

        if final_rec.get('action') in ['BET', 'LEAN']:
            primary_rec = final_rec.get('primary_recommendation', {})

            frontend_format['recommendation'] = {
                'team': primary_rec.get('side', home_team),
                'bet_type': 'moneyline',
                'stake_percent': float(final_rec.get('kelly_allocation', '2.5%').rstrip('%')),
                'expected_value': float(final_rec.get('expected_value', '+0%').lstrip('+').rstrip('%'))
            }
        else:
            # No strong recommendation - pass
            frontend_format['recommendation'] = {
                'team': 'No Strong Play',
                'bet_type': 'pass',
                'stake_percent': 0,
                'expected_value': 0
            }

        # Set overall confidence
        frontend_format['overall_confidence'] = int(final_rec.get('overall_confidence', 0.75) * 100)

        return frontend_format

    except Exception as e:
        logger.error(f"Error transforming orchestration results: {e}")
        # Return minimal valid structure on error
        return {
            'agents': [{
                'name': 'System',
                'confidence': 50,
                'analysis': f'Analysis completed for {home_team} vs {away_team}. Error formatting results.'
            }],
            'recommendation': {
                'team': home_team,
                'bet_type': 'pass',
                'stake_percent': 0,
                'expected_value': 0
            },
            'overall_confidence': 50
        }


@shared_task(bind=True, max_retries=2, soft_time_limit=90, time_limit=120)
def execute_sports_orchestration(self, game_id: str, home_team: str, away_team: str,
                                 league: str, subscription_tier: str = 'basic',
                                 selected_agents: list = None, cache_key: str = None):
    """
    Execute sports betting agent orchestration asynchronously.
    This task handles the coordination of multiple betting analysis agents.
    """
    import asyncio
    from sports.orchestration import execute_coordinated_analysis
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync

    logger.info(f"Starting async sports orchestration for {home_team} vs {away_team}")

    channel_layer = get_channel_layer()

    try:
        # Send initial status via WebSocket
        async_to_sync(channel_layer.group_send)(
            'agents_general',
            {
                'type': 'agent_progress',
                'data': {
                    'game_id': game_id,
                    'agent_name': 'Orchestration Engine',
                    'agent_id': 'orchestration',
                    'status': 'running',
                    'message_type': 'orchestration',
                    'content': f'Starting orchestration for {home_team} vs {away_team}',
                    'timestamp': datetime.now().isoformat()
                }
            }
        )

        # Create a new event loop for async execution
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Execute the orchestration
            orchestration_results = loop.run_until_complete(
                execute_coordinated_analysis(
                    game_id=game_id,
                    home_team=home_team,
                    away_team=away_team,
                    league=league,
                    subscription_tier=subscription_tier,
                    selected_agents=selected_agents
                )
            )

            # Send completion status via WebSocket
            async_to_sync(channel_layer.group_send)(
                'agents_general',
                {
                    'type': 'agent_progress',
                    'data': {
                        'game_id': game_id,
                        'agent_name': 'Orchestration Engine',
                        'agent_id': 'orchestration',
                        'status': 'completed',
                        'message_type': 'result',
                        'content': f'Orchestration completed for {home_team} vs {away_team}',
                        'timestamp': datetime.now().isoformat(),
                        'results': orchestration_results
                    }
                }
            )

            logger.info(f"Sports orchestration completed successfully for game {game_id}")

            # Transform orchestration results into frontend-friendly format
            frontend_results = _transform_orchestration_for_frontend(
                orchestration_results,
                home_team,
                away_team
            )

            result_data = {
                'success': True,
                'game_id': game_id,
                'results': frontend_results
            }

            # Cache results for 20 minutes to avoid redundant expensive operations
            if cache_key:
                from django.core.cache import cache
                cache.set(cache_key, {
                    'result': result_data,
                    'timestamp': datetime.now().isoformat(),
                    'cache_age': 0  # Fresh result
                }, timeout=1200)  # 20 minutes
                logger.info(f"Cached analysis for game {game_id} (cache_key: {cache_key}, TTL: 20 min)")

            return result_data

        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Sports orchestration failed for game {game_id}: {str(e)}")

        # Send error status via WebSocket
        async_to_sync(channel_layer.group_send)(
            'agents_general',
            {
                'type': 'agent_progress',
                'data': {
                    'game_id': game_id,
                    'agent_name': 'Orchestration Engine',
                    'agent_id': 'orchestration',
                    'status': 'error',
                    'message_type': 'error',
                    'content': f'Orchestration failed: {str(e)}',
                    'timestamp': datetime.now().isoformat()
                }
            }
        )

        # Retry if we haven't exceeded max retries
        raise self.retry(exc=e, countdown=30)


@shared_task(name='agents.update_agent_performance')
def update_agent_performance():
    """
    Update agent performance metrics from evaluated predictions
    Runs daily after prediction evaluation (Phase 3 - Agent Learning)

    Returns:
        dict: Summary of predictions processed and agents updated
    """
    from sports.models import MLPrediction
    from core.models.agents_registry import AgentPerformanceMetrics

    logger.info("Starting agent performance update task")

    # Get recently evaluated predictions (last 24 hours)
    cutoff = timezone.now() - timedelta(hours=24)
    new_evaluations = MLPrediction.objects.filter(
        was_correct__isnull=False,
        evaluated_at__gte=cutoff,
        agent__isnull=False  # Only predictions with assigned agents
    ).select_related('agent')

    logger.info(f"Found {new_evaluations.count()} evaluated predictions from last 24 hours")

    agents_updated = set()
    predictions_processed = 0

    for prediction in new_evaluations:
        try:
            # Get agent who made this prediction
            agent = prediction.agent

            if not agent:
                continue

            # Get or create performance metrics for this agent+sport combination
            metrics, created = AgentPerformanceMetrics.objects.get_or_create(
                agent=agent,
                sport_type=prediction.sport_type
            )

            if created:
                logger.info(
                    f"Created new performance metrics for {agent.name} - {prediction.sport_type.upper()}"
                )

            # Update metrics with this prediction
            metrics.update_from_prediction(prediction)

            agents_updated.add(agent.id)
            predictions_processed += 1

            logger.debug(
                f"Updated {agent.name} metrics for {prediction.sport_type.upper()}: "
                f"{metrics.sport_accuracy:.1%} accuracy ({metrics.sport_correct}/{metrics.sport_predictions})"
            )

        except Exception as e:
            logger.error(
                f"Error updating agent performance for prediction {prediction.id}: {e}",
                exc_info=True
            )
            continue

    result = {
        'predictions_processed': predictions_processed,
        'agents_updated': len(agents_updated),
        'timestamp': timezone.now().isoformat()
    }

    logger.info(
        f"Agent performance update complete: "
        f"{predictions_processed} predictions processed, "
        f"{len(agents_updated)} agents updated"
    )

    return result
from typing import Tuple, Union  # noqa: F401 — needed by extracted _impl_ functions


# Late imports from core.tasks — these helpers live in the main module
# and can't be imported at module level without circular import risk,
# but are safe here because core.tasks is always loaded first.
from core.tasks import (  # noqa: F401
    _record_timeout_signature,
    _is_media_task_blocked,
    _circuit_breaker_check,
    _circuit_breaker_record_timeout,
    _circuit_breaker_release,
    _apply_task_routing_override,
)

# ============================================================
# Extracted task implementations (from core/tasks.py via do_extract.py)
# ============================================================

def _impl_cleanup_stale_agent_executions(self, minutes_threshold: int = 60):
    """
    Session 835: Clean up agent executions stuck in 'running'/'in_progress' status.
    Session 842: Added detailed logging for debugging.
    Session 911: Fixed to check both 'running' and 'in_progress' statuses.
    Session 925: Added to Celery Beat schedule - runs every 30 min with 2hr threshold.
    Session 1017: Changed default from 30 to 60 min. Beat kwargs (120) weren't being
                  passed — 30 min was too aggressive for slow agents (WorkflowAgent
                  max 22 min, MeetingCoordinatorAgent max 24 min).

    Tasks that have been running for more than the threshold are
    marked as 'failed' since they clearly didn't complete properly.

    Args:
        minutes_threshold: Mark tasks as failed after this many minutes (default 30)
    """
    from django.utils import timezone
    from datetime import timedelta
    from core.models_unified_system import AgentExecution

    task_id = self.request.id if self.request else 'unknown'
    logger.info(f"🧹 [CLEANUP] Task {task_id} STARTED - threshold: {minutes_threshold} minutes")

    try:
        from django.db.models import Q
        from django.db.models.functions import Coalesce

        now = timezone.now()
        cutoff_time = now - timedelta(minutes=minutes_threshold)
        logger.info(f"🧹 [CLEANUP] Current time: {now.isoformat()}, cutoff: {cutoff_time.isoformat()}")

        # Session 911: Check both 'running' and 'in_progress' statuses
        # Tasks can be stuck in either state depending on how they were created
        running_statuses = ['running', 'in_progress']
        all_running = AgentExecution.objects.filter(status__in=running_statuses).count()
        logger.info(f"🧹 [CLEANUP] Total running/in_progress executions: {all_running}")

        # Session 1100: Use last_heartbeat_at when available — agents that touch
        # their heartbeat periodically are still alive. Fall back to created_at
        # for older executions that predate the heartbeat field.
        # Session 1102: Wrapped in atomic() — ProgrammingError poisons the PG
        # transaction, so the fallback query in except would also fail without
        # a savepoint rollback.
        _has_heartbeat = False
        try:
            with transaction.atomic():
                stale_tasks = AgentExecution.objects.filter(
                    status__in=running_statuses,
                ).annotate(
                    alive_at=Coalesce('last_heartbeat_at', 'created_at'),
                ).filter(
                    alive_at__lt=cutoff_time,
                )
                count = stale_tasks.count()
                _has_heartbeat = True
        except Exception:
            # Migration 0301 not yet applied — fall back to created_at only
            logger.info("🧹 [CLEANUP] last_heartbeat_at column not yet available, using created_at fallback")
            stale_tasks = AgentExecution.objects.filter(
                status__in=running_statuses,
                created_at__lt=cutoff_time,
            )
            count = stale_tasks.count()

        logger.info(f"🧹 [CLEANUP] Stale executions (>{minutes_threshold}min since last heartbeat): {count}")

        if count > 0:
            # Log details + emit timeout signatures for each stale task
            _fields = ['id', 'agent__name', 'created_at']
            if _has_heartbeat:
                _fields.append('last_heartbeat_at')
            sample_tasks = list(stale_tasks.values(*_fields)[:20])
            for task in sample_tasks:
                ref_time = task.get('last_heartbeat_at') or task['created_at']
                age_min = (now - ref_time).total_seconds() / 60
                hb_status = 'heartbeat' if task.get('last_heartbeat_at') else 'no heartbeat'
                logger.info(f"🧹 [CLEANUP] Marking stale: {task['agent__name']} - {age_min:.0f}min since {hb_status} - ID: {task['id']}")
                # Session 1080: Emit structured timeout signature
                _record_timeout_signature(
                    agent_name=task['agent__name'],
                    timeout_source='watchdog_cleanup',
                    elapsed_seconds=age_min * 60,
                    execution_id=task['id'],
                )

            # Perform the cleanup
            updated = stale_tasks.update(
                status='failed',
                error_message=f'Task timed out after {minutes_threshold} minutes (no heartbeat) - marked as failed by cleanup',
                completed_at=now
            )
            logger.info(f"🧹 [CLEANUP] SUCCESS - Cleaned up {updated} stale agent executions")
        else:
            logger.info(f"🧹 [CLEANUP] No stale executions found - nothing to clean")

        logger.info(f"🧹 [CLEANUP] Task {task_id} COMPLETED - cleaned: {count}")
        return {'cleaned': count, 'total_running': all_running, 'task_id': task_id}

    except Exception as e:
        logger.error(f"🧹 [CLEANUP] Task {task_id} FAILED with error: {e}", exc_info=True)
        raise




def _impl_auto_process_extracted_artifacts(
stale_days: int = 7,
    archive_days: int = 14,
    batch_size: int = 2000,
    aggressive: bool = True
):
    """
    Session 943: Auto-process ExtractedArtifacts to prevent backlog accumulation.

    Processes 42K+ pending artifacts based on type, age, and score.

    AGGRESSIVE MODE (default=True) - Session 943 update:
    - ALL insights → approved (informational, no action needed)
    - proposals older than 10 days with score < 0.6 → rejected
    - proposals with score < 0.4 (any age) → rejected
    - experiments older than 7 days → rejected (stale experiments)
    - data_specs with score < 0.5 → rejected (low-value specs)
    - questions older than 7 days → rejected
    - risks with score < 0.4 → rejected (low-priority risks)
    - action_items older than 14 days with score < 0.5 → rejected

    STANDARD MODE (aggressive=False):
    - insights with score < 0.5 → approved
    - questions older than 14 days → rejected
    - items older than 30 days with score < 0.4 → rejected
    - duplicate titles → rejected (keep highest score)
    - data_specs with confidence < 0.3 → deferred

    ALWAYS KEEP PENDING (needs human review):
    - high-score risks (score >= 0.4)
    - recent action_items with good scores (score >= 0.5, age < 14 days)
    - high-score proposals (score >= 0.6, age < 10 days)

    Args:
        stale_days: Days after which questions/experiments become stale (default: 7)
        archive_days: Days after which low-score items get rejected (default: 14)
        batch_size: Max items to process per run (default: 2000)
        aggressive: Use aggressive cleanup rules (default: True)

    Returns:
        Dict with processing statistics
    """
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count
    from core.models_conversation_artifacts import ExtractedArtifact

    mode = "AGGRESSIVE" if aggressive else "STANDARD"
    logger.info(f"🔄 [ARTIFACT-AUTO-PROCESS] Starting auto-processing ({mode} mode)...")

    try:
        now = timezone.now()
        stale_cutoff = now - timedelta(days=stale_days)  # 7 days for questions/experiments
        archive_cutoff = now - timedelta(days=archive_days)  # 14 days for action_items
        proposal_cutoff = now - timedelta(days=10)  # 10 days for proposals
        experiment_cutoff = now - timedelta(days=stale_days)  # Same as questions (7 days)

        stats = {
            'insights_approved': 0,
            'questions_rejected': 0,
            'stale_rejected': 0,
            'duplicates_rejected': 0,
            'specs_rejected': 0,
            'proposals_rejected': 0,
            'experiments_rejected': 0,
            'risks_rejected': 0,
            'action_items_rejected': 0,
            'specs_deferred': 0,
            'total_processed': 0,
            'still_pending': 0,
        }

        # =====================================================================
        # 1. Session 1070: AUTO-REJECT very low-score noise insights only.
        # All other insights stay 'pending' until human classifies + approves.
        # (Previously this block auto-approved insights, which bypassed
        #  the decision gate — the core semantic bug this session fixes.)
        # =====================================================================
        noise_insights = ExtractedArtifact.objects.filter(
            status='pending',
            artifact_type='insight',
            composite_score__lt=0.3
        )[:batch_size]
        noise_note = 'Auto-rejected: Very low-score insight (noise, composite < 0.3)'

        for artifact in noise_insights:
            artifact.status = 'rejected'
            artifact.decided_at = now
            artifact.decision_notes = noise_note
            artifact.save(update_fields=['status', 'decided_at', 'decision_notes'])
            stats['insights_approved'] += 1  # reusing key for backwards compat
            stats['total_processed'] += 1

        # =====================================================================
        # 2. AUTO-REJECT: Stale questions (older than stale_days)
        # =====================================================================
        stale_questions = ExtractedArtifact.objects.filter(
            status='pending',
            artifact_type='question',
            extracted_at__lt=stale_cutoff
        )[:batch_size]

        for artifact in stale_questions:
            artifact.status = 'rejected'
            artifact.decided_at = now
            artifact.decision_notes = f'Auto-rejected: Stale question (>{stale_days} days old)'
            artifact.save(update_fields=['status', 'decided_at', 'decision_notes'])
            stats['questions_rejected'] += 1
            stats['total_processed'] += 1

        # =====================================================================
        # 3. AUTO-REJECT: Old low-score artifacts (older than archive_days, score < 0.4)
        # =====================================================================
        stale_low_score = ExtractedArtifact.objects.filter(
            status='pending',
            extracted_at__lt=archive_cutoff,
            composite_score__lt=0.4
        )[:batch_size]

        for artifact in stale_low_score:
            artifact.status = 'rejected'
            artifact.decided_at = now
            artifact.decision_notes = f'Auto-rejected: Stale and low-priority (>{archive_days} days, score<0.4)'
            artifact.save(update_fields=['status', 'decided_at', 'decision_notes'])
            stats['stale_rejected'] += 1
            stats['total_processed'] += 1

        # =====================================================================
        # 4. AUTO-REJECT: Duplicate titles (keep highest score)
        # =====================================================================
        # Find duplicate titles within each artifact type
        duplicates = (
            ExtractedArtifact.objects
            .filter(status='pending')
            .values('artifact_type', 'title')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
        )[:100]  # Limit duplicate groups to check

        for dup in duplicates:
            # Get all artifacts with this title/type, ordered by score desc
            matching = ExtractedArtifact.objects.filter(
                status='pending',
                artifact_type=dup['artifact_type'],
                title=dup['title']
            ).order_by('-composite_score')

            # Keep the first (highest score), reject the rest
            for artifact in matching[1:]:
                artifact.status = 'rejected'
                artifact.decided_at = now
                artifact.decision_notes = 'Auto-rejected: Duplicate (lower score copy)'
                artifact.save(update_fields=['status', 'decided_at', 'decision_notes'])
                stats['duplicates_rejected'] += 1
                stats['total_processed'] += 1

        # =====================================================================
        # 5. AGGRESSIVE: Reject proposals (two rules)
        # Rule A: older than 10 days with score < 0.6 → rejected
        # Rule B: very low score < 0.4 (any age) → rejected
        # =====================================================================
        if aggressive:
            # Rule A: Old proposals with mediocre scores
            old_proposals = ExtractedArtifact.objects.filter(
                status='pending',
                artifact_type='proposal',
                extracted_at__lt=proposal_cutoff,
                composite_score__lt=0.6
            )[:batch_size]

            for artifact in old_proposals:
                artifact.status = 'rejected'
                artifact.decided_at = now
                artifact.decision_notes = 'Auto-rejected: Stale proposal (>10 days, score<0.6)'
                artifact.save(update_fields=['status', 'decided_at', 'decision_notes'])
                stats['proposals_rejected'] += 1
                stats['total_processed'] += 1

            # Rule B: Very low-score proposals (any age)
            low_score_proposals = ExtractedArtifact.objects.filter(
                status='pending',
                artifact_type='proposal',
                composite_score__lt=0.4
            )[:batch_size]

            for artifact in low_score_proposals:
                artifact.status = 'rejected'
                artifact.decided_at = now
                artifact.decision_notes = 'Auto-rejected: Low-score proposal (score<0.4)'
                artifact.save(update_fields=['status', 'decided_at', 'decision_notes'])
                stats['proposals_rejected'] += 1
                stats['total_processed'] += 1

        # =====================================================================
        # 6. AGGRESSIVE: Reject old experiments (>14 days)
        # =====================================================================
        if aggressive:
            old_experiments = ExtractedArtifact.objects.filter(
                status='pending',
                artifact_type='experiment',
                extracted_at__lt=experiment_cutoff
            )[:batch_size]

            for artifact in old_experiments:
                artifact.status = 'rejected'
                artifact.decided_at = now
                artifact.decision_notes = f'Auto-rejected: Stale experiment (>{stale_days} days old)'
                artifact.save(update_fields=['status', 'decided_at', 'decision_notes'])
                stats['experiments_rejected'] += 1
                stats['total_processed'] += 1

        # =====================================================================
        # 7. AGGRESSIVE: Reject low-score data_specs (score < 0.5)
        # Standard: Defer low-confidence specs
        # =====================================================================
        if aggressive:
            low_specs = ExtractedArtifact.objects.filter(
                status='pending',
                artifact_type='data_spec',
                composite_score__lt=0.5
            )[:batch_size]

            for artifact in low_specs:
                artifact.status = 'rejected'
                artifact.decided_at = now
                artifact.decision_notes = 'Auto-rejected: Low-score data spec (score<0.5)'
                artifact.save(update_fields=['status', 'decided_at', 'decision_notes'])
                stats['specs_rejected'] += 1
                stats['total_processed'] += 1
        else:
            # Standard mode: just defer unclear specs
            unclear_specs = ExtractedArtifact.objects.filter(
                status='pending',
                artifact_type='data_spec',
                confidence_score__lt=0.3
            )[:batch_size]

            for artifact in unclear_specs:
                artifact.status = 'deferred'
                artifact.decided_at = now
                artifact.decision_notes = 'Auto-deferred: Low-confidence spec needs clarification'
                artifact.save(update_fields=['status', 'decided_at', 'decision_notes'])
                stats['specs_deferred'] += 1
                stats['total_processed'] += 1

        # =====================================================================
        # 8. AGGRESSIVE: Reject low-score risks (score < 0.4)
        # Low-score risks aren't actionable enough to keep
        # =====================================================================
        if aggressive:
            low_risks = ExtractedArtifact.objects.filter(
                status='pending',
                artifact_type='risk',
                composite_score__lt=0.4
            )[:batch_size]

            for artifact in low_risks:
                artifact.status = 'rejected'
                artifact.decided_at = now
                artifact.decision_notes = 'Auto-rejected: Low-score risk (score<0.4)'
                artifact.save(update_fields=['status', 'decided_at', 'decision_notes'])
                stats['risks_rejected'] += 1
                stats['total_processed'] += 1

        # =====================================================================
        # 9. AGGRESSIVE: Reject old low-score action_items (>14 days, score<0.5)
        # Old action items that weren't actioned can be cleared
        # =====================================================================
        if aggressive:
            old_action_items = ExtractedArtifact.objects.filter(
                status='pending',
                artifact_type='action_item',
                extracted_at__lt=archive_cutoff,
                composite_score__lt=0.5
            )[:batch_size]

            for artifact in old_action_items:
                artifact.status = 'rejected'
                artifact.decided_at = now
                artifact.decision_notes = 'Auto-rejected: Stale action item (>14 days, score<0.5)'
                artifact.save(update_fields=['status', 'decided_at', 'decision_notes'])
                stats['action_items_rejected'] += 1
                stats['total_processed'] += 1

        # =====================================================================
        # 10. Count remaining pending
        # =====================================================================
        stats['still_pending'] = ExtractedArtifact.objects.filter(status='pending').count()

        total_rejected = (
            stats['questions_rejected'] + stats['stale_rejected'] +
            stats['duplicates_rejected'] + stats['specs_rejected'] +
            stats['proposals_rejected'] + stats['experiments_rejected'] +
            stats['risks_rejected'] + stats['action_items_rejected']
        )
        logger.info(
            f"🔄 [ARTIFACT-AUTO-PROCESS] Complete ({mode}) - processed {stats['total_processed']} items: "
            f"approved={stats['insights_approved']}, "
            f"rejected={total_rejected} "
            f"(questions={stats['questions_rejected']}, proposals={stats['proposals_rejected']}, "
            f"experiments={stats['experiments_rejected']}, specs={stats['specs_rejected']}, "
            f"risks={stats['risks_rejected']}, action_items={stats['action_items_rejected']}, "
            f"dupes={stats['duplicates_rejected']}, stale={stats['stale_rejected']}), "
            f"deferred={stats['specs_deferred']}, "
            f"still_pending={stats['still_pending']}"
        )

        return stats

    except Exception as e:
        logger.error(f"🔄 [ARTIFACT-AUTO-PROCESS] Failed: {e}", exc_info=True)
        raise




def _impl_execute_agent_task(
self,
    agent_name: str,
    task: str,
    context: Dict[str, Any] = None
):
    """
    Session 811: Execute a task via a specific agent from conversation next_steps.
    Session 1017: Added soft_time_limit=2700 (45 min) to kill hung agents.
    Session 1058: Raised to 3600/3900 (60/65 min) — WorkflowAgent/TrendAnalysisAgent hit 43-44 min.
    NOTE: soft_time_limit does NOT enforce on --pool=threads (Railway) — SIGUSR1
    only works with prefork. The WorkflowAgent wall-clock guard is the real timeout.

    This task is queued by ConversationActionDispatcher when a conversation
    produces next_steps that should be executed.

    Args:
        agent_name: Name of the agent to execute the task (e.g., "ResearchAgent")
        task: Task description from conversation next_steps
        context: Additional context including conversation_id, participants

    Returns:
        Dict with execution result including status and output
    """
    from core.agent_router import AgentRouter
    # Session 1084: Explicit import of the canonical AgentExecution model.
    #
    # Context: this module already has a module-level import at line 27 —
    # `from core.models.agents_registry import AgentExecution` — which
    # resolves to a DIFFERENT model (table `agents_agentexecution`, used
    # by the outer training/registry functions in this file). That table
    # is empty in practice.
    #
    # The canonical live AgentExecution — the one `ops_tool` reads, the
    # one `agent_router._create_execution_record` writes, the one
    # cleanup_watchdog reaps from, and the one this function needs to
    # coordinate with — lives in `core.models_unified_system` and writes
    # to table `core_agentexecution`. We import it here with the name
    # `AgentExecution` explicitly so this function scope shadows the
    # module-level import intentionally. Do NOT "fix" this by removing
    # the shadow without migrating the two models — the two tables have
    # different schemas and different consumers.
    #
    # Same rationale for `Agent`.
    from core.models_unified_system import Agent, AgentExecution  # noqa: F811
    from core.services.context_tracing import ContextTracer, auto_repair_context
    from decimal import Decimal

    # Session 1064: Respect body throttle mode — proportional delay when system stressed
    # Note: body health tasks (run_heartbeat, check_breathing, etc.), PA chat
    # (process_pa_chat_task), and gate progression (process_gate_progression) are
    # separate Celery tasks that never flow through execute_agent_task — they are
    # naturally exempt. All agent work dispatched here is deferrable.
    try:
        from core.services.body_coordinator import BodyCoordinator
        from django.conf import settings as django_settings
        coordinator = BodyCoordinator()
        throttle = coordinator.get_throttle_factor()
        if throttle < 1.0:
            max_delay = getattr(django_settings, 'BODY_THROTTLE_MAX_DELAY_SECONDS', 30)
            delay = int((1.0 - throttle) * max_delay)
            logger.info(f"Body throttle {throttle:.1f}: delaying {agent_name} by {delay}s")
            time.sleep(delay)
    except Exception:
        pass  # Never block agent execution due to body system errors

    # Session 875: Initialize context tracer for bad context forensics
    tracer = ContextTracer(source=f"execute_agent_task:{agent_name}")

    # Session 875: Log context at post-deserialize stage (after Celery receives it)
    tracer.log_post_deserialize(
        context=context,
        agent_name=agent_name,
        task_name="execute_agent_task"
    )

    # Session 875: Ensure context is a dict (defensive fix for list being passed)
    if not isinstance(context, dict):
        logger.warning(f"[execute_agent_task] Received non-dict context (type={type(context).__name__}), using empty dict")
        # Auto-repair the context
        context = auto_repair_context(context)
    else:
        context = context or {}
    conversation_id = str(context.get('conversation_id', 'unknown'))
    execution_start = time.time()

    # Session 1031: Hard-block agents that can't do useful work on Railway
    # Session 1080: Centralized in AgentControlEntry (DB-backed, PA-manageable)
    from core.models_unified_system import AgentControlEntry
    _BLOCKED_AGENTS = AgentControlEntry.get_blocked_names()
    if agent_name in _BLOCKED_AGENTS:
        logger.warning(
            f"[execute_agent_task] BLOCKED: {agent_name} disabled on Railway "
            f"(task='{task[:50]}...')"
        )
        return {
            'status': 'blocked',
            'agent': agent_name,
            'reason': f'{agent_name} disabled on Railway since Session 1031',
        }

    # Session 1036: Block non-generative tasks for media agents.
    # ImageAgent, VideoAgent, etc. can only generate/edit content — tasks like
    # "list recent images in workspace" waste API spend ($0.03+) for nothing.
    if _is_media_task_blocked(agent_name, task):
        logger.info(
            f"[execute_agent_task] BLOCKED non-generative task for {agent_name}: "
            f"'{task[:60]}...'"
        )
        return {
            'status': 'blocked',
            'agent': agent_name,
            'reason': f'{agent_name} only handles generation/editing tasks',
        }

    # Session 1095: Circuit breaker — prevent repeated execution of doomed tasks.
    # Checks: (1) has this (agent, task) timed out 2+ times in 24h? If so, skip.
    # (2) is an identical task already running? If so, dedup.
    _cb_block = _circuit_breaker_check(agent_name, task)
    if _cb_block:
        logger.warning(
            f"[execute_agent_task] CIRCUIT BREAKER: {agent_name} — "
            f"{_cb_block['status']} (task='{task[:50]}...')"
        )
        return _cb_block

    # Session 1077: Focus Mode — block autonomous tasks with banned topics
    # Only applies to non-manual runs (no user_id in context = autonomous)
    if not context.get('user_id'):
        try:
            from core.services.focus_mode import check_autonomous_task, record_block
            fm = check_autonomous_task(agent_name, task, context)
            if not fm['allowed']:
                logger.info(
                    f"[execute_agent_task] FOCUS MODE: {agent_name} blocked — "
                    f"{fm['reason']} (task='{task[:50]}...')"
                )
                record_block(fm['reason'])
                return {
                    'status': 'blocked',
                    'agent': agent_name,
                    'reason': f"focus_mode:{fm['reason']}",
                }
        except Exception as e:
            logger.warning(f"[execute_agent_task] Focus Mode check failed (proceeding): {e}")

    # Session 1090: Demo mode gate — blocks non-allowlisted agents at the
    # Celery execution layer.  The governor's should_dispatch() is called by
    # callers *before* enqueueing, but PA tool dispatch + direct Celery calls
    # bypass it.  This is the safety net.
    try:
        from core.services.priority.governor import _check_demo_mode
        demo_block = _check_demo_mode(agent_name)
        if demo_block is not None:
            logger.info(
                "[execute_agent_task] DEMO BLOCK: %s — %s",
                agent_name, demo_block.detail,
            )
            return {
                'status': 'blocked',
                'agent': agent_name,
                'reason': f'demo_mode:{demo_block.reason}',
            }
    except Exception:
        pass  # fail-open

    logger.info(
        f"[execute_agent_task] Starting: {agent_name} <- '{task[:50]}...' "
        f"(conversation={conversation_id})"
    )

    try:
        # Create execution record
        agent_obj = Agent.objects.filter(name=agent_name).first()

        # Session 841: Resolve experiment for proper error rate scoping
        experiment = None
        experiment_id = context.get('experiment_id')
        if experiment_id:
            try:
                from core.models import Experiment
                experiment = Experiment.objects.filter(id=experiment_id).first()
            except Exception as e:
                logger.warning(f"Experiment lookup failed for {experiment_id}: {e}")

        execution_record = None
        if agent_obj:
            # Session 1088: Sanitize input_data — context may contain UUID objects
            # (e.g. user_id, experiment_id) that aren't JSON-serializable.
            import json as _json
            _raw_input = {
                'task': task,
                'context': context,
                'source': 'conversation_action_dispatch',
                'celery_task_id': str(self.request.id),
            }
            try:
                input_data = _json.loads(_json.dumps(_raw_input, default=str))
            except (TypeError, ValueError):
                input_data = {'task': task, 'source': 'conversation_action_dispatch',
                              'celery_task_id': str(self.request.id)}

            _create_kwargs = dict(
                agent=agent_obj,
                task=task[:500],  # Truncate for DB field
                status='in_progress',
                input_data=input_data,
                experiment=experiment,  # Session 841: Link to experiment for scoped metrics
            )
            # Session 1100: Set initial heartbeat (graceful if migration not yet applied)
            try:
                _create_kwargs['last_heartbeat_at'] = timezone.now()
                execution_record = AgentExecution.objects.create(**_create_kwargs)
            except Exception:
                _create_kwargs.pop('last_heartbeat_at', None)
                execution_record = AgentExecution.objects.create(**_create_kwargs)

            # Session 1084: Temporary writer-attribution log so PR #1887 can
            # be verified in prod (one dispatch → exactly one Table B row).
            logger.info(
                f"[execution_record_created_by=tasks_agents] agent={agent_name} "
                f"execution_id={getattr(execution_record, 'id', None)}"
            )

        # Session 1031: Routing override — reroute specialist tasks away from
        # non-specialist agents.  E.g. "competitor audit" should never go to
        # WorkflowAgent, VideoAgent, etc.
        agent_name = _apply_task_routing_override(agent_name, task)

        # Session 1031: Dedup — skip if this agent already ran a very similar task recently
        # Exclude the execution_record we just created (it would always match itself)
        # Only dedup against SUCCESSFUL completions — failed/deduped tasks should be retryable
        dedup_qs = AgentExecution.objects.filter(
            agent__name=agent_name,
            created_at__gte=timezone.now() - timedelta(hours=2),
            task__startswith=task[:80],
            status='completed',
        ).exclude(
            output_data__skipped='dedup',
        )
        if execution_record:
            dedup_qs = dedup_qs.exclude(id=execution_record.id)
        recent_dup = dedup_qs.exists()
        if recent_dup:
            logger.info(
                f"[execute_agent_task] Dedup skip: {agent_name} already ran "
                f"'{task[:60]}' in the last 2h"
            )
            if execution_record:
                execution_record.status = 'completed'
                execution_record.output_data = {'skipped': 'dedup', 'reason': 'Similar task ran in last 2h'}
                execution_record.completed_at = timezone.now()
                # Session 1084 round 48: update_fields excludes last_heartbeat_at
                # so the heartbeat thread's queryset update() is not stomped
                # by full-instance save(). See PR description for evidence.
                execution_record.save(update_fields=[
                    'status', 'output_data', 'completed_at',
                ])
            return {
                'success': True,
                'agent_name': agent_name,
                'task': task,
                'skipped': 'dedup',
                'conversation_id': conversation_id,
            }

        # Route to agent — resolve user from context so media is owned correctly
        _route_user = None
        _route_user_id = context.get('user_id')
        if _route_user_id:
            try:
                from django.contrib.auth import get_user_model
                _route_user = get_user_model().objects.filter(id=_route_user_id).first()
            except Exception as _e:
                logger.warning(
                    "tasks_agents._impl_execute_agent_task: swallowed (%s: %s) — degraded",
                    type(_e).__name__, _e,
                )

        # Session 1091: Per-agent wall-clock timeout moved to shared module
        # core/services/agent_timeouts.py so the router path enforces the
        # same ceilings as this Celery-task path. Edit values there, not here.
        from core.services.agent_timeouts import get_agent_timeout
        _wall_timeout = get_agent_timeout(agent_name)

        # Session 1087: Check for remediation-engine timeout overrides
        try:
            from core.models.system import SystemConfiguration
            _override = SystemConfiguration.objects.filter(
                key=f'agent_timeout_override:{agent_name}',
            ).values_list('value', flat=True).first()
            if _override:
                _wall_timeout = int(_override)
                logger.info(f"[execute_agent_task] Using override timeout {_wall_timeout}s for {agent_name}")
        except Exception as _e:
            logger.warning(
                "tasks_agents._impl_execute_agent_task: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        router = AgentRouter(user=_route_user)

        # Debug: log context keys entering route() for directed mode debugging
        directed_keys = ['research_summary', 'editor_feedback', 'required_checks', 'review_feedback', 'original_draft']
        found_directed = {k: bool(context.get(k)) for k in directed_keys}
        logger.info(
            "[execute_agent_task] %s context directed-mode keys: %s | total context keys: %s",
            agent_name, found_directed, list(context.keys())[:20],
        )

        from concurrent.futures import ThreadPoolExecutor as _TPE, TimeoutError as _FuturesTimeout
        def _run_route():
            from django.db import close_old_connections
            close_old_connections()
            try:
                # Session 1084 / PR #1887: tasks_agents already created the
                # AgentExecution row above. Pass it through to the router and
                # tell it NOT to create a duplicate. Before this change every
                # PA dispatch produced 2 rows in core_agentexecution — one
                # from tasks_agents, one from agent_router._create_execution_record.
                return router.route(
                    agent_name=agent_name,
                    task=task,
                    context={
                        'source': 'conversation_action_dispatch',
                        'conversation_id': conversation_id,
                        **context
                    },
                    create_execution_record=False,
                    existing_execution_record=execution_record,
                )
            finally:
                close_old_connections()

        # Session 1100: Heartbeat thread — touch execution record every 2 min
        # so the cleanup watchdog knows this agent is still alive.
        # Session 1084: Import hoisted out of loop body. Rationale: when the
        # main thread wedges on a C-level socket hang (e.g. CLOSE_WAIT on a
        # provider / spider HTTP call), it can hold the Python import lock,
        # and any `import` statement in a background thread then blocks
        # forever. Heartbeat threads must not touch the import machinery
        # at tick time — resolve everything before the thread starts.
        import threading
        from django.db import close_old_connections as _hb_close_old_connections
        _hb_stop = threading.Event()
        _hb_execution_id = execution_record.id if execution_record else None

        # Session 1084 heartbeat tick proof: first tick at 30s so short runs
        # (the majority) actually exercise the update() path at least once,
        # then 120s thereafter for long-running agents. Inline the update()
        # call (instead of model.touch_heartbeat()) so we can capture rowcount
        # and prove the write landed — catches the silent no-op case where
        # the execution_id row has disappeared.
        _HB_FIRST_TICK_S = 30
        _HB_TICK_S = 120

        def _heartbeat_loop():
            logger.info(
                f"[heartbeat] thread start agent={agent_name} "
                f"execution_id={_hb_execution_id} first_tick={_HB_FIRST_TICK_S}s "
                f"interval={_HB_TICK_S}s"
            )
            tick_count = 0
            next_sleep = _HB_FIRST_TICK_S
            try:
                while not _hb_stop.wait(timeout=next_sleep):
                    if execution_record:
                        try:
                            _hb_close_old_connections()
                            rowcount = AgentExecution.objects.filter(
                                id=_hb_execution_id
                            ).update(last_heartbeat_at=timezone.now())
                            tick_count += 1
                            if rowcount != 1:
                                logger.warning(
                                    f"[heartbeat] tick rowcount mismatch "
                                    f"agent={agent_name} execution_id={_hb_execution_id} "
                                    f"tick={tick_count} rowcount={rowcount} "
                                    f"(expected 1 — row may have been deleted)"
                                )
                            else:
                                logger.info(
                                    f"[heartbeat] tick agent={agent_name} "
                                    f"execution_id={_hb_execution_id} tick={tick_count} "
                                    f"rowcount={rowcount} next_sleep={_HB_TICK_S}s"
                                )
                        except Exception as e:
                            logger.exception(
                                f"[heartbeat] periodic write failed for {agent_name} "
                                f"execution_id={_hb_execution_id}: {e}"
                            )
                    next_sleep = _HB_TICK_S
            finally:
                logger.info(
                    f"[heartbeat] thread exit agent={agent_name} "
                    f"execution_id={_hb_execution_id} total_ticks={tick_count}"
                )

        _hb_thread = None
        if execution_record:
            # Immediate heartbeat so last_heartbeat_at is never null for live executions
            try:
                execution_record.touch_heartbeat()
            except Exception as e:
                logger.exception(f"[heartbeat] initial write failed for {agent_name}: {e}")
            _hb_thread = threading.Thread(
                target=_heartbeat_loop,
                daemon=True,
                name=f"exec-heartbeat-{str(_hb_execution_id)[:8]}",
            )
            _hb_thread.start()

        try:
            _pool = _TPE(max_workers=1)
            _future = _pool.submit(_run_route)
            try:
                result = _future.result(timeout=_wall_timeout)
            finally:
                # Session 1075: shutdown(wait=False) to avoid blocking on hung threads.
                # The `with` statement calls shutdown(wait=True) which blocks until the
                # thread finishes — defeating the timeout if the LLM call is truly hung.
                _pool.shutdown(wait=False)
                # Session 1100: Stop heartbeat thread
                _hb_stop.set()
        except _FuturesTimeout:
            _elapsed = time.time() - execution_start
            logger.error(
                f"[execute_agent_task] WALL-CLOCK TIMEOUT: {agent_name} exceeded "
                f"{_wall_timeout}s limit — killing"
            )
            _record_timeout_signature(
                agent_name=agent_name,
                timeout_source='wall_clock',
                elapsed_seconds=_elapsed,
                execution_id=execution_record.id if execution_record else None,
                task_name='core.tasks.execute_agent_task',
            )
            # Session 1095: Record timeout for circuit breaker
            _circuit_breaker_record_timeout(agent_name, task)
            _circuit_breaker_release(agent_name, task)

            from core.agents.base_agent import AgentResult
            result = AgentResult(
                success=False,
                error=f'{agent_name} exceeded {_wall_timeout}s wall-clock timeout',
                agent_name=agent_name,
                execution_time_ms=int(_elapsed * 1000),
            )

        execution_time_ms = int((time.time() - execution_start) * 1000)

        # Update execution record
        if execution_record:
            execution_record.status = 'completed' if result.success else 'failed'
            execution_record.execution_time_ms = execution_time_ms
            # Session 1076: Sanitize output_data — agent results may contain
            # UUID/datetime objects that aren't JSON-serializable. Force through
            # json.dumps(default=str) round-trip to coerce everything to strings.
            import json as _json
            _raw_output = {
                'content': result.content[:5000] if result.content else None,
                'metadata': getattr(result, 'data', {}) or {},
            }
            try:
                execution_record.output_data = _json.loads(_json.dumps(_raw_output, default=str))
            except (TypeError, ValueError):
                execution_record.output_data = {'content': str(result.content)[:5000] if result.content else None}
            # Session 1084 round 48: build update_fields dynamically so
            # last_heartbeat_at is excluded from save(). Prevents the
            # heartbeat thread's queryset update() from being stomped by
            # full-instance save() reading stale in-memory fields.
            _update_fields = [
                'status', 'execution_time_ms', 'output_data', 'completed_at',
            ]
            if not result.success:
                # Session 1068: Ensure error_message is never blank — fall back through
                # error, message, then generic label
                execution_record.error_message = (
                    result.error or result.message or 'Agent returned failure with no error details'
                )[:2000]
                _update_fields.append('error_message')
            execution_record.completed_at = timezone.now()
            execution_record.save(update_fields=_update_fields)

            # Update agent metrics
            Agent.objects.filter(pk=agent_obj.pk).update(
                total_executions=F('total_executions') + 1,
                successful_executions=F('successful_executions') + (1 if result.success else 0)
            )

        if execution_time_ms > 2_400_000:  # 40 min
            logger.warning(
                f"[execute_agent_task] SLOW AGENT: {agent_name} took "
                f"{execution_time_ms // 60_000}min — approaching timeout"
            )

        # Session 1095: Release circuit breaker single-flight lock
        _circuit_breaker_release(agent_name, task)

        logger.info(
            f"[execute_agent_task] Completed: {agent_name} "
            f"(success={result.success}, time={execution_time_ms}ms)"
        )

        # Push notification for completed media jobs
        _MEDIA_AGENTS = frozenset({
            'ImageAgent', 'VideoAgent', 'AudioAgent', 'TalkingCharacterAgent',
            'ImageEditingAgent', 'VideoEditingAgent', 'ThreeDAgent', 'ResolveAgent',
            # Also match router-normalized names
            'image_generation_agent', 'video_generation_agent',
            'audio_generation_agent', 'talking_character_agent',
        })
        _MEDIA_TYPE_LABELS = {
            'ImageAgent': 'image', 'VideoAgent': 'video',
            'AudioAgent': 'audio', 'TalkingCharacterAgent': 'talking character video',
            'ImageEditingAgent': 'edited image', 'VideoEditingAgent': 'edited video',
            'ThreeDAgent': '3D render', 'ResolveAgent': 'color-graded video',
            'image_generation_agent': 'image', 'video_generation_agent': 'video',
            'audio_generation_agent': 'audio', 'talking_character_agent': 'talking character video',
        }
        if agent_name in _MEDIA_AGENTS and result.success:
            push_user_id = context.get('user_id')
            if push_user_id:
                try:
                    from core.services.expo_push import send_push_to_user
                    media_type = _MEDIA_TYPE_LABELS.get(agent_name, 'media')
                    send_push_to_user(
                        user_id=push_user_id,
                        title=f'Your {media_type} is ready!',
                        body=(task[:80] + '...') if len(task) > 80 else task,
                        route='/media',
                        object_type='media_complete',
                        object_id=str(execution_record.id) if execution_record else None,
                    )
                except Exception as e:
                    logger.warning('[execute_agent_task] Push failed: %s', e)

        return {
            'success': result.success,
            'agent_name': agent_name,
            'task': task,
            'content': result.content[:1000] if result.content else None,
            'execution_time_ms': execution_time_ms,
            'execution_id': str(execution_record.id) if execution_record else None,
            'conversation_id': conversation_id,
        }

    except SoftTimeLimitExceeded:
        execution_time_ms = int((time.time() - execution_start) * 1000)
        logger.error(f"[execute_agent_task] KILLED by soft_time_limit: {agent_name} after {execution_time_ms}ms")
        _circuit_breaker_record_timeout(agent_name, task)
        _circuit_breaker_release(agent_name, task)
        if execution_record:
            execution_record.status = 'failed'
            execution_record.error_message = 'Celery soft_time_limit exceeded (60 min)'
            execution_record.execution_time_ms = execution_time_ms
            execution_record.completed_at = timezone.now()
            # Session 1084 round 48: update_fields excludes last_heartbeat_at
            # to avoid stomping the heartbeat thread's queryset update().
            execution_record.save(update_fields=[
                'status', 'error_message', 'execution_time_ms', 'completed_at',
            ])
        return {
            'success': False,
            'agent_name': agent_name,
            'task': task,
            'error': 'Celery soft_time_limit exceeded (60 min)',
            'execution_time_ms': execution_time_ms,
            'conversation_id': conversation_id,
        }

    except Exception as e:
        execution_time_ms = int((time.time() - execution_start) * 1000)
        logger.error(f"[execute_agent_task] Failed: {agent_name} - {e}")
        _circuit_breaker_release(agent_name, task)

        # Update execution record on failure
        if execution_record:
            execution_record.status = 'failed'
            execution_record.error_message = str(e) or f'{type(e).__name__}: (no message)'
            execution_record.execution_time_ms = execution_time_ms
            execution_record.completed_at = timezone.now()
            # Session 1084 round 48: update_fields excludes last_heartbeat_at
            # to avoid stomping the heartbeat thread's queryset update().
            execution_record.save(update_fields=[
                'status', 'error_message', 'execution_time_ms', 'completed_at',
            ])

        # Retry on certain errors
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)

        return {
            'success': False,
            'agent_name': agent_name,
            'task': task,
            'error': str(e),
            'execution_time_ms': execution_time_ms,
            'conversation_id': conversation_id,
        }


# ==================== CREATE TALKING VIDEO PIPELINE ====================




def _impl_record_all_user_style_evolution():
    """
    Daily task to record style evolution snapshots for all active users.

    Session 210: Runs at 12:30 AM daily to capture each user's style distribution.
    This enables trend analysis and shift detection over time.
    """
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from datetime import timedelta
    from core.services import get_learning_service

    User = get_user_model()
    service = get_learning_service()

    logger.info("📊 [STYLE EVOLUTION] Starting daily style evolution snapshot...")

    # Get users who have been active in the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)

    try:
        # Get users with recent behavior signals
        from core.models_unified_system import UserBehaviorSignal
        active_user_ids = UserBehaviorSignal.objects.filter(
            created_at__gte=thirty_days_ago
        ).values_list('user_id', flat=True).distinct()

        active_user_ids = list(set(active_user_ids))
        logger.info(f"📊 [STYLE EVOLUTION] Found {len(active_user_ids)} active users")

        stats = {
            'users_processed': 0,
            'snapshots_created': 0,
            'already_exists': 0,
            'no_data': 0,
            'errors': 0,
        }

        for user_id in active_user_ids:
            try:
                # Record evolution for each content domain
                for domain in ['image', 'video', 'audio']:
                    result = service.record_daily_evolution(user_id, domain)

                    if result:
                        if result.get('already_exists'):
                            stats['already_exists'] += 1
                        else:
                            stats['snapshots_created'] += 1
                    else:
                        stats['no_data'] += 1

                stats['users_processed'] += 1

            except Exception as e:
                logger.error(f"❌ [STYLE EVOLUTION] Error processing user {user_id}: {e}")
                stats['errors'] += 1

        logger.info(
            f"📊 [STYLE EVOLUTION] Complete: "
            f"{stats['users_processed']} users, "
            f"{stats['snapshots_created']} new snapshots, "
            f"{stats['already_exists']} already existed, "
            f"{stats['errors']} errors"
        )

        return {
            'status': 'completed',
            **stats
        }

    except Exception as e:
        logger.error(f"❌ [STYLE EVOLUTION] Task failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


# =============================================================================
# SESSION 213: SCHEDULED WORKFLOW EXECUTION
# =============================================================================



def _impl_run_agent_learning_cycle():
    """
    Main learning cycle - agents share knowledge with connected agents.
    Runs every 10 minutes to facilitate continuous learning.

    This creates the "agents learning from each other" effect:
    1. Select active learning connections
    2. For each connection, transfer relevant knowledge
    3. Track what was learned and how useful it was
    4. Update connection strength based on successful transfers

    Session 592: Teaching Diversity Fix
    Problem: Teaching was concentrated in few agents (top 2 = 41% of transfers)
    Solution: Minimum slots for underrepresented + weighted exploration
    """
    import random
    from datetime import timedelta
    from django.utils import timezone
    from django.db.models import Count
    from core.models import (
        Agent, AgentLearningConnection, AgentKnowledgeSource, KnowledgeTransfer,
        MythologyQuarantine  # Session 541: Quarantine for blocked transfers
    )

    logger.info("🧠 [LEARNING] Starting autonomous agent learning cycle...")

    try:
        # =================================================================
        # Session 592: Teaching Diversity Selection
        # =================================================================
        # Instead of pure random selection which favors high-connection agents,
        # we use a two-tier approach:
        # 1. MIN_DIVERSITY_SLOTS: Reserved for underrepresented teachers
        # 2. EXPLORATION_SLOTS: Weighted selection favoring low-transfer agents
        # =================================================================

        TOTAL_SLOTS = 10
        MIN_DIVERSITY_SLOTS = 3  # Guaranteed slots for underrepresented teachers
        EXPLORATION_SLOTS = 7   # Weighted exploration slots

        # Get transfer counts per teacher in last 24h
        since_24h = timezone.now() - timedelta(hours=24)
        transfer_counts = KnowledgeTransfer.objects.filter(
            created_at__gte=since_24h
        ).values('connection__teacher_agent_id').annotate(count=Count('id'))
        transfer_map = {t['connection__teacher_agent_id']: t['count'] for t in transfer_counts}

        # Get all active connections
        all_connections = list(AgentLearningConnection.objects.filter(
            is_active=True
        ).select_related('teacher_agent', 'student_agent'))

        if not all_connections:
            logger.warning("🧠 [LEARNING] No active connections found")
            return {'transfers': 0, 'events': []}

        # Group connections by teacher
        teachers_by_transfers = {}
        for conn in all_connections:
            teacher_id = conn.teacher_agent_id
            count = transfer_map.get(teacher_id, 0)
            if teacher_id not in teachers_by_transfers:
                teachers_by_transfers[teacher_id] = {'count': count, 'connections': [], 'name': conn.teacher_agent.name}
            teachers_by_transfers[teacher_id]['connections'].append(conn)

        # =================================================================
        # Option B: Minimum Teaching Slots
        # Sort teachers by transfer count (ascending) and give slots to lowest
        # =================================================================
        sorted_teachers = sorted(teachers_by_transfers.items(), key=lambda x: x[1]['count'])

        diversity_connections = []
        diversity_teachers = set()
        for teacher_id, data in sorted_teachers:
            if len(diversity_connections) >= MIN_DIVERSITY_SLOTS:
                break
            # Pick one random connection from this underrepresented teacher
            conn = random.choice(data['connections'])
            diversity_connections.append(conn)
            diversity_teachers.add(teacher_id)
            logger.debug(f"🎯 [DIVERSITY] Reserved slot for {data['name']} (transfers: {data['count']})")

        # =================================================================
        # Option A: Weighted Exploration
        # Weight = 1 / (transfer_count + 1) so low-transfer agents get higher probability
        # This breaks the feedback loop where popular agents get more popular
        # =================================================================
        remaining_connections = [c for c in all_connections if c not in diversity_connections]

        exploration_connections = []
        if remaining_connections and EXPLORATION_SLOTS > 0:
            # Calculate weights - inverse of transfer count
            weights = []
            for conn in remaining_connections:
                teacher_id = conn.teacher_agent_id
                count = transfer_map.get(teacher_id, 0)
                # Inverse weighting: agents with 0 transfers get weight 1.0
                # agents with 10 transfers get weight 0.09
                weight = 1.0 / (count + 1)
                weights.append(weight)

            # Normalize weights
            total_weight = sum(weights)
            if total_weight > 0:
                weights = [w / total_weight for w in weights]

                try:
                    # Weighted random selection without replacement
                    exploration_connections = []
                    remaining_pool = list(zip(remaining_connections, weights))

                    for _ in range(min(EXPLORATION_SLOTS, len(remaining_pool))):
                        if not remaining_pool:
                            break
                        conns, wts = zip(*remaining_pool)
                        # Renormalize weights
                        total_wt = sum(wts)
                        if total_wt == 0:
                            break
                        norm_wts = [w / total_wt for w in wts]
                        # Select one
                        selected = random.choices(list(conns), weights=norm_wts, k=1)[0]
                        exploration_connections.append(selected)
                        # Remove selected from pool
                        remaining_pool = [(c, w) for c, w in remaining_pool if c != selected]

                except Exception as e:
                    logger.warning(f"⚠️ [LEARNING] Weighted selection failed, using random: {e}")
                    exploration_connections = random.sample(
                        remaining_connections,
                        min(EXPLORATION_SLOTS, len(remaining_connections))
                    )
            else:
                # No weights, fall back to random
                exploration_connections = random.sample(
                    remaining_connections,
                    min(EXPLORATION_SLOTS, len(remaining_connections))
                )

        # Combine diversity + exploration slots
        connections = diversity_connections + exploration_connections

        # Log selection stats
        diversity_count = len(diversity_connections)
        exploration_count = len(exploration_connections)
        unique_teachers = len(set(c.teacher_agent_id for c in connections))
        logger.info(f"🧠 [LEARNING] Selected {len(connections)} connections: "
                   f"{diversity_count} diversity + {exploration_count} exploration, "
                   f"{unique_teachers} unique teachers")

        transfers_made = 0
        mythology_blocks = 0  # Session 541: Track mythology validation blocks
        learning_events = []

        for connection in connections:
            teacher = connection.teacher_agent
            student = connection.student_agent

            # Get teacher's recent knowledge that student doesn't have
            # Session 357: Expanded default to include ALL knowledge types for better sharing
            ALL_KNOWLEDGE_TYPES = ['trend', 'opportunity', 'market', 'user_behavior', 'content_idea',
                                   'tool_discovery', 'pricing', 'research', 'insight', 'strategy',
                                   'collaborative_insight']
            # Session 1035: Recency gate — only transfer knowledge updated within 90 days
            # Prevents stale/outdated data from propagating through the learning network
            recency_cutoff = timezone.now() - timedelta(days=90)
            teacher_knowledge = AgentKnowledgeSource.objects.filter(
                agent=teacher,
                is_active=True,
                knowledge_type__in=connection.shareable_knowledge_types or ALL_KNOWLEDGE_TYPES,
                last_updated_at__gte=recency_cutoff,
            ).exclude(
                # Also honor expires_at if set
                expires_at__lt=timezone.now(),
            ).order_by('-confidence_score', '-last_updated_at')[:5]

            if not teacher_knowledge:
                logger.debug(
                    f"🧠 [LEARNING] {teacher.name} has no knowledge updated within 90 days — skipping"
                )

            for knowledge in teacher_knowledge:
                # Session 358: Enhanced Delta Detection using semantic similarity
                # Uses embeddings + cosine similarity to detect semantic duplicates
                # This catches cases like "AI Content Tools" vs "Content Creation AI Tools"
                try:
                    from core.services.knowledge_similarity import get_knowledge_similarity_service
                    similarity_service = get_knowledge_similarity_service()

                    should_transfer, reason = similarity_service.should_transfer_knowledge(
                        student_agent=student,
                        teacher_knowledge=knowledge,
                        threshold=0.80  # 80% similarity = duplicate
                    )

                    if not should_transfer:
                        logger.debug(f"[LEARNING] Skipping transfer: {reason}")
                        continue

                except Exception as e:
                    # Fallback to Session 357 exact title matching if semantic fails
                    logger.warning(f"Semantic similarity failed, using fallback: {e}")
                    import re
                    clean_title = re.sub(r'^\[Learned\]\s*', '', knowledge.title or '').strip()
                    while clean_title.startswith('[Learned]'):
                        clean_title = clean_title[9:].strip()

                    from django.db.models import Q
                    student_has_similar = AgentKnowledgeSource.objects.filter(
                        agent=student,
                        knowledge_type=knowledge.knowledge_type
                    ).filter(
                        Q(title=clean_title) |
                        Q(title=f"[Learned] {clean_title}") |
                        Q(title__iexact=knowledge.title)
                    ).exists()

                    if student_has_similar:
                        continue

                # Session 541: Mythology validation for knowledge transfers
                # Prevents unrealistic claims from propagating through the learning network
                try:
                    from ai_core.agents.mythology_validator import mythology_enforcer

                    # Validate the knowledge content before transfer
                    knowledge_content = knowledge.summary or knowledge.title or ""
                    validation = mythology_enforcer.enforce(
                        f"{teacher.name}→{student.name}",
                        knowledge_content
                    )

                    if validation.get('mythology_corrected'):
                        # Knowledge contains unrealistic claims - quarantine instead of just logging
                        mythology_blocks += 1

                        # Get violation details from the original validation
                        original_validation = mythology_enforcer.validator.validate_output(
                            f"{teacher.name}→{student.name}",
                            knowledge_content
                        )
                        violations = original_validation.get('violations', [])
                        first_violation_type = violations[0]['type'] if violations else 'spider_data_myth'

                        # Create quarantine entry with full context
                        try:
                            MythologyQuarantine.objects.create(
                                teacher_agent=teacher,
                                student_agent=student,
                                connection=connection,
                                source_knowledge=knowledge,
                                blocked_title=knowledge.title[:500] if knowledge.title else "Unknown",
                                blocked_content=knowledge_content[:2000],
                                blocked_summary=knowledge.summary[:500] if knowledge.summary else "",
                                violation_type=first_violation_type,
                                violation_count=len(violations),
                                violation_patterns=[v.get('pattern', '') for v in violations[:5]],
                                mythology_warning=validation.get('warning', ''),
                                spider_sources=knowledge.source_spider_names or [],
                                source_urls=[],  # Could be extracted from knowledge if available
                            )
                        except Exception as q_err:
                            logger.warning(f"⚠️ [MYTHOLOGY] Quarantine creation failed: {q_err}")

                        # Apply trust decay to the connection
                        connection.apply_mythology_penalty()

                        logger.warning(
                            f"🚨 [MYTHOLOGY] Blocked & quarantined {teacher.name}→{student.name}: "
                            f"'{knowledge.title[:50]}' ({len(violations)} violations, "
                            f"connection strength now {connection.strength:.2f})"
                        )
                        continue

                except Exception as myth_err:
                    # If mythology validation fails, log but continue (don't block learning)
                    logger.warning(f"⚠️ [MYTHOLOGY] Validation error (continuing): {myth_err}")

                # Knowledge is new and validated - proceed with transfer
                # Session 350: Strip existing [Learned] prefixes to prevent accumulation
                import re
                clean_title = re.sub(r'^\[Learned\]\s*', '', knowledge.title).strip()
                # Also strip from beginning multiple times in case of nested
                while clean_title.startswith('[Learned]'):
                    clean_title = clean_title[9:].strip()

                # Create knowledge transfer record
                usefulness = random.uniform(0.6, 1.0)  # Simulate usefulness

                # Session 532: Include actual knowledge content in transfer summary
                # Session 1035: Include timestamps and source provenance
                knowledge_content = knowledge.summary[:500] if knowledge.summary else ""
                data_window = f"Data from: {knowledge.first_discovered_at.strftime('%Y-%m-%d')}"
                if knowledge.last_updated_at:
                    data_window += f" → {knowledge.last_updated_at.strftime('%Y-%m-%d')}"
                source_info = ""
                if knowledge.source_spider_names:
                    real_spiders = [s for s in knowledge.source_spider_names if not s.startswith('learned_from_')]
                    if real_spiders:
                        source_info = f"\nSources: {', '.join(real_spiders[:5])}"
                transfer_summary = (
                    f"{teacher.name} shared '{clean_title}' with {student.name}.\n"
                    f"{data_window}{source_info}\n\n{knowledge_content}"
                )

                transfer = KnowledgeTransfer.objects.create(
                    connection=connection,
                    source_knowledge=knowledge,
                    transfer_summary=transfer_summary,
                    key_points=knowledge.key_insights[:5] if knowledge.key_insights else [],
                    was_useful=usefulness > 0.7,
                    usefulness_score=usefulness,
                    was_applied=random.random() > 0.3,  # 70% chance of being applied
                )

                # Create new knowledge for student (adapted from teacher's)
                # Session 532: Include full summary for richer knowledge transfer
                student_summary = f"Learned from {teacher.name}:\n\n{knowledge.summary}" if knowledge.summary else f"Knowledge transferred from {teacher.name}"

                # Session 1035: Carry original freshness instead of resetting to 1.0
                # This prevents stale knowledge from appearing "fresh" after transfer
                knowledge_age_days = (timezone.now() - knowledge.first_discovered_at).days if knowledge.first_discovered_at else 0
                inherited_freshness = max(0.1, 1.0 - (knowledge_age_days / 180.0))  # Decays over 6 months

                new_knowledge = AgentKnowledgeSource.objects.create(
                    agent=student,
                    knowledge_type=knowledge.knowledge_type,
                    spider_category=knowledge.spider_category,
                    source_spider_names=knowledge.source_spider_names + [f'learned_from_{teacher.name}'],
                    title=f"[Learned] {clean_title}",
                    summary=student_summary,
                    key_insights=knowledge.key_insights,
                    data_points_count=knowledge.data_points_count,
                    confidence_score=knowledge.confidence_score * 0.9,  # Slightly lower confidence
                    relevance_score=knowledge.relevance_score,
                    freshness_score=inherited_freshness,  # Session 1035: Inherit age-based freshness
                    is_active=True,
                    expires_at=knowledge.expires_at,  # Session 1035: Carry expiry from source
                )

                transfers_made += 1
                learning_events.append({
                    'teacher': teacher.name,
                    'student': student.name,
                    'knowledge': knowledge.title[:50],
                    'type': connection.learning_type,
                    'usefulness': usefulness
                })

                # Update connection stats
                connection.total_transfers += 1
                if usefulness > 0.7:
                    connection.successful_transfers += 1
                connection.last_transfer_at = timezone.now()

                # Update connection strength based on success
                if connection.total_transfers > 0:
                    success_rate = connection.successful_transfers / connection.total_transfers
                    connection.strength = min(1.0, connection.strength + (success_rate * 0.05))
                    connection.avg_improvement_score = (
                        connection.avg_improvement_score * 0.9 + usefulness * 0.1
                    )
                connection.save()

                logger.info(
                    f"🎓 [LEARNING] {teacher.name} → {student.name}: "
                    f"'{knowledge.title[:30]}...' (usefulness: {usefulness:.2f})"
                )

                # Session 429: Send Discord notification for knowledge transfer
                # Session 435: Format summary nicely instead of showing raw JSON
                try:
                    from core.services.discord_notifications import discord_notify

                    # Parse JSON summary into human-readable format
                    formatted_summary = f"{teacher.name} shared knowledge with {student.name}"
                    if knowledge.summary:
                        try:
                            import json
                            data = json.loads(knowledge.summary)
                            if isinstance(data, dict):
                                parts = []
                                if data.get('query'):
                                    parts.append(f"Query: \"{data['query'][:80]}\"")
                                if data.get('sources_used'):
                                    sources = data['sources_used']
                                    if isinstance(sources, list):
                                        parts.append(f"Sources: {', '.join(sources[:3])}")
                                if data.get('result_count'):
                                    parts.append(f"Results: {data['result_count']} items")
                                if data.get('insight'):
                                    parts.append(f"Insight: {data['insight'][:100]}")
                                if data.get('recommendation'):
                                    parts.append(f"Recommendation: {data['recommendation'][:100]}")
                                if parts:
                                    formatted_summary = "\n".join(parts)
                                else:
                                    # Fallback: show first few key-value pairs
                                    formatted_summary = "\n".join([
                                        f"{k}: {str(v)[:50]}" for k, v in list(data.items())[:3]
                                    ])
                        except (json.JSONDecodeError, TypeError):
                            formatted_summary = knowledge.summary[:200]

                    discord_notify.send_knowledge(
                        agent_name=f"{teacher.name} → {student.name}",
                        title=clean_title[:100],
                        summary=formatted_summary,
                        knowledge_type=knowledge.knowledge_type or 'insight',
                        confidence=usefulness
                    )
                except Exception as discord_err:
                    logger.debug(f"Discord notification failed: {discord_err}")

                # Only transfer one piece of knowledge per connection per cycle
                break

        # Broadcast learning events via Redis for real-time updates
        if learning_events:
            try:
                import redis
                import json
                r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'), decode_responses=True)

                for event in learning_events:
                    r.publish('agent_learning', json.dumps({
                        'type': 'knowledge_transfer',
                        'data': event,
                        'timestamp': timezone.now().isoformat()
                    }))

                # Also store last learning events for dashboard
                r.setex(
                    'agent_learning:recent_events',
                    3600,  # 1 hour TTL
                    json.dumps(learning_events)
                )
                r.set('agent_learning:last_cycle', timezone.now().isoformat())
                r.set('agent_learning:total_transfers_today',
                      int(r.get('agent_learning:total_transfers_today') or 0) + transfers_made)
            except Exception as redis_err:
                logger.warning(f"Redis broadcast failed: {redis_err}")

        # Session 541: Include mythology blocks in log
        mythology_msg = f", {mythology_blocks} quarantined by mythology" if mythology_blocks > 0 else ""
        logger.info(
            f"🧠 [LEARNING] Cycle complete: {transfers_made} knowledge transfers made "
            f"across {len(connections)} connections{mythology_msg}"
        )

        # Session 541: Get quarantine stats for return
        quarantine_pending = MythologyQuarantine.objects.filter(status='pending').count()

        return {
            'status': 'success',
            'transfers_made': transfers_made,
            'mythology_blocks': mythology_blocks,  # Session 541: Track quality gate blocks
            'quarantine_pending': quarantine_pending,  # Session 541: Total awaiting review
            'connections_processed': len(connections),
            'learning_events': learning_events,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"🧠 [LEARNING] Learning cycle failed: {e}")
        return {'status': 'failed', 'error': str(e)}




def _impl_agent_think_and_synthesize():
    """
    Agents "think" about their knowledge and synthesize new insights.
    This simulates agents processing what they've learned and forming new ideas.

    Runs every 30 minutes.
    """
    import random
    from django.utils import timezone
    from core.models import Agent, AgentKnowledgeSource

    logger.info("💭 [THINKING] Agents are synthesizing knowledge...")

    try:
        # Get agents with enough knowledge to synthesize
        agents = Agent.objects.filter(
            is_active=True
        ).prefetch_related('knowledge_sources')

        insights_created = 0

        for agent in agents:
            knowledge_count = agent.knowledge_sources.filter(is_active=True).count()

            # Agents need at least 10 knowledge items to synthesize
            if knowledge_count >= 10:
                # Get diverse knowledge types
                knowledge_by_type = {}
                for k in agent.knowledge_sources.filter(is_active=True)[:20]:
                    if k.knowledge_type not in knowledge_by_type:
                        knowledge_by_type[k.knowledge_type] = []
                    knowledge_by_type[k.knowledge_type].append(k)

                # If agent has knowledge in multiple areas, synthesize
                if len(knowledge_by_type) >= 2:
                    types = list(knowledge_by_type.keys())[:2]
                    k1 = random.choice(knowledge_by_type[types[0]])
                    k2 = random.choice(knowledge_by_type[types[1]])

                    # Create synthesized insight
                    synthesis_title = f"[Synthesis] Combining {types[0]} and {types[1]} insights"
                    synthesis_summary = (
                        f"{agent.name} synthesized knowledge from {k1.title[:30]} "
                        f"and {k2.title[:30]} to form new understanding."
                    )

                    # Check if similar synthesis exists
                    if not AgentKnowledgeSource.objects.filter(
                        agent=agent,
                        title__icontains="Synthesis",
                        knowledge_type='trend'  # Syntheses are trends
                    ).exists():
                        AgentKnowledgeSource.objects.create(
                            agent=agent,
                            knowledge_type='trend',
                            title=synthesis_title,
                            summary=synthesis_summary,
                            source_spider_names=[f'synthesized_by_{agent.name}'],
                            key_insights=[
                                f"Combined insight from {types[0]} and {types[1]}",
                                k1.key_insights[0] if k1.key_insights else "Primary source",
                                k2.key_insights[0] if k2.key_insights else "Secondary source"
                            ],
                            data_points_count=k1.data_points_count + k2.data_points_count,
                            confidence_score=(k1.confidence_score + k2.confidence_score) / 2 * 0.85,
                            freshness_score=1.0,
                            is_active=True,
                        )
                        insights_created += 1

                        logger.info(f"💡 [THINKING] {agent.name} synthesized: {synthesis_title[:50]}")

        # Broadcast thinking results
        try:
            import redis
            import json
            r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'), decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'synthesis_complete',
                'insights_created': insights_created,
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.warning(f"Redis publish failed (synthesis_complete): {e}")

        logger.info(f"💭 [THINKING] Synthesis complete: {insights_created} new insights created")

        return {
            'status': 'success',
            'insights_created': insights_created,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"💭 [THINKING] Synthesis failed: {e}")
        return {'status': 'failed', 'error': str(e)}




def _impl_broadcast_learning_status():
    """
    Broadcast current learning network status via WebSocket.
    Called frequently to keep the UI updated with learning activity.
    """
    from django.utils import timezone
    from core.models import Agent, AgentLearningConnection, AgentKnowledgeSource, KnowledgeTransfer
    from datetime import timedelta

    try:
        import redis
        import json
        r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'), decode_responses=True)

        now = timezone.now()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)

        # Gather stats
        stats = {
            'total_agents': Agent.objects.filter(is_active=True).count(),
            'total_knowledge': AgentKnowledgeSource.objects.filter(is_active=True).count(),
            'total_connections': AgentLearningConnection.objects.filter(is_active=True).count(),
            'transfers_last_hour': KnowledgeTransfer.objects.filter(created_at__gte=last_hour).count(),
            'transfers_last_day': KnowledgeTransfer.objects.filter(created_at__gte=last_day).count(),
            'active_learners': Agent.objects.filter(
                teachers__last_transfer_at__gte=last_hour
            ).distinct().count(),
            'active_teachers': Agent.objects.filter(
                students__last_transfer_at__gte=last_hour
            ).distinct().count(),
            'timestamp': now.isoformat()
        }

        # Top learning agents
        top_learners = []
        for agent in Agent.objects.filter(is_active=True).order_by('-effectiveness_score')[:5]:
            top_learners.append({
                'name': agent.name,
                'knowledge_count': agent.knowledge_sources.filter(is_active=True).count(),
                'effectiveness': agent.effectiveness_score,
                'teaches': agent.students.count(),
                'learns_from': agent.teachers.count()
            })

        stats['top_learners'] = top_learners

        # Recent transfers
        recent_transfers = []
        for transfer in KnowledgeTransfer.objects.order_by('-created_at')[:5]:
            recent_transfers.append({
                'teacher': transfer.connection.teacher_agent.name,
                'student': transfer.connection.student_agent.name,
                'summary': transfer.transfer_summary[:50],
                'useful': transfer.was_useful,
                'time': transfer.created_at.isoformat()
            })

        stats['recent_transfers'] = recent_transfers

        # Publish to Redis (legacy)
        r.publish('agent_learning', json.dumps({
            'type': 'status_update',
            'data': stats
        }))

        # Cache for API access
        r.setex('agent_learning:status', 300, json.dumps(stats))

        # Session 324: Broadcast to Learning Feed WebSocket channel
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            # Build feed items for WebSocket
            feed_items = []
            for transfer in KnowledgeTransfer.objects.select_related(
                'connection__teacher_agent',
                'connection__student_agent'
            ).order_by('-created_at')[:20]:
                teacher = transfer.connection.teacher_agent
                student = transfer.connection.student_agent

                if teacher.id == student.id:
                    source = 'self_learning'
                    description = f"{teacher.name} acquired new knowledge"
                else:
                    source = 'knowledge_transfer'
                    description = f"{teacher.name} shared knowledge with {student.name}"

                feed_items.append({
                    'timestamp': transfer.created_at.isoformat(),
                    'type': source,
                    'source': 'Knowledge transfer',
                    'description': description,
                    'knowledge': transfer.transfer_summary[:100] if transfer.transfer_summary else 'Knowledge shared',
                    'teacher': teacher.name,
                    'student': student.name,
                    'was_useful': transfer.was_useful,
                    # Session 761: Use usefulness_score as effectiveness_gain proxy
                    'effectiveness_gain': transfer.usefulness_score if transfer.usefulness_score else 0.0
                })

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'agent_learning_feed',
                {
                    'type': 'learning_feed_update',
                    'feed_items': feed_items,
                    'stats': stats
                }
            )
            logger.info(f"🧠 [LEARNING FEED] Broadcast {len(feed_items)} items to WebSocket")
        except Exception as ws_error:
            logger.warning(f"🧠 [LEARNING FEED] WebSocket broadcast failed: {ws_error}")

        return stats

    except Exception as e:
        logger.exception(f"📡 [BROADCAST] Status broadcast failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 728: Knowledge Source Validation
# Validates AgentKnowledgeSource records based on confidence, mythology checks,
# and data point counts. Sets is_validated=True for valid knowledge.
# =============================================================================



def _impl_validate_knowledge_sources():
    """
    Validate AgentKnowledgeSource records and set is_validated=True.

    Session 728: Addresses the audit finding that all 3,909 knowledge records
    were unvalidated despite having high confidence scores.

    Validation Criteria:
    1. High confidence score (>=0.7) = auto-validate
    2. Medium confidence (0.4-0.7) + sufficient data points (>=5) = auto-validate
    3. Low confidence (<0.4) = requires human review (not auto-validated)
    4. Mythology check: Skip validation if content contains mythology patterns

    Runs daily at 3 AM.
    """
    from django.utils import timezone
    from django.db import transaction
    from core.models import AgentKnowledgeSource

    logger.info("✅ [VALIDATION] Starting knowledge source validation...")

    try:
        stats = {
            'total_checked': 0,
            'auto_validated_high_conf': 0,
            'auto_validated_medium_conf': 0,
            'mythology_blocked': 0,
            'needs_review': 0,
            'already_validated': 0,
            'errors': 0
        }

        # Get mythology enforcer for content validation
        mythology_enforcer = None
        try:
            from ai_core.agents.mythology_validator import mythology_enforcer as enforcer
            mythology_enforcer = enforcer
        except Exception as e:
            logger.warning(f"⚠️ [VALIDATION] Mythology enforcer not available: {e}")

        # Process unvalidated knowledge in batches
        batch_size = 100
        unvalidated = AgentKnowledgeSource.objects.filter(
            is_validated=False,
            is_active=True
        ).order_by('-confidence_score')

        total_unvalidated = unvalidated.count()
        logger.info(f"✅ [VALIDATION] Found {total_unvalidated} unvalidated knowledge sources")

        for knowledge in unvalidated.iterator(chunk_size=batch_size):
            stats['total_checked'] += 1

            try:
                # Check for mythology in content
                if mythology_enforcer:
                    content_to_check = f"{knowledge.title or ''} {knowledge.summary or ''}"
                    validation = mythology_enforcer.enforce(
                        f"Knowledge:{knowledge.agent.name if knowledge.agent else 'Unknown'}",
                        content_to_check
                    )

                    if validation.get('mythology_corrected'):
                        # Content contains mythology - don't validate
                        stats['mythology_blocked'] += 1
                        logger.debug(f"🚫 [VALIDATION] Mythology blocked: {knowledge.title[:50]}")
                        continue

                # Validation logic based on confidence and data points
                should_validate = False
                validation_reason = ""

                if knowledge.confidence_score >= 0.7:
                    # High confidence - auto-validate
                    should_validate = True
                    validation_reason = "high_confidence"
                    stats['auto_validated_high_conf'] += 1

                elif knowledge.confidence_score >= 0.4 and knowledge.data_points_count >= 5:
                    # Medium confidence with sufficient data points - auto-validate
                    should_validate = True
                    validation_reason = "medium_confidence_with_data"
                    stats['auto_validated_medium_conf'] += 1

                else:
                    # Low confidence or insufficient data - needs review
                    stats['needs_review'] += 1

                if should_validate:
                    with transaction.atomic():
                        knowledge.is_validated = True
                        knowledge.save(update_fields=['is_validated'])

                    logger.debug(
                        f"✅ [VALIDATION] Validated: {knowledge.title[:40]}... "
                        f"(reason: {validation_reason}, conf: {knowledge.confidence_score:.2f})"
                    )

            except Exception as e:
                stats['errors'] += 1
                logger.warning(f"⚠️ [VALIDATION] Error validating {knowledge.id}: {e}")
                continue

        # Log summary
        validated_count = stats['auto_validated_high_conf'] + stats['auto_validated_medium_conf']
        logger.info(
            f"✅ [VALIDATION] Complete: {validated_count} validated, "
            f"{stats['mythology_blocked']} blocked by mythology, "
            f"{stats['needs_review']} need review, "
            f"{stats['errors']} errors"
        )

        # Broadcast update via Redis
        try:
            import redis
            import json
            r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'), decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'knowledge_validation_complete',
                'data': stats,
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.warning(f"Redis publish failed (knowledge_validation): {e}")

        return {
            'status': 'success',
            **stats,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"✅ [VALIDATION] Knowledge validation failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 244: Daily Learning Embeddings
# Convert all agent learning (knowledge transfers, syntheses, insights) into
# searchable vector embeddings stored in PGVector. This enables semantic search
# across all agent learning and builds the foundation for long-term AI memory.
# =============================================================================



def _impl_embed_daily_agent_learning():
    """
    Create document embeddings for all agent learning activity.

    This task:
    1. Gathers all knowledge transfers, learned items, and syntheses from the last 24 hours
    2. Creates rich text documents from each learning event
    3. Generates embeddings using OpenAI
    4. Stores them in PGVector via DocumentEmbedding

    Runs daily at 2 AM to capture a full day's learning.
    This is the key to AI longevity - everything becomes a searchable document.
    """
    import asyncio
    from datetime import timedelta
    from django.utils import timezone
    from django.db import transaction
    from core.models import AgentKnowledgeSource, KnowledgeTransfer
    from content.models import Document, DocumentEmbedding, DocumentType, EmbeddingModel, ContentStatus, ContentSource
    from content.embeddings import EmbeddingManager

    logger.info("📚 [EMBEDDINGS] Starting daily agent learning embedding task...")

    def run_async(coro):
        """Run an async coroutine synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        embedding_manager = EmbeddingManager()
        cutoff = timezone.now() - timedelta(hours=24)

        stats = {
            'transfers_processed': 0,
            'learned_items_processed': 0,
            'syntheses_processed': 0,
            'embeddings_created': 0,
            'embeddings_failed': 0,
            'total_cost': 0.0
        }

        # Get or create a system user for the learning document
        system_user, _ = User.objects.get_or_create(
            username='system_learning',
            defaults={
                'email': 'system@learning.internal',
                'is_active': True,
            }
        )

        # Get or create the master learning document
        learning_doc, created = Document.objects.get_or_create(
            title='Agent Learning Knowledge Base',
            document_type=DocumentType.KNOWLEDGE_EXTRACT,
            defaults={
                'owner': system_user,
                'description': 'Embedded knowledge from agent-to-agent learning, syntheses, and insights',
                'raw_content': '',
                'processed_content': '',
                'status': ContentStatus.PROCESSED,
                'source': ContentSource.WORKFLOW,
                'tags': ['agent_learning', 'knowledge_transfer', 'synthesis', 'embedded']
            }
        )

        # Track existing chunk indices to avoid duplicates
        existing_indices = set(
            DocumentEmbedding.objects.filter(document=learning_doc)
            .values_list('chunk_index', flat=True)
        )
        next_index = max(existing_indices) + 1 if existing_indices else 0

        # 1. Process Knowledge Transfers
        recent_transfers = KnowledgeTransfer.objects.filter(
            created_at__gte=cutoff
        ).select_related(
            'connection__teacher_agent',
            'connection__student_agent',
            'source_knowledge'
        )

        for transfer in recent_transfers:
            # Create a unique identifier for this transfer
            transfer_id = f"transfer_{transfer.id}"

            # Build rich text document from transfer
            text_parts = [
                f"Knowledge Transfer Event",
                f"Teacher: {transfer.connection.teacher_agent.name if transfer.connection.teacher_agent else 'Unknown'}",
                f"Student: {transfer.connection.student_agent.name if transfer.connection.student_agent else 'Unknown'}",
                f"Knowledge Topic: {transfer.source_knowledge.title if transfer.source_knowledge else 'Unknown'}",
                f"Summary: {transfer.transfer_summary or 'No summary'}",
                f"Key Points: {', '.join(transfer.key_points) if transfer.key_points else 'No key points'}",
                f"Usefulness Score: {transfer.usefulness_score}",
                f"Was Applied: {transfer.was_applied}",
                f"Timestamp: {transfer.created_at.isoformat()}"
            ]

            if transfer.source_knowledge:
                text_parts.append(f"Source Knowledge Summary: {transfer.source_knowledge.summary[:500] if transfer.source_knowledge.summary else 'No summary'}")

            text = "\n".join(text_parts)

            # Generate embedding
            result = run_async(
                embedding_manager.generate_embedding(text, EmbeddingModel.OPENAI_SMALL)
            )

            if result.success:
                with transaction.atomic():
                    DocumentEmbedding.objects.update_or_create(
                        document=learning_doc,
                        chunk_index=next_index,
                        embedding_model=EmbeddingModel.OPENAI_SMALL,
                        defaults={
                            'chunk_text': text,
                            'chunk_size': len(text),
                            'embedding_vector': result.embedding,
                            'embedding_dimension': result.dimension,
                            'processing_time_ms': result.processing_time_ms,
                            'embedding_cost': result.cost,
                            'metadata': {
                                'type': 'knowledge_transfer',
                                'transfer_id': str(transfer.id),
                                'teacher': transfer.connection.teacher_agent.name if transfer.connection.teacher_agent else None,
                                'student': transfer.connection.student_agent.name if transfer.connection.student_agent else None,
                                'date': transfer.created_at.isoformat()
                            }
                        }
                    )
                next_index += 1
                stats['embeddings_created'] += 1
                stats['total_cost'] += float(result.cost)
            else:
                stats['embeddings_failed'] += 1
                logger.warning(f"📚 [EMBEDDINGS] Failed to embed transfer {transfer.id}: {result.error_message}")

            stats['transfers_processed'] += 1

        # 2. Process Learned Items (knowledge sources with [Learned] prefix)
        learned_items = AgentKnowledgeSource.objects.filter(
            first_discovered_at__gte=cutoff,
            title__startswith='[Learned]',
            is_active=True
        ).select_related('agent')

        for item in learned_items:
            text_parts = [
                f"Learned Knowledge Item",
                f"Agent: {item.agent.name if item.agent else 'Unknown'}",
                f"Title: {item.title}",
                f"Type: {item.knowledge_type}",
                f"Summary: {item.summary or 'No summary'}",
                f"Key Insights: {', '.join(str(i) for i in item.key_insights) if item.key_insights else 'No insights'}",
                f"Confidence: {item.confidence_score}",
                f"Data Points: {item.data_points_count}",
                f"Learned At: {item.first_discovered_at.isoformat()}"
            ]

            text = "\n".join(text_parts)

            result = run_async(
                embedding_manager.generate_embedding(text, EmbeddingModel.OPENAI_SMALL)
            )

            if result.success:
                with transaction.atomic():
                    DocumentEmbedding.objects.update_or_create(
                        document=learning_doc,
                        chunk_index=next_index,
                        embedding_model=EmbeddingModel.OPENAI_SMALL,
                        defaults={
                            'chunk_text': text,
                            'chunk_size': len(text),
                            'embedding_vector': result.embedding,
                            'embedding_dimension': result.dimension,
                            'processing_time_ms': result.processing_time_ms,
                            'embedding_cost': result.cost,
                            'metadata': {
                                'type': 'learned_item',
                                'knowledge_id': str(item.id),
                                'agent': item.agent.name if item.agent else None,
                                'knowledge_type': item.knowledge_type,
                                'date': item.first_discovered_at.isoformat()
                            }
                        }
                    )
                next_index += 1
                stats['embeddings_created'] += 1
                stats['total_cost'] += float(result.cost)
            else:
                stats['embeddings_failed'] += 1

            stats['learned_items_processed'] += 1

        # 3. Process Syntheses (knowledge sources with [Synthesis] prefix)
        syntheses = AgentKnowledgeSource.objects.filter(
            first_discovered_at__gte=cutoff,
            title__startswith='[Synthesis]',
            is_active=True
        ).select_related('agent')

        for synthesis in syntheses:
            text_parts = [
                f"Agent Synthesis - Combined Insight",
                f"Agent: {synthesis.agent.name if synthesis.agent else 'Unknown'}",
                f"Title: {synthesis.title}",
                f"Summary: {synthesis.summary or 'No summary'}",
                f"Key Insights: {', '.join(str(i) for i in synthesis.key_insights) if synthesis.key_insights else 'No insights'}",
                f"Confidence: {synthesis.confidence_score}",
                f"Source Data Points: {synthesis.data_points_count}",
                f"Synthesized At: {synthesis.first_discovered_at.isoformat()}"
            ]

            text = "\n".join(text_parts)

            result = run_async(
                embedding_manager.generate_embedding(text, EmbeddingModel.OPENAI_SMALL)
            )

            if result.success:
                with transaction.atomic():
                    DocumentEmbedding.objects.update_or_create(
                        document=learning_doc,
                        chunk_index=next_index,
                        embedding_model=EmbeddingModel.OPENAI_SMALL,
                        defaults={
                            'chunk_text': text,
                            'chunk_size': len(text),
                            'embedding_vector': result.embedding,
                            'embedding_dimension': result.dimension,
                            'processing_time_ms': result.processing_time_ms,
                            'embedding_cost': result.cost,
                            'metadata': {
                                'type': 'synthesis',
                                'knowledge_id': str(synthesis.id),
                                'agent': synthesis.agent.name if synthesis.agent else None,
                                'date': synthesis.first_discovered_at.isoformat()
                            }
                        }
                    )
                next_index += 1
                stats['embeddings_created'] += 1
                stats['total_cost'] += float(result.cost)
            else:
                stats['embeddings_failed'] += 1

            stats['syntheses_processed'] += 1

        # Update the document's last modified time
        learning_doc.save()

        # Broadcast success
        try:
            import redis
            import json
            r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'), decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'embeddings_complete',
                'stats': stats,
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.warning(f"Redis publish failed (embeddings_complete): {e}")

        logger.info(
            f"📚 [EMBEDDINGS] Daily embedding complete: "
            f"{stats['transfers_processed']} transfers, "
            f"{stats['learned_items_processed']} learned items, "
            f"{stats['syntheses_processed']} syntheses, "
            f"{stats['embeddings_created']} embeddings created, "
            f"${stats['total_cost']:.4f} total cost"
        )

        return {
            'status': 'success',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"📚 [EMBEDDINGS] Daily embedding failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 417: Comprehensive Agent Activity Embeddings
# Runs every 30 minutes to embed ALL agent activity:
# - Dreams (AgentDream)
# - Hive Mind Sessions (HiveMindSession)
# - Knowledge Sources (AgentKnowledgeSource) - including non-prefixed ones
# =============================================================================



def _impl_embed_agent_activity(hours: int = 2):
    """
    Session 417: Create embeddings for ALL agent activity within the last N hours.

    This task embeds:
    1. Agent Dreams - Creative thoughts and ideas
    2. Hive Mind Sessions - Collective intelligence outputs
    3. Agent Knowledge Sources - All knowledge (not just [Learned]/[Synthesis] prefixed)

    Runs every 30 minutes to keep embeddings fresh for semantic search.
    """
    import asyncio
    from datetime import timedelta
    from django.utils import timezone
    from django.db import transaction
    from core.models_unified_system import Agent, AgentDream, HiveMindSession, AgentKnowledgeSource
    from content.models import Document, DocumentEmbedding, DocumentType, EmbeddingModel, ContentStatus, ContentSource
    from content.embeddings import EmbeddingManager

    logger.info(f"🧠 [EMBEDDINGS] Starting agent activity embedding (last {hours} hours)...")

    def run_async(coro):
        """Run an async coroutine synchronously."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)

    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()

        embedding_manager = EmbeddingManager()
        cutoff = timezone.now() - timedelta(hours=hours)

        stats = {
            'dreams_processed': 0,
            'dreams_embedded': 0,
            'hive_minds_processed': 0,
            'hive_minds_embedded': 0,
            'knowledge_processed': 0,
            'knowledge_embedded': 0,
            'total_embedded': 0,
            'failed': 0,
            'total_cost': 0.0
        }

        # Get or create system user
        system_user, _ = User.objects.get_or_create(
            username='system_learning',
            defaults={
                'email': 'system@learning.internal',
                'is_active': True,
            }
        )

        # Get or create the agent activity document
        activity_doc, created = Document.objects.get_or_create(
            title='Agent Activity Knowledge Base',
            document_type=DocumentType.KNOWLEDGE_EXTRACT,
            defaults={
                'owner': system_user,
                'description': 'Embedded content from agent dreams, hive minds, and knowledge',
                'raw_content': '',
                'processed_content': '',
                'status': ContentStatus.PROCESSED,
                'source': ContentSource.WORKFLOW,
                'tags': ['agent_activity', 'dreams', 'hive_mind', 'knowledge', 'embedded']
            }
        )

        # Track existing embeddings to avoid duplicates (by metadata type+id)
        existing_embeddings = set()
        for emb in DocumentEmbedding.objects.filter(document=activity_doc).values('metadata'):
            if emb['metadata']:
                key = f"{emb['metadata'].get('type', '')}_{emb['metadata'].get('id', '')}"
                existing_embeddings.add(key)

        next_index = DocumentEmbedding.objects.filter(document=activity_doc).count()

        # =================================================================
        # 1. EMBED AGENT DREAMS
        # =================================================================
        recent_dreams = AgentDream.objects.filter(
            dreamed_at__gte=cutoff
        ).select_related('agent')

        for dream in recent_dreams:
            dream_key = f"dream_{dream.id}"
            if dream_key in existing_embeddings:
                continue  # Already embedded

            text_parts = [
                f"Agent Dream: {dream.title or 'Untitled'}",
                f"Agent: {dream.agent.name if dream.agent else 'Unknown'}",
                f"Type: {dream.dream_type}",
                f"Content: {dream.content or 'No content'}",
                f"Topics: {', '.join(dream.related_topics) if dream.related_topics else 'None'}",
                f"Inspiration: {dream.inspiration_source or 'Unknown'}",
                f"Vividness: {dream.vividness_score:.2f}" if dream.vividness_score else "",
                f"Creativity: {dream.creativity_score:.2f}" if dream.creativity_score else "",
                f"Created: {dream.dreamed_at.isoformat()}"
            ]
            text = "\n".join([p for p in text_parts if p])

            result = run_async(
                embedding_manager.generate_embedding(text, EmbeddingModel.OPENAI_SMALL)
            )

            if result.success:
                with transaction.atomic():
                    DocumentEmbedding.objects.create(
                        document=activity_doc,
                        chunk_index=next_index,
                        embedding_model=EmbeddingModel.OPENAI_SMALL,
                        chunk_text=text,
                        chunk_size=len(text),
                        embedding_vector=result.embedding,
                        embedding_dimension=result.dimension,
                        processing_time_ms=result.processing_time_ms,
                        embedding_cost=result.cost,
                        metadata={
                            'type': 'dream',
                            'id': str(dream.id),
                            'agent': dream.agent.name if dream.agent else None,
                            'dream_type': dream.dream_type,
                            'date': dream.dreamed_at.isoformat()
                        },
                        source_type='internal',
                        ingested_via='backfill',
                    )
                next_index += 1
                stats['dreams_embedded'] += 1
                stats['total_embedded'] += 1
                stats['total_cost'] += float(result.cost)
            else:
                stats['failed'] += 1

            stats['dreams_processed'] += 1

        # =================================================================
        # 2. EMBED HIVE MIND SESSIONS
        # =================================================================
        recent_hive_minds = HiveMindSession.objects.filter(
            created_at__gte=cutoff,
            status='completed'
        )

        for session in recent_hive_minds:
            session_key = f"hive_mind_{session.id}"
            if session_key in existing_embeddings:
                continue

            # Get participant names
            participant_names = []
            if session.participant_ids:
                participants = Agent.objects.filter(id__in=session.participant_ids)
                participant_names = [p.name for p in participants]

            text_parts = [
                f"Hive Mind Session: {session.conversation_topic or session.question}",
                f"Mode: {session.session_mode}",
                f"Participants: {', '.join(participant_names) if participant_names else 'Unknown'}",
                f"Question: {session.question}",
                f"Context: {session.context}" if session.context else "",
                f"Synthesis: {session.synthesis}" if session.synthesis else "",
                f"Summary: {session.synthesis_summary}" if session.synthesis_summary else "",
                f"Contributions: {session.contribution_count}",
                f"Created: {session.created_at.isoformat()}"
            ]
            text = "\n".join([p for p in text_parts if p])

            result = run_async(
                embedding_manager.generate_embedding(text, EmbeddingModel.OPENAI_SMALL)
            )

            if result.success:
                with transaction.atomic():
                    DocumentEmbedding.objects.create(
                        document=activity_doc,
                        chunk_index=next_index,
                        embedding_model=EmbeddingModel.OPENAI_SMALL,
                        chunk_text=text,
                        chunk_size=len(text),
                        embedding_vector=result.embedding,
                        embedding_dimension=result.dimension,
                        processing_time_ms=result.processing_time_ms,
                        embedding_cost=result.cost,
                        metadata={
                            'type': 'hive_mind',
                            'id': str(session.id),
                            'mode': session.session_mode,
                            'participants': participant_names,
                            'date': session.created_at.isoformat(),
                        },
                        source_type='internal',
                        ingested_via='backfill',
                    )
                next_index += 1
                stats['hive_minds_embedded'] += 1
                stats['total_embedded'] += 1
                stats['total_cost'] += float(result.cost)
            else:
                stats['failed'] += 1

            stats['hive_minds_processed'] += 1

        # =================================================================
        # 3. EMBED ALL KNOWLEDGE SOURCES (not just prefixed ones)
        # =================================================================
        recent_knowledge = AgentKnowledgeSource.objects.filter(
            first_discovered_at__gte=cutoff,
            is_active=True
        ).select_related('agent')

        for knowledge in recent_knowledge:
            knowledge_key = f"knowledge_{knowledge.id}"
            if knowledge_key in existing_embeddings:
                continue

            text_parts = [
                f"Agent Knowledge: {knowledge.title}",
                f"Agent: {knowledge.agent.name if knowledge.agent else 'Unknown'}",
                f"Type: {knowledge.knowledge_type}",
                f"Summary: {knowledge.summary or 'No summary'}",
                f"Insights: {', '.join(str(i) for i in knowledge.key_insights) if knowledge.key_insights else 'None'}",
                f"Confidence: {knowledge.confidence_score:.2f}" if knowledge.confidence_score else "",
                f"Relevance: {knowledge.relevance_score:.2f}" if knowledge.relevance_score else "",
                f"Data Points: {knowledge.data_points_count}",
                f"Discovered: {knowledge.first_discovered_at.isoformat()}"
            ]
            text = "\n".join([p for p in text_parts if p])

            result = run_async(
                embedding_manager.generate_embedding(text, EmbeddingModel.OPENAI_SMALL)
            )

            if result.success:
                with transaction.atomic():
                    DocumentEmbedding.objects.create(
                        document=activity_doc,
                        chunk_index=next_index,
                        embedding_model=EmbeddingModel.OPENAI_SMALL,
                        chunk_text=text,
                        chunk_size=len(text),
                        embedding_vector=result.embedding,
                        embedding_dimension=result.dimension,
                        processing_time_ms=result.processing_time_ms,
                        embedding_cost=result.cost,
                        metadata={
                            'type': 'knowledge',
                            'id': str(knowledge.id),
                            'agent': knowledge.agent.name if knowledge.agent else None,
                            'knowledge_type': knowledge.knowledge_type,
                            'date': knowledge.first_discovered_at.isoformat()
                        },
                        source_type='internal',
                        ingested_via='backfill',
                    )
                next_index += 1
                stats['knowledge_embedded'] += 1
                stats['total_embedded'] += 1
                stats['total_cost'] += float(result.cost)
            else:
                stats['failed'] += 1

            stats['knowledge_processed'] += 1

        # Update document timestamp
        activity_doc.save()

        # Broadcast completion
        try:
            import redis
            import json
            r = redis.Redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'), decode_responses=True)
            r.publish('agent_learning', json.dumps({
                'type': 'activity_embeddings_complete',
                'stats': stats,
                'timestamp': timezone.now().isoformat()
            }))
        except Exception as e:
            logger.warning(f"Redis publish failed (activity_embeddings): {e}")

        logger.info(
            f"🧠 [EMBEDDINGS] Agent activity embedding complete: "
            f"{stats['dreams_embedded']}/{stats['dreams_processed']} dreams, "
            f"{stats['hive_minds_embedded']}/{stats['hive_minds_processed']} hive minds, "
            f"{stats['knowledge_embedded']}/{stats['knowledge_processed']} knowledge, "
            f"${stats['total_cost']:.4f} cost"
        )

        return {
            'status': 'success',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }

    except Exception as e:
        logger.exception(f"🧠 [EMBEDDINGS] Agent activity embedding failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# =============================================================================
# Session 1020: Temporal context for conversation system prompts
# =============================================================================



def _impl_process_agent_activity_xp():
    """
    Session 254: Award XP to agents based on their recent activity.
    Session 748: Fixed field name mismatches - was using wrong timestamp/relationship fields.

    Called by Celery Beat every 15 minutes.
    Looks at agent activity from the last 15 minutes and awards XP accordingly.
    """
    try:
        from core.models_unified_system import (
            AgentEvolution, Agent, AgentConversation, AgentDream, AgentLearning
        )

        now = timezone.now()
        fifteen_min_ago = now - timedelta(minutes=15)

        agents_awarded = 0
        total_xp_awarded = 0

        # Award XP for conversations
        # Session 748: Fixed - AgentConversation uses 'started_at' not 'created_at',
        # and 'participants' (M2M) not 'initiator'/'responder'
        try:
            recent_conversations = AgentConversation.objects.filter(
                started_at__gte=fifteen_min_ago
            ).prefetch_related('participants')

            for convo in recent_conversations:
                for agent in convo.participants.all():
                    try:
                        evolution, _ = AgentEvolution.objects.get_or_create(agent=agent)
                        evolution.award_xp(5, 'conversation', f'Participated in conversation: {convo.topic[:50] if convo.topic else "Agent discussion"}')
                        agents_awarded += 1
                        total_xp_awarded += 5
                    except Exception as e:
                        logger.warning(f"📈 [EVOLUTION] XP award failed for conversation: {e}")
        except Exception as e:
            logger.warning(f"📈 [EVOLUTION] Conversation XP check skipped: {e}")

        # Award XP for dreams
        # Session 748: Fixed - AgentDream uses 'dreamed_at' not 'created_at'
        try:
            recent_dreams = AgentDream.objects.filter(
                dreamed_at__gte=fifteen_min_ago
            ).select_related('agent')

            for dream in recent_dreams:
                if dream.agent:
                    try:
                        evolution, _ = AgentEvolution.objects.get_or_create(agent=dream.agent)
                        evolution.award_xp(3, 'dream', f'Generated dream: {dream.title[:50] if dream.title else "Creative dream"}')
                        agents_awarded += 1
                        total_xp_awarded += 3
                    except Exception as e:
                        logger.warning(f"📈 [EVOLUTION] XP award failed for dream: {e}")
        except Exception as e:
            logger.warning(f"📈 [EVOLUTION] Dream XP check skipped: {e}")

        # Award XP for learning
        # Session 748: Fixed - AgentLearning uses 'teacher_agent' and 'student_agent' not 'agent'
        try:
            recent_learning = AgentLearning.objects.filter(
                created_at__gte=fifteen_min_ago
            ).select_related('teacher_agent', 'student_agent')

            for learning in recent_learning:
                # Award XP to both teacher and student
                if learning.teacher_agent:
                    try:
                        evolution, _ = AgentEvolution.objects.get_or_create(agent=learning.teacher_agent)
                        evolution.award_xp(8, 'mentorship', f'Taught: {learning.learning_type}')
                        agents_awarded += 1
                        total_xp_awarded += 8
                    except Exception as e:
                        logger.warning(f"📈 [EVOLUTION] XP award failed for mentorship: {e}")
                if learning.student_agent:
                    try:
                        evolution, _ = AgentEvolution.objects.get_or_create(agent=learning.student_agent)
                        evolution.award_xp(8, 'learning', f'Learned: {learning.learning_type}')
                        agents_awarded += 1
                        total_xp_awarded += 8
                    except Exception as e:
                        logger.warning(f"📈 [EVOLUTION] XP award failed for learning: {e}")
        except Exception as e:
            logger.warning(f"📈 [EVOLUTION] Learning XP check skipped: {e}")

        logger.info(f"📈 [EVOLUTION] Awarded {total_xp_awarded} XP to {agents_awarded} agent activities")

        return {
            'status': 'success',
            'agents_awarded': agents_awarded,
            'total_xp': total_xp_awarded
        }

    except Exception as e:
        logger.exception(f"📈 [EVOLUTION] Failed to process activity XP: {e}")
        return {'status': 'failed', 'error': str(e)}




def _impl_calculate_agent_accuracy():
    """
    Session 464: Calculate agent accuracy metrics for the learning loop.

    Runs weekly on Sundays at 8 PM to analyze BullCaseAgent and BearCaseAgent performance
    over the past 30 days. Updates confidence multipliers based on track record.

    Process:
    1. Create or get AgentAccuracyMetrics for past 30 days
    2. For BullCaseAgent: analyze all bull predictions
    3. For BearCaseAgent: analyze all bear predictions
    4. Calculate overall accuracy, conviction calibration, market regime performance
    5. Update confidence multipliers (0.5-1.5x based on accuracy)
    6. Log insights about agent performance

    Returns:
        dict: Summary of accuracy metrics calculated
    """
    from datetime import date, timedelta
    from core.models_unified_system import AgentAccuracyMetrics

    logger.info("🎯 [SESSION 464] Starting agent accuracy calculation...")

    results = {
        'bull_agent': {},
        'bear_agent': {},
    }

    try:
        # Calculate 30-day period
        period_end = date.today()
        period_start = period_end - timedelta(days=30)

        # Calculate metrics for BullCaseAgent
        try:
            bull_metrics, created = AgentAccuracyMetrics.objects.get_or_create(
                agent_name='BullCaseAgent',
                period_start=period_start,
                period_end=period_end,
            )

            bull_metrics.calculate_metrics()

            results['bull_agent'] = {
                'total_predictions': bull_metrics.total_predictions,
                'accuracy_7d': bull_metrics.accuracy_rate_7_days,
                'accuracy_30d': bull_metrics.accuracy_rate_30_days,
                'confidence_multiplier': bull_metrics.confidence_multiplier,
                'high_conviction_accuracy': bull_metrics.high_conviction_accuracy,
            }

            logger.info(f"  🐂 BullCaseAgent: {bull_metrics.accuracy_rate_7_days:.1f}% accurate "
                       f"({bull_metrics.total_predictions} predictions, "
                       f"confidence multiplier: {bull_metrics.confidence_multiplier:.2f}x)")

        except Exception as e:
            logger.error(f"  ❌ Failed to calculate BullCaseAgent metrics: {e}")
            results['bull_agent']['error'] = str(e)

        # Calculate metrics for BearCaseAgent
        try:
            bear_metrics, created = AgentAccuracyMetrics.objects.get_or_create(
                agent_name='BearCaseAgent',
                period_start=period_start,
                period_end=period_end,
            )

            bear_metrics.calculate_metrics()

            results['bear_agent'] = {
                'total_predictions': bear_metrics.total_predictions,
                'accuracy_7d': bear_metrics.accuracy_rate_7_days,
                'accuracy_30d': bear_metrics.accuracy_rate_30_days,
                'confidence_multiplier': bear_metrics.confidence_multiplier,
                'high_conviction_accuracy': bear_metrics.high_conviction_accuracy,
            }

            logger.info(f"  🐻 BearCaseAgent: {bear_metrics.accuracy_rate_7_days:.1f}% accurate "
                       f"({bear_metrics.total_predictions} predictions, "
                       f"confidence multiplier: {bear_metrics.confidence_multiplier:.2f}x)")

        except Exception as e:
            logger.error(f"  ❌ Failed to calculate BearCaseAgent metrics: {e}")
            results['bear_agent']['error'] = str(e)

        logger.info(f"🎯 [SESSION 464] Agent accuracy calculation complete")

        return results

    except Exception as e:
        logger.error(f"🎯 [SESSION 464] Agent accuracy calculation failed: {e}")
        return {'status': 'failed', 'error': str(e)}


# ==================== SESSION 466: AUTONOMOUS CONTENT STUDIO ====================




def _impl_generate_human_attention_items():
    """
    Generate attention items from various system events.

    This task runs periodically to check for:
    - Failed agent executions
    - Pilot gates pending approval
    - High-value spider data
    - System health issues

    Returns:
        Dict with generation statistics
    """
    logger.info("🧑 [HUMAN INTERFACE] Starting attention item generation")

    try:
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from datetime import timedelta
        from core.services.human_attention_bridge import attention_bridge

        User = get_user_model()
        stats = {
            'pilot_gates': 0,
            'failed_executions': 0,
            'system_alerts': 0,
            'high_value_spiders': 0,
            'stock_alerts': 0,
            'content_ready': 0,
        }

        # 1. Check for pilot gates pending approval
        try:
            from core.models_pilot_readiness import PilotReadinessGate
            pending_gates = PilotReadinessGate.objects.filter(status='pending_review')
            for gate in pending_gates:
                attention_bridge.create_pilot_gate_attention(gate)
                stats['pilot_gates'] += 1
        except Exception as e:
            logger.warning(f"Pilot gate check failed: {e}")

        # 2. Check for recent failed agent executions (Session 984: widened from 6 hardcoded agents to all)
        try:
            from core.models_unified_system import AgentExecution
            recent_failures = AgentExecution.objects.filter(
                status='failed',
                created_at__gte=timezone.now() - timedelta(hours=4)
            ).select_related('agent')[:20]

            for execution in recent_failures:
                attention_bridge.create_agent_execution_attention(execution)
                stats['failed_executions'] += 1
        except Exception as e:
            logger.warning(f"Agent execution check failed: {e}")

        # 3. Check system health
        try:
            from core.services.system_state_aggregator import get_system_state_aggregator
            agg = get_system_state_aggregator()
            # get_attention_items returns actual data; build a simple state dict
            state = {}

            # Alert if API costs are high
            if state.get('api_costs_today', 0) > 50:  # $50 threshold
                attention_bridge.create_system_alert(
                    alert_type='api_costs',
                    title='High API Costs Today',
                    summary=f"API costs have reached ${state['api_costs_today']:.2f} today. Review usage patterns.",
                    urgency='medium',
                    payload={'costs': state['api_costs_today']}
                )
                stats['system_alerts'] += 1

            # Alert if many tasks are queued
            if state.get('celery_pending_tasks', 0) > 100:
                attention_bridge.create_system_alert(
                    alert_type='task_queue',
                    title='High Task Queue',
                    summary=f"{state['celery_pending_tasks']} tasks pending in Celery queue.",
                    urgency='medium',
                    payload={'pending_tasks': state['celery_pending_tasks']}
                )
                stats['system_alerts'] += 1
        except Exception as e:
            logger.warning(f"System health check failed: {e}")

        # 4. Check for high-value spider data
        # Session 984: Fixed data_type filter — old values (market_alert, security_alert, etc.)
        # never matched any actual spider data. Real types from base_spider.py:
        # opportunity, market_data, news, trend_data, competitor_info, job_posting, etc.
        # Session 1076: Exclude 'news' — raw headlines are not actionable and create
        # boardroom noise (6+ items per cycle from Reuters/BBC/TechCrunch/etc).
        # News data is still collected by spiders and available via spider_data_tool.
        try:
            from core.models_unified_system import SpiderData
            recent_spider_data = SpiderData.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=4),
                data_type__in=['opportunity', 'market_data', 'trend_data', 'competitor_info']
            ).order_by('-created_at')[:10]

            for data in recent_spider_data:
                title = ''
                summary = 'New data available'
                if data.raw_data and isinstance(data.raw_data, dict):
                    rd = data.raw_data
                    title = rd.get('title', '')
                    # Session 1067: Build human-readable summary instead of str(dict)
                    # Try top-level text fields first
                    for key in ('summary', 'description', 'content', 'text', 'headline'):
                        if isinstance(rd.get(key), str) and len(rd[key]) > 10:
                            summary = rd[key][:300]
                            break
                    else:
                        # For list-style data (e.g. news items), summarize first few titles
                        items = rd.get('items') or rd.get('results') or rd.get('articles') or []
                        if isinstance(items, list) and items:
                            titles = [
                                str(it.get('title', ''))[:80]
                                for it in items[:5]
                                if isinstance(it, dict) and it.get('title')
                            ]
                            if titles:
                                summary = ' | '.join(titles)
                            else:
                                summary = f"{len(items)} items from {data.spider_name}"
                        elif title:
                            summary = f"{data.data_type.replace('_', ' ').title()} from {data.spider_name}"
                if not title:
                    title = f"Spider Data: {data.data_type.replace('_', ' ').title()}"
                attention_bridge.create_spider_alert(
                    spider_name=data.spider_name,
                    alert_type=data.data_type,
                    title=title[:200],
                    summary=summary[:300],
                    data=data.raw_data,
                    urgency='medium'
                )
                stats['high_value_spiders'] += 1
        except Exception as e:
            logger.warning(f"Spider data check failed: {e}")

        # 5. Session 984: Check for recent stock market alerts
        try:
            from core.models_autonomous_alerts import StockMarketAlert
            recent_alerts = StockMarketAlert.objects.filter(
                detected_at__gte=timezone.now() - timedelta(hours=4)
            ).order_by('-detected_at')[:5]

            for alert in recent_alerts:
                urgency = 'high' if alert.alert_type in ['risk_alert', 'anomaly_detected'] else 'medium'
                attention_bridge.create_spider_alert(
                    spider_name='stock_intelligence',
                    alert_type=alert.alert_type,
                    title=f"{alert.symbol}: {alert.title}"[:200],
                    summary=alert.summary[:300] if alert.summary else f"{alert.alert_type} for {alert.symbol}",
                    data={
                        'symbol': alert.symbol,
                        'alert_type': alert.alert_type,
                        'bull_score': alert.bull_score,
                        'bear_score': alert.bear_score,
                        'recommended_action': alert.recommended_action,
                    },
                    urgency=urgency
                )
                stats['stock_alerts'] += 1
        except Exception as e:
            logger.warning(f"Stock alert check failed: {e}")

        # 6. Session 984: Check for publish-ready blog content awaiting review
        # Session 1076: Suppress low-quality/novelty blogs from Boardroom.
        # Quality 1% / Novelty 1% items are noise — only surface blogs with
        # meaningful scores (>= 0.2 on both) to preserve human attention bandwidth.
        try:
            from core.models_unified_system import SelfBlog
            ready_blogs = SelfBlog.objects.filter(
                publish_ready=True,
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).order_by('-created_at')[:3]

            for blog in ready_blogs:
                q = blog.quality_score or 0
                n = blog.novelty_score or 0
                if q < 0.2 and n < 0.2:
                    logger.debug(
                        f"Suppressed low-signal blog attention: '{blog.title}' "
                        f"(quality={q:.0%}, novelty={n:.0%})"
                    )
                    continue
                attention_bridge.create_system_alert(
                    alert_type='content_ready',
                    title=f"Blog Ready: {blog.title}"[:200] if blog.title else "New blog ready for review",
                    summary=f"Quality: {q:.0%} | Novelty: {n:.0%} | {blog.word_count} words",
                    urgency='low',
                    payload={
                        'blog_id': str(blog.id),
                        'quality_score': q,
                        'novelty_score': n,
                        'word_count': blog.word_count,
                    }
                )
                stats['content_ready'] += 1
        except Exception as e:
            logger.warning(f"Blog content check failed: {e}")

        total = sum(stats.values())
        logger.info(f"🧑 [HUMAN INTERFACE] Generated {total} attention items: {stats}")

        return {
            'status': 'completed',
            'items_created': total,
            'breakdown': stats
        }

    except Exception as e:
        logger.error(f"❌ [HUMAN INTERFACE] Attention generation failed: {e}")
        return {
            'status': 'failed',
            'error': str(e)
        }


# =============================================================================
# Session 766: Human Attention Lifecycle Management
# =============================================================================



def _impl_agent_workspace_status_report():
    """
    Session 776: Generate a workspace status report via SystemIntelligenceAgent.

    Creates a status report file in the active workspace documenting:
    - Current system health
    - Recent agent activity
    - Active pilots and gates
    - Learning metrics

    Runs every 6 hours to maintain visibility into system state.

    Returns:
        Operation result
    """
    from core.services.workspace_manager import WorkspaceManager
    from core.agents.system_intelligence_agent import SystemIntelligenceAgent

    logger.info("🖥️ [SKIN LAYER] Starting workspace status report generation...")

    # Session 1089: Governor gate
    try:
        from core.services.priority.governor import should_dispatch
        gov = should_dispatch('SystemIntelligenceAgent', trigger_source='workspace_autopilot', task='status_report')
        if not gov.proceed:
            logger.info(f"🛑 [SKIN LAYER] Governor BLOCKED status report: {gov.reason}")
            return {'success': False, 'skipped': True, 'reason': f'governor_{gov.reason}'}
    except Exception:
        pass  # fail-open

    try:
        # Session 885: Use helper to find workspace (handles codebase workspace)
        user, workspace = _get_workspace_for_skin_layer()
        if not workspace:
            return {'success': False, 'error': 'No active workspace found (run setup_codebase_workspace)'}

        # Generate status report using SystemIntelligenceAgent
        agent = SystemIntelligenceAgent()
        report_content = agent.execute(
            task="Generate a comprehensive system status report including: "
                 "1) Overall system health metrics "
                 "2) Active agents and their recent activity "
                 "3) Current pilot status "
                 "4) Learning and knowledge metrics "
                 "5) Any warnings or issues that need attention",
            context={'report_type': 'status', 'output_format': 'markdown'},
            scifi_context={},
            spider_context={}
        )

        # Format the report
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        filename = f"reports/system_status_{timestamp}.md"

        # Session 875: Use unified extraction function
        output_content = _extract_agent_output_content(report_content, 'system status report')

        content = f"""# System Status Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Agent: SystemIntelligenceAgent

---

{output_content}

---
*This report was automatically generated via the SKIN Layer.*
"""

        # Write to workspace
        manager = WorkspaceManager(user)
        operation = manager.write_file(
            workspace=workspace,
            file_path=filename,
            content=content,
            agent_name='SystemIntelligenceAgent',
            agent_task='Automated system status report'
        )

        logger.info(
            f"🖥️ [SKIN LAYER] Status report generated: {filename} "
            f"(success: {operation.success})"
        )

        return {
            'success': operation.success,
            'file': filename,
            'operation_id': str(operation.id)
        }

    except Exception as e:
        logger.error(f"🖥️ [SKIN LAYER] Status report failed: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}




def _impl_agent_research_to_workspace(topic: str = None):
    """
    Session 776: Have ResearchAgent write research findings to workspace.

    Conducts research on a topic (or trending topics) and writes
    the findings to a markdown file in the workspace.

    Args:
        topic: Specific topic to research, or None for trending topics

    Returns:
        Operation result
    """
    from django.contrib.auth import get_user_model
    from core.models_skin_layer import ProjectWorkspace
    from core.services.workspace_manager import WorkspaceManager
    from core.agents.research_agent import ResearchAgent

    logger.info(f"🔬 [SKIN LAYER] Starting research task (topic: {topic or 'trending'})...")

    # Session 1089: Governor gate
    try:
        from core.services.priority.governor import should_dispatch
        gov = should_dispatch('ResearchAgent', trigger_source='workspace_autopilot', task=topic or 'trending')
        if not gov.proceed:
            logger.info(f"🛑 [SKIN LAYER] Governor BLOCKED research: {gov.reason}")
            return {'success': False, 'skipped': True, 'reason': f'governor_{gov.reason}'}
    except Exception:
        pass  # fail-open

    try:
        # Session 885: Use helper to find workspace (handles codebase workspace)
        user, workspace = _get_workspace_for_skin_layer()
        if not workspace:
            return {'success': False, 'error': 'No active workspace found (run setup_codebase_workspace)'}

        # Determine topic
        if not topic:
            topic = "current AI and technology trends for content creation"

        # Conduct research
        agent = ResearchAgent()
        research_result = agent.execute(
            task=f"Research the following topic and provide a comprehensive summary: {topic}",
            context={'research_topic': topic, 'output_format': 'markdown'},
            scifi_context={},
            spider_context={}
        )

        # Format the research
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        safe_topic = topic[:30].replace(' ', '_').replace('/', '-')
        filename = f"research/{safe_topic}_{timestamp}.md"

        # Session 875: Use unified extraction function
        output_content = _extract_agent_output_content(research_result, f'research on {topic}')

        content = f"""# Research: {topic}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Agent: ResearchAgent

---

{output_content}

---
*Research conducted via SKIN Layer automation.*
"""

        # Write to workspace
        manager = WorkspaceManager(user)
        operation = manager.write_file(
            workspace=workspace,
            file_path=filename,
            content=content,
            agent_name='ResearchAgent',
            agent_task=f'Research: {topic}'
        )

        logger.info(
            f"🔬 [SKIN LAYER] Research written: {filename} "
            f"(success: {operation.success})"
        )

        return {
            'success': operation.success,
            'file': filename,
            'topic': topic,
            'operation_id': str(operation.id)
        }

    except Exception as e:
        logger.error(f"🔬 [SKIN LAYER] Research task failed: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}




def _impl_agent_content_to_workspace(content_type: str = 'blog', topic: str = None):
    """
    Session 776: Have ContentWriterAgent generate content and write to workspace.
    Session 887: Now gathers research first before generating content.

    Generates content (blog post, article, etc.) and writes it to the workspace.
    First calls ResearchAgent to gather research, then passes to ContentWriterAgent.

    Args:
        content_type: Type of content ('blog', 'article', 'tutorial')
        topic: Topic for the content, or None for AI-selected topic

    Returns:
        Operation result
    """
    from django.contrib.auth import get_user_model
    from core.models_skin_layer import ProjectWorkspace
    from core.services.workspace_manager import WorkspaceManager
    from core.agents.content_writer_agent import ContentWriterAgent
    from core.agents.research_agent import ResearchAgent

    logger.info(f"✍️ [SKIN LAYER] Starting content generation ({content_type})...")

    # Session 1089: Governor gate
    try:
        from core.services.priority.governor import should_dispatch
        gov = should_dispatch('ContentWriterAgent', trigger_source='workspace_autopilot', task=topic or content_type)
        if not gov.proceed:
            logger.info(f"🛑 [SKIN LAYER] Governor BLOCKED content gen: {gov.reason}")
            return {'success': False, 'skipped': True, 'reason': f'governor_{gov.reason}'}
    except Exception:
        pass  # fail-open

    try:
        # Session 885: Use helper to find workspace (handles codebase workspace)
        user, workspace = _get_workspace_for_skin_layer()
        if not workspace:
            return {'success': False, 'error': 'No active workspace found (run setup_codebase_workspace)'}

        # Determine topic
        if not topic:
            topic = "AI-assisted software development best practices"

        # Session 887: Map common content type names to ContentWriterAgent's expected types
        content_type_map = {
            'blog': 'blog_post',
            'article': 'article',
            'podcast': 'podcast_script',
            'video': 'video_script',
            'social': 'social_thread',
            'newsletter': 'newsletter',
        }
        mapped_content_type = content_type_map.get(content_type, content_type)

        # Session 887: First gather research on the topic
        logger.info(f"🔬 [SKIN LAYER] Step 1: Gathering research on '{topic}'...")
        research_agent = ResearchAgent()
        research_result = research_agent.execute(
            task=f"Research the topic: {topic}. "
                 f"Find current trends, statistics, expert opinions, and practical examples. "
                 f"Focus on information that would be useful for a {content_type}.",
            context={'research_topic': topic, 'output_format': 'markdown'},
            scifi_context={},
            spider_context={}
        )

        # Extract research content
        research_content = ""
        if research_result.success:
            if research_result.message:
                research_content = research_result.message
            elif research_result.data:
                # Try to get research from data
                research_content = (
                    research_result.data.get('research', '') or
                    research_result.data.get('summary', '') or
                    research_result.data.get('content', '') or
                    str(research_result.data)
                )
            logger.info(f"✅ Research gathered: {len(research_content)} chars")
        else:
            logger.warning(f"⚠️ Research failed: {research_result.error}, proceeding with topic only")
            research_content = f"Topic: {topic}\n\nWrite an informative {content_type} about this topic."

        # Session 887: Generate content with research context
        logger.info(f"✍️ [SKIN LAYER] Step 2: Generating {mapped_content_type} from research...")
        agent = ContentWriterAgent()
        content_result = agent.execute(
            task=f"Transform this research into a compelling {mapped_content_type} about: {topic}. "
                 f"Include practical examples, clear explanations, and actionable insights.",
            context={
                'content_type': mapped_content_type,
                'topic': topic,
                'research': research_content,
                'output_format': 'markdown'
            },
            scifi_context={},
            spider_context={}
        )

        # Format and write
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        safe_topic = topic[:30].replace(' ', '_').replace('/', '-')
        filename = f"content/{content_type}_{safe_topic}_{timestamp}.md"

        # Session 875: Use unified extraction function (now handles dict content with full_text)
        output_content = _extract_agent_output_content(content_result, f'{content_type} about {topic}')

        # Session 887: Include research info in header
        research_note = f"Research: {len(research_content)} chars gathered" if research_content else "No research available"
        content_body = f"""# {topic}
Type: {mapped_content_type.replace('_', ' ').title()}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Agent: ResearchAgent → ContentWriterAgent
{research_note}

---

{output_content}

---
*Content generated via SKIN Layer automation (research-backed).*
"""

        manager = WorkspaceManager(user)
        operation = manager.write_file(
            workspace=workspace,
            file_path=filename,
            content=content_body,
            agent_name='ContentWriterAgent',
            agent_task=f'{content_type.title()}: {topic}'
        )

        logger.info(
            f"✍️ [SKIN LAYER] Content written: {filename} "
            f"(success: {operation.success})"
        )

        return {
            'success': operation.success,
            'file': filename,
            'content_type': content_type,
            'topic': topic,
            'operation_id': str(operation.id)
        }

    except Exception as e:
        logger.error(f"✍️ [SKIN LAYER] Content task failed: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


# ============================================================================
# Session 864: Content Enhancement Tasks (EditorAgent)
# ============================================================================



def _impl_agent_daily_summary():
    """
    Session 776: Generate a daily summary of all agent activities.

    Creates a comprehensive daily summary including:
    - Agent execution counts
    - Content generated
    - Learning achievements
    - System health overview

    Runs once daily at midnight.

    Returns:
        Operation result
    """
    from django.contrib.auth import get_user_model
    from django.utils import timezone
    from datetime import timedelta
    from core.models_skin_layer import ProjectWorkspace, WorkspaceOperation
    from core.models_unified_system import AgentExecution, AgentMemory
    from core.services.workspace_manager import WorkspaceManager

    logger.info("📊 [SKIN LAYER] Generating daily summary...")

    try:
        # Session 885: Use helper to find workspace (handles codebase workspace)
        user, workspace = _get_workspace_for_skin_layer()
        if not workspace:
            return {'success': False, 'error': 'No active workspace found (run setup_codebase_workspace)'}

        # Gather daily statistics
        yesterday = timezone.now() - timedelta(days=1)

        # Agent executions
        executions = AgentExecution.objects.filter(created_at__gte=yesterday)
        execution_count = executions.count()
        successful = executions.filter(status='completed').count()
        failed = executions.filter(status='failed').count()

        # By agent
        from django.db.models import Count
        by_agent = list(
            executions.values('agent__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )

        # Workspace operations
        operations = WorkspaceOperation.objects.filter(
            workspace=workspace,
            created_at__gte=yesterday
        )
        ops_count = operations.count()
        files_created = operations.filter(operation_type='file_create').count()
        files_modified = operations.filter(operation_type='file_update').count()

        # Memories created
        memories = AgentMemory.objects.filter(created_at__gte=yesterday).defer('embedding').count()

        # Build summary content
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")

        content = f"""# Daily Agent Summary - {today}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Agent Executions (Last 24h)
- **Total Executions:** {execution_count}
- **Successful:** {successful} ({(successful/execution_count*100) if execution_count else 0:.1f}%)
- **Failed:** {failed}

### Top Agents by Activity
"""
        for item in by_agent:
            content += f"- {item['agent__name']}: {item['count']} executions\n"

        content += f"""
## Workspace Operations
- **Total Operations:** {ops_count}
- **Files Created:** {files_created}
- **Files Modified:** {files_modified}

## Learning & Memory
- **New Memories Created:** {memories}

---
*Daily summary generated via SKIN Layer automation.*
"""

        # Write to workspace
        filename = f"summaries/daily_{today}.md"
        manager = WorkspaceManager(user)
        operation = manager.write_file(
            workspace=workspace,
            file_path=filename,
            content=content,
            agent_name='DailySummaryTask',
            agent_task='Automated daily summary generation'
        )

        logger.info(
            f"📊 [SKIN LAYER] Daily summary generated: {filename} "
            f"(success: {operation.success})"
        )

        return {
            'success': operation.success,
            'file': filename,
            'stats': {
                'executions': execution_count,
                'operations': ops_count,
                'memories': memories
            },
            'operation_id': str(operation.id)
        }

    except Exception as e:
        logger.error(f"📊 [SKIN LAYER] Daily summary failed: {e}", exc_info=True)
        return {'success': False, 'error': str(e)}


# =============================================================================
# Session 777: UNIVERSAL AGENT WORKSPACE INTEGRATION
# All 74 agents connected to SKIN Layer for workspace output
# =============================================================================

# Agent Registry: Maps agent names to their output configurations


def _impl_universal_agent_workspace_output(
agent_name: str,
    topic: str = None,
    initiative_id: str = None,
    trigger_source: str = None,
    force_production: bool = False
):
    """
    Session 777: Universal task to execute any agent and write output to workspace.
    Session 864: Added run_mode detection and intent-based quality gates.

    This task can run any registered agent and write its output to the SKIN Layer.
    Now distinguishes between PRODUCTION (purposeful) and WARMUP (exercise) runs.

    Args:
        agent_name: Name of the agent to execute
        topic: Optional topic override (if None, may trigger warmup mode)
        initiative_id: Optional initiative this is associated with
        trigger_source: What triggered this run (initiative, user, schedule, warmup)
        force_production: Force production mode even without topic

    Returns:
        Operation result with run_mode metadata
    """
    from django.contrib.auth import get_user_model
    from core.models_skin_layer import ProjectWorkspace, WorkspaceOperation
    from core.services.workspace_manager import WorkspaceManager
    from datetime import datetime
    import hashlib
    import importlib

    # ==========================================================================
    # DEDUP GUARD: Prevent duplicate dispatch of same agent+topic
    # ==========================================================================
    # Only applies to scheduled/auto triggers — user-initiated runs bypass.
    # Uses Django cache (Redis on Railway) with a 10-minute lock.
    _auto_triggers = {'schedule', 'warmup', 'initiative', None}
    from django.core.cache import cache
    if trigger_source in _auto_triggers:
        topic_hash = hashlib.md5((topic or '').encode()).hexdigest()[:12]
        dedup_key = f"agent_dedup:{agent_name}:{topic_hash}"
        if cache.get(dedup_key):
            logger.info(
                f"⏭️ [DEDUP] Skipping duplicate dispatch: {agent_name} "
                f"(topic_hash={topic_hash}, key={dedup_key})"
            )
            return {'success': False, 'skipped': True, 'reason': 'duplicate_dispatch'}
        cache.set(dedup_key, True, timeout=600)  # 10-minute lock

    # ==========================================================================
    # GOVERNOR GATE: Check mission alignment + circuit breaker before dispatch
    # ==========================================================================
    # Only gates autonomous beat-task work. User-triggered dispatches bypass.
    try:
        from core.services.priority.governor import should_dispatch
        gov_decision = should_dispatch(
            agent_name=agent_name,
            trigger_source=trigger_source,
            task=topic,
        )
        if not gov_decision.proceed:
            logger.info(
                f"🛑 [GOVERNOR] Skipping {agent_name}: {gov_decision.reason} "
                f"({gov_decision.detail})"
            )
            return {
                'success': False,
                'skipped': True,
                'reason': f'governor_{gov_decision.reason}',
                'governor_detail': gov_decision.detail,
            }
    except Exception as e:
        logger.warning(f"[GOVERNOR] fail-open for {agent_name}: {e}")

    # ==========================================================================
    # SESSION 864 PHASE 0: DETERMINE RUN MODE
    # ==========================================================================
    # If no topic provided and not forced, this is a warmup run
    is_warmup = (topic is None) and (not force_production) and (not initiative_id)

    if is_warmup:
        run_mode = 'warmup'
        trigger = trigger_source or 'warmup'
    else:
        run_mode = 'production'
        trigger = trigger_source or ('initiative' if initiative_id else 'schedule')

    logger.info(
        f"🤖 [SKIN LAYER] Agent execution: {agent_name} "
        f"(run_mode={run_mode}, trigger={trigger})"
    )

    # ==========================================================================
    # SESSION 864 PHASE 2: CHECK FOR REAL TASK (Initiative Queue)
    # If this is a scheduled run without topic, try to get a real task first
    # ==========================================================================
    real_task = None
    if topic is None and not is_warmup:
        real_task = _get_next_task_for_agent(agent_name)
        if real_task:
            topic = real_task.get('topic')
            initiative_id = real_task.get('initiative_id')
            trigger = 'initiative'
            run_mode = 'production'
            logger.info(f"🤖 [SKIN LAYER] Found real task for {agent_name}: {topic[:50]}...")

    # ==========================================================================
    # SESSION 864 PHASE 1: WARMUP MODE - Just verify agent works, no content
    # ==========================================================================
    if is_warmup and not real_task:
        logger.info(f"🔄 [WARMUP] {agent_name} - Infra check only, no content generation")
        return _run_agent_warmup(agent_name)

    # Get agent config (lazy import — defined in core.tasks)
    from core.tasks import AGENT_WORKSPACE_REGISTRY
    config = AGENT_WORKSPACE_REGISTRY.get(agent_name)
    if not config:
        logger.warning(f"Agent {agent_name} not in registry, using defaults")
        config = {
            'category': 'uncategorized',
            'output_dir': f'agents/{agent_name.lower()}',
            'output_type': 'output',
            'task_template': 'Generate output for {topic}',
            'default_topic': 'general task',
        }

    try:
        # Session 885: Use helper to find workspace (handles codebase workspace)
        user, workspace = _get_workspace_for_skin_layer()
        if not workspace:
            return {'success': False, 'error': 'No active workspace found (run setup_codebase_workspace)', 'run_mode': run_mode}

        # Determine topic - use provided or fall back to default
        actual_topic = topic or config['default_topic']
        is_default_topic = (topic is None or topic == '') and actual_topic == config['default_topic']
        task_description = config['task_template'].format(topic=actual_topic)

        # Session 1088: Skip default-topic scheduled runs entirely.
        # When no real task exists, the agent gets generic prompts like
        # "Research current trends in AI and technology innovation" which
        # produce low-value deliverables. Only dispatch if there's a real
        # topic (from initiative, user request, or conversation).
        if is_default_topic and trigger in ('schedule', 'warmup'):
            logger.info(
                f"⏭️ [DEFAULT-TOPIC] Skipping {agent_name}: no real task, "
                f"would use default_topic='{actual_topic}'"
            )
            return {
                'success': False,
                'skipped': True,
                'reason': 'default_topic_skip',
                'detail': f'No real task for {agent_name}, skipped generic default topic',
            }

        # Dynamically import and instantiate agent
        agent_class = _get_agent_class(agent_name)

        if not agent_class:
            return {
                'success': False,
                'error': f'Could not find agent class: {agent_name}',
                'run_mode': run_mode
            }

        # Session 987: Pre-flight data check — skip if required data doesn't exist
        if run_mode == 'production' and trigger == 'schedule':
            preflight = _preflight_check_agent_data(agent_name, actual_topic)
            if not preflight['proceed']:
                logger.warning(
                    f"[Session 987] Pre-flight SKIP: {agent_name} — {preflight['reason']}"
                )
                return {
                    'success': False,
                    'agent': agent_name,
                    'error': f"Pre-flight check: {preflight['reason']}",
                    'run_mode': run_mode,
                    'preflight_skip': True,
                    'preflight_counts': preflight.get('counts', {}),
                }

        # Execute agent
        agent = agent_class()
        result = agent.execute(
            task=task_description,
            context={
                'topic': actual_topic,
                'output_format': 'markdown',
                'initiative_id': initiative_id,
                'run_mode': run_mode,
                'trigger_source': trigger,
            },
            scifi_context={},
            spider_context={}
        )

        # Session 813: Improved output extraction from AgentResult
        output_content = _extract_agent_output_content(result, task_description)

        # ==========================================================================
        # SESSION 864 PHASE 3: QUALITY GATE - Only write meaningful content
        # ==========================================================================
        # For production runs, always write
        # For warmup runs that slipped through, quarantine to .warmups/
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        safe_topic = actual_topic[:30].replace(' ', '_').replace('/', '-').replace(':', '')

        if run_mode == 'production':
            filename = f"{config['output_dir']}/{config['output_type']}_{safe_topic}_{timestamp}.md"
        else:
            # Quarantine warmup output to .warmups/ directory
            filename = f".warmups/{agent_name}/{config['output_type']}_{safe_topic}_{timestamp}.md"

        content = f"""# {agent_name}: {actual_topic}
Type: {config['output_type'].replace('_', ' ').title()}
Category: {config['category'].title()}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Run Mode: {run_mode.upper()}
Trigger: {trigger}
{f'Initiative: {initiative_id}' if initiative_id else ''}

---

{output_content}

---
*Generated via SKIN Layer - Universal Agent Workspace Integration*
"""

        # Write to workspace with run_mode metadata
        manager = WorkspaceManager(user)
        operation = manager.write_file(
            workspace=workspace,
            file_path=filename,
            content=content,
            agent_name=agent_name,
            agent_task=task_description
        )

        # Session 864: Update operation with run_mode metadata
        if operation and operation.id:
            WorkspaceOperation.objects.filter(pk=operation.id).update(
                run_mode=run_mode,
                trigger_source=trigger,
                initiative_id=initiative_id,
                is_warmup=(run_mode == 'warmup')
            )

        logger.info(
            f"🤖 [SKIN LAYER] {agent_name} output written: {filename} "
            f"(success: {operation.success}, run_mode: {run_mode})"
        )

        return {
            'success': operation.success,
            'agent': agent_name,
            'category': config['category'],
            'file': filename,
            'topic': actual_topic,
            'operation_id': str(operation.id),
            'run_mode': run_mode,
            'trigger_source': trigger,
            'initiative_id': initiative_id,
        }

    except SoftTimeLimitExceeded:
        logger.error(f"🤖 [SKIN LAYER] {agent_name} KILLED by soft_time_limit (45 min)")
        # Mark any in-progress execution records for this agent as failed
        try:
            from core.models_unified_system import AgentExecution
            from django.utils import timezone as tz
            stuck = AgentExecution.objects.filter(
                agent__name=agent_name,
                status__in=['running', 'in_progress'],
            ).update(
                status='failed',
                error_message=f'Celery soft_time_limit exceeded (60 min)',
                completed_at=tz.now(),
            )
            if stuck:
                logger.info(f"🤖 [SKIN LAYER] Marked {stuck} execution(s) as failed for {agent_name}")
        except Exception as _e:
            logger.warning(
                "tasks_agents._impl_universal_agent_workspace_output: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )
        return {'success': False, 'agent': agent_name, 'error': 'Celery soft_time_limit exceeded (60 min)', 'run_mode': run_mode}

    except Exception as e:
        logger.error(f"🤖 [SKIN LAYER] {agent_name} execution failed: {e}", exc_info=True)
        return {'success': False, 'agent': agent_name, 'error': str(e), 'run_mode': run_mode}




def _impl_workspace_autopilot_tick(
budget_per_tick: int = 5,
    min_priority: int = None,
    category: str = None,
    dry_run: bool = False
):
    """
    Session 785: Hybrid Workspace Autopilot Conductor

    This is the single conductor task that drains the WorkspaceTrigger queue.
    Instead of 14+ individual scheduled tasks, this one task:

    1. Gets pending workspace triggers (respecting TTL, priority)
    2. Routes each trigger to the appropriate agent
    3. Executes within budget constraints
    4. Reports results

    The event-driven triggers (from spider data) populate the queue,
    and this conductor drains it on a schedule.

    Args:
        budget_per_tick: Maximum triggers to process per tick (default: 5)
        min_priority: Minimum priority to process (None = all)
        category: Only process triggers for this category (None = all)
        dry_run: If True, log what would happen without executing

    Returns:
        dict: Summary of processing results
    """
    from core.models_skin_layer import WorkspaceTrigger, WorkspaceTriggerType
    from core.agent_router import AgentRouter
    from core.models_unified_system import AgentExecution
    from django.utils import timezone
    from django.contrib.auth import get_user_model
    import time

    User = get_user_model()

    logger.info(
        f"🤖 [WORKSPACE AUTOPILOT] Tick starting | "
        f"Budget: {budget_per_tick} | "
        f"Category: {category or 'all'} | "
        f"Min Priority: {min_priority or 'any'}"
    )

    results = {
        'triggers_processed': 0,
        'triggers_succeeded': 0,
        'triggers_failed': 0,
        'triggers_skipped': 0,
        'expired_count': 0,
        'executions': [],
        'errors': [],
        'dry_run': dry_run
    }

    try:
        # Mark expired triggers
        expired_count = WorkspaceTrigger.objects.filter(
            status='pending',
            expires_at__lt=timezone.now()
        ).update(status='expired')
        results['expired_count'] = expired_count

        if expired_count > 0:
            logger.info(f"🤖 [WORKSPACE AUTOPILOT] Expired {expired_count} stale triggers")

        # Get pending triggers
        pending_triggers = WorkspaceTrigger.get_pending_triggers(
            limit=budget_per_tick,
            category=category,
            min_priority=min_priority
        )

        total_pending = len(pending_triggers)
        logger.info(f"🤖 [WORKSPACE AUTOPILOT] Found {total_pending} pending triggers to process")

        if total_pending == 0:
            logger.info("🤖 [WORKSPACE AUTOPILOT] No triggers to process, tick complete")
            return results

        # Initialize router
        router = AgentRouter()

        # Category to agent mapping
        # Session 1029: CodeGeneratorAgent replaced — no codebase access on Railway
        CATEGORY_AGENTS = {
            'development': 'FullStackDeveloperAgent',
            'security': 'CodeReviewAgent',
            'research': 'ResearchAgent',
            'content': 'ContentWriterAgent',
            'analysis': 'TrendAnalysisAgent',
        }

        # Trigger type to agent mapping
        TYPE_AGENTS = {
            WorkspaceTriggerType.SPIDER_SECURITY_ALERT: 'CodeReviewAgent',
            WorkspaceTriggerType.SPIDER_DEPENDENCY_UPDATE: 'ResearchAgent',
            WorkspaceTriggerType.SPIDER_BUG_PATTERN: 'CodeReviewAgent',
            WorkspaceTriggerType.SPIDER_BEST_PRACTICE: 'CodeReviewAgent',
            WorkspaceTriggerType.SPIDER_CODE_INSIGHT: 'FullStackDeveloperAgent',
            WorkspaceTriggerType.AGENT_REFACTOR_SUGGESTION: 'CodeReviewAgent',
            # Session 1029: CodeGeneratorAgent replaced — no codebase access on Railway
            WorkspaceTriggerType.AGENT_TEST_NEEDED: 'FullStackDeveloperAgent',
            WorkspaceTriggerType.AGENT_DOC_NEEDED: 'TechnicalDocumentAgent',
            WorkspaceTriggerType.AGENT_OPTIMIZATION: 'CodeReviewAgent',
        }

        for trigger in pending_triggers:
            results['triggers_processed'] += 1
            trigger_start_time = time.time()

            try:
                if dry_run:
                    logger.info(
                        f"🤖 [WORKSPACE AUTOPILOT] [DRY RUN] Would process: "
                        f"{trigger.title} → {trigger.target_agent or trigger.target_category or 'auto-route'}"
                    )
                    results['triggers_skipped'] += 1
                    continue

                # Mark as queued
                trigger.status = 'queued'
                trigger.queued_at = timezone.now()
                trigger.save(update_fields=['status', 'queued_at'])

                # Determine which agent to use
                agent_name = trigger.target_agent
                if not agent_name:
                    # Try category mapping
                    if trigger.target_category and trigger.target_category in CATEGORY_AGENTS:
                        agent_name = CATEGORY_AGENTS[trigger.target_category]
                    # Try trigger type mapping
                    elif trigger.trigger_type in TYPE_AGENTS:
                        agent_name = TYPE_AGENTS[trigger.trigger_type]
                    # Default fallback
                    else:
                        agent_name = 'ResearchAgent'

                if not agent_name:
                    logger.warning(
                        f"🤖 [WORKSPACE AUTOPILOT] Could not route trigger: {trigger.title}"
                    )
                    trigger.status = 'skipped'
                    trigger.error_message = 'Could not determine agent for routing'
                    trigger.save(update_fields=['status', 'error_message'])
                    results['triggers_skipped'] += 1
                    continue

                # Mark as in progress
                trigger.status = 'in_progress'
                trigger.started_at = timezone.now()
                trigger.save(update_fields=['status', 'started_at'])

                # Execute via agent router
                logger.info(
                    f"🤖 [WORKSPACE AUTOPILOT] Executing: {trigger.title} → {agent_name}"
                )

                # Build task prompt
                context = trigger.context_data or {}
                prompt_parts = [
                    f"## Task: {trigger.title}",
                    "",
                    trigger.description or "No additional description provided.",
                    "",
                    "## Context",
                ]
                if context.get('spider_name'):
                    prompt_parts.append(f"- Source: Spider data from `{context['spider_name']}`")
                if context.get('matched_value'):
                    prompt_parts.append(f"- Matched content: {context['matched_value']}")

                prompt_parts.extend([
                    "",
                    "## Instructions",
                    "Analyze this information and take appropriate action based on the trigger type.",
                    f"Trigger type: {trigger.get_trigger_type_display()}",
                ])
                task_prompt = "\n".join(prompt_parts)

                # Session 1089: Governor gate — check mission alignment + budget
                # before executing any agent via autopilot. This path was
                # bypassing the governor entirely, causing $17+ in unsupervised
                # overnight LLM spend.
                try:
                    from core.services.priority.governor import should_dispatch
                    gov_decision = should_dispatch(
                        agent_name=agent_name,
                        trigger_source='workspace_autopilot',
                        task=trigger.title,
                    )
                    if not gov_decision.proceed:
                        logger.info(
                            f"🛑 [WORKSPACE AUTOPILOT] Governor BLOCKED {agent_name}: "
                            f"{gov_decision.reason} ({gov_decision.detail})"
                        )
                        trigger.status = 'skipped'
                        trigger.error_message = f'Governor: {gov_decision.reason}'
                        trigger.save(update_fields=['status', 'error_message'])
                        results['triggers_skipped'] += 1
                        continue
                except Exception as gov_err:
                    logger.warning(f"[WORKSPACE AUTOPILOT] Governor fail-open: {gov_err}")

                # Execute the agent
                try:
                    agent_class = router.get_agent_class(agent_name)
                    if not agent_class:
                        raise ValueError(f'Agent class not found: {agent_name}')

                    # Session 908: Use system_autonomous for workspace operations
                    system_user = User.objects.filter(username='system_autonomous').first()
                    if not system_user:
                        system_user = User.objects.filter(username='system').first()
                    if not system_user:
                        system_user = User.objects.first()

                    agent = agent_class(user=system_user)
                    result = agent.execute(
                        task=task_prompt,
                        context={
                            'trigger_id': str(trigger.id),
                            'trigger_type': trigger.trigger_type,
                            'spider_name': context.get('spider_name'),
                            'matched_value': context.get('matched_value'),
                            'output_format': 'markdown',
                            'source': 'workspace_autopilot'
                        },
                        scifi_context={},
                        spider_context=context.get('raw_item', {})
                    )

                    # Agent's execute() creates its own AgentExecution record
                    # Extract success and summary from result
                    success = result.success if hasattr(result, 'success') else True
                    summary = ''
                    if hasattr(result, 'data') and isinstance(result.data, dict):
                        summary = str(result.data.get('summary', result.data.get('content', '')))[:500]
                    elif hasattr(result, 'data'):
                        summary = str(result.data)[:500]

                    execution_result = {
                        'success': success,
                        'summary': summary
                    }

                except Exception as agent_error:
                    logger.error(f"🤖 [WORKSPACE AUTOPILOT] Agent execution failed: {agent_error}")
                    execution_result = {
                        'success': False,
                        'error': str(agent_error)
                    }

                # Calculate execution time
                execution_time_ms = int((time.time() - trigger_start_time) * 1000)

                # Update trigger with results
                trigger.status = 'completed' if execution_result.get('success') else 'failed'
                trigger.completed_at = timezone.now()
                trigger.execution_time_ms = execution_time_ms
                trigger.result_summary = str(execution_result.get('summary', ''))[:1000]
                trigger.execution_id = execution_result.get('execution_id')

                if not execution_result.get('success'):
                    trigger.error_message = str(execution_result.get('error', 'Unknown error'))[:1000]
                    results['triggers_failed'] += 1
                else:
                    results['triggers_succeeded'] += 1

                trigger.save(update_fields=[
                    'status', 'completed_at', 'execution_time_ms',
                    'result_summary', 'execution_id', 'error_message'
                ])

                results['executions'].append({
                    'trigger_id': str(trigger.id),
                    'title': trigger.title,
                    'agent': agent_name,
                    'success': execution_result.get('success'),
                    'execution_time_ms': execution_time_ms
                })

            except Exception as e:
                logger.error(f"🤖 [WORKSPACE AUTOPILOT] Error processing trigger {trigger.id}: {e}")
                trigger.status = 'failed'
                trigger.error_message = str(e)[:1000]
                trigger.completed_at = timezone.now()
                trigger.save(update_fields=['status', 'error_message', 'completed_at'])

                results['triggers_failed'] += 1
                results['errors'].append({
                    'trigger_id': str(trigger.id),
                    'error': str(e)
                })

        logger.info(
            f"🤖 [WORKSPACE AUTOPILOT] Tick complete | "
            f"Processed: {results['triggers_processed']} | "
            f"Succeeded: {results['triggers_succeeded']} | "
            f"Failed: {results['triggers_failed']} | "
            f"Skipped: {results['triggers_skipped']}"
        )

        return results

    except Exception as e:
        logger.error(f"🤖 [WORKSPACE AUTOPILOT] Fatal error in tick: {e}")
        results['errors'].append({'fatal': str(e)})
        return results


# =============================================================================
# Session 787: Comprehensive Agent Scheduling
# =============================================================================
# All 73 agents should run autonomously. These tasks organize agents into
# logical groups with appropriate frequencies.
# =============================================================================



def _impl_run_system_self_audit():
    """
    Session 823: Run a comprehensive system self-audit with LIVE DATA.

    This task:
    1. Queries actual database counts (agents, spiders, tasks, etc.)
    2. Checks body system health by calling actual services
    3. Measures recent activity (executions, spider data, LLM calls)
    4. Identifies errors and failing components
    5. Tracks revenue and remediation status
    6. Passes all this REAL data to TechnicalDocumentAgent for analysis

    The report is saved to docs/audits/ where it will be discovered
    by the autonomous remediation system.

    Runs weekly on Sundays at 3am.
    """
    import os
    from datetime import datetime
    from pathlib import Path

    logger.info("📋 [SYSTEM AUDIT] Starting periodic system self-audit with LIVE DATA...")

    try:
        # Get current session number from 00-START-NEXT-SESSION.md
        import re
        session_number = 823  # Default
        session_file_path = Path(__file__).parent.parent / '00-START-NEXT-SESSION.md'
        if session_file_path.exists():
            content = session_file_path.read_text()
            match = re.search(r'^#\s+Session\s+(\d+)', content, re.MULTILINE)
            if match:
                session_number = int(match.group(1))

        # =====================================================================
        # GATHER LIVE SYSTEM METRICS
        # =====================================================================
        logger.info("📊 [SYSTEM AUDIT] Gathering live system metrics...")
        live_metrics = _gather_live_system_metrics()
        metrics_text = _format_metrics_for_audit(live_metrics)
        logger.info(f"📊 [SYSTEM AUDIT] Gathered metrics: {len(live_metrics)} categories")

        # Import and run the TechnicalDocumentAgent
        from core.agents.technical_document_agent import TechnicalDocumentAgent

        agent = TechnicalDocumentAgent()

        # Create the audit task with LIVE DATA
        audit_task = f"""
        Perform a comprehensive SYSTEM SELF-AUDIT of the Donkey Betz Platform.

        IMPORTANT: Below are LIVE METRICS queried directly from the database.
        Use these ACTUAL numbers in your analysis, not estimates from documentation.

        {metrics_text}

        Based on the LIVE DATA above, generate an audit report that:

        1. VERIFIES COMPONENT COUNTS:
           - Compare actual counts to expected (74 agents, 77 spiders, ~235 Celery tasks)
           - Flag any significant discrepancies

        2. ANALYZES SYSTEM HEALTH:
           - Which body systems are healthy vs having issues?
           - Are agents actively executing tasks?
           - Is spider data being collected?

        3. IDENTIFIES CRITICAL ISSUES (P0-P1):
           - Zero activity in key areas
           - High error rates
           - Body systems in error state
           - No revenue being tracked

        4. IDENTIFIES IMPROVEMENT OPPORTUNITIES (P2-P3):
           - Low activity areas
           - Missing integrations
           - Optimization opportunities

        5. RECOMMENDS SPECIFIC ACTIONS:
           - What needs immediate attention?
           - What can be automated?
           - What's working well and should be preserved?

        Output a formal audit report with findings categorized by priority (P0-P3).
        Include the actual numbers from the live metrics.
        Be specific about what's working and what's not.
        """

        context = {
            'doc_type': 'analysis_report',
            'stage': 4,
            'topic': f'Session {session_number} System Self-Audit',
            'classification': 'INTERNAL',
            'is_system_audit': True,
            'live_metrics': live_metrics,  # Include raw metrics for potential tool use
        }

        result = agent.execute(task=audit_task, context=context)

        if result.success and result.data:
            # Save the audit report to docs/audits/
            audit_dir = Path(__file__).parent.parent / 'docs' / 'audits'
            audit_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            audit_filename = f'SYSTEM_SELF_AUDIT_{timestamp}.md'
            audit_path = audit_dir / audit_filename

            # Extract content from result
            content = result.data.get('content', {})
            full_text = content.get('full_text', '') if isinstance(content, dict) else str(content)

            if full_text:
                # Add header with live metrics summary
                header = f"""# System Self-Audit Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Session:** {session_number}
**Agent:** TechnicalDocumentAgent
**Type:** Automated Self-Audit (LIVE DATA)

## Quick Stats (Live)
| Metric | Value |
|--------|-------|
| Agents | {live_metrics.get('components', {}).get('agents_in_db', 'N/A')} |
| Spiders | {live_metrics.get('components', {}).get('spiders_in_db', 'N/A')} |
| Celery Tasks | {live_metrics.get('components', {}).get('celery_tasks', 'N/A')} |
| Executions (24h) | {live_metrics.get('activity', {}).get('agent_executions_24h', 'N/A')} |
| Spider Entries (24h) | {live_metrics.get('activity', {}).get('spider_entries_24h', 'N/A')} |
| LLM Calls (24h) | {live_metrics.get('activity', {}).get('llm_calls_24h', 'N/A')} |
| Revenue (Total) | ${live_metrics.get('revenue', {}).get('total_amount', 0):.2f} |

---

"""
                audit_path.write_text(header + full_text)
                logger.info(f"✅ [SYSTEM AUDIT] Saved audit to {audit_filename}")

                return {
                    'success': True,
                    'audit_file': str(audit_path),
                    'session': session_number,
                    'live_metrics': live_metrics,
                }
            else:
                logger.warning("⚠️ [SYSTEM AUDIT] Agent returned no content")
                return {'success': False, 'error': 'No audit content generated', 'live_metrics': live_metrics}

        else:
            logger.error(f"❌ [SYSTEM AUDIT] Agent failed: {result.message}")
            return {'success': False, 'error': result.message, 'live_metrics': live_metrics}

    except Exception as e:
        logger.exception(f"❌ [SYSTEM AUDIT] Self-audit failed: {e}")
        raise ScheduledTaskError(
            f"SCHEDULED_FAIL_LOUD::run_system_self_audit::{type(e).__name__}: {e}"
        ) from e


# =============================================================================
# Session 820: Autonomous Remediation System Tasks
# =============================================================================



def _impl_analyze_pa_tool_patterns():
    """
    Mine last 24h of ToolCallRecord for PA tool-call patterns.

    Detects 4 pattern types:
    - param_correction: same tool retried in same conversation with different
      params after a failure → first failed, second succeeded
    - error_pattern: same tool + param combo fails >3 times across conversations
    - success_pattern: specific param combos with >80% success rate and >5 uses
    - follow_up: tool B consistently called within 60s after tool A succeeds
    """
    from core.models_tool_calls import ToolCallRecord, PAToolInsight
    from django.db.models import Count, Q, Avg
    import hashlib as _hl

    cutoff = timezone.now() - timedelta(hours=24)
    records = ToolCallRecord.objects.filter(
        created_at__gte=cutoff,
        agent_name='PersonalAssistant',
    )
    total = records.count()
    if total < 5:
        logger.info("[PA-LEARNING] <5 PA tool calls in last 24h, skipping")
        return {'status': 'skipped', 'reason': 'insufficient_data', 'records': total}

    created = 0
    updated = 0

    # --- 1. param_correction: retry-in-conversation pattern ---
    conv_ids = (
        records.filter(conversation_id__isnull=False)
        .values_list('conversation_id', flat=True)
        .distinct()
    )
    for conv_id in conv_ids:
        conv_calls = list(
            records.filter(conversation_id=conv_id)
            .order_by('created_at')
            .values('tool_name', 'parameters', 'success', 'error_message')
        )
        # Look for fail → success pairs on same tool
        failed = {}
        for call in conv_calls:
            tn = call['tool_name']
            if not call['success']:
                failed[tn] = call
            elif tn in failed and call['success']:
                fail_params = failed.pop(tn)
                if call['parameters'] != fail_params['parameters']:
                    pattern_key = json.dumps(
                        {'tool': tn, 'bad': fail_params['parameters'], 'good': call['parameters']},
                        sort_keys=True, default=str,
                    )
                    pattern_hash = _hl.md5(pattern_key.encode()).hexdigest()
                    pattern = {
                        'hash': pattern_hash,
                        'bad_params': fail_params['parameters'],
                        'good_params': call['parameters'],
                        'error': fail_params.get('error_message', ''),
                    }
                    snippet = (
                        f"When using {tn}, prefer {_summarize_diff(fail_params['parameters'], call['parameters'])}. "
                        f"Previous error: {fail_params.get('error_message', 'unknown')[:120]}"
                    )
                    c, u = _upsert_insight(tn, 'param_correction', pattern, snippet)
                    created += c
                    updated += u

    # --- 2. error_pattern: repeated failures ---
    error_groups = (
        records.filter(success=False)
        .values('tool_name', 'error_message')
        .annotate(cnt=Count('id'))
        .filter(cnt__gt=3)
    )
    for eg in error_groups:
        pattern = {'error': eg['error_message'][:500]}
        snippet = (
            f"Known error: {eg['error_message'][:200]}. "
            f"Occurred {eg['cnt']} times in 24h — double-check parameters."
        )
        c, u = _upsert_insight(eg['tool_name'], 'error_pattern', pattern, snippet)
        created += c
        updated += u

    # --- 3. success_pattern: high-success param combos ---
    tool_param_groups = (
        records.values('tool_name', 'parameters')
        .annotate(
            total=Count('id'),
            successes=Count('id', filter=Q(success=True)),
        )
        .filter(total__gt=5)
    )
    for tpg in tool_param_groups:
        rate = tpg['successes'] / tpg['total']
        if rate >= 0.8:
            params = tpg['parameters']
            if not params:
                continue
            pattern = {'params': params}
            snippet = (
                f"Reliable combo ({rate:.0%} success over {tpg['total']} calls): "
                f"{_summarize_params(params)}"
            )
            c, u = _upsert_insight(tpg['tool_name'], 'success_pattern', pattern, snippet, confidence=rate)
            created += c
            updated += u

    # --- 4. follow_up: tool B after tool A ---
    conv_ids_list = list(conv_ids[:100])  # cap to avoid huge loops
    pair_counts: dict = {}
    for conv_id in conv_ids_list:
        calls = list(
            records.filter(conversation_id=conv_id, success=True)
            .order_by('created_at')
            .values('tool_name', 'created_at')
        )
        for i in range(len(calls) - 1):
            a, b = calls[i], calls[i + 1]
            delta = (b['created_at'] - a['created_at']).total_seconds()
            if delta <= 60 and a['tool_name'] != b['tool_name']:
                key = (a['tool_name'], b['tool_name'])
                pair_counts[key] = pair_counts.get(key, 0) + 1

    for (tool_a, tool_b), count in pair_counts.items():
        if count >= 3:
            pattern = {'after': tool_a, 'then': tool_b}
            snippet = f"Users often call {tool_b} right after {tool_a} — consider suggesting it."
            conf = min(count / 10, 1.0)
            c, u = _upsert_insight(tool_a, 'follow_up', pattern, snippet, confidence=conf)
            created += c
            updated += u

    # --- 5. consistency_check: same tool+params → contradictory outcomes ---
    tool_param_all = (
        records.values('tool_name', 'parameters')
        .annotate(
            total=Count('id'),
            successes=Count('id', filter=Q(success=True)),
            failures=Count('id', filter=Q(success=False)),
        )
        .filter(total__gte=3)
    )
    for tpa in tool_param_all:
        s, f = tpa['successes'], tpa['failures']
        if s > 0 and f > 0:
            rate = s / tpa['total']
            if 0.30 <= rate <= 0.70:
                params = tpa['parameters']
                if not params:
                    continue
                pattern = {'params': params, 'success_rate': round(rate, 2)}
                snippet = (
                    f"Inconsistent results ({rate:.0%} success over {tpa['total']} calls) "
                    f"with params: {_summarize_params(params)}. Needs investigation."
                )
                c, u = _upsert_insight(
                    tpa['tool_name'], 'consistency_check', pattern, snippet, confidence=rate,
                )
                created += c
                updated += u

    logger.info(
        f"[PA-LEARNING] Analyzed {total} records: "
        f"{created} new insights, {updated} updated"
    )
    return {'status': 'ok', 'records': total, 'created': created, 'updated': updated}



