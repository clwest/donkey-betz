"""
Session 600: Experiment Learning Enhancer

Provides enhanced learning analytics for ThinkingAgent.
Includes outcome classification analysis, weighted insights, and predictive scoring.

Enhancements:
1. PASS/LEARN/FAIL outcome distribution analysis
2. Weighted learning insights by outcome type
3. Predictive success scoring for new decisions
4. Cross-pattern analysis between outcome types
"""

import logging
from collections import defaultdict
from typing import Dict, List, Any, Optional

from django.db.models import Count, Avg, F
from django.utils import timezone

logger = logging.getLogger(__name__)


class ExperimentLearningEnhancer:
    """
    Enhanced experiment learning analysis for ThinkingAgent consumption.

    Provides deeper insights into experiment outcomes to improve
    future decision-making through pattern recognition and prediction.
    """

    # Outcome weights for insight prioritization
    # PASS outcomes teach what works, FAIL outcomes teach what to avoid
    OUTCOME_WEIGHTS = {
        'pass': 1.2,   # High value - these are proven successes
        'learn': 1.0,  # Standard value - informative but mixed
        'fail': 1.5,   # Highest value - avoid repeating failures
        'pending': 0.5 # Lower weight - incomplete data
    }

    # Success factors to track
    SUCCESS_FACTORS = [
        'clear_hypothesis',
        'measurable_kpi',
        'stakeholder_alignment',
        'risk_mitigation',
        'incremental_approach',
    ]

    # Failure patterns to watch
    FAILURE_PATTERNS = [
        'scope_creep',
        'resource_constraints',
        'technical_complexity',
        'market_timing',
        'user_resistance',
    ]

    def get_enhanced_learnings(self) -> Dict[str, Any]:
        """
        Get comprehensive enhanced learning data for ThinkingAgent.

        Returns:
            Dict with outcome distribution, weighted insights, predictions, and patterns
        """
        try:
            from core.models_pilot_readiness import Experiment, ExperimentLearning, DecisionTypeSuccessPattern

            result = {
                'outcome_distribution': self._get_outcome_distribution(),
                'weighted_insights': self._get_weighted_insights(),
                'predictive_scores': self._get_predictive_scores(),
                'cross_patterns': self._get_cross_patterns(),
                'actionable_recommendations': self._get_actionable_recommendations(),
                'learning_velocity': self._get_learning_velocity(),
            }

            return result

        except Exception as e:
            logger.error(f"[Session 600] Error getting enhanced learnings: {e}")
            return {}

    def _get_outcome_distribution(self) -> Dict[str, Any]:
        """
        Get distribution of outcomes across PASS/LEARN/FAIL classifications.
        """
        from core.models_pilot_readiness import Experiment

        # Count by outcome classification
        distribution = Experiment.objects.values('outcome_classification').annotate(
            count=Count('id')
        )

        total = sum(d['count'] for d in distribution)
        result = {
            'total_experiments': total,
            'by_classification': {},
            'by_halt_status': {'halted': 0, 'normal': 0}
        }

        for d in distribution:
            classification = d['outcome_classification'] or 'pending'
            result['by_classification'][classification] = {
                'count': d['count'],
                'percentage': round((d['count'] / total * 100) if total > 0 else 0, 1)
            }

        # Halted vs normal breakdown
        halted = Experiment.objects.filter(is_halted=True).count()
        result['by_halt_status']['halted'] = halted
        result['by_halt_status']['normal'] = total - halted

        # Trend analysis (last 30 days vs previous 30 days)
        from datetime import timedelta
        now = timezone.now()
        recent_start = now - timedelta(days=30)
        older_start = now - timedelta(days=60)

        recent_pass = Experiment.objects.filter(
            outcome_classification='pass',
            ended_at__gte=recent_start
        ).count()
        older_pass = Experiment.objects.filter(
            outcome_classification='pass',
            ended_at__gte=older_start,
            ended_at__lt=recent_start
        ).count()

        result['trend'] = {
            'recent_pass_rate': recent_pass,
            'older_pass_rate': older_pass,
            'improving': recent_pass > older_pass
        }

        return result

    def _get_weighted_insights(self) -> List[Dict[str, Any]]:
        """
        Get insights weighted by outcome classification.

        FAIL outcomes get highest weight (most important to avoid).
        PASS outcomes get high weight (proven to work).
        LEARN outcomes get standard weight (informative but mixed).
        """
        from core.models_pilot_readiness import ExperimentLearning

        insights = []

        for learning in ExperimentLearning.objects.select_related('experiment').order_by('-extracted_at')[:20]:
            # Determine classification from experiment
            classification = 'pending'
            if learning.experiment:
                classification = learning.experiment.outcome_classification or 'pending'

            weight = self.OUTCOME_WEIGHTS.get(classification, 1.0)
            confidence = (learning.confidence_score or 0.5) * weight

            insight = {
                'experiment_name': learning.experiment.name if learning.experiment else 'Unknown',
                'classification': classification,
                'weight': weight,
                'weighted_confidence': round(confidence, 2),
                'outcome': learning.outcome,
                'key_insight': learning.key_insight,
                'what_worked': learning.what_worked,
                'what_failed': learning.what_failed,
                'recommendation': learning.future_recommendation,
                'decision_type': learning.decision_type,
            }

            # Add halt info if applicable
            if learning.experiment and learning.experiment.is_halted:
                insight['halt_reason'] = learning.experiment.halt_reason
                insight['was_auto_halted'] = learning.experiment.halted_by == 'auto'

            insights.append(insight)

        # Sort by weighted confidence
        insights.sort(key=lambda x: x['weighted_confidence'], reverse=True)

        return insights

    def _get_predictive_scores(self) -> Dict[str, Any]:
        """
        Generate predictive success scores for decision types.

        Uses historical patterns to predict likelihood of success
        for different types of decisions.
        """
        from core.models_pilot_readiness import DecisionTypeSuccessPattern, ExperimentLearning

        predictions = {}

        for pattern in DecisionTypeSuccessPattern.objects.all():
            decision_type = pattern.decision_type

            # Base prediction from historical success rate
            base_score = pattern.success_rate / 100.0

            # Adjust based on recent trends
            recent_count = ExperimentLearning.objects.filter(
                decision_type=decision_type,
                extracted_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count()

            recent_success = ExperimentLearning.objects.filter(
                decision_type=decision_type,
                outcome='success',
                extracted_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count()

            if recent_count >= 3:
                recent_rate = recent_success / recent_count
                # Weight recent performance more heavily
                adjusted_score = (base_score * 0.4) + (recent_rate * 0.6)
            else:
                adjusted_score = base_score

            # Factor in sample size confidence
            sample_confidence = min(pattern.total_experiments / 10, 1.0)

            predictions[decision_type] = {
                'predicted_success_rate': round(adjusted_score * 100, 1),
                'historical_rate': pattern.success_rate,
                'sample_size': pattern.total_experiments,
                'sample_confidence': round(sample_confidence, 2),
                'avg_kpi_impact': pattern.avg_kpi_delta_percent,
                'common_success_factors': pattern.common_success_factors[:3] if pattern.common_success_factors else [],
                'common_failure_factors': pattern.common_failure_factors[:3] if pattern.common_failure_factors else [],
                'recommendation': self._get_type_recommendation(adjusted_score, pattern)
            }

        return predictions

    def _get_type_recommendation(self, score: float, pattern) -> str:
        """Generate recommendation based on predictive score."""
        if score >= 0.7:
            return f"HIGH confidence - proceed with caution. Success rate: {score*100:.0f}%"
        elif score >= 0.5:
            return f"MODERATE confidence - ensure strong risk mitigation. Historical insights: {pattern.top_insights[0] if pattern.top_insights else 'N/A'}"
        else:
            return f"LOW confidence - consider smaller pilot scope or alternative approach. Common failures: {pattern.common_failure_factors[0] if pattern.common_failure_factors else 'N/A'}"

    def _get_cross_patterns(self) -> Dict[str, Any]:
        """
        Identify patterns that span across different outcome classifications.

        Finds what distinguishes PASS from FAIL experiments.
        """
        from core.models_pilot_readiness import Experiment, ExperimentLearning

        patterns = {
            'pass_characteristics': [],
            'fail_characteristics': [],
            'key_differentiators': [],
        }

        # Analyze PASS experiments
        pass_experiments = Experiment.objects.filter(outcome_classification='pass')
        fail_experiments = Experiment.objects.filter(outcome_classification='fail')

        # Look at learnings from each
        pass_learnings = ExperimentLearning.objects.filter(
            experiment__in=pass_experiments
        )
        fail_learnings = ExperimentLearning.objects.filter(
            experiment__in=fail_experiments
        )

        # Aggregate what worked in PASS experiments
        pass_worked = []
        for learning in pass_learnings:
            if learning.what_worked:
                pass_worked.append(learning.what_worked)

        # Aggregate what failed in FAIL experiments
        fail_reasons = []
        for learning in fail_learnings:
            if learning.what_failed:
                fail_reasons.append(learning.what_failed)

        patterns['pass_characteristics'] = pass_worked[:5]
        patterns['fail_characteristics'] = fail_reasons[:5]

        # Key differentiators
        patterns['key_differentiators'] = [
            {
                'factor': 'Clear KPIs',
                'pass_rate': self._calculate_factor_rate(pass_experiments, 'has_kpi'),
                'fail_rate': self._calculate_factor_rate(fail_experiments, 'has_kpi'),
            },
            {
                'factor': 'Risk Mitigation',
                'pass_rate': self._calculate_factor_rate(pass_experiments, 'has_risk'),
                'fail_rate': self._calculate_factor_rate(fail_experiments, 'has_risk'),
            },
        ]

        return patterns

    def _calculate_factor_rate(self, experiments, factor_type: str) -> float:
        """Calculate what percentage of experiments had a certain factor."""
        total = experiments.count()
        if total == 0:
            return 0.0

        if factor_type == 'has_kpi':
            with_kpi = experiments.exclude(primary_kpi='').exclude(primary_kpi__isnull=True).count()
            return round((with_kpi / total) * 100, 1)
        elif factor_type == 'has_risk':
            # Check if gate has risk_factors.
            # Previously a bare 'except: pass' hid every missing
            # pilot/gate relation so experiments without a readiness gate
            # silently counted as "no risk factors," which undercounted
            # the risk-coverage percentage. Now we narrow to the
            # expected attribute-lookup / None-access cases and log
            # anything unexpected so the metric is trustworthy.
            with_risk = 0
            for exp in experiments[:50]:  # Limit for performance
                try:
                    if exp.pilot.gate.risk_factors:
                        with_risk += 1
                except AttributeError:
                    # Experiment has no pilot or pilot has no gate —
                    # expected for experiments outside the readiness
                    # pipeline; skip silently (no risk data).
                    continue
                except Exception as e:
                    logger.warning(
                        "experiment_learning_enhancer: unexpected error "
                        "reading risk_factors for experiment %s (%s: %s) — "
                        "skipping from risk coverage count",
                        getattr(exp, 'id', '<unknown>'),
                        type(e).__name__, e,
                    )
                    continue
            return round((with_risk / min(total, 50)) * 100, 1)

        return 0.0

    def _get_actionable_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate specific actionable recommendations based on learnings.
        """
        from core.models_pilot_readiness import Experiment, ExperimentLearning

        recommendations = []

        # Check for high fail rate
        total = Experiment.objects.exclude(outcome_classification='pending').count()
        fails = Experiment.objects.filter(outcome_classification='fail').count()

        if total >= 5 and (fails / total) > 0.3:
            recommendations.append({
                'priority': 'high',
                'type': 'process_improvement',
                'recommendation': f'High failure rate detected ({fails}/{total} = {fails/total*100:.0f}%). Review experiment planning process and consider smaller pilot scopes.',
                'action': 'Review last 5 failed experiments for common patterns'
            })

        # Check for auto-halt patterns
        auto_halts = Experiment.objects.filter(halted_by='auto').count()
        if auto_halts >= 2:
            recommendations.append({
                'priority': 'medium',
                'type': 'monitoring',
                'recommendation': f'{auto_halts} experiments were auto-halted by monitoring. Review halt condition thresholds and monitoring coverage.',
                'action': 'Audit halt conditions and adjust thresholds if needed'
            })

        # Check for learning extraction
        no_learnings = Experiment.objects.exclude(
            outcome_classification='pending'
        ).exclude(
            pk__in=ExperimentLearning.objects.values_list('experiment_id', flat=True)
        ).count()

        if no_learnings >= 3:
            recommendations.append({
                'priority': 'low',
                'type': 'documentation',
                'recommendation': f'{no_learnings} completed experiments lack extracted learnings. Ensure learnings are captured for all experiments.',
                'action': 'Run learning extraction for completed experiments'
            })

        return recommendations

    def _get_learning_velocity(self) -> Dict[str, Any]:
        """
        Calculate how fast the system is learning and improving.
        """
        from core.models_pilot_readiness import ExperimentLearning
        from datetime import timedelta

        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        learnings_this_week = ExperimentLearning.objects.filter(extracted_at__gte=week_ago).count()
        learnings_this_month = ExperimentLearning.objects.filter(extracted_at__gte=month_ago).count()

        fed_to_thinking = ExperimentLearning.objects.filter(fed_to_thinking_agent=True).count()
        total_learnings = ExperimentLearning.objects.count()

        return {
            'learnings_this_week': learnings_this_week,
            'learnings_this_month': learnings_this_month,
            'fed_to_thinking_agent': fed_to_thinking,
            'total_learnings': total_learnings,
            'utilization_rate': round((fed_to_thinking / total_learnings * 100) if total_learnings > 0 else 0, 1),
            'velocity_status': 'active' if learnings_this_week >= 1 else 'stale'
        }


def get_enhanced_learnings_for_thinking_agent() -> Dict[str, Any]:
    """
    Convenience function to get enhanced learnings for ThinkingAgent context.

    Returns:
        Enhanced learning data including outcome distribution, weighted insights,
        predictive scores, and actionable recommendations.
    """
    enhancer = ExperimentLearningEnhancer()
    return enhancer.get_enhanced_learnings()
