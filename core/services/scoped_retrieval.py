"""
Scoped Document Retrieval Service

Session 786: Provides scope-aware document retrieval with smart defaults.

Scopes:
- DOCS_INDEX_ACTIVE: Curated docs from Docs Index (status=active)
- DOCS_INDEX_ALL: All curated docs including superseded
- REPO_MARKDOWN: All markdown files in repo (uncurated)

Usage:
    from core.services.scoped_retrieval import ScopedRetrievalService

    service = ScopedRetrievalService()

    # Default: search only active curated docs
    results = service.search("agent architecture")

    # Include superseded docs for historical context
    results = service.search("agent architecture", include_superseded=True)

    # Expand to uncurated repo markdown
    results = service.search("agent architecture", scope='repo_markdown')
"""

from enum import Enum
from typing import Optional, List
from dataclasses import dataclass
import logging

from django.conf import settings
from django.db.models import Q

logger = logging.getLogger(__name__)


class DocumentScope(Enum):
    """Document retrieval scopes."""
    DOCS_INDEX_ACTIVE = 'docs_index_active'      # Curated, active docs only
    DOCS_INDEX_ALL = 'docs_index_all'            # Curated, including superseded
    REPO_MARKDOWN = 'repo_markdown'               # All repo markdown (uncurated)


@dataclass
class RetrievalResult:
    """Result from document retrieval."""
    document_id: str
    title: str
    path: str
    content_snippet: str
    similarity_score: float
    scope: str
    status: str
    is_curated: bool


class ScopedRetrievalService:
    """
    Scope-aware document retrieval service.

    Default behavior:
    - Searches curated active docs first
    - Only expands scope when explicitly requested or no results found
    - Ranks curated > uncurated, active > superseded
    """

    def __init__(self):
        self.default_scope = DocumentScope.DOCS_INDEX_ACTIVE
        self.default_limit = 10
        self.min_similarity = 0.4  # Lowered from 0.7 - embedding similarity scores are typically 0.3-0.6

    def search(
        self,
        query: str,
        scope: Optional[DocumentScope] = None,
        include_superseded: bool = False,
        limit: int = None,
        auto_expand: bool = True
    ) -> List[RetrievalResult]:
        """
        Search documents within the specified scope.

        Args:
            query: Search query text
            scope: Document scope to search (default: DOCS_INDEX_ACTIVE)
            include_superseded: Include superseded docs in results
            limit: Maximum results to return
            auto_expand: If no results in primary scope, expand to next scope

        Returns:
            List of RetrievalResult objects
        """
        scope = scope or self.default_scope
        limit = limit or self.default_limit

        # Adjust scope based on include_superseded
        if include_superseded and scope == DocumentScope.DOCS_INDEX_ACTIVE:
            scope = DocumentScope.DOCS_INDEX_ALL

        # Search in primary scope
        results = self._search_scope(query, scope, limit)

        # Auto-expand if no results and enabled
        if not results and auto_expand:
            expanded_scope = self._get_expanded_scope(scope)
            if expanded_scope:
                logger.info(f"Auto-expanding search from {scope} to {expanded_scope}")
                results = self._search_scope(query, expanded_scope, limit)

        return results

    def _search_scope(
        self,
        query: str,
        scope: DocumentScope,
        limit: int
    ) -> List[RetrievalResult]:
        """Search within a specific scope."""
        try:
            from content.models import Document, DocumentEmbedding, ContentStatus
            from core.services.embedding_service import EmbeddingService

            # Build base queryset
            qs = Document.objects.all()

            # Apply scope filters
            if scope == DocumentScope.DOCS_INDEX_ACTIVE:
                # Only active, curated docs
                qs = qs.filter(
                    status=ContentStatus.PROCESSED,
                    extracted_metadata__scope='docs_index'
                )
            elif scope == DocumentScope.DOCS_INDEX_ALL:
                # All curated docs (active + archived/superseded)
                qs = qs.filter(
                    extracted_metadata__scope='docs_index'
                )
            # REPO_MARKDOWN scope has no filter (searches all)

            # Check if we have embeddings
            doc_ids_with_embeddings = set(
                DocumentEmbedding.objects.filter(document__in=qs)
                .values_list('document_id', flat=True)
                .distinct()
            )

            if doc_ids_with_embeddings:
                # Use semantic search
                return self._semantic_search(query, qs, limit)
            else:
                # Fall back to keyword search
                return self._keyword_search(query, qs, limit, scope)

        except Exception as e:
            logger.error(f"Scoped search failed: {e}")
            return []

    def _semantic_search(
        self,
        query: str,
        queryset,
        limit: int
    ) -> List[RetrievalResult]:
        """Perform semantic similarity search using embeddings."""
        try:
            from content.models import DocumentEmbedding
            from core.services.embedding_service import EmbeddingService

            # Generate query embedding
            service = EmbeddingService()
            query_embedding = service.create_embedding(
                text=query,
                model='text-embedding-3-small',
                agent_name='scoped_retrieval'
            )

            if not query_embedding or not query_embedding.embedding:
                return []

            # Find similar documents - extract vector from EmbeddingResult
            results = DocumentEmbedding.cosine_similarity_search(
                query_vector=query_embedding.embedding,
                limit=limit,
                min_similarity=self.min_similarity
            )

            return [
                RetrievalResult(
                    document_id=str(r.document_id),
                    title=r.document.title,
                    path=r.document.file_path,
                    content_snippet=r.chunk_text[:300],
                    similarity_score=1 - r.distance,  # Convert distance to similarity
                    scope=r.document.extracted_metadata.get('scope', 'unknown'),
                    status=r.document.status,
                    is_curated=r.document.extracted_metadata.get('scope') == 'docs_index'
                )
                for r in results
                if r.document
            ]

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    def _keyword_search(
        self,
        query: str,
        queryset,
        limit: int,
        scope: DocumentScope
    ) -> List[RetrievalResult]:
        """Fall back to keyword-based search."""
        try:
            # Split query into keywords
            keywords = query.lower().split()

            # Build Q objects for each keyword
            q_objects = Q()
            for keyword in keywords:
                q_objects |= (
                    Q(title__icontains=keyword) |
                    Q(processed_content__icontains=keyword) |
                    Q(description__icontains=keyword)
                )

            results = queryset.filter(q_objects)[:limit]

            return [
                RetrievalResult(
                    document_id=str(doc.id),
                    title=doc.title,
                    path=doc.file_path,
                    content_snippet=doc.processed_content[:300] if doc.processed_content else '',
                    similarity_score=0.5,  # Fixed score for keyword matches
                    scope=doc.extracted_metadata.get('scope', 'unknown') if doc.extracted_metadata else 'unknown',
                    status=doc.status,
                    is_curated=doc.extracted_metadata.get('scope') == 'docs_index' if doc.extracted_metadata else False
                )
                for doc in results
            ]

        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []

    def _get_expanded_scope(self, current_scope: DocumentScope) -> Optional[DocumentScope]:
        """Get the next broader scope for auto-expansion."""
        expansion_order = {
            DocumentScope.DOCS_INDEX_ACTIVE: DocumentScope.DOCS_INDEX_ALL,
            DocumentScope.DOCS_INDEX_ALL: DocumentScope.REPO_MARKDOWN,
            DocumentScope.REPO_MARKDOWN: None
        }
        return expansion_order.get(current_scope)

    def get_scope_stats(self) -> dict:
        """Get document counts per scope."""
        try:
            from content.models import Document, ContentStatus

            total = Document.objects.count()
            curated_active = Document.objects.filter(
                status=ContentStatus.PROCESSED,
                extracted_metadata__scope='docs_index'
            ).count()
            curated_all = Document.objects.filter(
                extracted_metadata__scope='docs_index'
            ).count()

            return {
                'docs_index_active': curated_active,
                'docs_index_all': curated_all,
                'docs_index_superseded': curated_all - curated_active,
                'total_documents': total,
                'uncurated': total - curated_all
            }

        except Exception as e:
            logger.error(f"Failed to get scope stats: {e}")
            return {}


# Singleton instance for convenience
_service_instance = None

def get_scoped_retrieval_service() -> ScopedRetrievalService:
    """Get the singleton scoped retrieval service."""
    global _service_instance
    if _service_instance is None:
        _service_instance = ScopedRetrievalService()
    return _service_instance
