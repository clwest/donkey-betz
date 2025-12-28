"""
Celery tasks for agent execution and orchestration.
"""

import logging
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any

from celery import shared_task, Task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Session 392: Updated to use canonical import path
from core.models.agents_registry import (
    AgentExecution,
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
        
        # Prepare GPT-5-mini compatible prompt with platform awareness
        from agents.platform_integration import inject_platform_tools_prompt

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
                    task_description=task_description,
                    domain=agent_template.specialization or 'general',
                    input_data=input_data or {},
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
    
    Args:
        orchestration_id: The ID of the AgentOrchestration instance
    """
    try:
        orchestration = AgentOrchestration.objects.get(id=orchestration_id)
        
        logger.info(f"Starting orchestration {orchestration_id}: {orchestration.name}")
        
        # Update orchestration status to running
        orchestration.status = AgentStatus.RUNNING
        orchestration.save()
        
        # Get the prompt from workflow definition
        prompt = orchestration.workflow_definition.get('prompt', 'Execute workflow')
        
        # Execute agents based on strategy
        if orchestration.execution_strategy == 'sequential':
            # Sequential execution
            previous_result = None
            for i, agent_info in enumerate(orchestration.agent_sequence):
                logger.info(f"Executing agent {i+1}/{len(orchestration.agent_sequence)}: {agent_info['name']}")
                
                # Create execution record
                execution = AgentExecution.objects.create(
                    user=orchestration.user,
                    parent_orchestration=orchestration,
                    agent_id=agent_info.get('agent_id'),
                    user_prompt=prompt if i == 0 else f"Continue from: {previous_result[:100] if previous_result else 'previous step'}",
                    execution_context={
                        'orchestration_id': str(orchestration_id),
                        'step': i + 1,
                        'total_steps': len(orchestration.agent_sequence),
                        'previous_result': previous_result
                    },
                    status=AgentStatus.RUNNING,
                    execution_order=i + 1
                )
                
                # Mock execution (replace with actual agent execution)
                execution.result = {
                    'output': f"Agent {agent_info['name']} completed successfully",
                    'data': f"Processed: {prompt[:50]}..." if prompt else "Processed workflow"
                }
                execution.status = AgentStatus.COMPLETED
                execution.completed_at = timezone.now()
                execution.save()
                
                previous_result = json.dumps(execution.result)
                
        elif orchestration.execution_strategy == 'parallel':
            # Parallel execution (simplified - in production use celery group)
            executions = []
            for i, agent_info in enumerate(orchestration.agent_sequence):
                execution = AgentExecution.objects.create(
                    user=orchestration.user,
                    parent_orchestration=orchestration,
                    agent_id=agent_info.get('agent_id'),
                    user_prompt=prompt,
                    execution_context={
                        'orchestration_id': str(orchestration_id),
                        'parallel': True
                    },
                    status=AgentStatus.RUNNING,
                    execution_order=i + 1
                )
                executions.append(execution)
            
            # Mock parallel completion
            for execution in executions:
                execution.result = {
                    'output': f"Agent completed in parallel",
                    'data': f"Processed: {prompt[:50]}..." if prompt else "Processed"
                }
                execution.status = AgentStatus.COMPLETED
                execution.completed_at = timezone.now()
                execution.save()
        
        # Mark orchestration as completed
        orchestration.status = AgentStatus.COMPLETED
        orchestration.completed_at = timezone.now()
        orchestration.save()
        
        logger.info(f"Orchestration {orchestration_id} completed successfully")
        
        # Send WebSocket notification if needed
        send_execution_update(str(orchestration_id), {
            'status': 'completed',
            'message': f'Workflow {orchestration.name} completed successfully'
        })
        
        return {
            'success': True,
            'orchestration_id': str(orchestration_id),
            'message': f'Executed {len(orchestration.agent_sequence)} agents successfully'
        }
        
    except AgentOrchestration.DoesNotExist:
        logger.error(f"Orchestration {orchestration_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error executing orchestration {orchestration_id}: {e}")
        if 'orchestration' in locals():
            orchestration.status = AgentStatus.FAILED
            orchestration.error_message = str(e)
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
    
    logger.info(f"🚀 Starting async sports orchestration for {home_team} vs {away_team}")
    
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
                    'content': f'🎯 Starting orchestration for {home_team} vs {away_team}',
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
                        'content': f'✅ Orchestration completed for {home_team} vs {away_team}',
                        'timestamp': datetime.now().isoformat(),
                        'results': orchestration_results
                    }
                }
            )
            
            logger.info(f"✅ Sports orchestration completed successfully for game {game_id}")

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
                logger.info(f"💾 Cached analysis for game {game_id} (cache_key: {cache_key}, TTL: 20 min)")

            return result_data
            
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"❌ Sports orchestration failed for game {game_id}: {str(e)}")
        
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
                    'content': f'❌ Orchestration failed: {str(e)}',
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