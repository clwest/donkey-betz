"""
Session 616: Spider Item-Level Deduplication Service

Ensures spider data quality by deduplicating at the item level using content hashing.
This prevents storing the same news article, market, or event multiple times.

Usage:
    from core.services.spider_deduplication import SpiderDeduplicationService

    dedup = SpiderDeduplicationService()
    unique_items = dedup.deduplicate_items(spider_name, items)
    # unique_items contains only items not seen in the last N days
"""

import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import timedelta
from django.utils import timezone
from django.db import models

logger = logging.getLogger(__name__)


class SpiderDeduplicationService:
    """
    Item-level deduplication for spider data.

    Uses content hashing to identify duplicate items across spider runs.
    Tracks seen items in SpiderItemHash model to prevent re-ingestion.
    """

    # How long to remember seen items (days)
    # Was 7 days — but RSS feeds keep items for weeks, so items got re-ingested
    # after the 7-day hash cleanup. 90 days prevents the cycle.
    DEFAULT_LOOKBACK_DAYS = 90

    # Fields to use for generating item hash, in priority order
    HASH_FIELDS_BY_TYPE = {
        # URL-based sources (articles, news)
        'url_based': ['url', 'link', 'href'],

        # Sports/betting (use event identifiers)
        'sports': ['event_id', 'game_id', 'match_id'],

        # Markets/trading (use ticker/symbol)
        'markets': ['ticker', 'symbol', 'market_id'],

        # Fallback: title + source
        'fallback': ['title', 'name', 'headline'],
    }

    def __init__(self, lookback_days: int = None):
        self.lookback_days = lookback_days or self.DEFAULT_LOOKBACK_DAYS
        self.logger = logging.getLogger(f"{__name__}.SpiderDeduplicationService")

    def deduplicate_items(
        self,
        spider_name: str,
        items: List[Dict[str, Any]],
        data_type: str = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """
        Filter items to only include unique (not previously seen) items.

        Args:
            spider_name: Name of the spider
            items: List of item dicts from spider
            data_type: Optional data type hint for better hashing

        Returns:
            Tuple of (unique_items, stats_dict)
            stats_dict contains: total, unique, duplicates, new_hashes
        """
        from core.models_unified_system import SpiderItemHash

        if not items:
            return [], {'total': 0, 'unique': 0, 'duplicates': 0, 'new_hashes': 0}

        stats = {
            'total': len(items),
            'unique': 0,
            'duplicates': 0,
            'new_hashes': 0,
        }

        # Get existing hashes for this spider within lookback period
        cutoff = timezone.now() - timedelta(days=self.lookback_days)
        existing_hashes = set(
            SpiderItemHash.objects.filter(
                spider_name=spider_name,
                created_at__gte=cutoff
            ).values_list('content_hash', flat=True)
        )

        unique_items = []
        new_hashes = []

        for item in items:
            content_hash = self._generate_hash(spider_name, item, data_type)

            if content_hash in existing_hashes:
                stats['duplicates'] += 1
                continue

            # New unique item
            unique_items.append(item)
            existing_hashes.add(content_hash)  # Prevent within-batch duplicates

            # Prepare hash record for bulk create
            new_hashes.append(SpiderItemHash(
                spider_name=spider_name,
                content_hash=content_hash,
                item_title=self._get_item_title(item)[:200],
                data_type=data_type or 'unknown',
            ))

        stats['unique'] = len(unique_items)
        stats['new_hashes'] = len(new_hashes)

        # Bulk create hash records
        if new_hashes:
            try:
                SpiderItemHash.objects.bulk_create(new_hashes, ignore_conflicts=True)
            except Exception as e:
                self.logger.error(f"Error saving item hashes: {e}")

        self.logger.info(
            f"Dedup {spider_name}: {stats['total']} items -> "
            f"{stats['unique']} unique, {stats['duplicates']} duplicates"
        )

        return unique_items, stats

    def _generate_hash(
        self,
        spider_name: str,
        item: Dict[str, Any],
        data_type: str = None
    ) -> str:
        """
        Generate a content hash for an item.

        Uses the most reliable unique identifier available:
        1. URL/link for articles
        2. Event ID for sports
        3. Ticker for markets
        4. Title + spider as fallback
        """
        hash_content = None

        # Try URL-based first (most reliable)
        for field in self.HASH_FIELDS_BY_TYPE['url_based']:
            if item.get(field):
                hash_content = item[field]
                break

        # Try sports identifiers
        if not hash_content:
            for field in self.HASH_FIELDS_BY_TYPE['sports']:
                if item.get(field):
                    hash_content = f"{spider_name}:{item[field]}"
                    break

        # Try market identifiers
        if not hash_content:
            for field in self.HASH_FIELDS_BY_TYPE['markets']:
                if item.get(field):
                    hash_content = f"{spider_name}:{item[field]}"
                    break

        # Fallback to title
        if not hash_content:
            for field in self.HASH_FIELDS_BY_TYPE['fallback']:
                if item.get(field):
                    # Include spider name to avoid cross-spider collisions
                    hash_content = f"{spider_name}:{item[field]}"
                    break

        # Last resort: hash entire item
        if not hash_content:
            import json
            hash_content = f"{spider_name}:{json.dumps(item, sort_keys=True)}"

        # Generate SHA256 hash (truncated for storage efficiency)
        return hashlib.sha256(hash_content.encode('utf-8')).hexdigest()[:32]

    def _get_item_title(self, item: Dict[str, Any]) -> str:
        """Extract a human-readable title from item for debugging."""
        for field in ['title', 'name', 'headline', 'ticker', 'event_id']:
            if item.get(field):
                return str(item[field])
        return 'Unknown'

    def cleanup_old_hashes(self, days_to_keep: int = None) -> int:
        """
        Remove hash records older than specified days.

        Returns number of records deleted.
        """
        from core.models_unified_system import SpiderItemHash

        days = days_to_keep or self.lookback_days
        cutoff = timezone.now() - timedelta(days=days)

        deleted, _ = SpiderItemHash.objects.filter(created_at__lt=cutoff).delete()

        self.logger.info(f"Cleaned up {deleted} old hash records (older than {days} days)")
        return deleted

    def get_dedup_stats(self, spider_name: str = None, hours: int = 24) -> Dict[str, Any]:
        """
        Get deduplication statistics.

        Returns stats about unique vs duplicate items processed.
        """
        from core.models_unified_system import SpiderItemHash

        cutoff = timezone.now() - timedelta(hours=hours)

        query = SpiderItemHash.objects.filter(created_at__gte=cutoff)
        if spider_name:
            query = query.filter(spider_name=spider_name)

        total_hashes = query.count()
        by_spider = query.values('spider_name').annotate(
            count=models.Count('id')
        ).order_by('-count')

        return {
            'period_hours': hours,
            'total_unique_items': total_hashes,
            'by_spider': list(by_spider),
        }


# Convenience function for use in tasks
def deduplicate_spider_items(
    spider_name: str,
    items: List[Dict[str, Any]],
    data_type: str = None
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    Convenience function to deduplicate spider items.

    Returns (unique_items, stats_dict)
    """
    service = SpiderDeduplicationService()
    return service.deduplicate_items(spider_name, items, data_type)
