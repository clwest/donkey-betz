"""
Integration layer between Content models and Data Persistence infrastructure.

This module provides seamless integration between existing content models
and the new unified embedding and persistence system.
"""

import logging
from typing import List, Dict, Optional, Any
from django.db import transaction
from django.utils import timezone

from content.models import Document, DocumentEmbedding, ContentGeneration
from .models import UnifiedEmbedding
from .services import EmbeddingService

logger = logging.getLogger(__name__)


class DocumentPersistenceIntegration:
    """
    Integration service for connecting Document models with unified embeddings.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def create_document_embeddings(self, document: Document, chunk_size: int = 1000,
                                 chunk_overlap: int = 200) -> List[UnifiedEmbedding]:
        """
        Create unified embeddings for a document with chunking.

        Args:
            document: Document instance to create embeddings for
            chunk_size: Size of each text chunk
            chunk_overlap: Overlap between chunks

        Returns:
            List of created UnifiedEmbedding instances
        """
        try:
            content = document.get_content()
            if not content:
                logger.warning(f"No content found for document {document.id}")
                return []

            # Split content into chunks
            chunks = self._split_text_into_chunks(content, chunk_size, chunk_overlap)

            embeddings = []
            for i, chunk in enumerate(chunks):
                try:
                    # Create unified embedding
                    embedding = self.embedding_service.create_embedding(
                        content_text=chunk,
                        content_type='document_chunk',
                        content_id=document.id,
                        content_title=f"{document.title} - Chunk {i+1}",
                        source_system='content',
                        creator_user=document.owner,
                        metadata={
                            'document_id': str(document.id),
                            'document_type': document.document_type,
                            'chunk_index': i,
                            'chunk_count': len(chunks),
                            'file_path': document.file_path,
                            'category': document.category,
                        },
                        tags=document.tags,
                        category=document.category,
                        importance_score=0.7,  # Documents are generally important
                        relevance_score=0.8,
                        confidence_score=0.9,
                    )
                    embeddings.append(embedding)

                    # Also create legacy DocumentEmbedding for backward compatibility
                    self._create_legacy_embedding(document, chunk, i, embedding)

                except Exception as e:
                    logger.error(f"Failed to create embedding for chunk {i} of document {document.id}: {e}")
                    continue

            logger.info(f"Created {len(embeddings)} embeddings for document {document.id}")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to create embeddings for document {document.id}: {e}")
            return []

    def _split_text_into_chunks(self, text: str, chunk_size: int,
                               overlap: int) -> List[str]:
        """Split text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundaries
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                search_start = max(start + chunk_size - 100, start)
                search_end = min(end + 100, len(text))
                search_text = text[search_start:search_end]

                sentence_endings = ['.', '!', '?', '\n\n']
                best_break = -1

                for ending in sentence_endings:
                    pos = search_text.rfind(ending)
                    if pos > best_break and pos > chunk_size - 200:
                        best_break = pos

                if best_break > -1:
                    end = search_start + best_break + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Calculate next start position with overlap
            start = max(start + chunk_size - overlap, end)

        return chunks

    def _create_legacy_embedding(self, document: Document, chunk_text: str,
                                chunk_index: int, unified_embedding: UnifiedEmbedding):
        """Create legacy DocumentEmbedding for backward compatibility."""
        try:
            # Check if DocumentEmbedding already exists
            existing = DocumentEmbedding.objects.filter(
                document=document,
                chunk_index=chunk_index
            ).first()

            if existing:
                # Update existing
                existing.chunk_text = chunk_text
                existing.embedding_vector = unified_embedding.embedding
                existing.save()
            else:
                # Create new
                from content.embeddings import _derive_source_type
                DocumentEmbedding.objects.create(
                    document=document,
                    embedding_model=unified_embedding.embedding_model,
                    chunk_index=chunk_index,
                    chunk_text=chunk_text,
                    chunk_size=len(chunk_text),
                    overlap_size=0,  # Will be calculated if needed
                    embedding_vector=unified_embedding.embedding,
                    embedding_dimension=unified_embedding.embedding_dimension,
                    processing_time_ms=unified_embedding.generation_time_ms,
                    embedding_cost=unified_embedding.generation_cost,
                    source_type=_derive_source_type(document),
                    ingested_via='unknown',
                )

        except Exception as e:
            logger.error(f"Failed to create legacy embedding: {e}")

    def search_documents(self, query: str, document_types: List[str] = None,
                        categories: List[str] = None, limit: int = 20) -> List[Dict]:
        """
        Search documents using unified embedding system.

        Args:
            query: Search query
            document_types: Filter by document types
            categories: Filter by categories
            limit: Maximum number of results

        Returns:
            List of search results with document information
        """
        try:
            # Build filters
            filters = {'source_system': 'content'}
            if document_types:
                filters['metadata__document_type__in'] = document_types
            if categories:
                filters['category__in'] = categories

            # Search using unified system
            results = self.embedding_service.search_all_content(
                query=query,
                content_types=['document_chunk'],
                limit=limit,
                filters=filters
            )

            # Enrich results with document information
            enriched_results = []
            for result in results:
                try:
                    document_id = result['metadata'].get('document_id')
                    if document_id:
                        document = Document.objects.get(id=document_id)
                        result['document'] = {
                            'id': str(document.id),
                            'title': document.title,
                            'file_path': document.file_path,
                            'document_type': document.document_type,
                            'owner': document.owner.username,
                            'created_at': document.created_at.isoformat(),
                            'view_count': document.view_count,
                            'is_public': document.is_public,
                        }
                        enriched_results.append(result)
                except Document.DoesNotExist:
                    logger.warning(f"Document {document_id} not found for search result")
                    continue

            return enriched_results

        except Exception as e:
            logger.error(f"Document search failed: {e}")
            return []

    def migrate_existing_documents(self, batch_size: int = 10) -> Dict[str, int]:
        """
        Migrate existing documents to the unified embedding system.

        Args:
            batch_size: Number of documents to process in each batch

        Returns:
            Dictionary with migration statistics
        """
        stats = {
            'processed': 0,
            'succeeded': 0,
            'failed': 0,
            'skipped': 0
        }

        try:
            # Get documents that don't have unified embeddings yet
            documents_to_migrate = Document.objects.filter(
                status='processed',
                is_active=True
            ).exclude(
                id__in=UnifiedEmbedding.objects.filter(
                    content_type='document_chunk',
                    source_system='content'
                ).values_list('content_id', flat=True)
            )

            total_documents = documents_to_migrate.count()
            logger.info(f"Starting migration of {total_documents} documents")

            # Process in batches
            for i in range(0, total_documents, batch_size):
                batch = documents_to_migrate[i:i + batch_size]

                for document in batch:
                    stats['processed'] += 1

                    try:
                        # Skip if document has no content
                        if not document.get_content():
                            stats['skipped'] += 1
                            continue

                        # Create embeddings
                        embeddings = self.create_document_embeddings(document)

                        if embeddings:
                            stats['succeeded'] += 1
                            logger.info(f"Migrated document {document.id}: {document.title}")
                        else:
                            stats['failed'] += 1

                    except Exception as e:
                        stats['failed'] += 1
                        logger.error(f"Failed to migrate document {document.id}: {e}")

                logger.info(f"Migrated batch {i//batch_size + 1}/{(total_documents + batch_size - 1)//batch_size}")

            logger.info(f"Migration completed: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Document migration failed: {e}")
            return stats


class ContentGenerationIntegration:
    """
    Integration service for ContentGeneration with unified embeddings.
    """

    def __init__(self):
        self.embedding_service = EmbeddingService()

    def create_generation_embedding(self, generation: ContentGeneration) -> Optional[UnifiedEmbedding]:
        """
        Create unified embedding for generated content.

        Args:
            generation: ContentGeneration instance

        Returns:
            UnifiedEmbedding instance if successful
        """
        try:
            if not generation.generated_content:
                return None

            # Combine prompt and generated content for embedding
            combined_content = f"PROMPT: {generation.prompt}\n\nGENERATED CONTENT: {generation.generated_content}"

            embedding = self.embedding_service.create_embedding(
                content_text=combined_content,
                content_type='generated_content',
                content_id=generation.id,
                content_title=f"Generated Content {generation.id}",
                source_system='content',
                creator_user=generation.user,
                metadata={
                    'generation_id': str(generation.id),
                    'template_id': str(generation.template.id) if generation.template else None,
                    'source_system': generation.source_system,
                    'token_usage': generation.token_usage,
                    'generation_cost': float(generation.generation_cost),
                    'quality_score': generation.quality_score,
                    'user_rating': generation.user_rating,
                },
                importance_score=0.6,
                relevance_score=generation.quality_score or 0.5,
                confidence_score=0.8,
            )

            logger.info(f"Created embedding for content generation {generation.id}")
            return embedding

        except Exception as e:
            logger.error(f"Failed to create embedding for generation {generation.id}: {e}")
            return None

    def search_generated_content(self, query: str, templates: List[str] = None,
                                limit: int = 20) -> List[Dict]:
        """
        Search generated content using unified embedding system.

        Args:
            query: Search query
            templates: Filter by template names
            limit: Maximum number of results

        Returns:
            List of search results with generation information
        """
        try:
            # Build filters
            filters = {'source_system': 'content'}
            if templates:
                filters['metadata__template_id__in'] = templates

            # Search using unified system
            results = self.embedding_service.search_all_content(
                query=query,
                content_types=['generated_content'],
                limit=limit,
                filters=filters
            )

            # Enrich results with generation information
            enriched_results = []
            for result in results:
                try:
                    generation_id = result['metadata'].get('generation_id')
                    if generation_id:
                        generation = ContentGeneration.objects.get(id=generation_id)
                        result['generation'] = {
                            'id': str(generation.id),
                            'prompt': generation.prompt[:200] + '...' if len(generation.prompt) > 200 else generation.prompt,
                            'template': generation.template.name if generation.template else 'Custom',
                            'user': generation.user.username,
                            'created_at': generation.created_at.isoformat(),
                            'status': generation.status,
                            'quality_score': generation.quality_score,
                            'user_rating': generation.user_rating,
                        }
                        enriched_results.append(result)
                except ContentGeneration.DoesNotExist:
                    logger.warning(f"ContentGeneration {generation_id} not found for search result")
                    continue

            return enriched_results

        except Exception as e:
            logger.error(f"Generated content search failed: {e}")
            return []


# Export integration services
document_persistence = DocumentPersistenceIntegration()
content_generation_integration = ContentGenerationIntegration()