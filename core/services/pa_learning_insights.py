"""
Session 605: PA Learning Insights Service

Integrates the weighted learning system with the Personal Assistant to provide:
- Success probability predictions for user plans/decisions
- Running pilot status and progress
- Similar experiments with outcomes
- Learning-based recommendations

When a user says "I want to try X" or "Should I do Y?", the PA can now
respond with "Based on 5 similar experiments, this approach has a 73% success rate."
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)


class PALearningInsightsService:
    """
    Session 605: Provides learning insights for Personal Assistant context.

    Key features:
    1. Analyze user messages for decision/planning intent
    2. Find similar historical experiments
    3. Calculate success probability using weighted learning
    4. Surface active pilot status
    5. Format insights for PA prompt injection
    """

    # Keywords that suggest the user is considering a decision
    DECISION_KEYWORDS = [
        'should i', 'should we', 'want to try', 'thinking about',
        'planning to', 'considering', 'what if', 'would it work',
        'is it worth', 'good idea', 'bad idea', 'recommend',
        'pros and cons', 'try', 'experiment', 'test', 'pilot',
        'implement', 'build', 'create', 'launch', 'start'
    ]

    # Keywords for checking pilot/experiment status
    PILOT_STATUS_KEYWORDS = [
        'pilot', 'experiment', 'running', 'active', 'progress',
        'how is', 'status of', 'update on', 'check on',
        'experiments', 'pilots'
    ]

    # Theme mappings for experiment matching
    TOPIC_THEMES = {
        'content': ['content', 'writing', 'blog', 'article', 'post', 'copy'],
        'financial': ['financial', 'trading', 'investment', 'stocks', 'crypto', 'money'],
        'product': ['product', 'feature', 'ux', 'user', 'interface', 'design'],
        'marketing': ['marketing', 'campaign', 'ads', 'growth', 'audience'],
        'automation': ['automation', 'workflow', 'pipeline', 'bot', 'automate'],
        'ai': ['ai', 'model', 'gpt', 'llm', 'agent', 'ml', 'machine learning'],
        'research': ['research', 'analysis', 'data', 'insight', 'study'],
        'legal': ['legal', 'court', 'law', 'document', 'case'],
    }

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.PALearningInsightsService")

    def get_learning_insights(self, message: str, user_context: dict = None) -> Dict[str, Any]:
        """
        Get learning insights relevant to the user's message.

        Args:
            message: User's message to the PA
            user_context: Optional user preferences/context

        Returns:
            Dict with:
                - has_insights: bool
                - prediction: Success probability if decision detected
                - active_pilots: Running pilots relevant to message
                - similar_experiments: Past experiments with outcomes
                - learning_summary: Formatted text for PA context
                - recommendation: AI guidance based on learning
        """
        try:
            message_lower = message.lower()

            result = {
                'has_insights': False,
                'decision_detected': False,
                'prediction': None,
                'active_pilots': [],
                'similar_experiments': [],
                'learning_summary': '',
                'recommendation': '',
                'metadata': {
                    'similar_count': 0,
                    'active_pilot_count': 0,
                    'confidence': 'insufficient',
                }
            }

            # Check if user is asking about pilot status
            if self._wants_pilot_status(message_lower):
                pilots = self._get_active_pilots()
                result['active_pilots'] = pilots
                result['has_insights'] = len(pilots) > 0
                result['metadata']['active_pilot_count'] = len(pilots)
                self.logger.info(f"Found {len(pilots)} active pilots")

            # Check if user is considering a decision
            if self._is_decision_query(message_lower):
                result['decision_detected'] = True

                # Extract topic from message
                topic = self._extract_topic(message)
                themes = self._detect_themes(topic)

                # Get similar experiments and prediction
                similar = self._find_similar_experiments(topic, themes)
                result['similar_experiments'] = similar[:5]
                result['metadata']['similar_count'] = len(similar)

                if similar:
                    prediction = self._calculate_prediction(similar)
                    result['prediction'] = prediction
                    result['recommendation'] = self._generate_recommendation(
                        topic, prediction, similar
                    )
                    result['has_insights'] = True
                    result['metadata']['confidence'] = prediction.get('confidence', 'low')
                    self.logger.info(
                        f"Decision detected: {topic[:50]}... "
                        f"Prediction: {prediction.get('success_probability', 0)}% "
                        f"({len(similar)} similar experiments)"
                    )

            # Format learning summary if we have insights
            if result['has_insights']:
                result['learning_summary'] = self._format_learning_summary(result)

            return result

        except Exception as e:
            self.logger.error(f"Error getting learning insights: {e}", exc_info=True)
            return {
                'has_insights': False,
                'error': str(e)
            }

    def _wants_pilot_status(self, message_lower: str) -> bool:
        """Check if user wants pilot/experiment status."""
        return any(kw in message_lower for kw in self.PILOT_STATUS_KEYWORDS)

    def _is_decision_query(self, message_lower: str) -> bool:
        """Check if the message suggests the user is considering a decision."""
        return any(kw in message_lower for kw in self.DECISION_KEYWORDS)

    def _extract_topic(self, message: str) -> str:
        """Extract the main topic/subject from the message."""
        # Remove common question prefixes
        topic = message.strip()
        prefixes = [
            'should i', 'should we', 'i want to', "i'm thinking about",
            'we are considering', 'what if we', 'is it worth',
            'would it be a good idea to', 'can you help me',
            'i need to', "let's", 'help me', 'please'
        ]

        topic_lower = topic.lower()
        for prefix in prefixes:
            if topic_lower.startswith(prefix):
                topic = topic[len(prefix):].strip()
                break

        # Limit length
        if len(topic) > 150:
            topic = topic[:150]

        return topic

    def _detect_themes(self, topic: str) -> List[str]:
        """Detect themes in the topic for experiment matching."""
        topic_lower = topic.lower()
        detected_themes = []

        for theme, keywords in self.TOPIC_THEMES.items():
            if any(kw in topic_lower for kw in keywords):
                detected_themes.append(theme)

        return detected_themes

    def _get_active_pilots(self) -> List[Dict]:
        """Get currently running pilots/experiments."""
        try:
            from core.models_pilot_readiness import Experiment

            active = Experiment.objects.filter(
                status__in=['running', 'pilot_running', 'active', 'in_progress']
            ).order_by('-created_at')[:10]

            pilots = []
            for exp in active:
                # Calculate duration
                started = exp.started_at or exp.created_at
                duration = timezone.now() - started
                days = duration.days

                pilots.append({
                    'id': str(exp.id),
                    'name': exp.name[:80] if exp.name else 'Unnamed',
                    'hypothesis': exp.hypothesis[:150] if exp.hypothesis else '',
                    'primary_kpi': exp.primary_kpi or 'Not specified',
                    'target_value': exp.target_value,
                    'current_value': exp.current_value,
                    'status': exp.status,
                    'days_running': days,
                    'started_at': started.isoformat() if started else None,
                })

            return pilots

        except Exception as e:
            self.logger.error(f"Error getting active pilots: {e}")
            return []

    def _find_similar_experiments(self, topic: str, themes: List[str]) -> List[Dict]:
        """Find experiments similar to the topic."""
        try:
            from core.models_pilot_readiness import Experiment, ExperimentLearning

            # Build query from topic and themes
            query = Q()

            # Search in experiment name and hypothesis
            topic_words = [w for w in topic.lower().split() if len(w) > 3][:10]
            for word in topic_words:
                query |= Q(name__icontains=word) | Q(hypothesis__icontains=word)

            # Add theme-based search
            for theme in themes:
                theme_keywords = self.TOPIC_THEMES.get(theme, [])
                for kw in theme_keywords[:3]:
                    query |= Q(name__icontains=kw) | Q(hypothesis__icontains=kw)

            if not query:
                return []

            # Get experiments with their learning (OneToOne)
            experiments = Experiment.objects.filter(query).select_related(
                'learning'
            ).order_by('-created_at')[:20]

            similar = []
            for exp in experiments:
                # Get learning data (OneToOne relationship)
                learning = getattr(exp, 'learning', None)
                confidence = learning.confidence_score if learning else 0

                # Determine outcome from status
                if exp.status == 'success':
                    outcome = 'success'
                elif exp.status in ['failed', 'halted']:
                    outcome = 'failed'
                else:
                    outcome = 'in_progress'

                # Get key insight from learning if available
                key_insight = learning.key_insight if learning else None

                similar.append({
                    'id': str(exp.id),
                    'name': exp.name[:80] if exp.name else 'Unnamed',
                    'hypothesis': exp.hypothesis[:100] if exp.hypothesis else '',
                    'outcome': outcome,
                    'status': exp.status,
                    'has_learning': learning is not None,
                    'confidence': round(confidence, 2) if confidence else 0,
                    'key_insight': key_insight[:150] if key_insight else '',
                    'result_summary': exp.result_summary[:150] if exp.result_summary else '',
                    'primary_kpi': exp.primary_kpi or '',
                })

            return similar

        except Exception as e:
            self.logger.error(f"Error finding similar experiments: {e}")
            return []

    def _calculate_prediction(self, similar_experiments: List[Dict]) -> Dict[str, Any]:
        """Calculate success probability from similar experiments."""
        if not similar_experiments:
            return {
                'success_probability': 50,
                'confidence': 'insufficient',
                'sample_size': 0,
                'message': 'No similar experiments found'
            }

        # Count outcomes
        successes = sum(1 for e in similar_experiments if e['outcome'] == 'success')
        failures = sum(1 for e in similar_experiments if e['outcome'] == 'failed')
        in_progress = sum(1 for e in similar_experiments if e['outcome'] == 'in_progress')

        # Calculate from completed experiments
        completed = successes + failures

        if completed == 0:
            return {
                'success_probability': 50,
                'confidence': 'insufficient',
                'sample_size': len(similar_experiments),
                'in_progress_count': in_progress,
                'message': f'{in_progress} similar experiments still running'
            }

        # Calculate success rate
        success_rate = (successes / completed) * 100

        # Determine confidence based on sample size
        if completed >= 5:
            confidence = 'high'
        elif completed >= 3:
            confidence = 'medium'
        else:
            confidence = 'low'

        # Apply confidence adjustment (Session 601 weighted learning style)
        confidence_multiplier = {'high': 1.0, 'medium': 0.85, 'low': 0.7}
        adjusted_probability = int(success_rate * confidence_multiplier[confidence])

        return {
            'success_probability': adjusted_probability,
            'raw_success_rate': round(success_rate, 1),
            'confidence': confidence,
            'sample_size': completed,
            'successes': successes,
            'failures': failures,
            'in_progress_count': in_progress,
            'message': f'Based on {completed} similar experiments ({successes} succeeded, {failures} failed)'
        }

    def _generate_recommendation(
        self,
        topic: str,
        prediction: Dict,
        similar: List[Dict]
    ) -> str:
        """Generate a recommendation based on learning data."""
        prob = prediction.get('success_probability', 50)
        confidence = prediction.get('confidence', 'low')
        sample_size = prediction.get('sample_size', 0)

        if sample_size == 0:
            return (
                "This appears to be a novel approach with no similar experiments. "
                "Consider running a small pilot first to gather data."
            )

        if prob >= 70:
            rec = f"Historical data suggests good success potential ({prob}% probability). "
            if confidence == 'high':
                rec += "We have strong evidence from similar experiments."
            else:
                rec += "Consider this a promising direction, but monitor closely."
        elif prob >= 50:
            rec = f"Mixed results from similar experiments ({prob}% success rate). "
            rec += "Success depends on execution. Review what worked in past experiments."
        else:
            rec = f"Similar experiments have had limited success ({prob}% rate). "
            rec += "Consider reviewing past failures before proceeding, or try a different approach."

        # Add insight from successful experiment if available
        success_exp = next((e for e in similar if e['outcome'] == 'success'), None)
        if success_exp and success_exp.get('result_summary'):
            rec += f"\n\nFrom a successful experiment: \"{success_exp['result_summary'][:100]}...\""

        return rec

    def _format_learning_summary(self, data: Dict) -> str:
        """Format learning insights for PA context injection."""
        parts = []

        # Active pilots section
        if data.get('active_pilots'):
            parts.append("### Active Pilots You're Running:")
            for pilot in data['active_pilots'][:5]:
                name = pilot['name'][:50]
                days = pilot.get('days_running', 0)
                kpi = pilot.get('primary_kpi', 'N/A')
                current = pilot.get('current_value')
                target = pilot.get('target_value')

                progress = ""
                if current is not None and target is not None:
                    try:
                        pct = (float(current) / float(target)) * 100
                        progress = f" ({pct:.0f}% to target)"
                    except (ValueError, ZeroDivisionError):
                        pass

                parts.append(f"- **{name}** - Day {days}{progress}")
                if kpi != 'N/A':
                    parts.append(f"  KPI: {kpi}")

        # Prediction section
        if data.get('prediction') and data.get('decision_detected'):
            pred = data['prediction']
            prob = pred.get('success_probability', 0)
            confidence = pred.get('confidence', 'low')
            message = pred.get('message', '')

            # Visual indicator
            if prob >= 70:
                indicator = "📈"
            elif prob >= 50:
                indicator = "📊"
            else:
                indicator = "📉"

            parts.append(f"\n### Learning-Based Prediction:")
            parts.append(f"{indicator} **{prob}% success probability** ({confidence} confidence)")
            parts.append(f"_{message}_")

        # Similar experiments section
        if data.get('similar_experiments'):
            parts.append("\n### Similar Past Experiments:")
            for exp in data['similar_experiments'][:3]:
                name = exp['name'][:40]
                outcome = exp['outcome']
                outcome_emoji = {'success': '✅', 'failed': '❌', 'in_progress': '🔄'}
                emoji = outcome_emoji.get(outcome, '❓')
                parts.append(f"- {emoji} {name} ({outcome})")

        # Recommendation
        if data.get('recommendation'):
            parts.append(f"\n### Recommendation:")
            parts.append(data['recommendation'])

        return "\n".join(parts)


# Convenience function
def get_pa_learning_insights(message: str) -> Dict[str, Any]:
    """Get learning insights for a PA message."""
    service = PALearningInsightsService()
    return service.get_learning_insights(message)
