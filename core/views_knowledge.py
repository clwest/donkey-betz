"""
Personal Knowledge Base Views
Handles upload, management, and retrieval of personal knowledge
"""

import json
import logging
import uuid
import psycopg2
from datetime import datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from core.rag_integration import create_embedding

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def personal_knowledge_upload(request):
    """Upload new knowledge to personal knowledge base"""
    try:
        # Get data from request
        title = request.data.get('title', '')
        description = request.data.get('description', '')
        content = request.data.get('content', '')
        category = request.data.get('category', 'note')
        tags = request.data.get('tags', '')
        use_in_generation = request.data.get('use_in_generation', True)
        
        # Handle file upload
        if 'file' in request.FILES:
            file = request.FILES['file']
            content = file.read().decode('utf-8', errors='ignore')
            if not title:
                title = file.name
        
        if not content:
            return Response({'error': 'Content is required'}, status=400)
        
        # Create embedding for the content
        embedding = create_embedding(content)
        
        # Prepare metadata
        metadata = {
            'user_id': request.user.id,
            'title': title or content[:50],
            'description': description,
            'tags': [tag.strip() for tag in tags.split(',') if tag.strip()] if isinstance(tags, str) else tags,
            'use_in_generation': use_in_generation,
            'uploaded_by': request.user.username,
            'upload_date': datetime.now().isoformat()
        }
        
        # Connect to ai_unified_platform database
        conn = psycopg2.connect(
            host='localhost',
            database='ai_unified_platform',
            user='ai_unified_user',
            password='[REDACTED - HISTORICAL SECRET]'
        )
        cursor = conn.cursor()
        
        # Insert into unified_embeddings
        knowledge_id = str(uuid.uuid4())
        insert_query = """
            INSERT INTO unified_embeddings (
                source_database, source_table, source_id,
                content_type, content_text, embedding,
                embedding_model, metadata, importance_score,
                created_at, updated_at
            ) VALUES (
                'unified_donkey_betz', 'personal_knowledge', %s,
                %s, %s, %s,
                'text-embedding-3-small', %s, %s,
                NOW(), NOW()
            )
            RETURNING id
        """
        
        cursor.execute(insert_query, (
            knowledge_id,
            category,
            content,
            embedding,
            json.dumps(metadata),
            0.8  # Default importance score for user uploads
        ))
        
        db_id = cursor.fetchone()[0]
        conn.commit()
        conn.close()
        
        logger.info(f"Uploaded knowledge entry {knowledge_id} for user {request.user.id}")
        
        # Broadcast update to WebSocket clients
        try:
            from core.knowledge_consumer import broadcast_knowledge_update
            broadcast_knowledge_update(
                request.user.id,
                'added',
                {
                    'id': knowledge_id,
                    'title': title or content[:50],
                    'category': category,
                    'word_count': len(content.split()),
                    'created_at': datetime.now().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Failed to broadcast knowledge update: {e}")
        
        return Response({
            'success': True,
            'message': 'Knowledge uploaded successfully',
            'id': knowledge_id,
            'title': title or content[:50],
            'word_count': len(content.split())
        })
        
    except Exception as e:
        logger.error(f"Error uploading knowledge: {e}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def personal_knowledge_delete(request, knowledge_id):
    """Delete a knowledge entry"""
    try:
        # Connect to ai_unified_platform database
        conn = psycopg2.connect(
            host='localhost',
            database='ai_unified_platform',
            user='ai_unified_user',
            password='[REDACTED - HISTORICAL SECRET]'
        )
        cursor = conn.cursor()
        
        # Delete only if owned by user
        delete_query = """
            DELETE FROM unified_embeddings 
            WHERE source_id = %s 
            AND metadata->>'user_id' = %s
            AND source_table = 'personal_knowledge'
        """
        
        cursor.execute(delete_query, (knowledge_id, str(request.user.id)))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            logger.info(f"Deleted knowledge entry {knowledge_id} for user {request.user.id}")
            return Response({
                'success': True,
                'message': 'Knowledge entry deleted'
            })
        else:
            return Response({
                'error': 'Knowledge entry not found or not authorized'
            }, status=404)
            
    except Exception as e:
        logger.error(f"Error deleting knowledge: {e}")
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def personal_knowledge_stats(request):
    """Get detailed statistics about user's knowledge base"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            database='ai_unified_platform',
            user='ai_unified_user',
            password='[REDACTED - HISTORICAL SECRET]'
        )
        cursor = conn.cursor()
        
        # Get comprehensive stats
        stats_query = """
            SELECT 
                COUNT(*) as total_entries,
                COUNT(DISTINCT content_type) as total_categories,
                COUNT(embedding) as entries_with_embeddings,
                AVG(importance_score) as avg_importance,
                MAX(created_at) as last_upload,
                SUM(CASE WHEN created_at >= CURRENT_DATE THEN 1 ELSE 0 END) as uploads_today,
                SUM(CASE WHEN created_at >= CURRENT_DATE - INTERVAL '7 days' THEN 1 ELSE 0 END) as uploads_week
            FROM unified_embeddings
            WHERE metadata->>'user_id' = %s
        """
        
        cursor.execute(stats_query, (str(request.user.id),))
        stats = cursor.fetchone()
        
        # Get top categories
        cat_query = """
            SELECT content_type, COUNT(*) as count
            FROM unified_embeddings
            WHERE metadata->>'user_id' = %s
            GROUP BY content_type
            ORDER BY count DESC
            LIMIT 5
        """
        cursor.execute(cat_query, (str(request.user.id),))
        top_categories = [{'name': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return Response({
            'total_entries': stats[0] if stats else 0,
            'total_categories': stats[1] if stats else 0,
            'entries_with_embeddings': stats[2] if stats else 0,
            'average_importance': float(stats[3]) if stats and stats[3] else 0,
            'last_upload': stats[4].isoformat() if stats and stats[4] else None,
            'uploads_today': stats[5] if stats else 0,
            'uploads_this_week': stats[6] if stats else 0,
            'top_categories': top_categories,
            'storage_used_mb': 0  # Placeholder for future storage tracking
        })
        
    except Exception as e:
        logger.error(f"Error getting knowledge stats: {e}")
        return Response({
            'error': str(e)
        }, status=500)