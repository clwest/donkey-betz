"""
Concern Tracker Service - Tracks and verifies resolution of system concerns

Session 546: This service creates a feedback loop to ensure concerns identified
by the ThinkingAgent are actually addressed, not just logged.

The verification process:
1. When a ThinkingAgent cycle identifies concerns, they're registered here
2. When actions are taken, they're linked to relevant concerns
3. Verification checks run to see if the underlying issue is resolved
4. Status updates reflect whether concerns are actually fixed
"""

import hashlib
import logging
from datetime import timedelta
from typing import Dict, List, Any, Optional, Tuple
from django.utils import timezone
from django.db.models import Q

logger = logging.getLogger(__name__)


class ConcernTrackerService:
    """
    Tracks concerns across thinking cycles and verifies their resolution.
    """

    # Mapping of concern keywords to categories
    CATEGORY_KEYWORDS = {
        'spider': 'spider_activity',
        'crawl': 'spider_activity',
        'external data': 'spider_activity',
        'decision': 'decision_bottleneck',
        'boardroom': 'decision_bottleneck',
        'bottleneck': 'decision_bottleneck',
        'silo': 'knowledge_silos',
        'concentrated': 'knowledge_silos',
        'teacher': 'knowledge_silos',
        'insight': 'insight_gap',
        'action': 'action_gap',
        'execution': 'execution_failure',
        # Session 549: Information redundancy category
        'redundancy': 'information_redundancy',
        'duplicate': 'information_redundancy',
        'echo chamber': 'information_redundancy',
        'duplication': 'information_redundancy',
        # Session 551: Dream backlog category
        'dream': 'dream_backlog',
        'pending dream': 'dream_backlog',
        'awaiting decision': 'dream_backlog',
        'dream backlog': 'dream_backlog',
    }

    # Verification metrics for different concern categories
    VERIFICATION_METRICS = {
        'spider_activity': 'spider_data_24h',
        'decision_bottleneck': 'boardroom_decisions_24h',
        'knowledge_silos': 'unique_teachers_24h',
        'insight_gap': 'insights_generated_24h',
        'action_gap': 'actions_executed_24h',
        'execution_failure': 'action_success_rate',
        'information_redundancy': 'duplicate_ratio',  # Session 549
        'dream_backlog': 'pending_dreams_count',  # Session 551
    }

    def __init__(self):
        from core.models_unified_system import TrackedConcern, ThoughtRecord, AutonomousAction
        self.TrackedConcern = TrackedConcern
        self.ThoughtRecord = ThoughtRecord
        self.AutonomousAction = AutonomousAction

    def _generate_concern_hash(self, concern_text: str) -> str:
        """Generate a hash for deduplication of similar concerns."""
        # Normalize text for comparison
        normalized = concern_text.lower().strip()
        # Remove common words for better matching
        for word in ['the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been']:
            normalized = normalized.replace(f' {word} ', ' ')
        return hashlib.sha256(normalized.encode()).hexdigest()[:32]

    def _categorize_concern(self, concern_text: str) -> str:
        """Categorize a concern based on its text."""
        text_lower = concern_text.lower()
        for keyword, category in self.CATEGORY_KEYWORDS.items():
            if keyword in text_lower:
                return category
        return 'general'

    def _extract_severity(self, concern_data: Dict) -> str:
        """Extract severity from concern data."""
        if isinstance(concern_data, dict):
            severity = concern_data.get('severity', 'medium')
            if severity in ['critical', 'high', 'medium', 'low']:
                return severity
        return 'medium'

    def _find_similar_concern(self, concern_text: str) -> Optional[Any]:
        """Find an existing similar concern."""
        concern_hash = self._generate_concern_hash(concern_text)

        # First try exact hash match
        existing = self.TrackedConcern.objects.filter(concern_hash=concern_hash).first()
        if existing:
            return existing

        # Then try fuzzy matching based on category and keywords
        category = self._categorize_concern(concern_text)
        keywords = concern_text.lower().split()[:5]  # First 5 words

        # Look for concerns in same category that share keywords
        similar = self.TrackedConcern.objects.filter(
            category=category,
            status__in=['active', 'in_progress', 'monitoring']
        )

        for concern in similar:
            concern_words = concern.concern_text.lower().split()
            overlap = set(keywords) & set(concern_words)
            if len(overlap) >= 3:  # At least 3 words in common
                return concern

        return None

    def register_concerns_from_cycle(self, thought_record) -> List[Dict]:
        """
        Register all concerns from a thinking cycle.

        Returns list of registered concerns with their status.
        """
        concerns = thought_record.concerns or []
        registered = []

        for concern_data in concerns:
            if isinstance(concern_data, dict):
                concern_text = concern_data.get('concern', str(concern_data))
                severity = self._extract_severity(concern_data)
            else:
                concern_text = str(concern_data)
                severity = 'medium'

            result = self.register_concern(
                concern_text=concern_text,
                severity=severity,
                thought_record=thought_record
            )
            registered.append(result)

        return registered

    def register_concern(
        self,
        concern_text: str,
        severity: str = 'medium',
        thought_record=None
    ) -> Dict[str, Any]:
        """
        Register a new concern or update an existing one.

        Returns:
            Dict with 'concern', 'is_new', and 'status' keys
        """
        # Check for existing similar concern
        existing = self._find_similar_concern(concern_text)

        if existing:
            # Update existing concern
            existing.times_detected += 1
            existing.last_seen_cycle = thought_record

            # If it was resolved but came back, mark as recurring
            if existing.status == 'resolved':
                existing.status = 'recurring'
                existing.resolved_at = None
                logger.warning(f"Concern recurring: {concern_text[:50]}...")

            existing.save()

            return {
                'concern': existing,
                'is_new': False,
                'status': existing.status,
                'times_detected': existing.times_detected
            }

        # Create new concern
        concern_hash = self._generate_concern_hash(concern_text)
        category = self._categorize_concern(concern_text)
        verification_metric = self.VERIFICATION_METRICS.get(category, '')

        concern = self.TrackedConcern.objects.create(
            concern_hash=concern_hash,
            concern_text=concern_text,
            category=category,
            severity=severity,
            status='active',
            first_seen_cycle=thought_record,
            last_seen_cycle=thought_record,
            verification_metric=verification_metric
        )

        logger.info(f"New concern registered: [{category}] {concern_text[:50]}...")

        return {
            'concern': concern,
            'is_new': True,
            'status': 'active',
            'times_detected': 1
        }

    def link_action_to_concerns(self, action, thought_record=None) -> List[Any]:
        """
        Link an executed action to relevant concerns it might address.

        Returns list of concerns that were linked.
        """
        linked_concerns = []

        # Get active concerns
        active_concerns = self.TrackedConcern.objects.filter(
            status__in=['active', 'in_progress', 'recurring']
        )

        # Match action to concerns based on action type and concern category
        action_to_category = {
            'spawn_spider': 'spider_activity',
            'trigger_debate': 'decision_bottleneck',
            'trigger_conversation': 'knowledge_silos',
            'request_research': 'insight_gap',
            'create_report': 'insight_gap',
        }

        target_category = action_to_category.get(action.action_type)

        for concern in active_concerns:
            should_link = False

            # Category match
            if target_category and concern.category == target_category:
                should_link = True

            # Keyword match in action reasoning
            if action.reasoning:
                concern_keywords = concern.concern_text.lower().split()[:5]
                for keyword in concern_keywords:
                    if len(keyword) > 4 and keyword in action.reasoning.lower():
                        should_link = True
                        break

            if should_link:
                concern.actions_taken.add(action)
                if concern.status == 'active':
                    concern.status = 'in_progress'
                    concern.save()
                linked_concerns.append(concern)
                logger.info(f"Linked action '{action.action_type}' to concern: {concern.concern_text[:50]}")

        return linked_concerns

    def verify_concern_resolution(self, concern) -> Dict[str, Any]:
        """
        Verify if a concern has been resolved by checking relevant metrics.

        Returns verification result with status update recommendation.
        """
        from core.models_unified_system import SpiderData, KnowledgeTransfer, AgentDecisionSummary
        from datetime import timedelta

        now = timezone.now()
        last_24h = now - timedelta(hours=24)

        result = {
            'verified_at': now.isoformat(),
            'metric_checked': concern.verification_metric,
            'previous_status': concern.status,
            'recommended_status': concern.status,
            'metrics': {},
            'is_resolved': False
        }

        try:
            if concern.category == 'spider_activity':
                # Check if spiders have collected data
                spider_data_count = SpiderData.objects.filter(
                    created_at__gte=last_24h
                ).count()
                result['metrics']['spider_data_24h'] = spider_data_count
                result['is_resolved'] = spider_data_count > 100  # Threshold

            elif concern.category == 'decision_bottleneck':
                # Check if agent decisions are being made
                try:
                    decisions_count = AgentDecisionSummary.objects.filter(
                        created_at__gte=last_24h
                    ).count()
                except Exception:
                    decisions_count = 0
                result['metrics']['decisions_24h'] = decisions_count
                result['is_resolved'] = decisions_count > 0

            elif concern.category == 'knowledge_silos':
                # Check if knowledge is being shared by more agents
                unique_teachers = KnowledgeTransfer.objects.filter(
                    created_at__gte=last_24h
                ).values('connection__teacher_agent').distinct().count()
                result['metrics']['unique_teachers_24h'] = unique_teachers
                result['is_resolved'] = unique_teachers >= 5  # At least 5 different teachers

            elif concern.category == 'action_gap':
                # Check action execution rate
                from core.models_unified_system import AutonomousAction
                total_actions = AutonomousAction.objects.filter(
                    created_at__gte=last_24h
                ).count()
                successful = AutonomousAction.objects.filter(
                    created_at__gte=last_24h,
                    status='completed'
                ).count()
                success_rate = (successful / total_actions * 100) if total_actions > 0 else 0
                result['metrics']['action_success_rate'] = success_rate
                result['is_resolved'] = success_rate >= 80

            elif concern.category == 'execution_failure':
                # Session 548: Check action success rate for execution failures
                from core.models_unified_system import AutonomousAction
                total_actions = AutonomousAction.objects.filter(
                    created_at__gte=last_24h
                ).count()
                successful = AutonomousAction.objects.filter(
                    created_at__gte=last_24h,
                    status='completed'
                ).count()
                success_rate = (successful / total_actions * 100) if total_actions > 0 else 0
                result['metrics']['action_success_rate'] = success_rate
                result['metrics']['total_actions'] = total_actions
                result['metrics']['successful_actions'] = successful
                result['is_resolved'] = success_rate >= 80

            elif concern.category == 'information_redundancy':
                # Session 549: Check deduplication stats
                from core.services.deduplication_service import get_deduplication_service
                dedup = get_deduplication_service()
                stats = dedup.get_deduplication_stats()

                total_duplicates = (
                    stats['spider_duplicates'] +
                    stats['conversation_duplicates'] +
                    stats['dream_duplicates']
                )
                result['metrics']['spider_duplicates'] = stats['spider_duplicates']
                result['metrics']['conversation_duplicates'] = stats['conversation_duplicates']
                result['metrics']['dream_duplicates'] = stats['dream_duplicates']
                result['metrics']['total_duplicates'] = total_duplicates

                # Resolved if total duplicates are under threshold
                # Session 549: Set to 100 - some spider duplicates have FK refs and can't be deleted
                result['is_resolved'] = total_duplicates <= 100

            else:
                # General verification - check if concern appears in recent cycles
                from core.models_unified_system import ThoughtRecord
                recent_cycles = ThoughtRecord.objects.filter(
                    started_at__gte=last_24h
                ).order_by('-started_at')[:3]

                concern_still_present = False
                for cycle in recent_cycles:
                    for c in (cycle.concerns or []):
                        if isinstance(c, dict):
                            text = c.get('concern', '')
                        else:
                            text = str(c)
                        if self._generate_concern_hash(text) == concern.concern_hash:
                            concern_still_present = True
                            break

                result['metrics']['still_detected'] = concern_still_present
                result['is_resolved'] = not concern_still_present

        except Exception as e:
            logger.error(f"Error verifying concern: {e}")
            result['error'] = str(e)
            return result

        # Determine recommended status
        if result['is_resolved']:
            result['recommended_status'] = 'resolved'
        elif concern.status == 'active' and concern.actions_taken.exists():
            result['recommended_status'] = 'monitoring'

        # Update concern
        concern.last_verification_at = now
        concern.last_verification_result = result

        if result['is_resolved'] and concern.status != 'resolved':
            concern.status = 'resolved'
            concern.resolved_at = now
            concern.resolution_notes = f"Auto-verified: {result['metrics']}"
            logger.info(f"Concern RESOLVED: {concern.concern_text[:50]}")
        elif result['recommended_status'] != concern.status:
            concern.status = result['recommended_status']

        concern.save()

        return result

    def verify_all_active_concerns(self) -> Dict[str, Any]:
        """
        Run verification on all active concerns.

        Returns summary of verification results.
        """
        active_concerns = self.TrackedConcern.objects.filter(
            status__in=['active', 'in_progress', 'monitoring', 'recurring']
        )

        results = {
            'total_checked': 0,
            'resolved': 0,
            'still_active': 0,
            'errors': 0,
            'concerns': []
        }

        for concern in active_concerns:
            result = self.verify_concern_resolution(concern)
            results['total_checked'] += 1

            if result.get('error'):
                results['errors'] += 1
            elif result.get('is_resolved'):
                results['resolved'] += 1
            else:
                results['still_active'] += 1

            results['concerns'].append({
                'id': str(concern.id),
                'text': concern.concern_text[:50],
                'category': concern.category,
                'status': concern.status,
                'is_resolved': result.get('is_resolved', False)
            })

        return results

    def get_concern_dashboard(self) -> Dict[str, Any]:
        """
        Get a dashboard view of all concerns for UI display.
        """
        all_concerns = self.TrackedConcern.objects.all()

        by_status = {}
        for status_choice in ['active', 'in_progress', 'monitoring', 'resolved', 'recurring', 'accepted']:
            by_status[status_choice] = all_concerns.filter(status=status_choice).count()

        by_category = {}
        for concern in all_concerns.filter(status__in=['active', 'in_progress', 'recurring']):
            cat = concern.category
            if cat not in by_category:
                by_category[cat] = 0
            by_category[cat] += 1

        # Get stale concerns (active for > 7 days)
        stale_threshold = timezone.now() - timedelta(days=7)
        stale_concerns = all_concerns.filter(
            status='active',
            created_at__lt=stale_threshold
        )

        # Recent concern activity
        recent = all_concerns.order_by('-updated_at')[:10]

        return {
            'total': all_concerns.count(),
            'by_status': by_status,
            'by_category': by_category,
            'stale_count': stale_concerns.count(),
            'recent': [
                {
                    'id': str(c.id),
                    'text': c.concern_text,  # Session 549: Show full text
                    'category': c.category,
                    'severity': c.severity,
                    'status': c.status,
                    'times_detected': c.times_detected,
                    'days_active': c.days_active,
                    'actions_count': c.actions_taken.count(),
                    'last_verified': c.last_verification_at.isoformat() if c.last_verification_at else None
                }
                for c in recent
            ]
        }


# Singleton instance for easy access
_concern_tracker = None

def get_concern_tracker() -> ConcernTrackerService:
    """Get or create the concern tracker service instance."""
    global _concern_tracker
    if _concern_tracker is None:
        _concern_tracker = ConcernTrackerService()
    return _concern_tracker
