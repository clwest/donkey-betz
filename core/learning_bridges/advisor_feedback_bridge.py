"""
Advisor Feedback Learning Bridge
Tracks advisor consultation effectiveness and optimizes advisor selection
"""

import logging
from django.db import models
from django.conf import settings
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

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


class AutoConsultationLearningLoop:
    """
    Session 461: Learns from automatic advisor consultations in audit coordinators.

    When StockAuditCoordinator or BlockchainAuditCoordinator auto-consult advisors
    for high-risk findings, we track:
    1. What alerts triggered the consultation
    2. The advisor's response/recommendation
    3. Whether the predicted risk materialized (outcome tracking)

    This enables the system to learn which advisors are most accurate for which
    types of alerts and to improve advisor selection over time.
    """

    def _get_system_user(self):
        """Get or create a system user for anonymous tracking."""
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()

            system_user, _ = User.objects.get_or_create(
                username='system_advisor_tracker',
                defaults={
                    'email': 'system@advisor-tracker.local',
                    'is_active': False,  # Can't log in
                }
            )
            return system_user
        except Exception as e:
            logger.warning(f"Could not get system user: {e}")
            return None

    def track_auto_consultation(self, consultation: Dict, user=None) -> bool:
        """
        Track an automatic advisor consultation from audit coordinators.

        Args:
            consultation: Dict with keys:
                - advisor: Advisor name (e.g., 'Warren Buffett (AI)')
                - ticker/token: Symbol being analyzed
                - severity: Alert severity (CRITICAL, HIGH, etc.)
                - alert_type: Type of alert (stock_audit, blockchain_security)
                - response: Advisor's response text
                - confidence: Advisor's confidence score
                - timestamp: When consultation occurred

        Returns:
            True if successfully tracked
        """
        try:
            advisor_name = consultation.get('advisor', 'Unknown')
            ticker = consultation.get('ticker') or consultation.get('token', 'UNKNOWN')
            severity = consultation.get('severity', 'UNKNOWN')
            alert_type = consultation.get('alert_type', 'general')
            response = consultation.get('response', '')
            confidence = consultation.get('confidence', 0.7)

            # Use system user if no user provided (for auto-consultations)
            if user is None:
                user = self._get_system_user()
                if user is None:
                    logger.warning("Could not get system user for tracking")
                    return False

            logger.info(f"📊 Tracking auto-consultation: {advisor_name} on {ticker} ({severity})")

            # Get or create learning record for this advisor's auto-consultations
            learning, _ = UserAgentLearning.objects.get_or_create(
                user=user,
                agent_name=advisor_name.replace(' (AI)', ''),  # Clean advisor name
                learning_domain='auto_consultation_accuracy',
                defaults={
                    'learning_content': {
                        'total_consultations': 0,
                        'by_alert_type': {},
                        'by_severity': {},
                        'outcomes_tracked': 0,
                        'correct_predictions': 0,
                        'recent_consultations': [],
                    },
                    'confidence_score': 0.5,
                    'learning_source': 'auto_consultation'
                }
            )

            content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
            content['total_consultations'] = content.get('total_consultations', 0) + 1

            # Track by alert type
            if 'by_alert_type' not in content:
                content['by_alert_type'] = {}
            if alert_type not in content['by_alert_type']:
                content['by_alert_type'][alert_type] = 0
            content['by_alert_type'][alert_type] += 1

            # Track by severity
            if 'by_severity' not in content:
                content['by_severity'] = {}
            if severity not in content['by_severity']:
                content['by_severity'][severity] = 0
            content['by_severity'][severity] += 1

            # Store recent consultation (for outcome tracking later)
            if 'recent_consultations' not in content:
                content['recent_consultations'] = []

            from django.utils import timezone
            content['recent_consultations'].append({
                'ticker': ticker,
                'severity': severity,
                'alert_type': alert_type,
                'response_summary': response[:200] if response else '',
                'confidence': confidence,
                'timestamp': timezone.now().isoformat(),
                'outcome': None,  # To be filled when outcome is known
            })

            # Keep only last 100 consultations
            content['recent_consultations'] = content['recent_consultations'][-100:]

            learning.learning_content = content
            learning.save()

            logger.info(f"✅ Auto-consultation tracked: {advisor_name} - consultation #{content['total_consultations']}")
            return True

        except Exception as e:
            logger.error(f"Error tracking auto-consultation: {e}", exc_info=True)
            return False

    def record_outcome(self, advisor_name: str, ticker: str, outcome: bool, user=None) -> bool:
        """
        Record the outcome of a previous consultation.

        Called when we later determine if the advisor's prediction was correct.
        For example, if Warren Buffett warned about a stock and it later dropped,
        that's a successful prediction.

        Args:
            advisor_name: Advisor name
            ticker: Symbol that was analyzed
            outcome: True if advisor's prediction was correct
            user: User associated with the consultation

        Returns:
            True if outcome successfully recorded
        """
        try:
            clean_name = advisor_name.replace(' (AI)', '')

            # Use system user if no user provided
            if user is None:
                user = self._get_system_user()

            learning = UserAgentLearning.objects.filter(
                user=user,
                agent_name=clean_name,
                learning_domain='auto_consultation_accuracy',
            ).first()

            if not learning:
                logger.warning(f"No learning record found for {clean_name}")
                return False

            content = learning.learning_content if isinstance(learning.learning_content, dict) else {}

            # Find matching consultation and update outcome
            recent = content.get('recent_consultations', [])
            for consultation in recent:
                if consultation.get('ticker') == ticker and consultation.get('outcome') is None:
                    consultation['outcome'] = outcome
                    content['outcomes_tracked'] = content.get('outcomes_tracked', 0) + 1

                    if outcome:
                        content['correct_predictions'] = content.get('correct_predictions', 0) + 1
                        learning.record_success()
                        logger.info(f"✅ {clean_name} correct about {ticker}")
                    else:
                        learning.record_failure()
                        logger.info(f"❌ {clean_name} incorrect about {ticker}")

                    # Calculate accuracy
                    if content['outcomes_tracked'] > 0:
                        content['accuracy'] = content['correct_predictions'] / content['outcomes_tracked']

                    break

            content['recent_consultations'] = recent
            learning.learning_content = content
            learning.save()

            return True

        except Exception as e:
            logger.error(f"Error recording outcome: {e}", exc_info=True)
            return False

    def get_advisor_accuracy_stats(self, advisor_name: str, user=None) -> Dict:
        """
        Get accuracy statistics for an advisor's auto-consultations.

        Returns:
            Dict with accuracy metrics
        """
        try:
            clean_name = advisor_name.replace(' (AI)', '')

            # Use system user if no user provided
            if user is None:
                user = self._get_system_user()

            learning = UserAgentLearning.objects.filter(
                user=user,
                agent_name=clean_name,
                learning_domain='auto_consultation_accuracy',
            ).first()

            if not learning:
                return {
                    'advisor': advisor_name,
                    'total_consultations': 0,
                    'outcomes_tracked': 0,
                    'accuracy': None,
                    'message': 'No consultation data yet'
                }

            content = learning.learning_content if isinstance(learning.learning_content, dict) else {}

            return {
                'advisor': advisor_name,
                'total_consultations': content.get('total_consultations', 0),
                'outcomes_tracked': content.get('outcomes_tracked', 0),
                'correct_predictions': content.get('correct_predictions', 0),
                'accuracy': content.get('accuracy'),
                'by_alert_type': content.get('by_alert_type', {}),
                'by_severity': content.get('by_severity', {}),
                'confidence_score': learning.confidence_score,
            }

        except Exception as e:
            logger.error(f"Error getting advisor stats: {e}")
            return {'advisor': advisor_name, 'error': str(e)}


# Session 461: Global instance for auto-consultation tracking
auto_consultation_learning = AutoConsultationLearningLoop()


def track_audit_advisor_consultation(consultation: Dict, user=None) -> bool:
    """
    Convenience function to track auto-consultations from audit coordinators.

    Usage:
        from core.learning_bridges.advisor_feedback_bridge import track_audit_advisor_consultation

        # In StockAuditCoordinator after getting advisor response:
        track_audit_advisor_consultation({
            'advisor': 'Warren Buffett (AI)',
            'ticker': 'AAPL',
            'severity': 'HIGH',
            'alert_type': 'stock_audit',
            'response': response_text,
            'confidence': 0.8,
        })
    """
    return auto_consultation_learning.track_auto_consultation(consultation, user)
