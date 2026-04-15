"""
Knowledge-First Router Service
==============================

Session 744: Intelligent routing that checks existing knowledge BEFORE
querying external sources or routing to agents.

Flow:
    Task arrives
        │
        ▼
    Check existing knowledge (embeddings/learnings)
        │
        ├── Sufficient & Fresh? → Use cached knowledge
        │
        ├── Stale? → Query spiders for fresh data
        │
        └── Missing? → Route to ResearchAgent

This prevents:
- Redundant API calls when we already know the answer
- Stale information being used when fresh data is available
- Unnecessary agent invocations for simple queries

Usage:
    from core.services.knowledge_first_router import get_knowledge_first_router

    router = get_knowledge_first_router()
    decision = router.route_with_knowledge(
        task="What are the latest AI trends?",
        agent_name="ResearchAgent"
    )

    if decision.use_cached:
        # Use decision.cached_knowledge directly
    elif decision.refresh_spiders:
        # Get fresh spider data first
    else:
        # Route to agent for full research
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from django.utils import timezone

logger = logging.getLogger(__name__)


class RoutingDecision(Enum):
    """Possible routing decisions."""
    USE_CACHED_KNOWLEDGE = "use_cached"      # Knowledge is sufficient and fresh
    REFRESH_THEN_RESPOND = "refresh_spiders"  # Need fresh spider data first
    ROUTE_TO_RESEARCH = "research_agent"      # Need active research
    ROUTE_TO_AGENT = "route_agent"            # Route to specified agent with context


@dataclass
class KnowledgeMatch:
    """A matched piece of knowledge."""
    source: str  # 'embedding', 'learning', 'spider', 'research'
    content: str
    relevance_score: float
    freshness_score: float  # 1.0 = fresh, 0.0 = very stale
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def combined_score(self) -> float:
        """Combined relevance * freshness score."""
        return self.relevance_score * self.freshness_score


@dataclass
class KnowledgeRoutingResult:
    """Result of knowledge-first routing decision."""
    decision: RoutingDecision
    confidence: float
    reasoning: str

    # Knowledge found
    cached_knowledge: List[KnowledgeMatch] = field(default_factory=list)
    knowledge_summary: str = ""

    # Routing info
    recommended_agent: str = ""
    spider_categories_to_refresh: List[str] = field(default_factory=list)

    # Metrics
    knowledge_coverage: float = 0.0  # 0-1, how much of query we can answer
    freshness_avg: float = 0.0
    sources_checked: List[str] = field(default_factory=list)

    @property
    def use_cached(self) -> bool:
        return self.decision == RoutingDecision.USE_CACHED_KNOWLEDGE

    @property
    def refresh_spiders(self) -> bool:
        return self.decision == RoutingDecision.REFRESH_THEN_RESPOND

    @property
    def needs_research(self) -> bool:
        return self.decision == RoutingDecision.ROUTE_TO_RESEARCH


class KnowledgeFirstRouter:
    """
    Intelligent router that checks existing knowledge before external queries.

    This creates a "knowledge-first" paradigm where:
    1. We check what we already know
    2. Evaluate if it's sufficient and fresh
    3. Only then decide to query spiders or route to agents
    """

    # Thresholds for decision making
    KNOWLEDGE_SUFFICIENT_THRESHOLD = 0.7  # Combined score needed to use cached
    FRESHNESS_STALE_THRESHOLD = 0.4       # Below this, knowledge is considered stale
    COVERAGE_MINIMUM_THRESHOLD = 0.5      # Minimum coverage to avoid research agent

    # Freshness decay rates (in hours)
    FRESHNESS_HALF_LIFE = {
        'spider': 24,          # Spider data half-fresh after 24 hours
        'learning': 168,       # Learning patterns half-fresh after 1 week
        'embedding': 720,      # Embeddings half-fresh after 30 days
        'research': 72,        # Research results half-fresh after 3 days
        'user_document': 2160, # User docs half-fresh after 90 days (long-lived reference)
    }

    def __init__(self):
        self._unified_search = None
        self._spider_search = None
        self._learning_engine = None
        self._embedding_service = None
        self._embeddings_cache = {}

    # ==================== Lazy-Loaded Dependencies ====================

    @property
    def unified_search(self):
        """Lazy-load unified intelligence search."""
        if self._unified_search is None:
            from core.services.unified_intelligence_search import UnifiedIntelligenceSearch
            self._unified_search = UnifiedIntelligenceSearch()
        return self._unified_search

    @property
    def spider_search(self):
        """Lazy-load spider semantic search."""
        if self._spider_search is None:
            from core.services.spider_semantic_search import get_spider_semantic_search
            self._spider_search = get_spider_semantic_search()
        return self._spider_search

    @property
    def learning_engine(self):
        """Lazy-load learning pattern engine."""
        if self._learning_engine is None:
            from core.services.learning_pattern_engine import get_learning_pattern_engine
            self._learning_engine = get_learning_pattern_engine()
        return self._learning_engine

    @property
    def embedding_service(self):
        """Session 744: Lazy-load centralized EmbeddingService for tracked embedding calls."""
        if self._embedding_service is None:
            from core.services.embedding_service import get_embedding_service
            self._embedding_service = get_embedding_service()
        return self._embedding_service

    # ==================== Freshness Calculation ====================

    def _calculate_freshness(self, timestamp: datetime, source_type: str) -> float:
        """
        Calculate freshness score (0-1) based on age and source type.

        Uses exponential decay with source-specific half-lives.
        """
        if timestamp is None:
            return 0.5  # Unknown timestamp = moderate freshness

        # Make timestamp timezone-aware if needed
        if timezone.is_naive(timestamp):
            timestamp = timezone.make_aware(timestamp)

        age_hours = (timezone.now() - timestamp).total_seconds() / 3600
        half_life = self.FRESHNESS_HALF_LIFE.get(source_type, 168)  # Default 1 week

        # Exponential decay: freshness = 0.5 ^ (age / half_life)
        freshness = 0.5 ** (age_hours / half_life)

        return min(1.0, max(0.0, freshness))

    # ==================== Knowledge Queries ====================

    def _query_spider_data(
        self,
        query: str,
        limit: int = 10
    ) -> List[KnowledgeMatch]:
        """Query spider data for relevant information."""
        matches = []

        try:
            results = self.spider_search.semantic_search(
                query,
                limit=limit,
                hours=168  # Last 7 days
            )

            for result in results:
                # Parse timestamp — on any parse failure, log the value and
                # fall back to a 24h-old default. Bare except previously hid
                # bad found_at payloads so every parse error silently
                # downranked fresh spider results to "1 day old."
                ts = None
                if hasattr(result, 'found_at'):
                    try:
                        ts = datetime.fromisoformat(
                            result.found_at.replace('Z', '+00:00')
                        )
                    except (ValueError, TypeError, AttributeError) as e:
                        logger.warning(
                            "Spider freshness parse failed for found_at=%r "
                            "(%s: %s) — defaulting to 24h old",
                            getattr(result, 'found_at', None),
                            type(e).__name__,
                            e,
                        )
                if ts is None:
                    ts = timezone.now() - timedelta(hours=24)

                freshness = self._calculate_freshness(ts, 'spider')

                matches.append(KnowledgeMatch(
                    source='spider',
                    content=f"{result.title}: {result.description[:300]}",
                    relevance_score=result.similarity,
                    freshness_score=freshness,
                    timestamp=ts,
                    metadata={
                        'url': result.url,
                        'spider': result.source,
                        'category': result.category
                    }
                ))
        except Exception as e:
            logger.warning(f"Spider data query failed: {e}")

        return matches

    def _query_learning_patterns(
        self,
        query: str,
        agent_name: Optional[str] = None
    ) -> List[KnowledgeMatch]:
        """Query learning patterns for relevant past experiences."""
        matches = []

        try:
            patterns = self.learning_engine.get_patterns_for_agent(
                agent_name or 'ResearchAgent',
                query
            )

            if patterns.get('has_patterns'):
                # Best practices as knowledge
                for practice in patterns.get('best_practices', []):
                    matches.append(KnowledgeMatch(
                        source='learning',
                        content=practice,
                        relevance_score=0.7,  # Best practices are generally relevant
                        freshness_score=self._calculate_freshness(
                            timezone.now() - timedelta(days=7),  # Assume 1 week old
                            'learning'
                        ),
                        timestamp=timezone.now() - timedelta(days=7),
                        metadata={'type': 'best_practice'}
                    ))

                # Collaboration insights
                for insight in patterns.get('collaboration_insights', []):
                    matches.append(KnowledgeMatch(
                        source='learning',
                        content=insight,
                        relevance_score=0.6,
                        freshness_score=0.8,
                        timestamp=timezone.now() - timedelta(days=3),
                        metadata={'type': 'collaboration_insight'}
                    ))
        except Exception as e:
            logger.warning(f"Learning patterns query failed: {e}")

        return matches

    def _query_shared_knowledge(self, query: str) -> List[KnowledgeMatch]:
        """Query SharedKnowledge table for relevant entries."""
        matches = []

        try:
            from core.models import SharedKnowledge

            # Get query embedding
            query_embedding = self._get_embedding(query)
            if not query_embedding:
                return matches

            # Get recent shared knowledge
            recent_knowledge = SharedKnowledge.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=30)
            ).order_by('-created_at')[:50]

            for knowledge in recent_knowledge:
                # Get knowledge embedding
                knowledge_text = f"{knowledge.title}: {knowledge.knowledge_content or knowledge.description}"
                knowledge_embedding = self._get_embedding(knowledge_text)

                if knowledge_embedding:
                    similarity = self._cosine_similarity(query_embedding, knowledge_embedding)

                    if similarity > 0.3:  # Minimum relevance
                        matches.append(KnowledgeMatch(
                            source='embedding',
                            content=knowledge_text[:500],
                            relevance_score=similarity,
                            freshness_score=self._calculate_freshness(
                                knowledge.created_at,
                                'embedding'
                            ),
                            timestamp=knowledge.created_at,
                            metadata={
                                'knowledge_type': knowledge.knowledge_type,
                                'agent': knowledge.source_agent
                            }
                        ))
        except Exception as e:
            logger.warning(f"Shared knowledge query failed: {e}")

        return matches

    def _query_agent_knowledge_sources(self, query: str) -> List[KnowledgeMatch]:
        """Query AgentKnowledgeSource for relevant entries."""
        matches = []

        try:
            from core.models import AgentKnowledgeSource

            query_embedding = self._get_embedding(query)
            if not query_embedding:
                return matches

            # Get recent knowledge sources
            recent_sources = AgentKnowledgeSource.objects.filter(
                last_updated_at__gte=timezone.now() - timedelta(days=14)
            ).order_by('-last_updated_at')[:100]

            for source in recent_sources:
                source_text = f"{source.title}: {source.summary or ''}"
                source_embedding = self._get_embedding(source_text[:500])

                if source_embedding:
                    similarity = self._cosine_similarity(query_embedding, source_embedding)

                    if similarity > 0.35:
                        matches.append(KnowledgeMatch(
                            source='embedding',
                            content=source_text[:400],
                            relevance_score=similarity,
                            freshness_score=self._calculate_freshness(
                                source.last_updated_at,
                                'embedding'
                            ),
                            timestamp=source.last_updated_at,
                            metadata={
                                'knowledge_type': source.knowledge_type,
                                'agent': str(source.agent) if source.agent else None
                            }
                        ))
        except Exception as e:
            logger.warning(f"Agent knowledge source query failed: {e}")

        return matches

    def _query_user_documents(self, query: str, limit: int = 10) -> List[KnowledgeMatch]:
        """Query user-uploaded RAG documents for relevant knowledge."""
        matches = []
        try:
            query_embedding = self._get_embedding(query)
            if not query_embedding:
                return matches

            from content.models import DocumentEmbedding

            results = DocumentEmbedding.cosine_similarity_search(
                query_vector=query_embedding,
                limit=limit,
                min_similarity=0.35
            )

            for result in results:
                similarity = 1 - result.distance
                doc = result.document
                freshness = self._calculate_freshness(doc.created_at, 'user_document')

                matches.append(KnowledgeMatch(
                    source='user_document',
                    content=result.chunk_text[:500],
                    relevance_score=similarity,
                    freshness_score=freshness,
                    timestamp=doc.created_at,
                    metadata={
                        'document_id': doc.id,
                        'document_title': doc.title,
                        'document_type': doc.document_type,
                        'chunk_index': result.chunk_index,
                        'source_url': doc.source_url or '',
                    }
                ))
        except Exception as e:
            logger.warning(f"User document query failed: {e}")

        return matches

    # ==================== Embedding Utilities ====================

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for text with caching. Session 744: Uses centralized EmbeddingService."""
        cache_key = text[:100]

        if cache_key in self._embeddings_cache:
            return self._embeddings_cache[cache_key]

        try:
            # Session 744: Use centralized service for tracking
            result = self.embedding_service.create_embedding(
                text=text[:8000],
                model="text-embedding-3-small",
                agent_name='KnowledgeFirstRouter'
            )
            embedding = result.embedding
            self._embeddings_cache[cache_key] = embedding
            return embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import numpy as np

        a = np.array(vec1)
        b = np.array(vec2)

        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    # ==================== Main Routing Logic ====================

    def route_with_knowledge(
        self,
        task: str,
        agent_name: Optional[str] = None,
        check_spiders: bool = True,
        check_learnings: bool = True,
        check_embeddings: bool = True,
        check_user_documents: bool = True
    ) -> KnowledgeRoutingResult:
        """
        Route a task using knowledge-first approach.

        Args:
            task: The task or query to route
            agent_name: Target agent (optional)
            check_spiders: Whether to check spider data
            check_learnings: Whether to check learning patterns
            check_embeddings: Whether to check knowledge embeddings

        Returns:
            KnowledgeRoutingResult with decision and supporting data
        """
        logger.info(f"Knowledge-first routing for: {task[:100]}...")

        all_matches: List[KnowledgeMatch] = []
        sources_checked = []

        # 1. Query spider data (most recent real-world info)
        if check_spiders:
            spider_matches = self._query_spider_data(task)
            all_matches.extend(spider_matches)
            sources_checked.append('spider_data')
            logger.debug(f"Found {len(spider_matches)} spider matches")

        # 2. Query learning patterns (past agent experiences)
        if check_learnings:
            learning_matches = self._query_learning_patterns(task, agent_name)
            all_matches.extend(learning_matches)
            sources_checked.append('learning_patterns')
            logger.debug(f"Found {len(learning_matches)} learning matches")

        # 3. Query knowledge embeddings (stored knowledge)
        if check_embeddings:
            shared_matches = self._query_shared_knowledge(task)
            all_matches.extend(shared_matches)
            sources_checked.append('shared_knowledge')

            source_matches = self._query_agent_knowledge_sources(task)
            all_matches.extend(source_matches)
            sources_checked.append('agent_knowledge_sources')
            logger.debug(f"Found {len(shared_matches) + len(source_matches)} embedding matches")

        # 4. Query user-uploaded documents (RAG)
        if check_user_documents:
            doc_matches = self._query_user_documents(task)
            all_matches.extend(doc_matches)
            sources_checked.append('user_documents')
            logger.debug(f"Found {len(doc_matches)} user document matches")

        # 5. Analyze matches and make decision
        return self._make_routing_decision(
            task=task,
            matches=all_matches,
            sources_checked=sources_checked,
            agent_name=agent_name
        )

    def _make_routing_decision(
        self,
        task: str,
        matches: List[KnowledgeMatch],
        sources_checked: List[str],
        agent_name: Optional[str] = None
    ) -> KnowledgeRoutingResult:
        """Analyze matches and decide routing strategy."""
        spider_categories: List[str] = []  # Initialize early

        if not matches:
            # No knowledge found - need full research
            return KnowledgeRoutingResult(
                decision=RoutingDecision.ROUTE_TO_RESEARCH,
                confidence=0.9,
                reasoning="No relevant knowledge found in any source. Full research needed.",
                recommended_agent="ResearchAgent",
                sources_checked=sources_checked
            )

        # Sort by combined score
        matches.sort(key=lambda m: m.combined_score, reverse=True)
        top_matches = matches[:10]

        # Calculate aggregate metrics
        avg_relevance = sum(m.relevance_score for m in top_matches) / len(top_matches)
        avg_freshness = sum(m.freshness_score for m in top_matches) / len(top_matches)
        avg_combined = sum(m.combined_score for m in top_matches) / len(top_matches)

        # Determine knowledge coverage
        # High coverage = many relevant, diverse sources
        source_diversity = len(set(m.source for m in top_matches)) / 5  # Max 5 source types
        knowledge_coverage = min(1.0, avg_relevance * (0.5 + 0.5 * source_diversity))

        # Generate knowledge summary
        knowledge_summary = self._generate_summary(top_matches)

        # Decision logic
        if avg_combined >= self.KNOWLEDGE_SUFFICIENT_THRESHOLD:
            # Knowledge is sufficient and fresh
            decision = RoutingDecision.USE_CACHED_KNOWLEDGE
            reasoning = f"Found sufficient knowledge (score: {avg_combined:.2f}). " \
                       f"Top sources: {', '.join(set(m.source for m in top_matches[:3]))}"
            confidence = min(0.95, avg_combined)

        elif avg_relevance >= self.COVERAGE_MINIMUM_THRESHOLD and avg_freshness < self.FRESHNESS_STALE_THRESHOLD:
            # Knowledge exists but is stale - refresh spiders
            decision = RoutingDecision.REFRESH_THEN_RESPOND
            reasoning = f"Relevant knowledge found (relevance: {avg_relevance:.2f}) but stale " \
                       f"(freshness: {avg_freshness:.2f}). Refreshing spider data first."
            confidence = 0.7

            # Identify which spider categories to refresh
            spider_categories = list(set(
                m.metadata.get('category', 'general')
                for m in matches if m.source == 'spider'
            ))

        elif avg_relevance >= 0.3:
            # Partial knowledge - route to agent with context
            decision = RoutingDecision.ROUTE_TO_AGENT
            reasoning = f"Partial knowledge found (relevance: {avg_relevance:.2f}). " \
                       f"Routing to agent with existing context."
            confidence = 0.6

        else:
            # Insufficient knowledge - full research needed
            decision = RoutingDecision.ROUTE_TO_RESEARCH
            reasoning = f"Insufficient knowledge (relevance: {avg_relevance:.2f}). " \
                       f"Full research needed."
            confidence = 0.8

        return KnowledgeRoutingResult(
            decision=decision,
            confidence=confidence,
            reasoning=reasoning,
            cached_knowledge=top_matches,
            knowledge_summary=knowledge_summary,
            recommended_agent=agent_name or ("ResearchAgent" if decision == RoutingDecision.ROUTE_TO_RESEARCH else ""),
            spider_categories_to_refresh=spider_categories if decision == RoutingDecision.REFRESH_THEN_RESPOND else [],
            knowledge_coverage=knowledge_coverage,
            freshness_avg=avg_freshness,
            sources_checked=sources_checked
        )

    def _generate_summary(self, matches: List[KnowledgeMatch]) -> str:
        """Generate a summary of the knowledge found."""
        if not matches:
            return ""

        # Group by source
        by_source = {}
        for m in matches:
            if m.source not in by_source:
                by_source[m.source] = []
            by_source[m.source].append(m)

        summary_parts = []

        for source, source_matches in by_source.items():
            top = source_matches[0]
            summary_parts.append(f"[{source}] {top.content[:200]}...")

        return "\n\n".join(summary_parts[:3])  # Top 3 sources

    # ==================== Convenience Methods ====================

    def should_use_cached(self, task: str, agent_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Quick check if cached knowledge is sufficient.

        Returns:
            (should_use_cached, reason)
        """
        result = self.route_with_knowledge(task, agent_name)
        return result.use_cached, result.reasoning

    def get_relevant_knowledge(
        self,
        task: str,
        min_score: float = 0.4
    ) -> List[Dict[str, Any]]:
        """
        Get relevant knowledge without routing decision.

        Returns list of knowledge items with scores.
        """
        result = self.route_with_knowledge(task)

        return [
            {
                'source': m.source,
                'content': m.content,
                'relevance': m.relevance_score,
                'freshness': m.freshness_score,
                'combined_score': m.combined_score
            }
            for m in result.cached_knowledge
            if m.combined_score >= min_score
        ]

    def analyze_knowledge_state(self, task: str) -> Dict[str, Any]:
        """
        Analyze knowledge state for a task without making routing decision.

        Useful for debugging and understanding knowledge coverage.
        """
        result = self.route_with_knowledge(task)

        return {
            'task': task,
            'knowledge_coverage': result.knowledge_coverage,
            'freshness_avg': result.freshness_avg,
            'sources_checked': result.sources_checked,
            'matches_found': len(result.cached_knowledge),
            'top_matches': [
                {
                    'source': m.source,
                    'relevance': round(m.relevance_score, 3),
                    'freshness': round(m.freshness_score, 3),
                    'combined': round(m.combined_score, 3),
                    'content_preview': m.content[:100]
                }
                for m in result.cached_knowledge[:5]
            ],
            'would_route_to': result.decision.value,
            'reasoning': result.reasoning
        }


# ==================== Factory Function ====================

_router_instance = None

def get_knowledge_first_router() -> KnowledgeFirstRouter:
    """Get singleton instance of KnowledgeFirstRouter."""
    global _router_instance
    if _router_instance is None:
        _router_instance = KnowledgeFirstRouter()
    return _router_instance
