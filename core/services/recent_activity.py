"""
Session 614: Recent Activity Service

Aggregates recent system activity from multiple sources:
- Agent Dreams
- Agent Conversations
- Boardroom Decisions
- Pilot Starts/Completions

Provides a unified feed showing the flow of autonomous system activity.
"""

import logging
from typing import Dict, List, Any
from datetime import timedelta

from django.utils import timezone

logger = logging.getLogger(__name__)


class RecentActivityService:
    """
    Session 614: Aggregates recent system activity into a unified feed.

    Shows the living activity of the autonomous system:
    Dream → Conversation → Decision → Pilot
    """

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.RecentActivityService")

    def get_recent_activity(self, limit: int = 20, hours: int = 72) -> Dict[str, Any]:
        """
        Get recent activity from all sources.

        Args:
            limit: Maximum number of items to return
            hours: How far back to look (default 72 hours)

        Returns:
            Dict with unified activity feed and counts by type
        """
        try:
            cutoff = timezone.now() - timedelta(hours=hours)

            activities = []

            # Gather from each source
            activities.extend(self._get_recent_dreams(cutoff))
            activities.extend(self._get_recent_conversations(cutoff))
            activities.extend(self._get_recent_decisions(cutoff))
            activities.extend(self._get_recent_pilots(cutoff))

            # Sort by timestamp descending
            activities.sort(key=lambda x: x['timestamp'], reverse=True)

            # Limit results
            activities = activities[:limit]

            # Count by type
            type_counts = {}
            for act in activities:
                t = act['type']
                type_counts[t] = type_counts.get(t, 0) + 1

            return {
                'success': True,
                'activities': activities,
                'counts': type_counts,
                'total': len(activities),
                'hours_back': hours,
                'timestamp': timezone.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error getting recent activity: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'activities': [],
            }

    def _get_recent_dreams(self, cutoff) -> List[Dict]:
        """Get recent agent dreams."""
        activities = []

        try:
            from core.models_unified_system import AgentDream

            dreams = AgentDream.objects.filter(
                created_at__gte=cutoff
            ).order_by('-created_at')[:10]

            for dream in dreams:
                # Clean up title
                title = (dream.title or dream.content[:50] if dream.content else 'Untitled dream')
                title = title.replace('[Learned]', '').replace('[Synthesis]', '').strip()

                activities.append({
                    'id': str(dream.id),
                    'type': 'dream',
                    'icon': '💭',
                    'title': title[:60] + ('...' if len(title) > 60 else ''),
                    'subtitle': f"by {dream.agent_name or 'Unknown Agent'}",
                    'timestamp': dream.created_at.isoformat(),
                    'timestamp_display': self._format_time_ago(dream.created_at),
                    'agent': dream.agent_name,
                    'category': getattr(dream, 'category', None),
                })

        except Exception as e:
            self.logger.debug(f"Error getting dreams: {e}")

        return activities

    def _get_recent_conversations(self, cutoff) -> List[Dict]:
        """Get recent agent conversations."""
        activities = []

        try:
            from core.models_unified_system import AgentConversation

            convos = AgentConversation.objects.filter(
                created_at__gte=cutoff
            ).order_by('-created_at')[:10]

            for convo in convos:
                # Get participant names
                agent_a = getattr(convo, 'participant_a_name', None) or 'Agent A'
                agent_b = getattr(convo, 'participant_b_name', None) or 'Agent B'
                topic = getattr(convo, 'topic', None) or getattr(convo, 'title', None) or 'Discussion'
                topic = topic.replace('Discussion:', '').replace('[Synthesis]', '').strip()

                activities.append({
                    'id': str(convo.id),
                    'type': 'conversation',
                    'icon': '🗣️',
                    'title': topic[:60] + ('...' if len(topic) > 60 else ''),
                    'subtitle': f"{agent_a} + {agent_b}",
                    'timestamp': convo.created_at.isoformat(),
                    'timestamp_display': self._format_time_ago(convo.created_at),
                    'agents': [agent_a, agent_b],
                })

        except Exception as e:
            self.logger.debug(f"Error getting conversations: {e}")

        return activities

    def _get_recent_decisions(self, cutoff) -> List[Dict]:
        """Get recent boardroom decisions."""
        activities = []

        try:
            from core.models_unified_system import AgentDecisionSummary

            decisions = AgentDecisionSummary.objects.filter(
                created_at__gte=cutoff
            ).order_by('-created_at')[:10]

            for dec in decisions:
                topic = dec.topic or 'Untitled decision'
                topic = topic.replace('Discussion:', '').replace('[Synthesis]', '').replace('[Learned]', '').strip()

                # Status indicator
                status = getattr(dec, 'status', 'pending')
                status_icon = {
                    'approved': '✅',
                    'rejected': '❌',
                    'pending': '⏳',
                    'promoted': '🚀',
                }.get(status, '📋')

                activities.append({
                    'id': str(dec.id),
                    'type': 'decision',
                    'icon': '🏛️',
                    'title': topic[:60] + ('...' if len(topic) > 60 else ''),
                    'subtitle': f"{status_icon} {dec.decision_type or 'Decision'} · {dec.impact_area or 'General'}",
                    'timestamp': dec.created_at.isoformat(),
                    'timestamp_display': self._format_time_ago(dec.created_at),
                    'status': status,
                    'decision_type': dec.decision_type,
                })

        except Exception as e:
            self.logger.debug(f"Error getting decisions: {e}")

        return activities

    def _get_recent_pilots(self, cutoff) -> List[Dict]:
        """Get recent pilot starts and completions."""
        activities = []

        try:
            from core.models_pilot_readiness import Experiment

            # Recently started
            started = Experiment.objects.filter(
                created_at__gte=cutoff
            ).order_by('-created_at')[:10]

            for exp in started:
                name = exp.name or 'Unnamed Pilot'
                name = (name.replace('Experiment:', '').replace('Discussion:', '')
                        .replace('[Synthesis]', '').replace('[Learned]', '').strip())

                # Different icons based on status
                if exp.status == 'running':
                    icon = '🧪'
                    action = 'Started'
                elif exp.status == 'success':
                    icon = '✅'
                    action = 'Succeeded'
                elif exp.status == 'failure':
                    icon = '❌'
                    action = 'Failed'
                else:
                    icon = '📊'
                    action = exp.status.title()

                activities.append({
                    'id': str(exp.id),
                    'type': 'pilot',
                    'icon': icon,
                    'title': name[:60] + ('...' if len(name) > 60 else ''),
                    'subtitle': f"{action} · Day {(timezone.now() - (exp.started_at or exp.created_at)).days}",
                    'timestamp': exp.created_at.isoformat(),
                    'timestamp_display': self._format_time_ago(exp.created_at),
                    'status': exp.status,
                    'kpi': exp.primary_kpi,
                })

        except Exception as e:
            self.logger.debug(f"Error getting pilots: {e}")

        return activities

    def _format_time_ago(self, dt) -> str:
        """Format datetime as human-readable time ago."""
        now = timezone.now()
        diff = now - dt

        seconds = diff.total_seconds()

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            mins = int(seconds / 60)
            return f"{mins}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        else:
            days = int(seconds / 86400)
            return f"{days}d ago"


# Convenience function
def get_recent_activity(limit: int = 20, hours: int = 72) -> Dict[str, Any]:
    """Get recent system activity feed."""
    service = RecentActivityService()
    return service.get_recent_activity(limit=limit, hours=hours)
