"""
Agent Learning System - Phase 3 of Agent Learning Integration

Enables agents to learn from their own prediction performance and adapt their strategies.
Each agent tracks their personal track record and adjusts confidence based on experience.

Features:
- Agent performance tracking by sport
- Confidence calibration based on track record
- Specialization discovery
- Self-awareness for agents
"""

import logging
from typing import Optional, Dict, List

from agents.models import UnifiedAgentTemplate, AgentPerformanceMetrics

logger = logging.getLogger(__name__)


class AgentLearningSystem:
    """
    Enables agents to learn from their performance and adapt predictions

    Usage:
        agent = UnifiedAgentTemplate.objects.get(name='sports-predictor-agent')
        learning_system = AgentLearningSystem(agent)

        # Get confidence adjustment for a sport
        adjustment = learning_system.get_confidence_adjustment('nfl')

        # Check if agent should make prediction
        should_predict = learning_system.should_make_prediction('nfl')

        # Get agent's specializations
        specializations = learning_system.get_specializations()
    """

    def __init__(self, agent: UnifiedAgentTemplate):
        """
        Initialize agent learning system

        Args:
            agent: UnifiedAgentTemplate instance
        """
        self.agent = agent
        self.metrics = AgentPerformanceMetrics.objects.filter(agent=agent)

    def get_confidence_adjustment(self, sport_type: str) -> float:
        """
        Adjust confidence based on agent's track record in this sport

        Args:
            sport_type: Sport type ('nfl', 'nba', 'mlb', 'nhl')

        Returns:
            float: Multiplier for confidence (0.8 to 1.2)
                  - 1.1 if agent is performing well (>60% accuracy)
                  - 0.9 if agent is performing poorly (<50% accuracy)
                  - 1.0 otherwise (neutral)
        """
        try:
            metrics = self.metrics.get(sport_type=sport_type)

            # Need at least 10 predictions to adjust confidence
            if metrics.sport_predictions < 10:
                return 1.0

            # If accuracy > 60%, boost confidence
            if metrics.sport_accuracy > 0.60:
                logger.info(
                    f"Agent {self.agent.name} performing well in {sport_type.upper()} "
                    f"({metrics.sport_accuracy:.1%}) - boosting confidence"
                )
                return 1.1

            # If accuracy < 50%, reduce confidence
            if metrics.sport_accuracy < 0.50:
                logger.info(
                    f"Agent {self.agent.name} struggling in {sport_type.upper()} "
                    f"({metrics.sport_accuracy:.1%}) - reducing confidence"
                )
                return 0.9

            # Normal range - no adjustment
            return 1.0

        except AgentPerformanceMetrics.DoesNotExist:
            # New to this sport - neutral confidence
            logger.debug(
                f"Agent {self.agent.name} has no history in {sport_type.upper()} - neutral confidence"
            )
            return 1.0

    def should_make_prediction(self, sport_type: str) -> bool:
        """
        Decide if agent should make prediction based on competence

        Agents with very poor track record (< 40% accuracy after 20+ predictions)
        should decline to make predictions in that sport.

        Args:
            sport_type: Sport type ('nfl', 'nba', 'mlb', 'nhl')

        Returns:
            bool: True if agent should predict, False if agent should decline
        """
        try:
            metrics = self.metrics.get(sport_type=sport_type)

            # Don't predict if performing very poorly with enough data
            if metrics.sport_predictions > 20 and metrics.sport_accuracy < 0.40:
                logger.warning(
                    f"Agent {self.agent.name} declining {sport_type.upper()} prediction - "
                    f"poor track record ({metrics.sport_accuracy:.1%} after {metrics.sport_predictions} predictions)"
                )
                return False

            return True

        except AgentPerformanceMetrics.DoesNotExist:
            # New agent - let them try
            logger.debug(
                f"Agent {self.agent.name} is new to {sport_type.upper()} - allowing prediction"
            )
            return True

    def get_specializations(self) -> Dict:
        """
        Identify which sports/areas agent excels at

        Returns:
            dict: Specialization summary with:
                - status: 'new_agent' or 'experienced'
                - best_sport: Sport with highest accuracy
                - best_accuracy: Accuracy in best sport
                - worst_sport: Sport with lowest accuracy
                - worst_accuracy: Accuracy in worst sport
                - specializations: List of sports where agent excels (>60% accuracy)
                - total_predictions: Total predictions across all sports
                - sports_breakdown: Dict of accuracy by sport
        """
        all_metrics = list(self.metrics.all())

        if not all_metrics:
            return {
                'status': 'new_agent',
                'specializations': [],
                'total_predictions': 0,
                'message': f"Agent {self.agent.name} is new - no prediction history yet"
            }

        # Find best and worst sports
        best_metric = max(all_metrics, key=lambda m: m.sport_accuracy)
        worst_metric = min(all_metrics, key=lambda m: m.sport_accuracy)

        # Find specializations (>60% accuracy with at least 10 predictions)
        specializations = [
            {
                'sport': m.sport_type,
                'accuracy': m.sport_accuracy,
                'predictions': m.sport_predictions
            }
            for m in all_metrics
            if m.sport_accuracy > 0.60 and m.sport_predictions > 10
        ]

        # Sort specializations by accuracy
        specializations.sort(key=lambda x: x['accuracy'], reverse=True)

        # Create sports breakdown
        sports_breakdown = {
            m.sport_type: {
                'accuracy': m.sport_accuracy,
                'predictions': m.sport_predictions,
                'correct': m.sport_correct,
            }
            for m in all_metrics
        }

        total_predictions = sum(m.sport_predictions for m in all_metrics)

        result = {
            'status': 'experienced',
            'best_sport': best_metric.sport_type,
            'best_accuracy': best_metric.sport_accuracy,
            'worst_sport': worst_metric.sport_type,
            'worst_accuracy': worst_metric.sport_accuracy,
            'specializations': specializations,
            'total_predictions': total_predictions,
            'sports_breakdown': sports_breakdown,
            'message': self._generate_performance_summary(
                best_metric, worst_metric, specializations, total_predictions
            )
        }

        logger.info(
            f"Agent {self.agent.name} specializations: "
            f"Best={best_metric.sport_type.upper()}({best_metric.sport_accuracy:.1%}), "
            f"Worst={worst_metric.sport_type.upper()}({worst_metric.sport_accuracy:.1%}), "
            f"Total={total_predictions} predictions"
        )

        return result

    def _generate_performance_summary(
        self,
        best_metric: AgentPerformanceMetrics,
        worst_metric: AgentPerformanceMetrics,
        specializations: List[Dict],
        total_predictions: int
    ) -> str:
        """Generate human-readable performance summary"""

        summary_parts = [
            f"Agent {self.agent.name} has made {total_predictions} predictions."
        ]

        if specializations:
            spec_sports = ', '.join([s['sport'].upper() for s in specializations])
            summary_parts.append(f"Specializes in: {spec_sports}.")

        summary_parts.append(
            f"Best in {best_metric.sport_type.upper()} ({best_metric.sport_accuracy:.1%}), "
            f"weakest in {worst_metric.sport_type.upper()} ({worst_metric.sport_accuracy:.1%})."
        )

        return " ".join(summary_parts)

    def get_confidence_calibration(self, sport_type: str) -> Dict:
        """
        Get confidence calibration metrics for a sport

        Args:
            sport_type: Sport type

        Returns:
            dict: Calibration metrics including:
                - level: 'overconfident', 'well_calibrated', or 'underconfident'
                - avg_confidence_when_correct: Average confidence for correct predictions
                - avg_confidence_when_wrong: Average confidence for wrong predictions
                - calibration_score: Difference between correct and wrong confidence
                - recommendation: Suggested action
        """
        try:
            metrics = self.metrics.get(sport_type=sport_type)

            # Determine calibration level
            if metrics.confidence_calibration_score > 0.15:
                level = 'well_calibrated'
                recommendation = "Confidence levels are well-calibrated. Continue current approach."
            elif metrics.confidence_calibration_score < 0.05:
                level = 'overconfident'
                recommendation = "May be overconfident. Consider reducing confidence slightly."
            else:
                level = 'underconfident'
                recommendation = "May be underconfident. Consider increasing confidence slightly."

            return {
                'level': level,
                'avg_confidence_when_correct': metrics.avg_confidence_when_correct,
                'avg_confidence_when_wrong': metrics.avg_confidence_when_wrong,
                'calibration_score': metrics.confidence_calibration_score,
                'recommendation': recommendation,
                'predictions_analyzed': metrics.sport_predictions
            }

        except AgentPerformanceMetrics.DoesNotExist:
            return {
                'level': 'unknown',
                'message': f"No calibration data for {sport_type.upper()} yet"
            }