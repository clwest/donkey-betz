"""
Attention Aggregator Service
============================

Session 932: Unifies two attention systems into a single endpoint.

Problem: Two different endpoints returned conflicting counts:
- Human Interface: 609 items (all user notifications)
- System State Aggregator: 17 items (curated platform health)

Solution: Single aggregator that returns BOTH with clear labels.

Usage:
    from core.services.attention_aggregator import get_attention_aggregator

    aggregator = get_attention_aggregator(user)
    result = aggregator.get_unified_attention()
    # Returns:
    # {
    #     "system_attention": {"count": 17, "items": [...], "source": "platform_health"},
    #     "human_attention": {"count": 609, "items": [...], "source": "user_notifications"},
    #     "combined_urgent": 5,
    #     "total_count": 626
    # }
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


@dataclass
class UnifiedAttentionItem:
    """
    A unified attention item from either source.
    """
    id: str
    source: str  # 'system' or 'human'
    category: str
    urgency: str  # 'critical', 'high', 'medium', 'low'
    title: str
    summary: str
    created_at: str
    action_url: Optional[str] = None
    payload: Optional[Dict] = None
    # System-specific fields
    section: Optional[str] = None
    explanation: Optional[str] = None
    recommended_action: Optional[str] = None
    # Human-specific fields
    source_agent: Optional[str] = None
    item_type: Optional[str] = None
    ml_confidence: Optional[float] = None
    ml_recommendation: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


class AttentionAggregator:
    """
    Unified attention aggregator combining system health and human notifications.

    Provides a single source of truth for "what needs attention" across the platform.
    """

    # Map system priority (1-100) to urgency levels
    PRIORITY_TO_URGENCY = {
        (80, 100): 'critical',
        (60, 79): 'high',
        (40, 59): 'medium',
        (0, 39): 'low',
    }

    def __init__(self, user):
        """
        Initialize with a user for human attention items.

        Args:
            user: Django User object
        """
        self.user = user
        self.logger = logging.getLogger(f"{__name__}.AttentionAggregator")

    def get_unified_attention(
        self,
        include_system: bool = True,
        include_human: bool = True,
        urgency_filter: List[str] = None,
        limit_per_source: int = 50,
    ) -> Dict[str, Any]:
        """
        Get unified attention from all sources.

        Args:
            include_system: Include system health items (default True)
            include_human: Include human notification items (default True)
            urgency_filter: Filter by urgency levels (default all)
            limit_per_source: Max items per source (default 50)

        Returns:
            Dict with system_attention, human_attention, combined stats
        """
        result = {
            'system_attention': None,
            'human_attention': None,
            'combined_urgent': 0,
            'total_count': 0,
            'timestamp': timezone.now().isoformat(),
        }

        system_items = []
        human_items = []

        # Get system attention
        if include_system:
            try:
                system_items = self._get_system_attention(limit_per_source)
                result['system_attention'] = {
                    'count': len(system_items),
                    'items': [item.to_dict() for item in system_items],
                    'source': 'platform_health',
                    'description': 'Platform health metrics and operational alerts',
                }
            except Exception as e:
                self.logger.error(f"Failed to get system attention: {e}")
                result['system_attention'] = {
                    'count': 0,
                    'items': [],
                    'source': 'platform_health',
                    'error': str(e),
                }

        # Get human attention
        if include_human:
            try:
                human_items = self._get_human_attention(limit_per_source)
                result['human_attention'] = {
                    'count': len(human_items),
                    'items': [item.to_dict() for item in human_items],
                    'source': 'user_notifications',
                    'description': 'User-specific notifications, decisions, and alerts',
                }
            except Exception as e:
                self.logger.error(f"Failed to get human attention: {e}")
                result['human_attention'] = {
                    'count': 0,
                    'items': [],
                    'source': 'user_notifications',
                    'error': str(e),
                }

        # Apply urgency filter if provided
        if urgency_filter:
            if result['system_attention']:
                result['system_attention']['items'] = [
                    item for item in result['system_attention']['items']
                    if item.get('urgency') in urgency_filter
                ]
                result['system_attention']['count'] = len(result['system_attention']['items'])

            if result['human_attention']:
                result['human_attention']['items'] = [
                    item for item in result['human_attention']['items']
                    if item.get('urgency') in urgency_filter
                ]
                result['human_attention']['count'] = len(result['human_attention']['items'])

        # Calculate combined stats
        all_items = system_items + human_items
        result['combined_urgent'] = len([
            item for item in all_items
            if item.urgency in ['critical', 'high']
        ])
        result['total_count'] = len(all_items)

        # Add summary by urgency
        result['by_urgency'] = {
            'critical': len([i for i in all_items if i.urgency == 'critical']),
            'high': len([i for i in all_items if i.urgency == 'high']),
            'medium': len([i for i in all_items if i.urgency == 'medium']),
            'low': len([i for i in all_items if i.urgency == 'low']),
        }

        return result

    def get_combined_items(
        self,
        limit: int = 20,
        urgency_filter: List[str] = None,
    ) -> List[UnifiedAttentionItem]:
        """
        Get combined attention items from both sources, sorted by urgency.

        Args:
            limit: Maximum total items to return
            urgency_filter: Filter by urgency levels

        Returns:
            List of UnifiedAttentionItem sorted by urgency
        """
        system_items = self._get_system_attention(limit)
        human_items = self._get_human_attention(limit)

        all_items = system_items + human_items

        # Apply filter
        if urgency_filter:
            all_items = [i for i in all_items if i.urgency in urgency_filter]

        # Sort by urgency (critical > high > medium > low)
        urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        all_items.sort(key=lambda x: urgency_order.get(x.urgency, 4))

        return all_items[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get attention statistics without full item details.

        Returns:
            Dict with counts and breakdowns
        """
        from core.models_human_interface import HumanAttentionItem
        from core.services.system_state_aggregator import get_system_state_aggregator

        # Human attention stats
        human_items = HumanAttentionItem.objects.filter(user=self.user)
        pending_human = human_items.filter(status__in=['pending', 'viewed']).count()
        total_human = human_items.count()

        human_by_urgency = {}
        for urgency in ['critical', 'high', 'medium', 'low']:
            human_by_urgency[urgency] = human_items.filter(
                status__in=['pending', 'viewed'],
                urgency=urgency
            ).count()

        # System attention stats
        system_aggregator = get_system_state_aggregator()
        system_items = system_aggregator.get_attention_items()

        system_by_urgency = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for item in system_items:
            urgency = self._priority_to_urgency(item.priority)
            system_by_urgency[urgency] += 1

        return {
            'human_attention': {
                'pending': pending_human,
                'total': total_human,
                'by_urgency': human_by_urgency,
            },
            'system_attention': {
                'count': len(system_items),
                'by_urgency': system_by_urgency,
            },
            'combined': {
                'pending': pending_human + len(system_items),
                'urgent': (
                    human_by_urgency.get('critical', 0) +
                    human_by_urgency.get('high', 0) +
                    system_by_urgency.get('critical', 0) +
                    system_by_urgency.get('high', 0)
                ),
            },
            'timestamp': timezone.now().isoformat(),
        }

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    def _get_system_attention(self, limit: int = 50) -> List[UnifiedAttentionItem]:
        """Convert system state items to unified format."""
        from core.services.system_state_aggregator import get_system_state_aggregator

        aggregator = get_system_state_aggregator()
        items = aggregator.get_attention_items()

        unified = []
        for item in items[:limit]:
            unified.append(UnifiedAttentionItem(
                id=item.id,
                source='system',
                category=item.category,
                urgency=self._priority_to_urgency(item.priority),
                title=item.title,
                summary=item.summary,
                created_at=timezone.now().isoformat(),  # System items don't have created_at
                action_url=item.action_url,
                section=item.section,
                explanation=item.explanation,
                recommended_action=item.recommended_action,
            ))

        return unified

    def _get_human_attention(self, limit: int = 50) -> List[UnifiedAttentionItem]:
        """Convert human attention items to unified format."""
        from core.models_human_interface import HumanAttentionItem

        items = HumanAttentionItem.objects.filter(
            user=self.user,
            status__in=['pending', 'viewed']
        ).exclude(
            expires_at__lt=timezone.now()
        ).order_by('-priority_score', '-created_at')[:limit]

        unified = []
        for item in items:
            unified.append(UnifiedAttentionItem(
                id=str(item.id),
                source='human',
                category=item.item_type,
                urgency=item.urgency,
                title=item.title,
                summary=item.summary,
                created_at=item.created_at.isoformat(),
                action_url=f'/ai-studio/?attention={item.id}',
                payload=item.payload,
                source_agent=item.source_agent,
                item_type=item.item_type,
                ml_confidence=item.ml_confidence,
                ml_recommendation=item.ml_recommendation,
            ))

        return unified

    def _priority_to_urgency(self, priority: int) -> str:
        """Convert numeric priority (1-100) to urgency level."""
        for (min_p, max_p), urgency in self.PRIORITY_TO_URGENCY.items():
            if min_p <= priority <= max_p:
                return urgency
        return 'medium'


# Factory and caching
_aggregator_cache = {}


def get_attention_aggregator(user) -> AttentionAggregator:
    """
    Get or create an AttentionAggregator for a user.

    Args:
        user: Django User object

    Returns:
        AttentionAggregator instance
    """
    user_id = user.id if user else None

    if user_id not in _aggregator_cache:
        _aggregator_cache[user_id] = AttentionAggregator(user)

    return _aggregator_cache[user_id]
