"""
Session 601: Weighted Learning System

Implements ChatGPT's recommended learning weight formula:

    learning_weight = outcome_signal × confidence_weight × decay_weight

Where:
- outcome_signal: Base value based on PASS/LEARN/FAIL type
- confidence_weight: Based on sample size (logarithmic)
- decay_weight: Exponential decay so old outcomes fade

This replaces the simple static weights with a sophisticated
evidence-based learning system that:
- Rewards confidence (more data = more weight)
- Prevents permanent bias (decay over time)
- Distinguishes safety FAILs from execution FAILs
- Preserves innovation while respecting risk
"""

import math
import logging
from datetime import timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from django.db.models import Count, Avg
from django.utils import timezone

logger = logging.getLogger(__name__)


class WeightedLearningService:
    """
    Session 601: Weighted learning system following ChatGPT's formula.

    Key principles:
    1. Outcomes are weighted memory, not truth
    2. Confidence comes from evidence, not loudness
    3. Old outcomes fade unless reinforced
    4. No idea is permanently banned (with guardrails)
    """

    # =========================================================================
    # OUTCOME SIGNAL MAPPING
    # =========================================================================

    # Outcome signals based on type
    OUTCOME_SIGNALS = {
        'pass': 1.0,           # Success - positive signal
        'learn': 0.3,          # Informative - weak positive
        'fail_safety': -1.0,   # Safety/trust failure - strong negative
        'fail_execution': -0.5, # Execution/quality failure - informative negative
    }

    # =========================================================================
    # SAFETY FAIL KEYWORD CLASSIFICATION (v1.2 - Session 805)
    # =========================================================================
    # Strong keywords: Single hit is enough to classify as safety FAIL
    # Weak keywords: Need 2 weak hits OR 1 weak + 1 strong to classify
    #
    # Session 805: Removed operational monitoring terms that caused false positives:
    # - 'integrity_anomaly': This is an operational monitoring signal, not safety
    # - 'anomaly': Used for error rate spikes, not security issues
    # - 'integrity': Too generic, used in operational contexts

    STRONG_SAFETY_KEYWORDS = [
        'kill_switch', 'kill-switch', 'harmful', 'security', 'data_breach',
        'offensive', 'discriminat', 'compliance_violation',
        'unauthorized', 'malicious', 'exploit'
    ]

    WEAK_SAFETY_KEYWORDS = [
        'privacy', 'bias', 'user_trust', 'safety', 'compliance',
        'pii', 'gdpr', 'sensitive_data'
    ]

    # Minimum samples for reliable evidence (novelty penalty threshold)
    INSUFFICIENT_EVIDENCE_THRESHOLD = 3

    # =========================================================================
    # CONFIDENCE WEIGHT
    # =========================================================================

    # Minimum samples for full confidence
    CONFIDENCE_FULL_SAMPLES = 10

    @classmethod
    def calculate_confidence_weight(cls, sample_size: int) -> float:
        """
        Calculate confidence weight based on sample size.

        Formula: confidence_weight = min(1.0, log10(sample_size + 1))

        Examples:
        - 9+ samples → 1.0 (full confidence) [log10(10) = 1.0]
        - 5 samples → ~0.78
        - 3 samples → ~0.60
        - 1 sample → ~0.30

        This avoids knee-jerk learning from small samples.
        """
        if sample_size <= 0:
            return 0.0

        confidence = min(1.0, math.log10(sample_size + 1))
        return round(confidence, 3)

    # =========================================================================
    # DECAY WEIGHT
    # =========================================================================

    # How many days until outcome has ~37% weight (e^-1)
    DECAY_CONSTANT_DAYS = 21  # 3 weeks

    @classmethod
    def calculate_decay_weight(cls, age_days: float, decay_constant: float = None) -> float:
        """
        Calculate decay weight based on age.

        Formula: decay_weight = e^(-age_in_days / decay_constant)

        This ensures:
        - Recent outcomes matter more
        - Old failures don't haunt the system forever
        - Learning stays current and relevant

        Examples (with 21-day decay):
        - 0 days → 1.0 (full weight)
        - 7 days → ~0.72
        - 21 days → ~0.37
        - 42 days → ~0.14
        """
        if decay_constant is None:
            decay_constant = cls.DECAY_CONSTANT_DAYS

        if age_days <= 0:
            return 1.0

        decay = math.exp(-age_days / decay_constant)
        return round(decay, 3)

    # =========================================================================
    # OUTCOME SIGNAL
    # =========================================================================

    @classmethod
    def _is_safety_failure(cls, halt_reason: str) -> bool:
        """
        Determine if a halt reason indicates a safety failure.

        Uses strong/weak keyword classification (v1.1):
        - Strong keyword: Single hit = safety failure
        - Weak keywords: Need 2 weak hits OR 1 weak + 1 strong

        This prevents false positives from neutral mentions of "privacy" etc.
        """
        halt_reason_lower = (halt_reason or '').lower()

        # Count strong keyword hits
        strong_hits = sum(1 for kw in cls.STRONG_SAFETY_KEYWORDS if kw in halt_reason_lower)

        # Count weak keyword hits
        weak_hits = sum(1 for kw in cls.WEAK_SAFETY_KEYWORDS if kw in halt_reason_lower)

        # Classification rules:
        # 1. Any strong keyword = safety failure
        # 2. 2+ weak keywords = safety failure
        # 3. 1 weak + 1 strong = safety failure (covered by rule 1)
        return strong_hits >= 1 or weak_hits >= 2

    @classmethod
    def determine_outcome_signal(cls, outcome_classification: str, halt_reason: str = None) -> Tuple[float, str]:
        """
        Determine the outcome signal value and type.

        For FAIL outcomes, distinguishes between:
        - Safety/trust failures (strong negative: -1.0)
        - Execution/quality failures (informative negative: -0.5)

        Uses strong/weak keyword classification to reduce false positives.

        Returns:
            (signal_value, signal_type)
        """
        if outcome_classification == 'pass':
            return cls.OUTCOME_SIGNALS['pass'], 'pass'
        elif outcome_classification == 'learn':
            return cls.OUTCOME_SIGNALS['learn'], 'learn'
        elif outcome_classification == 'fail':
            # Check if it's a safety failure using strong/weak classification
            if cls._is_safety_failure(halt_reason):
                return cls.OUTCOME_SIGNALS['fail_safety'], 'fail_safety'
            else:
                return cls.OUTCOME_SIGNALS['fail_execution'], 'fail_execution'
        else:
            return 0.0, 'pending'

    # =========================================================================
    # LEARNING WEIGHT CALCULATION
    # =========================================================================

    @classmethod
    def calculate_learning_weight(
        cls,
        outcome_classification: str,
        halt_reason: str = None,
        sample_size: int = 1,
        age_days: float = 0
    ) -> Dict[str, Any]:
        """
        Calculate the complete learning weight for an outcome.

        Formula: learning_weight = outcome_signal × confidence_weight × decay_weight

        Returns dict with all components for transparency, including
        insufficient_evidence flag for novelty penalty.
        """
        # Get outcome signal
        outcome_signal, signal_type = cls.determine_outcome_signal(outcome_classification, halt_reason)

        # Calculate weights
        confidence_weight = cls.calculate_confidence_weight(sample_size)
        decay_weight = cls.calculate_decay_weight(age_days)

        # Calculate final weight
        learning_weight = outcome_signal * confidence_weight * decay_weight

        # Check for insufficient evidence (novelty penalty)
        insufficient_evidence = sample_size < cls.INSUFFICIENT_EVIDENCE_THRESHOLD

        return {
            'learning_weight': round(learning_weight, 4),
            'outcome_signal': outcome_signal,
            'signal_type': signal_type,
            'confidence_weight': confidence_weight,
            'decay_weight': decay_weight,
            'sample_size': sample_size,
            'age_days': round(age_days, 1),
            'insufficient_evidence': insufficient_evidence,
            'evidence_status': 'promising' if insufficient_evidence else 'proven',
            'components': {
                'formula': 'outcome_signal × confidence_weight × decay_weight',
                'calculation': f'{outcome_signal} × {confidence_weight} × {decay_weight}',
            }
        }

    # =========================================================================
    # AGGREGATION: CUMULATIVE SCORES
    # =========================================================================

    def aggregate_theme_scores(self, theme_or_topic: str) -> Dict[str, Any]:
        """
        Calculate cumulative weighted score for a theme/idea.

        Returns:
        - cumulative_score: Sum of all weighted outcomes
        - confidence_interval: Based on variance and sample size
        - trend_direction: positive/negative/neutral
        - recommendation: Strategic reasoning based on data
        """
        from core.models_pilot_readiness import Experiment, ExperimentLearning

        # Find experiments related to this theme
        related_experiments = Experiment.objects.filter(
            name__icontains=theme_or_topic
        ) | Experiment.objects.filter(
            hypothesis__icontains=theme_or_topic
        )

        if not related_experiments.exists():
            return {
                'theme': theme_or_topic,
                'cumulative_score': 0.0,
                'sample_count': 0,
                'confidence_interval': 'insufficient_data',
                'trend_direction': 'unknown',
                'recommendation': 'No data - consider exploratory pilot',
            }

        now = timezone.now()
        weighted_scores = []
        recent_scores = []  # Last 14 days
        older_scores = []   # Before that

        for exp in related_experiments:
            if exp.outcome_classification == 'pending':
                continue

            # Calculate age
            ended_at = exp.ended_at or exp.updated_at
            age_days = (now - ended_at).total_seconds() / 86400 if ended_at else 0

            # Get sample size (using related learnings count as proxy)
            sample_size = ExperimentLearning.objects.filter(experiment=exp).count()
            sample_size = max(1, sample_size)

            # Calculate weight
            weight_data = self.calculate_learning_weight(
                outcome_classification=exp.outcome_classification,
                halt_reason=exp.halt_reason,
                sample_size=sample_size,
                age_days=age_days
            )

            weighted_scores.append(weight_data['learning_weight'])

            if age_days <= 14:
                recent_scores.append(weight_data['learning_weight'])
            else:
                older_scores.append(weight_data['learning_weight'])

        if not weighted_scores:
            return {
                'theme': theme_or_topic,
                'cumulative_score': 0.0,
                'sample_count': 0,
                'confidence_interval': 'no_completed_experiments',
                'trend_direction': 'unknown',
                'recommendation': 'No completed experiments - await results',
            }

        cumulative = sum(weighted_scores)
        sample_count = len(weighted_scores)

        # Calculate confidence interval
        if sample_count >= 10:
            confidence_interval = 'high'
        elif sample_count >= 5:
            confidence_interval = 'medium'
        elif sample_count >= 2:
            confidence_interval = 'low'
        else:
            confidence_interval = 'insufficient'

        # Calculate trend
        recent_avg = sum(recent_scores) / len(recent_scores) if recent_scores else 0
        older_avg = sum(older_scores) / len(older_scores) if older_scores else 0

        if not recent_scores:
            trend_direction = 'stale'
        elif recent_avg > older_avg + 0.1:
            trend_direction = 'positive'
        elif recent_avg < older_avg - 0.1:
            trend_direction = 'negative'
        else:
            trend_direction = 'stable'

        # Generate recommendation
        recommendation = self._generate_recommendation(
            cumulative, confidence_interval, trend_direction
        )

        return {
            'theme': theme_or_topic,
            'cumulative_score': round(cumulative, 3),
            'sample_count': sample_count,
            'confidence_interval': confidence_interval,
            'trend_direction': trend_direction,
            'recent_avg': round(recent_avg, 3),
            'older_avg': round(older_avg, 3),
            'recommendation': recommendation,
            'scores_breakdown': weighted_scores,
        }

    def _generate_recommendation(
        self,
        cumulative: float,
        confidence: str,
        trend: str
    ) -> str:
        """Generate strategic recommendation based on aggregated data."""

        if confidence == 'insufficient':
            return "High variance, insufficient data → keep exploring with small pilots"

        if cumulative < -0.8 and confidence in ('high', 'medium'):
            return "Consistent negative safety signal → gate harder, require review"

        if cumulative > 0.5 and trend == 'positive':
            return "Positive momentum → propose scaled pilot, increase investment"

        if cumulative > 0.3 and confidence == 'high':
            return "Proven concept → ready for broader execution"

        if trend == 'negative' and confidence != 'insufficient':
            return "Declining trend → investigate root cause before continuing"

        if trend == 'stale':
            return "No recent data → consider refresher pilot to validate"

        return "Mixed signals → continue monitoring, gather more evidence"

    # =========================================================================
    # GUARDRAIL: PERMANENT BAN CHECK
    # =========================================================================

    def check_permanent_ban_eligible(self, theme_or_topic: str) -> Dict[str, Any]:
        """
        Check if an idea/theme qualifies for permanent ban.

        Guardrail: No idea can be permanently banned unless:
        - ≥2 independent safety FAILs
        - across ≥2 pilots
        - with confidence_weight ≥0.8

        This preserves innovation without ignoring risk.
        """
        from core.models_pilot_readiness import Experiment

        related_experiments = Experiment.objects.filter(
            name__icontains=theme_or_topic
        ) | Experiment.objects.filter(
            hypothesis__icontains=theme_or_topic
        )

        safety_fails = []
        now = timezone.now()

        for exp in related_experiments.filter(outcome_classification='fail'):
            # Check if safety failure using strong/weak classification
            if self._is_safety_failure(exp.halt_reason):
                # Calculate confidence
                age_days = (now - (exp.ended_at or exp.updated_at)).total_seconds() / 86400
                # Use 5 as default sample size for individual experiment
                confidence = self.calculate_confidence_weight(5)

                if confidence >= 0.8:
                    safety_fails.append({
                        'experiment_id': str(exp.id),
                        'experiment_name': exp.name,
                        'halt_reason': exp.halt_reason,
                        'confidence': confidence,
                    })

        independent_count = len(safety_fails)
        pilot_count = len(set(sf['experiment_id'] for sf in safety_fails))

        eligible_for_ban = independent_count >= 2 and pilot_count >= 2

        return {
            'theme': theme_or_topic,
            'eligible_for_permanent_ban': eligible_for_ban,
            'safety_fails_count': independent_count,
            'pilots_with_safety_fails': pilot_count,
            'required_safety_fails': 2,
            'required_pilots': 2,
            'required_confidence': 0.8,
            'safety_fails': safety_fails,
            'status': 'BANNED' if eligible_for_ban else 'ACTIVE',
            'message': (
                f"Theme '{theme_or_topic}' meets permanent ban criteria"
                if eligible_for_ban else
                f"Theme '{theme_or_topic}' remains conditionally revisitable"
            )
        }

    # =========================================================================
    # GET ALL WEIGHTED LEARNINGS
    # =========================================================================

    def get_weighted_learnings_for_thinking_agent(self) -> Dict[str, Any]:
        """
        Get all weighted learning data for ThinkingAgent context.

        Replaces the simple static weights with ChatGPT's formula.
        """
        from core.models_pilot_readiness import Experiment, ExperimentLearning

        now = timezone.now()

        # Calculate weighted learnings for all recent experiments
        weighted_learnings = []
        for exp in Experiment.objects.exclude(outcome_classification='pending').order_by('-ended_at')[:20]:
            age_days = (now - (exp.ended_at or exp.updated_at)).total_seconds() / 86400 if exp.ended_at else 0

            # Get related learning count as sample proxy
            learning_count = ExperimentLearning.objects.filter(experiment=exp).count()
            sample_size = max(1, learning_count)

            weight_data = self.calculate_learning_weight(
                outcome_classification=exp.outcome_classification,
                halt_reason=exp.halt_reason,
                sample_size=sample_size,
                age_days=age_days
            )

            # Get learning details if available
            learning = ExperimentLearning.objects.filter(experiment=exp).first()

            weighted_learnings.append({
                'experiment_name': exp.name,
                'outcome_classification': exp.outcome_classification,
                'weight': weight_data,
                'key_insight': learning.key_insight if learning else None,
                'what_worked': learning.what_worked if learning else None,
                'what_failed': learning.what_failed if learning else None,
                'recommendation': learning.future_recommendation if learning else None,
            })

        # Sort by absolute weight (most impactful first)
        weighted_learnings.sort(key=lambda x: abs(x['weight']['learning_weight']), reverse=True)

        # Calculate aggregate stats
        total_positive = sum(
            w['weight']['learning_weight']
            for w in weighted_learnings
            if w['weight']['learning_weight'] > 0
        )
        total_negative = sum(
            w['weight']['learning_weight']
            for w in weighted_learnings
            if w['weight']['learning_weight'] < 0
        )

        # Count experiments with insufficient evidence
        insufficient_count = sum(
            1 for w in weighted_learnings
            if w['weight'].get('insufficient_evidence', False)
        )

        return {
            'weighted_learnings': weighted_learnings[:10],  # Top 10 most impactful
            'aggregate_stats': {
                'total_experiments': len(weighted_learnings),
                'total_positive_weight': round(total_positive, 3),
                'total_negative_weight': round(total_negative, 3),
                'net_learning_weight': round(total_positive + total_negative, 3),
                'insufficient_evidence_count': insufficient_count,
                'learning_health': (
                    'positive' if total_positive > abs(total_negative)
                    else 'negative' if abs(total_negative) > total_positive
                    else 'neutral'
                ),
            },
            'formula_explanation': {
                'formula': 'learning_weight = outcome_signal × confidence_weight × decay_weight',
                'outcome_signals': self.OUTCOME_SIGNALS,
                'confidence_formula': 'min(1.0, log10(sample_size + 1))',
                'decay_formula': f'e^(-age_days / {self.DECAY_CONSTANT_DAYS})',
                'decay_constant_days': self.DECAY_CONSTANT_DAYS,
                'insufficient_evidence_threshold': self.INSUFFICIENT_EVIDENCE_THRESHOLD,
            },
            'evidence_guidance': {
                'proven': 'Has sufficient samples (≥3) - treat as reliable signal',
                'promising': 'Few samples (<3) - treat as promising, not proven',
            },
        }


# Convenience functions
def get_weighted_learnings_for_thinking_agent() -> Dict[str, Any]:
    """Get weighted learnings using ChatGPT's formula for ThinkingAgent."""
    service = WeightedLearningService()
    return service.get_weighted_learnings_for_thinking_agent()


def calculate_learning_weight(
    outcome: str,
    halt_reason: str = None,
    sample_size: int = 1,
    age_days: float = 0
) -> Dict[str, Any]:
    """Calculate learning weight for a single outcome."""
    return WeightedLearningService.calculate_learning_weight(
        outcome, halt_reason, sample_size, age_days
    )
