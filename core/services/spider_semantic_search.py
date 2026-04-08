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
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import timedelta

import numpy as np
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)

# Session 744: Use centralized EmbeddingService for all embedding calls
from core.services.embedding_service import get_embedding_service

HAS_OPENAI = True  # EmbeddingService handles this internally


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
        self._embedding_service = None

    @property
    def embedding_service(self):
        """Lazy-load centralized EmbeddingService."""
        if self._embedding_service is None:
            self._embedding_service = get_embedding_service()
        return self._embedding_service

    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using centralized EmbeddingService."""
        try:
            # Session 744: Use centralized service for tracking
            result = self.embedding_service.create_embedding(
                text=text[:8000],  # Truncate to avoid token limits
                model=self.EMBEDDING_MODEL,
                agent_name='SpiderSemanticSearch'
            )
            return result.embedding
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

    def _cosine_similarity(self, a, b) -> float:
        """Calculate cosine similarity between two vectors."""
        # Session 736: Guard against empty embeddings
        # pgvector returns numpy arrays, so use 'is None' and len() checks
        if a is None or b is None:
            return 0.0

        # Convert to numpy if needed
        a_arr = np.array(a) if not isinstance(a, np.ndarray) else a
        b_arr = np.array(b) if not isinstance(b, np.ndarray) else b

        # Check for empty arrays
        if a_arr.size == 0 or b_arr.size == 0:
            return 0.0

        # Check for shape mismatch
        if a_arr.shape != b_arr.shape:
            return 0.0

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

        # Session 814: Limit entries scanned to prevent slow queries
        # This prevents 10+ minute query times when generating embeddings on-the-fly
        MAX_ENTRIES_TO_SCAN = 200
        for entry in queryset.order_by('-created_at')[:MAX_ENTRIES_TO_SCAN]:
            if not entry.raw_data:
                continue

            # Session 534: Handle raw_data as string (JSON) or dict
            raw_data = entry.raw_data
            if isinstance(raw_data, str):
                try:
                    import json
                    raw_data = json.loads(raw_data)
                except (json.JSONDecodeError, TypeError):
                    continue

            # Get items list, or treat single item as list (from news spiders)
            items = raw_data.get('items', []) if isinstance(raw_data, dict) else []
            if not items and isinstance(raw_data, dict) and raw_data.get('title'):
                # Single item stored directly (not wrapped in 'items')
                items = [raw_data]

            # Session 534: Flatten nested structures (VentureBeat, Kickstarter, etc.)
            flat_items = []
            for item in items[:10]:
                if not isinstance(item, dict):
                    continue
                if 'articles' in item:
                    flat_items.extend(item.get('articles', [])[:10])
                elif 'items' in item and isinstance(item.get('items'), list):
                    flat_items.extend(item.get('items', [])[:10])
                elif 'by_category' in item:
                    for cat_items in item.get('by_category', {}).values():
                        if isinstance(cat_items, list):
                            flat_items.extend(cat_items[:3])
                else:
                    flat_items.append(item)

            for item in flat_items:
                if not isinstance(item, dict):
                    continue
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

    def generate_entry_embedding(self, spider_data, mark_empty: bool = True) -> str:
        """
        Generate and store embedding for a SpiderData entry.

        Uses the model's get_searchable_text() method.

        Args:
            spider_data: SpiderData model instance
            mark_empty: If True, mark entries with no text as [NO_ITEMS]

        Returns:
            'success' if embedding was generated
            'no_text' if no searchable text (marked as [NO_ITEMS] if mark_empty=True)
            'failed' if embedding generation failed
        """
        text = spider_data.get_searchable_text()
        if not text:
            # Session 792: Mark as empty so we don't retry forever
            if mark_empty:
                spider_data.embedding_text = "[NO_ITEMS]"
                spider_data.save(update_fields=['embedding_text'])
            return 'no_text'

        embedding = self._generate_embedding(text)
        if embedding:
            spider_data.embedding = embedding
            spider_data.embedding_text = text[:1000]  # Store truncated for debugging
            spider_data.save(update_fields=['embedding', 'embedding_text'])
            return 'success'

        return 'failed'

    def backfill_embeddings(self, batch_size: int = 100, hours: int = None) -> Dict[str, int]:
        """
        Generate embeddings for SpiderData entries that don't have them.

        Session 394: Improved to skip already-marked empty entries and use larger batches.
        Session triage (Apr 2026): Removed default hours=168 window that excluded
        86k+ historical records. After triage_spider_embeddings deduped the backlog,
        the remaining records are all worth embedding regardless of age.

        Args:
            batch_size: Number of entries to process (default 100)
            hours: Only process entries from last N hours (None = all)

        Returns:
            Dict with processing stats
        """
        from core.models_unified_system import SpiderData

        # Find entries without embeddings
        # Session 394: Also exclude entries marked as empty
        # Session 782: Exclude by embedding_text instead of embedding=[] (pgvector error)
        qs = SpiderData.objects.filter(
            embedding__isnull=True  # Only NULL, not empty list
        ).exclude(
            embedding_text='[NO_ITEMS]'  # Skip already-marked empty entries
        )
        if hours is not None:
            qs = qs.filter(created_at__gte=timezone.now() - timedelta(hours=hours))
        entries = qs.order_by('-created_at')[:batch_size]

        stats = {'processed': 0, 'succeeded': 0, 'failed': 0, 'skipped': 0, 'marked_empty': 0}

        # Phase 1: Collect texts, skip empties
        entries_with_text = []  # (entry, text) pairs
        for entry in entries:
            stats['processed'] += 1

            # Session 534: Handle raw_data as string (JSON) or dict
            raw_data = entry.raw_data
            if isinstance(raw_data, str):
                try:
                    import json
                    raw_data = json.loads(raw_data)
                except (json.JSONDecodeError, TypeError):
                    raw_data = {}

            # Get items list, or treat single item as list (from news spiders)
            items = raw_data.get('items', []) if isinstance(raw_data, dict) else []
            if not items and isinstance(raw_data, dict) and raw_data.get('title'):
                items = [raw_data]

            # Skip entries with no items
            if not items:
                stats['skipped'] += 1
                entry.embedding_text = "[NO_ITEMS]"
                entry.save(update_fields=['embedding_text'])
                stats['marked_empty'] += 1
                continue

            text = entry.get_searchable_text()
            if not text:
                stats['skipped'] += 1
                stats['marked_empty'] += 1
                entry.embedding_text = "[NO_ITEMS]"
                entry.save(update_fields=['embedding_text'])
                continue

            entries_with_text.append((entry, text[:8000]))

        if not entries_with_text:
            logger.info(f"Spider embedding backfill: {stats}")
            return stats

        # Phase 2: Batch embed all texts in one API call (fixes 3.7GB memory spike)
        texts = [t for _, t in entries_with_text]
        try:
            embeddings = self.embedding_service.get_embeddings_sync(texts)
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            stats['failed'] += len(entries_with_text)
            return stats

        # Phase 3: Save results
        for i, (entry, text) in enumerate(entries_with_text):
            embedding = embeddings[i] if i < len(embeddings) else None
            if embedding:
                entry.embedding = embedding
                entry.embedding_text = text[:1000]
                entry.save(update_fields=['embedding', 'embedding_text'])
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
        # Session 736: Exclude entries marked as empty (embedding_text='[NO_ITEMS]')
        since = timezone.now() - timedelta(hours=hours)
        queryset = SpiderData.objects.filter(
            created_at__gte=since,
            embedding__isnull=False
        ).exclude(
            embedding_text='[NO_ITEMS]'
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

            # Session 534: Handle raw_data as string (JSON) or dict
            raw_data = entry.raw_data
            if isinstance(raw_data, str):
                try:
                    import json
                    raw_data = json.loads(raw_data)
                except (json.JSONDecodeError, TypeError):
                    continue

            # Get items list, or treat single item as list (from news spiders)
            items = raw_data.get('items', []) if isinstance(raw_data, dict) else []
            if not items and isinstance(raw_data, dict) and raw_data.get('title'):
                items = [raw_data]

            # Session 534: Flatten nested structures (VentureBeat, Kickstarter, etc.)
            flat_items = []
            for item in items[:5]:
                if not isinstance(item, dict):
                    continue
                # VentureBeat: articles key
                if 'articles' in item:
                    flat_items.extend(item.get('articles', [])[:10])
                # Kickstarter: nested items key
                elif 'items' in item and isinstance(item.get('items'), list):
                    flat_items.extend(item.get('items', [])[:10])
                # Kickstarter: by_category dict
                elif 'by_category' in item:
                    for cat_items in item.get('by_category', {}).values():
                        if isinstance(cat_items, list):
                            flat_items.extend(cat_items[:3])
                else:
                    flat_items.append(item)

            for item in flat_items[:10]:
                if not isinstance(item, dict):
                    continue
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
        # Session 736: pgvector returns numpy arrays, check size properly
        sample_size = min(total, 5000)
        for entry in SpiderData.objects.order_by('-created_at')[:sample_size]:
            if entry.embedding is None:
                pending += 1
            elif len(entry.embedding) == 0:
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
            # Session 736: pgvector returns numpy arrays, not lists
            # Must use 'is not None' instead of truth check on numpy arrays
            if entry.embedding is not None and len(entry.embedding) > 0:
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
