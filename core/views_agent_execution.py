"""
Enhanced Agent Execution Views

Provides synchronous agent execution without requiring Celery,
making agents immediately available for testing and use.
"""

import logging
import asyncio
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Import the concrete executor
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_core.agents.concrete_executor import concrete_executor, execute_agent_directly

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow any for testing, add auth later
def execute_agent_sync(request):
    """
    Execute an agent synchronously without Celery.

    This endpoint allows immediate agent execution for testing and development.

    Request body:
    {
        "agent_name": "intelligent_job_matcher",
        "task_description": "Find AI jobs",
        "input_data": {
            "skills": ["python", "AI"],
            "location": "remote"
        }
    }
    """
    try:
        # Extract parameters
        agent_name = request.data.get('agent_name')

        if not agent_name:
            return Response({
                'success': False,
                'error': 'agent_name is required',
                'available_agents': concrete_executor.list_available_agents()
            }, status=400)

        # Prepare task configuration
        task = {
            'task_description': request.data.get('task_description', ''),
            'input': request.data.get('input_data', {}),
            'context': request.data.get('context', {}),
            'task_type': request.data.get('task_type', 'general')
        }

        # Get user if authenticated
        user = request.user if request.user.is_authenticated else None

        logger.info(f"🚀 Executing agent '{agent_name}' synchronously")

        # Execute the agent using asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                execute_agent_directly(agent_name, task, user)
            )
        finally:
            loop.close()

        # Return the result
        if result['success']:
            return Response({
                'success': True,
                'data': result,
                'message': f"Agent '{agent_name}' executed successfully"
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'traceback': result.get('traceback', ''),
                'agent': agent_name
            }, status=500)

    except Exception as e:
        logger.error(f"❌ Error in execute_agent_sync: {str(e)}")
        return Response({
            'success': False,
            'error': str(e),
            'message': 'Failed to execute agent'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_executable_agents(request):
    """
    List all agents that can be executed directly.

    Returns information about available agents and their capabilities.
    """
    try:
        agents = concrete_executor.list_available_agents()

        return Response({
            'success': True,
            'data': {
                'total_agents': len(agents),
                'agents': agents,
                'executor_type': 'ConcreteAgentExecutor',
                'features': {
                    'synchronous_execution': True,
                    'ai_enforced': True,
                    'user_context_aware': True,
                    'no_celery_required': True
                }
            }
        })
    except Exception as e:
        logger.error(f"Error listing agents: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def agent_execution_history(request):
    """
    Get recent agent execution history.
    """
    try:
        limit = int(request.GET.get('limit', 10))
        history = concrete_executor.get_execution_history(limit)

        return Response({
            'success': True,
            'data': {
                'history': history,
                'count': len(history),
                'limit': limit
            }
        })
    except Exception as e:
        logger.error(f"Error getting execution history: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def test_agent_execution(request):
    """
    Test endpoint for agent execution with sample data.

    Provides easy testing with pre-configured examples.
    """
    try:
        agent_type = request.data.get('agent_type', 'content')

        # Sample test configurations
        test_configs = {
            'content': {
                'agent_name': 'real_content_creator',
                'task': {
                    'task_description': 'Create blog post about AI trends',
                    'input': {
                        'topic': 'AI Trends in 2025',
                        'type': 'blog',
                        'keywords': ['AI', 'machine learning', 'automation', '2025'],
                        'word_count': 500
                    }
                }
            },
            'job': {
                'agent_name': 'intelligent_job_matcher',
                'task': {
                    'task_description': 'Find remote Python developer jobs',
                    'input': {
                        'skills': ['Python', 'Django', 'React', 'AI'],
                        'experience_level': 'mid',
                        'location': 'remote',
                        'salary_range': {
                            'min': 80000,
                            'max': 150000
                        }
                    }
                }
            },
            'income': {
                'agent_name': 'zero_capital_income_generator',
                'task': {
                    'task_description': 'Generate income plan for $1000 in 30 days',
                    'input': {
                        'target_income': 1000,
                        'timeframe_days': 30,
                        'skill_level': 'intermediate'
                    }
                }
            }
        }

        if agent_type not in test_configs:
            return Response({
                'success': False,
                'error': f'Unknown agent type: {agent_type}',
                'available_types': list(test_configs.keys())
            }, status=400)

        config = test_configs[agent_type]
        user = request.user if request.user.is_authenticated else None

        logger.info(f"🧪 Testing {agent_type} agent: {config['agent_name']}")

        # Execute the test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                execute_agent_directly(config['agent_name'], config['task'], user)
            )
        finally:
            loop.close()

        return Response({
            'success': True,
            'test_type': agent_type,
            'agent': config['agent_name'],
            'result': result
        })

    except Exception as e:
        logger.error(f"❌ Error in test execution: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def execute_agent_batch(request):
    """
    Execute multiple agents in sequence or parallel.

    Request body:
    {
        "agents": [
            {
                "agent_name": "intelligent_job_matcher",
                "input_data": {...}
            },
            {
                "agent_name": "job_application_agent",
                "input_data": {...}
            }
        ],
        "execution_mode": "sequential"  # or "parallel"
    }
    """
    try:
        agents = request.data.get('agents', [])
        execution_mode = request.data.get('execution_mode', 'sequential')

        if not agents:
            return Response({
                'success': False,
                'error': 'No agents provided'
            }, status=400)

        user = request.user if request.user.is_authenticated else None
        results = []

        async def execute_agents():
            if execution_mode == 'parallel':
                # Execute all agents in parallel
                tasks = []
                for agent_config in agents:
                    task = {
                        'task_description': agent_config.get('task_description', ''),
                        'input': agent_config.get('input_data', {})
                    }
                    tasks.append(
                        execute_agent_directly(
                            agent_config['agent_name'],
                            task,
                            user
                        )
                    )
                return await asyncio.gather(*tasks)
            else:
                # Execute agents sequentially
                agent_results = []
                for agent_config in agents:
                    task = {
                        'task_description': agent_config.get('task_description', ''),
                        'input': agent_config.get('input_data', {})
                    }
                    result = await execute_agent_directly(
                        agent_config['agent_name'],
                        task,
                        user
                    )
                    agent_results.append(result)
                return agent_results

        # Run the execution
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(execute_agents())
        finally:
            loop.close()

        # Analyze results
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful

        return Response({
            'success': True,
            'data': {
                'total_agents': len(agents),
                'successful': successful,
                'failed': failed,
                'execution_mode': execution_mode,
                'results': results
            }
        })

    except Exception as e:
        logger.error(f"❌ Error in batch execution: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# Session 760: Agent Execution Detail APIs for Output Modal

@api_view(['GET'])
@permission_classes([AllowAny])
def unified_execution_history(request):
    """
    Get agent execution history from the unified system with full output_data.

    Query params:
    - limit: Number of executions to return (default 20)
    - agent_name: Filter by agent name (optional)
    - status: Filter by status (optional)
    """
    try:
        from core.models_unified_system import AgentExecution

        limit = int(request.GET.get('limit', 20))
        agent_name = request.GET.get('agent_name')
        status = request.GET.get('status')

        queryset = AgentExecution.objects.select_related('agent').order_by('-created_at')

        if agent_name:
            queryset = queryset.filter(agent__name__icontains=agent_name)
        if status:
            queryset = queryset.filter(status=status)

        executions = queryset[:limit]

        return Response({
            'success': True,
            'data': {
                'executions': [
                    {
                        'id': str(ex.id),
                        'agent_name': ex.agent.name if ex.agent else 'Unknown',
                        'task': ex.task[:200] if ex.task else None,
                        'status': ex.status,
                        'output_data': ex.output_data,
                        'error_message': ex.error_message,
                        'tokens_used': ex.tokens_used,
                        'cost': float(ex.cost) if ex.cost else 0,
                        'execution_time_ms': ex.execution_time_ms,
                        'created_at': ex.created_at.isoformat(),
                        'completed_at': ex.completed_at.isoformat() if ex.completed_at else None,
                    }
                    for ex in executions
                ],
                'count': len(executions),
                'limit': limit
            }
        })
    except Exception as e:
        logger.error(f"Error getting unified execution history: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def execution_detail(request, execution_id):
    """
    Get detailed information about a specific execution including full output_data.

    Session 760: Created for Agent Output Detail Modal
    """
    try:
        from core.models_unified_system import AgentExecution, AgentMemory

        try:
            execution = AgentExecution.objects.select_related('agent').get(id=execution_id)
        except AgentExecution.DoesNotExist:
            return Response({
                'success': False,
                'error': f'Execution {execution_id} not found'
            }, status=404)

        # Get related memory if exists
        related_memory = None
        if execution.agent:
            memory = AgentMemory.objects.filter(
                agent=execution.agent,
                source_type='execution',
                created_at__gte=execution.created_at
            ).first()
            if memory:
                related_memory = {
                    'id': str(memory.id),
                    'title': memory.title,
                    'content': memory.content,
                    'valence': memory.valence,
                    'memory_type': memory.memory_type,
                    'importance_score': memory.importance_score,
                }

        return Response({
            'success': True,
            'data': {
                'execution': {
                    'id': str(execution.id),
                    'agent_name': execution.agent.name if execution.agent else 'Unknown',
                    'agent_display_name': execution.agent.display_name if execution.agent else None,
                    'task': execution.task,
                    'status': execution.status,
                    'output_data': execution.output_data,
                    'input_data': execution.input_data,
                    'error_message': execution.error_message,
                    'tokens_used': execution.tokens_used,
                    'cost': float(execution.cost) if execution.cost else 0,
                    'execution_time_ms': execution.execution_time_ms,
                    'created_at': execution.created_at.isoformat(),
                    'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
                },
                'related_memory': related_memory
            }
        })
    except Exception as e:
        logger.error(f"Error getting execution detail: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)