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
    # Session 949: Risk-aware RAG fields
    is_critical: bool = False
    risk_level: str = 'medium'
    document_class: str = 'reference'
    retrieval_channel: str = 'semantic'  # semantic, critical, incident, constraint


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
        # Session 949: Risk-aware RAG configuration
        self.include_critical_docs = True  # Always include critical docs
        self.include_incident_channel = True  # Include incident/postmortem docs
        self.incident_lookback_days = 30  # How far back to look for incidents

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

    # =========================================================================
    # Session 949: Risk-Aware RAG - Dual-Channel Retrieval
    # =========================================================================

    def get_critical_docs(self, limit: int = 5) -> List[RetrievalResult]:
        """
        Get documents marked as critical - always include regardless of query.
        These are docs that should never be missed in any retrieval.
        """
        try:
            from content.models import Document, ContentStatus

            docs = Document.objects.filter(
                is_critical=True,
                status=ContentStatus.PROCESSED
            ).order_by('-retrieval_boost', '-updated_at')[:limit]

            return [
                RetrievalResult(
                    document_id=str(doc.id),
                    title=doc.title,
                    path=doc.file_path,
                    content_snippet=doc.processed_content[:300] if doc.processed_content else '',
                    similarity_score=1.0,  # Max score for critical docs
                    scope=doc.extracted_metadata.get('scope', 'unknown') if doc.extracted_metadata else 'unknown',
                    status=doc.status,
                    is_curated=True,
                    is_critical=True,
                    risk_level=doc.risk_level,
                    document_class=doc.document_class,
                    retrieval_channel='critical'
                )
                for doc in docs
            ]

        except Exception as e:
            logger.error(f"Failed to get critical docs: {e}")
            return []

    def get_incident_docs(self, lookback_days: int = None, limit: int = 5) -> List[RetrievalResult]:
        """
        Get incident reports, postmortems, and constraint docs.
        These are docs that describe failures, risks, and hard constraints.
        """
        try:
            from content.models import Document, ContentStatus
            from django.utils import timezone
            from datetime import timedelta

            lookback = lookback_days or self.incident_lookback_days
            cutoff_date = timezone.now() - timedelta(days=lookback)

            # Get incident-class docs (postmortems, incident reports, security advisories)
            incident_classes = ['postmortem', 'incident_report', 'security', 'constraint']

            docs = Document.objects.filter(
                document_class__in=incident_classes,
                status=ContentStatus.PROCESSED
            ).filter(
                # Either has an incident date in lookback period OR was updated recently
                Q(incident_date__gte=cutoff_date) | Q(updated_at__gte=cutoff_date)
            ).order_by('-risk_level', '-incident_date', '-updated_at')[:limit]

            return [
                RetrievalResult(
                    document_id=str(doc.id),
                    title=doc.title,
                    path=doc.file_path,
                    content_snippet=doc.processed_content[:300] if doc.processed_content else '',
                    similarity_score=0.9,  # High score for incident docs
                    scope=doc.extracted_metadata.get('scope', 'unknown') if doc.extracted_metadata else 'unknown',
                    status=doc.status,
                    is_curated=True,
                    is_critical=doc.is_critical,
                    risk_level=doc.risk_level,
                    document_class=doc.document_class,
                    retrieval_channel='incident'
                )
                for doc in docs
            ]

        except Exception as e:
            logger.error(f"Failed to get incident docs: {e}")
            return []

    def get_audit_findings_context(self, priorities: List[str] = None, limit: int = 3) -> List[dict]:
        """
        Get open/in-progress audit findings as context for RAG.
        Returns findings that might be relevant to current queries.
        """
        try:
            from core.models_audit_tracking import AuditFinding

            priorities = priorities or ['P0', 'P1']

            findings = AuditFinding.objects.filter(
                priority__in=priorities,
                status__in=['open', 'in_progress']
            ).order_by('priority', '-updated_at')[:limit]

            return [
                {
                    'finding_id': str(f.id),
                    'title': f.title,
                    'priority': f.priority,
                    'category': f.category,
                    'status': f.status,
                    'description': f.description[:500],
                    'recommendation': f.recommendation[:300] if f.recommendation else '',
                    'affected_components': f.affected_components,
                    'linked_document_id': str(f.linked_document_id) if f.linked_document_id else None,
                }
                for f in findings
            ]

        except Exception as e:
            logger.error(f"Failed to get audit findings: {e}")
            return []

    def dual_channel_search(
        self,
        query: str,
        scope: Optional[DocumentScope] = None,
        include_critical: bool = True,
        include_incidents: bool = True,
        include_findings: bool = True,
        limit: int = None
    ) -> dict:
        """
        Session 949: Dual-channel retrieval that combines:
        1. Semantic search results
        2. Critical docs (always include)
        3. Incident/postmortem docs
        4. Open audit findings

        Returns:
            {
                'semantic_results': [...],
                'critical_docs': [...],
                'incident_docs': [...],
                'audit_findings': [...],
                'merged_results': [...]  # Deduplicated and ranked
            }
        """
        limit = limit or self.default_limit

        # Channel 1: Semantic search
        semantic_results = self.search(query, scope=scope, limit=limit)

        # Channel 2: Critical docs
        critical_docs = self.get_critical_docs(limit=3) if include_critical else []

        # Channel 3: Incident docs
        incident_docs = self.get_incident_docs(limit=3) if include_incidents else []

        # Channel 4: Audit findings
        audit_findings = self.get_audit_findings_context(limit=3) if include_findings else []

        # Merge and deduplicate results
        seen_ids = set()
        merged = []

        # Priority order: critical > incident > semantic
        for doc in critical_docs:
            if doc.document_id not in seen_ids:
                seen_ids.add(doc.document_id)
                merged.append(doc)

        for doc in incident_docs:
            if doc.document_id not in seen_ids:
                seen_ids.add(doc.document_id)
                merged.append(doc)

        for doc in semantic_results:
            if doc.document_id not in seen_ids:
                seen_ids.add(doc.document_id)
                merged.append(doc)

        return {
            'semantic_results': semantic_results,
            'critical_docs': critical_docs,
            'incident_docs': incident_docs,
            'audit_findings': audit_findings,
            'merged_results': merged[:limit]
        }

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
