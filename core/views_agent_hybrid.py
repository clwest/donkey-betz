"""
Hybrid Agent Execution Views

Production-ready views that support both synchronous and asynchronous execution.
"""

import logging
import asyncio
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.hybrid_executor import hybrid_executor, smart_execute_agent

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])  # Change to IsAuthenticated for production
def execute_agent_hybrid(request):
    """
    Execute an agent using the hybrid executor.

    Automatically chooses between sync/async based on availability and configuration.

    Request body:
    {
        "agent_name": "intelligent_job_matcher",
        "task_description": "Find AI jobs",
        "input_data": {...},
        "mode": "auto"  // "sync", "async", or "auto"
    }

    Response for sync mode:
    {
        "success": true,
        "mode": "synchronous",
        "result": {...}
    }

    Response for async mode:
    {
        "success": true,
        "mode": "asynchronous",
        "execution_id": "exec_xxx",
        "task_id": "celery-task-id",
        "status": "queued"
    }
    """
    try:
        agent_name = request.data.get('agent_name')
        mode = request.data.get('mode', 'auto')

        if not agent_name:
            return Response({
                'success': False,
                'error': 'agent_name is required'
            }, status=400)

        task = {
            'task_description': request.data.get('task_description', ''),
            'input': request.data.get('input_data', {}),
            'context': request.data.get('context', {})
        }

        user = request.user if request.user.is_authenticated else None

        # Execute using hybrid executor
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                hybrid_executor.execute_agent(agent_name, task, user, mode)
            )
        finally:
            loop.close()

        if result['success']:
            return Response({
                'success': True,
                'data': result
            })
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'mode': result.get('mode')
            }, status=500)

    except Exception as e:
        logger.error(f"Error in execute_agent_hybrid: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def chain_agents(request):
    """
    Execute a chain of agents with dependencies.

    Request body:
    {
        "chain": [
            {
                "agent": "intelligent_job_matcher",
                "task": {"input": {...}}
            },
            {
                "agent": "job_application_agent",
                "task": {"input": {...}},
                "depends_on": "intelligent_job_matcher"
            }
        ],
        "mode": "auto"
    }
    """
    try:
        chain = request.data.get('chain', [])
        mode = request.data.get('mode', 'auto')

        if not chain:
            return Response({
                'success': False,
                'error': 'chain is required and must not be empty'
            }, status=400)

        user = request.user if request.user.is_authenticated else None

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                hybrid_executor.chain_agents(chain, user, mode)
            )
        finally:
            loop.close()

        return Response({
            'success': result['success'],
            'data': result
        })

    except Exception as e:
        logger.error(f"Error in chain_agents: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def parallel_agents(request):
    """
    Execute multiple agents in parallel.

    Request body:
    {
        "agents": [
            {"agent": "agent1", "task": {...}},
            {"agent": "agent2", "task": {...}}
        ],
        "mode": "auto"
    }
    """
    try:
        agents = request.data.get('agents', [])
        mode = request.data.get('mode', 'auto')

        if not agents:
            return Response({
                'success': False,
                'error': 'agents list is required'
            }, status=400)

        user = request.user if request.user.is_authenticated else None

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                hybrid_executor.parallel_execute(agents, user, mode)
            )
        finally:
            loop.close()

        return Response({
            'success': result['success'],
            'data': result
        })

    except Exception as e:
        logger.error(f"Error in parallel_agents: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_execution_status(request):
    """
    Check the status of an async task.

    Query params:
    - task_id: The Celery task ID

    Returns task status and result if available.
    """
    try:
        task_id = request.GET.get('task_id')

        if not task_id:
            return Response({
                'success': False,
                'error': 'task_id is required'
            }, status=400)

        status = hybrid_executor.get_execution_status(task_id)

        return Response({
            'success': True,
            'data': status
        })

    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def execution_capabilities(request):
    """
    Get information about execution capabilities.

    Returns what execution modes are available.
    """
    try:
        capabilities = {
            'celery_available': hybrid_executor.celery_available,
            'execution_mode': hybrid_executor.execution_mode,
            'supported_modes': ['sync', 'async', 'auto'],
            'features': {
                'synchronous': True,
                'asynchronous': hybrid_executor.celery_available,
                'task_chaining': hybrid_executor.celery_available,
                'parallel_execution': True,
                'background_jobs': hybrid_executor.celery_available,
                'retries': hybrid_executor.celery_available,
                'monitoring': hybrid_executor.celery_available
            },
            'recommendations': []
        }

        # Add recommendations
        if not hybrid_executor.celery_available:
            capabilities['recommendations'].append(
                "Start Celery workers for production use: celery -A backend worker -l info"
            )
            capabilities['recommendations'].append(
                "Start Celery Beat for scheduled tasks: celery -A backend beat -l info"
            )
        else:
            capabilities['recommendations'].append(
                "Celery is running - production ready!"
            )

        return Response({
            'success': True,
            'data': capabilities
        })

    except Exception as e:
        logger.error(f"Error getting capabilities: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def smart_execute(request):
    """
    Smart execution endpoint that automatically chooses the best execution strategy.

    This is the recommended endpoint for production use.

    Request body:
    {
        "agent_name": "agent_name",
        "task": {...},
        "prefer_async": true  // Default true for production
    }
    """
    try:
        agent_name = request.data.get('agent_name')
        task = request.data.get('task', {})
        prefer_async = request.data.get('prefer_async', True)

        if not agent_name:
            return Response({
                'success': False,
                'error': 'agent_name is required'
            }, status=400)

        user = request.user if request.user.is_authenticated else None

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                smart_execute_agent(agent_name, task, user, prefer_async)
            )
        finally:
            loop.close()

        return Response({
            'success': result['success'],
            'data': result,
            'recommendation': 'Use async mode for production' if not prefer_async else None
        })

    except Exception as e:
        logger.error(f"Error in smart_execute: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)