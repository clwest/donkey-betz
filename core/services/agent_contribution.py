"""
Agent Contribution Service - Track which agents created what content
Session 120: Service layer for agent tracking functionality
Session 727: Migrated from agents/services.py to core/services/agent_contribution.py
"""

from typing import Dict, List, Optional, Any
from datetime import timedelta
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from django.core.cache import cache
import logging

from core.models.agents_registry import AgentContribution, UnifiedAgentTemplate, AgentExecution
from content.models import CreativeProject, ImageHistory, VideoHistory

logger = logging.getLogger(__name__)


class AgentContributionService:
    """Service for tracking and querying agent contributions to content"""

    def __init__(self):
        self.cache_timeout = 300  # 5 minutes

    # ========================================================================
    # TRACK CONTRIBUTIONS
    # ========================================================================

    def track_image_contribution(
        self,
        agent: UnifiedAgentTemplate,
        project: CreativeProject,
        image: ImageHistory,
        contribution_type: str = 'generation',
        contribution_role: str = 'Primary Creator',
        contribution_percentage: int = 100,
        execution: Optional[AgentExecution] = None,
        task_description: str = '',
        execution_time_seconds: Optional[float] = None,
        tokens_used: Optional[int] = None
    ) -> AgentContribution:
        """
        Track an agent's contribution to image creation/editing.

        This is called automatically when an agent creates or edits an image.
        """
        try:
            # Set agent on image for simple queries
            if not image.agent:
                image.agent = agent
                image.save(update_fields=['agent'])

            # Create detailed contribution record
            contribution = AgentContribution.objects.create(
                agent=agent,
                project=project,
                image=image,
                contribution_type=contribution_type,
                contribution_role=contribution_role,
                contribution_percentage=contribution_percentage,
                execution=execution,
                task_description=task_description,
                execution_time_seconds=execution_time_seconds,
                tokens_used=tokens_used
            )

            # Invalidate project agent cache
            cache_key = f'project_agents_{project.id}'
            cache.delete(cache_key)

            logger.info(
                f"✓ Tracked contribution: {agent.display_name} → "
                f"Image #{image.get_sequential_number()} in {project.name}"
            )

            return contribution

        except Exception as e:
            logger.error(f"Error tracking image contribution: {e}")
            raise

    def track_video_contribution(
        self,
        agent: UnifiedAgentTemplate,
        project: CreativeProject,
        video: VideoHistory,
        contribution_type: str = 'generation',
        contribution_role: str = 'Primary Creator',
        contribution_percentage: int = 100,
        execution: Optional[AgentExecution] = None,
        task_description: str = '',
        execution_time_seconds: Optional[float] = None,
        tokens_used: Optional[int] = None
    ) -> AgentContribution:
        """
        Track an agent's contribution to video creation/editing.

        This is called automatically when an agent creates or edits a video.
        """
        try:
            # Set agent on video for simple queries
            if not video.agent:
                video.agent = agent
                video.save(update_fields=['agent'])

            # Create detailed contribution record
            contribution = AgentContribution.objects.create(
                agent=agent,
                project=project,
                video=video,
                contribution_type=contribution_type,
                contribution_role=contribution_role,
                contribution_percentage=contribution_percentage,
                execution=execution,
                task_description=task_description,
                execution_time_seconds=execution_time_seconds,
                tokens_used=tokens_used
            )

            # Invalidate project agent cache
            cache_key = f'project_agents_{project.id}'
            cache.delete(cache_key)

            logger.info(
                f"✓ Tracked contribution: {agent.display_name} → "
                f"Video #{video.get_sequential_number()} in {project.name}"
            )

            return contribution

        except Exception as e:
            logger.error(f"Error tracking video contribution: {e}")
            raise

    def track_project_contribution(
        self,
        agent: UnifiedAgentTemplate,
        project: CreativeProject,
        contribution_type: str = 'orchestration',
        contribution_role: str = 'Project Coordinator',
        contribution_percentage: int = 100,
        execution: Optional[AgentExecution] = None,
        task_description: str = '',
        execution_time_seconds: Optional[float] = None,
        tokens_used: Optional[int] = None
    ) -> AgentContribution:
        """
        Track an agent's contribution at project level (e.g., orchestration, planning).

        Use this for agents that coordinate work but don't create specific images/videos.
        """
        try:
            contribution = AgentContribution.objects.create(
                agent=agent,
                project=project,
                contribution_type=contribution_type,
                contribution_role=contribution_role,
                contribution_percentage=contribution_percentage,
                execution=execution,
                task_description=task_description,
                execution_time_seconds=execution_time_seconds,
                tokens_used=tokens_used
            )

            # Invalidate project agent cache
            cache_key = f'project_agents_{project.id}'
            cache.delete(cache_key)

            logger.info(
                f"✓ Tracked project contribution: {agent.display_name} → "
                f"{project.name} ({contribution_type})"
            )

            return contribution

        except Exception as e:
            logger.error(f"Error tracking project contribution: {e}")
            raise

    # ========================================================================
    # QUERY CONTRIBUTIONS
    # ========================================================================

    def get_project_agents(self, project: CreativeProject) -> List[Dict[str, Any]]:
        """
        Get all agents that contributed to a project with summary stats.

        Returns list of dicts with agent info and contribution stats.
        Cached for 5 minutes.
        """
        cache_key = f'project_agents_{project.id}'
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Get unique agents with contribution counts
        contributions = AgentContribution.objects.filter(
            project=project
        ).values('agent').annotate(
            contribution_count=Count('id'),
            total_percentage=Sum('contribution_percentage'),
            avg_execution_time=Avg('execution_time_seconds'),
            total_tokens=Sum('tokens_used'),
            avg_rating=Avg('user_rating')
        ).order_by('-contribution_count')

        result = []
        for contrib_data in contributions:
            agent = UnifiedAgentTemplate.objects.get(id=contrib_data['agent'])

            # Get contribution breakdown by type
            type_breakdown = AgentContribution.objects.filter(
                project=project,
                agent=agent
            ).values('contribution_type').annotate(
                count=Count('id')
            )

            result.append({
                'agent_id': str(agent.id),
                'agent_name': agent.display_name,
                'agent_description': agent.description,
                'contribution_count': contrib_data['contribution_count'],
                'total_percentage': contrib_data['total_percentage'] or 0,
                'avg_execution_time': contrib_data['avg_execution_time'],
                'total_tokens': contrib_data['total_tokens'] or 0,
                'avg_rating': contrib_data['avg_rating'],
                'type_breakdown': {
                    item['contribution_type']: item['count']
                    for item in type_breakdown
                }
            })

        cache.set(cache_key, result, self.cache_timeout)
        return result

    def get_agent_timeline(
        self,
        project: CreativeProject,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get chronological timeline of agent contributions to a project.

        Returns list of contribution events in reverse chronological order.
        """
        contributions = AgentContribution.objects.filter(
            project=project
        ).select_related(
            'agent', 'image', 'video'
        ).order_by('-created_at')[:limit]

        timeline = []
        for contrib in contributions:
            timeline.append({
                'id': str(contrib.id),
                'timestamp': contrib.created_at.isoformat(),
                'agent_name': contrib.agent.display_name,
                'agent_id': str(contrib.agent.id),
                'contribution_type': contrib.contribution_type,
                'contribution_role': contrib.contribution_role,
                'content_reference': contrib.content_reference,
                'task_description': contrib.task_description,
                'execution_time_seconds': contrib.execution_time_seconds,
                'tokens_used': contrib.tokens_used,
                'user_rating': contrib.user_rating,
                'user_selected': contrib.user_selected
            })

        return timeline

    def get_contribution_stats(self, project: CreativeProject) -> Dict[str, Any]:
        """
        Get aggregate statistics for project contributions.

        Returns summary stats for displaying in UI.
        """
        contributions = AgentContribution.objects.filter(project=project)

        stats = {
            'total_contributions': contributions.count(),
            'unique_agents': contributions.values('agent').distinct().count(),
            'total_tokens_used': contributions.aggregate(
                total=Sum('tokens_used')
            )['total'] or 0,
            'total_execution_time': contributions.aggregate(
                total=Sum('execution_time_seconds')
            )['total'] or 0,
            'average_rating': contributions.aggregate(
                avg=Avg('user_rating')
            )['avg'],
            'contribution_types': {}
        }

        # Get breakdown by contribution type
        type_counts = contributions.values('contribution_type').annotate(
            count=Count('id')
        )
        for item in type_counts:
            stats['contribution_types'][item['contribution_type']] = item['count']

        return stats

    # ========================================================================
    # USER FEEDBACK
    # ========================================================================

    def rate_contribution(
        self,
        contribution_id: str,
        rating: int
    ) -> AgentContribution:
        """
        Let user rate an agent's contribution (1-5 stars).
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        contribution = AgentContribution.objects.get(id=contribution_id)
        contribution.user_rating = rating
        contribution.save(update_fields=['user_rating'])

        # Invalidate cache
        cache_key = f'project_agents_{contribution.project.id}'
        cache.delete(cache_key)

        logger.info(
            f"✓ User rated contribution {contribution_id}: {rating} stars"
        )

        return contribution

    def mark_contribution_selected(
        self,
        contribution_id: str,
        selected: bool = True
    ) -> AgentContribution:
        """
        Mark an agent's contribution as user's favorite/selected.
        """
        contribution = AgentContribution.objects.get(id=contribution_id)
        contribution.user_selected = selected
        contribution.save(update_fields=['user_selected'])

        # Invalidate cache
        cache_key = f'project_agents_{contribution.project.id}'
        cache.delete(cache_key)

        logger.info(
            f"✓ Contribution {contribution_id} marked as "
            f"{'selected' if selected else 'not selected'}"
        )

        return contribution

    # ========================================================================
    # AGENT PERFORMANCE
    # ========================================================================

    def get_agent_performance(
        self,
        agent: UnifiedAgentTemplate,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get performance stats for an agent over the last N days.
        """
        since = timezone.now() - timedelta(days=days)
        contributions = AgentContribution.objects.filter(
            agent=agent,
            created_at__gte=since
        )

        return {
            'agent_id': str(agent.id),
            'agent_name': agent.display_name,
            'period_days': days,
            'total_contributions': contributions.count(),
            'projects_contributed': contributions.values('project').distinct().count(),
            'avg_execution_time': contributions.aggregate(
                avg=Avg('execution_time_seconds')
            )['avg'],
            'total_tokens_used': contributions.aggregate(
                total=Sum('tokens_used')
            )['total'] or 0,
            'avg_user_rating': contributions.filter(
                user_rating__isnull=False
            ).aggregate(
                avg=Avg('user_rating')
            )['avg'],
            'selection_rate': self._calculate_selection_rate(contributions)
        }

    def _calculate_selection_rate(self, queryset) -> Optional[float]:
        """Calculate percentage of contributions marked as selected"""
        total = queryset.count()
        if total == 0:
            return None

        selected = queryset.filter(user_selected=True).count()
        return (selected / total) * 100
