"""
Celery tasks for agent execution and orchestration.
"""

import logging
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from celery import shared_task, Task
from celery.exceptions import MaxRetriesExceededError
from django.utils import timezone
from django.core.cache import cache
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import (
    AgentExecution, 
    UnifiedAgentTemplate,
    AgentStatus,
    AgentOrchestration
)
from content.ai_providers import AIProviderManager

logger = logging.getLogger(__name__)


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
        
        # Prepare the prompt
        system_prompt = agent_template.system_prompt
        user_prompt = f"""
Task: {execution.task_description}

Input Data:
{json.dumps(execution.input_data, indent=2)}

Context:
{json.dumps(execution.context, indent=2)}

Please complete this task using your specialized capabilities.
"""
        
        # Update progress
        execution.current_step = "Processing with AI model"
        execution.progress_percentage = 50
        execution.save()
        
        send_execution_update(execution_id, {
            'progress': 50,
            'current_step': 'Processing with AI model'
        })
        
        # Execute the AI call
        start_time = timezone.now()
        
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
            execution.output_data = {
                'response': result_content,
                'metadata': {
                    'model': agent_template.llm_model,
                    'provider': agent_template.llm_provider,
                    'execution_time': execution_time
                }
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


@shared_task
def execute_orchestration(orchestration_id: int):
    """
    Execute an agent orchestration with multiple agents.
    
    Args:
        orchestration_id: The ID of the AgentOrchestration instance
    """
    try:
        orchestration = AgentOrchestration.objects.get(id=orchestration_id)
        
        # Implementation for orchestration execution
        # This would coordinate multiple agent executions
        # based on the orchestration strategy
        
        logger.info(f"Executing orchestration {orchestration_id}")
        
        # TODO: Implement orchestration logic
        # - Parse workflow definition
        # - Execute agents in sequence/parallel
        # - Handle dependencies
        # - Aggregate results
        
    except AgentOrchestration.DoesNotExist:
        logger.error(f"Orchestration {orchestration_id} not found")
        raise