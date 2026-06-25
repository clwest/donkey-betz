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
    exclude_personal: bool = True,
    # Session 1234 D12 — D9/D10 filter pushdown
    category: Optional[str] = None,
    document_class: Optional[str] = None,
    is_pinned: Optional[bool] = None,
    min_session: Optional[int] = None,
    include_superseded: bool = False,
) -> List[Dict[str, Any]]:
    """
    Session 1234 D12 — semantic search over Document corpus via pgvector.

    Pre-D12 this function targeted a `unified_embeddings` table that
    doesn't exist (the real Django table is `persistence_unifiedembedding`,
    which was empty even on local DB). Callers silently degraded to
    "no context" because the SQL failed every time.

    D12 pivots to the populated path: pgvector cosine similarity over
    `DocumentEmbedding` (the table the D9 sync + D10 backfill populated,
    ~16k+ rows post-backfill), joined to `Document` for the D9/D10
    type-aware filter pushdown (category / document_class / is_pinned /
    min_session) and default-exclude-superseded ranking.

    Backward-compat: the original signature kwargs (limit / content_types
    / similarity_threshold / namespace / exclude_personal) remain in
    place. `content_types` is treated as a soft hint mapped to
    `document_class` if not explicitly provided.

    Args:
        query: The search query (text → embedding via OpenAI).
        limit: Max results.
        content_types: Optional list of content types — back-compat hint.
            If `document_class` is also unset, the first entry is used
            as the document_class filter.
        similarity_threshold: Minimum cosine similarity (0-1).
        namespace: (legacy) — informational, not currently filtered.
        exclude_personal: (legacy) — Document table has no personal
            namespace; ignored. Kept for signature stability.
        category, document_class, is_pinned, min_session,
            include_superseded: Session 1234 D9/D10 filter pushdown.
            Same semantics as kb_tool action=documents (#2620).

    Returns:
        List of dicts shaped to the legacy contract:
        ``{id, content, content_type, metadata, importance_score,
        similarity_score}``. The retrieval_boost from D9/D10 maps to
        importance_score so downstream ranking still respects it.
    """
    # Create embedding for the query
    query_embedding = create_embedding(query)
    if not query_embedding:
        logger.error("Failed to create query embedding")
        return []

    try:
        from content.models import Document, DocumentEmbedding, ContentStatus

        # Back-compat: if content_types is given and document_class isn't,
        # use the first content_type as a document_class hint. Avoids
        # breaking callers that passed e.g. ['document_chunk'] from the
        # legacy unified_embeddings era.
        effective_class = document_class
        if effective_class is None and content_types:
            first = content_types[0] if isinstance(content_types, (list, tuple)) and content_types else None
            if first and isinstance(first, str):
                effective_class = first

        # Base queryset: native pgvector cosine similarity via the
        # existing classmethod (content/models.py:856-887). Inherits
        # the orphan-chunk exclusion (no parent file_path).
        qs = DocumentEmbedding.cosine_similarity_search(
            query_vector=query_embedding,
            limit=limit * 4,  # overshoot so post-filter still hits limit
            min_similarity=similarity_threshold,
        )

        # D9/D10 filter pushdown via Document join
        if category:
            qs = qs.filter(document__category=category)
        if effective_class:
            qs = qs.filter(document__document_class=effective_class)
        if is_pinned is True:
            # Truthy-only — feedback_llm_autofills_boolean_params_with_false.
            qs = qs.filter(document__is_pinned=True)
        if not include_superseded:
            qs = qs.exclude(document__status=ContentStatus.ARCHIVED)
        # Session 1234 D14 — positive-only min_session guard.
        # LLM autofills integer params with 0 the same way it autofills
        # booleans with False; treat anything <= 0 as "no filter" so
        # the corpus isn't silently narrowed to handoff-only.
        if min_session is not None:
            try:
                threshold = int(min_session)
                if threshold > 0:
                    # Filter docs whose tags include any session-N >= threshold.
                    # JSONField tag filtering goes through a Python-side pass
                    # because semantics need int parsing of 'session-N' tags.
                    ok_doc_ids = set()
                    for d in Document.objects.filter(
                        id__in=qs.values_list('document_id', flat=True).distinct(),
                    ).only('id', 'tags'):
                        for t in (d.tags or []):
                            if isinstance(t, str) and t.startswith('session-'):
                                try:
                                    if int(t.split('-', 1)[1]) >= threshold:
                                        ok_doc_ids.add(d.id)
                                        break
                                except (ValueError, IndexError):
                                    continue
                    qs = qs.filter(document_id__in=ok_doc_ids)
            except (ValueError, TypeError):
                pass

        # Take final K after filtering
        qs = qs[:limit]

        documents = []
        encryption_service = get_encryption_service()

        for chunk in qs:
            doc = chunk.document
            # Decrypt content if encrypted; chunk_text usually plaintext.
            try:
                content = encryption_service.decrypt(chunk.chunk_text) if chunk.chunk_text else ''
            except Exception:
                content = chunk.chunk_text or ''

            # Cosine similarity = 1 - distance (annotation set by the
            # classmethod). Guard against NaN/inf.
            import math
            distance = getattr(chunk, 'distance', None)
            if distance is None:
                similarity = 0.0
            else:
                similarity = float(1 - distance)
                if math.isnan(similarity) or math.isinf(similarity):
                    similarity = 0.0

            documents.append({
                'id': str(chunk.id),
                'content': content[:1000],
                'content_type': doc.document_class or 'document',
                'metadata': {
                    'file_path': doc.file_path,
                    'title': doc.title,
                    'category': doc.category,
                    'document_class': doc.document_class,
                    'is_pinned': doc.is_pinned,
                    'tags': list(doc.tags or []),
                    'chunk_index': chunk.chunk_index,
                    # citation in the same shape as search_docs PA tool
                    'citation': f"[{doc.file_path}#{chunk.chunk_index}]",
                },
                # D9/D10 retrieval_boost maps to legacy importance_score.
                'importance_score': float(doc.retrieval_boost or 1.0),
                'similarity_score': similarity,
            })

        logger.info(
            f"Found {len(documents)} relevant chunks for query "
            f"(filters: category={category} class={effective_class} "
            f"is_pinned={is_pinned} min_session={min_session} "
            f"include_superseded={include_superseded})"
        )
        return documents

    except Exception as e:
        logger.error(f"Error searching embeddings: {e}", exc_info=True)
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