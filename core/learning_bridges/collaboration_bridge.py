"""
Collaboration Learning Bridge
Learns from multi-agent collaboration outcomes to optimize team formation
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import Dict, List

from core.models_unified_system import Collaboration, UserAgentLearning

logger = logging.getLogger(__name__)


class CollaborationLearningLoop:
    """
    Learns from multi-agent collaboration outcomes
    Optimizes which agents work well together
    """

    def process_collaboration(self, collaboration: Collaboration):
        """Process collaboration outcome"""

        # Only learn from completed collaborations
        if collaboration.status != 'completed':
            return

        logger.info(f"🤝 Processing collaboration: {collaboration.id}")

        try:
            # Determine if collaboration was successful
            was_successful = self._evaluate_success(collaboration)

            # Extract collaboration patterns
            patterns = self._extract_collaboration_patterns(collaboration)

            # Update team formation learning
            self._update_team_formation_learning(collaboration, was_successful, patterns)

            # Update individual agent collaboration skills
            self._update_agent_collaboration_metrics(collaboration, was_successful, patterns)

            logger.info(f"✅ Collaboration learning complete")

        except Exception as e:
            logger.error(f"Error in collaboration learning: {e}", exc_info=True)

    def _evaluate_success(self, collaboration: Collaboration) -> bool:
        """Evaluate if collaboration was successful"""
        # Check outcome field if it exists
        if hasattr(collaboration, 'outcome'):
            return collaboration.outcome in ['success', 'completed', 'achieved']

        # Otherwise, check if there's a result and no errors
        if hasattr(collaboration, 'result') and collaboration.result:
            return True

        return False

    def _extract_collaboration_patterns(self, collaboration: Collaboration) -> Dict:
        """Extract patterns from collaboration"""
        patterns = {
            'task_type': collaboration.task if hasattr(collaboration, 'task') else 'unknown',
            'num_agents': 0,
            'agent_names': [],
            'coordinator_agent': collaboration.coordinator_agent.name if hasattr(collaboration, 'coordinator_agent') and collaboration.coordinator_agent else None,
            'duration': None,
            'result_quality': 0
        }

        # Extract participating agents
        if hasattr(collaboration, 'agents'):
            agents = collaboration.agents.all()
            patterns['num_agents'] = agents.count()
            patterns['agent_names'] = [agent.name for agent in agents]

        # Calculate duration
        if hasattr(collaboration, 'completed_at') and collaboration.completed_at and hasattr(collaboration, 'created_at'):
            duration = collaboration.completed_at - collaboration.created_at
            patterns['duration'] = duration.total_seconds()

        # Extract result quality if available
        if hasattr(collaboration, 'result') and isinstance(collaboration.result, dict):
            patterns['result_quality'] = collaboration.result.get('quality_score', 0)

        return patterns

    def _update_team_formation_learning(self, collaboration: Collaboration,
                                       was_successful: bool, patterns: Dict):
        """Update learning about which agent combinations work well"""

        user = collaboration.user if hasattr(collaboration, 'user') else None
        if not user:
            return

        # Create a team signature (sorted agent names for consistency)
        team_signature = '_'.join(sorted(patterns['agent_names']))

        learning, _ = UserAgentLearning.objects.get_or_create(
            user=user,
            agent_name=f'Team:{team_signature[:50]}',  # Truncate for DB field
            learning_domain='team_formation',
            defaults={
                'learning_content': {
                    'collaborations': 0,
                    'successes': 0,
                    'failures': 0,
                    'team_members': patterns['agent_names'],
                    'avg_duration': 0,
                    'task_types': []
                },
                'confidence_score': 0.5,
                'learning_source': 'performance_tracking'
            }
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
        content['collaborations'] = content.get('collaborations', 0) + 1

        if was_successful:
            content['successes'] = content.get('successes', 0) + 1
            learning.record_success()
        else:
            content['failures'] = content.get('failures', 0) + 1
            learning.record_failure()

        # Update average duration
        if patterns['duration']:
            current_avg = content.get('avg_duration', 0)
            total = content['collaborations']
            new_avg = ((current_avg * (total - 1)) + patterns['duration']) / total
            content['avg_duration'] = new_avg

        # Track task types this team handles
        if 'task_types' not in content:
            content['task_types'] = []
        if patterns['task_type'] not in content['task_types']:
            content['task_types'].append(patterns['task_type'])

        # Calculate success rate
        if content['collaborations'] > 0:
            content['success_rate'] = content['successes'] / content['collaborations']

        learning.learning_content = content
        learning.save()

        logger.info(f"✅ Updated team formation learning for {team_signature[:30]}...")

    def _update_agent_collaboration_metrics(self, collaboration: Collaboration,
                                           was_successful: bool, patterns: Dict):
        """Update individual agent's collaboration performance metrics"""

        user = collaboration.user if hasattr(collaboration, 'user') else None
        if not user:
            return

        # Update each participating agent's collaboration metrics
        for agent_name in patterns['agent_names']:
            learning, _ = UserAgentLearning.objects.get_or_create(
                user=user,
                agent_name=agent_name,
                learning_domain='collaboration_skills',
                defaults={
                    'learning_content': {
                        'total_collaborations': 0,
                        'successful_collaborations': 0,
                        'team_sizes': [],
                        'common_partners': {}
                    },
                    'confidence_score': 0.5,
                    'learning_source': 'performance_tracking'
                }
            )

            content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
            content['total_collaborations'] = content.get('total_collaborations', 0) + 1

            if was_successful:
                content['successful_collaborations'] = content.get('successful_collaborations', 0) + 1
                learning.record_success()
            else:
                learning.record_failure()

            # Track team sizes this agent works well in
            if 'team_sizes' not in content:
                content['team_sizes'] = []
            content['team_sizes'].append(patterns['num_agents'])

            # Track common collaboration partners
            if 'common_partners' not in content:
                content['common_partners'] = {}

            for partner_name in patterns['agent_names']:
                if partner_name != agent_name:
                    if partner_name not in content['common_partners']:
                        content['common_partners'][partner_name] = {'count': 0, 'successes': 0}

                    content['common_partners'][partner_name]['count'] += 1
                    if was_successful:
                        content['common_partners'][partner_name]['successes'] += 1

            # Calculate collaboration success rate
            if content['total_collaborations'] > 0:
                content['collaboration_success_rate'] = (
                    content['successful_collaborations'] / content['total_collaborations']
                )

            learning.learning_content = content
            learning.save()

        logger.info(f"✅ Updated agent collaboration metrics for {len(patterns['agent_names'])} agents")


# Signal integration
collaboration_learning = CollaborationLearningLoop()


@receiver(post_save, sender=Collaboration)
def on_collaboration_completed(sender, instance, created, **kwargs):
    """Learn from completed collaborations"""
    if instance.status == 'completed':
        try:
            collaboration_learning.process_collaboration(instance)
        except Exception as e:
            logger.error(f"Error in collaboration learning signal: {e}", exc_info=True)
