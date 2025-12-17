"""
Application Outcome Learning Bridge
Learns from application outcomes to improve future success rates

Session 461: Extended to also handle JobApplication model (detailed job tracking)
in addition to the generic Application model.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count, Avg
from typing import Dict, Any
from django.utils import timezone

from core.models_unified_system import Application, UserAgentLearning, Opportunity

logger = logging.getLogger(__name__)

# Success/failure status mappings for both Application and JobApplication models
SUCCESS_STATUSES = ['accepted', 'offer_received', 'offer_accepted']
FAILURE_STATUSES = ['rejected']


class ApplicationOutcomeLearningLoop:
    """
    Learns from application outcomes to optimize future applications

    Tracks:
    - Which applications get interviews/offers
    - What characteristics lead to success
    - Which agents/strategies are most effective
    - Platform-specific success patterns
    """

    def process_application_outcome(self, application: Application):
        """Process application status change"""

        logger.info(f"📝 Processing application outcome: {application.status}")

        # Only learn from final outcomes
        if application.status not in ['accepted', 'rejected']:
            return

        try:
            was_successful = application.status == 'accepted'

            # Extract success factors
            success_factors = self._extract_success_factors(application)

            # Update agent learning if agent assisted
            if hasattr(application, 'assisted_by') and application.assisted_by:
                self._update_agent_application_learning(application, was_successful, success_factors)

            # Update opportunity platform learning
            self._update_platform_success_patterns(application, was_successful)

            # Update user's application strategy learning
            self._update_user_application_patterns(application, was_successful, success_factors)

            logger.info(f"✅ Application outcome learning complete")

        except Exception as e:
            logger.error(f"Error in application outcome learning: {e}", exc_info=True)

    def _extract_success_factors(self, application: Application) -> Dict:
        """Extract what made this application successful/unsuccessful"""
        opportunity = application.opportunity

        factors = {
            'platform': opportunity.source if hasattr(opportunity, 'source') else 'unknown',
            'opportunity_type': opportunity.opportunity_type if hasattr(opportunity, 'opportunity_type') else 'unknown',
            'match_score': opportunity.match_score if hasattr(opportunity, 'match_score') else 0,
            'salary_range': float(opportunity.potential_revenue) if hasattr(opportunity, 'potential_revenue') else 0,
            'agent_used': application.assisted_by.name if hasattr(application, 'assisted_by') and application.assisted_by else 'None',
            'ai_confidence': application.ai_confidence if hasattr(application, 'ai_confidence') else 0,
            'cover_letter_length': len(application.cover_letter) if hasattr(application, 'cover_letter') and application.cover_letter else 0,
            'had_custom_cover_letter': hasattr(application, 'cover_letter') and application.cover_letter and len(application.cover_letter) > 0,
            'application_speed': self._calculate_application_speed(application)
        }

        return factors

    def _calculate_application_speed(self, application: Application) -> float:
        """Calculate how quickly user applied after seeing opportunity"""
        if hasattr(application, 'submitted_at') and application.submitted_at and hasattr(application, 'created_at') and application.created_at:
            delta = application.submitted_at - application.created_at
            return delta.total_seconds() / 3600  # hours
        return 0

    def _update_agent_application_learning(self, application: Application,
                                          was_successful: bool, success_factors: Dict):
        """Update agent's learning about application success"""

        learning, _ = UserAgentLearning.objects.get_or_create(
            user=application.user,
            agent_name=application.assisted_by.name,
            learning_domain='opportunity_matching',
            defaults={
                'learning_content': {
                    'applications_created': 0,
                    'applications_accepted': 0,
                    'applications_rejected': 0,
                    'success_factors': []
                },
                'confidence_score': 0.5,
                'learning_source': 'success_pattern'
            }
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
        content['applications_created'] = content.get('applications_created', 0) + 1

        if was_successful:
            content['applications_accepted'] = content.get('applications_accepted', 0) + 1
            if 'success_factors' not in content:
                content['success_factors'] = []
            content['success_factors'].append(success_factors)
            learning.record_success()
        else:
            content['applications_rejected'] = content.get('applications_rejected', 0) + 1
            learning.record_failure()

        # Calculate acceptance rate
        if content['applications_created'] > 0:
            content['acceptance_rate'] = content['applications_accepted'] / content['applications_created']

        learning.learning_content = content
        learning.save()

        logger.info(f"✅ Updated agent application learning for {application.assisted_by.name}")

    def _update_platform_success_patterns(self, application: Application, was_successful: bool):
        """Learn which platforms have highest success rates"""

        platform = application.opportunity.source if hasattr(application.opportunity, 'source') else 'unknown'

        learning, _ = UserAgentLearning.objects.get_or_create(
            user=application.user,
            agent_name='SystemIntelligence',
            learning_domain='platform_preferences',
            defaults={
                'learning_content': {'platforms': {}},
                'confidence_score': 0.5,
                'learning_source': 'success_pattern'
            }
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
        if 'platforms' not in content:
            content['platforms'] = {}

        if platform not in content['platforms']:
            content['platforms'][platform] = {'applied': 0, 'accepted': 0}

        content['platforms'][platform]['applied'] += 1
        if was_successful:
            content['platforms'][platform]['accepted'] += 1

        # Calculate success rate for this platform
        platform_data = content['platforms'][platform]
        platform_data['success_rate'] = platform_data['accepted'] / platform_data['applied']

        learning.learning_content = content

        # Adjust confidence based on success
        if was_successful:
            learning.record_success()
        else:
            learning.record_failure()

        learning.save()

    def _update_user_application_patterns(self, application: Application,
                                         was_successful: bool, success_factors: Dict):
        """Update user's application strategy patterns"""

        learning, _ = UserAgentLearning.objects.get_or_create(
            user=application.user,
            agent_name='SystemIntelligence',
            learning_domain='success_factors',
            defaults={
                'learning_content': {
                    'successful_patterns': [],
                    'unsuccessful_patterns': []
                },
                'confidence_score': 0.5,
                'learning_source': 'success_pattern'
            }
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}

        if was_successful:
            if 'successful_patterns' not in content:
                content['successful_patterns'] = []
            content['successful_patterns'].append(success_factors)
        else:
            if 'unsuccessful_patterns' not in content:
                content['unsuccessful_patterns'] = []
            content['unsuccessful_patterns'].append(success_factors)

        learning.learning_content = content
        learning.save()


# Signal integration
application_learning_loop = ApplicationOutcomeLearningLoop()


@receiver(post_save, sender=Application)
def on_application_status_changed(sender, instance, created, **kwargs):
    """Learn from application status changes"""
    if instance.status in ['accepted', 'rejected']:
        try:
            application_learning_loop.process_application_outcome(instance)
        except Exception as e:
            logger.error(f"Error in application learning loop signal: {e}", exc_info=True)


# Session 461: Signal integration for JobApplication model
try:
    from core.models import JobApplication

    @receiver(post_save, sender=JobApplication)
    def on_job_application_status_changed(sender, instance, created, **kwargs):
        """
        Learn from JobApplication status changes.

        Session 461: Extended to also learn from the detailed JobApplication model
        which tracks job applications with more granular status (offer_received,
        offer_accepted, phone_interview, etc.)
        """
        # Only learn from final outcomes
        is_success = instance.status in SUCCESS_STATUSES
        is_failure = instance.status in FAILURE_STATUSES

        if not (is_success or is_failure):
            return

        try:
            logger.info(f"📝 Processing JobApplication outcome: {instance.status}")

            # Extract factors from JobApplication
            factors = {
                'platform': instance.job_source if hasattr(instance, 'job_source') else 'unknown',
                'position': instance.position if hasattr(instance, 'position') else 'unknown',
                'company': instance.company if hasattr(instance, 'company') else 'unknown',
                'match_score': instance.match_score if hasattr(instance, 'match_score') else 0,
                'application_method': instance.application_method if hasattr(instance, 'application_method') else 'unknown',
                'resume_version': instance.resume_version if hasattr(instance, 'resume_version') else None,
                'response_time_days': instance.response_time_days if hasattr(instance, 'response_time_days') else None,
                'had_cover_letter': bool(instance.cover_letter_used) if hasattr(instance, 'cover_letter_used') else False,
            }

            # Update user's job application learning
            learning, _ = UserAgentLearning.objects.get_or_create(
                user=instance.user,
                agent_name='SystemIntelligence',
                learning_domain='job_application_outcomes',
                defaults={
                    'learning_content': {
                        'total_applications': 0,
                        'successful': 0,
                        'rejected': 0,
                        'success_factors': [],
                        'failure_factors': [],
                        'best_platforms': {},
                        'best_methods': {},
                    },
                    'confidence_score': 0.5,
                    'learning_source': 'job_application_tracking'
                }
            )

            content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
            content['total_applications'] = content.get('total_applications', 0) + 1

            if is_success:
                content['successful'] = content.get('successful', 0) + 1
                if 'success_factors' not in content:
                    content['success_factors'] = []
                content['success_factors'].append({
                    **factors,
                    'timestamp': timezone.now().isoformat()
                })
                # Keep last 50 success patterns
                content['success_factors'] = content['success_factors'][-50:]
                learning.record_success()
            else:
                content['rejected'] = content.get('rejected', 0) + 1
                if 'failure_factors' not in content:
                    content['failure_factors'] = []
                content['failure_factors'].append({
                    **factors,
                    'timestamp': timezone.now().isoformat()
                })
                # Keep last 50 failure patterns
                content['failure_factors'] = content['failure_factors'][-50:]
                learning.record_failure()

            # Update platform success tracking
            platform = factors['platform']
            if 'best_platforms' not in content:
                content['best_platforms'] = {}
            if platform not in content['best_platforms']:
                content['best_platforms'][platform] = {'applied': 0, 'successful': 0}
            content['best_platforms'][platform]['applied'] += 1
            if is_success:
                content['best_platforms'][platform]['successful'] += 1
            # Calculate success rate
            p = content['best_platforms'][platform]
            p['success_rate'] = p['successful'] / p['applied'] if p['applied'] > 0 else 0

            # Update method success tracking
            method = factors['application_method']
            if 'best_methods' not in content:
                content['best_methods'] = {}
            if method not in content['best_methods']:
                content['best_methods'][method] = {'applied': 0, 'successful': 0}
            content['best_methods'][method]['applied'] += 1
            if is_success:
                content['best_methods'][method]['successful'] += 1
            # Calculate success rate
            m = content['best_methods'][method]
            m['success_rate'] = m['successful'] / m['applied'] if m['applied'] > 0 else 0

            # Calculate overall success rate
            content['success_rate'] = content['successful'] / content['total_applications'] if content['total_applications'] > 0 else 0

            learning.learning_content = content
            learning.save()

            logger.info(f"✅ JobApplication outcome learning complete for {instance.user.username}")

        except Exception as e:
            logger.error(f"Error in JobApplication learning signal: {e}", exc_info=True)

    logger.info("✅ JobApplication outcome signal registered")

except ImportError:
    logger.warning("JobApplication model not found - job application signals not registered")
