"""
Session 326: Project Research Bridge

This service bridges the gap between Projects and Agent Learning:
1. Converts BusinessResearchResult → AgentKnowledgeSource
2. Applies user feedback to adjust confidence scores
3. Triggers spider priority recalculation based on project needs
4. Integrates with the Agent Learning Cycle

The bridge enables:
- Research insights to become permanent agent knowledge
- User accept/reject to train the system
- Active projects to influence spider data collection
"""
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from django.db import transaction
from django.db.models import Avg, Count
from django.utils import timezone

logger = logging.getLogger(__name__)


class ProjectResearchBridge:
    """
    Central bridge connecting Projects → Agent Learning System.

    Data Flow:
    1. User creates project with research topic
    2. Business agents conduct research → BusinessResearchResult
    3. This bridge converts research → AgentKnowledgeSource
    4. User provides feedback (accept/reject/star)
    5. Feedback adjusts knowledge confidence
    6. Learning cycle propagates to other agents
    """

    # Confidence boost/penalty values
    FEEDBACK_CONFIDENCE_DELTA = {
        'starred': 0.3,    # Excellent research gets big boost
        'accept': 0.15,    # Accepted = useful, moderate boost
        'partial': 0.0,    # Partially useful = no change
        'reject': -0.25,   # Rejected = decrease confidence
    }

    # Base confidence for knowledge derived from research
    BASE_RESEARCH_CONFIDENCE = 0.75

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ProjectResearchBridge")

    def research_to_knowledge(
        self,
        research_id: UUID,
        agent_id: Optional[UUID] = None,
        force: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Convert a BusinessResearchResult into AgentKnowledgeSource entries.

        Args:
            research_id: UUID of the BusinessResearchResult
            agent_id: Optional agent to associate knowledge with
            force: If True, recreate even if already converted

        Returns:
            List of created AgentKnowledgeSource entries
        """
        from core.models_unified_system import (
            BusinessResearchResult,
            AgentKnowledgeSource,
            Agent,
        )

        try:
            research = BusinessResearchResult.objects.get(id=research_id)
        except BusinessResearchResult.DoesNotExist:
            self.logger.error(f"Research {research_id} not found")
            return []

        # Check if already converted (unless forced)
        existing = AgentKnowledgeSource.objects.filter(source_research=research)
        if existing.exists() and not force:
            self.logger.info(f"Research {research_id} already converted to {existing.count()} knowledge entries")
            return list(existing.values('id', 'title', 'confidence_score'))

        # Determine which agent(s) to create knowledge for
        if agent_id:
            agents = Agent.objects.filter(id=agent_id)
        else:
            # Find agents related to the research topic
            agents = self._find_relevant_agents(research)

        created_knowledge = []

        with transaction.atomic():
            # Delete existing if forcing recreation
            if force:
                existing.delete()

            for agent in agents:
                knowledge = self._create_knowledge_from_research(research, agent)
                if knowledge:
                    created_knowledge.append({
                        'id': str(knowledge.id),
                        'title': knowledge.title,
                        'confidence': knowledge.confidence_score,
                        'agent': str(agent.id),
                    })

        self.logger.info(
            f"Converted research {research_id} to {len(created_knowledge)} knowledge entries"
        )

        # Trigger spider priority update if project exists
        if research.project:
            self._update_spider_priorities(research.project)

        return created_knowledge

    def _find_relevant_agents(self, research) -> List:
        """Find agents whose expertise matches the research topic."""
        from core.models_unified_system import Agent

        # Get keywords from research - use correct field names
        research_text = f"{research.query} {research.market_topic or ''}"
        keywords = self._extract_keywords(research_text)

        # Find agents with matching specializations
        matching_agents = []
        # Session 329: Use ALL agents (including legacy/deprecated) for project matching
        for agent in Agent.objects.all()[:50]:  # Limit to prevent overload
            # Use specialization and description for matching
            agent_text = f"{agent.specialization or ''} {agent.description or ''}"
            # Check for topic overlap
            if any(kw.lower() in agent_text.lower() for kw in keywords):
                matching_agents.append(agent)

        # Fallback: if no matches, use random agents (ALL including legacy)
        if not matching_agents:
            matching_agents = list(
                Agent.objects.all().order_by('?')[:5]
            )

        return matching_agents

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract key topics from text."""
        # Simple keyword extraction - could be enhanced with NLP
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter common words
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'are', 'was', 'were'}
        keywords = [w for w in words if len(w) > 3 and w not in stopwords]
        return keywords[:10]  # Top 10 keywords

    def _create_knowledge_from_research(self, research, agent) -> Optional[Any]:
        """Create a single AgentKnowledgeSource from research."""
        from core.models_unified_system import AgentKnowledgeSource

        # Build knowledge summary from research - use correct field names
        summary_parts = []

        # Use 'analysis' field (not report_summary)
        if research.analysis:
            summary_parts.append(research.analysis[:1500])

        # Extract key insights from various fields
        key_insights = []

        # Add recommendations as insights
        if research.recommendations:
            for rec in research.recommendations[:3]:
                if isinstance(rec, str):
                    key_insights.append(rec[:200])
                elif isinstance(rec, dict):
                    key_insights.append(str(rec.get('text', rec))[:200])

        # Add pain points as insights
        if research.pain_points:
            for pp in research.pain_points[:3]:
                if isinstance(pp, str):
                    key_insights.append(f"Pain point: {pp[:180]}")
                elif isinstance(pp, dict):
                    key_insights.append(f"Pain point: {str(pp.get('text', pp))[:180]}")

        # Add from raw_data if available
        if research.raw_data and isinstance(research.raw_data, list):
            for item in research.raw_data[:3]:
                if isinstance(item, dict):
                    title = item.get('title', item.get('summary', ''))
                    if title:
                        key_insights.append(title[:200])

        if not summary_parts and not key_insights:
            return None

        # Map research type to knowledge type
        knowledge_type_map = {
            'competitor': 'competitor',
            'competitor_analysis': 'competitor',
            'customer': 'user_behavior',
            'customer_research': 'user_behavior',
            'market': 'market',
            'market_research': 'market',
            'trend': 'trend',
            'trend_analysis': 'trend',
        }
        knowledge_type = knowledge_type_map.get(research.research_type, 'market')

        # Use query or market_topic as title
        title = research.market_topic or research.query[:500]

        knowledge = AgentKnowledgeSource.objects.create(
            agent=agent,
            knowledge_type=knowledge_type,
            title=title,
            summary="\n".join(summary_parts)[:2000] if summary_parts else "Research-derived knowledge",
            key_insights=key_insights[:10],  # Cap at 10 insights
            confidence_score=self.BASE_RESEARCH_CONFIDENCE,
            data_points_count=research.data_points_analyzed or len(key_insights),
            source_project=research.project,
            source_research=research,
        )

        return knowledge

    def apply_feedback(self, feedback_id: UUID) -> Dict[str, Any]:
        """
        Process a ProjectResearchFeedback and apply it to knowledge.

        This is the core learning mechanism:
        1. Find knowledge derived from the research
        2. Adjust confidence based on feedback type
        3. Update feedback statistics on knowledge entries
        4. Mark feedback as applied

        Args:
            feedback_id: UUID of the ProjectResearchFeedback

        Returns:
            Dict with update statistics
        """
        from core.models_unified_system import (
            ProjectResearchFeedback,
            AgentKnowledgeSource,
        )

        try:
            feedback = ProjectResearchFeedback.objects.get(id=feedback_id)
        except ProjectResearchFeedback.DoesNotExist:
            self.logger.error(f"Feedback {feedback_id} not found")
            return {'error': 'Feedback not found'}

        if feedback.applied_to_knowledge:
            return {'status': 'already_applied'}

        # Get the confidence delta for this feedback type
        delta = self.FEEDBACK_CONFIDENCE_DELTA.get(feedback.feedback_type, 0.0)

        # Find related knowledge entries
        if feedback.research:
            # Specific research feedback
            knowledge_entries = AgentKnowledgeSource.objects.filter(
                source_research=feedback.research
            )
        else:
            # Project-level feedback - apply to all project knowledge
            knowledge_entries = AgentKnowledgeSource.objects.filter(
                source_project=feedback.project
            )

        updated_count = 0
        affected_ids = []

        with transaction.atomic():
            for knowledge in knowledge_entries:
                knowledge.apply_feedback(feedback.feedback_type)
                affected_ids.append(str(knowledge.id))
                updated_count += 1

            # Mark feedback as applied
            feedback.applied_to_knowledge = True
            feedback.knowledge_delta = delta
            feedback.affected_knowledge_ids = affected_ids
            feedback.save()

        self.logger.info(
            f"Applied {feedback.feedback_type} feedback to {updated_count} knowledge entries"
        )

        return {
            'status': 'applied',
            'feedback_type': feedback.feedback_type,
            'updated_count': updated_count,
            'confidence_delta': delta,
            'affected_knowledge_ids': affected_ids,
        }

    def _update_spider_priorities(self, project) -> None:
        """Update spider category priorities based on project needs."""
        from core.services.spider_priority_engine import SpiderPriorityEngine

        try:
            engine = SpiderPriorityEngine()
            engine.update_project_priorities(project)
        except Exception as e:
            self.logger.warning(f"Failed to update spider priorities: {e}")

    def get_project_knowledge_stats(self, project_id: UUID) -> Dict[str, Any]:
        """
        Get statistics about knowledge generated from a project.

        Returns:
            Dict with knowledge count, feedback stats, confidence averages
        """
        from core.models_unified_system import (
            PartnershipProject,
            AgentKnowledgeSource,
            ProjectResearchFeedback,
        )

        try:
            project = PartnershipProject.objects.get(id=project_id)
        except PartnershipProject.DoesNotExist:
            return {'error': 'Project not found'}

        # Knowledge stats
        knowledge = AgentKnowledgeSource.objects.filter(source_project=project)
        knowledge_stats = knowledge.aggregate(
            count=Count('id'),
            avg_confidence=Avg('confidence'),
            avg_adjusted=Avg('feedback_adjusted_confidence'),
        )

        # Feedback stats
        feedback = ProjectResearchFeedback.objects.filter(project=project)
        feedback_stats = feedback.values('feedback_type').annotate(count=Count('id'))
        feedback_by_type = {f['feedback_type']: f['count'] for f in feedback_stats}

        # Calculate acceptance rate
        total_feedback = feedback.count()
        positive = feedback_by_type.get('accept', 0) + feedback_by_type.get('starred', 0)
        acceptance_rate = positive / total_feedback if total_feedback > 0 else 0.0

        return {
            'project_id': str(project_id),
            'project_name': getattr(project, 'project_name', '') or getattr(project, 'name', ''),
            'knowledge_generated': knowledge_stats['count'] or 0,
            'avg_confidence': round(knowledge_stats['avg_confidence'] or 0.0, 3),
            'avg_adjusted_confidence': round(knowledge_stats['avg_adjusted'] or 0.0, 3),
            'feedback_given': total_feedback,
            'feedback_by_type': feedback_by_type,
            'acceptance_rate': round(acceptance_rate, 3),
        }

    def sync_all_research_to_knowledge(self, limit: int = 100) -> Dict[str, Any]:
        """
        Batch sync all unprocessed research to knowledge.
        Called by Celery task periodically.

        Args:
            limit: Maximum number of research results to process

        Returns:
            Dict with sync statistics
        """
        from core.models_unified_system import (
            BusinessResearchResult,
            AgentKnowledgeSource,
        )

        # Find research that hasn't been converted to knowledge
        processed_research_ids = AgentKnowledgeSource.objects.filter(
            source_research__isnull=False
        ).values_list('source_research_id', flat=True).distinct()

        unprocessed = BusinessResearchResult.objects.exclude(
            id__in=processed_research_ids
        ).order_by('-created_at')[:limit]

        total_created = 0
        processed_count = 0

        for research in unprocessed:
            result = self.research_to_knowledge(research.id)
            total_created += len(result)
            processed_count += 1

        self.logger.info(
            f"Synced {processed_count} research results → {total_created} knowledge entries"
        )

        return {
            'processed_research': processed_count,
            'knowledge_created': total_created,
            'timestamp': timezone.now().isoformat(),
        }


# Singleton instance
_bridge_instance = None

def get_project_research_bridge() -> ProjectResearchBridge:
    """Get the singleton ProjectResearchBridge instance."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = ProjectResearchBridge()
    return _bridge_instance
