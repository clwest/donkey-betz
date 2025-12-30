"""
Session 607: Pilot Progress Dashboard Service

Provides comprehensive progress tracking for running experiments/pilots with:
- KPI progress (target vs current with percentage)
- Health status indicators (on_track, at_risk, overdue, needs_attention)
- Timeline visualization data
- Quick action recommendations
- Aggregate metrics and trends

"I really wanna know whats going on with the Pilots lol" - The User
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import timedelta

from django.db.models import Count, Avg, Q
from django.utils import timezone

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status for experiments."""
    ON_TRACK = "on_track"           # KPI progress >= expected, no issues
    AT_RISK = "at_risk"             # KPI below expected or running long
    NEEDS_ATTENTION = "needs_attention"  # Missing KPIs, no updates
    OVERDUE = "overdue"             # Running too long without progress
    COMPLETED = "completed"         # Finished (success/failure)
    HALTED = "halted"               # Manually or auto halted


@dataclass
class PilotProgress:
    """Progress data for a single pilot/experiment."""
    id: str
    name: str
    hypothesis: str
    status: str
    health_status: str
    days_running: int
    expected_duration_days: int

    # KPI tracking
    primary_kpi: str
    target_value: str
    current_value: str
    kpi_progress_percent: Optional[float]
    kpi_owner: str

    # Timeline
    started_at: str
    updated_at: str
    last_kpi_update: Optional[str]

    # Health indicators
    health_reasons: List[str]
    recommended_actions: List[str]

    # Outcome (if completed)
    outcome_classification: str
    result_summary: str


class PilotProgressService:
    """
    Session 607: Comprehensive pilot/experiment progress tracking.

    Answers the question: "What's going on with the Pilots?"
    """

    # Expected duration for experiments by type (in days)
    DEFAULT_EXPECTED_DURATION = 7  # 1 week default
    EXPECTED_DURATIONS = {
        'quick_test': 3,
        'standard': 7,
        'extended': 14,
        'long_term': 30,
    }

    # Health thresholds
    AT_RISK_DAYS_WITHOUT_UPDATE = 3
    OVERDUE_MULTIPLIER = 1.5  # 1.5x expected duration = overdue

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.PilotProgressService")

    def get_progress_dashboard(self) -> Dict[str, Any]:
        """
        Get comprehensive progress dashboard for all experiments.

        Returns:
            Dict with:
                - experiments: List of experiment progress data
                - summary: Aggregate stats
                - attention_needed: Experiments requiring action
                - health_breakdown: Count by health status
                - timeline: Recent activity timeline
        """
        try:
            from core.models_pilot_readiness import Experiment

            experiments = Experiment.objects.all().select_related(
                'pilot', 'pilot__gate', 'pilot__gate__decision'
            ).order_by('-created_at')

            progress_list = []
            attention_needed = []
            health_counts = {status.value: 0 for status in HealthStatus}

            for exp in experiments:
                progress = self._calculate_progress(exp)
                progress_list.append(self._progress_to_dict(progress))

                # Track health
                health_counts[progress.health_status] += 1

                # Track attention needed
                if progress.health_status in [
                    HealthStatus.AT_RISK.value,
                    HealthStatus.NEEDS_ATTENTION.value,
                    HealthStatus.OVERDUE.value
                ]:
                    attention_needed.append({
                        'id': progress.id,
                        'name': progress.name[:50],
                        'health_status': progress.health_status,
                        'reasons': progress.health_reasons,
                        'actions': progress.recommended_actions,
                    })

            # Summary stats
            summary = self._calculate_summary(experiments, health_counts)

            # Recent activity timeline
            timeline = self._get_activity_timeline(experiments)

            return {
                'success': True,
                'experiments': progress_list,
                'summary': summary,
                'attention_needed': attention_needed,
                'health_breakdown': health_counts,
                'timeline': timeline,
                'timestamp': timezone.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error getting progress dashboard: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
            }

    def get_experiment_progress(self, experiment_id: str) -> Dict[str, Any]:
        """Get detailed progress for a single experiment."""
        try:
            from core.models_pilot_readiness import Experiment

            exp = Experiment.objects.select_related(
                'pilot', 'pilot__gate', 'pilot__gate__decision', 'learning'
            ).get(id=experiment_id)

            progress = self._calculate_progress(exp)

            # Get additional details
            learning = getattr(exp, 'learning', None)

            result = self._progress_to_dict(progress)
            result['details'] = {
                'secondary_kpis': exp.secondary_kpis or [],
                'halt_conditions': exp.halt_conditions or {},
                'extracted_metrics': exp.extracted_metrics or {},
                'learnings': exp.learnings,
                'has_learning_record': learning is not None,
            }

            if learning:
                result['learning'] = {
                    'outcome': learning.outcome,
                    'key_insight': learning.key_insight,
                    'confidence_score': learning.confidence_score,
                }

            return {
                'success': True,
                'experiment': result,
            }

        except Exception as e:
            self.logger.error(f"Error getting experiment progress: {e}")
            return {
                'success': False,
                'error': str(e),
            }

    def _calculate_progress(self, exp) -> PilotProgress:
        """Calculate progress metrics for an experiment."""
        now = timezone.now()
        started = exp.started_at or exp.created_at
        days_running = (now - started).days

        # Determine expected duration
        expected_duration = self._get_expected_duration(exp)

        # Calculate KPI progress
        kpi_progress = self._calculate_kpi_progress(
            exp.current_value,
            exp.target_value
        )

        # Determine health status and reasons
        health_status, health_reasons = self._assess_health(
            exp, days_running, expected_duration, kpi_progress
        )

        # Generate recommended actions
        actions = self._generate_actions(
            exp, health_status, health_reasons, days_running
        )

        # Last KPI update (approximated from updated_at)
        last_kpi_update = None
        if exp.current_value:
            last_kpi_update = exp.updated_at.isoformat()

        return PilotProgress(
            id=str(exp.id),
            name=exp.name or 'Unnamed Experiment',
            hypothesis=exp.hypothesis or '',
            status=exp.status,
            health_status=health_status,
            days_running=days_running,
            expected_duration_days=expected_duration,
            primary_kpi=exp.primary_kpi or 'Not set',
            target_value=exp.target_value or '',
            current_value=exp.current_value or '',
            kpi_progress_percent=kpi_progress,
            kpi_owner=exp.kpi_owner or 'Unassigned',
            started_at=started.isoformat() if started else '',
            updated_at=exp.updated_at.isoformat() if exp.updated_at else '',
            last_kpi_update=last_kpi_update,
            health_reasons=health_reasons,
            recommended_actions=actions,
            outcome_classification=exp.outcome_classification,
            result_summary=exp.result_summary or '',
        )

    def _get_expected_duration(self, exp) -> int:
        """Determine expected duration based on experiment metadata."""
        # Check if duration hint is in extracted_metrics
        if exp.extracted_metrics:
            duration_hint = exp.extracted_metrics.get('expected_duration')
            if duration_hint:
                for key, days in self.EXPECTED_DURATIONS.items():
                    if key in str(duration_hint).lower():
                        return days

        # Check if it's a "quick" or "test" experiment
        name_lower = (exp.name or '').lower()
        if 'quick' in name_lower or 'test' in name_lower:
            return self.EXPECTED_DURATIONS['quick_test']
        elif 'long' in name_lower or 'extended' in name_lower:
            return self.EXPECTED_DURATIONS['extended']

        return self.DEFAULT_EXPECTED_DURATION

    def _calculate_kpi_progress(
        self,
        current: Optional[str],
        target: Optional[str]
    ) -> Optional[float]:
        """Calculate KPI progress as percentage."""
        if not current or not target:
            return None

        try:
            # Try to extract numeric values
            current_num = self._extract_number(current)
            target_num = self._extract_number(target)

            if current_num is not None and target_num is not None and target_num != 0:
                progress = (current_num / target_num) * 100
                return round(min(progress, 200), 1)  # Cap at 200%

            return None
        except (ValueError, TypeError):
            return None

    def _extract_number(self, value: str) -> Optional[float]:
        """Extract numeric value from string like '50%' or '15.5'."""
        if not value:
            return None

        # Remove common suffixes
        cleaned = value.replace('%', '').replace('$', '').replace(',', '').strip()

        try:
            return float(cleaned)
        except ValueError:
            return None

    def _assess_health(
        self,
        exp,
        days_running: int,
        expected_duration: int,
        kpi_progress: Optional[float]
    ) -> tuple:
        """Assess health status and return status + reasons."""
        reasons = []

        # Check if halted
        if exp.is_halted:
            return HealthStatus.HALTED.value, [f"Halted: {exp.halt_reason or 'No reason given'}"]

        # Check if completed
        if exp.status in ['success', 'failure', 'partial', 'inconclusive']:
            return HealthStatus.COMPLETED.value, [f"Completed with status: {exp.status}"]

        # Check for overdue
        overdue_threshold = expected_duration * self.OVERDUE_MULTIPLIER
        if days_running > overdue_threshold:
            reasons.append(f"Running {days_running} days (expected {expected_duration})")
            return HealthStatus.OVERDUE.value, reasons

        # Check for missing KPIs
        if not exp.primary_kpi or exp.primary_kpi == 'Not set':
            reasons.append("No primary KPI defined")

        if not exp.target_value:
            reasons.append("No target value set")

        if not exp.current_value:
            reasons.append("No current value recorded")

        if len(reasons) >= 2:
            return HealthStatus.NEEDS_ATTENTION.value, reasons

        # Check KPI progress vs time progress
        if kpi_progress is not None:
            time_progress = (days_running / expected_duration) * 100
            if kpi_progress < time_progress * 0.5:  # Less than half expected progress
                reasons.append(f"KPI at {kpi_progress}% but {round(time_progress)}% of time elapsed")
                return HealthStatus.AT_RISK.value, reasons

        # Check for stale experiments (no recent updates)
        if exp.updated_at:
            days_since_update = (timezone.now() - exp.updated_at).days
            if days_since_update >= self.AT_RISK_DAYS_WITHOUT_UPDATE:
                reasons.append(f"No updates in {days_since_update} days")
                return HealthStatus.AT_RISK.value, reasons

        # All good!
        if reasons:
            return HealthStatus.NEEDS_ATTENTION.value, reasons

        return HealthStatus.ON_TRACK.value, ["Progressing as expected"]

    def _generate_actions(
        self,
        exp,
        health_status: str,
        reasons: List[str],
        days_running: int
    ) -> List[str]:
        """Generate recommended actions based on health status."""
        actions = []

        if health_status == HealthStatus.NEEDS_ATTENTION.value:
            if not exp.primary_kpi or exp.primary_kpi == 'Not set':
                actions.append("Define a primary KPI to track")
            if not exp.target_value:
                actions.append("Set a target value for the KPI")
            if not exp.current_value:
                actions.append("Record current KPI value")

        elif health_status == HealthStatus.AT_RISK.value:
            actions.append("Review experiment progress immediately")
            if 'No updates' in str(reasons):
                actions.append("Update KPI with current measurements")
            if 'KPI at' in str(reasons):
                actions.append("Consider if hypothesis needs adjustment")
                actions.append("Evaluate if experiment should continue")

        elif health_status == HealthStatus.OVERDUE.value:
            actions.append("Decide: complete with current learnings or extend with justification")
            actions.append("Document why experiment is taking longer")
            if not exp.current_value:
                actions.append("Record final KPI measurement")

        elif health_status == HealthStatus.ON_TRACK.value:
            if days_running >= 3 and not exp.current_value:
                actions.append("Consider recording first KPI measurement")

        return actions

    def _calculate_summary(self, experiments, health_counts: Dict) -> Dict:
        """Calculate summary statistics."""
        total = experiments.count()
        running = experiments.filter(status='running').count()
        completed = total - running

        # Success rate for completed experiments
        success = experiments.filter(status='success').count()
        success_rate = round((success / completed * 100), 1) if completed > 0 else 0

        # Average days running for active experiments
        running_exps = experiments.filter(status='running')
        avg_days = 0
        if running_exps.exists():
            now = timezone.now()
            days_list = [(now - (e.started_at or e.created_at)).days for e in running_exps]
            avg_days = round(sum(days_list) / len(days_list), 1)

        # KPI completion rate
        with_kpis = experiments.filter(
            ~Q(primary_kpi='') & ~Q(primary_kpi__isnull=True)
        ).count()
        kpi_completion = round((with_kpis / total * 100), 1) if total > 0 else 0

        # Healthy percentage
        healthy = health_counts.get(HealthStatus.ON_TRACK.value, 0)
        healthy_percent = round((healthy / running * 100), 1) if running > 0 else 100

        return {
            'total_experiments': total,
            'running': running,
            'completed': completed,
            'success_count': success,
            'success_rate': success_rate,
            'avg_days_running': avg_days,
            'kpi_completion_rate': kpi_completion,
            'healthy_percent': healthy_percent,
            'needs_attention': (
                health_counts.get(HealthStatus.AT_RISK.value, 0) +
                health_counts.get(HealthStatus.NEEDS_ATTENTION.value, 0) +
                health_counts.get(HealthStatus.OVERDUE.value, 0)
            ),
        }

    def _get_activity_timeline(self, experiments) -> List[Dict]:
        """Get recent activity timeline."""
        timeline = []
        now = timezone.now()

        for exp in experiments[:10]:  # Last 10 experiments
            started = exp.started_at or exp.created_at

            # Add start event
            timeline.append({
                'experiment_id': str(exp.id),
                'experiment_name': (exp.name or 'Unnamed')[:40],
                'event_type': 'started',
                'timestamp': started.isoformat(),
                'days_ago': (now - started).days,
            })

            # Add completion event if applicable
            if exp.ended_at:
                timeline.append({
                    'experiment_id': str(exp.id),
                    'experiment_name': (exp.name or 'Unnamed')[:40],
                    'event_type': 'completed',
                    'outcome': exp.status,
                    'timestamp': exp.ended_at.isoformat(),
                    'days_ago': (now - exp.ended_at).days,
                })

            # Add halt event if applicable
            if exp.halted_at:
                timeline.append({
                    'experiment_id': str(exp.id),
                    'experiment_name': (exp.name or 'Unnamed')[:40],
                    'event_type': 'halted',
                    'reason': exp.halt_reason or 'No reason',
                    'timestamp': exp.halted_at.isoformat(),
                    'days_ago': (now - exp.halted_at).days,
                })

        # Sort by timestamp descending
        timeline.sort(key=lambda x: x['timestamp'], reverse=True)

        return timeline[:20]  # Return last 20 events

    def _progress_to_dict(self, progress: PilotProgress) -> Dict:
        """Convert PilotProgress to dictionary."""
        return {
            'id': progress.id,
            'name': progress.name,
            'hypothesis': progress.hypothesis[:200] if progress.hypothesis else '',
            'status': progress.status,
            'health_status': progress.health_status,
            'days_running': progress.days_running,
            'expected_duration_days': progress.expected_duration_days,
            'kpi': {
                'primary': progress.primary_kpi,
                'target': progress.target_value,
                'current': progress.current_value,
                'progress_percent': progress.kpi_progress_percent,
                'owner': progress.kpi_owner,
            },
            'timeline': {
                'started_at': progress.started_at,
                'updated_at': progress.updated_at,
                'last_kpi_update': progress.last_kpi_update,
            },
            'health': {
                'status': progress.health_status,
                'reasons': progress.health_reasons,
                'recommended_actions': progress.recommended_actions,
            },
            'outcome': {
                'classification': progress.outcome_classification,
                'result_summary': progress.result_summary[:200] if progress.result_summary else '',
            },
        }


# Convenience functions
def get_pilot_progress_dashboard() -> Dict[str, Any]:
    """Get pilot progress dashboard."""
    service = PilotProgressService()
    return service.get_progress_dashboard()


def get_experiment_detail(experiment_id: str) -> Dict[str, Any]:
    """Get detailed progress for single experiment."""
    service = PilotProgressService()
    return service.get_experiment_progress(experiment_id)
