"""
Session 930: Agent Feedback Service

Handles 👍/👎 feedback on agent executions and uses that data
to learn user preferences per agent. Works with the existing
AgentLearningService for deeper preference tracking.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg, Count, Q

logger = logging.getLogger(__name__)


@dataclass
class AgentEffectiveness:
    """Summary of how effective an agent is for a user"""
    agent_id: str
    agent_name: str
    total_feedbacks: int
    helpful_count: int
    not_helpful_count: int
    neutral_count: int
    effectiveness_score: float  # -1 to 1
    recent_trend: str  # 'improving', 'declining', 'stable'
    top_successful_contexts: List[str]
    areas_for_improvement: List[str]


class AgentFeedbackService:
    """
    Session 930: Track and learn from user feedback on agents.

    This service complements the existing AgentLearningService by:
    - Using the new AgentFeedback model for simple 👍/👎 tracking
    - Calculating per-agent effectiveness scores
    - Adjusting context based on what works for each user+agent
    """

    def __init__(self):
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes

    def record_feedback(
        self,
        user,
        agent,
        rating: int,
        execution_id: str = None,
        deliverable=None,
        feedback_text: str = '',
        task_description: str = '',
        context_snapshot: Dict = None,
    ) -> 'AgentFeedback':
        """
        Record user feedback on an agent execution.

        Args:
            user: User giving feedback
            agent: Agent that was executed
            rating: 1 (helpful), 0 (neutral), -1 (not helpful)
            execution_id: Optional UUID of AgentExecution
            deliverable: Optional Deliverable that was created
            feedback_text: Optional detailed feedback
            task_description: What user was trying to accomplish
            context_snapshot: The context that was used

        Returns:
            Created AgentFeedback instance
        """
        from core.models_user_learning import AgentFeedback
        import uuid

        feedback = AgentFeedback.objects.create(
            user=user,
            agent=agent,
            execution_id=uuid.UUID(execution_id) if execution_id else None,
            deliverable=deliverable,
            rating=rating,
            feedback_text=feedback_text,
            task_description=task_description,
            context_snapshot=context_snapshot or {},
        )

        # Invalidate cache for this user+agent
        cache_key = f"{user.id}_{agent.id}"
        if cache_key in self._cache:
            del self._cache[cache_key]

        logger.info(
            f"Recorded feedback: user={user.username}, agent={agent.name}, "
            f"rating={rating}, execution={execution_id}"
        )

        # Also record in the existing AgentLearningService for deep learning
        self._sync_to_learning_service(user, agent, rating, context_snapshot)

        return feedback

    def _sync_to_learning_service(self, user, agent, rating: int, context: Dict = None):
        """Sync feedback to the existing AgentLearningService."""
        try:
            from core.services.agent_learning_service import (
                get_learning_service,
                InteractionType
            )

            service = get_learning_service()

            # Map rating to interaction type
            if rating == 1:
                interaction_type = InteractionType.USED
            elif rating == -1:
                interaction_type = InteractionType.REJECTED
            else:
                interaction_type = InteractionType.CREATED

            service.record_interaction(
                user_id=user.id,
                agent_name=agent.name,
                interaction_type=interaction_type,
                input_data=context or {},
                output_data={'feedback_rating': rating},
                rating=3 if rating == 0 else (5 if rating == 1 else 1),
            )
        except Exception as e:
            logger.debug(f"Could not sync to AgentLearningService: {e}")

    def get_agent_effectiveness(self, user, agent) -> AgentEffectiveness:
        """
        Get effectiveness metrics for a user+agent combination.

        Returns AgentEffectiveness with success rates and patterns.
        """
        from core.models_user_learning import AgentFeedback

        # Check cache
        cache_key = f"{user.id}_{agent.id}"
        if cache_key in self._cache:
            cached, timestamp = self._cache[cache_key]
            if (timezone.now() - timestamp).seconds < self._cache_ttl:
                return cached

        # Query feedbacks
        feedbacks = AgentFeedback.objects.filter(user=user, agent=agent)

        total = feedbacks.count()
        if total == 0:
            result = AgentEffectiveness(
                agent_id=str(agent.id),
                agent_name=agent.name,
                total_feedbacks=0,
                helpful_count=0,
                not_helpful_count=0,
                neutral_count=0,
                effectiveness_score=0.0,
                recent_trend='stable',
                top_successful_contexts=[],
                areas_for_improvement=[],
            )
            return result

        helpful = feedbacks.filter(rating=1).count()
        not_helpful = feedbacks.filter(rating=-1).count()
        neutral = feedbacks.filter(rating=0).count()

        # Calculate effectiveness score (-1 to 1)
        score = (helpful - not_helpful) / total if total > 0 else 0.0

        # Analyze recent trend (last 30 days vs previous 30 days)
        trend = self._calculate_trend(feedbacks)

        # Extract successful contexts
        successful_contexts = self._extract_successful_patterns(
            feedbacks.filter(rating=1)
        )

        # Extract areas for improvement
        improvement_areas = self._extract_improvement_areas(
            feedbacks.filter(rating=-1)
        )

        result = AgentEffectiveness(
            agent_id=str(agent.id),
            agent_name=agent.name,
            total_feedbacks=total,
            helpful_count=helpful,
            not_helpful_count=not_helpful,
            neutral_count=neutral,
            effectiveness_score=round(score, 2),
            recent_trend=trend,
            top_successful_contexts=successful_contexts,
            areas_for_improvement=improvement_areas,
        )

        # Cache result
        self._cache[cache_key] = (result, timezone.now())

        return result

    def _calculate_trend(self, feedbacks) -> str:
        """Calculate recent trend from feedbacks."""
        now = timezone.now()
        recent_cutoff = now - timedelta(days=30)
        older_cutoff = now - timedelta(days=60)

        recent = feedbacks.filter(created_at__gte=recent_cutoff)
        older = feedbacks.filter(
            created_at__gte=older_cutoff,
            created_at__lt=recent_cutoff
        )

        recent_score = self._calculate_score(recent)
        older_score = self._calculate_score(older)

        if recent_score > older_score + 0.1:
            return 'improving'
        elif recent_score < older_score - 0.1:
            return 'declining'
        return 'stable'

    def _calculate_score(self, feedbacks) -> float:
        """Calculate effectiveness score from a queryset."""
        total = feedbacks.count()
        if total == 0:
            return 0.0

        helpful = feedbacks.filter(rating=1).count()
        not_helpful = feedbacks.filter(rating=-1).count()

        return (helpful - not_helpful) / total

    def _extract_successful_patterns(self, successful_feedbacks) -> List[str]:
        """Extract patterns from successful interactions."""
        patterns = []

        for feedback in successful_feedbacks[:20]:
            context = feedback.context_snapshot
            if not context:
                continue

            # Extract key context elements
            if context.get('goals'):
                patterns.append(f"goal-aligned: {str(context['goals'])[:50]}")
            if feedback.task_description:
                patterns.append(f"task: {feedback.task_description[:50]}")

        return list(set(patterns))[:5]

    def _extract_improvement_areas(self, negative_feedbacks) -> List[str]:
        """Extract areas for improvement from negative feedback."""
        areas = []

        for feedback in negative_feedbacks[:20]:
            if feedback.feedback_text:
                text = feedback.feedback_text.lower()
                if 'too long' in text or 'verbose' in text:
                    areas.append('response_length')
                if 'irrelevant' in text or 'off topic' in text:
                    areas.append('relevance')
                if 'technical' in text or 'complex' in text:
                    areas.append('complexity')
                if 'incomplete' in text or 'missing' in text:
                    areas.append('completeness')

        return list(set(areas))

    def adjust_context_for_agent(
        self,
        user,
        agent,
        base_context: Dict,
    ) -> Dict:
        """
        Adjust context based on what has worked for this user+agent.

        Examines past successful interactions and modifies context
        to increase likelihood of helpful output.
        """
        effectiveness = self.get_agent_effectiveness(user, agent)

        adjusted_context = base_context.copy()

        # Add learning metadata
        adjusted_context['_agent_learning'] = {
            'effectiveness_score': effectiveness.effectiveness_score,
            'total_feedbacks': effectiveness.total_feedbacks,
            'trend': effectiveness.recent_trend,
        }

        # If we have enough data and patterns
        if effectiveness.total_feedbacks >= 5:
            if effectiveness.top_successful_contexts:
                adjusted_context['_successful_patterns'] = effectiveness.top_successful_contexts[:3]

            if effectiveness.effectiveness_score < 0 and effectiveness.areas_for_improvement:
                adjusted_context['_improvement_hints'] = effectiveness.areas_for_improvement[:3]

        return adjusted_context

    def get_user_agent_summary(self, user) -> Dict[str, Any]:
        """
        Get summary of all agent effectiveness for a user.
        """
        from core.models_user_learning import AgentFeedback
        from core.models import Agent

        # Get all agents user has interacted with
        agent_ids = AgentFeedback.objects.filter(user=user).values_list(
            'agent_id', flat=True
        ).distinct()

        agents = Agent.objects.filter(id__in=agent_ids)

        summaries = []
        for agent in agents:
            effectiveness = self.get_agent_effectiveness(user, agent)
            summaries.append({
                'agent_id': effectiveness.agent_id,
                'agent_name': effectiveness.agent_name,
                'score': effectiveness.effectiveness_score,
                'feedbacks': effectiveness.total_feedbacks,
                'trend': effectiveness.recent_trend,
            })

        summaries.sort(key=lambda x: x['score'], reverse=True)

        return {
            'total_agents_used': len(summaries),
            'total_feedbacks': sum(s['feedbacks'] for s in summaries),
            'top_agents': summaries[:5],
            'needs_improvement': [s for s in summaries if s['score'] < 0][:5],
            'trending_up': [s for s in summaries if s['trend'] == 'improving'],
        }


# Singleton instance
_agent_feedback_service = None


def get_agent_feedback_service() -> AgentFeedbackService:
    """Get singleton instance of AgentFeedbackService."""
    global _agent_feedback_service
    if _agent_feedback_service is None:
        _agent_feedback_service = AgentFeedbackService()
    return _agent_feedback_service
