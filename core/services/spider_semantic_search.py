"""
Spider Semantic Search Service
==============================

Session 293: Add semantic search to spider data.

This service enhances the SpiderIntelligenceService with embedding-based
semantic search, allowing more accurate matching of user queries to
relevant spider data.

Strategy:
- Generate and store embeddings in the SpiderData model
- Use semantic similarity to rank results
- Hybrid approach: combine semantic + keyword matching
- Celery task for background embedding generation

Usage:
    from core.services.spider_semantic_search import SpiderSemanticSearch

    search = SpiderSemanticSearch()
    results = search.semantic_search("AI writing tools for content creation", limit=10)

    # Backfill embeddings for existing data
    stats = search.backfill_embeddings(batch_size=100)
"""

import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import timedelta

import numpy as np
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

# Try to import OpenAI for embeddings
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    logger.warning("OpenAI not available for spider semantic search")


@dataclass
class SemanticSearchResult:
    """Result from semantic spider search."""
    title: str
    description: str
    url: str
    source: str
    similarity: float
    category: str
    found_at: str
    tags: List[str] = None


class SpiderSemanticSearch:
    """
    Semantic search across spider data using embeddings.

    Generates embeddings for spider data items and queries,
    then uses cosine similarity for ranking.
    """

    CACHE_KEY_PREFIX = "spider_semantic:"
    EMBEDDING_MODEL = "text-embedding-3-small"
    CACHE_TTL = 3600 * 6  # 6 hours for spider data embeddings

    def __init__(self):
        self._client = None

    @property
    def client(self):
        """Lazy-load OpenAI client."""
        if self._client is None and HAS_OPENAI:
            api_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY')
            if api_key:
                self._client = openai.OpenAI(api_key=api_key)
        return self._client

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using OpenAI."""
        if not self.client:
            return None

        try:
            response = self.client.embeddings.create(
                input=text[:8000],  # Truncate to avoid token limits
                model=self.EMBEDDING_MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None

    def _get_cached_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from cache or generate new one."""
        # Create cache key from text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
        cache_key = f"{self.CACHE_KEY_PREFIX}item:{text_hash}"

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

    def _build_item_text(self, item: Dict) -> str:
        """Build searchable text from a spider data item."""
        parts = []

        title = item.get('title') or item.get('name') or ''
        if title:
            parts.append(f"Title: {title}")

        description = item.get('description') or item.get('summary') or ''
        if description:
            parts.append(f"Description: {description[:500]}")

        tags = item.get('tags', [])
        if isinstance(tags, list) and tags:
            parts.append(f"Tags: {', '.join(tags[:10])}")
        elif isinstance(tags, str) and tags:
            parts.append(f"Tags: {tags}")

        category = item.get('category') or item.get('type') or ''
        if category:
            parts.append(f"Category: {category}")

        return "\n".join(parts)

    def semantic_search(
        self,
        query: str,
        category: str = None,
        hours: int = 72,
        limit: int = 20,
        min_similarity: float = 0.3
    ) -> List[SemanticSearchResult]:
        """
        Semantic search across spider data.

        Args:
            query: Search query
            category: Optional category filter (tech, financial, jobs, etc.)
            hours: Look back period
            limit: Maximum results
            min_similarity: Minimum similarity threshold

        Returns:
            List of SemanticSearchResult sorted by similarity
        """
        from core.models_unified_system import SpiderData
        from core.services.spider_intelligence import SpiderIntelligenceService

        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        if not query_embedding:
            logger.warning("Could not generate query embedding, falling back to keyword search")
            # Fall back to keyword search
            service = SpiderIntelligenceService()
            return self._convert_keyword_results(
                service.search_spider_data(query, category, hours, limit)
            )

        # Get spider data
        since = timezone.now() - timedelta(hours=hours)
        queryset = SpiderData.objects.filter(created_at__gte=since)

        if category:
            category_mappings = SpiderIntelligenceService.CATEGORY_MAPPINGS
            spider_names = category_mappings.get(category, [])
            if spider_names:
                queryset = queryset.filter(spider_name__in=spider_names)

        # Process items and calculate similarities
        results = []
        seen = set()

        for entry in queryset.order_by('-created_at'):
            if not entry.raw_data:
                continue

            items = entry.raw_data.get('items', [])
            for item in items:
                title = item.get('title', '') or item.get('name', '')
                if not title:
                    continue

                # Session 293: Get URL from either 'url' or 'link' field
                item_url = item.get('url') or item.get('link') or ''

                # Deduplicate
                item_key = f"{title}:{item_url}".lower()[:100]
                if item_key in seen:
                    continue
                seen.add(item_key)

                # Build item text and get/generate embedding
                item_text = self._build_item_text(item)

                # For performance, only generate embeddings for items with
                # keyword overlap (hybrid approach)
                if not self._has_keyword_overlap(query.lower(), item_text.lower()):
                    continue

                item_embedding = self._get_cached_embedding(item_text)
                if not item_embedding:
                    continue

                # Calculate similarity
                similarity = self._cosine_similarity(query_embedding, item_embedding)

                if similarity >= min_similarity:
                    results.append(SemanticSearchResult(
                        title=title,
                        description=(item.get('description') or item.get('snippet') or '')[:300],
                        url=item_url,
                        source=entry.spider_name,
                        similarity=round(similarity, 4),
                        category=entry.data_type,
                        found_at=entry.created_at.isoformat(),
                        tags=item.get('tags', []) if isinstance(item.get('tags'), list) else []
                    ))

        # Sort by similarity
        results.sort(key=lambda x: x.similarity, reverse=True)

        logger.info(f"Semantic spider search: query='{query[:50]}', results={len(results[:limit])}")
        return results[:limit]

    def _has_keyword_overlap(self, query: str, text: str, min_overlap: int = 1) -> bool:
        """Check if query has any keyword overlap with text."""
        # Common words to ignore
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                     'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who',
                     'this', 'that', 'these', 'those', 'my', 'your', 'our', 'their'}

        query_words = set(query.split()) - stopwords
        text_words = set(text.split()) - stopwords

        overlap = len(query_words & text_words)
        return overlap >= min_overlap

    def _convert_keyword_results(self, keyword_results: List[Dict]) -> List[SemanticSearchResult]:
        """Convert keyword search results to SemanticSearchResult format."""
        return [
            SemanticSearchResult(
                title=r.get('title', ''),
                description=r.get('description', ''),
                url=r.get('url', ''),
                source=r.get('source', ''),
                similarity=r.get('relevance', 0.5),  # Use relevance as similarity
                category=r.get('category', ''),
                found_at=r.get('found_at', ''),
                tags=[]
            )
            for r in keyword_results
        ]

    def get_related_content(
        self,
        content: str,
        hours: int = 72,
        limit: int = 5
    ) -> List[SemanticSearchResult]:
        """
        Find spider data related to given content.

        Useful for enriching agent responses with relevant data.

        Args:
            content: The content to find related data for
            hours: Look back period
            limit: Maximum results

        Returns:
            List of related spider data items
        """
        # Use first 200 chars as query
        query = content[:200]
        return self.semantic_search(query, hours=hours, limit=limit, min_similarity=0.4)

    def enhance_agent_context(
        self,
        query: str,
        max_items: int = 3,
        max_chars: int = 1000
    ) -> str:
        """
        Get relevant spider data as context for agent prompts.

        Args:
            query: The user's query
            max_items: Maximum items to include
            max_chars: Maximum total characters

        Returns:
            Formatted string with relevant spider data
        """
        results = self.semantic_search(query, limit=max_items, min_similarity=0.35)

        if not results:
            return ""

        lines = ["Relevant data from spider network:"]
        total_chars = len(lines[0])

        for result in results:
            item_line = f"- [{result.source}] {result.title}"
            if result.description:
                item_line += f": {result.description[:150]}..."

            if total_chars + len(item_line) > max_chars:
                break

            lines.append(item_line)
            total_chars += len(item_line)

        return "\n".join(lines) if len(lines) > 1 else ""

    # =========================================================================
    # Database Embedding Methods (Session 293)
    # =========================================================================

    def generate_entry_embedding(self, spider_data) -> bool:
        """
        Generate and store embedding for a SpiderData entry.

        Uses the model's get_searchable_text() method.

        Args:
            spider_data: SpiderData model instance

        Returns:
            True if embedding was generated and saved
        """
        text = spider_data.get_searchable_text()
        if not text:
            return False

        embedding = self._generate_embedding(text)
        if embedding:
            spider_data.embedding = embedding
            spider_data.embedding_text = text[:1000]  # Store truncated for debugging
            spider_data.save(update_fields=['embedding', 'embedding_text'])
            return True

        return False

    def backfill_embeddings(self, batch_size: int = 100, hours: int = 168) -> Dict[str, int]:
        """
        Generate embeddings for SpiderData entries that don't have them.

        Session 394: Improved to skip already-marked empty entries and use larger batches.

        Args:
            batch_size: Number of entries to process (default 100)
            hours: Only process entries from last N hours (default 7 days)

        Returns:
            Dict with processing stats
        """
        from core.models_unified_system import SpiderData

        since = timezone.now() - timedelta(hours=hours)

        # Find entries without embeddings
        # Session 394: Also exclude entries marked as empty (embedding=[])
        entries = SpiderData.objects.filter(
            created_at__gte=since,
            embedding__isnull=True  # Only NULL, not empty list
        ).order_by('-created_at')[:batch_size]

        stats = {'processed': 0, 'succeeded': 0, 'failed': 0, 'skipped': 0, 'marked_empty': 0}

        for entry in entries:
            stats['processed'] += 1

            # Skip entries with no items
            if not entry.raw_data or not entry.raw_data.get('items'):
                stats['skipped'] += 1
                # Session 394: Mark as empty so we don't reprocess
                entry.embedding = []
                entry.embedding_text = "[NO_ITEMS]"
                entry.save(update_fields=['embedding', 'embedding_text'])
                stats['marked_empty'] += 1
                continue

            if self.generate_entry_embedding(entry):
                stats['succeeded'] += 1
            else:
                stats['failed'] += 1

        logger.info(f"Spider embedding backfill: {stats}")
        return stats

    def semantic_search_with_db_embeddings(
        self,
        query: str,
        category: str = None,
        hours: int = 72,
        limit: int = 20,
        min_similarity: float = 0.3
    ) -> List[SemanticSearchResult]:
        """
        Semantic search using database-stored embeddings.

        Faster than on-the-fly embedding generation because embeddings
        are pre-computed and stored in the database.

        Falls back to regular semantic_search if no DB embeddings found.
        """
        from core.models_unified_system import SpiderData
        from core.services.spider_intelligence import SpiderIntelligenceService

        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        if not query_embedding:
            logger.warning("Could not generate query embedding")
            return []

        # Get spider data with embeddings
        since = timezone.now() - timedelta(hours=hours)
        queryset = SpiderData.objects.filter(
            created_at__gte=since,
            embedding__isnull=False
        )

        if category:
            category_mappings = SpiderIntelligenceService.CATEGORY_MAPPINGS
            spider_names = category_mappings.get(category, [])
            if spider_names:
                queryset = queryset.filter(spider_name__in=spider_names)

        entries = list(queryset.order_by('-created_at')[:500])  # Limit for performance

        if not entries:
            # Session 468: Do NOT fall back to slow on-the-fly embedding generation
            # This was causing 10+ minute delays in agent execution
            # Instead, return empty results - agents have other knowledge sources
            logger.info("No DB embeddings found, returning empty results (no fallback)")
            return []

        # Calculate similarities
        results = []
        seen = set()

        for entry in entries:
            similarity = self._cosine_similarity(query_embedding, entry.embedding)

            if similarity < min_similarity:
                continue

            # Extract top items from this entry
            items = entry.raw_data.get('items', [])[:5]
            for item in items:
                title = item.get('title', '') or item.get('name', '')
                if not title:
                    continue

                # Session 293: Get URL from either 'url' or 'link' field
                item_url = item.get('url') or item.get('link') or ''

                # Deduplicate
                item_key = f"{title}:{item_url}".lower()[:100]
                if item_key in seen:
                    continue
                seen.add(item_key)

                results.append(SemanticSearchResult(
                    title=title,
                    description=(item.get('description') or item.get('snippet') or '')[:300],
                    url=item_url,
                    source=entry.spider_name,
                    similarity=round(similarity, 4),
                    category=entry.data_type,
                    found_at=entry.created_at.isoformat(),
                    tags=item.get('tags', []) if isinstance(item.get('tags'), list) else []
                ))

        # Sort by similarity
        results.sort(key=lambda x: x.similarity, reverse=True)

        logger.info(f"DB semantic search: query='{query[:50]}', entries_checked={len(entries)}, results={len(results[:limit])}")
        return results[:limit]

    def get_embedding_stats(self) -> Dict[str, Any]:
        """
        Get statistics about spider data embeddings.

        Session 394: Updated to distinguish between:
        - with_embedding: Has actual embedding vector (searchable)
        - marked_empty: Has empty list [] (no content to embed)
        - pending: Has NULL (needs processing)
        """
        from core.models_unified_system import SpiderData

        total = SpiderData.objects.count()

        # Count entries with actual embeddings (not empty list)
        # PostgreSQL: embedding is not null AND embedding != '{}'
        with_embedding = 0
        marked_empty = 0
        pending = 0

        # Sample to count - for large datasets this is more efficient
        sample_size = min(total, 5000)
        for entry in SpiderData.objects.order_by('-created_at')[:sample_size]:
            if entry.embedding is None:
                pending += 1
            elif entry.embedding == [] or (isinstance(entry.embedding, list) and len(entry.embedding) == 0):
                marked_empty += 1
            else:
                with_embedding += 1

        # Extrapolate if sampling
        if sample_size < total:
            ratio = total / sample_size
            with_embedding = int(with_embedding * ratio)
            marked_empty = int(marked_empty * ratio)
            pending = int(pending * ratio)

        # Recent stats (last 24 hours)
        since = timezone.now() - timedelta(hours=24)
        recent_total = SpiderData.objects.filter(created_at__gte=since).count()
        recent_with = 0
        for entry in SpiderData.objects.filter(created_at__gte=since):
            if entry.embedding and len(entry.embedding) > 0:
                recent_with += 1

        searchable = with_embedding  # Only actual embeddings are searchable

        return {
            'total_entries': total,
            'with_embedding': with_embedding,
            'marked_empty': marked_empty,
            'pending': pending,
            'searchable': searchable,
            'coverage_percent': round(searchable / total * 100, 1) if total > 0 else 0,
            'recent_24h': {
                'total': recent_total,
                'with_embedding': recent_with,
            }
        }


# Global instance
_spider_search: Optional[SpiderSemanticSearch] = None


def get_spider_semantic_search() -> SpiderSemanticSearch:
    """Get the global spider semantic search instance."""
    global _spider_search
    if _spider_search is None:
        _spider_search = SpiderSemanticSearch()
    return _spider_search
