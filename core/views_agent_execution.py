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