"""
Agent Execution API Endpoints
Handles agent execution requests from the frontend
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from ai_core.agents.execution_queue import execution_queue
from ai_core.agents.execution_queue import Priority

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(['POST'])
async def execute_agent(request, agent_name):
    """
    Execute a specific agent with given task.

    Args:
        agent_name: Name of the agent to execute
        request.body: JSON with task parameters

    Returns:
        Task ID and execution status
    """
    try:
        # Parse request data
        task_data = request.data.get('task', {})
        priority_str = request.data.get('priority', 'MEDIUM')

        # Map priority
        priority_map = {
            'URGENT': Priority.URGENT,
            'HIGH': Priority.HIGH,
            'MEDIUM': Priority.MEDIUM,
            'LOW': Priority.LOW
        }
        priority = priority_map.get(priority_str, Priority.MEDIUM)

        # Check for spider data in session
        spider_data = request.session.get('latest_spider_data')

        # Queue task for execution
        task_id = await execution_queue.add_task(
            agent_name=agent_name,
            task_data=task_data,
            priority=priority,
            spider_data=spider_data
        )

        logger.info(f"✅ Queued task {task_id} for agent {agent_name}")

        return Response({
            'success': True,
            'task_id': task_id,
            'agent': agent_name,
            'status': 'queued',
            'priority': priority_str,
            'message': f'Task queued for execution with priority {priority_str}'
        })

    except Exception as e:
        logger.error(f"❌ Error executing agent {agent_name}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
async def get_task_status(request, task_id):
    """
    Get the status and result of a task.

    Args:
        task_id: ID of the task to check

    Returns:
        Task status and result if available
    """
    try:
        # Get task result
        result = await execution_queue.get_task_result(task_id)

        if result:
            return Response({
                'success': True,
                'task_id': task_id,
                'status': 'completed',
                'result': result
            })
        else:
            # Check if still pending
            import redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            if r.sismember('queue:pending', task_id):
                return Response({
                    'success': True,
                    'task_id': task_id,
                    'status': 'pending',
                    'message': 'Task is still in queue'
                })
            else:
                return Response({
                    'success': False,
                    'task_id': task_id,
                    'status': 'not_found',
                    'message': 'Task not found'
                }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        logger.error(f"❌ Error checking task {task_id}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
async def get_queue_status(request):
    """
    Get the current status of the execution queue.

    Returns:
        Queue metrics and top tasks
    """
    try:
        queue_status = await execution_queue.get_status()

        return Response({
            'success': True,
            'queue': queue_status
        })

    except Exception as e:
        logger.error(f"❌ Error getting queue status: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
async def start_queue(request):
    """
    Start the execution queue processor.
    """
    try:
        await execution_queue.start()

        return Response({
            'success': True,
            'message': 'Execution queue started'
        })

    except Exception as e:
        logger.error(f"❌ Error starting queue: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
async def stop_queue(request):
    """
    Stop the execution queue processor.
    """
    try:
        await execution_queue.stop()

        return Response({
            'success': True,
            'message': 'Execution queue stopped'
        })

    except Exception as e:
        logger.error(f"❌ Error stopping queue: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)