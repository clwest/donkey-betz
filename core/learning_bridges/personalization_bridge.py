"""
Personalization Feedback Bridge
Learns from user interactions to improve opportunity matching and personalization
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import Dict

logger = logging.getLogger(__name__)


class PersonalizationFeedbackLoop:
    """
    Learns from user interactions to personalize content and opportunities
    """

    def process_interaction(self, interaction):
        """Process opportunity interaction for personalization learning"""

        logger.info(f"👤 Processing interaction: {interaction.interaction_type}")

        try:
            from core.models_unified_system import Opportunity, UserAgentLearning

            # Get the opportunity
            opportunity = Opportunity.objects.filter(id=interaction.opportunity_id).first()
            if not opportunity:
                return

            # Extract interaction patterns
            patterns = self._extract_interaction_patterns(opportunity, interaction)

            # Update user preference learning
            self._update_user_preferences(interaction.user, patterns, interaction.interaction_type)

            # Update opportunity type preferences
            if hasattr(opportunity, 'opportunity_type'):
                self._update_opportunity_type_preferences(
                    interaction.user,
                    opportunity.opportunity_type,
                    interaction.interaction_type
                )

            logger.info(f"✅ Personalization learning complete")

        except Exception as e:
            logger.error(f"Error in personalization learning: {e}", exc_info=True)

    def _extract_interaction_patterns(self, opportunity, interaction) -> Dict:
        """Extract patterns from opportunity and interaction"""
        patterns = {
            'source': opportunity.source if hasattr(opportunity, 'source') else 'unknown',
            'opportunity_type': opportunity.opportunity_type if hasattr(opportunity, 'opportunity_type') else 'unknown',
            'salary_range': float(opportunity.potential_revenue) if hasattr(opportunity, 'potential_revenue') else 0,
            'match_score': opportunity.match_score if hasattr(opportunity, 'match_score') else 0,
            'interaction_type': interaction.interaction_type,
            'interaction_depth': self._calculate_interaction_depth(interaction.interaction_type)
        }

        # Extract metadata features
        if hasattr(opportunity, 'metadata') and isinstance(opportunity.metadata, dict):
            metadata = opportunity.metadata
            patterns['remote'] = metadata.get('remote', False)
            patterns['industry'] = metadata.get('industry', 'unknown')
            patterns['company_size'] = metadata.get('company_size', 'unknown')
            patterns['tech_stack'] = metadata.get('tech_stack', [])

        return patterns

    def _calculate_interaction_depth(self, interaction_type: str) -> int:
        """Calculate depth/engagement level of interaction"""
        depth_map = {
            'view': 1,
            'click': 2,
            'bookmark': 3,
            'apply': 4,
            'interview': 5,
            'accept': 6
        }
        return depth_map.get(interaction_type, 1)

    def _update_user_preferences(self, user, patterns: Dict, interaction_type: str):
        """Update user's opportunity preferences based on interactions"""
        from core.models_unified_system import UserAgentLearning

        learning, _ = UserAgentLearning.objects.get_or_create(
            user=user,
            agent_name='SystemIntelligence',
            learning_domain='user_preferences',
            defaults={
                'learning_content': {
                    'preferred_sources': {},
                    'preferred_salary_range': {'min': 0, 'max': 0},
                    'preferred_industries': {},
                    'preferred_remote': None,
                    'interaction_history': []
                },
                'confidence_score': 0.5,
                'learning_source': 'behavioral'
            }
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}

        # Update source preferences
        source = patterns['source']
        if 'preferred_sources' not in content:
            content['preferred_sources'] = {}
        if source not in content['preferred_sources']:
            content['preferred_sources'][source] = {'count': 0, 'depth_sum': 0}

        content['preferred_sources'][source]['count'] += 1
        content['preferred_sources'][source]['depth_sum'] += patterns['interaction_depth']
        content['preferred_sources'][source]['avg_depth'] = (
            content['preferred_sources'][source]['depth_sum'] /
            content['preferred_sources'][source]['count']
        )

        # Update salary preferences (if applied or deeper engagement)
        if patterns['interaction_depth'] >= 3:
            salary = patterns['salary_range']
            if 'preferred_salary_range' not in content:
                content['preferred_salary_range'] = {'min': salary, 'max': salary, 'count': 0}

            current_min = content['preferred_salary_range'].get('min', 0)
            current_max = content['preferred_salary_range'].get('max', 0)

            # Adjust range based on interactions
            if salary > 0:
                content['preferred_salary_range']['min'] = min(current_min, salary) if current_min > 0 else salary
                content['preferred_salary_range']['max'] = max(current_max, salary)
                content['preferred_salary_range']['count'] = content['preferred_salary_range'].get('count', 0) + 1

        # Update industry preferences
        if 'industry' in patterns and patterns['industry'] != 'unknown':
            industry = patterns['industry']
            if 'preferred_industries' not in content:
                content['preferred_industries'] = {}
            if industry not in content['preferred_industries']:
                content['preferred_industries'][industry] = {'count': 0, 'depth_sum': 0}

            content['preferred_industries'][industry]['count'] += 1
            content['preferred_industries'][industry]['depth_sum'] += patterns['interaction_depth']

        # Track interaction history (keep last 50)
        if 'interaction_history' not in content:
            content['interaction_history'] = []
        content['interaction_history'].append({
            'type': interaction_type,
            'patterns': patterns,
            'depth': patterns['interaction_depth']
        })
        content['interaction_history'] = content['interaction_history'][-50:]

        learning.learning_content = content

        # Adjust confidence based on engagement
        if patterns['interaction_depth'] >= 3:
            learning.record_success()

        learning.save()

        logger.info(f"✅ Updated user preferences for {user.username}")

    def _update_opportunity_type_preferences(self, user, opportunity_type: str, interaction_type: str):
        """Update preferences for specific opportunity types"""
        from core.models_unified_system import UserAgentLearning

        learning, _ = UserAgentLearning.objects.get_or_create(
            user=user,
            agent_name='SystemIntelligence',
            learning_domain=f'opportunity_type_{opportunity_type}',
            defaults={
                'learning_content': {
                    'interaction_count': 0,
                    'engagement_score': 0
                },
                'confidence_score': 0.5,
                'learning_source': 'behavioral'
            }
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
        content['interaction_count'] = content.get('interaction_count', 0) + 1

        # Calculate engagement score
        depth = self._calculate_interaction_depth(interaction_type)
        current_score = content.get('engagement_score', 0)
        new_score = ((current_score * (content['interaction_count'] - 1)) + depth) / content['interaction_count']
        content['engagement_score'] = new_score

        learning.learning_content = content

        # High engagement increases confidence
        if depth >= 3:
            learning.record_success()

        learning.save()


# Global instance
personalization_feedback_loop = PersonalizationFeedbackLoop()


# Signal integration
try:
    from core.models_engagement_metrics import OpportunityInteraction

    @receiver(post_save, sender=OpportunityInteraction)
    def on_opportunity_interaction_for_personalization(sender, instance, created, **kwargs):
        """Learn from user interactions for personalization"""
        if created:
            try:
                personalization_feedback_loop.process_interaction(instance)
            except Exception as e:
                logger.error(f"Error in personalization learning signal: {e}", exc_info=True)
except ImportError:
    logger.warning("OpportunityInteraction model not found - personalization signals not registered")
