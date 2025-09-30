"""
Unified Agent Performance - Single source of truth for agent performance across ALL domains

Provides a unified API to query agent performance across both:
- Sports betting domains (via AgentPerformanceMetrics)
- General domains (via UserAgentLearning)
"""

import logging
from typing import Dict, List, Optional
from django.db.models import Avg, Count

logger = logging.getLogger(__name__)


class UnifiedAgentPerformance:
    """
    Single source of truth for agent performance across ALL domains.

    Aggregates performance metrics from:
    1. Sports betting system (intelligence.AgentPerformanceMetrics)
    2. Core learning system (core.UserAgentLearning)

    Usage:
        performance = UnifiedAgentPerformance.get_agent_performance(
            agent=my_agent,
            domain='sports_betting_nfl'
        )

        # Or get all domains
        all_performance = UnifiedAgentPerformance.get_all_domains(agent=my_agent)
    """

    SPORTS_DOMAINS = ['nfl', 'nba', 'mlb', 'nhl']
    GENERAL_DOMAINS = [
        'opportunity_matching', 'content_creation', 'communication',
        'decision_making', 'skill_development', 'revenue_optimization'
    ]

    @staticmethod
    def get_agent_performance(agent, domain: str, user=None) -> Dict:
        """
        Get agent performance for ANY domain (sports or general)

        Args:
            agent: UnifiedAgentTemplate instance
            domain: Domain name (e.g., 'sports_betting_nfl', 'opportunity_matching')
            user: Optional user for user-specific performance

        Returns:
            {
                'domain': 'sports_betting_nfl',
                'accuracy': 0.58,
                'confidence_calibration': 0.12,
                'specialization_level': 'expert',
                'sample_size': 127,
                'recommendations': ['increase confidence', 'focus on this domain'],
                'source': 'sports_betting' or 'core_learning'
            }
        """

        # Determine if this is a sports or general domain
        if domain.startswith('sports_betting_'):
            sport = domain.replace('sports_betting_', '')
            return UnifiedAgentPerformance._get_sports_performance(agent, sport, user)
        else:
            return UnifiedAgentPerformance._get_general_performance(agent, domain, user)

    @staticmethod
    def get_all_domains(agent, user=None) -> List[Dict]:
        """
        Get agent performance across ALL domains

        Args:
            agent: UnifiedAgentTemplate instance
            user: Optional user for user-specific performance

        Returns:
            List of performance dicts for each domain agent has worked in
        """
        all_performance = []

        # Get sports performance
        for sport in UnifiedAgentPerformance.SPORTS_DOMAINS:
            perf = UnifiedAgentPerformance._get_sports_performance(agent, sport, user)
            if perf and perf.get('sample_size', 0) > 0:
                all_performance.append(perf)

        # Get general performance
        for domain in UnifiedAgentPerformance.GENERAL_DOMAINS:
            perf = UnifiedAgentPerformance._get_general_performance(agent, domain, user)
            if perf and perf.get('sample_size', 0) > 0:
                all_performance.append(perf)

        return all_performance

    @staticmethod
    def get_best_domains(agent, user=None, top_n: int = 3) -> List[Dict]:
        """
        Get agent's top-performing domains

        Args:
            agent: UnifiedAgentTemplate instance
            user: Optional user
            top_n: Number of top domains to return

        Returns:
            List of top N performance dicts sorted by accuracy
        """
        all_performance = UnifiedAgentPerformance.get_all_domains(agent, user)

        # Filter to domains with sufficient data (10+ samples)
        valid_domains = [
            perf for perf in all_performance
            if perf.get('sample_size', 0) >= 10
        ]

        # Sort by accuracy
        sorted_domains = sorted(
            valid_domains,
            key=lambda x: x.get('accuracy', 0),
            reverse=True
        )

        return sorted_domains[:top_n]

    @staticmethod
    def get_overall_performance_summary(agent, user=None) -> Dict:
        """
        Get aggregate performance summary across ALL domains

        Args:
            agent: UnifiedAgentTemplate instance
            user: Optional user

        Returns:
            {
                'total_domains': 12,
                'avg_accuracy': 0.64,
                'total_samples': 456,
                'best_domain': 'sports_betting_nfl',
                'best_accuracy': 0.72,
                'specializations': ['sports_betting_nfl', 'opportunity_matching'],
                'cross_domain_strength': 0.68  # consistency across domains
            }
        """
        all_performance = UnifiedAgentPerformance.get_all_domains(agent, user)

        if not all_performance:
            return {
                'total_domains': 0,
                'avg_accuracy': 0.0,
                'total_samples': 0,
                'message': 'No performance data available'
            }

        # Calculate aggregates
        valid_domains = [p for p in all_performance if p.get('sample_size', 0) >= 5]

        if not valid_domains:
            return {
                'total_domains': len(all_performance),
                'avg_accuracy': 0.0,
                'total_samples': sum(p.get('sample_size', 0) for p in all_performance),
                'message': 'Insufficient data for performance summary'
            }

        total_samples = sum(p.get('sample_size', 0) for p in valid_domains)
        avg_accuracy = sum(p.get('accuracy', 0) for p in valid_domains) / len(valid_domains)

        best_domain = max(valid_domains, key=lambda x: x.get('accuracy', 0))

        # Identify specializations (accuracy > 60% and > 20 samples)
        specializations = [
            p['domain']
            for p in valid_domains
            if p.get('accuracy', 0) > 0.60 and p.get('sample_size', 0) > 20
        ]

        # Cross-domain strength: standard deviation of accuracy (lower = more consistent)
        accuracies = [p.get('accuracy', 0) for p in valid_domains]
        import statistics
        std_dev = statistics.stdev(accuracies) if len(accuracies) > 1 else 0
        cross_domain_strength = max(0, 1.0 - std_dev)  # Convert to 0-1 scale

        return {
            'total_domains': len(valid_domains),
            'avg_accuracy': round(avg_accuracy, 3),
            'total_samples': total_samples,
            'best_domain': best_domain['domain'],
            'best_accuracy': round(best_domain['accuracy'], 3),
            'specializations': specializations,
            'cross_domain_strength': round(cross_domain_strength, 3)
        }

    # Private helper methods

    @staticmethod
    def _get_sports_performance(agent, sport: str, user=None) -> Optional[Dict]:
        """Get performance from sports betting system"""
        try:
            from intelligence.models import AgentPerformanceMetrics

            # Try to get metrics for this agent
            try:
                metrics = AgentPerformanceMetrics.objects.get(agent=agent)
            except AgentPerformanceMetrics.DoesNotExist:
                return None

            # Get sport-specific metrics
            sport_predictions = getattr(metrics, f'{sport}_predictions', 0)
            sport_correct = getattr(metrics, f'{sport}_correct', 0)

            if sport_predictions == 0:
                return None

            accuracy = sport_correct / sport_predictions

            # Calculate specialization level
            specialization = UnifiedAgentPerformance._calculate_specialization(
                accuracy * 100, sport_predictions
            )

            # Generate recommendations
            recommendations = UnifiedAgentPerformance._generate_recommendations(
                accuracy * 100, sport_predictions, metrics.confidence_calibration_score
            )

            return {
                'domain': f'sports_betting_{sport}',
                'accuracy': round(accuracy, 3),
                'confidence_calibration': float(metrics.confidence_calibration_score or 0),
                'specialization_level': specialization,
                'sample_size': sport_predictions,
                'correct_predictions': sport_correct,
                'recommendations': recommendations,
                'source': 'sports_betting'
            }

        except Exception as e:
            logger.error(f"Error getting sports performance: {e}")
            return None

    @staticmethod
    def _get_general_performance(agent, domain: str, user=None) -> Optional[Dict]:
        """Get performance from core learning system"""
        try:
            from core.models_unified_system import UserAgentLearning

            # Build query
            query = {
                'agent_name': agent.name,
                'learning_domain': domain
            }

            if user:
                query['user'] = user

            # Get learning entries
            learnings = UserAgentLearning.objects.filter(**query)

            if not learnings.exists():
                return None

            # Aggregate performance metrics
            avg_confidence = learnings.aggregate(
                avg_conf=Avg('confidence_score')
            )['avg_conf'] or 0

            avg_success = learnings.aggregate(
                avg_succ=Avg('success_rate')
            )['avg_succ'] or 0

            total_validations = learnings.aggregate(
                total=Count('validation_count')
            )['total'] or 0

            # Use success_rate as accuracy proxy
            accuracy = avg_success

            # Calculate specialization
            specialization = UnifiedAgentPerformance._calculate_specialization(
                accuracy * 100, total_validations
            )

            # Generate recommendations
            recommendations = UnifiedAgentPerformance._generate_recommendations(
                accuracy * 100, total_validations, None
            )

            return {
                'domain': domain,
                'accuracy': round(accuracy, 3),
                'confidence_calibration': None,  # Not tracked in general learning
                'specialization_level': specialization,
                'sample_size': total_validations,
                'avg_confidence': round(avg_confidence, 3),
                'recommendations': recommendations,
                'source': 'core_learning'
            }

        except Exception as e:
            logger.error(f"Error getting general performance: {e}")
            return None

    @staticmethod
    def _calculate_specialization(accuracy: float, sample_size: int) -> str:
        """Calculate specialization level based on accuracy and sample size"""
        if sample_size < 10:
            return 'novice'
        elif sample_size < 50:
            if accuracy > 60:
                return 'intermediate'
            return 'novice'
        elif sample_size >= 50:
            if accuracy > 65:
                return 'expert'
            elif accuracy > 55:
                return 'advanced'
            elif accuracy > 50:
                return 'intermediate'
            return 'novice'
        return 'novice'

    @staticmethod
    def _generate_recommendations(accuracy: float, sample_size: int, calibration: Optional[float]) -> List[str]:
        """Generate actionable recommendations based on performance"""
        recommendations = []

        # Sample size recommendations
        if sample_size < 20:
            recommendations.append('Need more data for reliable assessment')
        elif sample_size < 50:
            recommendations.append('Continue building track record')

        # Accuracy recommendations
        if accuracy > 65:
            recommendations.append('Strong performer - increase confidence')
        elif accuracy > 55:
            recommendations.append('Good performer - maintain current approach')
        elif accuracy > 45:
            recommendations.append('Moderate performer - review strategies')
        else:
            recommendations.append('Underperforming - consider retraining or specialization')

        # Calibration recommendations
        if calibration is not None:
            if calibration > 20:
                recommendations.append('Poor calibration - adjust confidence levels')
            elif calibration < 10:
                recommendations.append('Well-calibrated predictions')

        # Specialization recommendations
        if accuracy > 60 and sample_size > 50:
            recommendations.append('Focus on this domain - clear specialization')

        return recommendations


# Convenience functions

def get_agent_best_domains(agent, user=None, top_n: int = 3):
    """
    Convenience function: Get agent's best-performing domains

    Args:
        agent: UnifiedAgentTemplate instance
        user: Optional user
        top_n: Number of top domains

    Returns:
        List of top domains
    """
    return UnifiedAgentPerformance.get_best_domains(agent, user, top_n)


def compare_agents(agents: list, domain: str, user=None) -> List[Dict]:
    """
    Compare multiple agents' performance in a specific domain

    Args:
        agents: List of UnifiedAgentTemplate instances
        domain: Domain to compare
        user: Optional user

    Returns:
        List of performance dicts sorted by accuracy
    """
    performances = []

    for agent in agents:
        perf = UnifiedAgentPerformance.get_agent_performance(agent, domain, user)
        if perf:
            perf['agent_name'] = agent.name
            performances.append(perf)

    # Sort by accuracy
    return sorted(performances, key=lambda x: x.get('accuracy', 0), reverse=True)
