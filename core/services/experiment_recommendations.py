"""
Session 615: Experiment Recommendations Service

Analyzes running experiments and generates AI-powered recommendations:
1. Scale up - experiments exceeding targets
2. Investigate - experiments with declining KPIs
3. Adjust - experiments that are stalled
4. Continue - experiments on track
5. Consider ending - experiments not meeting goals

Uses KPI trends, alerts, and experiment metadata to generate actionable next steps.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import timedelta
from django.utils import timezone

logger = logging.getLogger(__name__)


class ExperimentRecommendationService:
    """
    Session 615: Generates recommendations for running experiments.

    Analyzes:
    - KPI trend direction (up/down/stable)
    - Target vs current value
    - Days running vs expected duration
    - Recent alerts
    - Source performance
    """

    # Recommendation types with priorities
    SCALE_UP = 'scale_up'           # Exceeding expectations - consider expanding
    INVESTIGATE = 'investigate'      # Declining - needs attention
    ADJUST = 'adjust'               # Stalled - try something different
    CONTINUE = 'continue'           # On track - keep going
    CELEBRATE = 'celebrate'         # Target exceeded - success!
    END_EARLY = 'end_early'         # Not working - cut losses

    # Priority order (lower = more urgent)
    PRIORITY_ORDER = {
        INVESTIGATE: 1,
        END_EARLY: 2,
        SCALE_UP: 3,
        CELEBRATE: 4,
        ADJUST: 5,
        CONTINUE: 6,
    }

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ExperimentRecommendationService")

    def get_all_recommendations(self) -> Dict[str, Any]:
        """
        Get recommendations for all running experiments.

        Returns:
            Dict with recommendations list, summary, and metadata
        """
        from core.models_pilot_readiness import Experiment, KPISnapshot
        from core.services.kpi_alerts import KPIAlertService

        results = {
            'success': True,
            'recommendations': [],
            'summary': {
                'total': 0,
                'by_type': {},
                'action_needed': 0,
            },
            'timestamp': timezone.now().isoformat(),
        }

        try:
            running = Experiment.objects.filter(status='running')
            results['summary']['total'] = running.count()

            # Get alerts for context
            alert_service = KPIAlertService()
            alerts_result = alert_service.check_all_experiments()
            alerts_by_exp = {}
            for alert in alerts_result.get('alerts', []):
                exp_id = alert.get('experiment_id')
                if exp_id not in alerts_by_exp:
                    alerts_by_exp[exp_id] = []
                alerts_by_exp[exp_id].append(alert)

            for exp in running:
                rec = self._analyze_experiment(exp, alerts_by_exp.get(str(exp.id), []))
                results['recommendations'].append(rec)

                # Update summary
                rec_type = rec['recommendation_type']
                results['summary']['by_type'][rec_type] = results['summary']['by_type'].get(rec_type, 0) + 1

                if rec_type in [self.INVESTIGATE, self.END_EARLY, self.SCALE_UP]:
                    results['summary']['action_needed'] += 1

            # Sort by priority
            results['recommendations'].sort(
                key=lambda r: self.PRIORITY_ORDER.get(r['recommendation_type'], 99)
            )

        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}", exc_info=True)
            results['success'] = False
            results['error'] = str(e)

        return results

    def _analyze_experiment(self, exp, alerts: List[Dict]) -> Dict[str, Any]:
        """Analyze a single experiment and generate recommendation."""
        from core.models_pilot_readiness import KPISnapshot

        # Get trend data
        lookback = timezone.now() - timedelta(days=14)
        snapshots = list(KPISnapshot.objects.filter(
            experiment=exp,
            captured_at__gte=lookback
        ).order_by('captured_at'))

        # Calculate trend
        trend_direction = 'unknown'
        trend_strength = 0
        current_value = None

        if len(snapshots) >= 2:
            first_val = snapshots[0].numeric_value or 0
            last_val = snapshots[-1].numeric_value or 0
            current_value = last_val

            if first_val > 0:
                change_pct = (last_val - first_val) / first_val * 100
                trend_strength = abs(change_pct)

                if change_pct > 10:
                    trend_direction = 'up'
                elif change_pct < -10:
                    trend_direction = 'down'
                else:
                    trend_direction = 'stable'
        elif len(snapshots) == 1:
            current_value = snapshots[0].numeric_value
            trend_direction = 'collecting'

        # Parse target value
        target_value = None
        if exp.target_value:
            try:
                target_value = float(exp.target_value.replace('%', '').replace(',', ''))
            except (ValueError, AttributeError):
                pass

        # Calculate progress
        progress_pct = None
        if target_value and current_value is not None and target_value > 0:
            progress_pct = (current_value / target_value) * 100

        # Calculate days running
        days_running = 0
        if exp.started_at:
            days_running = (timezone.now() - exp.started_at).days

        # Determine recommendation
        rec_type, reason, action = self._determine_recommendation(
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            progress_pct=progress_pct,
            days_running=days_running,
            alerts=alerts,
            current_value=current_value,
            target_value=target_value,
        )

        # Clean up name
        name = exp.name or 'Unnamed Experiment'
        for prefix in ['Experiment:', 'Discussion:', '[Synthesis]', '[Learned]']:
            name = name.replace(prefix, '').strip()

        return {
            'experiment_id': str(exp.id),
            'experiment_name': name[:60],
            'recommendation_type': rec_type,
            'reason': reason,
            'action': action,
            'icon': self._get_icon(rec_type),
            'priority': self.PRIORITY_ORDER.get(rec_type, 99),
            'metrics': {
                'current_value': current_value,
                'target_value': target_value,
                'progress_pct': round(progress_pct, 1) if progress_pct else None,
                'trend_direction': trend_direction,
                'trend_strength': round(trend_strength, 1),
                'days_running': days_running,
                'data_points': len(snapshots),
                'alert_count': len(alerts),
            },
            'kpi': exp.primary_kpi,
        }

    def _determine_recommendation(
        self,
        trend_direction: str,
        trend_strength: float,
        progress_pct: Optional[float],
        days_running: int,
        alerts: List[Dict],
        current_value: Optional[float],
        target_value: Optional[float],
    ) -> tuple:
        """
        Determine recommendation type, reason, and action.

        Returns:
            (recommendation_type, reason, action)
        """

        # Check for target exceeded
        if progress_pct and progress_pct >= 100:
            return (
                self.CELEBRATE,
                f"Target exceeded! Currently at {progress_pct:.0f}% of goal",
                "Consider marking as success or setting a higher target"
            )

        # Check for strong positive trend
        if trend_direction == 'up' and trend_strength > 25:
            if progress_pct and progress_pct >= 80:
                return (
                    self.SCALE_UP,
                    f"Strong growth (+{trend_strength:.0f}%) and {progress_pct:.0f}% to target",
                    "Consider scaling up resources or expanding scope"
                )
            return (
                self.CONTINUE,
                f"Good momentum with +{trend_strength:.0f}% growth",
                "Keep current approach - it's working"
            )

        # Check for critical alerts
        critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
        if critical_alerts:
            return (
                self.INVESTIGATE,
                f"{len(critical_alerts)} critical alert(s) detected",
                "Immediate investigation needed - check data sources and methodology"
            )

        # Check for declining trend
        if trend_direction == 'down':
            if trend_strength > 30:
                return (
                    self.INVESTIGATE,
                    f"Significant decline (-{trend_strength:.0f}%)",
                    "Investigate cause and consider pivoting approach"
                )
            if days_running > 14 and progress_pct and progress_pct < 30:
                return (
                    self.END_EARLY,
                    f"Declining after {days_running} days with only {progress_pct:.0f}% progress",
                    "Consider ending experiment and trying a different approach"
                )
            return (
                self.ADJUST,
                f"Declining trend (-{trend_strength:.0f}%)",
                "Try adjusting parameters or methodology"
            )

        # Check for stalled progress
        if trend_direction == 'stable' and days_running > 7:
            if progress_pct and progress_pct < 50:
                return (
                    self.ADJUST,
                    f"Stalled at {progress_pct:.0f}% for {days_running} days",
                    "Try a different approach or add more resources"
                )
            return (
                self.CONTINUE,
                "Steady progress - stable trend",
                "Continue monitoring, consider optimizations"
            )

        # Check for new experiments still collecting data
        if trend_direction in ['collecting', 'unknown']:
            return (
                self.CONTINUE,
                "Still collecting initial data",
                f"Wait for more data points (currently {days_running} days in)"
            )

        # Default: on track
        if progress_pct:
            return (
                self.CONTINUE,
                f"On track at {progress_pct:.0f}% of target",
                "Continue current approach"
            )

        return (
            self.CONTINUE,
            "Experiment running normally",
            "Continue monitoring progress"
        )

    def _get_icon(self, rec_type: str) -> str:
        """Get emoji icon for recommendation type."""
        icons = {
            self.SCALE_UP: '🚀',
            self.INVESTIGATE: '🔍',
            self.ADJUST: '🔧',
            self.CONTINUE: '✅',
            self.CELEBRATE: '🎉',
            self.END_EARLY: '⏹️',
        }
        return icons.get(rec_type, '📊')


# Convenience function
def get_experiment_recommendations() -> Dict[str, Any]:
    """Get recommendations for all running experiments."""
    service = ExperimentRecommendationService()
    return service.get_all_recommendations()
