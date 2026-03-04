"""
RAG (Retrieval-Augmented Generation) Integration
Connects to unified_embeddings table for context retrieval
"""

import logging
import os
import psycopg2
from typing import List, Dict, Any, Optional

# Import the migrated encryption service
from core.encryption_service import get_encryption_service

logger = logging.getLogger(__name__)

def create_embedding(text: str, model: str = "text-embedding-3-small") -> Optional[List[float]]:
    """Create embedding for a text using the centralized EmbeddingService (with Redis cache)."""
    try:
        from core.services.embedding_service import get_embedding_service
        service = get_embedding_service()
        result = service.create_embedding(text, model=model, agent_name='rag_integration', log_usage=True)
        return result.embedding
    except Exception as e:
        logger.error(f"Failed to create embedding: {e}")
        return None

def search_embeddings(
    query: str,
    limit: int = 5,
    content_types: Optional[List[str]] = None,
    similarity_threshold: float = 0.7,
    namespace: Optional[str] = 'system',
    exclude_personal: bool = True
) -> List[Dict[str, Any]]:
    """
    Search unified_embeddings table in ai_unified_platform database for relevant context
    
    Args:
        query: The search query
        limit: Maximum number of results to return
        content_types: Optional list of content types to filter
        similarity_threshold: Minimum similarity score (0-1)
        namespace: Specific namespace to search ('system', 'personal', 'agent_memory', 'public')
        exclude_personal: Whether to exclude personal memories (default: True for privacy)
    
    Returns:
        List of relevant documents with similarity scores
    """
    
    # Create embedding for the query
    query_embedding = create_embedding(query)
    if not query_embedding:
        logger.error("Failed to create query embedding")
        return []
    
    try:
        # Connect to the default database where unified_embeddings actually exists
        conn = psycopg2.connect(
            host='localhost',
            database='unified_donkey_betz',
            user='postgres',
            password=''  # No password for local postgres
        )
        
        with conn.cursor() as cursor:
            # Build the SQL query with vector similarity search
            sql = """
                SELECT 
                    id,
                    content_text,
                    content_type,
                    metadata,
                    importance_score,
                    1 - (embedding <=> %s::vector) as similarity
                FROM unified_embeddings
                WHERE embedding IS NOT NULL
            """
            
            params = [query_embedding]
            
            # Add content type filter if specified
            if content_types:
                # Use proper parameterized query
                sql += f" AND content_type = ANY(%s)"
                params.append(content_types)
            
            # Add namespace filtering for memory isolation
            if exclude_personal:
                # CRITICAL: Exclude personal memories for privacy
                sql += " AND (metadata->>'namespace' IS NULL OR metadata->>'namespace' != 'personal')"
                sql += " AND (metadata->>'searchable_by_agents' IS NULL OR metadata->>'searchable_by_agents' = 'true')"
            elif namespace:
                # Search specific namespace if provided
                sql += " AND metadata->>'namespace' = %s"
                params.append(namespace)
            
            sql += " AND 1 - (embedding <=> %s::vector) >= %s"
            params.extend([query_embedding, similarity_threshold])
            
            # Order by similarity and importance
            sql += """
                ORDER BY 
                    (1 - (embedding <=> %s::vector)) * importance_score DESC
                LIMIT %s
            """
            params.extend([query_embedding, limit])
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            # Format results
            documents = []
            encryption_service = get_encryption_service()
            
            for row in results:
                doc_id, content_text, content_type, metadata, importance, similarity = row
                
                # Decrypt content if encrypted using the migrated service
                decrypted_content = encryption_service.decrypt(content_text) if content_text else ""
                
                # Parse metadata
                meta = metadata if isinstance(metadata, dict) else {}
                
                # Handle NaN values
                import math
                similarity_val = float(similarity) if similarity else 0.0
                if math.isnan(similarity_val) or math.isinf(similarity_val):
                    similarity_val = 0.0
                    
                documents.append({
                    'id': doc_id,
                    'content': decrypted_content[:1000],  # Limit content length
                    'content_type': content_type,
                    'metadata': meta,
                    'importance_score': float(importance) if importance else 0.5,
                    'similarity_score': similarity_val
                })
            
            logger.info(f"Found {len(documents)} relevant documents for query")
            conn.close()  # Close the connection to ai_unified_platform
            return documents
            
    except Exception as e:
        logger.error(f"Error searching embeddings: {e}")
        if 'conn' in locals():
            conn.close()
        return []

def get_rag_context(query: str, max_tokens: int = 2000, include_personal: bool = False) -> Dict[str, Any]:
    """
    Get RAG context for a query
    
    Args:
        query: The user's query
        max_tokens: Maximum tokens to include in context
        include_personal: Whether to include personal memories (default: False)
        
    Returns:
        Dictionary with context and metadata
    """
    
    # Search for relevant documents
    documents = search_embeddings(
        query=query,
        limit=10,  # Get more initially, then filter
        similarity_threshold=0.6,  # Lower threshold to get more results
        exclude_personal=not include_personal  # Respect privacy by default
    )
    
    if not documents:
        logger.info("No relevant documents found for RAG")
        return {
            'has_context': False,
            'documents': [],
            'context_text': ""
        }
    
    # Build context text
    context_parts = []
    used_documents = []
    current_tokens = 0
    
    for doc in documents:
        # Estimate tokens (rough approximation)
        doc_tokens = len(doc['content']) // 4
        
        if current_tokens + doc_tokens > max_tokens:
            break
            
        context_parts.append(f"[{doc['content_type'].upper()}] {doc['content']}")
        used_documents.append({
            'id': doc['id'],
            'type': doc['content_type'],
            'similarity': doc['similarity_score']
        })
        current_tokens += doc_tokens
    
    context_text = "\n\n".join(context_parts)
    
    return {
        'has_context': bool(context_text),
        'documents': used_documents,
        'context_text': context_text,
        'total_documents': len(documents),
        'used_documents': len(used_documents)
    }

def search_personal_memories(
    query: str,
    user_id: Optional[int] = None,
    limit: int = 5,
    similarity_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Search personal memories with strict access control
    
    Args:
        query: The search query
        user_id: ID of the user whose memories to search
        limit: Maximum number of results to return
        similarity_threshold: Minimum similarity score (0-1)
    
    Returns:
        List of relevant personal documents with similarity scores
    """
    
    if not user_id:
        logger.warning("Attempted to search personal memories without user_id")
        return []  # No user, no personal memories
    
    # Create embedding for the query
    query_embedding = create_embedding(query)
    if not query_embedding:
        logger.error("Failed to create query embedding for personal search")
        return []
    
    try:
        # Connect to ai_unified_platform database
        conn = psycopg2.connect(
            host='localhost',
            database='ai_unified_platform',
            user='ai_unified_user',
            password=os.environ.get('AI_UNIFIED_DB_PASS', '')
        )
        
        with conn.cursor() as cursor:
            # Search ONLY personal namespace with user verification
            sql = """
                SELECT 
                    id,
                    content_text,
                    content_type,
                    metadata,
                    importance_score,
                    1 - (embedding <=> %s::vector) as similarity
                FROM unified_embeddings
                WHERE embedding IS NOT NULL
                AND metadata->>'namespace' = 'personal'
                AND (metadata->>'owner_id' = %s OR metadata->>'owner_id' IS NULL)
                AND 1 - (embedding <=> %s::vector) >= %s
                ORDER BY 
                    (1 - (embedding <=> %s::vector)) * importance_score DESC
                LIMIT %s
            """
            
            params = [
                query_embedding,
                str(user_id),
                query_embedding,
                similarity_threshold,
                query_embedding,
                limit
            ]
            
            cursor.execute(sql, params)
            results = cursor.fetchall()
            
            # Format results
            documents = []
            encryption_service = get_encryption_service()
            
            for row in results:
                doc_id, content_text, content_type, metadata, importance, similarity = row
                
                # Decrypt content if encrypted
                decrypted_content = encryption_service.decrypt(content_text) if content_text else ""
                
                # Parse metadata
                meta = metadata if isinstance(metadata, dict) else {}
                
                # Handle NaN values
                import math
                similarity_val = float(similarity) if similarity else 0.0
                if math.isnan(similarity_val) or math.isinf(similarity_val):
                    similarity_val = 0.0
                    
                documents.append({
                    'id': doc_id,
                    'content': decrypted_content[:1000],
                    'content_type': content_type,
                    'metadata': meta,
                    'importance_score': float(importance) if importance else 0.5,
                    'similarity_score': similarity_val,
                    'is_personal': True  # Mark as personal for UI
                })
            
            logger.info(f"Found {len(documents)} personal documents for user {user_id}")
            conn.close()
            return documents
            
    except Exception as e:
        logger.error(f"Error searching personal memories: {e}")
        if 'conn' in locals():
            conn.close()
        return []


def enhance_prompt_with_rag(user_message: str, rag_context: Dict[str, Any]) -> str:
    """
    Enhance the user's prompt with RAG context
    
    Args:
        user_message: Original user message
        rag_context: RAG context from get_rag_context
        
    Returns:
        Enhanced prompt with context
    """
    
    if not rag_context.get('has_context'):
        return user_message
    
    enhanced_prompt = f"""You have access to the following relevant context from the knowledge base:

{rag_context['context_text']}

Based on this context and your knowledge, please answer the following question:

{user_message}

Please incorporate relevant information from the context in your response where appropriate."""
    
    return enhanced_prompt