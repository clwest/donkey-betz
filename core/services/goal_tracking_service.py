"""
Session 930: Goal Tracking Service

Tracks user goal progress by linking deliverables and initiatives
to goals, calculating overall progress, and providing dashboards.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Count, Q

logger = logging.getLogger(__name__)


@dataclass
class GoalSummary:
    """Summary of a user's goal with progress"""
    goal_id: str
    name: str
    category: str
    target_value: float
    current_value: float
    progress_percentage: int
    status: str
    recent_contributions: List[Dict]
    milestones_reached: List[str]
    days_remaining: Optional[int]


class GoalTrackingService:
    """
    Session 930: Track progress toward user goals.

    Links deliverables and initiatives to goals, calculates progress,
    and provides summary dashboards.
    """

    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes

    def link_deliverable_to_goal(
        self,
        deliverable,
        goal,
        progress_delta: int = 5,
        milestone: str = '',
        notes: str = '',
        is_automatic: bool = True,
    ) -> 'GoalProgress':
        """
        Link a deliverable to a goal and record progress.

        Args:
            deliverable: Deliverable that contributes to goal
            goal: UserGoal being progressed
            progress_delta: Percentage points to add (e.g., 5 = +5%)
            milestone: Optional milestone description
            notes: Optional notes about the contribution
            is_automatic: True if system-detected, False if user-entered

        Returns:
            Created GoalProgress instance
        """
        from core.models_user_learning import GoalProgress

        progress = GoalProgress.objects.create(
            goal=goal,
            deliverable=deliverable,
            progress_delta=progress_delta,
            milestone_reached=milestone,
            notes=notes,
            is_automatic=is_automatic,
        )

        # Invalidate cache
        self._invalidate_cache(goal.user_id)

        logger.info(
            f"Linked deliverable {deliverable.id} to goal '{goal.name}': "
            f"+{progress_delta}%, milestone='{milestone}'"
        )

        return progress

    def link_initiative_to_goal(
        self,
        initiative,
        goal,
        progress_delta: int = 10,
        milestone: str = '',
        notes: str = '',
        is_automatic: bool = True,
    ) -> 'GoalProgress':
        """
        Link an initiative to a goal and record progress.

        Initiatives typically contribute more progress than individual deliverables.

        Args:
            initiative: Initiative that contributes to goal
            goal: UserGoal being progressed
            progress_delta: Percentage points to add (default 10 for initiatives)
            milestone: Optional milestone description
            notes: Optional notes about the contribution
            is_automatic: True if system-detected, False if user-entered

        Returns:
            Created GoalProgress instance
        """
        from core.models_user_learning import GoalProgress

        progress = GoalProgress.objects.create(
            goal=goal,
            initiative=initiative,
            progress_delta=progress_delta,
            milestone_reached=milestone,
            notes=notes,
            is_automatic=is_automatic,
        )

        # Invalidate cache
        self._invalidate_cache(goal.user_id)

        logger.info(
            f"Linked initiative {initiative.id} to goal '{goal.name}': "
            f"+{progress_delta}%, milestone='{milestone}'"
        )

        return progress

    def record_manual_progress(
        self,
        goal,
        progress_delta: int,
        milestone: str = '',
        notes: str = '',
    ) -> 'GoalProgress':
        """
        Record manual progress entry by user.

        Args:
            goal: UserGoal being progressed
            progress_delta: Percentage points to add
            milestone: Optional milestone description
            notes: Optional notes

        Returns:
            Created GoalProgress instance
        """
        from core.models_user_learning import GoalProgress

        progress = GoalProgress.objects.create(
            goal=goal,
            progress_delta=progress_delta,
            milestone_reached=milestone,
            notes=notes,
            is_automatic=False,
        )

        self._invalidate_cache(goal.user_id)

        logger.info(
            f"Manual progress for goal '{goal.name}': +{progress_delta}%"
        )

        return progress

    def calculate_progress(self, goal) -> int:
        """
        Calculate total progress percentage for a goal.

        Returns integer 0-100 representing progress percentage.
        """
        from core.models_user_learning import GoalProgress

        total = GoalProgress.objects.filter(goal=goal).aggregate(
            total=Sum('progress_delta')
        )['total'] or 0

        # Cap at 100%
        return min(100, max(0, total))

    def get_goal_summary(self, goal) -> GoalSummary:
        """
        Get comprehensive summary of a goal's progress.

        Returns GoalSummary with all progress details.
        """
        from core.models_user_learning import GoalProgress

        # Calculate progress
        progress_pct = self.calculate_progress(goal)

        # Get recent contributions (last 10)
        recent = GoalProgress.objects.filter(goal=goal).order_by('-created_at')[:10]
        contributions = []
        for p in recent:
            contrib = {
                'delta': p.progress_delta,
                'milestone': p.milestone_reached,
                'is_automatic': p.is_automatic,
                'created_at': p.created_at.isoformat(),
            }
            if p.deliverable:
                contrib['deliverable_id'] = str(p.deliverable.id)
                contrib['deliverable_title'] = p.deliverable.title
            if p.initiative:
                contrib['initiative_id'] = str(p.initiative.id)
                contrib['initiative_name'] = p.initiative.name
            contributions.append(contrib)

        # Collect milestones
        milestones = list(
            GoalProgress.objects.filter(goal=goal)
            .exclude(milestone_reached='')
            .values_list('milestone_reached', flat=True)
        )

        # Calculate days remaining if target_date exists
        days_remaining = None
        if hasattr(goal, 'target_date') and goal.target_date:
            delta = goal.target_date - timezone.now().date()
            days_remaining = max(0, delta.days)

        # Get target and current values
        target_value = float(getattr(goal, 'target_value', 100))
        current_value = float(getattr(goal, 'current_value', 0))

        return GoalSummary(
            goal_id=str(goal.id),
            name=getattr(goal, 'name', str(goal.id)),
            category=getattr(goal, 'category', 'general'),
            target_value=target_value,
            current_value=current_value,
            progress_percentage=progress_pct,
            status=getattr(goal, 'status', 'active'),
            recent_contributions=contributions,
            milestones_reached=milestones,
            days_remaining=days_remaining,
        )

    def get_user_goals_dashboard(self, user) -> Dict[str, Any]:
        """
        Get dashboard of all user goals with progress.

        Returns dict with goals organized by status and category.
        """
        from core.models import UserGoal

        # Check cache
        cache_key = f"goals_dashboard_{user.id}"
        if cache_key in self._cache:
            cached, timestamp = self._cache[cache_key]
            if (timezone.now() - timestamp).seconds < self._cache_ttl:
                return cached

        # Query all user goals
        goals = UserGoal.objects.filter(user=user)

        active_goals = []
        completed_goals = []
        goals_by_category = {}

        for goal in goals:
            summary = self.get_goal_summary(goal)

            goal_data = {
                'id': summary.goal_id,
                'name': summary.name,
                'category': summary.category,
                'progress': summary.progress_percentage,
                'status': summary.status,
                'days_remaining': summary.days_remaining,
                'milestones': len(summary.milestones_reached),
            }

            if summary.status == 'achieved' or summary.progress_percentage >= 100:
                completed_goals.append(goal_data)
            else:
                active_goals.append(goal_data)

            # Group by category
            if summary.category not in goals_by_category:
                goals_by_category[summary.category] = []
            goals_by_category[summary.category].append(goal_data)

        # Sort active goals by progress (most progress first)
        active_goals.sort(key=lambda g: g['progress'], reverse=True)

        result = {
            'total_goals': goals.count(),
            'active_count': len(active_goals),
            'completed_count': len(completed_goals),
            'average_progress': (
                sum(g['progress'] for g in active_goals) / len(active_goals)
                if active_goals else 0
            ),
            'active_goals': active_goals,
            'completed_goals': completed_goals,
            'by_category': goals_by_category,
        }

        # Cache result
        self._cache[cache_key] = (result, timezone.now())

        return result

    def suggest_goal_for_deliverable(self, user, deliverable) -> Optional['UserGoal']:
        """
        Suggest which goal a deliverable might contribute to.

        Uses deliverable content and metadata to match with user goals.
        """
        from core.models import UserGoal

        goals = UserGoal.objects.filter(user=user, status='active')
        if not goals.exists():
            return None

        deliverable_text = (
            f"{getattr(deliverable, 'title', '')} "
            f"{getattr(deliverable, 'description', '')} "
            f"{getattr(deliverable, 'content', '')[:500]}"
        ).lower()

        best_match = None
        best_score = 0

        for goal in goals:
            goal_text = (
                f"{getattr(goal, 'name', '')} "
                f"{getattr(goal, 'description', '')}"
            ).lower()

            # Simple keyword matching
            goal_words = set(goal_text.split())
            deliverable_words = set(deliverable_text.split())
            overlap = len(goal_words & deliverable_words)

            if overlap > best_score:
                best_score = overlap
                best_match = goal

        # Require minimum overlap
        if best_score >= 2:
            return best_match

        return None

    def auto_link_deliverable(self, deliverable) -> Optional['GoalProgress']:
        """
        Automatically link a deliverable to a matching goal.

        Convenience method that combines suggest + link.
        """
        user = getattr(deliverable, 'user', None)
        if not user:
            # Try to get from initiative
            initiative = getattr(deliverable, 'initiative', None)
            if initiative:
                user = getattr(initiative, 'user', None)

        if not user:
            return None

        goal = self.suggest_goal_for_deliverable(user, deliverable)
        if not goal:
            return None

        return self.link_deliverable_to_goal(
            deliverable=deliverable,
            goal=goal,
            progress_delta=5,
            notes=f"Auto-linked based on content match",
            is_automatic=True,
        )

    def _invalidate_cache(self, user_id):
        """Invalidate cache for a user."""
        cache_key = f"goals_dashboard_{user_id}"
        if cache_key in self._cache:
            del self._cache[cache_key]


# Singleton instance
_goal_tracking_service = None


def get_goal_tracking_service() -> GoalTrackingService:
    """Get singleton instance of GoalTrackingService."""
    global _goal_tracking_service
    if _goal_tracking_service is None:
        _goal_tracking_service = GoalTrackingService()
    return _goal_tracking_service
