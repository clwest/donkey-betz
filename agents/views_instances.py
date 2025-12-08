"""
Views for agent execution instances - provides proper data for the Mission Archive
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
import logging

# Session 392: Updated to use canonical import path
from core.models.agents_registry import AgentExecution, AgentOrchestration, AgentStatus

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_instances(request):
    """
    List agent execution instances for the current user.
    Returns data in the format expected by the frontend Mission Archive.
    """
    try:
        # Get all executions for the current user
        executions = AgentExecution.objects.filter(
            user=request.user
        ).select_related('template', 'parent_orchestration').order_by('-created_at')[:50]
        
        instances = []
        for execution in executions:
            # Format the instance data for the frontend
            instance = {
                'id': str(execution.id),
                'execution_id': execution.execution_id,
                'name': execution.template.name if execution.template else 'Unknown Agent',
                'template': {
                    'id': str(execution.template.id) if execution.template else None,
                    'name': execution.template.name if execution.template else 'Unknown Agent',
                    'specialization': execution.template.specialization if execution.template else None,
                    'description': execution.template.description if execution.template else None,
                } if execution.template else None,
                'task_description': execution.task_description,
                'status': execution.status.lower() if execution.status else 'pending',
                'created_at': execution.created_at.isoformat() if execution.created_at else None,
                'updated_at': execution.updated_at.isoformat() if execution.updated_at else None,
                'completed_at': execution.completed_at.isoformat() if hasattr(execution, 'completed_at') and execution.completed_at else None,
                'result': execution.result if hasattr(execution, 'result') and execution.result else None,
                'error_message': execution.error_message if hasattr(execution, 'error_message') else None,
                'parent_orchestration': {
                    'id': str(execution.parent_orchestration.id),
                    'name': execution.parent_orchestration.name
                } if execution.parent_orchestration else None,
                'metrics': {
                    'execution_time': execution.execution_time if hasattr(execution, 'execution_time') else None,
                    'tokens_used': execution.tokens_used if hasattr(execution, 'tokens_used') else None,
                    'cost': execution.estimated_cost if hasattr(execution, 'estimated_cost') else None,
                }
            }
            instances.append(instance)
        
        logger.info(f"Returning {len(instances)} instances for user {request.user.username}")
        
        return Response({
            'results': instances,
            'count': len(instances),
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error fetching instances: {e}")
        return Response({
            'error': str(e),
            'results': [],
            'success': False
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_instance_status(request, instance_id):
    """
    Get the status of a specific instance.
    """
    try:
        execution = AgentExecution.objects.get(
            Q(id=instance_id) | Q(execution_id=instance_id),
            user=request.user
        )
        
        return Response({
            'id': str(execution.id),
            'execution_id': execution.execution_id,
            'status': execution.status.lower() if execution.status else 'pending',
            'result': execution.result if hasattr(execution, 'result') and execution.result else None,
            'updated_at': execution.updated_at.isoformat() if execution.updated_at else None,
            'success': True
        })
        
    except AgentExecution.DoesNotExist:
        return Response({
            'error': 'Instance not found',
            'success': False
        }, status=404)
    except Exception as e:
        logger.error(f"Error fetching instance status: {e}")
        return Response({
            'error': str(e),
            'success': False
        }, status=500)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_instance(request, instance_id):
    """
    Delete a specific instance.
    """
    try:
        execution = AgentExecution.objects.get(
            Q(id=instance_id) | Q(execution_id=instance_id),
            user=request.user
        )
        execution.delete()
        
        return Response({
            'message': 'Instance deleted successfully',
            'success': True
        })
        
    except AgentExecution.DoesNotExist:
        return Response({
            'error': 'Instance not found',
            'success': False
        }, status=404)
    except Exception as e:
        logger.error(f"Error deleting instance: {e}")
        return Response({
            'error': str(e),
            'success': False
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_multiple_instances(request):
    """
    Delete multiple instances.
    """
    try:
        instance_ids = request.data.get('instance_ids', [])
        if not instance_ids:
            return Response({
                'error': 'No instance IDs provided',
                'success': False
            }, status=400)
        
        # Delete instances belonging to the user
        deleted_count = AgentExecution.objects.filter(
            Q(id__in=instance_ids) | Q(execution_id__in=instance_ids),
            user=request.user
        ).delete()[0]
        
        return Response({
            'message': f'Deleted {deleted_count} instances',
            'successful': instance_ids,
            'failed': [],
            'success': True
        })
        
    except Exception as e:
        logger.error(f"Error deleting multiple instances: {e}")
        return Response({
            'error': str(e),
            'success': False
        }, status=500)