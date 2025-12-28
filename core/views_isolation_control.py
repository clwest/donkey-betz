"""
Document Isolation Control Views
API endpoints to start, stop, and monitor background document isolation
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
import logging
from celery import current_app
from celery.result import AsyncResult

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_document_isolation(request):
    """
    Start background document isolation process
    """
    try:
        # Get parameters
        batch_size = int(request.data.get('batch_size', 50))
        max_batches = request.data.get('max_batches', None)
        if max_batches is not None:
            max_batches = int(max_batches)
        
        # Validate parameters
        if batch_size < 10 or batch_size > 200:
            return Response({
                'error': 'batch_size must be between 10 and 200',
                'timestamp': datetime.now().isoformat()
            }, status=400)
        
        # Check if isolation task is already running
        from core.tasks import isolate_documents_batch
        
        # Start the background task
        task = isolate_documents_batch.delay(
            batch_size=batch_size,
            max_batches=max_batches
        )
        
        logger.info(f"Started document isolation task {task.id} with batch_size={batch_size}, max_batches={max_batches}")
        
        return Response({
            'message': 'Document isolation started',
            'task_id': task.id,
            'status': 'PENDING',
            'batch_size': batch_size,
            'max_batches': max_batches,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to start document isolation: {e}")
        return Response({
            'error': f'Failed to start isolation: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def isolation_task_status(request, task_id):
    """
    Get status of a specific isolation task
    """
    try:
        result = AsyncResult(task_id, app=current_app)
        
        if result.state == 'PENDING':
            response = {
                'state': result.state,
                'message': 'Task is waiting to start...',
                'timestamp': datetime.now().isoformat()
            }
        elif result.state == 'PROGRESS':
            response = {
                'state': result.state,
                'processed': result.info.get('processed', 0),
                'total_found': result.info.get('total_found', 0),
                'batch_count': result.info.get('batch_count', 0),
                'stats': result.info.get('stats', {}),
                'rate_per_second': result.info.get('rate_per_second', 0),
                'batch_time': result.info.get('batch_time', 0),
                'timestamp': datetime.now().isoformat()
            }
        elif result.state == 'SUCCESS':
            response = {
                'state': result.state,
                'result': result.info,
                'timestamp': datetime.now().isoformat()
            }
        elif result.state == 'FAILURE':
            response = {
                'state': result.state,
                'error': str(result.info),
                'timestamp': datetime.now().isoformat()
            }
        else:
            response = {
                'state': result.state,
                'message': f'Task is in {result.state} state',
                'timestamp': datetime.now().isoformat()
            }
        
        return Response(response)
        
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        return Response({
            'error': f'Failed to get status: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_isolation_task(request, task_id):
    """
    Stop a running isolation task
    """
    try:
        result = AsyncResult(task_id, app=current_app)
        
        if result.state in ['PENDING', 'PROGRESS']:
            result.revoke(terminate=True)
            
            logger.info(f"Stopped isolation task {task_id}")
            
            return Response({
                'message': f'Task {task_id} has been stopped',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return Response({
                'message': f'Task {task_id} is not running (state: {result.state})',
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        logger.error(f"Failed to stop task: {e}")
        return Response({
            'error': f'Failed to stop task: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=500)

@api_view(['GET'])
def isolation_progress(request):
    """
    Get overall isolation progress (public endpoint for monitoring)
    """
    try:
        from core.tasks import monitor_isolation_progress
        
        # Run monitoring synchronously for quick response
        status = monitor_isolation_progress.apply().result
        
        return Response(status)
        
    except Exception as e:
        logger.error(f"Failed to get isolation progress: {e}")
        return Response({
            'error': f'Failed to get progress: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_active_tasks(request):
    """
    List all active isolation tasks
    """
    try:
        # Get active tasks from Celery
        inspect = current_app.control.inspect()
        active_tasks = inspect.active()
        
        if not active_tasks:
            return Response({
                'active_tasks': [],
                'message': 'No active tasks found',
                'timestamp': datetime.now().isoformat()
            })
        
        # Filter for isolation tasks
        isolation_tasks = []
        for worker, tasks in active_tasks.items():
            for task in tasks:
                if task['name'] == 'core.tasks.isolate_documents_batch':
                    isolation_tasks.append({
                        'task_id': task['id'],
                        'worker': worker,
                        'args': task.get('args', []),
                        'kwargs': task.get('kwargs', {}),
                        'time_start': task.get('time_start'),
                    })
        
        return Response({
            'active_tasks': isolation_tasks,
            'count': len(isolation_tasks),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to list active tasks: {e}")
        return Response({
            'error': f'Failed to list tasks: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cleanup_isolation(request):
    """
    Run cleanup task to fix any isolation metadata issues
    """
    try:
        from core.tasks import cleanup_isolation_metadata
        
        task = cleanup_isolation_metadata.delay()
        
        logger.info(f"Started isolation cleanup task {task.id}")
        
        return Response({
            'message': 'Isolation cleanup started',
            'task_id': task.id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to start cleanup: {e}")
        return Response({
            'error': f'Failed to start cleanup: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=500)