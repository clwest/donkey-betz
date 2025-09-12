"""
Personal Memory Views
Separate endpoints for accessing personal memories with strict authentication
"""

from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import datetime
import logging

from core.rag_integration import search_personal_memories
from core.memory_access_control import (
    MemoryAccessController, 
    require_personal_memory_access, 
    log_memory_access
)

logger = logging.getLogger(__name__)
User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@require_personal_memory_access
def search_personal_memories_api(request):
    """
    Search user's personal memories with strict access control
    """
    user = request.user
    
    try:
        # Get search parameters
        query = request.data.get('query', '').strip()
        limit = min(int(request.data.get('limit', 10)), 50)  # Cap at 50
        similarity_threshold = float(request.data.get('similarity_threshold', 0.7))
        
        if not query:
            return Response({
                'error': 'Query is required',
                'timestamp': datetime.now().isoformat()
            }, status=400)
        
        # Verify user access
        access_controller = MemoryAccessController()
        if not access_controller.verify_user_access(user, user.id):
            return Response({
                'error': 'Access denied',
                'timestamp': datetime.now().isoformat()
            }, status=403)
        
        logger.info(f"Personal memory search by user {user.id}: {query[:50]}...")
        
        # Search personal memories
        results = search_personal_memories(
            query=query,
            user_id=user.id,
            limit=limit,
            similarity_threshold=similarity_threshold
        )
        
        # Additional filtering for extra security
        filtered_results = access_controller.filter_personal_results(results, user.id)
        
        # Log access
        log_memory_access(
            user_id=user.id,
            query=query,
            results_count=len(filtered_results),
            access_type='personal_search'
        )
        
        return Response({
            'results': filtered_results,
            'query': query,
            'total_found': len(filtered_results),
            'user_id': user.id,
            'timestamp': datetime.now().isoformat(),
            'search_params': {
                'limit': limit,
                'similarity_threshold': similarity_threshold
            }
        })
        
    except Exception as e:
        logger.error(f"Personal memory search error for user {user.id}: {str(e)}")
        return Response({
            'error': f'Search failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def personal_memory_stats(request):
    """
    Get stats about user's personal memories
    """
    user = request.user
    
    try:
        from django.db import connection
        
        # Count personal documents for this user
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM unified_embeddings 
                WHERE metadata->>'namespace' = 'personal'
                AND (metadata->>'owner_id' = %s OR metadata->>'owner_id' IS NULL)
            """, [str(user.id)])
            
            personal_count = cursor.fetchone()[0]
        
        log_memory_access(
            user_id=user.id,
            query="stats",
            results_count=personal_count,
            access_type='stats'
        )
        
        return Response({
            'personal_memories_count': personal_count,
            'user_id': user.id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Personal memory stats error for user {user.id}: {str(e)}")
        return Response({
            'error': f'Stats retrieval failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@require_personal_memory_access
def delete_personal_memory(request):
    """
    Delete a specific personal memory (with user verification)
    """
    user = request.user
    
    try:
        memory_id = request.data.get('memory_id')
        if not memory_id:
            return Response({
                'error': 'Memory ID is required',
                'timestamp': datetime.now().isoformat()
            }, status=400)
        
        from django.db import connection
        
        # Verify ownership before deletion
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT metadata->>'owner_id', metadata->>'namespace'
                FROM unified_embeddings 
                WHERE id = %s
            """, [memory_id])
            
            result = cursor.fetchone()
            if not result:
                return Response({
                    'error': 'Memory not found',
                    'timestamp': datetime.now().isoformat()
                }, status=404)
            
            owner_id, namespace = result
            
            # Verify user owns this memory
            if namespace != 'personal' or (owner_id and str(owner_id) != str(user.id)):
                return Response({
                    'error': 'Access denied - not your memory',
                    'timestamp': datetime.now().isoformat()
                }, status=403)
            
            # Delete the memory
            cursor.execute("""
                DELETE FROM unified_embeddings 
                WHERE id = %s 
                AND metadata->>'namespace' = 'personal'
                AND (metadata->>'owner_id' = %s OR metadata->>'owner_id' IS NULL)
            """, [memory_id, str(user.id)])
            
            deleted_count = cursor.rowcount
        
        log_memory_access(
            user_id=user.id,
            query=f"delete_memory_{memory_id}",
            results_count=deleted_count,
            access_type='delete'
        )
        
        if deleted_count > 0:
            return Response({
                'success': True,
                'message': 'Memory deleted successfully',
                'memory_id': memory_id,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return Response({
                'error': 'Failed to delete memory',
                'timestamp': datetime.now().isoformat()
            }, status=500)
        
    except Exception as e:
        logger.error(f"Delete personal memory error for user {user.id}: {str(e)}")
        return Response({
            'error': f'Deletion failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=500)