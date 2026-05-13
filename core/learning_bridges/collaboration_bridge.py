"""
Collaboration Learning Bridge
Learns from multi-agent collaboration outcomes to optimize team formation

Session 1115 batch-10: refactored to inherit from the `LearningBridge` ABC
(second concrete migration after RevenueAttributionLearningLoop). Public
`process_collaboration` kept as a back-compat shim so the existing
`on_collaboration_completed` signal handler keeps working unchanged.
"""

import logging
from typing import Any, Dict, List

from django.db.models.signals import post_save
from django.dispatch import receiver

from core.learning_bridges.base import LearningBridge
from core.models_unified_system import Collaboration, UserAgentLearning

logger = logging.getLogger(__name__)


class CollaborationLearningLoop(LearningBridge):
    """
    Learns from multi-agent collaboration outcomes
    Optimizes which agents work well together.

    ABC contract mapping:
      - `process_event(collab)` wraps the original entry (only processes
        when `status='completed'`).
      - `_extract_patterns(collab)` → original `_extract_collaboration_patterns`
        plus the `was_successful` boolean and `_collab` instance threaded
        through for the update step.
      - `_update_learning(patterns)` → calls
        `_update_team_formation_learning` + `_update_agent_collaboration_metrics`.
      - `_generate_insights(patterns)` → human-readable strings about
        the team, duration, and success outcome.
    """

    def __init__(self):
        super().__init__(bridge_name='collaboration')

    # ------------------------------------------------------------------
    # ABC contract
    # ------------------------------------------------------------------
    def process_event(self, event_data: Any) -> Dict:
        """Process a completed Collaboration end-to-end."""
        collaboration: Collaboration = event_data
        if collaboration.status != 'completed':
            return {'status': 'skipped', 'reason': f'status={collaboration.status}'}

        self.log_event(f"Processing collaboration: {collaboration.id}")
        try:
            patterns = self._extract_patterns(collaboration)
            self._update_learning(patterns)
            insights = self._generate_insights(patterns)
            self.log_success(f"Collaboration learning complete for {collaboration.id}")
            return {
                'status': 'ok',
                'collaboration_id': str(collaboration.id),
                'was_successful': patterns.get('was_successful', False),
                'patterns': {k: v for k, v in patterns.items() if not k.startswith('_')},
                'insights': insights,
            }
        except Exception as e:
            self.log_error(f"Error in collaboration learning: {e}")
            return {'status': 'error', 'error': str(e)}

    def _extract_patterns(self, event_data: Any) -> Dict:
        """Extract collaboration patterns + success classification."""
        collaboration: Collaboration = event_data
        patterns: Dict[str, Any] = {
            'task_type': collaboration.task if hasattr(collaboration, 'task') else 'unknown',
            'num_agents': 0,
            'agent_names': [],
            'coordinator_agent': (
                collaboration.coordinator_agent.name
                if hasattr(collaboration, 'coordinator_agent') and collaboration.coordinator_agent
                else None
            ),
            'duration': None,
            'result_quality': 0,
            'was_successful': self._evaluate_success(collaboration),
            # Thread the Collaboration instance through so `_update_learning`
            # can use it without breaking the 1-argument ABC contract.
            '_collab': collaboration,
        }

        if hasattr(collaboration, 'agents'):
            agents = collaboration.agents.all()
            patterns['num_agents'] = agents.count()
            patterns['agent_names'] = [agent.name for agent in agents]

        if (
            hasattr(collaboration, 'completed_at') and collaboration.completed_at
            and hasattr(collaboration, 'created_at')
        ):
            duration = collaboration.completed_at - collaboration.created_at
            patterns['duration'] = duration.total_seconds()

        if hasattr(collaboration, 'result') and isinstance(collaboration.result, dict):
            patterns['result_quality'] = collaboration.result.get('quality_score', 0)

        return patterns

    def _update_learning(self, patterns: Dict) -> None:
        """Update team-formation + per-agent collaboration learning."""
        collaboration: Collaboration = patterns['_collab']
        was_successful: bool = patterns['was_successful']
        self._update_team_formation_learning(collaboration, was_successful, patterns)
        self._update_agent_collaboration_metrics(collaboration, was_successful, patterns)

    def _generate_insights(self, patterns: Dict) -> List[str]:
        """Derive human-readable insight strings."""
        insights: List[str] = []
        was_successful = patterns.get('was_successful', False)
        verb = 'succeeded' if was_successful else 'failed'
        team_size = patterns.get('num_agents', 0)
        names = patterns.get('agent_names', [])
        task = patterns.get('task_type', 'unknown')

        insights.append(
            f"team of {team_size} {verb} on task '{task}'"
        )
        duration = patterns.get('duration')
        if duration is not None:
            insights.append(f"duration: {duration:.1f}s")
        coord = patterns.get('coordinator_agent')
        if coord:
            insights.append(f"coordinator: {coord}")
        if names:
            insights.append(f"members: {sorted(names)}")
        return insights

    # ------------------------------------------------------------------
    # Bridge-specific helpers (unchanged from pre-refactor implementation)
    # ------------------------------------------------------------------
    def _evaluate_success(self, collaboration: Collaboration) -> bool:
        """Evaluate if collaboration was successful."""
        if hasattr(collaboration, 'outcome'):
            return collaboration.outcome in ['success', 'completed', 'achieved']
        if hasattr(collaboration, 'result') and collaboration.result:
            return True
        return False

    def _update_team_formation_learning(self, collaboration: Collaboration,
                                       was_successful: bool, patterns: Dict):
        """Update learning about which agent combinations work well."""

        user = collaboration.user if hasattr(collaboration, 'user') else None
        if not user:
            return

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
                    'task_types': [],
                },
                'confidence_score': 0.5,
                'learning_source': 'performance_tracking',
            },
        )

        content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
        content['collaborations'] = content.get('collaborations', 0) + 1

        if was_successful:
            content['successes'] = content.get('successes', 0) + 1
            learning.record_success()
        else:
            content['failures'] = content.get('failures', 0) + 1
            learning.record_failure()

        if patterns['duration']:
            current_avg = content.get('avg_duration', 0)
            total = content['collaborations']
            new_avg = ((current_avg * (total - 1)) + patterns['duration']) / total
            content['avg_duration'] = new_avg

        if 'task_types' not in content:
            content['task_types'] = []
        if patterns['task_type'] not in content['task_types']:
            content['task_types'].append(patterns['task_type'])

        if content['collaborations'] > 0:
            content['success_rate'] = content['successes'] / content['collaborations']

        learning.learning_content = content
        learning.save()

        logger.info(f"✅ Updated team formation learning for {team_signature[:30]}...")

    def _update_agent_collaboration_metrics(self, collaboration: Collaboration,
                                           was_successful: bool, patterns: Dict):
        """Update individual agent's collaboration performance metrics."""

        user = collaboration.user if hasattr(collaboration, 'user') else None
        if not user:
            return

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
                        'common_partners': {},
                    },
                    'confidence_score': 0.5,
                    'learning_source': 'performance_tracking',
                },
            )

            content = learning.learning_content if isinstance(learning.learning_content, dict) else {}
            content['total_collaborations'] = content.get('total_collaborations', 0) + 1

            if was_successful:
                content['successful_collaborations'] = content.get('successful_collaborations', 0) + 1
                learning.record_success()
            else:
                learning.record_failure()

            if 'team_sizes' not in content:
                content['team_sizes'] = []
            content['team_sizes'].append(patterns['num_agents'])

            if 'common_partners' not in content:
                content['common_partners'] = {}

            for partner_name in patterns['agent_names']:
                if partner_name != agent_name:
                    if partner_name not in content['common_partners']:
                        content['common_partners'][partner_name] = {'count': 0, 'successes': 0}

                    content['common_partners'][partner_name]['count'] += 1
                    if was_successful:
                        content['common_partners'][partner_name]['successes'] += 1

            if content['total_collaborations'] > 0:
                content['collaboration_success_rate'] = (
                    content['successful_collaborations'] / content['total_collaborations']
                )

            learning.learning_content = content
            learning.save()

        logger.info(
            f"✅ Updated agent collaboration metrics for {len(patterns['agent_names'])} agents"
        )

    # ------------------------------------------------------------------
    # Back-compat alias used by `on_collaboration_completed` signal handler
    # ------------------------------------------------------------------
    def process_collaboration(self, collaboration: Collaboration) -> Dict:
        """Back-compat shim — delegates to `process_event`."""
        return self.process_event(collaboration)


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
