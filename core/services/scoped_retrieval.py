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
from django.db.utils import DatabaseError

# Session 1234 D17 — narrow-except allowlist for retrieval methods.
# Pre-D17 every method here caught `Exception` and returned []/{},
# which silently hid logic errors (sliced-then-filtered TypeError
# per D16, AttributeError on missing fields, KeyError on changed
# APIs, etc.) as "no results found". The allowlist below covers
# legitimate runtime-only errors: DB connection drops, network
# failures hitting embedding service, OS-level issues. Logic errors
# now propagate so tests + production logs see them. Memory:
# feedback_test_real_db_for_queryset_semantics.md (D16) +
# feedback_fail_loud_first_then_root_cause_then_telemetry.
_RETRIEVAL_ENV_ERRORS = (DatabaseError, ConnectionError, OSError)

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

        # Session 949 P2: Risk-aware re-ranking configuration
        # These boosts are additive to similarity scores (0.0 - 1.0 scale)
        self.risk_level_boosts = {
            'critical': 0.25,  # +25% boost for critical docs
            'high': 0.15,      # +15% boost for high-risk docs
            'medium': 0.0,     # No boost for medium (default)
            'low': -0.05,      # Slight penalty for low-priority docs
        }
        self.document_class_boosts = {
            'postmortem': 0.20,       # Postmortems are highly valuable
            'incident_report': 0.15,  # Incident reports next
            'security': 0.15,         # Security advisories important
            'constraint': 0.10,       # Policy/constraint docs
            'architecture': 0.05,     # Architecture decisions
            'runbook': 0.05,          # Operational runbooks
            'changelog': 0.0,         # Changelogs standard
            'reference': 0.0,         # Reference docs standard
        }
        self.critical_doc_boost = 0.30  # is_critical=True gets max boost
        self.enable_risk_reranking = True  # Toggle for risk-aware re-ranking

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

        except _RETRIEVAL_ENV_ERRORS as e:
            logger.error(f"Scoped search failed: {e}")
            return []

    def _semantic_search(
        self,
        query: str,
        queryset,
        limit: int
    ) -> List[RetrievalResult]:
        """Perform semantic similarity search using embeddings with risk-aware re-ranking."""
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

            # Find similar documents - fetch more than limit for re-ranking
            # Session 949 P2: Fetch extra to allow re-ranking to surface risk-boosted docs
            fetch_limit = limit * 2 if self.enable_risk_reranking else limit
            results = DocumentEmbedding.cosine_similarity_search(
                query_vector=query_embedding.embedding,
                limit=fetch_limit,
                min_similarity=self.min_similarity
            )

            # Build results with risk metadata
            retrieval_results = [
                RetrievalResult(
                    document_id=str(r.document_id),
                    title=r.document.title,
                    path=r.document.file_path,
                    content_snippet=r.chunk_text[:300],
                    similarity_score=1 - r.distance,  # Convert distance to similarity
                    scope=r.document.extracted_metadata.get('scope', 'unknown') if r.document.extracted_metadata else 'unknown',
                    status=r.document.status,
                    is_curated=r.document.extracted_metadata.get('scope') == 'docs_index' if r.document.extracted_metadata else False,
                    # Session 949 P2: Include risk metadata for re-ranking
                    is_critical=getattr(r.document, 'is_critical', False),
                    risk_level=getattr(r.document, 'risk_level', 'medium'),
                    document_class=getattr(r.document, 'document_class', 'reference'),
                    retrieval_channel='semantic'
                )
                for r in results
                if r.document
            ]

            # Session 949 P2: Apply risk-aware re-ranking
            return self._apply_risk_reranking(retrieval_results, limit)

        except _RETRIEVAL_ENV_ERRORS as e:
            logger.error(f"Semantic search failed: {e}")
            return []

    def _keyword_search(
        self,
        query: str,
        queryset,
        limit: int,
        scope: DocumentScope
    ) -> List[RetrievalResult]:
        """Fall back to keyword-based search with risk-aware re-ranking."""
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

            # Session 949 P2: Fetch extra for re-ranking
            fetch_limit = limit * 2 if self.enable_risk_reranking else limit
            results = queryset.filter(q_objects)[:fetch_limit]

            retrieval_results = [
                RetrievalResult(
                    document_id=str(doc.id),
                    title=doc.title,
                    path=doc.file_path,
                    content_snippet=doc.processed_content[:300] if doc.processed_content else '',
                    similarity_score=0.5,  # Fixed score for keyword matches
                    scope=doc.extracted_metadata.get('scope', 'unknown') if doc.extracted_metadata else 'unknown',
                    status=doc.status,
                    is_curated=doc.extracted_metadata.get('scope') == 'docs_index' if doc.extracted_metadata else False,
                    # Session 949 P2: Include risk metadata for re-ranking
                    is_critical=getattr(doc, 'is_critical', False),
                    risk_level=getattr(doc, 'risk_level', 'medium'),
                    document_class=getattr(doc, 'document_class', 'reference'),
                    retrieval_channel='keyword'
                )
                for doc in results
            ]

            # Session 949 P2: Apply risk-aware re-ranking
            return self._apply_risk_reranking(retrieval_results, limit)

        except _RETRIEVAL_ENV_ERRORS as e:
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
    # Session 949 P2: Risk-Aware Re-Ranking
    # =========================================================================

    def _calculate_risk_boost(self, result: RetrievalResult) -> float:
        """
        Calculate the risk-based boost for a retrieval result.

        Args:
            result: The retrieval result to calculate boost for

        Returns:
            Float boost value (can be positive or negative)
        """
        boost = 0.0

        # Critical doc boost (highest priority)
        if result.is_critical:
            boost += self.critical_doc_boost

        # Risk level boost
        boost += self.risk_level_boosts.get(result.risk_level, 0.0)

        # Document class boost
        boost += self.document_class_boosts.get(result.document_class, 0.0)

        return boost

    def _apply_risk_reranking(
        self,
        results: List[RetrievalResult],
        limit: int
    ) -> List[RetrievalResult]:
        """
        Session 949 P2: Re-rank results based on risk levels and document classes.

        Applies boost factors to similarity scores and re-sorts results.
        Critical docs, incident reports, and postmortems get priority.

        Args:
            results: List of retrieval results with similarity scores
            limit: Maximum number of results to return

        Returns:
            Re-ranked list of results
        """
        if not self.enable_risk_reranking or not results:
            return results[:limit]

        # Calculate boosted scores
        scored_results = []
        for result in results:
            boost = self._calculate_risk_boost(result)
            boosted_score = min(1.0, result.similarity_score + boost)  # Cap at 1.0

            # Log significant boosts for observability
            if boost > 0.1:
                logger.debug(
                    f"🎯 [Session 949 P2] Risk boost +{boost:.2f} for '{result.title}' "
                    f"(is_critical={result.is_critical}, risk={result.risk_level}, "
                    f"class={result.document_class})"
                )

            scored_results.append((boosted_score, result))

        # Sort by boosted score (descending)
        scored_results.sort(key=lambda x: x[0], reverse=True)

        # Update similarity scores to reflect boosted values
        reranked = []
        for boosted_score, result in scored_results[:limit]:
            # Create new result with boosted score
            reranked.append(RetrievalResult(
                document_id=result.document_id,
                title=result.title,
                path=result.path,
                content_snippet=result.content_snippet,
                similarity_score=boosted_score,  # Use boosted score
                scope=result.scope,
                status=result.status,
                is_curated=result.is_curated,
                is_critical=result.is_critical,
                risk_level=result.risk_level,
                document_class=result.document_class,
                retrieval_channel=result.retrieval_channel,
            ))

        return reranked

    def search_by_document_class(
        self,
        document_classes: List[str],
        limit: int = 10,
        risk_levels: Optional[List[str]] = None
    ) -> List[RetrievalResult]:
        """
        Session 949 P2: Search for documents by their classification.

        Use this to find all postmortems, incident reports, security advisories, etc.

        Args:
            document_classes: List of document classes to search for
                              Options: postmortem, incident_report, security, constraint,
                                      architecture, runbook, changelog, reference
            limit: Maximum number of results
            risk_levels: Optional filter by risk levels (critical, high, medium, low)

        Returns:
            List of matching documents, ordered by risk_level and recency
        """
        try:
            from content.models import Document, ContentStatus

            qs = Document.objects.filter(
                document_class__in=document_classes,
                status=ContentStatus.PROCESSED
            )

            if risk_levels:
                qs = qs.filter(risk_level__in=risk_levels)

            # Order by risk level (critical first) and recency
            docs = qs.order_by('-is_critical', '-retrieval_boost', '-updated_at')[:limit]

            return [
                RetrievalResult(
                    document_id=str(doc.id),
                    title=doc.title,
                    path=doc.file_path,
                    content_snippet=doc.processed_content[:300] if doc.processed_content else '',
                    similarity_score=1.0 if doc.is_critical else 0.9,  # High base score
                    scope=doc.extracted_metadata.get('scope', 'unknown') if doc.extracted_metadata else 'unknown',
                    status=doc.status,
                    is_curated=doc.extracted_metadata.get('scope') == 'docs_index' if doc.extracted_metadata else False,
                    is_critical=doc.is_critical,
                    risk_level=doc.risk_level,
                    document_class=doc.document_class,
                    retrieval_channel='class_filter'
                )
                for doc in docs
            ]

        except _RETRIEVAL_ENV_ERRORS as e:
            logger.error(f"Document class search failed: {e}")
            return []

    def get_postmortems(self, limit: int = 10) -> List[RetrievalResult]:
        """Convenience method to get postmortem documents."""
        return self.search_by_document_class(['postmortem'], limit=limit)

    def get_incident_reports(self, limit: int = 10) -> List[RetrievalResult]:
        """Convenience method to get incident report documents."""
        return self.search_by_document_class(['incident_report'], limit=limit)

    def get_security_advisories(self, limit: int = 10) -> List[RetrievalResult]:
        """Convenience method to get security advisory documents."""
        return self.search_by_document_class(['security'], limit=limit)

    def get_constraint_docs(self, limit: int = 10) -> List[RetrievalResult]:
        """Convenience method to get policy/constraint documents."""
        return self.search_by_document_class(['constraint'], limit=limit)

    def get_high_risk_docs(self, limit: int = 10) -> List[RetrievalResult]:
        """Get all documents with critical or high risk levels."""
        return self.search_by_document_class(
            document_classes=['postmortem', 'incident_report', 'security', 'constraint',
                            'architecture', 'runbook', 'changelog', 'reference'],
            limit=limit,
            risk_levels=['critical', 'high']
        )

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

        except _RETRIEVAL_ENV_ERRORS as e:
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

        except _RETRIEVAL_ENV_ERRORS as e:
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

        except _RETRIEVAL_ENV_ERRORS as e:
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

        except _RETRIEVAL_ENV_ERRORS as e:
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
