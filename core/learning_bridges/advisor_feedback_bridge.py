"""
Advisor Feedback Learning Bridge
Tracks advisor consultation effectiveness and optimizes advisor selection
"""

import logging
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import Dict

from core.models_unified_system import AdvisorInsight, UserAgentLearning

logger = logging.getLogger(__name__)


class AdvisorConsultationFeedback(models.Model):
    """
    Tracks feedback on advisor consultations
    Enables learning which advisors provide most valuable insights
    """
    advisor_insight = models.ForeignKey('core.AdvisorInsight', on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    # Feedback metrics
    followed_advice = models.BooleanField(default=False)
    outcome_success = models.BooleanField(null=True)  # Did following advice lead to success?
    satisfaction_rating = models.IntegerField(default=0)  # 0-10 scale
    time_to_outcome = models.IntegerField(null=True)  # Hours until outcome

    # Metadata
    feedback_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    outcome_measured_at = models.DateTimeField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['advisor_insight', 'outcome_success']),
        ]


class AdvisorFeedbackLearningLoop:
    """
    Learns from advisor consultation outcomes to improve advisor selection
    """

    def process_feedback(self, feedback: AdvisorConsultationFeedback):
        """Process advisor consultation feedback"""

        logger.info(f"💡 Processing advisor feedback for {feedback.advisor_insight.advisor.name}")

        try:
            advisor_name = feedback.advisor_insight.advisor.name
            was_followed = feedback.followed_advice
            was_successful = feedback.outcome_success

            # Update advisor effectiveness learning
            self._update_advisor_effectiveness(feedback, advisor_name, was_followed, was_successful)

            # Update category-specific effectiveness
            if hasattr(feedback.advisor_insight, 'category'):
                self._update_category_effectiveness(feedback, advisor_name, was_followed, was_successful)

            logger.info(f"✅ Advisor feedback learning complete")

        except Exception as e:
            logger.error(f"Error in advisor feedback learning: {e}", exc_info=True)

    def _update_advisor_effectiveness(self, feedback: AdvisorConsultationFeedback,
                                     advisor_name: str, was_followed: bool, was_successful: bool):
        """Update advisor's overall effectiveness scores"""

        learning, _ = UserAgentLearning.objects.get_or_create(
            user=feedback.user,
            agent_name=advisor_name,
            learning_domain='advisor_effectiveness',
            defaults={
                'learning_content': {
                    'total_consultations': 0,
                    'advice_followed': 0,
                    'successful_outcomes': 0,
                    'average_satisfaction': 0,
                    'satisfaction_ratings': []
                },
                'confidence_score': 0.5,
                'learning_source': 'user_feedback'
            }
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
        content['total_consultations'] = content.get('total_consultations', 0) + 1

        if was_followed:
            content['advice_followed'] = content.get('advice_followed', 0) + 1

            if was_successful is not None:
                if was_successful:
                    content['successful_outcomes'] = content.get('successful_outcomes', 0) + 1
                    learning.record_success()
                else:
                    learning.record_failure()

        # Track satisfaction ratings
        if 'satisfaction_ratings' not in content:
            content['satisfaction_ratings'] = []
        content['satisfaction_ratings'].append(feedback.satisfaction_rating)

        # Calculate average satisfaction
        if content['satisfaction_ratings']:
            content['average_satisfaction'] = sum(content['satisfaction_ratings']) / len(content['satisfaction_ratings'])

        # Calculate advice follow rate
        if content['total_consultations'] > 0:
            content['advice_follow_rate'] = content.get('advice_followed', 0) / content['total_consultations']

        # Calculate success rate (when advice is followed)
        if content.get('advice_followed', 0) > 0:
            content['success_rate'] = content.get('successful_outcomes', 0) / content['advice_followed']

        learning.learning_content = content
        learning.save()

        logger.info(f"✅ Updated advisor effectiveness learning for {advisor_name}")

    def _update_category_effectiveness(self, feedback: AdvisorConsultationFeedback,
                                      advisor_name: str, was_followed: bool, was_successful: bool):
        """Update advisor effectiveness for specific consultation categories"""

        category = feedback.advisor_insight.category if hasattr(feedback.advisor_insight, 'category') else 'general'

        learning, _ = UserAgentLearning.objects.get_or_create(
            user=feedback.user,
            agent_name=advisor_name,
            learning_domain=f'advisor_category_{category}',
            defaults={
                'learning_content': {
                    'consultations': 0,
                    'successes': 0
                },
                'confidence_score': 0.5,
                'learning_source': 'success_pattern'
            }
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
        content['consultations'] = content.get('consultations', 0) + 1

        if was_followed and was_successful:
            content['successes'] = content.get('successes', 0) + 1
            learning.record_success()
        elif was_followed and was_successful is False:
            learning.record_failure()

        # Calculate success rate for this category
        if content['consultations'] > 0:
            content['success_rate'] = content.get('successes', 0) / content['consultations']

        learning.learning_content = content
        learning.save()


# Signal integration
advisor_feedback_learning = AdvisorFeedbackLearningLoop()


@receiver(post_save, sender=AdvisorConsultationFeedback)
def on_advisor_feedback_created(sender, instance, created, **kwargs):
    """Learn from advisor consultation feedback"""
    try:
        advisor_feedback_learning.process_feedback(instance)
    except Exception as e:
        logger.error(f"Error in advisor feedback learning signal: {e}", exc_info=True)
