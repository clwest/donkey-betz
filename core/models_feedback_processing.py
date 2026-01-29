"""
Session 861: Feedback Processing System

Addresses the LOW-MEDIUM RISK data persistence gap where user feedback
on agent outputs was recorded but not processed to improve agents.

This module provides:
1. Signal handlers that process feedback when created
2. Connection between feedback and agent learning
3. Positive reinforcement for good outputs
4. Learning triggers for negative feedback

The key problem was:
- HumanFeedbackRecord was stored but not processed
- Thumbs down didn't trigger improvements
- Good outputs didn't reinforce patterns

Now when feedback is recorded:
- Positive feedback (4-5 stars) reinforces the agent's approach
- Negative feedback (1-2 stars) creates learning records for improvement
- Mixed feedback (3 stars) is noted but not acted on
"""

import logging
from typing import Dict, Any, Optional
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger(__name__)


class FeedbackProcessor:
    """
    Process user feedback to improve agent behavior.

    This singleton class handles feedback processing and connects
    to the learning system to improve agent outputs based on
    user preferences.
    """

    # Rating thresholds
    POSITIVE_THRESHOLD = 4  # 4-5 stars = positive
    NEGATIVE_THRESHOLD = 2  # 1-2 stars = negative

    def __init__(self):
        self._agent_learning_model = None
        self._learning_insight_model = None
        self._agent_memory_model = None

    @property
    def AgentLearning(self):
        """Lazy-load AgentLearning model."""
        if self._agent_learning_model is None:
            try:
                from core.models_unified_system import AgentLearning
                self._agent_learning_model = AgentLearning
            except ImportError:
                pass
        return self._agent_learning_model

    @property
    def LearningInsight(self):
        """Lazy-load LearningInsight model."""
        if self._learning_insight_model is None:
            try:
                from core.models import LearningInsight
                self._learning_insight_model = LearningInsight
            except ImportError:
                pass
        return self._learning_insight_model

    @property
    def AgentMemory(self):
        """Lazy-load AgentMemory model."""
        if self._agent_memory_model is None:
            try:
                from core.models_agent_memory import AgentMemory
                self._agent_memory_model = AgentMemory
            except ImportError:
                pass
        return self._agent_memory_model

    def process_pipeline_feedback(
        self,
        stage: str,
        rating: float,
        agent_name: str = None,
        context: Dict[str, Any] = None,
        feedback_text: str = '',
    ) -> bool:
        """
        Process feedback from PipelineStageFeedback.

        Args:
            stage: Pipeline stage (research, script, image, voice, video)
            rating: Rating value (1.0 - 5.0)
            agent_name: Name of the agent that produced the output
            context: Additional context from the feedback
            feedback_text: Optional user text feedback

        Returns:
            True if feedback was processed successfully
        """
        try:
            rating_int = int(round(rating))
            agent_name = agent_name or f"{stage.title()}Agent"

            if rating >= self.POSITIVE_THRESHOLD:
                return self._reinforce_positive(agent_name, stage, context, feedback_text)
            elif rating <= self.NEGATIVE_THRESHOLD:
                return self._learn_from_negative(agent_name, stage, context, feedback_text)
            else:
                # Neutral (3 stars) - log but don't act
                logger.debug(f"📊 Session 861: Neutral feedback for {agent_name}: {rating}")
                return True

        except Exception as e:
            logger.error(f"📊 Session 861: Failed to process pipeline feedback: {e}")
            return False

    def process_human_feedback(
        self,
        attention_item_id: str,
        decision: str,
        feedback_text: str = '',
        ml_prediction: Dict[str, Any] = None,
        human_agreed_with_ml: bool = None,
    ) -> bool:
        """
        Process feedback from HumanFeedbackRecord.

        This handles the human-in-the-loop decisions where a human
        reviewed and approved/rejected agent output.

        Args:
            attention_item_id: ID of the HumanAttentionItem
            decision: The human's decision (approve, reject, etc.)
            feedback_text: Optional explanation
            ml_prediction: What the ML model predicted
            human_agreed_with_ml: Whether human agreed with ML

        Returns:
            True if feedback was processed successfully
        """
        try:
            from core.models_human_interface import HumanAttentionItem

            item = HumanAttentionItem.objects.filter(id=attention_item_id).first()
            if not item:
                return False

            agent_name = item.source_agent or 'UnknownAgent'

            # Determine if positive or negative based on decision
            is_positive = decision in ['approve', 'approved', 'accept', 'publish', 'completed']
            is_negative = decision in ['reject', 'rejected', 'decline', 'failed', 'needs_work']

            if is_positive:
                context = {
                    'item_type': item.item_type,
                    'priority': item.priority,
                    'ml_prediction': ml_prediction,
                }
                return self._reinforce_positive(agent_name, 'human_review', context, feedback_text)
            elif is_negative:
                context = {
                    'item_type': item.item_type,
                    'priority': item.priority,
                    'ml_prediction': ml_prediction,
                    'human_correction': decision,
                }
                return self._learn_from_negative(agent_name, 'human_review', context, feedback_text)
            else:
                logger.debug(f"📊 Session 861: Neutral human decision: {decision}")
                return True

        except Exception as e:
            logger.error(f"📊 Session 861: Failed to process human feedback: {e}")
            return False

    def process_execution_feedback(
        self,
        agent_name: str,
        user_rating: int,
        task_type: str = '',
        feedback_text: str = '',
        execution_context: Dict[str, Any] = None,
    ) -> bool:
        """
        Process feedback from AgentExecutionMemory.

        Args:
            agent_name: Name of the agent
            user_rating: 1-5 star rating
            task_type: Type of task executed
            feedback_text: Optional user feedback
            execution_context: Context from execution

        Returns:
            True if feedback was processed successfully
        """
        try:
            if user_rating >= self.POSITIVE_THRESHOLD:
                return self._reinforce_positive(agent_name, task_type, execution_context, feedback_text)
            elif user_rating <= self.NEGATIVE_THRESHOLD:
                return self._learn_from_negative(agent_name, task_type, execution_context, feedback_text)
            else:
                logger.debug(f"📊 Session 861: Neutral rating for {agent_name}: {user_rating}")
                return True

        except Exception as e:
            logger.error(f"📊 Session 861: Failed to process execution feedback: {e}")
            return False

    def _reinforce_positive(
        self,
        agent_name: str,
        task_context: str,
        context: Dict[str, Any],
        feedback_text: str,
    ) -> bool:
        """
        Reinforce positive feedback by recording what worked.

        This creates a learning record that captures the successful
        approach so it can be replicated.
        """
        try:
            if self.AgentLearning:
                # Record positive learning
                from core.models_unified_system import Agent, AgentLearning

                agent = Agent.objects.filter(name__iexact=agent_name).first()
                if not agent:
                    # Try partial match
                    agent = Agent.objects.filter(name__icontains=agent_name.replace('Agent', '')).first()

                if agent:
                    AgentLearning.objects.create(
                        agent=agent,
                        learning_type='positive_feedback',
                        content=f"User provided positive feedback for {task_context}: {feedback_text or 'Good output'}",
                        source='user_feedback',
                        confidence_score=0.8,
                        metadata={
                            'task_context': task_context,
                            'context': context or {},
                            'feedback_text': feedback_text,
                            'processed_at': timezone.now().isoformat(),
                        }
                    )
                    logger.info(f"📊 Session 861: Reinforced positive pattern for {agent_name}")

            # Also create learning insight if available
            if self.LearningInsight:
                self.LearningInsight.objects.create(
                    insight_type='positive_reinforcement',
                    description=f"User positively rated {agent_name} output for {task_context}",
                    agent_name=agent_name,
                    confidence_score=0.8,
                    metadata={
                        'task_context': task_context,
                        'feedback_text': feedback_text,
                    }
                )

            return True

        except Exception as e:
            logger.error(f"📊 Session 861: Failed to reinforce positive feedback: {e}")
            return False

    def _learn_from_negative(
        self,
        agent_name: str,
        task_context: str,
        context: Dict[str, Any],
        feedback_text: str,
    ) -> bool:
        """
        Learn from negative feedback by recording what didn't work.

        This creates a learning record that captures the failed
        approach so it can be avoided or improved.
        """
        try:
            if self.AgentLearning:
                from core.models_unified_system import Agent, AgentLearning

                agent = Agent.objects.filter(name__iexact=agent_name).first()
                if not agent:
                    agent = Agent.objects.filter(name__icontains=agent_name.replace('Agent', '')).first()

                if agent:
                    AgentLearning.objects.create(
                        agent=agent,
                        learning_type='negative_feedback',
                        content=f"User flagged issue with {task_context}: {feedback_text or 'Output needs improvement'}",
                        source='user_feedback',
                        confidence_score=0.9,  # Higher confidence for negative feedback
                        metadata={
                            'task_context': task_context,
                            'context': context or {},
                            'feedback_text': feedback_text,
                            'processed_at': timezone.now().isoformat(),
                            'action_needed': True,
                        }
                    )
                    logger.info(f"📊 Session 861: Created learning record for {agent_name} negative feedback")

            # Also create learning insight for tracking
            if self.LearningInsight:
                self.LearningInsight.objects.create(
                    insight_type='improvement_needed',
                    description=f"User flagged {agent_name} output as needing improvement for {task_context}",
                    agent_name=agent_name,
                    confidence_score=0.9,
                    metadata={
                        'task_context': task_context,
                        'feedback_text': feedback_text,
                        'requires_attention': True,
                    }
                )

            return True

        except Exception as e:
            logger.error(f"📊 Session 861: Failed to learn from negative feedback: {e}")
            return False


# Singleton instance
_feedback_processor: Optional[FeedbackProcessor] = None


def get_feedback_processor() -> FeedbackProcessor:
    """Get the singleton FeedbackProcessor instance."""
    global _feedback_processor
    if _feedback_processor is None:
        _feedback_processor = FeedbackProcessor()
    return _feedback_processor


# =============================================================================
# SIGNAL HANDLERS
# =============================================================================

@receiver(post_save, sender='core.PipelineStageFeedback')
def process_pipeline_feedback_signal(sender, instance, created, **kwargs):
    """
    Session 861: Automatically process pipeline stage feedback.

    Triggered when PipelineStageFeedback is saved.
    """
    if not created:
        return  # Only process new feedback

    try:
        processor = get_feedback_processor()
        processor.process_pipeline_feedback(
            stage=instance.stage,
            rating=float(instance.rating),
            agent_name=instance.input_params.get('agent_name') if instance.input_params else None,
            context=instance.input_params,
            feedback_text=str(instance.feedback_text) if hasattr(instance, 'feedback_text') else '',
        )
    except Exception as e:
        logger.error(f"📊 Session 861: Pipeline feedback signal failed: {e}")


@receiver(post_save, sender='core.HumanFeedbackRecord')
def process_human_feedback_signal(sender, instance, created, **kwargs):
    """
    Session 861: Automatically process human feedback.

    Triggered when HumanFeedbackRecord is saved.
    """
    if not created:
        return  # Only process new feedback

    try:
        processor = get_feedback_processor()
        processor.process_human_feedback(
            attention_item_id=str(instance.attention_item_id),
            decision=instance.decision,
            feedback_text=instance.feedback_text or '',
            ml_prediction=instance.ml_prediction,
            human_agreed_with_ml=instance.human_agreed_with_ml,
        )
    except Exception as e:
        logger.error(f"📊 Session 861: Human feedback signal failed: {e}")


@receiver(post_save, sender='core.AgentExecutionMemory')
def process_execution_memory_signal(sender, instance, created, **kwargs):
    """
    Session 861: Automatically process execution memory feedback.

    Triggered when AgentExecutionMemory is saved with a user rating.
    """
    # Only process if user_rating was just set
    if not instance.user_rating:
        return

    try:
        processor = get_feedback_processor()
        processor.process_execution_feedback(
            agent_name=instance.agent_name,
            user_rating=instance.user_rating,
            task_type=instance.task_type,
            feedback_text=getattr(instance, 'user_feedback', ''),
            execution_context={
                'task_summary': instance.task_summary,
                'success_score': instance.success_score,
            }
        )
    except Exception as e:
        logger.error(f"📊 Session 861: Execution memory feedback signal failed: {e}")


# Connect signals at module load time
def connect_feedback_signals():
    """
    Connect feedback processing signals.

    Call this from apps.py ready() method to ensure signals are connected.
    """
    # Signals are connected via decorators above
    logger.info("📊 Session 861: Feedback processing signals connected")


# Auto-connect on import (signals are already connected via decorators)
logger.info("📊 Session 861: Feedback processing module loaded")
