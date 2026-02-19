"""
Deduplication Service - Session 549

Addresses the concern: "Information redundancy (duplicate topics) wastes
learner/compute cycles and may bias trend detection."

This service provides:
1. Spider URL deduplication - prevent fetching same URL multiple times
2. Conversation topic deduplication - merge similar discussions
3. Dream title deduplication - generate unique dream titles
4. Bulk cleanup of existing duplicates
"""

import hashlib
import logging
import re
from datetime import timedelta
from typing import Dict, List, Optional, Tuple, Any
from django.utils import timezone
from django.db.models import Count, Q

logger = logging.getLogger(__name__)


class DeduplicationService:
    """
    Service for detecting and preventing duplicate content across the system.
    """

    # Similarity threshold for fuzzy matching (0-1)
    SIMILARITY_THRESHOLD = 0.70  # Session 1035: Lowered from 0.85 to catch near-miss topic variants

    # Time window for considering duplicates (hours)
    DUPLICATE_WINDOW_HOURS = 48

    # Common generic prefixes/patterns to normalize
    GENERIC_PREFIXES = [
        r'^\[Learned\]\s*',
        r'^Discussion:\s*',
        r'^Panel:\s*',
        r'^Research:\s*',
        r'^Topic:\s*',
    ]

    # Generic titles that indicate low-quality content
    GENERIC_TITLES = {
        'creative thought',
        'none',
        'creative idea',
        'new idea',
        'untitled',
        'discussion',
        'research',
        'analysis',
    }

    def __init__(self):
        from core.models_unified_system import SpiderData, AgentConversation, AgentDream
        self.SpiderData = SpiderData
        self.AgentConversation = AgentConversation
        self.AgentDream = AgentDream

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison by removing prefixes and lowercasing."""
        if not text:
            return ''

        normalized = text.strip().lower()

        # Remove generic prefixes
        for pattern in self.GENERIC_PREFIXES:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)

        # Remove extra whitespace
        normalized = ' '.join(normalized.split())

        return normalized

    def _generate_content_hash(self, text: str) -> str:
        """Generate a hash for content comparison."""
        normalized = self._normalize_text(text)
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        if not text1 or not text2:
            return 0.0

        words1 = set(self._normalize_text(text1).split())
        words2 = set(self._normalize_text(text2).split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def _is_generic_title(self, title: str) -> bool:
        """Check if a title is too generic."""
        if not title:
            return True

        normalized = self._normalize_text(title)
        return normalized in self.GENERIC_TITLES or len(normalized) < 5

    # ==================== SPIDER DEDUPLICATION ====================

    def check_spider_url_exists(self, url: str, spider_name: str = None) -> Tuple[bool, Optional[Any]]:
        """
        Check if a spider URL already exists in the database.

        Returns:
            Tuple of (exists: bool, existing_record: SpiderData or None)
        """
        if not url or url in ['internal', 'on-demand-execution']:
            # These are internal markers, not real URLs - allow them but don't duplicate
            cutoff = timezone.now() - timedelta(hours=1)
            existing = self.SpiderData.objects.filter(
                source_url=url,
                created_at__gte=cutoff
            ).first()
            return (existing is not None, existing)

        # For real URLs, check if we've seen it in the last 24 hours
        cutoff = timezone.now() - timedelta(hours=self.DUPLICATE_WINDOW_HOURS)

        query = Q(source_url=url, created_at__gte=cutoff)
        if spider_name:
            query &= Q(spider_name=spider_name)

        existing = self.SpiderData.objects.filter(query).first()
        return (existing is not None, existing)

    def get_duplicate_spider_urls(self, limit: int = 100) -> List[Dict]:
        """Get list of duplicate spider URLs for cleanup."""
        duplicates = (
            self.SpiderData.objects
            .values('source_url')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
            .order_by('-count')[:limit]
        )
        return list(duplicates)

    def cleanup_spider_duplicates(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Remove duplicate spider data, keeping only the most recent entry for each URL.

        Args:
            dry_run: If True, only report what would be deleted without actually deleting.

        Returns:
            Summary of cleanup operation.
        """
        result = {
            'duplicates_found': 0,
            'records_to_delete': 0,
            'records_deleted': 0,
            'dry_run': dry_run,
            'details': []
        }

        # Get all duplicate URLs
        duplicates = self.get_duplicate_spider_urls(limit=500)
        result['duplicates_found'] = len(duplicates)

        for dup in duplicates:
            url = dup['source_url']
            count = dup['count']

            # Get all records for this URL, ordered by created_at (newest first)
            records = self.SpiderData.objects.filter(source_url=url).order_by('-created_at')

            # Keep the first (newest), delete the rest
            ids_to_delete = list(records.values_list('id', flat=True)[1:])

            if not dry_run and ids_to_delete:
                # Delete one by one, skipping records with FK references
                for record_id in ids_to_delete:
                    try:
                        deleted, _ = self.SpiderData.objects.filter(id=record_id).delete()
                        result['records_deleted'] += deleted
                        result['records_to_delete'] += 1
                    except Exception:
                        # Skip records with foreign key references
                        pass
            else:
                result['records_to_delete'] += len(ids_to_delete)

            result['details'].append({
                'url': url[:50],
                'total': count,
                'to_delete': len(ids_to_delete)
            })

        logger.info(f"Spider deduplication: found {result['duplicates_found']} duplicate URLs, "
                   f"{'would delete' if dry_run else 'deleted'} {result['records_to_delete']} records")

        return result

    # ==================== CONVERSATION DEDUPLICATION ====================

    def find_similar_conversation(self, topic: str, agent_ids: List = None,
                                   hours: int = None) -> Optional[Any]:
        """
        Find an existing similar conversation to potentially join instead of creating new.

        Returns:
            Existing AgentConversation if similar one found, None otherwise.
        """
        if not topic:
            return None

        hours = hours or self.DUPLICATE_WINDOW_HOURS
        cutoff = timezone.now() - timedelta(hours=hours)
        normalized_topic = self._normalize_text(topic)

        # First try exact match on normalized topic
        recent_convos = self.AgentConversation.objects.filter(
            started_at__gte=cutoff
        ).order_by('-started_at')[:50]

        for convo in recent_convos:
            if self._normalize_text(convo.topic) == normalized_topic:
                return convo

            # Fuzzy match
            similarity = self._calculate_similarity(topic, convo.topic)
            if similarity >= self.SIMILARITY_THRESHOLD:
                return convo

        return None

    def get_duplicate_conversations(self, limit: int = 100) -> List[Dict]:
        """Get list of duplicate conversation topics."""
        duplicates = (
            self.AgentConversation.objects
            .values('topic')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
            .order_by('-count')[:limit]
        )
        return list(duplicates)

    def cleanup_conversation_duplicates(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Clean up duplicate conversations, keeping the most active one.
        """
        result = {
            'duplicates_found': 0,
            'records_to_delete': 0,
            'records_deleted': 0,
            'dry_run': dry_run,
            'details': []
        }

        duplicates = self.get_duplicate_conversations(limit=200)
        result['duplicates_found'] = len(duplicates)

        for dup in duplicates:
            topic = dup['topic']
            count = dup['count']

            # Get all conversations with this topic
            # Keep the one with most participants/messages (approximated by newest)
            convos = self.AgentConversation.objects.filter(topic=topic).order_by('-started_at')

            # Keep the first, delete the rest
            ids_to_delete = list(convos.values_list('id', flat=True)[1:])
            result['records_to_delete'] += len(ids_to_delete)

            if not dry_run and ids_to_delete:
                deleted_count, _ = self.AgentConversation.objects.filter(id__in=ids_to_delete).delete()
                result['records_deleted'] += deleted_count

            result['details'].append({
                'topic': (topic or '')[:50],
                'total': count,
                'to_delete': len(ids_to_delete)
            })

        logger.info(f"Conversation deduplication: found {result['duplicates_found']} duplicate topics, "
                   f"{'would delete' if dry_run else 'deleted'} {result['records_to_delete']} records")

        return result

    def cleanup_fuzzy_conversation_duplicates(
        self, dry_run: bool = True, hours: int = 168, threshold: float = None
    ) -> Dict[str, Any]:
        """
        Session 1032: BFS-cluster conversations by fuzzy Jaccard similarity,
        keep the highest quality_score per cluster, delete the rest.

        Args:
            dry_run: If True, only report what would be deleted.
            hours: Lookback window (default 168 = 7 days).
            threshold: Similarity threshold (default self.SIMILARITY_THRESHOLD).

        Returns:
            Summary of cleanup operation.
        """
        from collections import defaultdict

        threshold = threshold or self.SIMILARITY_THRESHOLD
        cutoff = timezone.now() - timedelta(hours=hours)

        convos = list(
            self.AgentConversation.objects.filter(started_at__gte=cutoff)
            .order_by('-started_at')[:500]
        )

        result = {
            'dry_run': dry_run,
            'conversations_scanned': len(convos),
            'clusters_found': 0,
            'records_to_delete': 0,
            'records_deleted': 0,
            'clusters': [],
        }

        if len(convos) < 2:
            return result

        # Build adjacency list of similar conversations
        similar_pairs: Dict[int, set] = defaultdict(set)
        for i, c1 in enumerate(convos):
            for c2 in convos[i + 1:]:
                similarity = self._calculate_similarity(c1.topic or '', c2.topic or '')
                if similarity >= threshold:
                    similar_pairs[i].add(convos.index(c2))
                    similar_pairs[convos.index(c2)].add(i)

        # BFS to find connected components (clusters)
        visited: set = set()
        clusters: List[List] = []

        for idx in range(len(convos)):
            if idx in visited or idx not in similar_pairs:
                continue

            cluster_indices: List[int] = []
            queue = [idx]
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                cluster_indices.append(current)
                for neighbor in similar_pairs[current]:
                    if neighbor not in visited:
                        queue.append(neighbor)

            if len(cluster_indices) > 1:
                cluster = [convos[ci] for ci in cluster_indices]
                # Sort: concluded first, then highest quality_score, then newest
                cluster.sort(
                    key=lambda c: (
                        c.status == 'concluded',
                        getattr(c, 'quality_score', 0) or 0,
                        c.started_at,
                    ),
                    reverse=True,
                )
                clusters.append(cluster)

        result['clusters_found'] = len(clusters)

        for cluster in clusters:
            keeper = cluster[0]
            duplicates = cluster[1:]
            ids_to_delete = [c.id for c in duplicates]
            result['records_to_delete'] += len(ids_to_delete)

            cluster_info = {
                'keeper': f"{str(keeper.id)[:8]}: {(keeper.topic or '')[:50]}",
                'duplicates': len(ids_to_delete),
                'sample_topics': [(c.topic or '')[:50] for c in duplicates[:3]],
            }
            result['clusters'].append(cluster_info)

            if not dry_run and ids_to_delete:
                deleted_count, _ = self.AgentConversation.objects.filter(
                    id__in=ids_to_delete
                ).delete()
                result['records_deleted'] += deleted_count

        logger.info(
            f"Fuzzy conversation dedup: {result['clusters_found']} clusters, "
            f"{'would delete' if dry_run else 'deleted'} {result['records_to_delete']} records"
        )

        return result

    # ==================== DREAM DEDUPLICATION ====================

    def check_dream_title_unique(self, title: str, agent_id: str = None) -> Tuple[bool, str]:
        """
        Check if a dream title is unique and not too generic.

        Returns:
            Tuple of (is_unique: bool, suggested_title: str)
        """
        if self._is_generic_title(title):
            # Generate a more unique title
            timestamp = timezone.now().strftime('%Y%m%d_%H%M')
            agent_suffix = f"_{agent_id[:8]}" if agent_id else ""
            suggested = f"Creative Vision {timestamp}{agent_suffix}"
            return (False, suggested)

        # Check for recent duplicates
        cutoff = timezone.now() - timedelta(hours=self.DUPLICATE_WINDOW_HOURS)
        normalized = self._normalize_text(title)

        recent_dreams = self.AgentDream.objects.filter(
            dreamed_at__gte=cutoff
        ).values_list('title', flat=True)[:100]

        for existing_title in recent_dreams:
            if self._normalize_text(existing_title) == normalized:
                # Add uniqueness suffix
                timestamp = timezone.now().strftime('%H%M%S')
                return (False, f"{title} ({timestamp})")

        return (True, title)

    def get_duplicate_dreams(self, limit: int = 100) -> List[Dict]:
        """Get list of duplicate dream titles."""
        duplicates = (
            self.AgentDream.objects
            .values('title')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
            .order_by('-count')[:limit]
        )
        return list(duplicates)

    def cleanup_dream_duplicates(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Clean up duplicate dreams, keeping the highest scored one.
        """
        result = {
            'duplicates_found': 0,
            'records_to_delete': 0,
            'records_deleted': 0,
            'dry_run': dry_run,
            'details': []
        }

        duplicates = self.get_duplicate_dreams(limit=200)
        result['duplicates_found'] = len(duplicates)

        for dup in duplicates:
            title = dup['title']
            count = dup['count']

            # Get all dreams with this title, ordered by composite_score (best first)
            dreams = self.AgentDream.objects.filter(title=title).order_by('-composite_score', '-dreamed_at')

            # Keep the best one, delete the rest
            ids_to_delete = list(dreams.values_list('id', flat=True)[1:])
            result['records_to_delete'] += len(ids_to_delete)

            if not dry_run and ids_to_delete:
                deleted_count, _ = self.AgentDream.objects.filter(id__in=ids_to_delete).delete()
                result['records_deleted'] += deleted_count

            result['details'].append({
                'title': (title or '')[:50],
                'total': count,
                'to_delete': len(ids_to_delete)
            })

        logger.info(f"Dream deduplication: found {result['duplicates_found']} duplicate titles, "
                   f"{'would delete' if dry_run else 'deleted'} {result['records_to_delete']} records")

        return result

    # ==================== DECISION SUMMARY DEDUPLICATION ====================

    def dedupe_decision_summary_blocks(self, text: str) -> Tuple[str, bool]:
        """
        Hash-based deduplication of repeated DecisionSummary blocks.

        Session 920: Prevents the same DecisionSummary from appearing multiple
        times in panel output due to agent message repeating.

        Args:
            text: The text potentially containing multiple DecisionSummary blocks

        Returns:
            Tuple of (deduped_text: str, dedupe_applied: bool)
        """
        if not text or "=== DecisionSummary ===" not in text:
            return text, False

        # Split by section markers (=== SectionName ===)
        section_pattern = r'(===\s*\w+(?:\s+\w+)*\s*===)'
        parts = re.split(section_pattern, text)

        seen_hashes = set()
        unique_parts = []
        dedupe_applied = False
        current_section = None

        i = 0
        while i < len(parts):
            part = parts[i]

            # Check if this is a section header
            if re.match(section_pattern, part.strip()):
                current_section = part.strip()
                # Get the content that follows this header
                content = parts[i + 1] if i + 1 < len(parts) else ''

                # Create hash of section + content
                section_with_content = part + content
                content_hash = self._generate_content_hash(section_with_content.strip())

                # Only dedupe if content is substantial (> 50 chars)
                if len(section_with_content.strip()) < 50 or content_hash not in seen_hashes:
                    seen_hashes.add(content_hash)
                    unique_parts.append(part)
                    if i + 1 < len(parts):
                        unique_parts.append(parts[i + 1])
                        i += 1
                else:
                    dedupe_applied = True
                    # Skip both the header and its content
                    i += 1
            else:
                # Not a section header, keep as-is
                unique_parts.append(part)

            i += 1

        if dedupe_applied:
            logger.info(f"Deduplication removed repeated DecisionSummary block(s)")

        return ''.join(unique_parts), dedupe_applied

    # ==================== COMPREHENSIVE CLEANUP ====================

    def run_full_deduplication(self, dry_run: bool = True) -> Dict[str, Any]:
        """
        Run deduplication across all content types.

        Args:
            dry_run: If True, only report what would be cleaned up.

        Returns:
            Comprehensive summary of all deduplication operations.
        """
        logger.info(f"Starting full deduplication (dry_run={dry_run})")

        results = {
            'dry_run': dry_run,
            'started_at': timezone.now().isoformat(),
            'spider_cleanup': self.cleanup_spider_duplicates(dry_run=dry_run),
            'conversation_cleanup': self.cleanup_conversation_duplicates(dry_run=dry_run),
            'dream_cleanup': self.cleanup_dream_duplicates(dry_run=dry_run),
        }

        # Calculate totals
        results['total_duplicates'] = (
            results['spider_cleanup']['duplicates_found'] +
            results['conversation_cleanup']['duplicates_found'] +
            results['dream_cleanup']['duplicates_found']
        )
        results['total_records_affected'] = (
            results['spider_cleanup']['records_to_delete'] +
            results['conversation_cleanup']['records_to_delete'] +
            results['dream_cleanup']['records_to_delete']
        )

        if not dry_run:
            results['total_deleted'] = (
                results['spider_cleanup']['records_deleted'] +
                results['conversation_cleanup']['records_deleted'] +
                results['dream_cleanup']['records_deleted']
            )

        results['completed_at'] = timezone.now().isoformat()

        logger.info(f"Full deduplication complete: {results['total_duplicates']} duplicate groups, "
                   f"{results['total_records_affected']} records affected")

        return results

    def get_deduplication_stats(self) -> Dict[str, Any]:
        """Get current duplication statistics without cleanup."""
        return {
            'spider_duplicates': len(self.get_duplicate_spider_urls(limit=1000)),
            'conversation_duplicates': len(self.get_duplicate_conversations(limit=1000)),
            'dream_duplicates': len(self.get_duplicate_dreams(limit=1000)),
            'top_spider_duplicates': self.get_duplicate_spider_urls(limit=5),
            'top_conversation_duplicates': self.get_duplicate_conversations(limit=5),
            'top_dream_duplicates': self.get_duplicate_dreams(limit=5),
        }


# Singleton instance
_dedup_service = None

def get_deduplication_service() -> DeduplicationService:
    """Get or create the deduplication service instance."""
    global _dedup_service
    if _dedup_service is None:
        _dedup_service = DeduplicationService()
    return _dedup_service
