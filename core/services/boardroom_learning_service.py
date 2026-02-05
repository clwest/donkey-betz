"""
Boardroom Learning Service - Records user decisions for PA learning
====================================================================

Session 940: Created to close the feedback loop for boardroom actions.

When users approve/ignore attention items or promote/reject decisions via PA,
this service:
1. Records the individual decision
2. Updates aggregate patterns (e.g., "user approves 80% of stock alerts")
3. Provides pattern data for PA recommendations

Usage:
    from core.services.boardroom_learning_service import get_boardroom_learning_service

    service = get_boardroom_learning_service()
    service.record_attention_decision(user, item_id, 'approved', source_agent, item_type)
    patterns = service.get_user_patterns(user)
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Count, Avg, F

logger = logging.getLogger(__name__)
User = get_user_model()


class BoardroomLearningService:
    """
    Records and analyzes user boardroom decisions for learning.
    """

    # Pattern types
    PATTERN_ATTENTION_BY_TYPE = 'boardroom_attention_by_type'
    PATTERN_ATTENTION_BY_SOURCE = 'boardroom_attention_by_source'
    PATTERN_DECISION_BY_TYPE = 'boardroom_decision_by_type'

    def record_attention_decision(
        self,
        user,
        item_id: str,
        decision: str,  # 'approved' or 'ignored'
        source_agent: str,
        item_type: str,
        urgency: str = 'medium',
        via: str = 'PA'
    ) -> bool:
        """
        Record a user's decision on an attention item.

        Returns True if recorded successfully.
        """
        try:
            from core.models_unified_system import LearningPattern

            # Get or create pattern for this item_type
            pattern, created = LearningPattern.objects.get_or_create(
                user=user,
                pattern_type=self.PATTERN_ATTENTION_BY_TYPE,
                defaults={
                    'description': f'User attention item decisions by type',
                    'confidence': 0.5,
                    'pattern_data': {},
                    'applies_to_agents': ['PersonalAssistant'],
                    'applies_to_query_types': ['boardroom', 'attention'],
                }
            )

            # Update pattern_data
            data = pattern.pattern_data or {}

            # Initialize type stats if needed
            if item_type not in data:
                data[item_type] = {
                    'approved': 0,
                    'ignored': 0,
                    'total': 0,
                    'approval_rate': 0.0,
                }

            # Update counts
            data[item_type]['total'] += 1
            data[item_type][decision] += 1
            data[item_type]['approval_rate'] = (
                data[item_type]['approved'] / data[item_type]['total']
            )

            # Store last decision metadata
            data[item_type]['last_decision'] = {
                'item_id': item_id,
                'decision': decision,
                'timestamp': timezone.now().isoformat(),
                'via': via,
            }

            pattern.pattern_data = data
            pattern.times_applied += 1
            if decision == 'approved':
                pattern.success_when_applied += 1

            # Update confidence based on sample size
            total_decisions = sum(t['total'] for t in data.values())
            pattern.confidence = min(0.95, 0.5 + (total_decisions * 0.01))

            pattern.save()

            # Also record by source agent
            self._record_by_source(user, source_agent, decision)

            logger.info(
                f"📚 Recorded boardroom decision: {user.username} {decision} "
                f"{item_type} from {source_agent} (via {via})"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to record attention decision: {e}")
            return False

    def _record_by_source(self, user, source_agent: str, decision: str):
        """Record decision pattern by source agent."""
        try:
            from core.models_unified_system import LearningPattern

            pattern, created = LearningPattern.objects.get_or_create(
                user=user,
                pattern_type=self.PATTERN_ATTENTION_BY_SOURCE,
                defaults={
                    'description': 'User attention item decisions by source agent',
                    'confidence': 0.5,
                    'pattern_data': {},
                    'applies_to_agents': ['PersonalAssistant'],
                    'applies_to_query_types': ['boardroom', 'attention'],
                }
            )

            data = pattern.pattern_data or {}

            if source_agent not in data:
                data[source_agent] = {
                    'approved': 0,
                    'ignored': 0,
                    'total': 0,
                    'approval_rate': 0.0,
                }

            data[source_agent]['total'] += 1
            data[source_agent][decision] += 1
            data[source_agent]['approval_rate'] = (
                data[source_agent]['approved'] / data[source_agent]['total']
            )

            pattern.pattern_data = data
            pattern.save()

        except Exception as e:
            logger.debug(f"Failed to record by source: {e}")

    def record_decision_action(
        self,
        user,
        decision_id: str,
        action: str,  # 'promoted' or 'rejected'
        decision_type: str,
        impact_area: str,
        via: str = 'PA'
    ) -> bool:
        """
        Record a user's action on a draft decision.

        Returns True if recorded successfully.
        """
        try:
            from core.models_unified_system import LearningPattern

            pattern, created = LearningPattern.objects.get_or_create(
                user=user,
                pattern_type=self.PATTERN_DECISION_BY_TYPE,
                defaults={
                    'description': 'User draft decision actions by type',
                    'confidence': 0.5,
                    'pattern_data': {},
                    'applies_to_agents': ['PersonalAssistant'],
                    'applies_to_query_types': ['boardroom', 'decisions'],
                }
            )

            data = pattern.pattern_data or {}

            if decision_type not in data:
                data[decision_type] = {
                    'promoted': 0,
                    'rejected': 0,
                    'total': 0,
                    'promotion_rate': 0.0,
                }

            data[decision_type]['total'] += 1
            data[decision_type][action] += 1
            data[decision_type]['promotion_rate'] = (
                data[decision_type]['promoted'] / data[decision_type]['total']
            )

            data[decision_type]['last_action'] = {
                'decision_id': decision_id,
                'action': action,
                'impact_area': impact_area,
                'timestamp': timezone.now().isoformat(),
                'via': via,
            }

            pattern.pattern_data = data
            pattern.times_applied += 1
            if action == 'promoted':
                pattern.success_when_applied += 1

            total_actions = sum(t['total'] for t in data.values())
            pattern.confidence = min(0.95, 0.5 + (total_actions * 0.01))

            pattern.save()

            logger.info(
                f"📚 Recorded boardroom action: {user.username} {action} "
                f"{decision_type} decision (via {via})"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to record decision action: {e}")
            return False

    def get_user_patterns(self, user) -> Dict[str, Any]:
        """
        Get all boardroom learning patterns for a user.

        Returns:
            Dict with attention and decision patterns
        """
        try:
            from core.models_unified_system import LearningPattern

            patterns = LearningPattern.objects.filter(
                user=user,
                pattern_type__startswith='boardroom_',
                is_active=True
            )

            result = {
                'attention_by_type': {},
                'attention_by_source': {},
                'decision_by_type': {},
                'insights': [],
            }

            for pattern in patterns:
                if pattern.pattern_type == self.PATTERN_ATTENTION_BY_TYPE:
                    result['attention_by_type'] = pattern.pattern_data or {}
                elif pattern.pattern_type == self.PATTERN_ATTENTION_BY_SOURCE:
                    result['attention_by_source'] = pattern.pattern_data or {}
                elif pattern.pattern_type == self.PATTERN_DECISION_BY_TYPE:
                    result['decision_by_type'] = pattern.pattern_data or {}

            # Generate insights
            result['insights'] = self._generate_insights(result)

            return result

        except Exception as e:
            logger.error(f"Failed to get user patterns: {e}")
            return {}

    def _generate_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """Generate human-readable insights from patterns."""
        insights = []

        # Attention by type insights
        for item_type, stats in patterns.get('attention_by_type', {}).items():
            if stats.get('total', 0) >= 5:
                rate = stats.get('approval_rate', 0)
                if rate >= 0.8:
                    insights.append(f"You approve most {item_type} items ({rate:.0%})")
                elif rate <= 0.2:
                    insights.append(f"You rarely approve {item_type} items ({rate:.0%})")

        # Attention by source insights
        for source, stats in patterns.get('attention_by_source', {}).items():
            if stats.get('total', 0) >= 5:
                rate = stats.get('approval_rate', 0)
                if rate >= 0.8:
                    insights.append(f"You trust {source}'s recommendations ({rate:.0%} approval)")
                elif rate <= 0.2:
                    insights.append(f"You typically dismiss {source}'s items ({rate:.0%} approval)")

        # Decision by type insights
        for decision_type, stats in patterns.get('decision_by_type', {}).items():
            if stats.get('total', 0) >= 3:
                rate = stats.get('promotion_rate', 0)
                if rate >= 0.7:
                    insights.append(f"You often promote {decision_type} decisions ({rate:.0%})")

        return insights

    def get_recommendation_context(self, user, item_type: str = None, source_agent: str = None) -> str:
        """
        Get recommendation context for PA prompt injection.

        Returns formatted text about user's past decision patterns.
        """
        try:
            patterns = self.get_user_patterns(user)

            context_parts = []

            # Add relevant pattern info
            if item_type and item_type in patterns.get('attention_by_type', {}):
                stats = patterns['attention_by_type'][item_type]
                rate = stats.get('approval_rate', 0)
                total = stats.get('total', 0)
                if total >= 3:
                    context_parts.append(
                        f"Note: User has approved {rate:.0%} of {item_type} items "
                        f"({total} total decisions)"
                    )

            if source_agent and source_agent in patterns.get('attention_by_source', {}):
                stats = patterns['attention_by_source'][source_agent]
                rate = stats.get('approval_rate', 0)
                total = stats.get('total', 0)
                if total >= 3:
                    context_parts.append(
                        f"Note: User typically {'approves' if rate > 0.5 else 'ignores'} "
                        f"items from {source_agent} ({rate:.0%} approval rate)"
                    )

            # Add general insights
            if patterns.get('insights'):
                context_parts.append(f"User patterns: {'; '.join(patterns['insights'][:3])}")

            return '\n'.join(context_parts) if context_parts else ''

        except Exception as e:
            logger.error(f"Failed to get recommendation context: {e}")
            return ''


# Singleton instance
_boardroom_learning_service: Optional[BoardroomLearningService] = None


def get_boardroom_learning_service() -> BoardroomLearningService:
    """Get the singleton BoardroomLearningService instance."""
    global _boardroom_learning_service
    if _boardroom_learning_service is None:
        _boardroom_learning_service = BoardroomLearningService()
    return _boardroom_learning_service
