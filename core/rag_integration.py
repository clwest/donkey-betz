"""
RAG (Retrieval-Augmented Generation) Integration
Connects to unified_embeddings table for context retrieval
"""

import os
import json
import logging
import numpy as np
import psycopg2
from typing import List, Dict, Any, Optional
from django.db import connection
from django.conf import settings
import openai

# Import the migrated encryption service
from core.encryption_service import get_encryption_service

logger = logging.getLogger(__name__)

def create_embedding(text: str, model: str = "text-embedding-3-small") -> Optional[List[float]]:
    """Create embedding for a text using OpenAI"""
    try:
        # Get API key from Django settings (same as AIProviderManager)
        api_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY')
        
        if not api_key:
            logger.error("No OpenAI API key found in settings.AI_PROVIDERS")
            return None
            
        client = openai.OpenAI(api_key=api_key)
        response = client.embeddings.create(
            input=text,
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Failed to create embedding: {e}")
        return None

def search_embeddings(
    query: str,
    limit: int = 5,
    content_types: Optional[List[str]] = None,
    similarity_threshold: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Search unified_embeddings table in ai_unified_platform database for relevant context
    
    Args:
        query: The search query
        limit: Maximum number of results to return
        content_types: Optional list of content types to filter
        similarity_threshold: Minimum similarity score (0-1)
    
    Returns:
        List of relevant documents with similarity scores
    """
    
    # Create embedding for the query
    query_embedding = create_embedding(query)
    if not query_embedding:
        logger.error("Failed to create query embedding")
        return []
    
    try:
        # Connect to ai_unified_platform database instead of default
        conn = psycopg2.connect(
            host='localhost',
            database='ai_unified_platform',
            user='ai_unified_user',
            password='[REDACTED - HISTORICAL SECRET]'
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
            
            # Remove the filter for encrypted content - we can now decrypt everything
            # sql += " AND content_text NOT LIKE %s"
            # params.append('gAAAAA%')
            
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

def get_rag_context(query: str, max_tokens: int = 2000) -> Dict[str, Any]:
    """
    Get RAG context for a query
    
    Args:
        query: The user's query
        max_tokens: Maximum tokens to include in context
        
    Returns:
        Dictionary with context and metadata
    """
    
    # Search for relevant documents
    documents = search_embeddings(
        query=query,
        limit=10,  # Get more initially, then filter
        similarity_threshold=0.6  # Lower threshold to get more results
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