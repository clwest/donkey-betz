"""
Knowledge Similarity Service
============================

Session 358: Enhanced Delta Detection for Agent Learning

This service uses semantic similarity (embeddings + cosine similarity) to detect
when knowledge is "similar enough" that it shouldn't be transferred again.

Current Problem:
- Exact title matching misses semantic duplicates
- "AI Content Tools" and "Content Creation AI Tools" are different titles but same knowledge

Solution:
- Generate embeddings for knowledge titles + summaries
- Use cosine similarity to detect semantic duplicates
- Configurable threshold (0.85 = very similar, 0.7 = moderately similar)

Usage:
    from core.services.knowledge_similarity import get_knowledge_similarity_service

    service = get_knowledge_similarity_service()

    # Check if knowledge already exists for an agent
    is_duplicate = service.is_semantically_similar(
        agent=student_agent,
        title="AI Content Tools for Creators",
        summary="Tools for creating AI-powered content",
        knowledge_type="tool_discovery",
        threshold=0.85
    )

    # Get similarity score
    score, similar_knowledge = service.find_most_similar(
        agent=student_agent,
        title="AI Content Tools",
        knowledge_type="tool_discovery"
    )
"""

import logging
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

import numpy as np
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Session 744: Use centralized EmbeddingService for all embedding calls
from core.services.embedding_service import get_embedding_service

HAS_OPENAI = True  # EmbeddingService handles this internally


@dataclass
class SimilarityResult:
    """Result from similarity check."""
    is_similar: bool
    similarity_score: float
    matching_knowledge_id: Optional[str]
    matching_knowledge_title: Optional[str]
    reason: str


class KnowledgeSimilarityService:
    """
    Semantic similarity service for agent knowledge.

    Uses OpenAI embeddings to compare knowledge items and detect
    when new knowledge is semantically similar to existing knowledge.
    """

    CACHE_KEY_PREFIX = "knowledge_embed:"
    EMBEDDING_MODEL = "text-embedding-3-small"
    CACHE_TTL = 3600 * 24  # 24 hours for knowledge embeddings

    # Similarity thresholds
    VERY_SIMILAR = 0.90  # Almost identical
    SIMILAR = 0.80       # Same topic, different wording
    RELATED = 0.70       # Related topics
    DEFAULT_THRESHOLD = 0.80

    def __init__(self):
        self._embedding_service = None

    @property
    def embedding_service(self):
        """Session 744: Lazy-load centralized EmbeddingService for tracked embedding calls."""
        if self._embedding_service is None:
            self._embedding_service = get_embedding_service()
        return self._embedding_service

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using centralized EmbeddingService."""
        try:
            # Session 744: Use centralized service for tracking
            result = self.embedding_service.create_embedding(
                text=text[:4000],  # Truncate to avoid token limits
                model=self.EMBEDDING_MODEL,
                agent_name='KnowledgeSimilarityService'
            )
            return result.embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    def _get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache or generate new one."""
        # Create cache key from text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()[:16]
        cache_key = f"{self.CACHE_KEY_PREFIX}{text_hash}"

        # Check cache
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        # Generate new embedding
        embedding = self._generate_embedding(text)
        if embedding:
            cache.set(cache_key, embedding, self.CACHE_TTL)

        return embedding

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a_arr = np.array(a)
        b_arr = np.array(b)
        norm_a = np.linalg.norm(a_arr)
        norm_b = np.linalg.norm(b_arr)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a_arr, b_arr) / (norm_a * norm_b))

    def _build_knowledge_text(self, title: str, summary: str = None) -> str:
        """Build searchable text from knowledge fields."""
        parts = [f"Title: {title}"]
        if summary:
            parts.append(f"Summary: {summary[:500]}")
        return "\n".join(parts)

    def is_semantically_similar(
        self,
        agent,
        title: str,
        summary: str = None,
        knowledge_type: str = None,
        threshold: float = None
    ) -> SimilarityResult:
        """
        Check if knowledge is semantically similar to agent's existing knowledge.

        Args:
            agent: Agent model instance
            title: Title of the knowledge to check
            summary: Optional summary text
            knowledge_type: Optional filter by knowledge type
            threshold: Similarity threshold (default 0.80)

        Returns:
            SimilarityResult with is_similar flag and details
        """
        if threshold is None:
            threshold = self.DEFAULT_THRESHOLD

        # Build text for the new knowledge
        new_text = self._build_knowledge_text(title, summary)
        new_embedding = self._get_cached_embedding(new_text)

        if not new_embedding:
            # Fall back to title matching if embeddings unavailable
            return SimilarityResult(
                is_similar=False,
                similarity_score=0.0,
                matching_knowledge_id=None,
                matching_knowledge_title=None,
                reason="Embedding generation failed, using fallback"
            )

        # Get agent's existing knowledge
        from core.models_unified_system import AgentKnowledgeSource

        queryset = AgentKnowledgeSource.objects.filter(
            agent=agent,
            is_active=True
        )
        if knowledge_type:
            queryset = queryset.filter(knowledge_type=knowledge_type)

        # Check similarity against each existing knowledge
        best_match = None
        best_score = 0.0

        for knowledge in queryset[:50]:  # Limit for performance
            existing_text = self._build_knowledge_text(
                knowledge.title or '',
                knowledge.summary or ''
            )
            existing_embedding = self._get_cached_embedding(existing_text)

            if not existing_embedding:
                continue

            score = self._cosine_similarity(new_embedding, existing_embedding)

            if score > best_score:
                best_score = score
                best_match = knowledge

        # Determine if similar
        is_similar = best_score >= threshold

        return SimilarityResult(
            is_similar=is_similar,
            similarity_score=round(best_score, 4),
            matching_knowledge_id=str(best_match.id) if best_match else None,
            matching_knowledge_title=best_match.title if best_match else None,
            reason=self._get_similarity_reason(best_score, threshold)
        )

    def _get_similarity_reason(self, score: float, threshold: float) -> str:
        """Get human-readable reason for similarity result."""
        if score >= self.VERY_SIMILAR:
            return f"Very similar (score={score:.2f} >= {self.VERY_SIMILAR})"
        elif score >= self.SIMILAR:
            return f"Similar (score={score:.2f} >= {self.SIMILAR})"
        elif score >= self.RELATED:
            return f"Related (score={score:.2f} >= {self.RELATED})"
        elif score >= threshold:
            return f"Above threshold (score={score:.2f} >= {threshold})"
        else:
            return f"Not similar (score={score:.2f} < {threshold})"

    def find_most_similar(
        self,
        agent,
        title: str,
        summary: str = None,
        knowledge_type: str = None,
        limit: int = 5
    ) -> List[Tuple[float, Any]]:
        """
        Find the most similar existing knowledge items.

        Args:
            agent: Agent model instance
            title: Title to compare
            summary: Optional summary
            knowledge_type: Optional filter
            limit: Maximum results

        Returns:
            List of (similarity_score, knowledge) tuples, sorted by score
        """
        from core.models_unified_system import AgentKnowledgeSource

        # Build text for the query
        query_text = self._build_knowledge_text(title, summary)
        query_embedding = self._get_cached_embedding(query_text)

        if not query_embedding:
            return []

        # Get agent's existing knowledge
        queryset = AgentKnowledgeSource.objects.filter(
            agent=agent,
            is_active=True
        )
        if knowledge_type:
            queryset = queryset.filter(knowledge_type=knowledge_type)

        results = []

        for knowledge in queryset[:100]:
            existing_text = self._build_knowledge_text(
                knowledge.title or '',
                knowledge.summary or ''
            )
            existing_embedding = self._get_cached_embedding(existing_text)

            if not existing_embedding:
                continue

            score = self._cosine_similarity(query_embedding, existing_embedding)
            results.append((round(score, 4), knowledge))

        # Sort by similarity score descending
        results.sort(key=lambda x: x[0], reverse=True)

        return results[:limit]

    def should_transfer_knowledge(
        self,
        student_agent,
        teacher_knowledge,
        threshold: float = None
    ) -> Tuple[bool, str]:
        """
        Determine if knowledge should be transferred to student.

        This is the main method used by the learning cycle.

        Args:
            student_agent: The agent receiving knowledge
            teacher_knowledge: AgentKnowledgeSource from teacher
            threshold: Similarity threshold

        Returns:
            Tuple of (should_transfer, reason)
        """
        if threshold is None:
            threshold = self.DEFAULT_THRESHOLD

        result = self.is_semantically_similar(
            agent=student_agent,
            title=teacher_knowledge.title or '',
            summary=teacher_knowledge.summary or '',
            knowledge_type=teacher_knowledge.knowledge_type,
            threshold=threshold
        )

        if result.is_similar:
            return False, f"Similar to existing: '{result.matching_knowledge_title}' ({result.reason})"
        else:
            return True, f"New knowledge ({result.reason})"

    def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics about the similarity service."""
        from core.models_unified_system import AgentKnowledgeSource

        total_knowledge = AgentKnowledgeSource.objects.filter(is_active=True).count()

        return {
            'total_active_knowledge': total_knowledge,
            'embedding_model': self.EMBEDDING_MODEL,
            'default_threshold': self.DEFAULT_THRESHOLD,
            'thresholds': {
                'very_similar': self.VERY_SIMILAR,
                'similar': self.SIMILAR,
                'related': self.RELATED,
            },
            'openai_available': HAS_OPENAI and self.client is not None,
        }


# Global instance
_similarity_service: Optional[KnowledgeSimilarityService] = None


def get_knowledge_similarity_service() -> KnowledgeSimilarityService:
    """Get the global knowledge similarity service instance."""
    global _similarity_service
    if _similarity_service is None:
        _similarity_service = KnowledgeSimilarityService()
    return _similarity_service
