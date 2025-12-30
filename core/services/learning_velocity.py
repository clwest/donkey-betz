"""
Session 603: Learning Velocity Dashboard

Tracks how fast the system learns and visualizes momentum over time.

Key metrics:
1. Learning Rate - New learnings per day/week
2. Velocity Trend - Is learning accelerating or slowing?
3. Theme Momentum - Which themes are improving/declining?
4. Cumulative Progress - Total learning weight over time

Uses ChatGPT's weighted learning formula from Session 601.
"""

import logging
from datetime import timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

from django.db.models import Count, Avg, Q
from django.db.models.functions import TruncDate, TruncWeek
from django.utils import timezone

logger = logging.getLogger(__name__)


class LearningVelocityService:
    """
    Session 603: Learning Velocity Dashboard Service.

    Tracks:
    - How fast the system accumulates learning
    - Whether learning is accelerating or slowing
    - Which themes are improving vs declining
    """

    def __init__(self):
        from core.services.weighted_learning import WeightedLearningService
        self.learning_service = WeightedLearningService()

    def get_velocity_dashboard(self, days: int = 30) -> Dict[str, Any]:
        """
        Get complete learning velocity dashboard data.

        Args:
            days: Number of days to analyze (default 30)

        Returns comprehensive velocity metrics and trends.
        """
        now = timezone.now()
        start_date = now - timedelta(days=days)

        # Get all metrics
        daily_velocity = self._get_daily_velocity(start_date, now)
        weekly_summary = self._get_weekly_summary(start_date, now)
        theme_momentum = self._get_theme_momentum(start_date, now)
        overall_health = self._calculate_overall_health(daily_velocity, theme_momentum)
        velocity_trend = self._calculate_velocity_trend(daily_velocity)

        return {
            'period': {
                'days': days,
                'start_date': start_date.isoformat(),
                'end_date': now.isoformat(),
            },
            'overall_health': overall_health,
            'velocity_trend': velocity_trend,
            'daily_velocity': daily_velocity,
            'weekly_summary': weekly_summary,
            'theme_momentum': theme_momentum,
            'timestamp': now.isoformat(),
        }

    def _get_daily_velocity(self, start_date, end_date) -> List[Dict]:
        """Calculate daily learning velocity with weighted scores."""
        from core.models_pilot_readiness import Experiment, ExperimentLearning

        # Get experiments by day
        experiments = Experiment.objects.filter(
            ended_at__gte=start_date,
            ended_at__lte=end_date
        ).exclude(outcome_classification='pending').order_by('ended_at')

        # Group by date
        daily_data = defaultdict(lambda: {
            'pass_count': 0,
            'learn_count': 0,
            'fail_count': 0,
            'total_weight': 0.0,
            'positive_weight': 0.0,
            'negative_weight': 0.0,
        })

        now = timezone.now()
        for exp in experiments:
            date_key = exp.ended_at.date().isoformat()

            # Calculate weight
            age_days = (now - exp.ended_at).total_seconds() / 86400
            learning_count = ExperimentLearning.objects.filter(experiment=exp).count()
            sample_size = max(1, learning_count)

            weight_data = self.learning_service.calculate_learning_weight(
                outcome_classification=exp.outcome_classification,
                halt_reason=exp.halt_reason,
                sample_size=sample_size,
                age_days=age_days
            )

            weight = weight_data['learning_weight']
            daily_data[date_key]['total_weight'] += weight

            if weight > 0:
                daily_data[date_key]['positive_weight'] += weight
            else:
                daily_data[date_key]['negative_weight'] += weight

            if exp.outcome_classification == 'pass':
                daily_data[date_key]['pass_count'] += 1
            elif exp.outcome_classification == 'learn':
                daily_data[date_key]['learn_count'] += 1
            elif exp.outcome_classification == 'fail':
                daily_data[date_key]['fail_count'] += 1

        # Convert to sorted list
        result = []
        for date_str in sorted(daily_data.keys()):
            data = daily_data[date_str]
            total_experiments = data['pass_count'] + data['learn_count'] + data['fail_count']
            result.append({
                'date': date_str,
                'experiments': total_experiments,
                'pass_count': data['pass_count'],
                'learn_count': data['learn_count'],
                'fail_count': data['fail_count'],
                'total_weight': round(data['total_weight'], 3),
                'positive_weight': round(data['positive_weight'], 3),
                'negative_weight': round(data['negative_weight'], 3),
                'net_velocity': round(data['total_weight'], 3),
            })

        return result

    def _get_weekly_summary(self, start_date, end_date) -> List[Dict]:
        """Get weekly learning summary."""
        from core.models_pilot_readiness import Experiment, ExperimentLearning

        # Group experiments by week
        experiments = Experiment.objects.filter(
            ended_at__gte=start_date,
            ended_at__lte=end_date
        ).exclude(outcome_classification='pending')

        weekly_data = defaultdict(lambda: {
            'experiments': 0,
            'pass_rate': 0,
            'total_weight': 0.0,
            'pass_count': 0,
            'fail_count': 0,
        })

        now = timezone.now()
        for exp in experiments:
            # Get week start (Monday)
            week_start = exp.ended_at - timedelta(days=exp.ended_at.weekday())
            week_key = week_start.date().isoformat()

            weekly_data[week_key]['experiments'] += 1

            if exp.outcome_classification == 'pass':
                weekly_data[week_key]['pass_count'] += 1
            elif exp.outcome_classification == 'fail':
                weekly_data[week_key]['fail_count'] += 1

            # Calculate weight
            age_days = (now - exp.ended_at).total_seconds() / 86400
            learning_count = ExperimentLearning.objects.filter(experiment=exp).count()
            sample_size = max(1, learning_count)

            weight_data = self.learning_service.calculate_learning_weight(
                outcome_classification=exp.outcome_classification,
                halt_reason=exp.halt_reason,
                sample_size=sample_size,
                age_days=age_days
            )
            weekly_data[week_key]['total_weight'] += weight_data['learning_weight']

        # Calculate pass rates and format
        result = []
        for week_str in sorted(weekly_data.keys()):
            data = weekly_data[week_str]
            total = data['experiments']
            pass_rate = (data['pass_count'] / total * 100) if total > 0 else 0

            result.append({
                'week_start': week_str,
                'experiments': total,
                'pass_count': data['pass_count'],
                'fail_count': data['fail_count'],
                'pass_rate': round(pass_rate, 1),
                'total_weight': round(data['total_weight'], 3),
                'avg_weight_per_experiment': round(data['total_weight'] / total, 3) if total > 0 else 0,
            })

        return result

    def _get_theme_momentum(self, start_date, end_date) -> List[Dict]:
        """
        Calculate momentum for each theme/topic.

        Identifies:
        - Themes with positive momentum (improving)
        - Themes with negative momentum (declining)
        - Stale themes (no recent activity)
        """
        from core.models_pilot_readiness import Experiment, ExperimentLearning

        # Get all experiments in period
        experiments = Experiment.objects.filter(
            ended_at__gte=start_date,
            ended_at__lte=end_date
        ).exclude(outcome_classification='pending')

        # Extract themes from experiment names
        theme_data = defaultdict(lambda: {
            'experiments': [],
            'recent_weight': 0.0,
            'older_weight': 0.0,
        })

        now = timezone.now()
        mid_point = start_date + (end_date - start_date) / 2

        for exp in experiments:
            # Extract theme from experiment name (first 2-3 words)
            words = exp.name.split()[:3]
            theme = ' '.join(words) if words else 'Unknown'

            # Calculate weight
            age_days = (now - exp.ended_at).total_seconds() / 86400
            learning_count = ExperimentLearning.objects.filter(experiment=exp).count()
            sample_size = max(1, learning_count)

            weight_data = self.learning_service.calculate_learning_weight(
                outcome_classification=exp.outcome_classification,
                halt_reason=exp.halt_reason,
                sample_size=sample_size,
                age_days=age_days
            )

            theme_data[theme]['experiments'].append({
                'name': exp.name,
                'outcome': exp.outcome_classification,
                'weight': weight_data['learning_weight'],
                'date': exp.ended_at.isoformat(),
            })

            # Split into recent vs older
            if exp.ended_at >= mid_point:
                theme_data[theme]['recent_weight'] += weight_data['learning_weight']
            else:
                theme_data[theme]['older_weight'] += weight_data['learning_weight']

        # Calculate momentum and format
        result = []
        for theme, data in theme_data.items():
            recent = data['recent_weight']
            older = data['older_weight']
            total = recent + older

            # Calculate momentum direction
            if len(data['experiments']) < 2:
                momentum = 'insufficient'
                momentum_score = 0
            elif recent > older + 0.2:
                momentum = 'accelerating'
                momentum_score = min(100, int((recent - older) * 50))
            elif recent < older - 0.2:
                momentum = 'declining'
                momentum_score = max(-100, int((recent - older) * 50))
            else:
                momentum = 'stable'
                momentum_score = 0

            # Determine health indicator
            if total > 0.5 and momentum in ('accelerating', 'stable'):
                health = 'healthy'
            elif total < -0.5:
                health = 'concerning'
            elif momentum == 'declining':
                health = 'attention'
            else:
                health = 'neutral'

            result.append({
                'theme': theme,
                'experiment_count': len(data['experiments']),
                'total_weight': round(total, 3),
                'recent_weight': round(recent, 3),
                'older_weight': round(older, 3),
                'momentum': momentum,
                'momentum_score': momentum_score,
                'health': health,
                'experiments': data['experiments'][:5],  # Top 5 for detail
            })

        # Sort by total weight (most impactful first)
        result.sort(key=lambda x: abs(x['total_weight']), reverse=True)

        return result[:15]  # Top 15 themes

    def _calculate_overall_health(self, daily_velocity: List[Dict], theme_momentum: List[Dict]) -> Dict[str, Any]:
        """Calculate overall learning system health."""
        if not daily_velocity:
            return {
                'status': 'no_data',
                'score': 0,
                'message': 'No learning data available for analysis',
            }

        # Calculate totals
        total_experiments = sum(d['experiments'] for d in daily_velocity)
        total_positive = sum(d['positive_weight'] for d in daily_velocity)
        total_negative = sum(d['negative_weight'] for d in daily_velocity)
        net_weight = total_positive + total_negative

        # Calculate health score (0-100)
        if total_experiments == 0:
            health_score = 50  # Neutral
        else:
            # Base score from net weight
            weight_score = min(100, max(0, 50 + net_weight * 20))

            # Bonus for volume
            volume_bonus = min(20, total_experiments * 2)

            # Penalty for declining themes
            declining_themes = sum(1 for t in theme_momentum if t['momentum'] == 'declining')
            decline_penalty = declining_themes * 5

            health_score = min(100, max(0, weight_score + volume_bonus - decline_penalty))

        # Determine status
        if health_score >= 75:
            status = 'excellent'
            message = 'Learning system is thriving with strong positive momentum'
        elif health_score >= 60:
            status = 'healthy'
            message = 'Learning system is performing well'
        elif health_score >= 40:
            status = 'moderate'
            message = 'Learning system is stable but could improve'
        elif health_score >= 25:
            status = 'attention'
            message = 'Learning system needs attention - declining trends detected'
        else:
            status = 'critical'
            message = 'Learning system requires immediate review'

        # Count theme health
        healthy_themes = sum(1 for t in theme_momentum if t['health'] == 'healthy')
        concerning_themes = sum(1 for t in theme_momentum if t['health'] == 'concerning')

        return {
            'status': status,
            'score': round(health_score),
            'message': message,
            'metrics': {
                'total_experiments': total_experiments,
                'net_weight': round(net_weight, 3),
                'positive_weight': round(total_positive, 3),
                'negative_weight': round(total_negative, 3),
                'healthy_themes': healthy_themes,
                'concerning_themes': concerning_themes,
            },
        }

    def _calculate_velocity_trend(self, daily_velocity: List[Dict]) -> Dict[str, Any]:
        """Calculate velocity trend (accelerating/stable/decelerating)."""
        # Session 619: Lowered threshold from 7 to 3 days for faster feedback
        if len(daily_velocity) < 3:
            return {
                'direction': 'insufficient_data',
                'rate': 0,
                'message': 'Need at least 3 days of data for trend analysis',
            }

        # Compare last 3 days vs previous 3 days (Session 619: changed from 7)
        recent_days = daily_velocity[-3:] if len(daily_velocity) >= 3 else daily_velocity
        older_days = daily_velocity[-6:-3] if len(daily_velocity) >= 6 else []

        recent_avg = sum(d['net_velocity'] for d in recent_days) / len(recent_days)
        older_avg = sum(d['net_velocity'] for d in older_days) / len(older_days) if older_days else 0

        # Calculate rate of change
        rate = recent_avg - older_avg

        if rate > 0.1:
            direction = 'accelerating'
            message = f'Learning velocity is increasing (+{rate:.2f}/day avg)'
        elif rate < -0.1:
            direction = 'decelerating'
            message = f'Learning velocity is decreasing ({rate:.2f}/day avg)'
        else:
            direction = 'stable'
            message = 'Learning velocity is stable'

        return {
            'direction': direction,
            'rate': round(rate, 3),
            'recent_avg': round(recent_avg, 3),
            'older_avg': round(older_avg, 3),
            'message': message,
        }

    def get_theme_detail(self, theme: str, days: int = 30) -> Dict[str, Any]:
        """Get detailed velocity data for a specific theme."""
        now = timezone.now()
        start_date = now - timedelta(days=days)

        # Use the weighted learning service for theme aggregation
        theme_scores = self.learning_service.aggregate_theme_scores(theme)

        return {
            'theme': theme,
            'period_days': days,
            'aggregation': theme_scores,
            'timestamp': now.isoformat(),
        }


# Convenience function
def get_learning_velocity_dashboard(days: int = 30) -> Dict[str, Any]:
    """Get the complete learning velocity dashboard."""
    service = LearningVelocityService()
    return service.get_velocity_dashboard(days)
