"""
Advisor Feedback Learning Bridge
Tracks advisor consultation effectiveness and optimizes advisor selection

Session 1115 batch-12: both `AdvisorFeedbackLearningLoop` and
`AutoConsultationLearningLoop` now inherit from `LearningBridge` ABC.
Public entry methods (`process_feedback`, `track_auto_consultation`)
kept as back-compat shims.
"""

import logging
from typing import Any, Dict, List

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.learning_bridges.base import LearningBridge
from core.models_unified_system import UserAgentLearning

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


class AdvisorFeedbackLearningLoop(LearningBridge):
    """
    Learns from advisor consultation outcomes to improve advisor selection.

    ABC contract mapping:
      - `process_event(feedback)` wraps `process_feedback`.
      - `_extract_patterns(feedback)` pulls advisor name, follow/success
        flags, and category, threading the AdvisorConsultationFeedback
        through as `_feedback`.
      - `_update_learning(patterns)` calls both
        `_update_advisor_effectiveness` and
        `_update_category_effectiveness` (when category is present).
      - `_generate_insights(patterns)` derives human-readable strings.
    """

    def __init__(self):
        super().__init__(bridge_name='advisor_feedback')

    # ------------------------------------------------------------------
    # ABC contract
    # ------------------------------------------------------------------
    def process_event(self, event_data: Any) -> Dict:
        """Process an AdvisorConsultationFeedback end-to-end."""
        feedback: AdvisorConsultationFeedback = event_data
        advisor_name = feedback.advisor_insight.advisor.name
        self.log_event(f"Processing advisor feedback for {advisor_name}")
        try:
            patterns = self._extract_patterns(feedback)
            self._update_learning(patterns)
            insights = self._generate_insights(patterns)
            self.log_success(f"Advisor feedback learning complete for {advisor_name}")
            return {
                'status': 'ok',
                'advisor_name': advisor_name,
                'was_followed': patterns['was_followed'],
                'was_successful': patterns['was_successful'],
                'insights': insights,
            }
        except Exception as e:
            self.log_error(f"Error in advisor feedback learning: {e}")
            return {'status': 'error', 'error': str(e)}

    def _extract_patterns(self, event_data: Any) -> Dict:
        """Extract advisor + outcome metadata from feedback row."""
        feedback: AdvisorConsultationFeedback = event_data
        category = (
            feedback.advisor_insight.category
            if hasattr(feedback.advisor_insight, 'category')
            else None
        )
        return {
            'advisor_name': feedback.advisor_insight.advisor.name,
            'was_followed': feedback.followed_advice,
            'was_successful': feedback.outcome_success,
            'satisfaction_rating': feedback.satisfaction_rating,
            'category': category,
            '_feedback': feedback,
        }

    def _update_learning(self, patterns: Dict) -> None:
        """Update advisor + category effectiveness rows."""
        feedback: AdvisorConsultationFeedback = patterns['_feedback']
        self._update_advisor_effectiveness(
            feedback, patterns['advisor_name'],
            patterns['was_followed'], patterns['was_successful'],
        )
        if patterns.get('category') is not None:
            self._update_category_effectiveness(
                feedback, patterns['advisor_name'],
                patterns['was_followed'], patterns['was_successful'],
            )

    def _generate_insights(self, patterns: Dict) -> List[str]:
        """Derive human-readable insight strings."""
        insights: List[str] = []
        advisor = patterns['advisor_name']
        followed = 'followed' if patterns['was_followed'] else 'ignored'
        insights.append(f"User {followed} advice from {advisor}")
        if patterns['was_followed'] and patterns['was_successful'] is not None:
            outcome = 'success' if patterns['was_successful'] else 'failure'
            insights.append(f"outcome: {outcome}")
        if patterns.get('satisfaction_rating'):
            insights.append(f"satisfaction: {patterns['satisfaction_rating']}/10")
        if patterns.get('category'):
            insights.append(f"category: {patterns['category']}")
        return insights

    # ------------------------------------------------------------------
    # Back-compat alias used by `on_advisor_feedback_created` signal handler
    # ------------------------------------------------------------------
    def process_feedback(self, feedback: AdvisorConsultationFeedback) -> Dict:
        """Back-compat shim — delegates to `process_event`."""
        return self.process_event(feedback)

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


class AutoConsultationLearningLoop(LearningBridge):
    """
    Session 461: Learns from automatic advisor consultations in audit coordinators.

    When StockAuditCoordinator or BlockchainAuditCoordinator auto-consult advisors
    for high-risk findings, we track:
    1. What alerts triggered the consultation
    2. The advisor's response/recommendation
    3. Whether the predicted risk materialized (outcome tracking)

    This enables the system to learn which advisors are most accurate for which
    types of alerts and to improve advisor selection over time.

    ABC contract mapping:
      - `process_event(consultation)` wraps `track_auto_consultation`
        — `event_data` is a Dict (not a Django row) since auto-consultations
        come from in-process audit coordinators, not signal handlers.
        Optional `user` is passed via `event_data['_user']` if needed.
      - `_extract_patterns(consultation)` normalizes the dict shape.
      - `_update_learning(patterns)` writes the UserAgentLearning row.
      - `_generate_insights(patterns)` derives summary strings.

    `record_outcome` and `get_advisor_accuracy_stats` are kept as
    separate public methods (different lifecycle than event processing).
    """

    def __init__(self):
        super().__init__(bridge_name='auto_consultation')

    # ------------------------------------------------------------------
    # ABC contract
    # ------------------------------------------------------------------
    def process_event(self, event_data: Any) -> Dict:
        """Process a consultation dict end-to-end.

        Expected shape: see docstring of `track_auto_consultation`.
        Optional `_user` key for non-system-user attribution.
        """
        consultation: Dict = event_data or {}
        user = consultation.get('_user')
        advisor_name = consultation.get('advisor', 'Unknown')
        self.log_event(f"Tracking auto-consultation: {advisor_name}")
        try:
            patterns = self._extract_patterns(consultation)
            patterns['_user'] = user
            success = self._update_learning_with_status(patterns)
            insights = self._generate_insights(patterns)
            if success:
                self.log_success(f"Auto-consultation tracked: {advisor_name}")
                return {
                    'status': 'ok',
                    'advisor_name': advisor_name,
                    'ticker': patterns['ticker'],
                    'severity': patterns['severity'],
                    'insights': insights,
                }
            return {'status': 'failed', 'reason': 'no_user'}
        except Exception as e:
            self.log_error(f"Error tracking auto-consultation: {e}")
            return {'status': 'error', 'error': str(e)}

    def _extract_patterns(self, event_data: Any) -> Dict:
        """Normalize the consultation dict shape."""
        consultation: Dict = event_data or {}
        return {
            'advisor_name': consultation.get('advisor', 'Unknown'),
            'ticker': (
                consultation.get('ticker') or consultation.get('token', 'UNKNOWN')
            ),
            'severity': consultation.get('severity', 'UNKNOWN'),
            'alert_type': consultation.get('alert_type', 'general'),
            'response': consultation.get('response', ''),
            'confidence': consultation.get('confidence', 0.7),
        }

    def _update_learning(self, patterns: Dict) -> None:
        """ABC-contract entry — delegates to the typed variant."""
        self._update_learning_with_status(patterns)

    def _update_learning_with_status(self, patterns: Dict) -> bool:
        """Write the auto-consultation row. Returns True on success."""
        user = patterns.get('_user')
        if user is None:
            user = self._get_system_user()
            if user is None:
                logger.warning("Could not get system user for tracking")
                return False

        from django.utils import timezone
        advisor_name = patterns['advisor_name']
        ticker = patterns['ticker']
        severity = patterns['severity']
        alert_type = patterns['alert_type']

        learning, _ = UserAgentLearning.objects.get_or_create(
            user=user,
            agent_name=advisor_name.replace(' (AI)', ''),
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
                'learning_source': 'auto_consultation',
            },
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
        content['total_consultations'] = content.get('total_consultations', 0) + 1

        if 'by_alert_type' not in content:
            content['by_alert_type'] = {}
        content['by_alert_type'][alert_type] = content['by_alert_type'].get(alert_type, 0) + 1

        if 'by_severity' not in content:
            content['by_severity'] = {}
        content['by_severity'][severity] = content['by_severity'].get(severity, 0) + 1

        if 'recent_consultations' not in content:
            content['recent_consultations'] = []
        content['recent_consultations'].append({
            'ticker': ticker,
            'severity': severity,
            'alert_type': alert_type,
            'response_summary': patterns['response'][:200] if patterns['response'] else '',
            'confidence': patterns['confidence'],
            'timestamp': timezone.now().isoformat(),
            'outcome': None,
        })
        content['recent_consultations'] = content['recent_consultations'][-100:]

        learning.learning_content = content
        learning.save()
        return True

    def _generate_insights(self, patterns: Dict) -> List[str]:
        """Derive insight strings."""
        insights = [
            f"{patterns['advisor_name']} consulted on "
            f"{patterns['ticker']} ({patterns['severity']})"
        ]
        if patterns['alert_type'] != 'general':
            insights.append(f"alert_type: {patterns['alert_type']}")
        if patterns['confidence']:
            insights.append(f"confidence: {patterns['confidence']:.2f}")
        return insights

    # ------------------------------------------------------------------
    # Bridge-specific helpers (preserved from pre-refactor implementation)
    # ------------------------------------------------------------------
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
        """Back-compat shim — delegates to `process_event`.

        Returns True if the consultation was tracked successfully (matches
        the original boolean return signature). Callers in audit
        coordinators (e.g. `track_audit_advisor_consultation`) keep working
        unchanged.
        """
        event_data = dict(consultation) if consultation else {}
        if user is not None:
            event_data['_user'] = user
        result = self.process_event(event_data)
        return result.get('status') == 'ok'

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
