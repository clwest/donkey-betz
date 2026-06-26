"""
Personal Memory Views
Separate endpoints for accessing personal memories with strict authentication
"""

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
def search_personal_memories_api(request, **kwargs):
    """Search user's personal memories with strict access control.

    Session 1237 P2.a: added ``**kwargs`` to absorb the ``user_id``
    passthrough that `@require_personal_memory_access` injects. Pre-fix
    every DRF dispatch raised `TypeError: unexpected keyword argument
    'user_id'`. The endpoint had been silently broken — same shape as
    the two sibling functions Session 1235 PR #2639 fixed (this one was
    left untouched per "don't fix outside scope" at that time).
    We read ``request.user`` directly so the kwarg is redundant.
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
def personal_memory_stats(request, **kwargs):
    """Get stats about user's personal memories.

    Note: ``**kwargs`` absorbs the ``user_id`` passthrough that the
    upstream `@require_personal_memory_access` decorator injects on
    other views in this file. We read ``request.user`` directly so
    the kwarg is redundant, but the signature must accept it to avoid
    `TypeError: unexpected keyword argument`.

    Session 1235 P5#3 audit Tranche 1 PR #4: pivoted from dead
    `unified_embeddings` raw-SQL query to live `UserEmbedding` ORM
    (same model D21 PR #2631 validated for the read-path
    `search_personal_memories`). Pre-pivot the cursor.execute would
    raise `relation "unified_embeddings" does not exist`, caught by
    broad except → 500 with error string. Endpoint silently degraded.
    """
    user = request.user

    try:
        from django.apps import apps
        UserEmbedding = apps.get_model('core', 'UserEmbedding')

        personal_count = UserEmbedding.objects.filter(
            user_id=user.id,
            is_active=True,
        ).count()

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
def delete_personal_memory(request, **kwargs):
    """Delete a specific personal memory (with user verification).

    Note: ``**kwargs`` absorbs the ``user_id`` passthrough that
    `@require_personal_memory_access` injects. We read ``request.user``
    directly so the kwarg is redundant.

    Session 1235 P5#3 audit Tranche 1 PR #4: pivoted from dead
    `unified_embeddings` raw-SQL DELETE to live `UserEmbedding` ORM.
    Pre-pivot every delete raised on the dead-table SELECT, caught by
    broad except → 500 "Deletion failed: relation does not exist".

    Access control simplified: pre-pivot relied on `metadata->>'namespace' =
    'personal' AND owner_id == user.id`. UserEmbedding is implicitly
    user-scoped via its `user` ForeignKey, so filtering by user_id IS
    the access check — no separate namespace field needed.
    """
    user = request.user

    try:
        memory_id = request.data.get('memory_id')
        if not memory_id:
            return Response({
                'error': 'Memory ID is required',
                'timestamp': datetime.now().isoformat()
            }, status=400)

        from django.apps import apps
        UserEmbedding = apps.get_model('core', 'UserEmbedding')

        # Verify ownership via user_id-scoped lookup. If the memory exists
        # but belongs to another user, the queryset returns empty — same
        # 404 path as truly-missing memory. This is stricter than the
        # pre-pivot version (which fetched the row first to distinguish
        # 404 from 403) but the surface only signals "you have no such
        # memory" either way — no info leak to the requesting user.
        memory = UserEmbedding.objects.filter(
            id=memory_id,
            user_id=user.id,
        ).first()

        if not memory:
            return Response({
                'error': 'Memory not found or access denied',
                'timestamp': datetime.now().isoformat()
            }, status=404)

        memory.delete()
        deleted_count = 1

        log_memory_access(
            user_id=user.id,
            query=f"delete_memory_{memory_id}",
            results_count=deleted_count,
            access_type='delete'
        )

        return Response({
            'success': True,
            'message': 'Memory deleted successfully',
            'memory_id': memory_id,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Delete personal memory error for user {user.id}: {str(e)}")
        return Response({
            'error': f'Deletion failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=500)