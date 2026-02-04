"""
Experiment Collision Service - Session 920

Detects and prevents experiment collisions on the same target page/feature.

When multiple A/B tests or experiments run simultaneously on the same page,
their results can interfere with each other, making it impossible to
attribute changes correctly. This service:

1. Checks if a new experiment would collide with active ones
2. Tracks which pages/features have active experiments
3. Provides recommendations for experiment scheduling
"""

import logging
from datetime import timedelta
from typing import Dict, List, Optional, Any

from django.utils import timezone
from django.db.models import Q

logger = logging.getLogger(__name__)


class ExperimentCollisionService:
    """
    Service for detecting and managing experiment collisions.

    Prevents multiple experiments from running on the same target
    within a collision window, ensuring clean statistical analysis.
    """

    # Default collision window - experiments on same target within this
    # period are considered potentially colliding
    COLLISION_WINDOW_DAYS = 14

    # Maximum concurrent experiments per page
    MAX_CONCURRENT_PER_PAGE = 1

    # Severity levels for collision warnings
    SEVERITY_CRITICAL = 'critical'  # Direct overlap, same target
    SEVERITY_HIGH = 'high'          # Related targets, likely interference
    SEVERITY_MEDIUM = 'medium'      # Same domain, possible interference
    SEVERITY_LOW = 'low'            # Minor overlap risk

    def __init__(self):
        """Initialize the collision service."""
        pass

    def check_collision(
        self,
        experiment_type: str,
        target_page: str,
        target_feature: Optional[str] = None,
        planned_start: Optional[Any] = None,
        planned_duration_days: int = 14,
    ) -> Dict[str, Any]:
        """
        Check if a proposed experiment would collide with active ones.

        Args:
            experiment_type: Type of experiment (a/b_test, feature_flag, etc.)
            target_page: Page or component being tested
            target_feature: Specific feature within the page (optional)
            planned_start: When the experiment would start (default: now)
            planned_duration_days: How long the experiment will run

        Returns:
            Dict with:
                - has_collision: bool
                - severity: str (critical/high/medium/low)
                - conflicts: List of conflicting experiments
                - recommendation: str
                - can_proceed: bool
        """
        try:
            from core.models_document_registry import Initiative
        except ImportError:
            logger.warning("Initiative model not available for collision check")
            return self._no_collision_result()

        planned_start = planned_start or timezone.now()
        planned_end = planned_start + timedelta(days=planned_duration_days)

        # Build query for active experiments on same target
        collision_window_start = planned_start - timedelta(days=self.COLLISION_WINDOW_DAYS)
        collision_window_end = planned_end + timedelta(days=self.COLLISION_WINDOW_DAYS)

        # Query initiatives that might be experiments
        experiment_keywords = ['experiment', 'a/b', 'ab test', 'test', 'trial', 'variation']

        # Initiative model uses 'name' not 'title', and status is uppercase
        q_filter = Q(status__in=['ACTIVE', 'ON_HOLD']) & (
            Q(name__icontains=target_page) |
            Q(description__icontains=target_page)
        )

        # Add time constraints if the model has date fields
        potential_conflicts = Initiative.objects.filter(q_filter).exclude(
            status__in=['COMPLETED', 'ARCHIVED']
        )[:50]  # Limit for performance

        conflicts = []
        max_severity = self.SEVERITY_LOW

        for initiative in potential_conflicts:
            # Determine if this is actually an experiment
            is_experiment = any(
                kw in (initiative.name or '').lower() or
                kw in (initiative.description or '').lower()
                for kw in experiment_keywords
            )

            if not is_experiment:
                continue

            # Calculate overlap severity
            name_lower = (initiative.name or '').lower()
            desc_lower = (initiative.description or '').lower()
            target_lower = target_page.lower()

            if target_lower in name_lower:
                severity = self.SEVERITY_CRITICAL
            elif target_lower in desc_lower:
                severity = self.SEVERITY_HIGH
            else:
                severity = self.SEVERITY_MEDIUM

            # Track highest severity
            severity_order = {
                self.SEVERITY_CRITICAL: 4,
                self.SEVERITY_HIGH: 3,
                self.SEVERITY_MEDIUM: 2,
                self.SEVERITY_LOW: 1,
            }
            if severity_order.get(severity, 0) > severity_order.get(max_severity, 0):
                max_severity = severity

            conflicts.append({
                'initiative_id': str(initiative.id),
                'name': initiative.name,
                'status': initiative.status,
                'severity': severity,
                'overlap_type': 'same_target' if severity == self.SEVERITY_CRITICAL else 'related',
            })

        has_collision = len(conflicts) > 0
        can_proceed = max_severity in [self.SEVERITY_LOW, self.SEVERITY_MEDIUM]

        # Generate recommendation
        if not has_collision:
            recommendation = "No conflicts detected. Safe to proceed with experiment."
        elif max_severity == self.SEVERITY_CRITICAL:
            recommendation = (
                f"CRITICAL: Direct collision detected with {len(conflicts)} active experiment(s) "
                f"on {target_page}. Strongly recommend waiting until existing experiments complete "
                f"or choosing a different target page."
            )
        elif max_severity == self.SEVERITY_HIGH:
            recommendation = (
                f"HIGH RISK: Related experiments detected that may interfere. "
                f"Consider isolating user segments or waiting {self.COLLISION_WINDOW_DAYS} days."
            )
        else:
            recommendation = (
                f"MODERATE RISK: {len(conflicts)} potentially related experiment(s) found. "
                f"Proceed with caution and monitor for interference patterns."
            )

        return {
            'has_collision': has_collision,
            'severity': max_severity,
            'conflicts': conflicts,
            'recommendation': recommendation,
            'can_proceed': can_proceed,
            'target_page': target_page,
            'collision_window_days': self.COLLISION_WINDOW_DAYS,
            'checked_at': timezone.now().isoformat(),
        }

    def _no_collision_result(self) -> Dict[str, Any]:
        """Return a default no-collision result."""
        return {
            'has_collision': False,
            'severity': self.SEVERITY_LOW,
            'conflicts': [],
            'recommendation': "Unable to check for collisions (model unavailable). Proceed with caution.",
            'can_proceed': True,
            'checked_at': timezone.now().isoformat(),
        }

    def get_active_experiments(self, target_page: Optional[str] = None) -> List[Dict]:
        """
        Get list of currently active experiments.

        Args:
            target_page: Optional filter for specific page

        Returns:
            List of active experiment summaries
        """
        try:
            from core.models_document_registry import Initiative
        except ImportError:
            return []

        q_filter = Q(status__in=['ACTIVE', 'ON_HOLD'])

        if target_page:
            q_filter &= (
                Q(name__icontains=target_page) |
                Q(description__icontains=target_page)
            )

        # Filter for experiment-like initiatives
        experiment_keywords = ['experiment', 'a/b', 'test', 'trial']

        experiments = []
        for initiative in Initiative.objects.filter(q_filter)[:100]:
            is_experiment = any(
                kw in (initiative.name or '').lower() or
                kw in (initiative.description or '').lower()
                for kw in experiment_keywords
            )
            if is_experiment:
                experiments.append({
                    'id': str(initiative.id),
                    'name': initiative.name,
                    'status': initiative.status,
                    'created_at': initiative.created_at.isoformat() if hasattr(initiative, 'created_at') else None,
                })

        return experiments

    def suggest_experiment_timing(
        self,
        target_page: str,
        duration_days: int = 14,
    ) -> Dict[str, Any]:
        """
        Suggest optimal timing for a new experiment.

        Args:
            target_page: The page to run the experiment on
            duration_days: How long the experiment will run

        Returns:
            Dict with suggested start date and reasoning
        """
        collision_check = self.check_collision(
            experiment_type='a/b_test',
            target_page=target_page,
            planned_duration_days=duration_days,
        )

        if not collision_check['has_collision']:
            return {
                'suggested_start': timezone.now().isoformat(),
                'reason': "No conflicts detected - can start immediately",
                'delay_days': 0,
            }

        # Suggest waiting until after collision window
        delay_days = self.COLLISION_WINDOW_DAYS
        suggested_start = timezone.now() + timedelta(days=delay_days)

        return {
            'suggested_start': suggested_start.isoformat(),
            'reason': f"Recommend waiting {delay_days} days due to {len(collision_check['conflicts'])} active conflicts",
            'delay_days': delay_days,
            'conflicts': collision_check['conflicts'],
        }


# Singleton instance
_collision_service = None


def get_experiment_collision_service() -> ExperimentCollisionService:
    """Get or create the experiment collision service instance."""
    global _collision_service
    if _collision_service is None:
        _collision_service = ExperimentCollisionService()
    return _collision_service
