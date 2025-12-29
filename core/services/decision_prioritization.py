"""
Session 604: Decision Prioritization Service

Auto-prioritizes the Boardroom decision queue based on:
- Success probability from weighted learning
- Risk level from safety failures
- Confidence level from evidence amount

Features:
1. Priority score calculation (0-100)
2. Smart queue ordering
3. High-risk flagging
4. Quick-win identification
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)


class PriorityTier(Enum):
    """Priority tiers for decision queue."""
    QUICK_WIN = "quick_win"  # High probability, low risk, good confidence
    RECOMMENDED = "recommended"  # Good probability, acceptable risk
    STANDARD = "standard"  # Moderate metrics
    NEEDS_REVIEW = "needs_review"  # Low probability or elevated risk
    HIGH_RISK = "high_risk"  # Flagged for additional scrutiny


@dataclass
class PrioritizedDecision:
    """A decision with priority scoring."""
    decision_id: str
    topic: str
    decision_type: str
    impact_area: str
    status: str
    priority_score: int  # 0-100
    priority_tier: PriorityTier
    success_probability: int
    risk_level: str
    confidence: str
    flags: List[str]
    recommendation: str
    similar_count: int


class DecisionPrioritizationService:
    """
    Session 604: Auto-prioritizes the Boardroom decision queue.

    Uses the weighted learning system to calculate priority scores and
    sort decisions for efficient human review.
    """

    # Risk level weights (lower is better for priority)
    RISK_WEIGHTS = {
        'minimal': 0,
        'low': 5,
        'medium': 15,
        'high': 30,
        'critical': 50,
        'unknown': 10,
    }

    # Confidence multipliers
    CONFIDENCE_MULTIPLIERS = {
        'high': 1.0,
        'medium': 0.85,
        'low': 0.7,
        'insufficient': 0.5,
    }

    def __init__(self):
        from core.services.boardroom_learning import BoardroomLearningService
        self.learning_service = BoardroomLearningService()

    def get_prioritized_queue(
        self,
        statuses: List[str] = None,
        limit: int = 50,
        include_flags: bool = True
    ) -> Dict[str, Any]:
        """
        Get prioritized decision queue.

        Args:
            statuses: Filter by status (default: ['draft', 'review'])
            limit: Maximum decisions to return
            include_flags: Include warning flags

        Returns:
            Prioritized queue with stats
        """
        from core.models_unified_system import AgentDecisionSummary

        if statuses is None:
            statuses = ['draft', 'review']

        # Get pending decisions
        decisions = AgentDecisionSummary.objects.filter(
            status__in=statuses
        ).order_by('-created_at')[:limit * 2]  # Get extra for filtering

        # Calculate priority for each
        prioritized = []
        for decision in decisions:
            priority_data = self._calculate_priority(decision)
            prioritized.append(priority_data)

        # Sort by priority score (descending)
        prioritized.sort(key=lambda x: x.priority_score, reverse=True)

        # Take top N
        prioritized = prioritized[:limit]

        # Calculate stats
        stats = self._calculate_queue_stats(prioritized)

        return {
            'decisions': [self._to_dict(p) for p in prioritized],
            'stats': stats,
            'timestamp': timezone.now().isoformat(),
        }

    def _calculate_priority(self, decision) -> PrioritizedDecision:
        """Calculate priority score for a single decision."""
        # Get learning context
        search_terms = self.learning_service._get_search_terms(decision)
        similar = self.learning_service._find_similar_experiments(search_terms)[:10]
        success_data = self.learning_service._calculate_success_probability(similar)
        risk_data = self.learning_service._calculate_risk_level(similar)

        # Extract metrics
        success_prob = success_data['probability']
        risk_level = risk_data['level']
        confidence = success_data['confidence']

        # Calculate base priority score
        # Start with success probability (0-100)
        base_score = success_prob

        # Apply risk penalty
        risk_penalty = self.RISK_WEIGHTS.get(risk_level, 10)
        base_score -= risk_penalty

        # Apply confidence multiplier
        conf_multiplier = self.CONFIDENCE_MULTIPLIERS.get(confidence, 0.7)
        priority_score = int(base_score * conf_multiplier)

        # Clamp to 0-100
        priority_score = max(0, min(100, priority_score))

        # Determine priority tier
        tier = self._determine_tier(success_prob, risk_level, confidence, priority_score)

        # Generate flags
        flags = self._generate_flags(success_prob, risk_level, confidence, similar)

        # Generate recommendation
        recommendation = self._generate_quick_recommendation(
            success_prob, risk_level, confidence, tier
        )

        return PrioritizedDecision(
            decision_id=str(decision.id),
            topic=decision.topic,
            decision_type=decision.decision_type,
            impact_area=decision.impact_area,
            status=decision.status,
            priority_score=priority_score,
            priority_tier=tier,
            success_probability=success_prob,
            risk_level=risk_level,
            confidence=confidence,
            flags=flags,
            recommendation=recommendation,
            similar_count=len(similar),
        )

    def _determine_tier(
        self,
        success_prob: int,
        risk_level: str,
        confidence: str,
        priority_score: int
    ) -> PriorityTier:
        """Determine the priority tier for a decision."""
        # High risk always gets flagged
        if risk_level in ('critical', 'high'):
            return PriorityTier.HIGH_RISK

        # Quick wins: high probability, low risk, good confidence
        if (success_prob >= 70 and
            risk_level in ('minimal', 'low') and
            confidence in ('high', 'medium')):
            return PriorityTier.QUICK_WIN

        # Recommended: good probability, acceptable risk
        if success_prob >= 60 and risk_level in ('minimal', 'low', 'medium'):
            return PriorityTier.RECOMMENDED

        # Needs review: low probability or unknown risk
        if success_prob < 40 or confidence == 'insufficient':
            return PriorityTier.NEEDS_REVIEW

        # Standard: everything else
        return PriorityTier.STANDARD

    def _generate_flags(
        self,
        success_prob: int,
        risk_level: str,
        confidence: str,
        similar_experiments: List[Dict]
    ) -> List[str]:
        """Generate warning/info flags for a decision."""
        flags = []

        # Risk flags
        if risk_level == 'critical':
            flags.append('🚨 CRITICAL RISK - Requires executive review')
        elif risk_level == 'high':
            flags.append('⚠️ HIGH RISK - Additional safeguards recommended')

        # Probability flags
        if success_prob < 30:
            flags.append('📉 Low success probability (<30%)')
        elif success_prob >= 80:
            flags.append('📈 High success probability (80%+)')

        # Confidence flags
        if confidence == 'insufficient':
            flags.append('❓ Insufficient data - Consider pilot first')
        elif confidence == 'high':
            flags.append('✅ High confidence prediction')

        # Pattern flags
        safety_fails = sum(
            1 for e in similar_experiments
            if e.get('weight', {}).get('signal_type') == 'fail_safety'
        )
        if safety_fails >= 2:
            flags.append(f'🛡️ {safety_fails} safety failures in similar experiments')

        # No similar experiments
        if len(similar_experiments) == 0:
            flags.append('🆕 No similar experiments - Novel decision')

        return flags

    def _generate_quick_recommendation(
        self,
        success_prob: int,
        risk_level: str,
        confidence: str,
        tier: PriorityTier
    ) -> str:
        """Generate a quick recommendation string."""
        if tier == PriorityTier.QUICK_WIN:
            return "✅ Quick Win - Approve with confidence"
        elif tier == PriorityTier.HIGH_RISK:
            return "🚨 Requires additional review before promotion"
        elif tier == PriorityTier.RECOMMENDED:
            return "👍 Recommended for approval"
        elif tier == PriorityTier.NEEDS_REVIEW:
            return "🔍 Needs careful review - Limited evidence"
        else:
            return "📋 Standard review process"

    def _calculate_queue_stats(self, prioritized: List[PrioritizedDecision]) -> Dict:
        """Calculate summary statistics for the queue."""
        if not prioritized:
            return {
                'total': 0,
                'by_tier': {},
                'avg_priority': 0,
                'high_risk_count': 0,
                'quick_win_count': 0,
            }

        by_tier = {}
        for tier in PriorityTier:
            count = sum(1 for p in prioritized if p.priority_tier == tier)
            if count > 0:
                by_tier[tier.value] = count

        avg_priority = sum(p.priority_score for p in prioritized) / len(prioritized)

        return {
            'total': len(prioritized),
            'by_tier': by_tier,
            'avg_priority': round(avg_priority, 1),
            'high_risk_count': by_tier.get('high_risk', 0),
            'quick_win_count': by_tier.get('quick_win', 0),
        }

    def _to_dict(self, p: PrioritizedDecision) -> Dict:
        """Convert PrioritizedDecision to dictionary."""
        return {
            'id': p.decision_id,
            'topic': p.topic,
            'decision_type': p.decision_type,
            'impact_area': p.impact_area,
            'status': p.status,
            'priority': {
                'score': p.priority_score,
                'tier': p.priority_tier.value,
                'tier_display': self._get_tier_display(p.priority_tier),
            },
            'learning': {
                'success_probability': p.success_probability,
                'risk_level': p.risk_level,
                'confidence': p.confidence,
                'similar_count': p.similar_count,
            },
            'flags': p.flags,
            'recommendation': p.recommendation,
        }

    def _get_tier_display(self, tier: PriorityTier) -> str:
        """Get display name for tier."""
        displays = {
            PriorityTier.QUICK_WIN: "🚀 Quick Win",
            PriorityTier.RECOMMENDED: "👍 Recommended",
            PriorityTier.STANDARD: "📋 Standard",
            PriorityTier.NEEDS_REVIEW: "🔍 Needs Review",
            PriorityTier.HIGH_RISK: "🚨 High Risk",
        }
        return displays.get(tier, tier.value)

    def get_decision_priority(self, decision_id: str) -> Dict[str, Any]:
        """Get priority details for a single decision."""
        from core.models_unified_system import AgentDecisionSummary

        decision = AgentDecisionSummary.objects.get(id=decision_id)
        priority_data = self._calculate_priority(decision)

        # Get full learning context for detail view
        learning_context = self.learning_service.get_decision_learning_context(decision)

        result = self._to_dict(priority_data)
        result['learning_context'] = learning_context

        return result


# Convenience functions
def get_prioritized_decision_queue(limit: int = 50) -> Dict[str, Any]:
    """Get the prioritized decision queue."""
    service = DecisionPrioritizationService()
    return service.get_prioritized_queue(limit=limit)


def get_decision_priority(decision_id: str) -> Dict[str, Any]:
    """Get priority for a specific decision."""
    service = DecisionPrioritizationService()
    return service.get_decision_priority(decision_id)
