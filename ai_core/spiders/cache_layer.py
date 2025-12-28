"""
Smart Cache Layer with Deduplication
Phase 4: Scale & Optimize - Efficient Data Storage

This module implements intelligent caching with content-based deduplication,
compression, and delta updates to handle massive data volumes efficiently.
"""

import logging
import hashlib
import json
import zlib
import pickle
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, field
from collections import OrderedDict
from django.core.cache import cache

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Individual cache entry with metadata"""
    key: str
    content_hash: str
    data: Any
    compressed_data: bytes
    original_size: int
    compressed_size: int
    created_at: datetime
    accessed_at: datetime
    access_count: int = 0
    ttl: int = 3600  # Time to live in seconds
    metadata: Dict = field(default_factory=dict)


class SmartCacheLayer:
    """
    Intelligent cache layer with deduplication, compression, and delta updates.
    Handles caching for 1,000+ spiders efficiently.
    """

    def __init__(self, max_size_mb: int = 1024, compression_level: int = 6):
        # Configuration
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.compression_level = compression_level
        self.dedup_enabled = True
        self.delta_updates_enabled = True

        # Storage
        self.cache_entries: OrderedDict[str, CacheEntry] = OrderedDict()
        self.content_hashes: Dict[str, str] = {}  # hash -> key mapping
        self.duplicate_count = 0
        self.current_size_bytes = 0

        # Delta tracking
        self.previous_versions: Dict[str, Any] = {}  # key -> previous data
        self.delta_cache: Dict[str, List] = {}  # key -> list of deltas

        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'duplicates_prevented': 0,
            'bytes_saved': 0,
            'compression_ratio': 1.0,
            'delta_updates': 0,
            'evictions': 0
        }

        # Bloom filter for quick existence checks (simulated)
        self.bloom_filter: Set[str] = set()

        logger.info(f"📦 Smart cache initialized: {max_size_mb}MB max size")

    def _generate_content_hash(self, data: Any) -> str:
        """Generate content-based hash for deduplication"""
        if isinstance(data, dict):
            # Sort keys for consistent hashing
            data_str = json.dumps(data, sort_keys=True, default=str)
        else:
            data_str = str(data)

        return hashlib.sha256(data_str.encode()).hexdigest()

    def _compress_data(self, data: Any) -> Tuple[bytes, int, int]:
        """
        Compress data using zlib

        Returns:
            Tuple of (compressed_data, original_size, compressed_size)
        """
        # Serialize data
        if isinstance(data, (dict, list)):
            serialized = json.dumps(data, default=str).encode()
        else:
            serialized = pickle.dumps(data)

        original_size = len(serialized)

        # Compress
        compressed = zlib.compress(serialized, level=self.compression_level)
        compressed_size = len(compressed)

        # Update compression ratio (prevent division by zero)
        if original_size > 0:
            self.stats['compression_ratio'] = compressed_size / original_size
        else:
            self.stats['compression_ratio'] = 1.0

        return compressed, original_size, compressed_size

    def _decompress_data(self, compressed_data: bytes, is_json: bool = True) -> Any:
        """Decompress data"""
        decompressed = zlib.decompress(compressed_data)

        if is_json:
            return json.loads(decompressed.decode())
        else:
            return pickle.loads(decompressed)

    async def get(self, key: str) -> Optional[Any]:
        """
        Get item from cache with deduplication check

        Args:
            key: Cache key

        Returns:
            Cached data or None
        """
        # Quick bloom filter check
        if key not in self.bloom_filter:
            self.stats['misses'] += 1
            return None

        # Check local cache
        if key in self.cache_entries:
            entry = self.cache_entries[key]

            # Check TTL
            if (datetime.now() - entry.created_at).total_seconds() > entry.ttl:
                await self.evict(key)
                self.stats['misses'] += 1
                return None

            # Update access info
            entry.accessed_at = datetime.now()
            entry.access_count += 1

            # Move to end (LRU)
            self.cache_entries.move_to_end(key)

            self.stats['hits'] += 1

            # Decompress and return
            return self._decompress_data(entry.compressed_data)

        # Check Django cache as fallback
        cached_data = cache.get(key)
        if cached_data:
            self.stats['hits'] += 1
            return cached_data

        self.stats['misses'] += 1
        return None

    async def set(self, key: str, data: Any, ttl: int = 3600) -> bool:
        """
        Set item in cache with deduplication

        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds

        Returns:
            True if cached successfully
        """
        # Generate content hash
        content_hash = self._generate_content_hash(data)

        # Check for duplicate content
        if self.dedup_enabled and content_hash in self.content_hashes:
            existing_key = self.content_hashes[content_hash]
            if existing_key != key:
                logger.debug(f"🔄 Duplicate detected: {key} -> {existing_key}")
                self.duplicate_count += 1
                self.stats['duplicates_prevented'] += 1

                # Point to existing entry instead of storing duplicate
                self.cache_entries[key] = self.cache_entries[existing_key]
                return True

        # Compress data
        compressed_data, original_size, compressed_size = self._compress_data(data)

        # Check if we need to evict entries
        if self.current_size_bytes + compressed_size > self.max_size_bytes:
            await self._evict_lru()

        # Create cache entry
        entry = CacheEntry(
            key=key,
            content_hash=content_hash,
            data=data,
            compressed_data=compressed_data,
            original_size=original_size,
            compressed_size=compressed_size,
            created_at=datetime.now(),
            accessed_at=datetime.now(),
            ttl=ttl
        )

        # Store entry
        self.cache_entries[key] = entry
        self.content_hashes[content_hash] = key
        self.bloom_filter.add(key)
        self.current_size_bytes += compressed_size

        # Update stats
        self.stats['bytes_saved'] += (original_size - compressed_size)

        # Store in Django cache as backup
        cache.set(key, data, ttl)

        # Track for delta updates
        if self.delta_updates_enabled and key in self.previous_versions:
            await self._store_delta(key, self.previous_versions[key], data)

        self.previous_versions[key] = data

        logger.debug(f"✅ Cached {key}: {original_size}→{compressed_size} bytes "
                    f"({self.stats['compression_ratio']:.2f}x compression)")

        return True

    async def _store_delta(self, key: str, old_data: Any, new_data: Any):
        """Store delta between old and new data"""
        try:
            if isinstance(old_data, dict) and isinstance(new_data, dict):
                # Calculate dict delta
                delta = self._calculate_dict_delta(old_data, new_data)

                if key not in self.delta_cache:
                    self.delta_cache[key] = []

                self.delta_cache[key].append({
                    'timestamp': datetime.now().isoformat(),
                    'delta': delta
                })

                # Keep only last 10 deltas
                if len(self.delta_cache[key]) > 10:
                    self.delta_cache[key] = self.delta_cache[key][-10:]

                self.stats['delta_updates'] += 1
                logger.debug(f"📝 Stored delta for {key}")

        except Exception as e:
            logger.error(f"❌ Error calculating delta: {e}")

    def _calculate_dict_delta(self, old_dict: Dict, new_dict: Dict) -> Dict:
        """Calculate delta between two dictionaries"""
        delta = {
            'added': {},
            'modified': {},
            'removed': []
        }

        # Find added and modified keys
        for key, value in new_dict.items():
            if key not in old_dict:
                delta['added'][key] = value
            elif old_dict[key] != value:
                delta['modified'][key] = {
                    'old': old_dict[key],
                    'new': value
                }

        # Find removed keys
        for key in old_dict:
            if key not in new_dict:
                delta['removed'].append(key)

        return delta

    async def get_with_delta(self, key: str) -> Optional[Dict]:
        """Get item with delta history"""
        data = await self.get(key)

        if data and key in self.delta_cache:
            return {
                'current': data,
                'deltas': self.delta_cache[key]
            }

        return data

    async def update_partial(self, key: str, updates: Dict) -> bool:
        """
        Perform partial update on cached data

        Args:
            key: Cache key
            updates: Dictionary of updates to apply

        Returns:
            True if updated successfully
        """
        data = await self.get(key)

        if not data or not isinstance(data, dict):
            return False

        # Apply updates
        data.update(updates)

        # Re-cache with same TTL
        entry = self.cache_entries.get(key)
        ttl = entry.ttl if entry else 3600

        return await self.set(key, data, ttl)

    async def _evict_lru(self):
        """Evict least recently used entries"""
        evicted_count = 0
        target_size = self.max_size_bytes * 0.8  # Free up to 80% capacity

        while self.current_size_bytes > target_size and self.cache_entries:
            # Get least recently used (first item in OrderedDict)
            key = next(iter(self.cache_entries))
            await self.evict(key)
            evicted_count += 1

        logger.info(f"🗑️ Evicted {evicted_count} entries to free space")
        self.stats['evictions'] += evicted_count

    async def evict(self, key: str):
        """Evict a specific key from cache"""
        if key not in self.cache_entries:
            return

        entry = self.cache_entries[key]

        # Update size tracking
        self.current_size_bytes -= entry.compressed_size

        # Remove from all structures
        del self.cache_entries[key]
        self.bloom_filter.discard(key)

        # Remove content hash mapping
        if entry.content_hash in self.content_hashes:
            if self.content_hashes[entry.content_hash] == key:
                del self.content_hashes[entry.content_hash]

        # Remove from Django cache
        cache.delete(key)

        # Clean up delta cache
        if key in self.delta_cache:
            del self.delta_cache[key]

        if key in self.previous_versions:
            del self.previous_versions[key]

    async def bulk_set(self, items: Dict[str, Any], ttl: int = 3600) -> int:
        """
        Bulk set multiple items

        Args:
            items: Dictionary of key-value pairs
            ttl: Time to live

        Returns:
            Number of items cached
        """
        cached_count = 0

        for key, data in items.items():
            if await self.set(key, data, ttl):
                cached_count += 1

        logger.info(f"📦 Bulk cached {cached_count}/{len(items)} items")
        return cached_count

    async def bulk_get(self, keys: List[str]) -> Dict[str, Any]:
        """
        Bulk get multiple items

        Args:
            keys: List of keys to retrieve

        Returns:
            Dictionary of found key-value pairs
        """
        results = {}

        for key in keys:
            data = await self.get(key)
            if data is not None:
                results[key] = data

        return results

    def get_statistics(self) -> Dict:
        """Get cache statistics"""
        hit_rate = 0
        if self.stats['hits'] + self.stats['misses'] > 0:
            hit_rate = self.stats['hits'] / (self.stats['hits'] + self.stats['misses'])

        # Ensure max_size_bytes is not zero to prevent division by zero
        utilization = 0
        if self.max_size_bytes > 0:
            utilization = self.current_size_bytes / self.max_size_bytes * 100

        return {
            'entries': len(self.cache_entries),
            'size_mb': self.current_size_bytes / (1024 * 1024),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'utilization': utilization,
            'hit_rate': hit_rate * 100,
            'compression_ratio': self.stats.get('compression_ratio', 1.0),
            'duplicates_prevented': self.stats.get('duplicates_prevented', 0),
            'bytes_saved': self.stats.get('bytes_saved', 0),
            'delta_updates': self.stats.get('delta_updates', 0),
            'evictions': self.stats.get('evictions', 0),
            'stats': self.stats
        }

    async def clear(self):
        """Clear all cache entries"""
        logger.warning("🗑️ Clearing entire cache")

        self.cache_entries.clear()
        self.content_hashes.clear()
        self.bloom_filter.clear()
        self.previous_versions.clear()
        self.delta_cache.clear()
        self.current_size_bytes = 0
        self.duplicate_count = 0

        # Reset stats
        for key in self.stats:
            if isinstance(self.stats[key], (int, float)):
                self.stats[key] = 0
            if key == 'compression_ratio':
                self.stats[key] = 1.0

    async def cleanup_expired(self):
        """Clean up expired entries"""
        now = datetime.now()
        expired_keys = []

        for key, entry in self.cache_entries.items():
            if (now - entry.created_at).total_seconds() > entry.ttl:
                expired_keys.append(key)

        for key in expired_keys:
            await self.evict(key)

        if expired_keys:
            logger.info(f"🧹 Cleaned up {len(expired_keys)} expired entries")

        return len(expired_keys)

    def find_similar(self, data: Any, threshold: float = 0.9) -> List[str]:
        """
        Find similar cached items using content hashing

        Args:
            data: Data to compare
            threshold: Similarity threshold (0-1)

        Returns:
            List of similar cache keys
        """
        content_hash = self._generate_content_hash(data)
        similar_keys = []

        # Quick exact match
        if content_hash in self.content_hashes:
            return [self.content_hashes[content_hash]]

        # For more sophisticated similarity, would need to implement
        # fuzzy hashing or other similarity metrics
        # For now, return empty list for non-exact matches

        return similar_keys

    async def optimize(self):
        """Optimize cache by removing duplicates and compressing further"""
        logger.info("🔧 Optimizing cache...")

        # Clean up expired entries
        await self.cleanup_expired()

        # Re-compress entries with better compression if needed
        optimized_count = 0
        for key, entry in list(self.cache_entries.items()):
            # Calculate compression ratio
            compression_ratio = entry.compressed_size / max(entry.original_size, 1)

            if compression_ratio > 0.7:  # If not well compressed
                # Try higher compression
                compressed, _, new_size = self._compress_data(entry.data)
                if new_size < entry.compressed_size:
                    saved = entry.compressed_size - new_size
                    entry.compressed_data = compressed
                    entry.compressed_size = new_size
                    self.current_size_bytes -= saved
                    self.stats['bytes_saved'] += saved
                    optimized_count += 1

        logger.info(f"✅ Optimization complete: {optimized_count} entries optimized")

        return {
            'expired_cleaned': await self.cleanup_expired(),
            'entries_optimized': optimized_count,
            'space_saved_mb': self.stats['bytes_saved'] / (1024 * 1024)
        }


# Singleton instance
smart_cache = SmartCacheLayer(max_size_mb=1024)


# Public API functions
async def cache_get(key: str) -> Optional[Any]:
    """Get item from cache"""
    return await smart_cache.get(key)


async def cache_set(key: str, data: Any, ttl: int = 3600) -> bool:
    """Set item in cache"""
    return await smart_cache.set(key, data, ttl)


async def cache_bulk_get(keys: List[str]) -> Dict[str, Any]:
    """Bulk get items from cache"""
    return await smart_cache.bulk_get(keys)


async def cache_bulk_set(items: Dict[str, Any], ttl: int = 3600) -> int:
    """Bulk set items in cache"""
    return await smart_cache.bulk_set(items, ttl)


def get_cache_stats() -> Dict:
    """Get cache statistics"""
    return smart_cache.get_statistics()


async def optimize_cache() -> Dict:
    """Optimize cache"""
    return await smart_cache.optimize()