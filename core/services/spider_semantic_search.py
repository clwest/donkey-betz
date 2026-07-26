"""
Spider Semantic Search Service
==============================

Session 293: Add semantic search to spider data.

This service enhances the SpiderIntelligenceService with embedding-based
semantic search, allowing more accurate matching of user queries to
relevant spider data.

Strategy:
- Generate and store embeddings in the LegacySpiderData model
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
from typing import Any, Dict, FrozenSet, List, Optional
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
        from core.models_unified_system import LegacySpiderData
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
        queryset = LegacySpiderData.objects.filter(created_at__gte=since)

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
        Generate and store embedding for a LegacySpiderData entry.

        Uses the model's get_searchable_text() method.

        Args:
            spider_data: LegacySpiderData model instance
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

    def backfill_embeddings(self, batch_size: int = 50, hours: int = None) -> Dict[str, int]:
        """
        Generate embeddings for LegacySpiderData entries that don't have them.

        Session 394: Improved to skip already-marked empty entries and use larger batches.
        Session triage (Apr 2026): Removed default hours=168 window that excluded
        86k+ historical records. After triage_spider_embeddings deduped the backlog,
        the remaining records are all worth embedding regardless of age.
        Session 1083 (Rigby audit): Reduced default batch_size 100→50 after
        observing 1.37GB memory spike per run in celery telemetry
        (start=669MB, end=2042MB). Only load id + raw_data + embedding_text
        columns via .only() so Django doesn't prefetch every LegacySpiderData
        field into memory. Beat runs this every 15 min so lower batches
        still drain the backlog — just with flatter memory profile.

        Args:
            batch_size: Number of entries to process (default 50)
            hours: Only process entries from last N hours (None = all)

        Returns:
            Dict with processing stats
        """
        from core.models_unified_system import LegacySpiderData

        # Find entries without embeddings
        # Session 394: Also exclude entries marked as empty
        # Session 782: Exclude by embedding_text instead of embedding=[] (pgvector error)
        # Session 1083: .only() to avoid loading every column (was pulling
        # large `processed_data` JSONB fields into memory unnecessarily)
        # S2975: Skip both NO_ITEMS and STALE_EMPTY_RAW sentinels via helper.
        from core.services.no_items_policy import BACKFILL_SKIP_SENTINELS

        qs = LegacySpiderData.objects.filter(
            embedding__isnull=True  # Only NULL, not empty list
        ).exclude(
            embedding_text__in=BACKFILL_SKIP_SENTINELS
        ).only('id', 'raw_data', 'embedding_text', 'created_at')
        if hours is not None:
            qs = qs.filter(created_at__gte=timezone.now() - timedelta(hours=hours))
        entries = list(qs.order_by('-created_at')[:batch_size])

        stats = {'processed': 0, 'succeeded': 0, 'failed': 0, 'skipped': 0, 'marked_empty': 0}

        # S2972: when we find no eligible rows, log the population split so
        # a manual trigger returning `{processed: 0}` is self-explanatory
        # in worker logs rather than looking like a no-op bug.
        if not entries:
            from django.db.models import Count, Q

            snapshot = LegacySpiderData.objects.aggregate(
                pending_null=Count('id', filter=Q(embedding__isnull=True)),
                triaged_no_items=Count(
                    'id',
                    filter=Q(embedding__isnull=True, embedding_text='[NO_ITEMS]'),
                ),
            )
            eligible = snapshot['pending_null'] - snapshot['triaged_no_items']
            # Numbers-only wording so future pipeline shifts don't invalidate
            # the message (per Rigby A2 SIGN feedback S2972).
            logger.info(
                "[backfill_embeddings] 0 eligible rows: "
                "pending_null=%s, triaged_no_items=%s, eligible=%s, "
                "batch_size=%s, hours=%s",
                snapshot['pending_null'],
                snapshot['triaged_no_items'],
                eligible,
                batch_size,
                hours,
            )
            return stats

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
        from core.models_unified_system import LegacySpiderData
        from core.services.spider_intelligence import SpiderIntelligenceService

        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        if not query_embedding:
            logger.warning("Could not generate query embedding")
            return []

        # Get spider data with embeddings
        # Session 736: Exclude entries marked as empty (embedding_text='[NO_ITEMS]')
        # S2975: Excludes both NO_ITEMS and STALE_EMPTY_RAW sentinels via helper.
        from core.services.no_items_policy import BACKFILL_SKIP_SENTINELS

        since = timezone.now() - timedelta(hours=hours)
        queryset = LegacySpiderData.objects.filter(
            created_at__gte=since,
            embedding__isnull=False
        ).exclude(
            embedding_text__in=BACKFILL_SKIP_SENTINELS
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

    NO_ITEMS_SENTINEL = '[NO_ITEMS]'
    STALE_EMPTY_SENTINEL = '[NO_ITEMS_STALE_EMPTY_RAW]'

    def get_embedding_stats(
        self,
        *,
        include_breakdown: bool = False,
        breakdown_window_hours: int = 24,
    ) -> Dict[str, Any]:
        """
        Statistics about spider-data embedding coverage.

        S2972 rework: drop the 5,000-row sampling extrapolation (accurate at
        pilot sizes, noisy past ~10k rows) and split "pending" into the two
        buckets that actually matter for backfill triage:

          - pending_eligible: embedding IS NULL AND embedding_text is not a skip sentinel
              → real backfill queue; backfill_embeddings will process these.
          - ineligible_empty: embedding IS NULL AND embedding_text == '[NO_ITEMS]'
              → already visited by backfill and found to have no embeddable
                content (aggregator rollups, metric-only responses, extractor
                misses). Currently the entire "pending" bucket at HEAD.
          - stale_empty_raw_data_total: embedding IS NULL AND embedding_text ==
              '[NO_ITEMS_STALE_EMPTY_RAW]' (S2975) — historical ghost rows
              (raw_data={} from a resolved ingest bug) flagged by
              cleanup_stale_no_items so they no longer distort the 30d
              NO_ITEMS rate while remaining observable.

        Also exposes 24h intake-quality breakdown so the UI can answer
        "is the backfill queue at 0 because the pipeline is healthy or
        because everything is going straight to [NO_ITEMS]?".

        Backward-compat: legacy fields (with_embedding, pending, marked_empty,
        searchable, coverage_percent, recent_24h.with_embedding) preserved
        with EXACT counts (no more sampling drift). Invariant asserted in
        test_embedding_coverage_pending_eligible_split:
            pending == pending_eligible + ineligible_empty + stale_empty_raw_data_total
        """
        from django.db.models import Count, Q

        from core.models_unified_system import LegacySpiderData
        from core.services.no_items_policy import (
            BACKFILL_SKIP_SENTINELS,
            EXCLUDED_DATA_TYPES,
            EXCLUDED_SPIDER_NAMES,
        )

        # Whole-table buckets — one round-trip via .aggregate().
        # Q(embedding__isnull=False) captures "has a vector" (any length);
        # pgvector stores real vectors as non-null arrays.
        # S2973: adds `policy_excluded_total` count so the UI can render
        # "N rows excluded by policy (non-content producers)" alongside
        # the coverage numbers without hardcoding the exclusion list.
        policy_filter = Q()
        if EXCLUDED_SPIDER_NAMES:
            policy_filter |= Q(spider_name__in=EXCLUDED_SPIDER_NAMES)
        if EXCLUDED_DATA_TYPES:
            policy_filter |= Q(data_type__in=EXCLUDED_DATA_TYPES)

        buckets = LegacySpiderData.objects.aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(embedding__isnull=False)),
            pending_eligible=Count(
                'id',
                filter=Q(embedding__isnull=True) & ~Q(embedding_text__in=BACKFILL_SKIP_SENTINELS),
            ),
            ineligible_empty=Count(
                'id',
                filter=Q(embedding__isnull=True, embedding_text=self.NO_ITEMS_SENTINEL),
            ),
            stale_empty_raw_data_total=Count(
                'id',
                filter=Q(embedding__isnull=True, embedding_text=self.STALE_EMPTY_SENTINEL),
            ),
            policy_excluded_total=(
                Count('id', filter=policy_filter)
                if (EXCLUDED_SPIDER_NAMES or EXCLUDED_DATA_TYPES)
                else Count('id', filter=Q(pk__isnull=True))  # always 0
            ),
        )
        total = buckets['total']
        present = buckets['present']
        pending_eligible = buckets['pending_eligible']
        ineligible_empty = buckets['ineligible_empty']
        stale_empty_raw_data_total = buckets['stale_empty_raw_data_total']
        policy_excluded_total = buckets['policy_excluded_total']
        # legacy semantics: `pending` = every NULL-embedding row (whether it
        # will be embedded, has been triaged, or is a stale ghost). Update the
        # invariant callers hold: pending = eligible + ineligible + stale.
        pending = pending_eligible + ineligible_empty + stale_empty_raw_data_total

        # Embeddable denominator = rows worth counting for coverage
        # (rules out [NO_ITEMS] rows so a healthy pipeline reads 100%).
        embeddable_total = present + pending_eligible
        embeddable_coverage_percent = (
            round(present / embeddable_total * 100, 1)
            if embeddable_total > 0 else 100.0
        )
        # Legacy coverage_percent = present / total (kept for existing callers).
        coverage_percent = round(present / total * 100, 1) if total > 0 else 0

        # Last 24h intake quality — same bucketing, filtered to fresh rows.
        # S2975: `still_pending` must exclude both sentinels (stale rows have
        # embedding__isnull=True but are not a real backfill queue).
        since = timezone.now() - timedelta(hours=24)
        recent = LegacySpiderData.objects.filter(created_at__gte=since).aggregate(
            total=Count('id'),
            embedded=Count('id', filter=Q(embedding__isnull=False)),
            marked_no_items=Count(
                'id',
                filter=Q(embedding__isnull=True, embedding_text=self.NO_ITEMS_SENTINEL),
            ),
            still_pending=Count(
                'id',
                filter=Q(embedding__isnull=True) & ~Q(embedding_text__in=BACKFILL_SKIP_SENTINELS),
            ),
        )
        recent_total = recent['total']
        recent_embedded = recent['embedded']
        recent_marked_no_items = recent['marked_no_items']
        recent_still_pending = recent['still_pending']
        no_items_rate = (
            round(recent_marked_no_items / recent_total * 100, 1)
            if recent_total > 0 else 0.0
        )

        payload: Dict[str, Any] = {
            # New (S2972) — accurate bucket split.
            'total': total,
            'present': present,
            'pending_eligible': pending_eligible,
            'ineligible_empty': ineligible_empty,
            'embeddable_total': embeddable_total,
            'embeddable_coverage_percent': embeddable_coverage_percent,
            # New (S2973) — policy-exclusion context (denominator hint, not a
            # separate percent — see docs in core/services/no_items_policy.py).
            'policy_excluded_total': policy_excluded_total,
            # New (S2975) — historical ghost rows flagged by
            # cleanup_stale_no_items. Observable but not counted as NO_ITEMS.
            'stale_empty_raw_data_total': stale_empty_raw_data_total,
            # Legacy — same values, kept for backward compat.
            'total_entries': total,
            'with_embedding': present,
            'marked_empty': 0,  # empty-vector representation superseded by [NO_ITEMS]
            'pending': pending,
            'searchable': present,
            'coverage_percent': coverage_percent,
            'recent_24h': {
                # New (S2972).
                'total': recent_total,
                'embedded': recent_embedded,
                'marked_no_items': recent_marked_no_items,
                'still_pending': recent_still_pending,
                'no_items_rate': no_items_rate,
                # Legacy alias.
                'with_embedding': recent_embedded,
            },
        }

        if include_breakdown:
            payload['no_items_breakdown'] = self._get_no_items_breakdown(
                window_hours=breakdown_window_hours,
                excluded_spider_names=EXCLUDED_SPIDER_NAMES,
                excluded_data_types=EXCLUDED_DATA_TYPES,
            )
        return payload

    def _get_no_items_breakdown(
        self,
        *,
        window_hours: int,
        excluded_spider_names: FrozenSet[str],
        excluded_data_types: FrozenSet[str],
    ) -> Dict[str, Any]:
        """S2973: top NO_ITEMS producers within a rolling window.

        Returns top 10 by spider_name and top 10 by data_type, plus the
        window's total-vs-NO_ITEMS numbers, plus the currently-active
        policy lists (so the UI can render "Policy excludes: X, Y" without
        hardcoding). Direct COUNT queries — no sampling.
        """
        from django.db.models import Count, Q

        from core.models_unified_system import LegacySpiderData

        since = timezone.now() - timedelta(hours=window_hours)
        window_qs = LegacySpiderData.objects.filter(created_at__gte=since)
        no_items_qs = window_qs.filter(embedding_text=self.NO_ITEMS_SENTINEL)

        window_totals = window_qs.aggregate(
            total_rows=Count('id'),
            no_items_total=Count(
                'id', filter=Q(embedding_text=self.NO_ITEMS_SENTINEL),
            ),
            # S2975: observable stale-ghost bucket in the same window so
            # dashboards can render "N historical artifacts (not counted as
            # NO_ITEMS)" alongside the active rate.
            stale_empty_raw_data_total=Count(
                'id', filter=Q(embedding_text=self.STALE_EMPTY_SENTINEL),
            ),
        )
        no_items_by_spider = list(
            no_items_qs.values('spider_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        no_items_by_data_type = list(
            no_items_qs.values('data_type')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
        window_rate = (
            round(
                window_totals['no_items_total'] / window_totals['total_rows'] * 100, 1
            )
            if window_totals['total_rows'] > 0 else 0.0
        )
        return {
            'window_hours': window_hours,
            'total_rows': window_totals['total_rows'],
            'no_items_total': window_totals['no_items_total'],
            'no_items_rate': window_rate,
            'stale_empty_raw_data_total': window_totals['stale_empty_raw_data_total'],
            'by_spider': no_items_by_spider,
            'by_data_type': no_items_by_data_type,
            # Policy reflection so the UI can render "Excludes: X, Y" without
            # hardcoding (Rigby T1 refinement, S2973).
            'excluded_spider_names': sorted(excluded_spider_names),
            'excluded_data_types': sorted(excluded_data_types),
        }


# Global instance
_spider_search: Optional[SpiderSemanticSearch] = None


def get_spider_semantic_search() -> SpiderSemanticSearch:
    """Get the global spider semantic search instance."""
    global _spider_search
    if _spider_search is None:
        _spider_search = SpiderSemanticSearch()
    return _spider_search
