"""
Session 602: Boardroom Learning Integration

Integrates ChatGPT's weighted learning formula with the Boardroom decision system.
This allows decision-makers to see:
- Historical success probability based on similar past decisions
- Risk assessment based on weighted learning scores
- Confidence levels for informed decision-making

Key features:
1. Success probability calculation for new decisions
2. Risk assessment using negative weighted scores
3. Similar experiment discovery
4. Confidence-adjusted recommendations
"""

import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict

from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)


class BoardroomLearningService:
    """
    Session 602: Integrates weighted learning with Boardroom decisions.

    Uses ChatGPT's weighted learning formula to provide:
    - Success probability for pending decisions
    - Risk assessment based on historical failures
    - Confidence-adjusted recommendations
    """

    # Map decision types to experiment themes for matching
    DECISION_TYPE_THEMES = {
        'policy': ['policy', 'governance', 'rule', 'guideline', 'standard'],
        'architecture': ['architecture', 'design', 'structure', 'system', 'infrastructure'],
        'pipeline': ['pipeline', 'workflow', 'process', 'automation', 'flow'],
        'product': ['product', 'feature', 'user', 'ux', 'ui'],
        'experiment': ['experiment', 'pilot', 'test', 'trial', 'validation'],
        'guideline': ['guideline', 'best practice', 'recommendation', 'standard'],
    }

    # Map impact areas to experiment themes
    IMPACT_AREA_THEMES = {
        'prompting': ['prompt', 'llm', 'gpt', 'language model', 'generation'],
        'memory': ['memory', 'storage', 'context', 'persistence', 'cache'],
        'image': ['image', 'visual', 'picture', 'graphic', 'photo'],
        'video': ['video', 'animation', 'motion', 'clip'],
        'audio': ['audio', 'sound', 'music', 'voice', 'speech'],
        'workflow': ['workflow', 'automation', 'process', 'orchestration'],
        'agents': ['agent', 'ai', 'bot', 'assistant', 'model'],
        'security': ['security', 'privacy', 'safety', 'trust', 'compliance'],
        'infrastructure': ['infrastructure', 'server', 'deployment', 'scaling'],
        'product': ['product', 'feature', 'user', 'customer'],
        'legal': ['legal', 'court', 'law', 'compliance', 'document'],
        'research': ['research', 'analysis', 'data', 'insight'],
        'spider': ['spider', 'scraping', 'data collection', 'feed'],
    }

    def __init__(self):
        from core.services.weighted_learning import WeightedLearningService
        self.learning_service = WeightedLearningService()

    def get_decision_learning_context(self, decision) -> Dict[str, Any]:
        """
        Get comprehensive learning context for a Boardroom decision.

        Returns:
        - success_probability: Estimated chance of success (0-100%)
        - risk_level: low/medium/high/critical
        - confidence_level: Based on amount of relevant data
        - similar_experiments: Past experiments that inform this decision
        - weighted_insights: Key learnings with weights
        - recommendation: AI-generated guidance
        """
        from core.models_pilot_readiness import Experiment, ExperimentLearning

        # Build search terms from decision metadata
        search_terms = self._get_search_terms(decision)

        # Find related experiments
        similar_experiments = self._find_similar_experiments(search_terms)

        # Calculate success probability
        success_data = self._calculate_success_probability(similar_experiments)

        # Calculate risk level
        risk_data = self._calculate_risk_level(similar_experiments)

        # Get weighted insights
        weighted_insights = self._get_weighted_insights(similar_experiments)

        # Generate recommendation
        recommendation = self._generate_recommendation(
            success_data, risk_data, decision
        )

        return {
            'decision_id': str(decision.id),
            'decision_topic': decision.topic,
            'decision_type': decision.decision_type,
            'impact_area': decision.impact_area,
            'learning_context': {
                'success_probability': success_data['probability'],
                'success_confidence': success_data['confidence'],
                'risk_level': risk_data['level'],
                'risk_factors': risk_data['factors'],
                'confidence_level': success_data['confidence'],
                'evidence_status': success_data['evidence_status'],
            },
            'similar_experiments': similar_experiments[:5],  # Top 5 most relevant
            'weighted_insights': weighted_insights,
            'recommendation': recommendation,
            'search_terms_used': search_terms,
            'timestamp': timezone.now().isoformat(),
        }

    def _get_search_terms(self, decision) -> List[str]:
        """Build search terms from decision metadata."""
        terms = []

        # Add topic words
        if decision.topic:
            terms.extend(decision.topic.lower().split())

        # Add decision type themes
        type_themes = self.DECISION_TYPE_THEMES.get(decision.decision_type, [])
        terms.extend(type_themes)

        # Add impact area themes
        area_themes = self.IMPACT_AREA_THEMES.get(decision.impact_area, [])
        terms.extend(area_themes)

        # Add key insight words
        if decision.key_insights:
            for insight in decision.key_insights[:3]:
                if isinstance(insight, str):
                    terms.extend(insight.lower().split()[:5])

        # Deduplicate and filter short words
        terms = list(set(t for t in terms if len(t) > 2))
        return terms[:15]  # Limit to avoid over-matching

    def _find_similar_experiments(self, search_terms: List[str]) -> List[Dict]:
        """Find experiments related to the search terms."""
        from core.models_pilot_readiness import Experiment, ExperimentLearning

        if not search_terms:
            return []

        # Build query
        query = Q()
        for term in search_terms:
            query |= Q(name__icontains=term)
            query |= Q(hypothesis__icontains=term)

        experiments = Experiment.objects.filter(query).exclude(
            outcome_classification='pending'
        ).order_by('-ended_at')[:20]

        now = timezone.now()
        results = []

        for exp in experiments:
            # Calculate age
            ended_at = exp.ended_at or exp.updated_at
            age_days = (now - ended_at).total_seconds() / 86400 if ended_at else 0

            # Get learning count
            learning_count = ExperimentLearning.objects.filter(experiment=exp).count()
            sample_size = max(1, learning_count)

            # Calculate weight
            weight_data = self.learning_service.calculate_learning_weight(
                outcome_classification=exp.outcome_classification,
                halt_reason=exp.halt_reason,
                sample_size=sample_size,
                age_days=age_days
            )

            # Get learning details
            learning = ExperimentLearning.objects.filter(experiment=exp).first()

            # Calculate relevance score (how many search terms match)
            exp_text = f"{exp.name} {exp.hypothesis}".lower()
            matches = sum(1 for term in search_terms if term in exp_text)
            relevance = matches / len(search_terms) if search_terms else 0

            results.append({
                'id': str(exp.id),
                'name': exp.name,
                'outcome': exp.outcome_classification,
                'weight': weight_data,
                'age_days': round(age_days, 1),
                'relevance_score': round(relevance, 2),
                'key_insight': learning.key_insight if learning else None,
                'what_worked': learning.what_worked if learning else None,
                'what_failed': learning.what_failed if learning else None,
            })

        # Sort by relevance * absolute weight
        results.sort(
            key=lambda x: x['relevance_score'] * abs(x['weight']['learning_weight']),
            reverse=True
        )

        return results

    def _calculate_success_probability(self, experiments: List[Dict]) -> Dict[str, Any]:
        """Calculate success probability based on similar experiments."""
        if not experiments:
            return {
                'probability': 50,  # Neutral when no data
                'confidence': 'insufficient',
                'evidence_status': 'no_data',
                'basis': 'No similar experiments found - using neutral estimate',
            }

        # Calculate weighted success score
        total_positive = sum(
            e['weight']['learning_weight']
            for e in experiments
            if e['weight']['learning_weight'] > 0
        )
        total_negative = sum(
            abs(e['weight']['learning_weight'])
            for e in experiments
            if e['weight']['learning_weight'] < 0
        )

        total_weight = total_positive + total_negative
        if total_weight == 0:
            probability = 50
        else:
            # Probability based on ratio of positive to total
            probability = int((total_positive / total_weight) * 100)

        # Determine confidence level
        sample_count = len(experiments)
        insufficient_count = sum(
            1 for e in experiments
            if e['weight'].get('insufficient_evidence', False)
        )

        if sample_count >= 10:
            confidence = 'high'
        elif sample_count >= 5:
            confidence = 'medium'
        elif sample_count >= 2:
            confidence = 'low'
        else:
            confidence = 'insufficient'

        # Evidence status
        if insufficient_count > sample_count / 2:
            evidence_status = 'mostly_preliminary'
        elif sample_count >= 3:
            evidence_status = 'established'
        else:
            evidence_status = 'preliminary'

        return {
            'probability': probability,
            'confidence': confidence,
            'evidence_status': evidence_status,
            'positive_weight': round(total_positive, 3),
            'negative_weight': round(total_negative, 3),
            'sample_count': sample_count,
            'basis': f'Based on {sample_count} similar experiments',
        }

    def _calculate_risk_level(self, experiments: List[Dict]) -> Dict[str, Any]:
        """Calculate risk level based on safety failures in similar experiments."""
        if not experiments:
            return {
                'level': 'unknown',
                'score': 0,
                'factors': ['No similar experiments to assess risk'],
            }

        # Count safety failures
        safety_fails = [
            e for e in experiments
            if e['weight']['signal_type'] == 'fail_safety'
        ]

        # Calculate risk score (sum of negative safety weights)
        risk_score = sum(
            abs(e['weight']['learning_weight'])
            for e in safety_fails
        )

        # Determine risk level
        if risk_score >= 1.5:
            level = 'critical'
        elif risk_score >= 0.8:
            level = 'high'
        elif risk_score >= 0.3:
            level = 'medium'
        elif risk_score > 0:
            level = 'low'
        else:
            level = 'minimal'

        # Extract risk factors
        factors = []
        for e in safety_fails[:3]:  # Top 3 safety concerns
            if e.get('what_failed'):
                factors.append(f"{e['name']}: {e['what_failed'][:100]}")
            else:
                factors.append(f"Safety issue in: {e['name']}")

        if not factors:
            factors = ['No safety failures detected in similar experiments']

        return {
            'level': level,
            'score': round(risk_score, 3),
            'safety_fail_count': len(safety_fails),
            'factors': factors,
        }

    def _get_weighted_insights(self, experiments: List[Dict]) -> List[Dict]:
        """Extract weighted insights from similar experiments."""
        insights = []

        for exp in experiments[:10]:
            if exp.get('key_insight'):
                # Determine icon based on outcome
                if exp['outcome'] == 'pass':
                    icon = '🟢'
                elif exp['outcome'] == 'fail':
                    icon = '🔴'
                else:
                    icon = '🟡'

                insights.append({
                    'icon': icon,
                    'experiment': exp['name'],
                    'outcome': exp['outcome'],
                    'weight': exp['weight']['learning_weight'],
                    'evidence_status': exp['weight'].get('evidence_status', 'unknown'),
                    'insight': exp['key_insight'],
                    'what_worked': exp.get('what_worked'),
                    'what_failed': exp.get('what_failed'),
                })

        return insights

    def _generate_recommendation(
        self,
        success_data: Dict,
        risk_data: Dict,
        decision
    ) -> Dict[str, Any]:
        """Generate recommendation based on learning context."""
        probability = success_data['probability']
        risk_level = risk_data['level']
        confidence = success_data['confidence']

        # Determine action recommendation
        if risk_level in ('critical', 'high') and confidence != 'insufficient':
            action = 'gate'
            reasoning = f"High risk detected ({risk_level}) with {confidence} confidence. Recommend requiring additional review or safeguards before promoting."
        elif probability >= 70 and confidence in ('high', 'medium'):
            action = 'approve'
            reasoning = f"High success probability ({probability}%) based on {confidence} confidence data. Similar decisions have performed well."
        elif probability >= 50 and risk_level in ('minimal', 'low'):
            action = 'approve_with_monitoring'
            reasoning = f"Moderate success probability ({probability}%) with low risk. Consider promoting with success metrics monitoring."
        elif confidence == 'insufficient':
            action = 'pilot_first'
            reasoning = "Insufficient historical data for confident prediction. Recommend running a small pilot before full promotion."
        else:
            action = 'defer'
            reasoning = f"Low success probability ({probability}%) or elevated risk ({risk_level}). Consider deferring or gathering more evidence."

        return {
            'action': action,
            'reasoning': reasoning,
            'confidence_note': self._get_confidence_note(confidence),
            'decision_type': decision.decision_type,
            'impact_area': decision.impact_area,
        }

    def _get_confidence_note(self, confidence: str) -> str:
        """Get human-readable confidence note."""
        notes = {
            'high': 'Based on substantial historical evidence (10+ similar experiments)',
            'medium': 'Based on moderate evidence (5-9 similar experiments)',
            'low': 'Based on limited evidence (2-4 similar experiments)',
            'insufficient': 'Warning: Very limited data - treat as preliminary guidance only',
        }
        return notes.get(confidence, 'Evidence level unknown')

    def enrich_decisions_list(self, decisions: List) -> List[Dict]:
        """
        Enrich a list of decisions with learning insights.

        This is a lighter-weight version for list views that adds:
        - Success probability
        - Risk level
        - Confidence level

        without the full detail of get_decision_learning_context.
        """
        enriched = []

        for decision in decisions:
            # Get search terms
            search_terms = self._get_search_terms(decision)

            # Find similar experiments (limited)
            similar = self._find_similar_experiments(search_terms)[:5]

            # Calculate quick metrics
            success_data = self._calculate_success_probability(similar)
            risk_data = self._calculate_risk_level(similar)

            enriched.append({
                'id': str(decision.id),
                'topic': decision.topic,
                'decision_type': decision.decision_type,
                'impact_area': decision.impact_area,
                'status': decision.status,
                'learning_summary': {
                    'success_probability': success_data['probability'],
                    'risk_level': risk_data['level'],
                    'confidence': success_data['confidence'],
                    'evidence_status': success_data['evidence_status'],
                    'similar_count': len(similar),
                },
            })

        return enriched


# Convenience function
def get_decision_learning_context(decision_id: str) -> Dict[str, Any]:
    """Get learning context for a specific decision by ID."""
    from core.models_unified_system import AgentDecisionSummary

    decision = AgentDecisionSummary.objects.get(id=decision_id)
    service = BoardroomLearningService()
    return service.get_decision_learning_context(decision)
