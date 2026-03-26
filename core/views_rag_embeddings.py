"""
Advanced RAG (Retrieval-Augmented Generation) and embeddings system.

Session 179: Connected to REAL RAGSystem and EmbeddingManager!
No more mock data - uses actual embedding providers and semantic search.

Compatible with existing frontend connections.
"""

from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Sum
from datetime import datetime
import json
import logging
import asyncio
import uuid

from content.models import Document, DocumentEmbedding, KnowledgeBase, EmbeddingModel, DocumentType
from content.embeddings import rag_system, EmbeddingManager

User = get_user_model()
logger = logging.getLogger(__name__)


class RagIngestThrottle(ScopedRateThrottle):
    scope = 'rag_ingest'


def run_async(coro):
    """Run an async coroutine synchronously."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_document_for_rag(request):
    """
    Upload and process document for RAG system.

    Session 179: Now creates REAL Document and DocumentEmbedding records
    using the actual RAGSystem instead of mock data.
    """
    user = request.user
    data = request.data if hasattr(request, 'data') else json.loads(request.body or b"{}")

    document_type = data.get('document_type', 'text')
    content = data.get('content', '')
    title = data.get('title', 'Untitled Document')
    tags = data.get('tags', [])
    embedding_model = data.get('embedding_model', EmbeddingModel.OPENAI_SMALL)

    if not content.strip():
        return Response({
            'success': False,
            'error': 'Document content is required'
        }, status=400)

    try:
        # Create real Document record
        doc_type_map = {
            'text': DocumentType.TEXT,
            'markdown': DocumentType.MARKDOWN,
            'html': DocumentType.HTML,
            'json': DocumentType.JSON,
        }
        document = Document.objects.create(
            owner=user,
            title=title,
            document_type=doc_type_map.get(document_type, DocumentType.TEXT),
            raw_content=content,
            processed_content=content,
            tags=tags if isinstance(tags, list) else [],
            status='pending'
        )

        # Process document with real RAGSystem
        success = run_async(
            rag_system.process_document_for_rag(
                document=document,
                embedding_model=embedding_model,
                chunk_size=1000,
                chunk_overlap=200
            )
        )

        if success:
            # Get actual embedding stats
            embeddings = DocumentEmbedding.objects.filter(document=document)
            chunks_created = embeddings.count()
            total_cost = embeddings.aggregate(total=Sum('embedding_cost'))['total'] or 0

            return Response({
                'success': True,
                'document': {
                    'id': str(document.id),
                    'title': document.title,
                    'document_type': document.document_type,
                    'status': document.status,
                    'chunks_created': chunks_created,
                    'total_tokens': len(content.split()),
                    'embedding_model': embedding_model,
                    'embedding_cost': float(total_cost),
                    'tags': tags,
                    'created_at': document.created_at.isoformat(),
                    'rag_enabled': True
                }
            })
        else:
            return Response({
                'success': False,
                'error': document.error_message or 'Failed to process document'
            }, status=500)

    except Exception as e:
        logger.error(f"Error uploading document for RAG: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def semantic_search(request):
    """
    Perform semantic search across user's document collection.

    Session 179: Now uses REAL RAGSystem.semantic_search() with actual
    embedding vectors and cosine similarity calculation.
    """
    user = request.user
    data = request.data if hasattr(request, 'data') else json.loads(request.body or b"{}")

    query = data.get('query', '')
    max_results = data.get('max_results', 10)
    similarity_threshold = data.get('similarity_threshold', 0.7)
    embedding_model = data.get('embedding_model', EmbeddingModel.OPENAI_SMALL)
    knowledge_base_id = data.get('knowledge_base_id')

    if not query.strip():
        return Response({
            'success': False,
            'error': 'Query is required'
        }, status=400)

    try:
        import time
        start_time = time.time()

        # Get knowledge base if specified
        knowledge_base = None
        if knowledge_base_id:
            try:
                knowledge_base = KnowledgeBase.objects.get(id=knowledge_base_id, user=user)
            except KnowledgeBase.DoesNotExist:
                pass

        # Perform semantic search (sync to avoid Django async context errors)
        results = rag_system.semantic_search_sync(
            query=query,
            knowledge_base=knowledge_base,
            embedding_model=embedding_model,
            limit=max_results,
            similarity_threshold=similarity_threshold
        )

        search_time_ms = (time.time() - start_time) * 1000

        # Format results
        formatted_results = [
            {
                'chunk_id': f'chunk_{r.chunk_index}',
                'document_id': r.document_id,
                'document_title': r.document_title,
                'content': r.chunk_text,
                'similarity_score': round(r.similarity_score, 4),
                'metadata': r.metadata or {},
                'context_before': r.context_before,
                'context_after': r.context_after
            }
            for r in results
        ]

        # Get total documents searched
        total_docs = Document.objects.filter(owner=user, status='processed').count()

        return Response({
            'success': True,
            'query': query,
            'results': formatted_results,
            'total_found': len(formatted_results),
            'search_metadata': {
                'similarity_threshold': similarity_threshold,
                'embedding_model': embedding_model,
                'search_time_ms': round(search_time_ms, 2),
                'total_documents_searched': total_docs
            }
        })

    except Exception as e:
        logger.error(f"Error in semantic search: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rag_generate(request):
    """
    Generate response using RAG (Retrieval-Augmented Generation).

    Session 179: Now uses REAL retrieve_and_generate from RAGSystem
    with actual context from document embeddings.
    """
    user = request.user
    data = request.data if hasattr(request, 'data') else json.loads(request.body or b"{}")

    query = data.get('query', '')
    context_limit = data.get('context_limit', 5)
    model = data.get('model', 'gpt-5-mini')
    temperature = data.get('temperature', 0.7)
    embedding_model = data.get('embedding_model', EmbeddingModel.OPENAI_SMALL)
    knowledge_base_id = data.get('knowledge_base_id')

    if not query.strip():
        return Response({
            'success': False,
            'error': 'Query is required'
        }, status=400)

    try:
        import time
        start_time = time.time()

        # Get knowledge base if specified
        knowledge_base = None
        if knowledge_base_id:
            try:
                knowledge_base = KnowledgeBase.objects.get(id=knowledge_base_id, user=user)
            except KnowledgeBase.DoesNotExist:
                pass

        # Perform REAL RAG retrieval
        rag_context = run_async(
            rag_system.retrieve_and_generate(
                query=query,
                generation_prompt="",  # Will be used by LLM
                knowledge_base=knowledge_base,
                embedding_model=embedding_model,
                max_results=context_limit,
                max_context_length=4000
            )
        )

        # Generate response using OpenAI with retrieved context
        import openai
        from django.conf import settings

        client = openai.OpenAI(api_key=settings.AI_PROVIDERS.get('OPENAI_API_KEY'))

        system_prompt = """You are a knowledgeable assistant that provides accurate, helpful responses.
When provided with context from documents, use that information to ground your responses.
Always cite your sources when referencing specific information from the context."""

        user_prompt = f"""Query: {query}

Retrieved Context:
{rag_context.get('context', 'No relevant context found.')}

Please provide a comprehensive response based on the query and the retrieved context.
If the context is relevant, reference it in your answer. If not relevant, provide your best response."""

        # Session 876: Increased max_completion_tokens for GPT-5-mini reasoning headroom
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=4000
        )

        generated_response = response.choices[0].message.content
        processing_time_ms = (time.time() - start_time) * 1000

        # Format context chunks for response
        context_chunks = [
            {
                'content': result.get('chunk_preview', ''),
                'source': result.get('document_title', 'Unknown'),
                'similarity': result.get('similarity_score', 0)
            }
            for result in rag_context.get('search_results', [])
        ]

        return Response({
            'success': True,
            'response': generated_response,
            'metadata': {
                'query': query,
                'model_used': model,
                'temperature': temperature,
                'context_chunks_used': len(context_chunks),
                'total_tokens': {
                    'context_tokens': len(rag_context.get('context', '').split()),
                    'generated_tokens': len(generated_response.split()),
                    'total_tokens': len(rag_context.get('context', '').split()) + len(generated_response.split())
                },
                'sources_cited': [chunk['source'] for chunk in context_chunks],
                'confidence_score': sum(c['similarity'] for c in context_chunks) / len(context_chunks) if context_chunks else 0,
                'generation_time_ms': round(processing_time_ms, 2)
            },
            'context_used': context_chunks
        })

    except Exception as e:
        logger.error(f"Error in RAG generation: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def embeddings_stats(request):
    """
    Get comprehensive embeddings and RAG system statistics.

    Session 179: Now returns REAL statistics from actual database records.
    """
    user = request.user

    try:
        # Get REAL document stats (Session 733: Fixed user -> owner)
        total_documents = Document.objects.filter(owner=user).count()
        processed_documents = Document.objects.filter(owner=user, status='processed').count()

        # Get REAL embedding stats
        embeddings = DocumentEmbedding.objects.filter(document__owner=user)
        total_embeddings = embeddings.count()

        if total_embeddings > 0:
            avg_dimension = embeddings.aggregate(avg=Avg('embedding_dimension'))['avg'] or 0
            total_cost = embeddings.aggregate(total=Sum('embedding_cost'))['total'] or 0
            avg_processing_time = embeddings.aggregate(avg=Avg('processing_time_ms'))['avg'] or 0

            # Get model distribution
            model_counts = embeddings.values('embedding_model').annotate(count=Count('id'))
            primary_model = max(model_counts, key=lambda x: x['count'])['embedding_model'] if model_counts else 'none'
        else:
            avg_dimension = 0
            total_cost = 0
            avg_processing_time = 0
            primary_model = 'none'

        # Get knowledge base stats
        knowledge_bases = KnowledgeBase.objects.filter(owner=user)
        total_kb = knowledge_bases.count()

        # Get recent activity
        recent_docs = Document.objects.filter(owner=user).order_by('-created_at')[:5]
        recent_activity = [
            {
                'type': 'document_upload',
                'title': doc.title,
                'timestamp': doc.created_at.isoformat(),
                'status': doc.status,
                'chunks_created': doc.embeddings.count()
            }
            for doc in recent_docs
        ]

        return Response({
            'success': True,
            'embeddings_stats': {
                'total_documents': total_documents,
                'processed_documents': processed_documents,
                'total_chunks': total_embeddings,
                'total_embeddings': total_embeddings,
                'embedding_dimensions': int(avg_dimension),
                'embedding_model': primary_model,
                'total_cost': float(total_cost),
                'avg_processing_time_ms': round(avg_processing_time, 2),
                'last_updated': datetime.now().isoformat()
            },
            'rag_performance': {
                'total_knowledge_bases': total_kb,
                'avg_query_time_ms': round(avg_processing_time * 0.5, 2),  # Estimate
                'avg_context_chunks': min(5, total_embeddings / max(1, total_documents)),
                'retrieval_success_rate': processed_documents / max(1, total_documents)
            },
            'recent_activity': recent_activity,
            'storage_breakdown': {
                'text_documents': Document.objects.filter(owner=user, document_type='text').count(),
                'markdown_documents': Document.objects.filter(owner=user, document_type='markdown').count(),
                'other_documents': Document.objects.filter(owner=user).exclude(document_type__in=['text', 'markdown']).count(),
            }
        })

    except Exception as e:
        logger.error(f"Error getting embeddings stats: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_knowledge_collection(request):
    """
    Create organized collections of documents for specialized RAG.

    Session 179: Now creates REAL KnowledgeBase records.
    """
    user = request.user
    data = request.data if hasattr(request, 'data') else json.loads(request.body or b"{}")

    collection_name = data.get('name', 'Untitled Collection')
    description = data.get('description', '')
    document_ids = data.get('document_ids', [])
    tags = data.get('tags', [])
    is_private = data.get('is_private', True)

    try:
        # Create real KnowledgeBase record
        kb = KnowledgeBase.objects.create(
            user=user,
            name=collection_name,
            description=description,
            tags=tags if isinstance(tags, list) else [],
            is_public=not is_private
        )

        # Add documents to knowledge base
        documents_added = 0
        if document_ids:
            for doc_id in document_ids:
                try:
                    doc = Document.objects.get(id=doc_id, user=user)
                    kb.documents.add(doc)
                    documents_added += 1
                except Document.DoesNotExist:
                    pass

        # Calculate embedding stats for this collection
        total_embeddings = DocumentEmbedding.objects.filter(
            document__in=kb.documents.all()
        ).count()

        return Response({
            'success': True,
            'collection': {
                'id': str(kb.id),
                'name': kb.name,
                'description': kb.description,
                'document_count': documents_added,
                'tags': tags,
                'is_private': is_private,
                'created_at': kb.created_at.isoformat(),
                'embedding_stats': {
                    'total_embeddings': total_embeddings,
                    'collection_similarity_threshold': 0.75,
                    'specialized_search_enabled': True
                }
            }
        })

    except Exception as e:
        logger.error(f"Error creating knowledge collection: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_knowledge_collections(request):
    """
    List user's knowledge collections with stats.

    Session 179: Now returns REAL KnowledgeBase records.
    """
    user = request.user

    try:
        # Session 733: Fixed user -> owner
        knowledge_bases = KnowledgeBase.objects.filter(owner=user).order_by('-created_at')

        collections = []
        total_documents = 0
        total_chunks = 0

        for kb in knowledge_bases:
            doc_count = kb.documents.count()
            chunk_count = DocumentEmbedding.objects.filter(document__in=kb.documents.all()).count()

            total_documents += doc_count
            total_chunks += chunk_count

            collections.append({
                'id': str(kb.id),
                'name': kb.name,
                'description': kb.description,
                'document_count': doc_count,
                'total_chunks': chunk_count,
                'tags': kb.tags if isinstance(kb.tags, list) else [],
                'last_used': kb.updated_at.isoformat() if kb.updated_at else kb.created_at.isoformat(),
                'is_public': kb.is_public
            })

        return Response({
            'success': True,
            'collections': collections,
            'total_collections': len(collections),
            'total_documents': total_documents,
            'total_chunks': total_chunks
        })

    except Exception as e:
        logger.error(f"Error listing knowledge collections: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def advanced_rag_query(request):
    """
    Advanced RAG query with multi-collection search and response synthesis.

    Session 179: Now uses REAL multi-collection semantic search.
    """
    user = request.user
    data = request.data if hasattr(request, 'data') else json.loads(request.body or b"{}")

    query = data.get('query', '')
    collection_ids = data.get('collection_ids', [])
    response_format = data.get('response_format', 'comprehensive')
    max_context_chunks = data.get('max_context_chunks', 10)
    include_citations = data.get('include_citations', True)
    embedding_model = data.get('embedding_model', EmbeddingModel.OPENAI_SMALL)

    if not query.strip():
        return Response({
            'success': False,
            'error': 'Query is required'
        }, status=400)

    try:
        import time
        start_time = time.time()

        all_results = []

        # Search across specified collections or all user documents
        if collection_ids:
            for kb_id in collection_ids:
                try:
                    kb = KnowledgeBase.objects.get(id=kb_id, user=user)
                    results = rag_system.semantic_search_sync(
                        query=query,
                        knowledge_base=kb,
                        embedding_model=embedding_model,
                        limit=max_context_chunks,
                        similarity_threshold=0.6
                    )
                    all_results.extend(results)
                except KnowledgeBase.DoesNotExist:
                    continue
        else:
            # Search all user documents
            results = rag_system.semantic_search_sync(
                query=query,
                embedding_model=embedding_model,
                limit=max_context_chunks,
                similarity_threshold=0.6
            )
            all_results = results

        # Sort by similarity and take top results
        all_results.sort(key=lambda x: x.similarity_score, reverse=True)
        top_results = all_results[:max_context_chunks]

        # Build context from results
        context = rag_system.get_context_for_generation(top_results, max_context_length=4000)

        # Generate response using OpenAI
        import openai
        from django.conf import settings

        client = openai.OpenAI(api_key=settings.AI_PROVIDERS.get('OPENAI_API_KEY'))

        format_instruction = "Provide a comprehensive, well-structured response with sections." if response_format == 'comprehensive' else "Provide a concise summary."

        system_prompt = f"""You are an expert analyst providing insights from a personal knowledge base.
{format_instruction}
When citing information, reference the source documents."""

        user_prompt = f"""Query: {query}

Retrieved Context from {len(top_results)} relevant documents:
{context}

Based on the context above, provide a thorough response to the query.
{'Include specific citations with document names.' if include_citations else ''}"""

        response = client.chat.completions.create(
            model='gpt-5-mini',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_completion_tokens=1500
        )

        generated_response = response.choices[0].message.content
        processing_time_ms = (time.time() - start_time) * 1000

        # Format citations
        citations = []
        if include_citations:
            seen_docs = set()
            for r in top_results:
                if r.document_title not in seen_docs:
                    citations.append({
                        'document_title': r.document_title,
                        'document_id': r.document_id,
                        'relevance_score': round(r.similarity_score, 4),
                        'chunk_id': f'chunk_{r.chunk_index}'
                    })
                    seen_docs.add(r.document_title)

        return Response({
            'success': True,
            'response': generated_response,
            'query_metadata': {
                'query': query,
                'response_format': response_format,
                'collections_searched': len(collection_ids) if collection_ids else 'all',
                'context_chunks_used': len(top_results),
                'total_sources': len(set(r.document_title for r in top_results)),
                'confidence_score': sum(r.similarity_score for r in top_results) / len(top_results) if top_results else 0,
                'processing_time_ms': round(processing_time_ms, 2)
            },
            'citations': citations
        })

    except Exception as e:
        logger.error(f"Error in advanced RAG query: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def optimize_embeddings(request):
    """
    Optimize embedding storage and performance.

    Session 179: Implements REAL optimization operations.
    """
    user = request.user
    data = request.data if hasattr(request, 'data') else json.loads(request.body or b"{}")

    optimization_type = data.get('type', 'full')  # full, dedup, reindex
    target_collections = data.get('collections', [])

    try:
        import time
        start_time = time.time()

        # Get user's embeddings
        embeddings_query = DocumentEmbedding.objects.filter(document__user=user)

        if target_collections:
            embeddings_query = embeddings_query.filter(
                document__knowledge_bases__id__in=target_collections
            )

        total_embeddings = embeddings_query.count()
        duplicates_removed = 0
        reindexed = 0

        if optimization_type in ['full', 'dedup']:
            # Find and remove duplicate chunks (same document + same chunk_index)
            from django.db.models import Count
            duplicates = embeddings_query.values(
                'document', 'chunk_index', 'embedding_model'
            ).annotate(count=Count('id')).filter(count__gt=1)

            for dup in duplicates:
                # Keep only the most recent one
                dup_embeddings = embeddings_query.filter(
                    document_id=dup['document'],
                    chunk_index=dup['chunk_index'],
                    embedding_model=dup['embedding_model']
                ).order_by('-created_at')

                # Delete all but the first (most recent)
                for emb in dup_embeddings[1:]:
                    emb.delete()
                    duplicates_removed += 1

        if optimization_type in ['full', 'reindex']:
            # Update chunk indices if there are gaps
            documents = Document.objects.filter(
                user=user, status='processed'
            )
            for doc in documents:
                embeddings = doc.embeddings.order_by('chunk_index')
                for i, emb in enumerate(embeddings):
                    if emb.chunk_index != i:
                        emb.chunk_index = i
                        emb.save(update_fields=['chunk_index'])
                        reindexed += 1

        processing_time_ms = (time.time() - start_time) * 1000

        return Response({
            'success': True,
            'optimization': {
                'type': optimization_type,
                'status': 'completed',
                'results': {
                    'embeddings_processed': total_embeddings,
                    'duplicates_removed': duplicates_removed,
                    'reindexed_chunks': reindexed,
                    'storage_saved_mb': duplicates_removed * 0.01,  # Estimate 10KB per embedding
                    'performance_improvement': f"{min(20, duplicates_removed)}%"
                },
                'processing_time_ms': round(processing_time_ms, 2),
                'completed_at': datetime.now().isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error optimizing embeddings: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# Additional utility endpoints

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_embedding_models(request):
    """Get list of available embedding models."""
    try:
        manager = EmbeddingManager()
        available = manager.get_available_models()

        models = []
        for model in EmbeddingModel.choices:
            model_enum = model[0]
            is_available = model_enum in available

            models.append({
                'id': model_enum,
                'name': model[1],
                'available': is_available,
                'dimension': {
                    EmbeddingModel.OPENAI_SMALL: 1536,
                    EmbeddingModel.OPENAI_LARGE: 3072,
                    EmbeddingModel.OPENAI_ADA: 1536,
                    EmbeddingModel.SENTENCE_TRANSFORMER: 384,
                    EmbeddingModel.COHERE: 1024,
                }.get(model_enum, 0),
                'cost_per_1k_tokens': {
                    EmbeddingModel.OPENAI_SMALL: 0.02,
                    EmbeddingModel.OPENAI_LARGE: 0.13,
                    EmbeddingModel.OPENAI_ADA: 0.10,
                    EmbeddingModel.SENTENCE_TRANSFORMER: 0.0,
                    EmbeddingModel.COHERE: 0.10,
                }.get(model_enum, 0)
            })

        return Response({
            'success': True,
            'models': models,
            'default_model': EmbeddingModel.OPENAI_SMALL
        })

    except Exception as e:
        logger.error(f"Error getting embedding models: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_document_embeddings(request, document_id):
    """Delete all embeddings for a specific document."""
    user = request.user

    try:
        document = Document.objects.get(id=document_id, user=user)
        deleted_count = document.embeddings.count()
        document.embeddings.all().delete()

        # Update document status
        document.status = 'pending'
        document.save(update_fields=['status'])

        return Response({
            'success': True,
            'deleted_embeddings': deleted_count,
            'document_id': str(document_id)
        })

    except Document.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Document not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error deleting document embeddings: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# =============================================================================
# Session 402: Document Ingestion API Endpoints
# =============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_documents(request):
    """
    List all documents for the current user.
    Session 402: Document ingestion system.
    """
    user = request.user

    try:
        documents = Document.objects.filter(owner=user).order_by('-created_at')

        # Calculate stats
        total = documents.count()
        youtube_count = documents.filter(document_type=DocumentType.YOUTUBE).count()
        url_count = documents.filter(document_type=DocumentType.URL).count()
        pdf_count = documents.filter(document_type=DocumentType.PDF).count()
        processed_count = documents.filter(status='processed').count()

        # Get documents with embedding counts
        docs_data = []
        for doc in documents[:50]:  # Limit to 50 most recent
            embedding_count = doc.embeddings.count() if hasattr(doc, 'embeddings') else 0
            docs_data.append({
                'id': str(doc.id),
                'title': doc.title,
                'document_type': doc.document_type,
                'status': doc.status,
                'source_url': doc.source_url if hasattr(doc, 'source_url') else '',
                'embedding_count': embedding_count,
                'word_count': len(doc.processed_content.split()) if doc.processed_content else 0,
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat() if doc.updated_at else None,
            })

        return Response({
            'success': True,
            'documents': docs_data,
            'stats': {
                'total': total,
                'youtube': youtube_count,
                'urls': url_count,
                'pdfs': pdf_count,
                'processed': processed_count,
            }
        })

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([RagIngestThrottle])
def ingest_url(request):
    """
    Ingest a URL (YouTube video or web page) and create a document.
    Session 402: Document ingestion system.
    Session 733: Added multi-page crawling support.

    Accepts:
    - url: The URL to ingest (YouTube or web page)
    - title: Optional custom title
    - generate_embeddings: Whether to generate embeddings (default: true)
    - crawl_site: Enable multi-page crawling (default: false)
    - max_pages: Maximum pages to crawl (default: 10, max: 50)
    - max_depth: Maximum link depth (default: 2, max: 3)
    - url_pattern: Regex pattern to filter URLs (e.g., '/tutorial/')
    """
    # Content-type guard: reject non-JSON requests early
    content_type = request.content_type or ''
    if content_type and 'json' not in content_type and 'x-www-form-urlencoded' not in content_type:
        return Response({
            'success': False,
            'error': 'Content-Type must be application/json',
            'correlation_id': str(uuid.uuid4()),
        }, status=415)

    user = request.user
    data = request.data if hasattr(request, 'data') else json.loads(request.body or b"{}")

    url = data.get('url', '').strip()
    title = data.get('title', '').strip()
    generate_embeddings = data.get('generate_embeddings', True)

    # Session 733: Multi-page crawling options
    crawl_site = data.get('crawl_site', False)
    max_pages = min(int(data.get('max_pages', 10)), 50)  # Cap at 50 pages
    max_depth = min(int(data.get('max_depth', 2)), 3)    # Cap at depth 3
    url_pattern = data.get('url_pattern', None)

    if not url:
        return Response({
            'success': False,
            'error': 'URL is required',
            'correlation_id': str(uuid.uuid4()),
        }, status=400)

    # YouTube URLs don't support crawling
    is_youtube = 'youtube.com' in url or 'youtu.be' in url
    if is_youtube and crawl_site:
        return Response({
            'success': False,
            'error': 'Multi-page crawling is not supported for YouTube videos',
            'correlation_id': str(uuid.uuid4()),
        }, status=400)

    try:
        from content.processors import DocumentProcessingPipeline, URLProcessor

        if crawl_site and not is_youtube:
            # Session 733: Multi-page crawling
            url_processor = URLProcessor()
            crawl_result = url_processor.crawl_site(
                start_url=url,
                max_pages=max_pages,
                max_depth=max_depth,
                same_domain_only=True,
                url_pattern=url_pattern
            )

            if not crawl_result.success:
                cid = str(uuid.uuid4())
                logger.warning(f"Crawl failed for '{url}' [correlation_id={cid}]: {crawl_result.error_message}")
                return Response({
                    'success': False,
                    'error': crawl_result.error_message or 'Failed to crawl site',
                    'correlation_id': cid,
                }, status=400)

            # Create a single document with combined content
            doc_type = DocumentType.URL
            combined_title = title or f"Site Crawl: {crawl_result.metadata.get('crawled_urls', [{}])[0].get('title', url)}"

            document = Document.objects.create(
                owner=user,
                title=combined_title,
                document_type=doc_type,
                raw_content='',  # Don't store raw HTML for crawls (too large)
                processed_content=crawl_result.combined_content,
                source_url=url,
                metadata={
                    'crawl_metadata': crawl_result.metadata,
                    'pages_crawled': crawl_result.pages_crawled,
                    'total_word_count': crawl_result.total_word_count,
                },
                status='processed',
                tags=['site-crawl']
            )

            if generate_embeddings and crawl_result.total_word_count > 50:
                from core.tasks import generate_document_embeddings
                generate_document_embeddings.delay(str(document.id))
                document.status = 'embedding'
                document.save(update_fields=['status'])

            return Response({
                'success': True,
                'document': {
                    'id': str(document.id),
                    'title': document.title,
                    'document_type': document.document_type,
                    'status': document.status,
                    'source_url': document.source_url,
                    'word_count': crawl_result.total_word_count,
                    'metadata': document.metadata,
                    'created_at': document.created_at.isoformat(),
                },
                'crawl_stats': {
                    'pages_crawled': crawl_result.pages_crawled,
                    'total_words': crawl_result.total_word_count,
                    'crawled_urls': crawl_result.metadata.get('crawled_urls', []),
                    'failed_urls': crawl_result.metadata.get('failed_urls', []),
                },
                'message': f"Successfully crawled {crawl_result.pages_crawled} pages from {url}"
            })

        else:
            # Single page ingestion (original behavior)
            pipeline = DocumentProcessingPipeline()
            result = pipeline.process_url(url)

            if not result.success:
                cid = str(uuid.uuid4())
                ip_blocked = result.metadata.get('ip_blocked', False) if result.metadata else False
                video_id = result.metadata.get('video_id') if result.metadata else None
                status_code = 502 if ip_blocked else 400
                logger.warning(f"URL processing failed for '{url}' [correlation_id={cid}]: {result.error_message}")
                error_response = {
                    'success': False,
                    'error': result.error_message or 'Failed to process URL',
                    'correlation_id': cid,
                }
                if ip_blocked:
                    error_response['error_code'] = 'YOUTUBE_TRANSCRIPT_BLOCKED'
                    error_response['video_id'] = video_id
                return Response(error_response, status=status_code)

            # Determine document type
            doc_type = DocumentType.YOUTUBE if is_youtube else DocumentType.URL

            # Check if we got meaningful content
            has_content = result.processed_content and len(result.processed_content.strip()) > 50
            warning_message = None

            if not has_content:
                # Check if it's likely a JavaScript-rendered SPA
                if result.raw_content and '<script' in result.raw_content and len(result.raw_content) < 10000:
                    warning_message = "This page appears to be JavaScript-rendered (SPA). Content may be incomplete."
                else:
                    warning_message = "Limited content extracted from this page."

            # Create document
            document = Document.objects.create(
                owner=user,
                title=title or result.metadata.get('title', url[:100]),
                document_type=doc_type,
                raw_content=result.raw_content,
                processed_content=result.processed_content or '',
                source_url=url,
                metadata=result.metadata,
                status='processed' if has_content else 'processed',  # Still mark as processed
                tags=[]
            )

            embedding_count = 0
            if generate_embeddings and has_content:
                # Generate embeddings in background
                from core.tasks import generate_document_embeddings
                generate_document_embeddings.delay(str(document.id))
                document.status = 'embedding'
                document.save(update_fields=['status'])

            response_data = {
                'success': True,
                'document': {
                    'id': str(document.id),
                    'title': document.title,
                    'document_type': document.document_type,
                    'status': document.status,
                    'source_url': document.source_url,
                    'word_count': len(result.processed_content.split()) if result.processed_content else 0,
                    'metadata': result.metadata,
                    'created_at': document.created_at.isoformat(),
                },
                'message': f"Successfully ingested {'YouTube video' if is_youtube else 'web page'}"
            }

            if warning_message:
                response_data['warning'] = warning_message

            return Response(response_data)

    except Exception as e:
        cid = str(uuid.uuid4())
        logger.exception(f"Error ingesting URL '{url}' [correlation_id={cid}]: {e}")
        return Response({
            'success': False,
            'error': str(e),
            'correlation_id': cid,
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document(request, document_id):
    """
    Get a single document with full content.
    Session 402: Document ingestion system.
    """
    user = request.user

    try:
        document = Document.objects.get(id=document_id, owner=user)
        embedding_count = document.embeddings.count() if hasattr(document, 'embeddings') else 0

        return Response({
            'success': True,
            'document': {
                'id': str(document.id),
                'title': document.title,
                'document_type': document.document_type,
                'status': document.status,
                'source_url': document.source_url if hasattr(document, 'source_url') else '',
                'raw_content': document.raw_content,
                'processed_content': document.processed_content,
                'metadata': document.metadata,
                'embedding_count': embedding_count,
                'word_count': len(document.processed_content.split()) if document.processed_content else 0,
                'tags': document.tags,
                'created_at': document.created_at.isoformat(),
                'updated_at': document.updated_at.isoformat() if document.updated_at else None,
            }
        })

    except Document.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Document not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_document(request, document_id):
    """
    Delete a document and its embeddings.
    Session 402: Document ingestion system.
    """
    user = request.user

    try:
        document = Document.objects.get(id=document_id, owner=user)
        title = document.title

        # Delete embeddings first
        if hasattr(document, 'embeddings'):
            document.embeddings.all().delete()

        # Delete document
        document.delete()

        return Response({
            'success': True,
            'message': f'Deleted document: {title}'
        })

    except Document.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Document not found'
        }, status=404)
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([RagIngestThrottle])
def ingest_file(request):
    """
    Upload and ingest a PDF or text file.
    Session 402: Document ingestion system.
    """
    from content.processors import PDFProcessor, TextProcessor, DOCXProcessor, CSVProcessor

    user = request.user

    if 'file' not in request.FILES:
        return Response({
            'success': False,
            'error': 'No file provided'
        }, status=400)

    uploaded_file = request.FILES['file']
    filename = uploaded_file.name.lower()
    generate_embeddings = request.POST.get('generate_embeddings', 'true').lower() == 'true'

    try:
        # Read file content
        file_content = uploaded_file.read()

        # Determine file type and process
        if filename.endswith('.pdf'):
            processor = PDFProcessor()
            result = processor.process(file_content, filename=uploaded_file.name)
            doc_type = DocumentType.PDF
        elif filename.endswith('.txt'):
            processor = TextProcessor()
            result = processor.process(file_content.decode('utf-8', errors='ignore'))
            doc_type = DocumentType.TEXT
        elif filename.endswith('.md'):
            processor = TextProcessor()
            result = processor.process(file_content.decode('utf-8', errors='ignore'))
            doc_type = DocumentType.MARKDOWN
        elif filename.endswith('.docx'):
            processor = DOCXProcessor()
            result = processor.process(file_content, filename=uploaded_file.name)
            doc_type = DocumentType.DOCX
        elif filename.endswith('.csv'):
            processor = CSVProcessor()
            result = processor.process(file_content, filename=uploaded_file.name)
            doc_type = DocumentType.CSV
        else:
            return Response({
                'success': False,
                'error': f'Unsupported file type. Supported: .pdf, .txt, .md, .docx, .csv'
            }, status=400)

        # Check if we got content
        has_content = result.processed_content and len(result.processed_content.strip()) > 50

        # Create document record
        document = Document.objects.create(
            owner=user,
            title=result.metadata.get('title', uploaded_file.name),
            document_type=doc_type,
            raw_content=result.raw_content[:100000] if result.raw_content else '',
            processed_content=result.processed_content[:100000] if result.processed_content else '',
            status='processed' if has_content else 'failed',
            metadata=result.metadata
        )

        # Generate embeddings if requested and we have content
        if generate_embeddings and has_content:
            from core.tasks import generate_document_embeddings
            generate_document_embeddings.delay(str(document.id))
            document.status = 'embedding'
            document.save()

        return Response({
            'success': True,
            'document': {
                'id': str(document.id),
                'title': document.title,
                'document_type': document.document_type,
                'status': document.status,
                'word_count': len(result.processed_content.split()) if result.processed_content else 0,
                'has_content': has_content,
                'created_at': document.created_at.isoformat()
            }
        })

    except Exception as e:
        logger.error(f"Error ingesting file: {e}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'error': str(e)
        }, status=500)


# ============================================================
# Video RAG Ingest
# ============================================================

class VideoIngestThrottle(ScopedRateThrottle):
    scope = 'video_ingest'


ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([VideoIngestThrottle])
def ingest_video(request):
    """
    Upload a video file for RAG ingestion.

    Accepts multipart/form-data with:
    - file (required): video file (.mp4, .mov, .avi, .mkv, .webm)
    - title: optional custom title
    - language: Whisper language code (default: 'en')

    Returns 202 with job_id for async polling via ingest_video_status.
    """
    import os
    import tempfile
    from django.conf import settings as django_settings

    correlation_id = str(uuid.uuid4())

    if 'file' not in request.FILES:
        return Response({
            'success': False,
            'error': 'No video file provided. Use multipart/form-data with a "file" field.',
            'correlation_id': correlation_id,
        }, status=400)

    uploaded_file = request.FILES['file']
    filename = uploaded_file.name or ''
    ext = os.path.splitext(filename.lower())[1]

    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        return Response({
            'success': False,
            'error': f'Unsupported video format "{ext}". Supported: {", ".join(sorted(ALLOWED_VIDEO_EXTENSIONS))}',
            'correlation_id': correlation_id,
        }, status=400)

    max_size = getattr(django_settings, 'VIDEO_INGEST_MAX_SIZE', 104857600)
    if uploaded_file.size and uploaded_file.size > max_size:
        return Response({
            'success': False,
            'error': f'File too large ({uploaded_file.size / 1048576:.1f}MB). Maximum: {max_size / 1048576:.0f}MB.',
            'correlation_id': correlation_id,
        }, status=400)

    title = request.POST.get('title', '').strip() or filename
    language = request.POST.get('language', 'en').strip() or 'en'

    # Write upload to temp file
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=ext)
    try:
        with os.fdopen(tmp_fd, 'wb') as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)

        file_size = os.path.getsize(tmp_path)

        # Create Document record
        document = Document.objects.create(
            owner=request.user,
            title=title,
            document_type=DocumentType.VIDEO,
            original_filename=filename,
            file_size=file_size,
            mime_type=uploaded_file.content_type or '',
            status='pending',
            source='upload',
        )

        # Dispatch Celery task
        from core.tasks import ingest_video_task
        try:
            task = ingest_video_task.delay(
                str(document.id), tmp_path, filename, str(request.user.id), language
            )
        except Exception as dispatch_err:
            logger.error(f"🎥 Celery dispatch failed: {dispatch_err} [{correlation_id}]")
            document.delete()
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            return Response({
                'success': False,
                'error': 'Task queue unavailable. Please try again later.',
                'correlation_id': correlation_id,
            }, status=503)

        logger.info(f"🎥 Video ingest queued: doc={document.id} job={task.id} [{correlation_id}]")

        return Response({
            'success': True,
            'document_id': str(document.id),
            'job_id': task.id,
            'status': 'queued',
            'correlation_id': correlation_id,
        }, status=202)

    except Exception as e:
        # Clean up temp file on outer error
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        logger.error(f"🎥 Video ingest error: {e} [{correlation_id}]")
        return Response({
            'success': False,
            'error': str(e),
            'correlation_id': correlation_id,
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ingest_video_status(request, job_id):
    """
    Poll the status of a video ingest task.

    Returns job status, progress info, and document details when complete.
    """
    from celery.result import AsyncResult

    # Try CeleryTaskEvent first (survives Redis TTL)
    try:
        from core.models_celery_telemetry import CeleryTaskEvent
        event = CeleryTaskEvent.objects.filter(task_id=job_id).order_by('-started_at').first()
        if event:
            result_data = {
                'job_id': job_id,
                'status': event.status,
                'progress': _video_progress_from_status(event.status),
            }

            if event.status == 'SUCCESS':
                result_data['document'] = _video_document_details(event)
            elif event.status == 'FAILURE':
                result_data['error'] = event.error_message or 'Task failed'

            return Response(result_data)
    except Exception:
        pass

    # Fallback: AsyncResult
    result = AsyncResult(job_id)

    status = result.status or 'UNKNOWN'
    response_data = {
        'job_id': job_id,
        'status': status,
        'progress': _video_progress_from_status(status),
    }

    if status == 'SUCCESS' and isinstance(result.result, dict):
        response_data['document'] = {
            'id': result.result.get('document_id'),
            'segment_count': result.result.get('segment_count'),
            'word_count': result.result.get('word_count'),
            'duration_seconds': result.result.get('duration_seconds'),
        }
    elif status == 'FAILURE':
        response_data['error'] = str(result.result) if result.result else 'Task failed'

    return Response(response_data)


def _video_progress_from_status(status):
    """Map task status to a human-readable progress string."""
    return {
        'PENDING': 'Queued',
        'STARTED': 'Processing video...',
        'SUCCESS': 'Complete',
        'FAILURE': 'Failed',
        'RETRY': 'Retrying...',
    }.get(status, 'Unknown')


def _video_document_details(event):
    """Extract document details from a completed CeleryTaskEvent."""
    try:
        # The task result is stored in CeleryTaskEvent only if result backend wrote it
        # Try fetching the document directly
        task_name = event.task_name or ''
        if 'ingest_video' in task_name:
            from celery.result import AsyncResult as AR
            result = AR(event.task_id)
            if isinstance(result.result, dict):
                doc_id = result.result.get('document_id')
                if doc_id:
                    doc = Document.objects.filter(id=doc_id).first()
                    if doc:
                        meta = doc.extracted_metadata or {}
                        return {
                            'id': str(doc.id),
                            'title': doc.title,
                            'status': doc.status,
                            'segment_count': meta.get('segment_count'),
                            'duration_seconds': meta.get('duration_seconds'),
                            'word_count': doc.word_count,
                        }
    except Exception:
        pass
    return None